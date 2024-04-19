
## Javascript Usage

- First install Node
- Put all contracts in `./contracts` (files in sub folder will not be analyzed)
- `node install`, `node index.js`, `node results.js`
- Or run script `./run.sh`

> You can specify `Python` executable by setting env `PYTHON`.\
> Or run `Activate` script before running js scripts if you are using venv.

> Currently, I only set 4 concurrent processes
> to analyze contracts due to the sheer memory required.\
> You can manually change in `./index.js` Line 31

### Scripts

- index.js, run multiple instance of python to check if is pozitract
- results.js, analyse result in `./results`.
- move-finished.js, move finished contract to `./_contract`
