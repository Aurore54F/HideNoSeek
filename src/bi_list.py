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
    Definition of the class BiList: similar Node objects between two PDGs.
"""

import logging
import copy


class BiList:

    def __init__(self):
        self.list1 = []
        self.list2 = []

    def append_equivalence(self, elt, my_id):
        if my_id == 1:
            self.list1.append(elt)
            return self
        if my_id == 2:
            self.list2.append(elt)
            return self
        logging.error('The id given should be either 1 or 2. Got %s', str(my_id))
        return None

    def append_list(self, elt1, elt2):
        self.list1.append(elt1)
        self.list2.append(elt2)

    def add_elements_begin(self, some_list):
        self.list1[:0] = some_list.list1
        self.list2[:0] = some_list.list2

    def add_elements_pos(self, pos, some_list):
        keep_pos = pos
        for elt in some_list.list1:
            self.list1.insert(pos, elt)
            pos += 1
        for elt in some_list.list2:
            self.list2.insert(keep_pos, elt)
            keep_pos += 1

    def extend_list(self, some_list):
        self.list1.extend(some_list.list1)
        self.list2.extend(some_list.list2)

    def copy_list(self):
        new_list = BiList()
        new_list.list1 = copy.copy(self.list1)
        new_list.list2 = copy.copy(self.list2)
        return new_list

    def is_empty(self):
        return not self.list1 and not self.list2
