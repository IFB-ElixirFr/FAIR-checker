[![Actions Status](https://github.com/IFB-ElixirFr/fair-checker/workflows/Unit%20testing/badge.svg)](https://github.com/IFB-ElixirFr/fair-checker/actions) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Version 1.3.4](https://img.shields.io/badge/version-v1.3.4-blue)]()

# FAIR-checker
FAIR-Checker is a tool aimed at assessing FAIR principles and empowering data provider to enhance the quality of their digital resources.

Data providers and consumers can check how FAIR are web resources. Developers can explore and inspect metadata exposed in web resources.

FAIR-Checker is a web tool to assess FAIRness of web resources. The web app is deployed at https://fair-checker.france-bioinformatique.fr. The user documentation is available from its "Documentation" menu (see [User documentation](#user-documentation)).

<!--
The command line tool (metadata scraper and validator) is not maintained anymore.

    **Usage examples :**
        python cli.py evaluate --url http://bio.tools/bwa --url http://bio.tools/jaspar
        python cli.py extract_metadata --url http://bio.tools/bwa -o metadata_dump
        python cli.py extract_metadata --url-collection input_urls.txt
        python cli.py validate_bioschemas --url http://bio.tools/bwa
-->

Main contributors are: 
- [Alban Gaignard](https://github.com/albangaignard)
- [Frédéric De Lamotte](https://orcid.org/0000-0003-4234-1172)
- [Brieuc Quemeneur](https://github.com/Phloemus)

Past contributors:
- [Thomas Rosnet](https://github.com/thomasrosnet)
- [Marie-Dominique Devignes](https://members.loria.fr/MDDevignes/)
- [Sahar Frikha](https://github.com/sahar-frikha)

## Main features
- extracts embedded metatdata from web pages, currently supporting RDFa, JSON-LD, and microdata formats
- retrieves metadata through HTTP content negotiation (JSON-LD, RDF/XML, Turtle, N-Triples, N3, TriG, N-Quads) and [FAIR Signposting](https://signposting.org/FAIR/) links
- evaluates [FAIR metrics](https://www.go-fair.org/fair-principles/) on these metadata (supported by [Identifiers.org](https://identifiers.org/)). 
- provides a graphical summary on FAIR assesment 
- provides detailed evaluations for each metric with technical recommendations
- explore the content of metadata
- enrich metadata based on live SPARQL endpoints, currently relying on [Wikidata](https://www.wikidata.org), [OpenAIRE](https://graph.openaire.eu/develop/), and [OpenCitations](https://opencitations.net)
- evaluate if used controled vocabularies / ontologies are indexed in community registries, currently supported by [OLS](https://www.ebi.ac.uk/ols), [LOV](https://lov.linkeddata.es/dataset/lov/), [BioPortal](https://bioportal.bioontology.org), [AgroPortal](https://agroportal.eu) and [EarthPortal](https://earthportal.eu)
- evaluate [Bioschemas community profiles](https://bioschemas.org/profiles/) to check if required or recommended metadata is missing
- evaluate DataCite and ENA Checklist 53 profiles when a compatible resource is detected
- provides a REST API, documented with Swagger at `/swagger`

## User documentation
The user documentation (Check and Inspect pages, content negotiation, metadata quality checks) is written with [Sphinx](https://www.sphinx-doc.org) in the `docs` folder. To build it, from the root of the repository:

```bash
poetry run sphinx-build -b html docs docs/_build/html
```

When the web application is running, the documentation is served at [http://localhost:5000/docs/index.html](http://localhost:5000/docs/index.html), and from the "Documentation" link of the navigation bar.

## Known bugs
- too few results retrieved from external SPARQL endpoints

## Contribute
Please submit GitHub issues to provide feedback or ask for new features, and contact us for any related question.

## Installation and Deployment

The deployment process can be done localy on your computer or on a production environment via a virtual machine.
To install Fair-Checker you need to have some programs installed on your computer: 

- git
- micromamba
- poetry

### Local installation

```
bash
git clone https://github.com/IFB-ElixirFr/fair-checker.git
cd fair-checker
```

To run Fair-Checker you first have to create an environment for Fair-Checker mongo database

```
bash
micromamba env create --name fc-mongodb --file fc-mongodb-environment.yaml
micromamba activate fc-mongodb
mongod --dbpath data
```

The database should display logs and wait for the Fair-Checker app to connect

In an other terminal, create the environment for the Fair-Checker application itself

```
micromamba env create --name fc-p311 python=3.11
micromamba activate fc-p311
poetry install 
poetry run playwright install chromium
```

To run the Fair-Checker application run the following command:

```
bash
poetry run python app.py --web
```

The application should be accessible localy on your browser at [http://localhost:5000](http://localhost:5000)

> [!NOTE]
> A know bug can occur when using the development version of **Fair-Checker** on Firefox. We advise to use an other 
> browser to use the application, such as **Google Chrome** or **Safari**

### Deployment in a production environment

In a production environment the process is similar but Python 3.12 has to be used for the Fair-Checker application. Moreover ```FAIR_CHECKER_ENV``` and ```SERVER_URL``` have to be set, as described in [Configuration](#configuration). Copy ```.env.sample``` to ```.env``` and edit it to fit your deployment server.

```
bash
git clone https://github.com/IFB-ElixirFr/fair-checker.git
cd fair-checker
```

To run Fair-Checker you first have to create an environment for Fair-Checker mongo database

```
bash
micromamba env create --name fc-mongodb --file fc-mongodb-environment.yaml
micromamba activate fc-mongodb
mongod --dbpath data
```

The database should display logs and wait for the Fair-Checker app to connect

In an other terminal, create the environment for the Fair-Checker application itself

```
micromamba env create --name fc-p312 python=3.12
micromamba activate fc-p312
poetry install 
poetry run playwright install chromium
```

To run the Fair-Checker application run the following command:

```
bash
export FAIR_CHECKER_ENV=production
poetry run python app.py --web
```

### Configuration

Fair-Checker is configured in three layers. They are easy to mix up, so here is what each one is for:

| Layer | What it holds | Where it lives |
|---|---|---|
| `config.py` | Settings that depend on the **kind of instance**: the base URLs minted in the RDF results (`EVAL_URL`, `ASSESSMENT_URL`, `TEST_URL`), debug mode, cache durations. One class per instance kind. | Versioned in git |
| Environment variables | Which class of `config.py` is used (`FAIR_CHECKER_ENV`), plus settings specific to **your machine or server** (`SERVER_URL`). | The shell, the service definition, or `.env` |
| `.env` file | A convenient place to store environment variables and secrets. It is loaded at startup by `config.py` (`python-dotenv`). | Local file, **not versioned** (copy it from `.env.sample`) |

In short: `config.py` defines what each kind of instance looks like, the environment variable `FAIR_CHECKER_ENV` picks one, and `.env` is just a file that sets environment variables. A variable that is already set in the real environment takes precedence over the same variable in `.env`.

#### Choosing the instance kind

The instance kind is read at startup from `FAIR_CHECKER_ENV`. If it is not set, the default is `development`.

> [!NOTE]
> Older deployments set `FLASK_ENV` instead (e.g. in the `Dockerfile`). It is still read when `FAIR_CHECKER_ENV` is not set, but Flask no longer uses it itself: prefer `FAIR_CHECKER_ENV` for new setups.

| `FAIR_CHECKER_ENV` | Class in `config.py` | Use it for | IRIs of results, e.g. `…/eval/<id>`, `…/test/<tag>` |
|---|---|---|---|
| `development` (default, or any other value) | `DevelopmentConfig` | Running locally | `SERVER_URL` + `/eval/`, `/assessment/`, `/test/` (default `http://127.0.0.1:5000`) |
| `staging` | `StagingConfig` | A public dev/test server, such as `https://fair-checker.dev.france-bioinformatique.fr` | `SERVER_URL` + `/eval/`, `/assessment/`, `/test/` |
| `production` | `ProductionConfig` | The production server | `https://w3id.org/fairchecker/{eval,assessment,test}/…` |

The IRIs matter because the RDF results (`/eval/<id>`, `/assessment/<id>`, `/test/<tag>`) link to each other and to the descriptions of the tests. In production these are persistent [W3ID](https://w3id.org/) IRIs, which must redirect to the production server. A dev or staging server must **not** use them: the W3ID IRIs would point to production, which knows nothing about the evaluations and tests of the dev instance. That is why `staging` and `development` build their IRIs from the address of the server itself.

#### Environment variables

| Variable | Required | Description |
|---|---|---|
| `FAIR_CHECKER_ENV` | recommended | `development`, `staging` or `production` (see above). |
| `SERVER_URL` | production and staging; optional in development | Public URL of the server, without trailing slash, e.g. `https://fair-checker.dev.france-bioinformatique.fr`. It is used by the web pages to open their websocket connection. For `staging` and `development` it is also the base of the IRIs of the results (no default for `staging`, which refuses to start without it; `http://127.0.0.1:5000` for `development`). It is not used as the listening address. |
| `FAIR_CHECKER_HOST`, `FAIR_CHECKER_PORT` | optional | Listening address of `python app.py --web` (default `127.0.0.1` and `5000`, suited to a reverse proxy on the same machine). Use `0.0.0.0` if the proxy runs elsewhere. Werkzeug debug mode is only enabled when `FAIR_CHECKER_ENV` is `development`. |
| `BIOPORTAL_APIKEY` | optional | Enables the BioPortal checks. |
| `GITHUB_TOKEN` | optional | Avoids GitHub API rate limits when retrieving the Bioschemas profiles. |

Do not commit `.env`: it can contain secrets (`BIOPORTAL_APIKEY`, `GITHUB_TOKEN`).

#### Development instance (your computer)

Nothing is required: the default is `development`, served on `http://127.0.0.1:5000`. Set `SERVER_URL` (e.g. `SERVER_URL=http://localhost:5000`) to change the host; the port is always 5000.

```
bash
cp .env.sample .env        # optional: only needed for BIOPORTAL_APIKEY / GITHUB_TOKEN
poetry run python app.py --web
```

Results are served from `http://127.0.0.1:5000`.

#### Dev server (staging)

```
bash
# .env
FAIR_CHECKER_ENV=staging
SERVER_URL=https://fair-checker.dev.france-bioinformatique.fr
```

```
bash
poetry run python app.py --web
```

You can instead export the two variables in the shell or in the service definition (systemd, Docker, …) instead of using `.env`. `FAIR_CHECKER_ENV=staging` is required: without it the server falls back to `development`, which still honours `SERVER_URL` but is not meant for a public server. Make sure `SERVER_URL` is the **public** address of the server, and that `/eval/`, `/assessment/` and `/test/` are reachable at this address.

#### Production server

```
bash
# .env
FAIR_CHECKER_ENV=production
SERVER_URL=https://fair-checker.france-bioinformatique.fr
```

```
bash
poetry run python app.py --web
```

In production the base IRIs are fixed in `ProductionConfig` to the W3ID namespace (`https://w3id.org/fairchecker/…`), and `SERVER_URL` is only used by the web pages. The W3ID redirections of `eval/`, `assessment/` and `test/` must point to the production server.

#### Adding or changing an instance kind

Edit `config.py`: add a class that extends `Config`, define `SERVER_URL`, `EVAL_URL`, `ASSESSMENT_URL` and `TEST_URL`, and select it in `app.py` according to `FAIR_CHECKER_ENV`.

## License
FAIR-Checker is released under the [MIT License](LICENSE). Some third-party components are included. They are subject to their own licenses. All of the license information can be found in the included [LICENSE](LICENSE) file.

## Funding
This project is developed by the [French institute for Bioinformatics (IFB)](https://france-bioinformatique.fr/) ([PIA2 11-INBS-0013 grant](https://anr.fr/ProjetIA-11-INBS-0013)), the French Node of [ELIXIR](https://www.ifb-elixir.fr/en/).
