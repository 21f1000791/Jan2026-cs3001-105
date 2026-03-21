module.exports = {
  chainWebpack: (config) => {
    // Vue CLI already renders public/index.html via HtmlWebpackPlugin.
    // Exclude it from CopyWebpackPlugin to avoid duplicate index.html emits.
    config.plugin("copy").tap((args) => {
      args[0].patterns = (args[0].patterns || []).map((pattern) => {
        const currentIgnore = pattern.globOptions?.ignore || [];
        return {
          ...pattern,
          globOptions: {
            ...(pattern.globOptions || {}),
            ignore: [...currentIgnore, "**/index.html", "index.html"],
          },
        };
      });
      return args;
    });
  },
};
