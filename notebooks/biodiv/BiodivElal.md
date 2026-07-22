ELIXIR Commissioned Service [2024-SCIENCE-BFSP, Work Package 6 - BioDiv-FAIR-Checker: Raising FAIRness of European
biodiversity data through ELIXIR-aligned standards, services, and training

# M6.2 Preliminary FAIR assessment of biodiversity data resources

## Executive summary

Biodiversity data are crucial for understanding and conserving the natural world, yet they are often fragmented,
heterogeneous, and difficult to reuse. The FAIR principles provide a framework for improving the management and sharing
of biodiversity data. However, generic FAIR assessment tools may not capture the specific needs and practices of
biodiversity communities. To address this gap, the BioDiv-FAIR-Checker (BioDiv-FC) project aims to enhance the FAIRness
assessment of biodiversity data by developing biodiversity-aware profiles and machine-actionable recommendations. In
this report, we present the results of a preliminary FAIR assessment of biodiversity data resources using the
FAIR-Checker tool. We evaluated a sample of biodiversity data resources, including ERGA, BOLD, LifeWatch ERIC, eLTER,
and DiSSCo. The obtained global FAIR scores ranged from 16.7% to 45.8%, with most resources lacking machine-readable
metadata, which is essential for their FAIRness. This highlights the need for better metadata management and sharing
practices in the context of biodiversity data, as proposed by the BioDiv-FC project.

## Supporting documents

- [https://link.springer.com/article/10.1186/s13326-023-00289-5](https://link.springer.com/article/10.1186/s13326-023-00289-5)
- [kick-off meeting slides](TODO: )

## Introduction

Biodiversity data are crucial for understanding and conserving the natural world, yet they are often fragmented,
heterogeneous, and difficult to reuse. The FAIR principles provide a framework for improving the management and sharing
of biodiversity data. However, generic FAIR assessment tools may not capture the specific needs and practices of
biodiversity communities. To address this gap, the BioDiv-FAIR-Checker (BioDiv-FC) project aims to enhance the FAIRness
assessment of biodiversity data by developing biodiversity-aware profiles and machine-actionable recommendations.

However, to measure the success of BioDiv-FC, it is essential to make an initial, even naïve, FAIR assessment of typical
biodiversity resources. This will provide a baseline for comparison and help identify areas for improvement. The goal of
this document is to present the results of a preliminary FAIR assessment of biodiversity data resources, using the
FAIR-Checker tool, and to discuss the implications for the BioDiv-FC project.

## Methods

**FAIR assesment tool**. FAIR-checker is a web-based tool that evaluates the FAIRness of web accessible digital
resources. Users submit web page URLs or DOIs, which are resolved as web pages. FAIR-Checker then consumes emnbedded
metadata to assess FAIRness of the intially submitted URLs. It provides both a global score and fine grained results for
each of the FAIR sub-principles. FAIR-Checker follows web search engines recommendations for describing the content of
web pages with semantic metadata, including but not limited to Schema.org. Technically, it consumes RDF metadata either
expressed in RDFa, microdata or JSON-LD formats. In addition to a web interface, FAIR-Checker also provides a web API
for batch processing and integration with other tools. For this preliminary assessment, we used the FAIR-Checker API
into a Jupyter notebook [1](https://github.com/IFB-ElixirFr/FAIR-checker/blob/master/notebooks/BiodivEval.ipynb) to
evaluate the FAIRness of a sample of biodiversity data resources.

**Benchmark dataset**. During the BioDiv-FC project kick-off meeting, we dicsussed with all project partners the most
relevant biodiversity data repositories and the kind of hosted resources. Project milestone M6.1 more precisely
describes the evaluated data repositories. The selected resources include:

1. *ERGA*, which relies on the ENA and BioSamples regitries to actualy store sequences as well as sample metadata. Four
   web resources were identified:
    - ERGA entry: https://portal.erga-biodiversity.eu/organism/SAMEA112797446,
    - ENA entry: https://www.ebi.ac.uk/ena/browser/view/SAMEA112797446,
    - BioSamples entry: https://www.ebi.ac.uk/biosamples/samples/SAMEA112797446,
    - BioSamples structured data entry:  https://www.ebi.ac.uk/biosamples/samples/SAMEA112797446.ldjson
2. *BOLD (from the iBOL consortium)*, which makes accessible individual records through barcodes as well as full
   datasets. Two web resources were identified:
    - BOLD entry: http://portal.boldsystems.org/record/CHOLH011-12
    - BOLD dataset: https://doi.org/10.5883/DP-Latest
3. *LifeWatch ERIC*,
    - https://metadatacatalogue.lifewatch.eu/srv/eng/catalog.search#/metadata/dc512697-ed50-40c5-a3cd-1774000444b9
4. *eLTER*,
    - https://doi.org/10.82159/gt66-zt98
5. *DiSSCo*,
    - https://doi.org/10.3535/ZVR-CRA-1Y1
    - https://doi.org/10.3535/ZVR-CRA-1Y1?noredirect

## Results

Figure 1 shows the FAIR scores obtained for each of the evaluated resources. The obtained global scores range from 16.7%
to 45.8%. All, except one, of the evaluated resources obtained a score a very limited score of 16.7%. Since they are web
accessible, they are all considered by FAIR-Checker as compliant with the F1A and A1.1 sub-principles, but they all fail
to comply with the other sub-principles, which results in a very low global score. In practice, this means that
FAIR-Checker was not able to find and consume any machine-readable metadata for these resources, which is a critical
issue for their FAIRness.

We have been trying the LifeWatch RDF export
(https://metadatacatalogue.lifewatch.eu/srv/api/records/dc512697-ed50-40c5-a3cd-1774000444b9/formatters/rdf?output=xml)
that should be consumable by FAIR-Checker, but it is not valid RDF/XML and therefore cannot be processed. This is
clearly a technical issue that can be easily fixed, but it also highlights the importance of providing valid machine
readable metadata for FAIRness as well as automated tools for checking the validity of metadata.

Only one resource (the biosamples entry) obtained a reasonable score above 40%, meaning that FAIR-Checker was able to
find and consume metadata. All individual metrics are reported here in a machine readable
format: [![45.83 % FAIR](https://img.shields.io/badge/FAIR_assessment-45.83_%25-red)](https://fair-checker.france-bioinformatique.fr/assessment/69b03f8620ba293e5fcf95f0).
Most noticeably, the biosample entry is missing a reference to a license (A1.2, R1.1) and to a provenance (R1.2), which
are critical for the reuse of the data.

## Discussion and future works

This preliminary assessment of the FAIRness of biodiversity data resources using the FAIR-Checker tool highlights
several critical issues. First, most of the evaluated resources lack machine-readable metadata, which is essential for
their FAIRness. This suggests that there is a need for better metadata management and sharing practices in the
biodiversity community. For data registries under active development, such as ERGA, it would be intersting to instrument
the HTML rendering code with JSON-LD content following the Bioschemas recommendation. This would allow to significantly
improve the FAIRness with a minimal development effort, and benefiting from other flagship Elixir resources such as
TeSS, bio.tools or workflowhub.

Second, even when metadata is available it may not be complete (BioSamples registry) or compliant with standards
(LifeWatch ERIC), which can hinder the reuse of the data. This underscores the importance of developing
biodiversity-aware profiles and machine-actionable recommendations to improve the FAIRness of biodiversity data.

As a continuation of this work, within the BioDiv-FAIRChecker project, we plan to:

1. Update the Bioschemas BioSample profile with Biodiversity community needs in terms of mandatory, recommended and
   optional properties, following the most used ENA checklists.
2. Develop a FAIR-Checker biodiversity plugin that will
    1. provide biodiversity-specific recommendations for the generic FAIR assessment results
    2. implement through SHACL a set of biodiversity-specific metadata completeness checks, based on the updated
       Bioschemas profile, and ENA checklists.
3. Improve metadata retrieval from external sources, by leveraging DataCite content negociation or the FAIR Signposting
   approach.


