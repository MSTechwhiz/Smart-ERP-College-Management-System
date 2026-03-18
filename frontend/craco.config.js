// craco.config.js
const path = require("path");
require("dotenv").config();

// Check if we're in development/preview mode (not production build)
const isDevServer = process.env.NODE_ENV !== "production";

const config = {
  enableHealthCheck: process.env.ENABLE_HEALTH_CHECK === "true",
  enableVisualEdits: false, // Explicitly disabled to fix white screen issue
};

const webpackConfig = {
  eslint: {
    configure: {
      extends: ["plugin:react-hooks/recommended"],
      rules: {
        "react-hooks/rules-of-hooks": "error",
        "react-hooks/exhaustive-deps": "warn",
      },
    },
  },
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig) => {
      // CRA dev-only Babel plugins can inject `_jsxFileName` before imports,
      // which breaks module parsing in some environments. Remove them safely.
      const stripProblemBabelPlugins = (cfg) => {
        const stripFromLoaderOptions = (loaderOptions) => {
          if (!loaderOptions || !Array.isArray(loaderOptions.plugins)) return;
          loaderOptions.plugins = loaderOptions.plugins.filter((p) => {
            const name = Array.isArray(p) ? p[0] : p;
            if (typeof name !== "string") return true;
            return (
              !name.includes("plugin-transform-react-jsx-source") &&
              !name.includes("plugin-transform-react-jsx-self")
            );
          });
        };

        const visitRules = (rules) => {
          if (!Array.isArray(rules)) return;
          for (const rule of rules) {
            if (!rule) continue;
            if (Array.isArray(rule.oneOf)) visitRules(rule.oneOf);
            if (Array.isArray(rule.rules)) visitRules(rule.rules);

            if (rule.use) {
              const uses = Array.isArray(rule.use) ? rule.use : [rule.use];
              for (const use of uses) {
                if (!use) continue;
                if (typeof use === "object" && use.loader && use.loader.includes("babel-loader")) {
                  stripFromLoaderOptions(use.options);
                }
              }
            }

            if (rule.loader && typeof rule.loader === "string" && rule.loader.includes("babel-loader")) {
              stripFromLoaderOptions(rule.options);
            }
          }
        };

        visitRules(cfg.module?.rules);
      };

      webpackConfig.watchOptions = {
        ...webpackConfig.watchOptions,
        ignored: [
          '**/node_modules/**',
          '**/.git/**',
          '**/build/**',
          '**/dist/**',
          '**/coverage/**',
          '**/public/**',
        ],
      };

      stripProblemBabelPlugins(webpackConfig);
      return webpackConfig;
    },
  },
  babel: {
    plugins: [],
  },
};

module.exports = webpackConfig;
