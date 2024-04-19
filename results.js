const fs = require('fs')
const path = require('path')
const readline = require('readline/promises')

const OUTPUT_DIR = "./results";

const files = fs.readdirSync(OUTPUT_DIR)

const HANDOVER = "handover";
const CHAIN = "chain";
const TREE = "tree";

const map = {}

async function main() {
    map.total = files.length;
    map.non_ponzi = 0;
    for (const file of files) {
        const is = fs.createReadStream(`${OUTPUT_DIR}${path.sep}${file}`)
        const rl = readline.createInterface({input: is, crlfDelay: Infinity})
        const line = rl.line
        for await (const line of rl) {
            if (line.startsWith("Passed")) {
                ++map.non_ponzi;
                break;
            } else {
                const name = line.split(' ')[1]
                if (!map[name]) {
                    map[name] = 1;
                } else {
                    ++map[name];
                }
            }
        }
        rl.close();
    }
    console.log(JSON.stringify(map, null, 4))
}

main().then();