/* eslint-disable */
const path = require("path");
import {terser} from "rollup-plugin-terser";
import alias from "@rollup/plugin-alias";
import commonjs from "@rollup/plugin-commonjs";
import {nodeResolve} from "@rollup/plugin-node-resolve";

const is_production = process.env.FLASK_ENV === "production";
export default {
  output: {
    sourcemap: (!is_production && "inline") || false,
    format: "iife",
    name: "app",
  },
  plugins: [
    alias({
      entries: [
        {
          find: "@gmg",
          replacement: path.resolve(__dirname, "static/js"),
        },
      ],
    }),
    nodeResolve(),
    commonjs(),

    is_production && terser(),
  ],
  watch: {
    clearScreen: false,
  },
};
