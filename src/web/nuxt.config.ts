// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: "src",
  pages: true,
  ssr: true,
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss", "@nuxt/icon", "nuxt-shiki"],
  shiki: {
    bundleThemes: ["ayu-dark"]
  },
  runtimeConfig: {
    public: {
        appName: "ABRomicsKG",
        hostUrl: typeof process.env.NUXT_PUBLIC_HOST_URL === "undefined" ? "http://localhost:3000" : process.env.NUXT_PUBLIC_HOST_URL,
        graphServerUrl: typeof process.env.NUXT_PUBLIC_HOST_URL === "undefined" ? "http://localhost:7200/" : process.env.NUXT_PUBLIC_HOST_URL + '/graphdb/',
        apiUrl: typeof process.env.NUXT_PUBLIC_API_HOST === "undefined" ? "http://localhost:5000/graph-api" : process.env.NUXT_PUBLIC_HTTP + process.env.NUXT_PUBLIC_API_HOST + ":" + process.env.NUXT_PUBLIC_API_PORT + '/' + process.env.NUXT_PUBLIC_API_BASEPATH
    }
  },
  routeRules: {
    '/': { appLayout: 'wide' }    
  }
})
