[![Actions Status](https://github.com/IFB-ElixirFr/fair-checker/workflows/Build%20and%20test/badge.svg)](https://github.com/IFB-ElixirFr/fair-checker/actions) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Version 1.0.1](https://img.shields.io/badge/version-v1.0.1-blue)]()


# FAIR-checker
FAIR-Checker is a tool aimed at assessing FAIR principles and empowering data provider to enhance the quality of their digital resources.

Data providers and consumers can check how FAIR are web resources. Developers can explore and inspect metadata exposed in web resources.

FAIR-Checker is deployed at [http://fair-checker.france-bioinformatique.fr](http://fair-checker.france-bioinformatique.fr).

Main contributors are: 
- [Thomas Rosnet](https://github.com/thomasrosnet)
- [Alban Gaignard](https://github.com/albangaignard)
- [Marie-Dominique Devignes](https://members.loria.fr/MDDevignes/)


## Main features
- extract embedded metadata from web pages, currently supporting RDFa, JSON-LD, and microdata formats
- evaluate [FAIR metrics](https://www.go-fair.org/fair-principles/) on these metadata 
- provide a graphical summary on FAIR assesment 
- provide detailed evaluations for each metric with technical recommendations
- explore the content of metadata
- enrich metadata based on live SPARQL endpoints, currently relying on [Wikidata](https://www.wikidata.org), [OpenAIRE](https://graph.openaire.eu/develop/), and [OpenCitations](https://opencitations.net)
- evaluate if used controled vocabularies / ontologies are indexed in community registries, currently supported by [OLS](https://www.ebi.ac.uk/ols), [LOV](https://lov.linkeddata.es/dataset/lov/) and [BioPortal](https://bioportal.bioontology.org)
- evaluate [Bioschemas community profiles](https://bioschemas.org/profiles/) to check if important metada is missing
## Known bugs
- too few results retrieved from external SPARQL endpoints

## Contribute
Please submit GitHub issues to provide feedback or ask for new features, and contact us for any related question.


## Install
### With Conda 
```
git clone https://github.com/IFB-ElixirFr/fair-checker.git
cd fair-checker
conda create --name fair-checker-env --file requirements.txt
conda activate fair-checker-env
pip install extruct

./launch_dev.sh
```

## License
FAIR-Checker is released under the [MIT License](LICENSE). Some third-party components are included. They are subject to their own licenses. All of the license information can be found in the included [LICENSE](LICENSE) file.

## Funding
This project is funded by the [French institute for Bioinformatics (IFB)](https://france-bioinformatique.fr/) through the [PIA2 11-INBS-0013 grant](https://anr.fr/ProjetIA-11-INBS-0013).