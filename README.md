# HideNoSeek: Camouflaging Malicious JavaScript in Benign ASTs

This repository contains most of the code of our [CCS'19 paper: "HideNoSeek: Camouflaging Malicious JavaScript in Benign ASTs"](https://swag.cispa.saarland/papers/fass2019hidenoseek.pdf), namely:
- our PDG generation module;
- our clone detection module;
- a part of our clone selection module.

Please note that in its current state, the code is a Poc and not a fully-fledged production-ready API.


## Summary
HideNoSeek is a novel and generic camouflage attack, which changes the constructs of malicious JavaScript samples to exactly reproduce an existing benign syntax. For this purpose, we statically enhance the Abstract Syntax Trees (ASTs) of valid JavaScript inputs with control and data flow information. We refer to the resulting data structure as Program Dependency Graph (PDG). In particular, HideNoSeek looks for isomorphic subgraphs between the malicious and the benign files. Specifically, it replaces benign sub-ASTs by their malicious equivalents (same syntactic structure) and adjusts the benign data dependencies–without changing the AST–, so that the malicious semantics is kept.

For ethical reasons, we decided to publish neither the complete code of our clone selection module nor our clone replacement module. Therefore, this HideNoSeek version can be used to **detect** syntactic clones, but not to **rewrite** them.


## Setup

```
install python3 # (tested with 3.6.7)
install nodejs # (tested with 8.10.0)
install npm # (tested with 3.5.2)
cd src
npm install escodegen # (tested with 1.9.1)
cd ..
```


## Usage: 

HideNoSeek works directly at the PDG level. To detect clones between 2 JavaScript folders, you should generate the PDGs beforehand (cf. PDGs Generation) and give them as input to the `src/samples_generation.replace_ast_df_folder` function.

To detect clones between 2 JavaScript samples, you should give the files' paths directly as input to the `src/samples_generation.replace_ast` function.

### PDGs Generation

To generate the PDGs of the JS files from the folder FOLDER\_NAME, launch the following shell command from the `src` folder location:
```
$ python3 -c "from pdgs_generation import store_pdg_folder; store_pdg_folder('FOLDER_NAME')"
```

The corresponding PDGs will be stored in FOLDER\_NAME/PDG.


To generate the PDG of one given JS file INPUT\_FILE, launch the following python3 commands from the `src` folder location:
```
>>> from pdgs_generation import get_data_flow
>>> pdg = get_data_flow('INPUT_FILE', benchmarks=dict())
```

Per default, the corresponding PDG will not be stored. To store it in an existing PDG\_PATH folder, call:
```
>>> from pdgs_generation import get_data_flow
>>> pdg = get_data_flow('INPUT_FILE', benchmarks=dict(), store_pdgs='PDG_PATH')
```

Note that, for this HideNoSeek version, we added a timeout of 60 seconds for the PDG generation process (cf. line 83 of `src/pdgs_generation.py`).



### Clone Detection

To find clones between the benign PDGs from the folder FOLDER\_BENIGN\_PDGS and the malicious ones from FOLDER\_MALICIOUS\_PDGS, launch the following python3 command from the `src` folder location:
```
$ python3 -c "from samples_generation import replace_ast_df_folder; replace_ast_df_folder('FOLDER_BENIGN_PDGS', 'FOLDER_MALICIOUS_PDGS')"
```

For each malicious PDG, a folder PDG_NAME-analysis will be created in FOLDER\_MALICIOUS\_PDGS. For each benign PDG analyzed, it will contain a JSON file (name format: benign_malicious.json), which summarizes the main findings, such as identical nodes, the proportion of identical nodes, dissimilar tokens, different benchmarks...  
In addition, we display in stdout the benign and malicious code of the reported clones. This can be disabled, e.g., for multiprocessing, by commenting the call to `print_clones` line 153 of `src/samples_generation.py`.


To find clones between a benign JS file BENIGN_JS and a malicious one MALICIOUS_JS, launch the following python3 commands from the `src` folder location:
```
>>> from samples_generation import replace_ast
>>> replace_ast('BENIGN_JS', 'MALICIOUS_JS')
```

The outputs, in terms of JSON file and on stdout, are as previously.


### Multiprocessing

The `src/pdgs_generation.store_pdg_folder` and `src/samples_generation.replace_ast_df_folder` functions are fully parallelized.
In both cases, we are currently using 1 CPU, but you can change that by modifying the variable NUM\_WORKERS from `src/utility_df.py`. If you use more than 1 CPU, you should comment out the call to `print_clones` line 153 of `src/samples_generation.py`.


## Example

The folder `example/Benign-example` contains `example.js` the benign example from our paper, while `example/Malicious-seed/seed.js` is the malicious seed from our paper.

To detect clones between these 2 files, launch the following python3 commands from the `src` folder location:
```
>>> from samples_generation import replace_ast
>>> replace_ast('../example/Benign-example/example.js', '../example/Malicious-seed/seed.js')
```

You will get the following output on stdout:
```
INFO:Successfully selected 2 clones in XXXs
==============
[<node.Node object at XXX>, <node.Node object at XXX>]
obj.setAttribute('type', 'application/x-shockwave-flash');
obj = document.createElement('object');
[<node.Node object at XXX>, <node.Node object at XXX>]
wscript.run('cmd.exe /c "<malicious powershell>;"', '0');
wscript = WScript.CreateObject('WScript.Shell');
--
[<node.Node object at XXX>, <node.Node object at XXX>]
obj.setAttribute('tabindex', '-1');
obj = document.createElement('object');
[<node.Node object at XXX>, <node.Node object at XXX>]
wscript.run('cmd.exe /c "<malicious powershell>;"', '0');
wscript = WScript.CreateObject('WScript.Shell');
--
==============
INFO:Could find 100.0% of the malicious nodes in the benign AST
```

Our tool found 2 clones (each time composed of 2 statements). It means that the whole malicious seed could be rewritten in 2 different ways in the benign example.  
In addition, the file `example/Malicious-seed/seed-analysis/example_seed.json`, containing additional clone information, was created.


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

This project is licensed under the terms of the AGPL3 license, which you can find in `LICENSE`.
