<script setup>
    
    // Necessary Imports
    import { ref, watch } from 'vue'

    // Icon imports
    import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
    import { faLink } from '@fortawesome/free-solid-svg-icons'

    // Chart JS import 
    import {
      Chart as ChartJS,
      RadialLinearScale,
      PointElement,
      LineElement,
      Filler,
      Tooltip,
      Legend
    } from 'chart.js'
    
    import { Radar } from 'vue-chartjs'
    
    ChartJS.register(
      RadialLinearScale,
      PointElement,
      LineElement,
      Filler,
      Tooltip,
      Legend
    )

    // States
    const resourceUrl = ref('')
    const isResourceUrlValid = ref()
    const fairEvaluatedValues = ref([12, 76, 23, 65])

    const chartData = computed(() => ({
      labels: [
        'Findable',
        'Interoperable',
        'Reusable',
        'Accessible'
      ],
    
      datasets: [
        {
          label: 'Success',
          data: fairEvaluatedValues.value,
    
          borderWidth: 2,
          borderColor: 'rgba(75, 192, 192, 1)',
          backgroundColor: 'rgba(219, 242, 242, 0.5)',
    
          pointRadius: 5,
          pointHitRadius: 50,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: 'rgba(75, 192, 192, 1)'
        }
      ]
    }))

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
    
      scales: {
        r: {
          min: 0,
          max: 100,
    
          ticks: {
            stepSize: 20
          }
        }
      },
    
      plugins: {
        tooltip: {
          callbacks: {
            title: (tooltipItems) => {
              return tooltipItems[0].label
            },
    
            label: (tooltipItem) => {
              return `${tooltipItem.raw} %`
            }
          }
        }
      },
    
      animation: {
        duration: 500
      }
    }
    
    function checkUrlValidity() {
      try {
        const url = new URL(resourceUrl.value)
    
        isResourceUrlValid.value =
          url.protocol === 'http:' || url.protocol === 'https:'
      } catch {
        isResourceUrlValid.value = false
      }
    }

    watch(resourceUrl, () => {
      checkUrlValidity()
    })
    
</script>
<template>

    <section class="pt-20 hero">
        <div class="hero-body has-text-centered">
            <p class="title">Check</p>
            <p>
                FAIR assessment of web resources 
            </p>
        </div>
    </section>
    <div class="columns is-centered">
        <div class="column is-four-fifths">
            <section class="section">
                <article class="message">
                    <div class="message-body is-check">
                      <h1 class="subtitle"><b>Resource identifier (URL/DOI)</b></h1>
                      <div class="field has-addons">
                        <div class="control is-expanded">

                          <div class="control has-icons-left has-icons-right">
                            <input 
                                :class="[
                                    'input', 
                                    'is-large',
                                    {
                                        'is-danger': !isResourceUrlValid && resourceUrl !== '',
                                        'is-success': isResourceUrlValid
                                    }
                                ]"
                                v-model="resourceUrl"
                                type="text" 
                                placeholder="FAIR resource URL or DOI"
                            >
                            <span class="icon is-small is-left">
                              <FontAwesomeIcon :icon="faLink" />
                            </span>
                            <span class="icon is-small is-right">
                              <i id="url_statut" class="fa"></i>
                            </span>
                          </div>
                          <div class="help_wrapper"><span id="url_helper" class="help"></span><span class="help" id="is_doi"></span></div>
                        </div>
                        <div class="field is-grouped is-grouped-centered">
                          <p class="control">
                            <button 
                                :disabled="!isResourceUrlValid" 
                                class="button is-info is-large"
                            >
                                <i class="fa fa-bar-chart fa-fw"></i>&nbsp;All
                                metrics
                            </button>
                          </p>
                        </div>
                      </div>
                      <span v-if="isResourceUrlValid && resourceUrl !== ''" class="help is-success">Valid URL/DOI</span>
                      <span v-if="!isResourceUrlValid && resourceUrl !== ''" class="help is-danger">The URL/DOI is not valid</span>
                      <br>

                      <div class="columns is-centered is-vcentered">
                        <div class="column is-half">
                          <progress id="p1" class="progress is-primary is-centered" value="0" max="12"></progress>

                        </div>
                        <div class="column is-narrow">
                          <p class="control">
                            <button onClick="window.location.reload();" class="button is-primary is-small"><i
                                class="fa fa-undo fa-fw"></i>&nbsp;Clean
                              results
                            </button>
                          </p>
                        </div>
                      </div>
                      <!-- This is the small panel with the url that you can use to test quickly -->   
                      <!-- TODO later when the app will be able to perform checks using the API -->
                      <!--{% for k in sample_data.keys() %} --> 
                      <!--
                      <div class="columns is-centered">
                        <div class="column is-narrow">
                          <div class="panel">
                            <div class="panel-block is-centered is-vcentered">
                              <div class="field is-grouped ">
                                {% for s in sample_data[k] %}
                                <p id="resource_{{k}}_{{loop.index}}" class="control"><a class="button is-small is-text"
                                    data-url="{{ s.url }}">{{ s.text }}</a></p>
                                {% endfor %}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                      {% endfor %}
                      -->
                    </div>
                </article>

                <article id="radar_chart" class="message">
                  <div class="message-body is-check">
                    <h1 class="subtitle"><b>FAIR compliance</b></h1>
                    <div class="content">
                        <div class="h-96">
                            <Radar
                                :data="chartData"
                                :options="chartOptions"
                            />
                        </div>
                    </div>
                    <h1 class="subtitle is-hidden" id="share_title"><b>Share your results</b></h1>
                    <div class="content" id="fair_badge"></div>
                    <div class="content has-text-light has-background-dark is-size-7" id="fair_badge_html"></div>
                    <div class="content has-text-light has-background-dark is-size-7" id="fair_badge_md"></div>
                  </div>
                </article>
                
                
                <article id="metrics_details_rec" class="message">
                  <div class="message-body is-check">
                    <h1 class="subtitle is-inline-block"><b>Detailed results</b></h1>
                    <button id="download_csv" data-dl="{{ uuid }}" download="results.csv" class="button is-info is-small is-pulled-right" disabled><i class="fa fa-download fa-fw"></i>&nbsp;Export</button>
                
                    <!--<div class="content">{% include 'metrics_table.html' %}</div>-->
                    <br>
                    <div class="content">
                        Did not find your metadata term ?
                        Please submit a request and let's discuss with the community !
                        <a href='https://github.com/IFB-ElixirFr/FAIR-checker/issues/new?assignees=albangaignard&labels=new+term&projects=&template=missing-ontology-term.md&title=YYY+ontology+term+should+be+evaluated+by+FAIR-Checker+' target="_blank">
                            <button id="new_term_button" class="button is-dark is-small is-outlined"><i class="fa fa-github fa-fw"></i>Ask for a new term</button>
                        </a>
                    </div>
                    <div class="content">
                      For additional tips and recommendations, please look at the FAIR Cookbook:
                      <a href="https://fairplus.github.io/the-fair-cookbook/content/home.html" target="_blank"
                        rel="noopener noreferrer">
                          <button id="fair_cookbook_button" class="button is-dark is-small is-outlined"><i class="fa fa-book fa-fw"></i>FAIR Cookbook</button>
                      </a>
                    </div>
                  </div>
                </article>

            </section>
        </div>
    </div>

</template>
