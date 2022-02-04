json_rec = {
    "A11": {
        "reco1": """
            Ensure that the resource is accessible using the provided URL
        """,
        "reco2": """
            You may consider to use the HTTP protocol
        """,
    },
    "F1A": {
        "reco1": """
            The URI is valid, but doesn't contains a DOI, you may want to have an URL tht refer to a DOI
        """,
        "reco2": """
            Ensure that the url you used is valid.
        """,
    },
    "F1B": {
        "reco1": """
            You should use a namespace that can be found in Identifiers.org
            here: https://registry.identifiers.org/registry#!
        """
    },
    "F2A": {
        "reco1": """
            Your metadata seem to not be conforming to the researched format, which is RDF (Resource Description Framework), 
            Resource Description Framework a W3C standard specification for representing information in the form of 
            subject / predicate / object statements known as triples.
            This structured format enable links between multiple data on the web using controlled
            vocabularies, learn more here:
            https://www.w3.org/TR/rdf11-primer/
        """
    },
    "F2B": {
        "reco1": """
            Maybe you should try to find a similar class to the one you used that can be found in one of the
             registry.
        """,
        "reco2": """
            Maybe you should try to find a similar property to the one you used that can be found in one of the
             registry.
        """,
        "reco3": """
            You should try to use standard classes and properties, controlled vocabularies that are defined 
            and used by the community. These standards can be found in the following registries: "Ontology Lookup 
            Service", "Linked Open Vocabulary", and BioPortal.
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
            You should look to annotate your metadata with one of the property that can be found in
            the following list: <br><br>""",
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
            You should add other external links that uses different domains name from what you already have.
        """
    },
    "R11": {
        "reco1": """
            You should look to annotate your metadata with one of the licence properties that can be found in 
            the following list: <br><br>
        """,
    },
    "R12": {
        "reco1": """            
            You should look to annotate your metadata with one of the provenance properties that can be found in
            the following list: <br><br>     
         """,
    },
    "R13": {
        # Calling F2B
    },
}
