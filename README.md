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

## Install

### Necessary software tools 

Before installing FAIR-Checker make sure you have the following software tools installed on you machine.

- git
- micromamba
- Google Chrome Webrowser

> [!NOTE]
> You won't be able to run FAIR-Checker correctly without them one of these tool missing.

### Cloning the project 

```
bash
git clone https://github.com/IFB-ElixirFr/fair-checker.git
cd fair-checker

```

### Install micromamba

```
bash
curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
```

### Creating and activating the micromamba enviromnent

```
bash
micromamba create --file environment.yml
```

```
bash
micromamba activate fair-checker-env
```

### Install Google Chrome

```
bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

### Fixing missing system binaries

Sometimes, other system binaries need to be installed in the host machine to make the project run without any error. 
If you encounter any error with the installation process, run this command:

```
bash
sudo apt install -y \
  fonts-liberation \
  libnss3 \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  libasound2 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  ca-certificates
```

### Start the mongodb 

Using the terminal where the `fair-checker-env` is active, launch the following command:

```
bash
mongod --dbpath data
```

### Start FAIR-Checker

In an other terminal, launch the project in a dev environment

```
bash
micromamba activate fair-checker-env
./launch_dev.sh
```

Go to [http://localhost:5000](http://localhost:5000) to see FAIR-Checker web interface. 
Depending on the security profile of your web browser, some cors error can block FAIR Checker core features. We advise using the default Google Chrome configuration to prevent any error.

## License
FAIR-Checker is released under the [MIT License](LICENSE). Some third-party components are included. They are subject to their own licenses. All of the license information can be found in the included [LICENSE](LICENSE) file.

## Funding
This project is funded by the [French institute for Bioinformatics (IFB)](https://france-bioinformatique.fr/) through the [PIA2 11-INBS-0013 grant](https://anr.fr/ProjetIA-11-INBS-0013).
