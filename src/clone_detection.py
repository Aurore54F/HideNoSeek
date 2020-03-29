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
2. Find all clones.
"""

from equivalence_classes import *
from clone_metric import *


LEAF_STATEMENTS = ['BreakStatement', 'ContinueStatement']


def data_or_control(node, label):
    """ Return the node statement, data or control dependencies. Parents or children."""

    if label == 'statement':
        return node.statement_dep_children
    if label == 'control_c':
        return node.control_dep_children
    if label == 'control':
        return node.control_dep_parents
    if label == 'data':
        return node.data_dep_parents
    logging.error('Expected \'data\' or \'control\', got %s instead', label)
    return None


def traverse(node, tab):
    """ Traverses a node and stores its descendants.
    Can be responsible for a stack overflow. Did not find a solution yet and
    traverse_statement_node is too incomplete. """

    for child in node.children:
        if not child.is_comment():
            tab.append(child)
        traverse(child, tab)
    return tab


def handle_statement_node(node, non_statement_list, label):
    """
        Traverses a Statement node by following the statement / control dependencies.
        Idea: to detect clones we are working at the statement level. Therefore we add to the list
        all the nodes that belong to the considered node (statement dependencies). For example, an
        IfStatement node HAS to be stored together with its condition. The ensemble represents the
        IfStatement. The body on the other hand is linked by a CF dependency and will be handled
        somewhere else.

        -------
        Parameters:
        - node: Node
            Node to be traversed.
        - non_statement_list: list
            Contains the nodes traversed so far.
        - label: 'data' or 'control'
            Indicates if we are handling data or control dependencies.
    """

    for child_cf_dep in data_or_control(node, label):
        child_cf = child_cf_dep.extremity
        non_statement_list.append(child_cf)
        traverse_statement_node(child_cf, non_statement_list, init=0)


def traverse_statement_node(node, non_statement_list, init=1):
    """
        Traverses a Statement node by following the statement dependencies. Also considers CF
        dependencies if there is a direct parent with a statement dependency.

        -------
        Parameters:
        - node: Node
            Node to be traversed.
        - non_statement_list: list
            Contains the nodes traversed so far.
        - init: 1 or 0
            Indicates if this is the first time (1) that the algorithm is run. Default: 1.

        -------
        Returns:
        - list
            Contains the type (Node.name) of the nodes traversed in node.
    """

    handle_statement_node(node, non_statement_list, label='statement')
    if init == 0:
        # Only if the nodes here are linked with a statement flow to their parent
        handle_statement_node(node, non_statement_list, label='control_c')
    return non_statement_list


def search_handled_nodes(node1, node2, all_clones_list):
    """
        Searches the nodes that have already been handled, so as not to do backward slicing again.

        -------
        Parameters:
        - node1: Node
            Statement node 1.
        - node2: Node
            Statement node 2.
        - all_clones_list: list of BiList()
            Contains the clones that have already been found so far.
    """

    current_clone_list = all_clones_list[-1]  # current clone list stored last

    for i, _ in enumerate(current_clone_list.list1):
        if current_clone_list.list1[i].parent.id == node1.id\
                and current_clone_list.list2[i].parent.id == node2.id:
            # Case where a node n is a clone and its parent n-1 too. We just store n-1 to avoid
            # duplicate (as n is in n-1)
            logging.debug(current_clone_list.list1[i].name + ' is a descendant of ' + node1.name)
            del current_clone_list.list1[i]
            del current_clone_list.list2[i]
    current_clone_list.append_list(node1, node2)  # Otherwise: new pair of clones
    follow_dependencies(node1, node2, all_clones_list)


def find_clones(node1, node2, all_clones_list, tab_handled, jump=0, jump_match=0):
    """
        Compare two statement nodes. We consider that they are equal (return True) iff:
            - they have the same type (referred to as Node.name);
            - they have the same statement dependencies till the leaf;
            - they have the same control dependencies till the leaf; beware we consider only control
            dependencies that originated from a statement dependency. Otherwise CF are handled
            somewhere else;
            - they have the same number of dependencies.

        -------
        Parameters:
        - node1: Node
            Statement node 1.
        - node2: Node
            Statement node 2.
        - all_clones_list: list of BiList()
            Contains the clones that have already been found so far.
        - tab_handled: list
            Contains the node id which have already been handled/jumped over. Use case: when no
            match can be found, we do backward slicing on the benign node to try to find a match.
        - jump: int
            Jumps over a sibling DD. Default: 0.
        - jump_match: int
            Jumps over a sibling DD and matches. Default: 0.
    """

    if node1.name == node2.name:
        belongs_node1 = traverse(node1, tab=[])
        belongs_node2 = traverse(node2, tab=[])

        if [elt1.name for elt1 in belongs_node1] == [elt2.name for elt2 in belongs_node2]:
            logging.debug('Clone found at the ' + node1.name + ' level, between node id '
                          + str(node1.id) + ' and ' + str(node2.id))

            if jump_match > 0:
                # 3 - The clones are independent and should not be stored together
                current_clone_list = all_clones_list[-1]  # current clone list stored last
                current_clone_list_copy = current_clone_list.copy_list()
                del current_clone_list_copy.list1[-1]
                del current_clone_list_copy.list2[-1]
                # 4 - Still, we keep the clones history
                all_clones_list.append(current_clone_list_copy)
            tab_handled.append(str(node1.id) + '_' + str(node2.id))
            search_handled_nodes(node1, node2, all_clones_list)

            if jump != 0:
                # 2 - and we have a match
                jump_match += 1
            return [jump, jump_match]

    for parent_f1_dep in data_or_control(node1, 'data'):  # Jump over benign DD if not match found
        jump += 1  # 1 - If the loop is iterated several times
        parent_f1 = parent_f1_dep.extremity
        if str(parent_f1.id) + '_' + str(node2.id) not in tab_handled:
            logging.debug('Jump over a data dependency of the benign file, to test the benign node '
                          + str(parent_f1.id) + ' with the malicious ' + str(node2.id))
            tab_handled.append(str(parent_f1.id) + '_' + str(node2.id))
            [jump, jump_match] = find_clones(parent_f1, node2, all_clones_list, tab_handled, jump,
                                             jump_match)
    return [jump, jump_match]


def follow_dependency(node1, node2, label, all_clones_list):
    """
        Given two statement nodes, does backward slicing to find clones.

        -------
        Parameters:
        - node1: Node
            Statement node 1.
        - node2: Node
            Statement node 2.
        - label: 'data' or 'control'
            Indicates if we are handling data or control dependencies.
        - all_clones_list: list of BiList()
            Contains the clones that have already been found so far.
    """

    for parent_f1_dep in data_or_control(node1, label):
        parent_f1 = parent_f1_dep.extremity
        if node1.id != parent_f1_dep.extremity.id:  # To avoid infinite loops if DD on oneself
            for parent_f2_dep in data_or_control(node2, label):
                parent_f2 = parent_f2_dep.extremity
                if node2.id != parent_f2_dep.extremity.id:  # To avoid infinite loops
                    find_clones(parent_f1, parent_f2, all_clones_list, tab_handled=[])


def follow_dependencies(node1, node2, all_clones_list):
    """
        Given two statement nodes, does backward slicing to find clones.

        -------
        Parameters:
        - node1: Node
            Statement node 1.
        - node2: Node
            Statement node 2.
        - all_clones_list: list of BiList()
            Contains the clones that have already been found so far.
    """

    follow_dependency(node1, node2, 'control', all_clones_list)
    follow_dependency(node1, node2, 'data', all_clones_list)

    """
    if node1.name != 'Program' and node2.name != 'Program':
        if node1.parent.name == 'Program' or node2.parent.name == 'Program':
            find_clones(node1.parent, node2.parent, all_clones_list)
    """


def annotate_clone(all_clones_list, res_dict):
    """
        Sets the nodes' clone attribute to true, when the nodes are in a clone.

        -------
        Parameter:
        - all_clones_list: list of BiList()
            Contains the clones that have been found.
        - res_dict: dict
            Contains the different results obtained so far.
    """

    res_dict['similar'] = list()
    for clone in all_clones_list:
        for node in clone.list1:
            node.set_clone_true()
            for child in traverse(node, tab=[]):
                child.set_clone_true()
        for node in clone.list2:
            node.set_clone_true()
            list_per_statement = list()
            if not node.is_comment():
                list_per_statement.append(node.name)
            for child in traverse(node, tab=[]):
                child.set_clone_true()
                if not child.is_comment():
                    list_per_statement.append(child.name)
            res_dict['similar'].append(list_per_statement)


def find_all_clones(dfg_nodes1, dfg_nodes2):
    """
        Given an EquivalenceClass object, tests all the nodes with one another to detect clones.

        -------
        Parameters:
        - dfg_nodes1: Node
            PDG of the benign file.
        - dfg_nodes2: Node
            PDG of the malicious file.

        -------
        Returns:
        - list of BiList()
            Contains the groups of clones, after duplicate deletion, found at the end.
    """

    equivalence_classes = get_equivalence_classes(dfg_nodes1, dfg_nodes2, equivalence_classes={})
    all_clones_list, tab_handled = [], []
    for equivalence_class in equivalence_classes.values():
        for node2 in equivalence_class.list2:
            for node1 in equivalence_class.list1:
                all_clones_list.append(BiList())
                find_clones(node1, node2, all_clones_list, tab_handled=tab_handled)
                if all_clones_list[-1].is_empty():
                    all_clones_list.remove(all_clones_list[-1])
    # print_clones(all_clones_list)
    return all_clones_list


def dissimilar(malicious_node, res_dict):
    if not malicious_node.clone:
        if not malicious_node.is_comment():
            res_dict['dissimilar'].append(malicious_node.name)
        for child in malicious_node.children:
            dissimilar(child, res_dict)


def get_percentage_cloned_node(node, cloned=0, total=0):
    """
        Gets the number of nodes in node that are cloned of nodes in another PDG,
        as well as the total number of nodes.

        -------
        Parameters:
        - node: Node
            Current node to analyze.
        - cloned: int
            Number of cloned nodes.
        - total: int
            Total number of nodes.

        -------
        Returns:
        - list
            * Elt1: int, number of cloned nodes;
            * Elt2: int, total number of nodes.
    """

    for child in node.children:
        if child.clone:
            cloned += 1
            total += 1
        elif not child.is_comment():
            total += 1
        [cloned, total] = get_percentage_cloned_node(child, cloned=cloned, total=total)
    return [cloned, total]


def get_percentage_cloned(dfg_nodes1, dfg_nodes2, res_dict):
    """
        Gets the percentage of the nodes in dfg_nodes1 that are in dfg_nodes2, and the contrary.

        -------
        Parameters:
        - dfg_nodes1: Node
            PDG of the benign file.
        - dfg_nodes2: Node
            PDG of the malicious file.
        - res_dict: dict
            Contains the different results obtained so far.
    """

    [clone1d, total1] = get_percentage_cloned_node(dfg_nodes1)
    [clone2d, total2] = get_percentage_cloned_node(dfg_nodes2)

    res_dict['%benign'] = [clone1d, total1]
    res_dict['%malicious'] = [clone2d, total2]

    """
    if (100 * clone2d / total2) > 90:
        print(str(100*clone1d/total1) + '% of ' + str(dfg_nodes1.id) + ' is in '
              + str(dfg_nodes2.id) + '. It represents ' + str(clone1d) + '/' + str(total1))
        print(str(100 * clone2d / total2) + '% of ' + str(dfg_nodes2.id) + ' is in '
              + str(dfg_nodes1.id) + '. It represents ' + str(clone2d) + '/' + str(total2))
    """

    return clone2d / total2
