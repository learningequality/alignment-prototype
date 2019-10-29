const path = require('path');
const VueAutoRoutingPlugin = require("vue-auto-routing/lib/webpack-plugin");
const webpack = require("webpack");
const BundleTracker = require('webpack-bundle-tracker');

module.exports = {
  outputDir: path.resolve(__dirname, 'alignmentpro/alignmentapp/static/bundles'),
  publicPath: '/static/bundles/',
  configureWebpack: () => {
    const config = {
      output: {},
      entry: './alignmentpro/frontend/main.js',
      resolve: {
        modules: [
            path.resolve(__dirname, 'node_modules'),
            path.resolve(__dirname, './alignmentpro/frontend'),
        ]
      },
      plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new VueAutoRoutingPlugin({
          // Path to the directory that contains your page components.
          pages: "apps",

          // A string that will be added to importing component path (default @/pages/).
          importPrefix: "@/apps/"
        })
      ]
    };
    return config;
  }
};
