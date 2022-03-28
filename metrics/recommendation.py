json_rec = {
    "A11": {
        "reco1": """
            You should access your resource through HTTP or HTTPS protocol
        """,
        "reco2": """
            Ensure that the resource is accessible using the provided URL (typos ? dead link ? other reason ?)
        """,
    },
    "F1A": {
        "reco1": """
            The webpage you are evaluating is not reachable. You should make sure that it can be reached properly with 
            an HTTP request.
        """,
    },
    "F1B": {
        "reco1": """
            To ensure that the used identification scheme is persistent, you should build your resource ID with a 
            namespace that can be found in Identifiers.org  (life-science oriented registry). Examples of persistent 
            identifiers for a UniProt entry is: https://identifiers.org/uniprot:P38938 with uniprot as namespace or for 
            a PubMed publication https://identifiers.org/pubmed/23584831 with pubmed as namespace, or DOI. This 
            identifier can be either the URL itself or encoded in the metadata as a dct:identifier or schema:identifier 
            property. Read more about persistent identifiers in the identifiers.org documentation or in the 
            FAIR-CookBook section on identifiers. 
        """
    },
    "F2A": {
        "reco1": """
            Structured metadata should be embedded as machine readable content into your HTML file. A variety of RDF-compliant options are available (RDFa, microformat, JSON-LD). The standard semantic web format RDF (Resource Description Framework) is a W3C standard specification for representing information in the form of (subject, predicate, object) statements known as triples. This structured format, also described as (URI, property, value) for metadata, enable links between multiple data on the web using controlled vocabularies. JSON-LD is widely recommended as the most suitable approach for encoding RDF metadata in your web page, learn more in the FAIR-CookBook section on search engine optimisation.
        """
    },
    "F2B": {
        "reco1": """
            You should express all your metadata with classes coming from interoperable ontologies and vocabularies: 
            use Ontology Lookup Service, BioPortal or Linked Open Vocabularies to find the most suitable classes 
            you want to use. Learn more in the FAIR-CookBook about how to select terminologies.
        """,
        "reco2": """
            You should express all your metadata with properties coming from interoperable ontologies and vocabularies:
             use Ontology Lookup Service, BioPortal or Linked Open Vocabularies to find the most suitable 
             properties you want to use. Learn more in the FAIR-CookBook about how to select terminologies.
        """,
        "reco3": """
            You should express all your metadata with classes and properties coming from interoperable ontologies and 
            vocabularies: use Ontology Lookup Service, BioPortal or Linked Open Vocabularies to find the most suitable 
            classes or properties you want to use. Learn more in the FAIR-CookBook about how to select terminologies.
        """,
    },
    "I1A": {
        # Calling F1A
    },
    "I1B": {
        # Calling F1B
    },
    "I2A": {
        "reco1": """
            Essential metadata are missing to describe your resource in a human-readable way. You should provide at lead one property from the following list: <br><br>
        """,
        "reco2": """
            Your metadata seem to not be conforming to the researched format, which is RDF (Resource Description Framework), 
            Resource Description Framework a W3C standard specification for representing information in the form of 
            subject / predicate / object statements known as triples.
            This structured format enable links between multiple data on the web using controlled
            vocabularies, learn more here:
            https://www.w3.org/TR/rdf11-primer/
        """,
    },
    "I2B": {
        # Calling F2A
    },
    "I3": {
        "reco1": """
            You should enrich your metadata with more diversified external links. Here we did not detect more than two distinct URL authorities (= domain name, first part of the URL right after ://) among all URLs referred to in your resource.
        """
    },
    "R11": {
        "reco1": """
            You should include information about licence in your metadata using one of the following properties: <br><br>
        """,
    },
    "R12": {
        "reco1": """            
            You should include information about provenance in your metadata using one of the following properties: <br><br>
         """,
    },
    "R13": {
        # Calling F2B
    },
}
