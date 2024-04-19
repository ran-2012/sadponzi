const fs = require('fs')
const os = require('os')
const path = require('path')
const process = require('node:process')
const child_process = require("child_process");
const stream = require('stream')

const INPUT_DIR = "./contracts";
const OUTPUT_DIR = "./results";

const LOG_DIR = "./logs";

const PYTHON = process.env.PYTHON ? process.env.PYTHON :
    child_process.execSync('powershell "echo \'import sys; print(sys.executable)\'|python"').toString().trim()

console.log(`Using python in ${PYTHON}`)

if (!fs.existsSync(INPUT_DIR)) {
    throw new Error(`Input dir ${INPUT_DIR} does not exists`)
}

// Clear output dir
fs.rmSync(OUTPUT_DIR, {recursive: true})
fs.mkdirSync(OUTPUT_DIR)

if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR);
}

// CHANGE PROCESS COUNT HERE ↓
const PROCESS_NUM = 4
    //os.cpus().length;

console.log(`Spawning ${PROCESS_NUM} processes`)

const files = []
const filesPerProcess = [];
{
    const _files = fs.readdirSync(INPUT_DIR);
    _files.forEach((file) => {
        const fileFull = `${INPUT_DIR}${path.sep}${file}`
        if (fs.lstatSync(fileFull).isFile()) {
            files.push(file);
        }
    })
    console.log(`Total contract count: ${files.length}`)

    for (let i = 0; i < PROCESS_NUM; ++i) {
        filesPerProcess.push([])
    }
    files.forEach((file, index) => {
        filesPerProcess[index % PROCESS_NUM].push(file)
    })
}

async function spawnProcess(id, inputFiles, logFile) {
    console.log(`Spawning process ${id}`)
    if (inputFiles.length === 0) {
        console.log(`No file for process ${id}`)
        return;
    }
    const total = inputFiles.length;
    const logStream = fs.createWriteStream(logFile)
    for (let index = 0; index < total; ++index) {
        const file = inputFiles[index];
        try {
            await new Promise((resolve, reject) => {
                console.log(`process ${id}, ${index}/${total}`)
                const cp = child_process.spawn(PYTHON,
                    ['sadponzi.py', '-i', `${INPUT_DIR}${path.sep}${file}`,
                        '-o', `${OUTPUT_DIR}${path.sep}${file}`])

                cp.on('error', (err) => {
                    reject(err);
                })
                const pipe = stream.pipeline(cp.stdout, logStream, (err) => {
                });
                stream.pipeline(cp.stderr, pipe, (err) => {
                });

                cp.addListener('exit', () => {
                    resolve();
                    console.log(`process ${id}, ${index}/${total} exited`)
                })
            })
        } catch (e) {
            console.error(e);
            console.error(`process ${id}, ${index}/${total} failed`)
        }
    }

    await new Promise((resolve) => {
        logStream.close(() => {
            resolve();
        })
    })
}

const promises = [];

filesPerProcess.forEach((files, index) => {
    promises.push(spawnProcess(index, files, `${LOG_DIR}${path.sep}${index}.log`))
})


async function main() {
    await Promise.all(promises)
}

main()
    .then(() => {
        console.log("All finished")
    })
    .catch((err) => {
        console.error(err);
    })

