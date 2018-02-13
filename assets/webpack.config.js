const path = require('path');
const webpack = require('webpack');

if (process.env.WATCH) {
  elmLoader = 'elm-webpack-loader?debug=true';
  plugins = [];
} else {
  elmLoader = 'elm-webpack-loader';
  plugins = [
    new webpack.optimize.UglifyJsPlugin({
      compress: {
        warnings: false,
      },
    }),
  ];
}

module.exports = {
  entry: {
    stcs: ['./stcs.js'],
  },
  output: {
    path: path.resolve(__dirname + '/../static/js'),
    filename: '[name].js',
  },
  module: {
    loaders: [
      {
        test: /\.elm$/,
        exclude: [/elm-stuff/, /node_modules/],
        loader: elmLoader,
      },
    ],
    noParse: /\.elm$/,
  },
  plugins: plugins,
  devServer: {
    inline: true,
    stats: { colors: true },
  },
};