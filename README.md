[![Actions Status](https://github.com/IFB-ElixirFr/fair-checker/workflows/Unit%20testing/badge.svg)](https://github.com/IFB-ElixirFr/fair-checker/actions) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Version 1.2.3](https://img.shields.io/badge/version-v1.2.3-blue)]()

# FAIR-checker
FAIR-Checker is a tool aimed at assessing FAIR principles and empowering data provider to enhance the quality of their digital resources.

Data providers and consumers can check how FAIR are web resources. Developers can explore and inspect metadata exposed in web resources.

FAIR-Checker is a web and command line tool to assess FAIRness of web resources:

1. FAIR Checker web app, is deployed at http://fair-checker.france-bioinformatique.fr. 
1. Command line tool, is a metadata scraper and validator.
    **Usage examples :**
        python app.py --url http://bio.tools/bwa
        python app.py --bioschemas --url http://bio.tools/bwa
        python app.py --scrapp --urls http://bio.tools/bwa
        python app.py --scrapp --files file.txt

Main contributors are: 
- [Thomas Rosnet](https://github.com/thomasrosnet)
- [Alban Gaignard](https://github.com/albangaignard)
- [Marie-Dominique Devignes](https://members.loria.fr/MDDevignes/)
- [Sahar Frikha](https://github.com/sahar-frikha)

## Main features
- extracts embedded metatdata from web pages, currently supporting RDFa, JSON-LD, and microdata formats
- evaluates [FAIR metrics](https://www.go-fair.org/fair-principles/) on these metadata (supported by [Identifiers.org](https://identifiers.org/)). 
- provides a graphical summary on FAIR assesment 
- provides detailed evaluations for each metric with technical recommendations
- explore the content of metadata
- enrich metadata based on live SPARQL endpoints, currently relying on [Wikidata](https://www.wikidata.org), [OpenAIRE](https://graph.openaire.eu/develop/), and [OpenCitations](https://opencitations.net)
- evaluate if used controled vocabularies / ontologies are indexed in community registries, currently supported by [OLS](https://www.ebi.ac.uk/ols), [LOV](https://lov.linkeddata.es/dataset/lov/) and [BioPortal](https://bioportal.bioontology.org)
- evaluate [Bioschemas community profiles](https://bioschemas.org/profiles/) to check if required or recommended metadata is missing

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
This project is funded by the [French institute for Bioinformatics (IFB)](https://france-bioinformatique.fr/) through the [PIA2 11-INBS-0013 grant](https://anr.fr/ProjetIA-11-INBS-0013).
