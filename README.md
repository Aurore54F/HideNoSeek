# HideNoSeek: Camouflaging Malicious JavaScript in Benign ASTs

This repository contains the code of our PDG generation module for the [CCS'19 paper: "HideNoSeek: Camouflaging Malicious JavaScript in Benign ASTs"](https://swag.cispa.saarland/papers/fass2019hidenoseek.pdf).  
Please note that in its current state, the code is a Poc and not a fully-fledged production-ready API.


## Summary
We statically enhance the Abstract Syntax Trees (ASTs) of valid JavaScript inputs with control and data flow information. We refer to the resulting data structure as Program Dependency Graph (PDG).


## Setup

```
install python3 version 3.6.7
install python3-pip # (tested with 9.0.1)
pip3 install -r requirements.txt # (tested versions indicated in requirements.txt)

install nodejs # (tested with 8.10.0)
install npm # (tested with 3.5.2)
cd src
npm install escodegen # (tested with 1.9.1)
cd ..
```


## Usage: PDGs Generation

We can generate PDGs either from a folder containing JavaScript files or directly from a given JavaScript file.  
In both cases, we are currently using 2 CPUs for the PDGs generation process. You can use more (or less) CPUs by modifying the variable NUM\_WORKERS from ```src/utility\_df.py```.


### PDGs From a JS Folder

To generate the PDGs of the JS files from the folder FOLDER\_NAME, launch the following shell command from the ```src``` folder location:
```
$ python3 -c "from pdgs_generation import *; store_pdg_folder('FOLDER_NAME')"
```

The corresponding PDGs will be stored in FOLDER\_NAME/PDG.


### PDGs From a JS File

To generate the PDG of one given JS file INPUT\_FILE, launch the following python3 commands from the ```src``` folder location:
```
>>> from pdgs_generation import *
>>> pdg = get_data_flow('INPUT_FILE', benchmarks=dict())
```

Per default, the corresponding PDG will not be stored. To store it in an existing PDG\_PATH folder, call:

```
>>> from pdgs_generation import *
>>> pdg = get_data_flow('INPUT_FILE', benchmarks=dict(), store_pdgs='PDG_PATH')
```


## Cite this work
If you use HideNoSeek for academic research, you are highly encouraged to cite the following [paper](https://swag.cispa.saarland/papers/fass2019hidenoseek.pdf):
```
@inproceedings{fass2019hidenoseek,
    author="Fass, Aurore and Backes, Michael and Stock, Ben",
    title="{\textsc{HideNoSeek}: Camouflaging Malicious JavaScript in Benign ASTs}",
    booktitle="ACM CCS",
    year="2019"
}
```


### Abstract:

In the malware field, learning-based systems have become popular to detect new malicious variants. Nevertheless, attackers with _specific_ and _internal_ knowledge of a target system may be able to produce input samples which are misclassified. In practice, the assumption of _strong attackers_ is not realistic as it implies access to insider information. We instead propose HideNoSeek, a novel and generic camouflage attack, which evades the entire class of detectors based on syntactic features, without needing any information about the system it is trying to evade. Our attack consists of changing the constructs of malicious JavaScript samples to reproduce a benign syntax.

For this purpose, we automatically rewrite the Abstract Syntax Trees (ASTs) of malicious JavaScript inputs into existing benign ones. In particular, HideNoSeek uses malicious seeds and searches for isomorphic subgraphs between the seeds and traditional benign scripts. Specifically, it replaces benign sub-ASTs by their malicious equivalents (same syntactic structure) and adjusts the benign data dependencies--without changing the AST--, so that the malicious semantics is kept. In practice, we leveraged 23 malicious seeds to generate 91,020 malicious scripts, which perfectly reproduce ASTs of Alexa top 10,000 web pages. Also, we can produce on average 14 different malicious samples with the same AST as each Alexa top 10.

Overall, a standard trained classifier has 99.98% false negatives with HideNoSeek inputs, while a classifier trained on such samples has over 88.74% false positives, rendering the targeted static detectors unreliable.


## License

This project is licensed under the terms of the AGPL3 license, which you can find in ```LICENSE```.
