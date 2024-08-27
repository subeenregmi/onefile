const path = require('path');

module.exports = {
    mode: "development",
    entry: "./scripts/admin.js",
    output: {
    path: path.resolve(__dirname, 'dist'),
        filename: "admin.js",
    },
    watch: true,
};


