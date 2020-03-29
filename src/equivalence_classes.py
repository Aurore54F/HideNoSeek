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
    1. Find pairs of clone (equivalence class).
"""


from bi_list import *


def get_equivalence_classes_graph(pdg, my_id, equivalence_classes):
    """
        Get the equivalence classes (i.e. the node type defined as Node.name) present in graph.

        -------
        Parameters:
        - pdg: Node
            PDG considered.
        - my_id: int, either 1 or 2
            Indicates if we are handling graph1 or graph2.
        - equivalence_classes: list of EquivalenceClass
            Stores the equivalence classes present in graph.

        -------
        Returns:
        - list of EquivalenceClass
            Equivalence classes currently used.
    """

    for child in pdg.children:
        # if child.statement_dep_parents:
        # pass  # Do nothing if the child is linked to his parent through a statement dependency
        if child.is_statement():
            if child.control_dep_children:
                pass  # Do nothing as will be tested using backward slicing if it matches
            else:
                if child.name in equivalence_classes.keys():
                    logging.debug('A new %s was added to the equivalence class', child.name)
                else:
                    logging.debug('The equivalence class %s was created', child.name)
                    equivalence_classes[child.name] = BiList()
                equivalence_classes[child.name].append_equivalence(child, my_id)
        get_equivalence_classes_graph(child, my_id, equivalence_classes)
    return equivalence_classes


def get_equivalence_classes(graph1, graph2, equivalence_classes):
    """
        Get the equivalence classes (i.e. the node type defined as Node.name) present in
        graph1 and graph2.

        -------
        Parameters:
        - graph1: Node
            PDG1.
        - graph2: Node
            PDG2.
        - equivalence_classes: list of EquivalenceClass
            Stores the equivalence classes present in graph.

        -------
        Returns:
        - list of EquivalenceClass
            Equivalence classes currently used.
    """

    get_equivalence_classes_graph(graph1, my_id=1, equivalence_classes=equivalence_classes)
    get_equivalence_classes_graph(graph2, my_id=2, equivalence_classes=equivalence_classes)
    return equivalence_classes
