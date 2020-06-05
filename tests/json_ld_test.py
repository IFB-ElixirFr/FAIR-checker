from rdflib import ConjunctiveGraph

sample_1 = """
{
  "@context": "https://schema.org/docs/jsonldcontext.json",
  "@type": "Person",
  "name": "Jane Doe",
  "jobTitle": "Professor",
  "telephone": "(425) 123-4567",
  "url": "http://www.janedoe.com"
}
"""

sample_2 = """
{
  "@context": "http://schema.org/",
  "@type": "Person",
  "name": "Jane Doe",
  "jobTitle": "Professor",
  "telephone": "(425) 123-4567",
  "url": "http://www.janedoe.com"
}
"""

if __name__ == '__main__':

    g1 = ConjunctiveGraph()
    g1.parse(data=sample_1, format="json-ld")
    print(g1.serialize(format="turtle").decode())

    g2 = ConjunctiveGraph()
    g2.parse(data=sample_2, format="json-ld")
    print(g2.serialize(format="turtle").decode())

