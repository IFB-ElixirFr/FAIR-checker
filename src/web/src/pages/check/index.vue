<script setup>

    import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
    import { faLink } from '@fortawesome/free-solid-svg-icons'

    import { ref, watch } from 'vue'

    const resourceUrl = ref('')
    const isResourceUrlValid = ref()
    
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
            </section>
        </div>
    </div>

</template>
