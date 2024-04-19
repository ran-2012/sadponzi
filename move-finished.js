const fs = require('fs')
const path = require('path')
const readline = require('readline/promises')

const INPUT_DIR = './contracts'
const OUTPUT_DIR = "./results";
const TARGET_DIR = "./_contracts";

const files = fs.readdirSync(OUTPUT_DIR)

const HANDOVER = "handover";
const CHAIN = "chain";
const TREE = "tree";

const map = {}

console.log("Move checked contracts to ./_contract directory")
async function main() {
    for (const file of files) {
        try {
            fs.renameSync(`${INPUT_DIR}${path.sep}${file}`, `${TARGET_DIR}${path.sep}${file}`,)
        } catch (e) {
            // ignored
        }
    }
}

main().then();