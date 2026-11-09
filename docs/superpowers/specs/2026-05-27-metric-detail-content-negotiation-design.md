# Design: Content Negotiation for `/test/<tag>`

**Date:** 2026-05-27  
**Branch:** ostrails-compliance  
**Author:** Alban Gaignard

---

## Goal

Extend the `metric_detail` route (`/test/<tag>`) so that clients requesting linked-data formats via HTTP `Accept` headers (or a `?format=` query parameter) receive the metric's metadata as RDF, while browser clients continue to receive the existing HTML page.

---

## Scope

- **In scope:** content negotiation on `/test/<tag>`; new `_build_metric_kg` helper in `util.py`; TDD unit tests.
- **Out of scope:** changes to other routes; new RDF vocabularies beyond what is already in `util.py`; UI changes to `metric_detail.html`.

---

## Architecture

### Reused components (no changes)

| Symbol | Location | Purpose |
|---|---|---|
| `_ACCEPT_MAP` | `metrics/util.py` | Maps Accept MIME types → `(rdflib format, mime)` tuples |
| `_FORMAT_PARAM` | `metrics/util.py` | Maps `?format=` values → `(rdflib format, mime)` tuples |
| `_negotiate_rdf_response(kg, record_id, target_uri, base_path)` | `metrics/util.py` | Serialises a KG according to Accept header / `?format=` param; renders `data.html` for `text/html` |
| `_turtle_to_html` | `metrics/util.py` | Used internally by `_negotiate_rdf_response` |

### New component

**`_build_metric_kg(metric, subject_uri: str) -> ConjunctiveGraph`** — added to `metrics/util.py`.

Constructs a `ConjunctiveGraph` describing one FAIR metric using `schema:` + `dcterms:` vocabularies:

```turtle
@prefix schema: <https://schema.org/> .
@prefix dcterms: <http://purl.org/dc/terms/> .

<{subject_uri}>
    a schema:Thing ;
    schema:name          "{metric.get_name()}" ;
    dcterms:description  "{metric.get_desc() — HTML stripped}" ;
    dcterms:identifier   "{metric.get_principle_tag()}" ;
    schema:isPartOf      <{metric.get_principle()}> ;
    schema:codeRepository <https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/metrics/{tag}_Impl.py> ;
    dcterms:modified     "{metric.get_update_date()}"^^xsd:date .
```

HTML tags are stripped from `get_desc()` before storing as an RDF literal.

---

## Route change (`app.py`)

```python
@app.route("/test/<tag>")
def metric_detail(tag):
    tag = tag.upper()
    metrics_by_tag = {m.get_principle_tag(): m for m in FAIRMetricsFactory.get_FC_impl()}
    metric = metrics_by_tag.get(tag)
    if metric is None:
        abort(404)

    best = request.accept_mimetypes.best_match(
        ["text/html"] + list(_ACCEPT_MAP.keys()),
        default="text/html",
    )
    fmt_param = request.args.get("format", "").lower()

    if best != "text/html" or fmt_param in _FORMAT_PARAM:
        kg = _build_metric_kg(metric, request.url)
        return _negotiate_rdf_response(kg, tag, request.url, "test")

    return render_template(
        "metric_detail.html",
        title=metric.get_principle_tag(),
        subtitle=metric.get_name(),
        tag=metric.get_principle_tag(),
        name=metric.get_name(),
        desc=metric.get_desc(),
        principle=metric.get_principle(),
        implem=metric.get_implem(),
        updated_at=metric.get_update_date(),
    )
```

The condition `best != "text/html" or fmt_param in _FORMAT_PARAM` ensures:
- Any RDF Accept header → KG path
- `?format=turtle|json-ld|rdf-xml` → KG path
- Plain browser request (no special Accept / no format param) → existing HTML template

---

## Data flow

```
GET /test/F1A
  Accept: text/turtle
        │
        ▼
metric_detail("F1A")
  │
  ├─ resolve metric object
  ├─ best_match → "text/turtle"  (≠ "text/html")
  ├─ _build_metric_kg(metric, request.url)  → ConjunctiveGraph
  └─ _negotiate_rdf_response(kg, "F1A", url, "test")
       └─ kg.serialize(format="turtle")  →  Response(mimetype="text/turtle")
```

---

## Tests (TDD)

All tests go in `tests/test_metric_detail_page.py`, added after the existing five.  
Write each test **before** its supporting code; verify it fails for the right reason; then implement.

| Test name | Accept / param | Expected |
|---|---|---|
| `test_metric_detail_returns_turtle_when_accept_turtle` | `Accept: text/turtle` | 200, parseable Turtle, tag URI present |
| `test_metric_detail_returns_jsonld_when_accept_jsonld` | `Accept: application/ld+json` | 200, parseable JSON-LD |
| `test_metric_detail_returns_rdfxml_when_accept_rdfxml` | `Accept: application/rdf+xml` | 200, parseable RDF/XML |
| `test_metric_detail_returns_turtle_via_format_param` | `?format=turtle` | 200, parseable Turtle |
| `test_metric_detail_still_returns_html_by_default` | *(none)* | 200, `text/html` content-type (regression guard) |

---

## Error handling

- Unknown `<tag>` → existing `abort(404)` — unchanged.
- `_build_metric_kg` failures (e.g. malformed date literal) propagate as 500; no special handling needed at this stage.

---

## Out-of-scope / future

- `?format=html` explicit redirect to `data.html` Turtle viewer.
- Pagination or collection endpoint listing all metrics as RDF.
- Cache-Control headers on RDF responses.
