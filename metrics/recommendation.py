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
            identifiers for a UniProt entry is: <a href="https://identifiers.org/uniprot:P38938" target=”_blank”><u>https://identifiers.org/uniprot:P38938</u></a> with uniprot as namespace or for 
            a PubMed publication <a href="https://identifiers.org/pubmed/23584831" target=”_blank”><u>https://identifiers.org/pubmed/23584831</u></a>
             with pubmed as namespace, or DOI. This 
            identifier can be either the URL itself or encoded in the metadata as a dct:identifier or schema:identifier 
            property. Read more about persistent identifiers in the identifiers.org documentation or in the 
            <a href="https://faircookbook.elixir-europe.org/content/recipes/findability/identifiers.html" target=”_blank”><b><u>FAIR-CookBook section on identifiers</u></b></a>
             or in <a href="https://rdmkit.elixir-europe.org/identifiers#relevant-tools-and-resources" target=”_blank”><b><u>RDMkit</u></b></a>. 
        """
    },
    "F2A": {
        "reco1": """
            Structured metadata should be embedded as machine readable content into your HTML file. A variety of RDF-compliant
             options are available (<a href="https://www.w3.org/MarkUp/2009/rdfa-for-html-authors" target=”_blank”><u>RDFa</u><a>, 
             <a href="https://www.w3.org/TR/2021/NOTE-microdata-20210128/" target=”_blank”><u>microdata</u><a>, 
             <a href="https://www.w3.org/TR/json-ld11/#relationship-to-rdf" target=”_blank”><u>JSON-LD</u><a>). The standard semantic web format RDF (Resource Description 
             Framework) is a W3C standard specification for representing information in the form of (subject, predicate, object) 
             statements known as triples. This structured format, also described as (URI, property, value) for metadata, 
             enable links between multiple data on the web using controlled vocabularies. JSON-LD is widely recommended 
             as the most suitable approach for encoding RDF metadata in your web page, learn more in the <a href="https://faircookbook.elixir-europe.org/content/recipes/findability/seo.html#" target=”_blank”><b><u>FAIR-CookBook 
             section on search engine optimisation</u></b></a>, or in the <a href="https://rdmkit.elixir-europe.org/machine_actionability#what-makes-a-file-machine-actionable" target=”_blank”><b><u>RDMkit section on machine actionability.</u></b></a>
        """
    },
    "F2B": {
        "reco1": """
            You should express all your metadata with classes coming from interoperable ontologies and vocabularies: 
            use <a href="https://www.ebi.ac.uk/ols/index" target=”_blank”><u>Ontology Lookup Service</u><a>, 
            <a href="https://bioportal.bioontology.org/" target=”_blank”><u>BioPortal</u><a> or 
            <a href="https://lov.linkeddata.es/dataset/lov/" target=”_blank”><u>Linked Open Vocabularies</u><a> to find the most suitable classes 
            you want to use. Learn more in the <a href="https://faircookbook.elixir-europe.org/content/recipes/interoperability/selecting-ontologies.html" target=”_blank”><b><u>FAIR-CookBook about how to select terminologies.</u></b><a>
        """,
        "reco2": """
            You should express all your metadata with properties coming from interoperable ontologies and vocabularies: 
            use <a href="https://www.ebi.ac.uk/ols/index" target=”_blank”><u>Ontology Lookup Service</u><a>, 
            <a href="https://bioportal.bioontology.org/" target=”_blank”><u>BioPortal</u><a> or 
            <a href="https://lov.linkeddata.es/dataset/lov/" target=”_blank”><u>Linked Open Vocabularies</u><a> to find the most suitable classes 
            you want to use. Learn more in the <a href="https://faircookbook.elixir-europe.org/content/recipes/interoperability/selecting-ontologies.html" target=”_blank”><b><u>FAIR-CookBook about how to select terminologies.</u></b><a>
        """,
        "reco3": """
            You should express all your metadata with classes and properties coming from interoperable ontologies and vocabularies: 
            use <a href="https://www.ebi.ac.uk/ols/index" target=”_blank”><u>Ontology Lookup Service</u><a>, 
            <a href="https://bioportal.bioontology.org/" target=”_blank”><u>BioPortal</u><a> or 
            <a href="https://lov.linkeddata.es/dataset/lov/" target=”_blank”><u>Linked Open Vocabularies</u><a> to find the most suitable classes 
            you want to use. Learn more in the <a href="https://faircookbook.elixir-europe.org/content/recipes/interoperability/selecting-ontologies.html" target=”_blank”><b><u>FAIR-CookBook about how to select terminologies.</u></b><a>
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
            You should enrich your metadata with more diversified external links. Here we did not detect more than two 
            distinct URL authorities (= domain name, first part of the URL right after ://) among all URLs referred 
            to in your resource.
        """
    },
    "R11": {
        "reco1": """
            You should include information about licence in your metadata using one of the properties below: <br><br>
            
            Read more about licenses in FAIR-Cookbook (
            <a href="https://faircookbook.elixir-europe.org/content/recipes/reusability/ATI-licensing.html" target=”_blank”><u><b></u>licence</b></a>, 
            <a href="https://faircookbook.elixir-europe.org/content/recipes/reusability/ATI_licensing_software.html" target=”_blank”><u><b>software license</u></b></a>, 
            <a href="https://faircookbook.elixir-europe.org/content/recipes/reusability/ATI_licensing_data.html" target=”_blank”><u><b>data licence</u></b></a>)
            or in <a href="https://rdmkit.elixir-europe.org/licensing" target=”_blank”><u><b>RDMkit</u></b></a>
            <br><br>
        """,
    },
    "R12": {
        "reco1": """    
            You should include information about provenance in your metadata using one of the properties below: <br><br>
            
            Read more in <a href="https://faircookbook.elixir-europe.org/content/recipes/reusability/provenance.html?highlight=prov " target=”_blank”><u><b>FAIR-Cookbook section on provenance.</u></b></a>
            <br><br>
         """,
    },
    "R13": {
        # Calling F2B
    },
}
