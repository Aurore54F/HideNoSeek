// Copyright (C) 2019 Aurore Fass
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

// Conversion of an Esprima AST to JS using Escodegen.


module.exports = {
    ast2js: ast2js
};


var es = require("escodegen");
var fs = require("fs");


/**
 * Extraction of the JS code from a given AST using Escodegen.
 *
 * @param json_path
 * @param code_path
 */
function ast2js(json_path, code_path) {
    var ast = fs.readFileSync(json_path).toString('utf-8');
    ast = JSON.parse(ast);
    if (code_path !== '1') {
        fs.writeFile(code_path, es.generate(ast, {comment: true, json: true}), function (err) {
            if (err) {
                console.error(err);
            }
        });
    }
    else {
        console.log(es.generate(ast, {comment: true, json: true}));
    }
}

ast2js(process.argv[2], process.argv[3]);
