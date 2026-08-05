<script setup>

</script>

<template>

    <footer class="p-8 bg-slate-50">
       <section class="text-center max-width">
            <div class="sponsor-row" style="max-width:100%;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:1rem;padding:0.5rem 1rem;">
                <div class="sponsor-item sponsor-logo" style="flex:1 1 10%;min-width:120px;text-align:center;">
                    <NuxtLink to="https://www.ifb-elixir.fr" style="display:inline-block;">
                        <img src="https://www.ifb-elixir.fr/wp-content/uploads/2025/08/logo-ifb-elixir.png" alt="ifb-elixir" style="max-height:6em;max-width:100%;height:auto;display:block;margin:0 auto;">
                    </NuxtLink>
                </div>
                <div class="sponsor-item sponsor-text" style="flex:2 1 15%;min-width:180px;font-family:Futura, Arial, sans-serif;font-size:0.9rem;font-weight:700;">
                  This resource is developed by<br>IFB, the French Node of ELIXIR.
                </div>
                <div class="sponsor-item sponsor-support" style="flex:1 1 30%;min-width:160px;text-align:center;font-family:Futura, Arial, sans-serif;font-size:1rem;font-weight:700;">
                        Supported by<br>
                    <div style="display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:1.2rem;margin-top:0.5rem;">
                        <img src="https://www.ifb-elixir.fr/wp-content/uploads/2025/08/logo-CNRS.png" title="Logo CNRS" alt="Logo CNRS" style="height:2em;max-width:100%;">
                        <img src="https://www.ifb-elixir.fr/wp-content/uploads/2025/08/logo-INRAe.png" title="Logo INRAE" alt="Logo INRAE" style="height:1.3em;max-width:100%;">
                        <img src="https://www.ifb-elixir.fr/wp-content/uploads/2025/08/logo-INSERM.png" title="Logo INSERM" alt="Logo INSERM" style="height:1.8em;max-width:100%;">
                        <img src="https://www.ifb-elixir.fr/wp-content/uploads/2025/08/logo-CEA.png" title="Logo CEA" alt="Logo CEA" style="height:2em;max-width:100%;">
                        <img src="https://www.ifb-elixir.fr/wp-content/uploads/2025/08/logo-France-2030.png" title="Logo France2030" alt="Logo France2030" style="height:2.3em;max-width:100%;">
                    </div>
                </div>
            </div>
       </section>

       <hr>

       <div class="content has-text-centered">
            Version: <NuxtLink to="https://github.com/IFB-ElixirFr/FAIR-checker/releases/tag/" target="_blank">v2.0.0-beta</NuxtLink> - Source code under <NuxtLink to="http://opensource.org/licenses/mit-license.php" target="_blank">MIT</NuxtLink> license - <NuxtLink to="/terms">Terms of use</NuxtLink>
       </div>

    </footer>

</template>