/* eslint-disable */
const plugin = require("tailwindcss/plugin");
const path = require("path");

module.exports = {
  content: [
    path.resolve(__dirname, "templates/**/*.j2"),
    path.resolve(__dirname, "static/js/**/*.js"),
  ],
  darkMode: "class",
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/forms")],
  safelist: [
    "button-primary",
    "button-success",
    "button-info",
    "button-danger",
    "button-warning",
    "bg-primary",
    "bg-success",
    "bg-info",
    "bg-danger",
    "bg-warning",
    "border-primary",
    "border-success",
    "border-info",
    "border-danger",
    "border-warning",
    "text-primary",
    "text-success",
    "text-info",
    "text-danger",
    "text-warning",
  ],
};
