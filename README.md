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

In a production environment the process is similar but Python 3.12 has to be used for the Fair-Checker application. Moreover the ```FLASK_ENV``` envrionment variable needs to be defined as well in the terminal. The environment variable such as the ```SERVER_IP``` also need to be editied from ```.env.sample``` file to fit the url of your deployment server. The ```.env.sample``` file also has to be renamed ```.env```

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
export FLASK_ENV=production
poetry run python app.py --web
```

## License
FAIR-Checker is released under the [MIT License](LICENSE). Some third-party components are included. They are subject to their own licenses. All of the license information can be found in the included [LICENSE](LICENSE) file.

## Funding
This project is developed by the [French institute for Bioinformatics (IFB)](https://france-bioinformatique.fr/) ([PIA2 11-INBS-0013 grant](https://anr.fr/ProjetIA-11-INBS-0013)), the French Node of [ELIXIR](https://www.ifb-elixir.fr/en/).
