/* eslint-disable */
const path = require("path");

const is_production = process.env.FLASK_ENV === "production";
module.exports = (ctx) => ({
  plugins: [
    require("tailwindcss")(path.resolve(__dirname, "tailwind.config.js")),
    require("autoprefixer"),
    is_production && require("cssnano"),
  ],
});
