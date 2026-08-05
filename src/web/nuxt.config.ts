// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: "src",
  pages: true,
  ssr: true,
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss", "@nuxt/icon"],
  css: ['bulma/css/bulma.css'],
  runtimeConfig: {
    public: {
        appName: "FAIR-Checker",
        apiUrl: typeof process.env.NUXT_PUBLIC_API_HOST === "undefined" ? "http://localhost:5000/graph-api" : process.env.NUXT_PUBLIC_HTTP + process.env.NUXT_PUBLIC_API_HOST + ":" + process.env.NUXT_PUBLIC_API_PORT + '/' + process.env.NUXT_PUBLIC_API_BASEPATH
    }
  },
})
