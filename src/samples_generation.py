# Copyright (C) 2020 Aurore Fass
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
    For HideNoSeek: Generation and storage of malicious JavaScript instances with a benign AST.
    For the open-source version: Searching for clones between 2 JavaScript instances
        (the functions' description have not been updated for this specific version).
    Possibility for multiprocessing (NUM_WORKERS defined in utility_df.py).
"""

import pickle
from multiprocessing import Process, Queue

from utility_df import *
from pdgs_generation import get_data_flow
from clone_detection import *


def worker(my_queue, start):
    """ Worker """

    while True:
        try:
            item = my_queue.get(timeout=2)
            # print(item)
            analyze_valid_pdgs(item[0], item[1], item[2])
        except Exception as e:
            break
    print('Total elapsed time: ' + str(timeit.default_timer() - start) + 's')


def replace_ast_df_folder(benign_pdgs, malicious_pdgs):
    """
        Replaces some benign parts of benign file with malicious ones. Loops over JS directories.

        -------
        Parameters:
        - benign_pdgs: str
            Path of the folder containing benign PDGs to test.
        - malicious_pdgs: str
            Path of the folder containing malicious PDGs to test.
    """

    start = timeit.default_timer()

    my_queue = Queue()
    workers = list()

    for malicious_pdg in os.listdir(malicious_pdgs):

        json_analysis = os.path.join(os.path.dirname(malicious_pdgs), malicious_pdg + '-analysis')
        if not os.path.exists(json_analysis):
            os.makedirs(json_analysis)

        for benign_pdg in os.listdir(benign_pdgs):
            my_queue.put([os.path.join(benign_pdgs, benign_pdg),
                          os.path.join(malicious_pdgs, malicious_pdg),
                          json_analysis])
            # time.sleep(0.1)  # Just enough to let the Queue finish

    for i in range(NUM_WORKERS):
        p = Process(target=worker, args=(my_queue, start,))
        p.start()
        print("Starting process")
        workers.append(p)

    for w in workers:
        w.join()


def unpickle_pdg(pdg_path):
    """ Tries to unpickle a PDG. """

    try:
        pdg = pickle.load(open(pdg_path, 'rb'))
        return pdg
    except IsADirectoryError as error_message:
        logging.exception('%s %s%s %s', 'Tried to unpickle the directory', pdg_path, ':',
                          str(error_message))
        return None


def analyze_valid_pdgs(benign_pdg_path, malicious_pdg_path, json_analysis):
    """ Take one benign and one malicious PDG paths and call the replace_ast_df function if both of
    them are valid. """

    results = dict()
    dfg_nodes_benign = unpickle_pdg(benign_pdg_path)
    if dfg_nodes_benign is not None:
        dfg_nodes_malicious = unpickle_pdg(malicious_pdg_path)
        if dfg_nodes_malicious is not None:
            print('Analysis of ' + os.path.basename(malicious_pdg_path) + ' and '
                  + os.path.basename(benign_pdg_path) + '\n')
            results['malicious'] = malicious_pdg_path
            results['benign'] = benign_pdg_path
            replace_ast_df(dfg_nodes_benign, dfg_nodes_malicious, results, json_analysis)


def replace_ast_df(dfg_nodes_benign, dfg_nodes_malicious, res_dict, json_analysis):
    """
        Replaces benign sub ASTs with their malicious equivalents.

        -------
        Parameters:
        - dfg_nodes_benign: Node
            PDG of the benign file considered.
        - dfg_nodes_malicious: Node
            PDG of the malicious file considered.
        - res_dict: dict
            Contains the different results obtained so far.
        - json_analysis: str
            Path of the directory to store the JSON analysis file.

        -------
        Returns:
        - list
            Contains the clones found between the benign and malicious AST.
        - or None.
    """

    start = timeit.default_timer()
    benchmarks = dict()

    malicious = os.path.basename(res_dict['malicious'])
    benign = os.path.basename(res_dict['benign'])

    all_clones_list = find_all_clones(dfg_nodes_benign, dfg_nodes_malicious)
    benchmarks['Clones detected'] = timeit.default_timer() - start
    start = micro_benchmark('Successfully detected ' + str(len(all_clones_list))
                            + ' clones without duplicate suppression in',
                            timeit.default_timer() - start)

    remove_duplicate_clones(all_clones_list, res_dict)  # Modified version
    annotate_clone(all_clones_list, res_dict)
    res_dict['dissimilar'] = list()
    dissimilar(dfg_nodes_malicious, res_dict)
    benchmarks['Clones selected'] = timeit.default_timer() - start
    micro_benchmark('Successfully selected ' + str(len(all_clones_list))
                    + ' clones in', timeit.default_timer() - start)

    nb_clones = get_percentage_cloned(dfg_nodes_benign, dfg_nodes_malicious, res_dict)
    print_clones(all_clones_list)  # Comment for multiprocessing!

    logging.info('Could find %s%% of the malicious nodes in the benign AST', nb_clones * 100)

    if nb_clones * 100 == 100:  # Only if malicious AST can be found in benign one
        res_dict['benchmarks'] = benchmarks

        with open(os.path.join(json_analysis, benign.replace('.js', '') + '_'\
                                              + malicious.replace('.js', '') + '.json'),
                  'w') as json_data:
            json.dump(res_dict, json_data)

        return all_clones_list

    res_dict['benchmarks'] = benchmarks
    with open(os.path.join(json_analysis, benign.replace('.js', '') + '_'\
                                          + malicious.replace('.js', '') + '.json'),
              'w') as json_data:
        json.dump(res_dict, json_data)

    return None


def replace_ast(input_benign, input_malicious):
    """
        Replaces some benign parts of a given file with malicious ones.

        -------
        Parameters:
        - input_benign: str
            Path of the benign file considered.
        - input_malicious: str
            Path of the malicious file considered.

        -------
        Returns:
        - list
            Contains the clones found between the benign and malicious AST.
        - or None.
    """

    benchmarks = dict()
    json_analysis = input_malicious.replace('.js', '') + '-analysis'
    if not os.path.exists(json_analysis):
        os.makedirs(json_analysis)
    start = timeit.default_timer()

    dfg_nodes_benign = get_data_flow(input_file=input_benign, benchmarks=benchmarks)
    dfg_nodes_malicious = get_data_flow(input_file=input_malicious, benchmarks=benchmarks)
    if dfg_nodes_benign is not None and dfg_nodes_malicious is not None:
        res_dict = dict()
        res_dict['malicious'] = input_malicious
        res_dict['benign'] = input_benign
        replaced_ast = replace_ast_df(dfg_nodes_benign, dfg_nodes_malicious, res_dict=res_dict,
                                      json_analysis=json_analysis)
        # same_ast(benign_file, malicious_file)
        micro_benchmark('Elapsed time:', timeit.default_timer() - start)
        return replaced_ast
    return None
