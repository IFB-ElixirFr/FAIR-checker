<script setup>

    import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
    import { faGithub } from '@fortawesome/free-brands-svg-icons'

</script>
<template>

    <nav id="fc_navbar" class="navbar is-fixed-top is-light" role="navigation" aria-label="main navigation">
      <div class="navbar-brand">
        <div class="navbar-item is-flex is-align-items-center">
          <NuxtLink to="/">
            <img src="assets/logo-FAIR-Checker.png" width="140"/>
          </NuxtLink>
          <NuxtLink href="https://www.ifb-elixir.fr/">
            <img src="assets/by-IFB.png" width="100"/>
          </NuxtLink>
        </div>
        <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false" data-target="navbarBasicExample">
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
          <span aria-hidden="true"></span>
        </a>
      </div>
      <div class="navbar-menu">
        <div class="navbar-start">
          <NuxtLink class="navbar-item" href="/check">Check</NuxtLink>
          <NuxtLink class="navbar-item" href="/inspect">Inspect</NuxtLink>
          <NuxtLink class="navbar-item" href="/about">About us</NuxtLink>
          <NuxtLink class="navbar-item" href="/swagger">API</NuxtLink>
        </div>
        <div class="navbar-end">
          <NuxtLink class="navbar-item" to="/docs" target="_blank">Documentation</NuxtLink>
          <NuxtLink class="navbar-item" to="/statistics">Statistics</NuxtLink>
          <NuxtLink class="navbar-item" to="https://github.com/IFB-ElixirFr/fair-checker/issues" target="_blank">Feedbacks</NuxtLink>
          <NuxtLink class="navbar-item" to="https://github.com/IFB-ElixirFr/fair-checker" target="_blank">
            <FontAwesomeIcon :icon="faGithub" />Github
          </NuxtLink>
        </div>
      </div>
    </nav>

</template>