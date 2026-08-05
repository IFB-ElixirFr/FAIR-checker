<script setup>

    import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
    import { faCheck, faSearch } from '@fortawesome/free-solid-svg-icons'

</script>
<template>

    <section class="pt-20 hero">
        <div class="hero-body has-text-centered">
            <p class="title">FAIR-Checker</p>
            <p>
                Improve the FAIRness of your web resources
            </p>
        </div>
    </section>

    <div class="columns is-centered">
        <div class="column is-four-fifths">
            <section class="section">
            
                <div class="columns is-centered is-vcentered">
                    <div class="column is-two-thirds">
                        <div class="section">
                            <h2 class="title">Welcome</h2>
                            <div class="block">
                                <p class="subtitle">FAIR-Checker is a tool aimed at assessing FAIR principles and empowering data provider to enhance the quality of their digital resources.</p>
                                <p class="subtitle">Data providers and consumers can <b class="has-text-ifb-green">check</b> how FAIR are web resources. Developers can explore and <b class="has-text-ifb-blue">inspect</b> metadata exposed in web resources.</p>
                            </div>
                            <div class="flex gap-2">
                                <NuxtLink id="landing_check" class="flex gap-2 button is-success is-large" to="/check">
                                    <span>Check</span>
                                    <FontAwesomeIcon :icon="faCheck" />
                                </NuxtLink>
                                <NuxtLink class="flex gap-2 button is-info is-large" to="/inspect">
                                    <span>Inspect</span>
                                    <FontAwesomeIcon :icon="faSearch" />
                                </NuxtLink>
                            </div>
                        </div>
                    </div>
                    <div class="column is-one-third">
                        <img src="../assets/fc.png">
                    </div>
                </div>

                <div class="section">
                    <h2 class="title">Inspect: how it works ?</h2>
                    <hr>
                    <div class="block">
                        FAIR-Checker leverages semantic web technologies to check that metadata use standards
                        and recognized ontologies or controlled vocabularies.
                    </div>

                    <div class="block">
                        First, embedded semantic annotations are extracted from web pages, forming a minimal knowledge graph (Step 1). Then,
                        this minimal knowledge graph is completed based on already deployed knowledge graphs:
                        <NuxtLink to="https://datacite.org/">Datacite</NuxtLink>, <NuxtLink to="https://www.openaire.eu/">OpenAire</NuxtLink>,
                        <NuxtLink to="https://www.wikidata.org/wiki/Wikidata:Main_Page">WikiData</NuxtLink>
                        (Step 2). Finally (Step 3), the resulting knowledge graph is tested to check that classes and properties are
                        recognized through <NuxtLink to="https://lov.linkeddata.es/dataset/lov/">Linked Open Vocabularies (LOV)</NuxtLink>,
                        <NuxtLink to="https://www.ebi.ac.uk/ols/index">Ontology Lookup Service (OLS)</NuxtLink>, or
                        <NuxtLink to="https://bioportal.bioontology.org/">Bioportal</NuxtLink>. The last
                        verification (Step 4) consists in validating the resource metadata against
                        <NuxtLink to="https://bioschemas.org/profiles/">Bioschemas community profiles</NuxtLink>.
                    </div>
                    <div class="block ">
                        The metadata assesment flow:
                    </div>

                    <div class="block has-text-centered">
                        <figure class="image">
                            <img class="is-bordered" src="../assets/pres_fc.png">
                        </figure>
                    </div>
                </div>

                <div class="section">
                    <h2 class="title">Resources</h2>
                    <hr>
                    <div class="columns is-vcentered">
                        <div class="column has-text-centered">
                          <NuxtLink to="https://doi.org/10.1186/s13326-023-00289-5" target="_blank">
                              <img class="is-bordered" src="../assets/fc_paper.png" width="96">
                          </NuxtLink>
                        </div>
                        <div class="column is-10">
                            Gaignard, A., Rosnet, T., de Lamotte, F., Lefort, V., & Devignes, M. (2023). 
                            <b>FAIR-Checker: supporting digital resource findability and reuse with Knowledge Graphs and Semantic Web standards.</b> 
                            <i>Journal of Biomedical Semantics, 14.</i>
                            <NuxtLink to="https://doi.org/10.1186/s13326-023-00289-5" target="_blank">https://doi.org/10.1186/s13326-023-00289-5</NuxtLink>
                        </div>
                      </div>
                  
                    <div class="columns is-vcentered">
                      <div class="column has-text-centered">
                        <NuxtLink to="../assets/FAIR_Checker_poster.pdf" target="_blank">
                            <img class="is-bordered" src="../assets/FAIR_Checker_poster.png" width="96">
                        </NuxtLink>
                      </div>
                      <div class="column is-10">
                        Rosnet, Thomas, Lefort, Vincent, Devignes, Marie-Dominique, & Gaignard, Alban. (2021). <b>FAIR-Checker, a web tool
                        to support the findability and reusability of digital life science resources.</b> <i>JOBIM (JOBIM)</i>, Paris.
                        <NuxtLink to="https://doi.org/10.5281/zenodo.5914307" target="_blank">https://doi.org/10.5281/zenodo.5914307</NuxtLink>
                      </div>
                    </div>

                    <div class="columns is-vcentered">
                      <div class="column has-text-centered">
                        <NuxtLink to="../assets/Slides_FAIR_checker-2021.pdf" target="_blank">
                            <img class="is-bordered" src="../assets/Slides_FAIR_checker-2021.png" width="96">
                        </NuxtLink>
                      </div>
                      <div class="column is-10">
                        Gaignard, Alban, Rosnet, Thomas, de Lamotte, Frédéric, & Devignes, Marie-Dominique. (2021, June 4). <b>Automatic
                        evaluation of FAIR metrics.</b> <i>Elixir All-Hands meeting</i>.
                        <NuxtLink to="https://doi.org/10.5281/zenodo.5914367" target="_blank">https://doi.org/10.5281/zenodo.5914367</NuxtLink>
                      </div>
                    </div>
                </div>

                <div class="section">
                    <h2 class="title">Funding</h2>
                    <hr>
                    <p>
                        This project is funded by the French institute for Bioinformatics (<NuxtLink to="https://france-bioinformatique.fr"
                        target="_blank">IFB</NuxtLink>) through the <NuxtLink to="https://anr.fr/ProjetIA-11-INBS-0013" target="_blank">PIA2
                        11-INBS-0013</NuxtLink> grant.
                    </p>
                </div>

            </section>
        </div>
    </div>


</template>
