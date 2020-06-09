# fair-checker

Web tool to assess FAIR principles and promote their implementation.

## Monitoring progress in FAIRification through self-assessment of resources maturity indicators

### FAIRMetrics based part

This demo is based on the FAIRMetrics framework [Wilkinson, Dumontier et al., Scientific Data 6:174] that is composed of Maturity Indicators (MI), compliance tests and the evaluator application itself. For now, few efforts have been done so far to take advantage from their concrete implementation, in the process of improving FAIRness of users/community resources. Furthermore, this does not provide concrete help or guidelines to developers for better sharing their published works. In this work we propose a web demonstrator, leveraging existing web APIs, aimed at i) evaluating FAIR maturity indicators and ii) providing hints to progress in the FAIRification process.

### Custom part

These FAIR checks aim at leveraging semantic web technologies to check that metadata use standards and recognized ontologies or controlled vocabularies.

First, embedded semantic annotations are extracted from web pages, forming a minimal knowledge graph. Then, these knowledge are completed based on already deployed knowledge graphs (Datacite, OpenAire, WikiData). Finally, the resulting knowledge graph is tested to check that classes and properties are recognized through Linked Open Vocabularies (LOV), or Ontology Lookup Service (OLS).

## Installation

Create a new conda ENV

Activate the new ENV

Run: 
- while read requirement; do conda install  conda-forge --yes $requirement || pip install $requirement; done < requirements.txt
