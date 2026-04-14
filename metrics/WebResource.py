import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import urljoin

import extruct
import requests
from lxml import html
from rdflib import ConjunctiveGraph, URIRef
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from metrics.util import clean_kg_excluding_ns_prefix, is_DOI, get_DOI

logger = logging.getLogger(__name__)

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)

# configure logger to print to console with a simple format, including line number
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s: %(lineno)d - %(message)s",
)


class WebResource:
    COMMON_RDF_MIME_TYPES: Sequence[Tuple[str, str]] = (
        ("application/ld+json", "json-ld"),
        ("application/rdf+xml", "xml"),
        ("text/turtle", "turtle"),
        ("application/n-triples", "ntriples"),
        ("text/n3", "n3"),
        ("application/trig", "trig"),
        ("application/n-quads", "nquads"),
    )

    RDF_MIME_TO_FORMAT: Dict[str, str] = {
        "application/ld+json": "json-ld",
        "application/rdf+xml": "xml",
        "text/turtle": "turtle",
        "application/n-triples": "ntriples",
        "text/plain": "ntriples",
        "text/n3": "n3",
        "application/trig": "trig",
        "application/n-quads": "nquads",
        "text/x-nquads": "nquads",
    }

    LINK_RELATIONS_FOR_METADATA = {
        "describedby",
        "alternate",
        "item",
        "meta",
    }

    def __init__(
        self,
        url: str,
        rdf_graph: Optional[ConjunctiveGraph] = None,
        timeout: int = 30,
    ) -> None:
        self.id = uuid.uuid4()
        self.url = url
        self.timeout = timeout

        self.status_code: Optional[int] = None
        self.headers: Dict[str, str] = {}
        self.content_type: Optional[str] = None

        self.dataset = ConjunctiveGraph()
        self.dataset.namespace_manager.bind("sc", URIRef("http://schema.org/"))
        self.dataset.namespace_manager.bind("scs", URIRef("https://schema.org/"))
        self.dataset.namespace_manager.bind("bsc", URIRef("https://bioschemas.org/"))
        self.dataset.namespace_manager.bind("dct", URIRef("http://purl.org/dc/terms/"))

        self.graph_uris = {
            "content_neg": URIRef(f"{self.url}#content-neg"),
            "mime_probe": URIRef(f"{self.url}#mime-probe"),
            "datacite_probe": URIRef(f"{self.url}#datacite-probe"),
            "html_jsonld": URIRef(f"{self.url}#html-jsonld"),
            "html_rdfa": URIRef(f"{self.url}#html-rdfa"),
            "html_microdata": URIRef(f"{self.url}#html-microdata"),
        }

        if rdf_graph is not None:
            for s, p, o in rdf_graph:
                self.dataset.add((s, p, o, URIRef(f"{self.url}#provided")))
        else:
            self._retrieve_all_metadata()

        # remove triples with the xhtml vocab namespace,
        # as they are often noise in this context and not relevant for FAIR assessment
        self.dataset = clean_kg_excluding_ns_prefix(self.dataset)

        logger.info(
            "WebResource loaded %s with %s RDF triples",
            self.url,
            len(self.dataset),
        )

    def get_url(self) -> str:
        return self.url

    def get_rdf(self) -> ConjunctiveGraph:
        return self.dataset

    def get_status_code(self) -> Optional[int]:
        return self.status_code

    def get_http_header(self) -> Dict[str, str]:
        return self.headers

    def _retrieve_all_metadata(self) -> None:
        base_response = self._http_get(self.url)
        if base_response is None:
            return

        self.status_code = base_response.status_code
        self.headers = dict(base_response.headers)
        self.content_type = self._normalize_content_type(
            base_response.headers.get("Content-Type")
        )

        # self._collect_from_link_relations(base_response)
        self._collect_from_common_accept_headers()
        g1 = self.dataset.get_context(self.graph_uris["mime_probe"])

        # if DOI, try datacite metadata retrieval
        if is_DOI(self.url):
            self._collect_from_datacite()

        self.dataset = clean_kg_excluding_ns_prefix(self.dataset)

        # if no triples were retrieved by content negotiation, try to collect embedded RDF with Selenium and extruct (costly)
        if len(g1) == 0:
            self._collect_embedded_rdf_with_selenium()

        self.dataset = clean_kg_excluding_ns_prefix(self.dataset)

    def _http_get(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
    ) -> Optional[requests.Response]:
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=False,
            )
            return response
        except requests.RequestException as exc:
            logger.warning("HTTP request failed for %s: %s", url, exc)
            return None

    def _collect_from_link_relations(self, base_response: requests.Response) -> None:
        graph = self.dataset.get_context(self.graph_uris["content_neg"])
        candidates = self._extract_link_candidates(base_response)

        for link_url, mime_hint in candidates:
            formats = self._formats_for_mime(mime_hint)
            if not formats:
                formats = [fmt for _, fmt in self.COMMON_RDF_MIME_TYPES]

            response = self._http_get(link_url)
            if response is None or response.status_code >= 400:
                continue

            if not self._parse_response_in_formats(
                graph,
                source_url=link_url,
                response=response,
                candidate_formats=formats,
            ):
                inferred_format = self._format_from_response_content_type(response)
                if inferred_format:
                    self._parse_response_in_formats(
                        graph,
                        source_url=link_url,
                        response=response,
                        candidate_formats=[inferred_format],
                    )

    def _extract_link_candidates(
        self, base_response: requests.Response
    ) -> List[Tuple[str, Optional[str]]]:
        candidates: List[Tuple[str, Optional[str]]] = []
        seen = set()

        raw_link_header = base_response.headers.get("Link")
        if raw_link_header:
            links = requests.utils.parse_header_links(raw_link_header)
            for link in links:
                href = link.get("url")
                rel = (link.get("rel") or "").lower()
                mime_hint = link.get("type")

                if not href:
                    continue
                rel_tokens = {
                    token.strip() for token in rel.split(" ") if token.strip()
                }
                if not rel_tokens.intersection(self.LINK_RELATIONS_FOR_METADATA):
                    continue

                absolute_href = urljoin(self.url, href)
                key = (absolute_href, mime_hint)
                if key not in seen:
                    seen.add(key)
                    candidates.append(key)

        if (
            self._normalize_content_type(base_response.headers.get("Content-Type"))
            == "text/html"
        ):
            try:
                doc = html.fromstring(base_response.text)
                for node in doc.xpath("//link[@href]"):
                    rel = (node.get("rel") or "").lower()
                    rel_tokens = {
                        token.strip()
                        for token in rel.replace(",", " ").split(" ")
                        if token.strip()
                    }
                    if not rel_tokens.intersection(self.LINK_RELATIONS_FOR_METADATA):
                        continue

                    href = node.get("href")
                    if not href:
                        continue
                    mime_hint = node.get("type")
                    absolute_href = urljoin(self.url, href)
                    key = (absolute_href, mime_hint)
                    if key not in seen:
                        seen.add(key)
                        candidates.append(key)
            except Exception as exc:
                logger.debug("Could not parse HTML links for %s: %s", self.url, exc)

        return candidates

    def _collect_from_datacite(self) -> None:
        graph = self.dataset.get_context(self.graph_uris["datacite_probe"])
        doi = get_DOI(self.url)
        if not doi:
            return

        logger.info(f"Collecting metadata from datacite for DOI {doi}")
        datacite_endpoint = f"https://data.crosscite.org/application/ld+json/{doi}"
        response = requests.get(datacite_endpoint)
        if response.status_code >= 400:
            logger.warning(
                "HTTP request failed for %s: %s", datacite_endpoint, response
            )
            return
        else:
            metadata = response.text
            kg = ConjunctiveGraph()
            try:
                kg.parse(data=metadata, format="json-ld")
            except Exception as e:
                logger.warning("Could not parse metadata from datacite")
                logger.warning(e)
                return

            if len(kg) > 0:
                logger.info(f"Collected {len(kg)} triples from datacite for {doi}")
                # logger.info(kg.serialize(format="turtle"))
            # merge graph and kg
            graph += kg

    def _collect_from_common_accept_headers(self) -> None:
        graph = self.dataset.get_context(self.graph_uris["mime_probe"])

        for accept_mime, rdf_format in self.COMMON_RDF_MIME_TYPES:
            response = self._http_get(self.url, headers={"Accept": accept_mime})
            if response is None or response.status_code >= 400:
                continue

            parsed = self._parse_response_in_formats(
                graph,
                source_url=self.url,
                response=response,
                candidate_formats=[rdf_format],
            )

            if parsed:
                logger.info(
                    f"Parsed RDF triples: {len(graph)} triples for {accept_mime}: {rdf_format}"
                )
            else:
                inferred_format = self._format_from_response_content_type(response)
                if inferred_format:
                    self._parse_response_in_formats(
                        graph,
                        source_url=self.url,
                        response=response,
                        candidate_formats=[inferred_format],
                    )
                    logger.info(
                        f"Parsed RDF triples: {len(graph)} triples for {accept_mime} with content-type inference: {inferred_format}"
                    )

    def _collect_embedded_rdf_with_selenium(self) -> None:
        logger.info("Collecting embedded RDF")
        driver = None
        service = None

        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")

            proxy = os.getenv("HTTP_PROXY")
            if proxy:
                chrome_options.add_argument("--proxy-server=" + proxy)

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(self.timeout)
            driver.get(self.url)
            logger.debug(f"Collecting embedded RDF with timeout {self.timeout}")
            WebDriverWait(driver, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            html_source = driver.page_source

            data = extruct.extract(
                html_source,
                base_url=self.url,
                syntaxes=["json-ld", "rdfa", "microdata"],
                errors="ignore",
            )

            self._parse_extruct_json_items(data.get("json-ld", []), "html_jsonld")
            self._parse_extruct_json_items(data.get("rdfa", []), "html_rdfa")
            self._parse_extruct_json_items(data.get("microdata", []), "html_microdata")
        except Exception as exc:
            logger.warning("Selenium extraction failed for %s: %s", self.url, exc)
        finally:
            # Always close webdriver and service to avoid orphan chromedriver processes.
            if driver is not None:
                try:
                    driver.quit()
                except Exception as exc:
                    logger.debug(
                        "Error while quitting webdriver for %s: %s", self.url, exc
                    )
            if service is not None:
                try:
                    service.stop()
                except Exception as exc:
                    logger.debug(
                        "Error while stopping chromedriver service for %s: %s",
                        self.url,
                        exc,
                    )

    def _parse_extruct_json_items(self, items: Sequence[dict], graph_key: str) -> None:
        graph = self.dataset.get_context(self.graph_uris[graph_key])
        for item in items:
            try:
                graph.parse(
                    data=json.dumps(item, ensure_ascii=False),
                    format="json-ld",
                    publicID=self.url,
                )
            except Exception:
                continue

    def _parse_response_in_formats(
        self,
        graph,
        source_url: str,
        response: requests.Response,
        candidate_formats: Sequence[str],
    ) -> bool:
        body_text = response.text
        parsed_any = False

        for rdf_format in candidate_formats:
            kg = ConjunctiveGraph()
            try:
                kg.parse(data=body_text, format=rdf_format, publicID=source_url)
                parsed_any = True
            except Exception:
                continue

            # merge graph and kg
            graph += kg

        return parsed_any

    def _format_from_response_content_type(
        self, response: requests.Response
    ) -> Optional[str]:
        content_type = self._normalize_content_type(
            response.headers.get("Content-Type")
        )
        return self.RDF_MIME_TO_FORMAT.get(content_type)

    def _formats_for_mime(self, mime: Optional[str]) -> List[str]:
        if not mime:
            return []
        normalized = self._normalize_content_type(mime)
        rdf_format = self.RDF_MIME_TO_FORMAT.get(normalized)
        return [rdf_format] if rdf_format else []

    @staticmethod
    def _normalize_content_type(content_type: Optional[str]) -> str:
        if not content_type:
            return ""
        return content_type.split(";", 1)[0].strip().lower()

    # def _is_html_only(self, base_response: requests.Response) -> bool:
    #     is_html = (
    #         self._normalize_content_type(base_response.headers.get("Content-Type"))
    #         == "text/html"
    #     )
    #     if not is_html:
    #         return False
    #
    #     content_neg_size = len(self.dataset.get_context(self.graph_uris["content_neg"]))
    #     mime_probe_size = len(self.dataset.get_context(self.graph_uris["mime_probe"]))
    #     return (content_neg_size + mime_probe_size) == 0

    def __str__(self) -> str:
        return (
            "Web resource under FAIR assessment:\n\t"
            + self.url
            + "\n\t"
            + str(len(self.dataset))
            + " RDF triples"
        )
