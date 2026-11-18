const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: "http://127.0.0.1:5001",
    supportFile: false,
    viewportWidth: 1280,
    viewportHeight: 800,
    video: true,
    setupNodeEvents(on, config) {},
  },
});