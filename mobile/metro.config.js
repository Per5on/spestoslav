const path = require("node:path");
const { getDefaultConfig } = require("expo/metro-config");

const config = getDefaultConfig(__dirname);
config.watchFolders = [...(config.watchFolders ?? []), path.resolve(__dirname, "../data/demo-thumbnails"),
  path.resolve(__dirname, "../data/symbolic-thumbnails"),];
module.exports = config;
