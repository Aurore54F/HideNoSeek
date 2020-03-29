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
3. Define metric to deduplicate clones.
For ethical reasons, we choose not to publish our complete code to select clones. Specifically, we:
    - still choose the largest clone and not a subsumed version of it;
    - still maximize the proportion of identical tokens between the benign and the crafted samples,
        but if they do not match, we do not suggest how to modify them for them to match;
    - do not minimize the distance between the nodes inside a clone (minimize_delta_between_clones).

Also, and of course, we did not publish 4. Clone replacement.
"""

from handle_json import *


def search_literal(node, tab):
    """
        Searches the Literal nodes descendants of node.
        -------
        Parameters:
        - nodes: Node
            Current node to test.
        - tab: list
            Will contain the Literal nodes found.

        -------
        Returns:
        - list
            Stores the Literal nodes found.
    """

    if isinstance(node, list):
        for elt in node:
            search_literal(elt, tab)
    else:
        if node.name == 'Literal':
            tab.append(node)
        else:
            for child in node.children:
                search_literal(child, tab)
    return tab


def print_clones(all_clones_list):
    """ Print the JS code of the clones detected. """

    my_json = 'my-json.json'
    print('==============')
    for el in all_clones_list:
        print(el.list1)
        for elt in el.list1:
            save_json(elt, my_json)
            get_code(my_json, test=True)

        print(el.list2)
        for elt in el.list2:
            save_json(elt, my_json)
            get_code(my_json, test=True)
        print('--')
    print('==============')


def change_literal(all_clones_list, res_dict):
    """ Reports Tokens that do not match, while the ASTs matched. """

    for clone_list in all_clones_list:
        literal_list_mal = search_literal(clone_list.list2, tab=[])
        literal_list_ben = search_literal(clone_list.list1, tab=[])

        for i, _ in enumerate(literal_list_ben):
            literal_mal = literal_list_mal[i].literal_type()
            literal_ben = literal_list_ben[i].literal_type()

            if literal_mal != literal_ben:
                logging.info('The tokens of %s and %s do not match',
                             literal_list_mal[i].attributes['raw'],
                             literal_list_ben[i].attributes['raw'])
                res_dict['pb_tokens'].append([literal_mal, literal_ben])

                # Possible modifications suggested


def same_tokens(all_clones_list, clone_list_a, clone_list_b, i, j):
    """
        Some clones can be found several times in a given file. As a metric, we would like two
        clones to share the same Tokens (since they already share an AST, the extra check is
        done on the Literals).

        -------
        Parameters:
        - all_clones_list: list of BiList()
            Contains the clones that have been found.
        - clone_list_a: list
            Corresponds to all the clones found in file A (when analyzed against file B).
        - clone_list_b: list
            Corresponds to all the clones found in file B (when analyzed against file A).
        - i, j: int
            Correspond to indexes such as clone_list_a[i] = clone_list_a[j].

        -------
        Returns:
        - list
            * Elt1: int, index to be tested next;
            * Elt2: int, index to be tested next.
    """

    logging.debug('A clone was found twice')

    tokens_a = [literal.literal_type() for literal in search_literal(clone_list_a[i], tab=[])]
    tokens_bi = [literal.literal_type() for literal in search_literal(clone_list_b[i], tab=[])]
    tokens_bj = [literal.literal_type() for literal in search_literal(clone_list_b[j], tab=[])]

    if tokens_a == tokens_bi and tokens_a == tokens_bj:
        logging.debug('The same tokens could be found twice')
        # No clones selection for the open source version
        # [i, j] = minimize_delta_between_clones(all_clones_list, clone_list_b, i, j)
    elif tokens_a == tokens_bi:
        logging.debug('The same tokens could be found')
        all_clones_list.remove(all_clones_list[j])  # To have the real index
        j -= 1  # Otherwise we miss an index, since j-old + 1 is now at position j-new
    elif tokens_a == tokens_bj:
        logging.debug('The same tokens could be found')
        all_clones_list.remove(all_clones_list[i])  # To have the real index
        i -= 1  # Otherwise we miss an index, since i-old + 1 is now at position i-new,
        # so i should not get i + 1
        j = i + 1  # Otherwise we miss indexes, as we get a new i value, j should be reset too
    else:
        logging.debug('The same tokens could not be found on this iteration')
        # No clones selection for the open source version
        # [i, j] = minimize_delta_between_clones(all_clones_list, clone_list_b, i, j)

    return [i, j]


def remove_subsumed_clones(all_clones_list, clone_list1, clone_list2, i, j):
    """
        Some clones can be found several times in a given file. As a metric, we consider the
        biggest one and delete subsumed clones.

        -------
        Parameters:
        - all_clones_list: list of BiList()
            Contains the clones that have been found.
        - clone_list1: list
            Corresponds to all the clones found in the file 1 (when analyzed against file 2).
        - clone_list2: list
            Corresponds to all the clones found in the file 2 (when analyzed against file 1).
        - i, j: int
            Correspond to indexes in the clone_listx.

        -------
        Returns:
        - list
            * Elt1: int, index to be tested next;
            * Elt2: int, index to be tested next.
    """

    if len(clone_list2[i]) > len(clone_list2[j])\
            and all(elt in clone_list2[i] for elt in clone_list2[j]):
        all_clones_list.remove(all_clones_list[j])
        j -= 1  # Otherwise we miss an index, since j-old + 1 is now at position j-new

    elif len(clone_list2[i]) < len(clone_list2[j])\
            and all(elt in clone_list2[j] for elt in clone_list2[i]):
        all_clones_list.remove(all_clones_list[i])
        i -= 1  # Otherwise we miss an index, since i-old + 1 is now at position i-new,
        # so i should not get i + 1
        j = i + 1  # Otherwise we miss indexes, as we get a new i value, j should be reset too

    elif len(clone_list1[i]) > len(clone_list1[j])\
            and all(elt in clone_list1[i] for elt in clone_list1[j]):
        all_clones_list.remove(all_clones_list[j])
        j -= 1  # Otherwise we miss an index, since j-old + 1 is now at position j-new

    elif len(clone_list1[i]) < len(clone_list1[j])\
            and all(elt in clone_list1[j] for elt in clone_list1[i]):
        all_clones_list.remove(all_clones_list[i])
        i -= 1  # Otherwise we miss an index, since i-old + 1 is now at position i-new,
        # so i should not get i + 1
        j = i + 1  # Otherwise we miss indexes, as we get a new i value, j should be reset too

    return [i, j]


def remove_duplicate_clones(all_clones_list, res_dict):
    """
        Because of backward slicing, some clones are reported twice, store them only once.
        Sometimes several clones are found. As a metric, we consider the distance between the nodes
        forming a clone, which should be minimized.

        -------
        Parameters:
        - all_clones_list: list of BiList()
            Contains the clones that have been found.
        - res_dict: dict
            Contains the different results obtained so far.
    """

    i = 0
    while i < len(all_clones_list):  # To iterate over the modified list
        store_i = i
        j = i + 1
        while j < len(all_clones_list):  # To iterate over the modified list
            if i < store_i:
                i = store_i  # i should not be reset under its value
            clone_list1 = [clone_list.list1 for clone_list in all_clones_list]
            clone_list2 = [clone_list.list2 for clone_list in all_clones_list]

            if clone_list1[i] == clone_list1[j] and clone_list2[i] == clone_list2[j]:
                logging.debug('The exact same clone was reported twice %s and %s. Kept only one ',
                              str(clone_list1[i]), str(clone_list2[i]))
                all_clones_list.remove(all_clones_list[j])
                j -= 1  # Otherwise we miss an index, since j-old + 1 is now at position j-new

            elif clone_list1[i] == clone_list1[j]:
                [i, j] = same_tokens(all_clones_list, clone_list1, clone_list2, i, j)
            elif clone_list2[i] == clone_list2[j]:
                [i, j] = same_tokens(all_clones_list, clone_list2, clone_list1, i, j)

            else:
                [i, j] = remove_subsumed_clones(all_clones_list, clone_list1, clone_list2, i, j)

            j += 1
        i += 1
    res_dict['pb_tokens'] = list()
    change_literal(all_clones_list, res_dict)
