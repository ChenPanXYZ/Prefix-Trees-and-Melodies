"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """
    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type: A str records what kind of aggregate weight it is.
    length: A int that records how many leaves are in the tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    length: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0.0
        self.subtrees = []
        self.weight_type = weight_type
        self.length = 0

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        # Does it mean to count leaves?
        if self.is_empty():
            return 0
        elif self.is_leaf():
            return 1
        else:
            length = 0
            for subtree in self.subtrees:
                length += len(subtree)
            return length

    def update_weight(self, weight: float, change: int) -> None:
        """Change the weight after insertion."""
        if self.weight_type == 'average':
            self.weight = \
                (self.weight * (self.length - change) + weight) / self.length
        else:
            self.weight = self.weight + weight

    def isprefix(self, prefix: list) -> bool:
        """This function judges whether a tree is a 'prefix' of a list. If the
        value of the tree is the 'prefix' of a list, will return True. Otherwise
        will return False.
        """
        if not isinstance(self.value, list):
            return False
        elif len(self.value) > len(prefix):
            return False
        else:
            return all(
                [self.value[i] == prefix[i] for i in range(len(self.value))])

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        if self.is_empty():
            last_new_prefix = self.add_new_common_prefix(
                prefix[len(self.value):], weight)
            new_leaf = SimplePrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            last_new_prefix.subtrees.append(new_leaf)
            last_new_prefix.length = last_new_prefix.length + 1
            self.weight = float(weight)
            return
        elif self.value == prefix:
            # That means the prefix is in the tree.
            for subtree in self.subtrees:
                if subtree.value == value:
                    # That means the value is in the tree. So the length does
                    # not need to be updated.
                    subtree.weight = float(subtree.weight + weight)
                    self.update_weight(weight, 0)
                    self.subtrees = sorted(self.subtrees,
                                           key=lambda x: x.weight, reverse=True)
                    return
            # the value is not in the tree although the prefix is in.
            # Length needs to be updated.
            new_leaf = SimplePrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            self.subtrees.append(new_leaf)
            self.length = self.length + 1
            self.update_weight(weight, 1)
            self.subtrees = sorted(self.subtrees,
                                   key=lambda x: x.weight, reverse=True)
            return
        else:
            # self.value is not the prefix, not sure whether prefix is in
            # or not. May need recursive call.
            for subtree in self.subtrees:
                if subtree.isprefix(prefix):
                    old_subtree_length = subtree.length
                    subtree.insert(value, weight, prefix)
                    self.length = self.length + (subtree.length -
                                                 old_subtree_length)
                    self.update_weight(weight,
                                       (subtree.length - old_subtree_length))
                    self.subtrees = sorted(self.subtrees,
                                           key=lambda x: x.weight,
                                           reverse=True)
                    self.subtrees = sorted(self.subtrees,
                                           key=lambda x: x.weight, reverse=True)
                    return
            last_new_prefix = self.add_new_common_prefix(
                prefix[len(self.value):], weight)
            new_leaf = SimplePrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            last_new_prefix.subtrees.append(new_leaf)
            last_new_prefix.length = last_new_prefix.length + 1
            self.update_weight(weight, 1)
            self.subtrees = sorted(self.subtrees,
                                   key=lambda x: x.weight, reverse=True)
            return

    def add_new_common_prefix(self, prefix: List, weight: float) \
            -> SimplePrefixTree:
        """Add new_common_prefix below an internal value and return the new
        common prefix.
        """
        if not prefix:
            return self
        else:
            new_common_prefix = SimplePrefixTree(self.weight_type)
            new_common_prefix.value = self.value + [prefix[0]]
            new_common_prefix.weight = float(weight)
            self.subtrees.append(new_common_prefix)
            self.length = self.length + 1
            return new_common_prefix.add_new_common_prefix(prefix[1:], weight)

    def search_prefix(self, prefix: List) -> tuple:
        """Find which internal value we should end at.
        There are two possible cases:
        1. Stop when we find prefix == self.value, in other words, the prefix
         exists in the tree already.
        2. Stop when we find prefix doesn't contain all items in any
        subtree.value).
        This function maybe called recursively, if we find one subtree.value
        whose items are all in prefix.
        """
        if self.value == prefix:
            return self, True
        else:
            keep_search = False
            i = 0
            for i in range(len(self.subtrees)):
                if isinstance(self.subtrees[i].value, list):
                    # Will len(self.subtrees[i].value > len(prefix))
                    # and it causes a problem?
                    if all([self.subtrees[i].value[k] == prefix[k] for k in
                            range(len(self.subtrees[i].value))]) \
                            and not self.subtrees[i].is_leaf():
                        keep_search = True
                        break
            if keep_search:
                return self.subtrees[i].search_prefix(prefix)
            else:
                return self, False

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        stop_point, prefix_is_in = self.search_prefix(prefix)
        if prefix_is_in is False:
            return []
        else:
            accumulator = stop_point.autocomplete_helper(limit)
        return accumulator

    def autocomplete_helper(self, limit: Optional[int] = None) \
            -> List[Tuple[Any, float]]:
        """Return leafs in self and store the value and weight of the leaf to
        a list. Once the length of the list meets the limit, will return the
        list immediately.
        """
        accumulator = []
        if limit is None or limit > 0:
            if self.is_leaf():
                return [(self.value, self.weight)]
            else:
                for subtree in self.subtrees:
                    if limit is not None:
                        accumulator.extend(subtree.autocomplete_helper(
                            limit - len(accumulator)))
                    else:
                        accumulator.extend(subtree.autocomplete_helper(limit))
                accumulator = sorted(accumulator,
                                     key=lambda x: x[1],
                                     reverse=True)
                return accumulator
        else:
            accumulator = sorted(accumulator,
                                 key=lambda x: x[1],
                                 reverse=True)
            return accumulator

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        # Need to sort!
        if not prefix:
            while len(self.subtrees) != 0:
                self.subtrees.pop()
            self.weight = 0.0
            self.length = 0
        for subtree in self.subtrees:
            if subtree.value == prefix:
                old_subtree_weight = float(subtree.weight)
                old_subtree_len = subtree.length
                old_len = self.length
                self.subtrees.remove(subtree)
                self.length = self.length - old_subtree_len
                if not self.subtrees:
                    self.weight = 0.0
                elif self.weight_type == 'sum':
                    self.weight = float(self.weight - old_subtree_weight)
                else:
                    self.weight = (self.weight * old_len - old_subtree_weight *
                                   old_subtree_len) / self.length
            elif subtree.isprefix(prefix):
                old_subtree_len = subtree.length
                old_len = self.length
                old_subtree_weight = float(subtree.weight)
                subtree.remove(prefix)
                self.length = self.length + (subtree.length - old_subtree_len)
                if self.length == 0:
                    self.weight = 0.0
                elif self.weight_type == 'sum':
                    self.weight = float(self.weight +
                                        (subtree.weight - old_subtree_weight))
                else:
                    weight_change = \
                        -(subtree.weight * subtree.length -
                          old_subtree_weight * old_subtree_len)
                    self.weight = \
                        (self.weight * old_len + weight_change) / self.length
        self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                               reverse=True)
        self.remove_empty_prefix()

    def remove_empty_prefix(self) -> None:
        """Remove all the empty prefix(weight == 0)"""
        for subtree in self.subtrees:
            if subtree.weight == 0.0:
                self.subtrees.remove(subtree)
            else:
                subtree.remove_empty_prefix()

    def assign(self, value: Any, weight: float) -> None:
        """Assign a value and weight to a PrefixTree."""
        self.value = value
        self.weight = float(weight)


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
class CompressedPrefixTree(SimplePrefixTree):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.
    weight_type: A str records what kind of aggregate weight it is.
    length: A int that records how many leaves are in the tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[CompressedPrefixTree]
    weight_type: str
    length: int

    def isprefix(self, prefix: List) -> bool:
        """Check whether self.value is the prefix of the 'prefix'"""
        if self.is_leaf():
            return False
        elif len(self.value) > len(prefix):
            return False
        else:
            return all([self.value[i] == prefix[i] for i in
                        range(len(self.value))])

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        if self.is_empty():
            self.assign(prefix, weight)
            new_leaf = CompressedPrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            self.subtrees.append(new_leaf)
            self.length = 1
            return
        elif self.value != [] and all([prefix[i] != self.value[i] for i in
                                       range(min(len(prefix),
                                                 len(self.value)))]):
            self.com_insert_case_1_helper(value, prefix, weight)
            return
        elif self.value == prefix:
            for subtree in self.subtrees:
                if subtree.value == value:
                    self.com_insert_case_2_helper(subtree, weight)
                    return
            self.com_insert_case_3_helper(value, weight)
            return
        elif len(self.value) >= len(prefix) and all([self.value[i] == prefix[i]
                                                     for i in
                                                     range(len(prefix))]):
            self.com_insert_case_4_helper(value, prefix, weight)
            return
        elif len(self.value) >= len(prefix):
            common_part = self.get_common_part(prefix)
            if all([self.value[i] == common_part[i] for i in
                    range(len(common_part))]):
                self.com_insert_case_5_helper(
                    value, prefix, weight, common_part)
                return
        elif all([self.value[i] == prefix[i] for i in range(len(self.value))]):
            for subtree in self.subtrees:
                if subtree.isprefix(prefix):
                    old_subtree_length = subtree.length
                    subtree.insert(value, weight, prefix)
                    self.length = self.length + (subtree.length -
                                                 old_subtree_length)
                    self.update_weight(weight,
                                       (subtree.length - old_subtree_length))
                    self.subtrees = sorted(self.subtrees,
                                           key=lambda x: x.weight,
                                           reverse=True)
                    return
                elif not subtree.is_leaf():
                    if self.com_insert_case_6_helper(
                            value, prefix, weight, subtree):
                        return
                    elif self.com_insert_case_7_helper(
                            value, prefix, weight, subtree):
                        return
            self.com_insert_case_8_helper(value, prefix, weight)
            return
        else:
            common_part = self.get_common_part(prefix)
            self.com_insert_case_9_helper(value, prefix, weight, common_part)
            return

    def com_insert_case_1_helper(self, value: Any,
                                 prefix: List, weight: float) -> None:
        """Case 1
        only happens when the top is not [].
        """
        temp_self = CompressedPrefixTree(self.weight_type)
        temp_self.assign(self.value, self.weight)
        temp_self.subtrees = self.subtrees
        temp_self.length = self.length
        if not prefix:
            new_leaf = CompressedPrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            self.value = []
            if self.weight_type == 'average':
                self.weight = (self.weight * self.length + weight) / \
                              (self.length + 1)
            else:
                self.weight = float(self.weight + weight)
                self.subtrees = [temp_self, new_leaf]
                self.length = self.length + 1
                self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                                       reverse=True)
        else:
            new_prefix = CompressedPrefixTree(self.weight_type)
            new_prefix.assign(prefix, weight)
            new_leaf = CompressedPrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            new_prefix.subtrees.append(new_leaf)
            new_prefix.length = new_prefix.length + 1
            self.value = []
            if self.weight_type == 'average':
                self.weight = (self.weight * self.length + weight) / \
                              (self.length + 1)
            else:
                self.weight = float(self.weight + weight)
            self.subtrees = [temp_self, new_prefix]
            self.length = self.length + 1
            self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                                   reverse=True)

    def com_insert_case_2_helper(
            self, subtree: CompressedPrefixTree, weight: float) -> None:
        """case 2
        The value is in the tree.
        """
        subtree.weight = (subtree.weight + weight)
        self.update_weight(weight, 0)
        self.subtrees = sorted(self.subtrees,
                               key=lambda x: x.weight,
                               reverse=True)

    def com_insert_case_3_helper(self, value: Any, weight: float) -> None:
        """Case 3
        The prefix is in. But the value that consists of every item in the
        prefix does not exist.
        """
        new_leaf = CompressedPrefixTree(self.weight_type)
        new_leaf.assign(value, weight)
        self.subtrees.append(new_leaf)
        self.length = self.length + 1
        self.update_weight(weight, 1)
        self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                               reverse=True)

    def com_insert_case_4_helper(self, value: Any,
                                 prefix: List, weight: float) -> None:
        """Case 4
        Prefix is the prefix of 'self'.
        """
        temp_self = CompressedPrefixTree(self.weight_type)
        temp_self.assign(self.value, self.weight)
        temp_self.subtrees = self.subtrees
        temp_self.length = self.length
        new_leaf = CompressedPrefixTree(self.weight_type)
        new_leaf.assign(value, weight)
        self.value = prefix
        self.length = self.length + 1
        self.update_weight(weight, 1)
        self.subtrees = [temp_self, new_leaf]
        self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                               reverse=True)

    def com_insert_case_5_helper(
            self, value: Any, prefix: List, weight: float, common_part: List) \
            -> None:
        """Case 5
        len(self.value) >= len(prefix), no need to recursive.
        And common_part is the prefix of both of them
        """
        temp_self = CompressedPrefixTree(self.weight_type)
        temp_self.assign(self.value, self.weight)
        temp_self.subtrees = self.subtrees
        temp_self.length = self.length
        new_prefix = CompressedPrefixTree(self.weight_type)
        new_prefix.assign(prefix, weight)
        new_leaf = CompressedPrefixTree(self.weight_type)
        new_leaf.assign(value, weight)
        new_prefix.subtrees.append(new_leaf)
        new_prefix.length = new_prefix.length + 1
        self.value = common_part
        self.length = self.length + 1
        self.update_weight(weight, 1)
        self.subtrees = [temp_self, new_prefix]
        self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                               reverse=True)

    def com_insert_case_6_helper(
            self, value: Any, prefix: List, weight: float,
            subtree: CompressedPrefixTree) -> bool:
        """Case 6
        common_part between subtree and prefix must contain self.value.
        """
        common_part = subtree.get_common_part(prefix)
        if common_part != [] and len(common_part) > len(self.value) \
                and common_part != prefix:
            index = self.subtrees.index(subtree)
            new_parent = CompressedPrefixTree(self.weight_type)
            new_parent.assign(common_part, 1)
            new_prefix = CompressedPrefixTree(self.weight_type)
            new_prefix.assign(prefix, weight)
            new_leaf = CompressedPrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            new_prefix.subtrees.append(new_leaf)
            new_prefix.length = new_prefix.length + 1
            new_parent.subtrees = [subtree, new_prefix]
            new_parent.subtrees = sorted(new_parent.subtrees,
                                         key=lambda x: x.weight,
                                         reverse=True)
            new_parent.length = subtree.length + 1
            self.length = self.length + 1
            if self.weight_type == 'average':
                new_parent.weight = \
                    (subtree.weight * subtree.length + weight) \
                    / new_parent.length
                self.weight = \
                    (self.weight * (self.length - 1) + weight) \
                    / self.length
            else:
                new_parent.weight = float(subtree.weight +
                                          weight)
                self.weight = float(self.weight + weight)
            self.subtrees[index] = new_parent
            self.subtrees = sorted(self.subtrees,
                                   key=lambda x: x.weight,
                                   reverse=True)
            return True
        else:
            return False

    def com_insert_case_7_helper(
            self, value: Any, prefix: List, weight: float,
            subtree: CompressedPrefixTree) -> bool:
        """Case 7
        common_part between subtree and prefix does not contain self.value.
        """
        common_part = subtree.get_common_part(prefix)
        if common_part != [] and len(common_part) > len(self.value) \
                and common_part == prefix:
            index = self.subtrees.index(subtree)
            new_prefix = CompressedPrefixTree(self.weight_type)
            new_prefix.assign(prefix, weight)
            new_leaf = CompressedPrefixTree(self.weight_type)
            new_leaf.assign(value, weight)
            new_prefix.subtrees = [subtree, new_leaf]
            new_prefix.subtrees = sorted(new_prefix.subtrees,
                                         key=lambda x: x.weight,
                                         reverse=True)
            new_prefix.length = subtree.length + 1
            self.length += 1
            if self.weight_type == 'average':
                new_prefix.weight = (subtree.weight *
                                     subtree.length + weight) \
                                    / new_prefix.length
                self.weight = (self.weight * (self.length - 1)
                               + weight) / self.length
            else:
                new_prefix.weight = float(subtree.weight +
                                          weight)
                self.weight = float(self.weight + weight)
            self.subtrees[index] = new_prefix
            self.subtrees = sorted(self.subtrees,
                                   key=lambda x: x.weight,
                                   reverse=True)
            return True
        else:
            return False

    def com_insert_case_8_helper(
            self, value: Any, prefix: List, weight: float) -> None:
        """Case 8
        None of the subtree is the prefix of the 'prefix'.
        No recursive call is made.
        """
        new_prefix = CompressedPrefixTree(self.weight_type)
        new_prefix.assign(prefix, weight)
        new_leaf = CompressedPrefixTree(self.weight_type)
        new_leaf.assign(value, weight)
        new_prefix.subtrees.append(new_leaf)
        new_prefix.length += 1
        self.subtrees.append(new_prefix)
        self.length += 1
        if self.weight_type == 'average':
            self.weight = (self.weight * (self.length - 1) + weight) / \
                          self.length
        else:
            self.weight = float(self.weight + weight)
        self.subtrees = sorted(self.subtrees,
                               key=lambda x: x.weight,
                               reverse=True)

    def com_insert_case_9_helper(
            self, value: Any, prefix: List, weight: float, common_part: List) \
            -> None:
        """Case 9
        In this case, self is not the prefix of prefix, so we do not need
        to make a recursive call.
        And, len(prefix) > len(self) and they share some
        same parts according to the conditions of other cases.
        """
        temp_self = CompressedPrefixTree(self.weight_type)
        temp_self.assign(self.value, self.weight)
        temp_self.subtrees = self.subtrees
        temp_self.length = self.length
        new_prefix = CompressedPrefixTree(self.weight_type)
        new_prefix.assign(prefix, weight)
        new_leaf = CompressedPrefixTree(self.weight_type)
        new_leaf.assign(value, weight)
        new_prefix.subtrees.append(new_leaf)
        new_prefix.length += 1
        self.value = common_part
        if self.weight_type == 'average':
            self.weight = (self.weight * self.length + weight) / \
                          (self.length + 1)
        else:
            self.weight = float(self.weight + weight)
        self.subtrees = [temp_self, new_prefix]
        self.length += 1
        self.subtrees = sorted(self.subtrees, key=lambda x: x.weight,
                               reverse=True)

    def get_common_part(self, prefix: List) -> List:
        """Get the common part with prefix."""
        common_part = []
        for i in range(min(len(prefix), len(self.value))):
            if prefix[i] == self.value[i]:
                common_part.append(prefix[i])
            else:
                return common_part
        return common_part

    def search_prefix(self, prefix: List) -> tuple:
        """Find which internal value we should end at.
        There are two possible cases:
        1. Stop when we find prefix == self.value, in other words, the prefix
         exists in the tree already.
        2. Stop when we find prefix doesn't contain all items in any
        subtree.value).
        This function maybe called recursively, if we find one subtree.value
        whose items are all in prefix.
        """
        if len(prefix) <= len(self.value) and \
                all([prefix[i] == self.value[i] for i in range(len(prefix))]):
            # In this case, prefix is the prefix of self, so we need to output
            # every leaf in self.
            return self, True
        elif len(prefix) <= len(self.value):
            return self, False
        else:
            # In this case, prefix is longer than self.value. That means,
            #  perhaps it is the prefix of a subtree
            # in self. If so, recursive call is needed. Otherwise,
            #  no recursive call is needed.
            for subtree in self.subtrees:
                if len(prefix) <= len(subtree.value) \
                        and all([prefix[i] == subtree.value[i]
                                 for i in range(len(prefix))]):
                    # prefix is the prefix of this subtree.
                    return subtree.search_prefix(prefix)
                elif len(prefix) > len(subtree.value) \
                        and all([prefix[i] == subtree.value[i]
                                 for i in range(len(subtree.value))]):
                    # subtree is the prefix of the 'prefix'.
                    return subtree.search_prefix(prefix)
            return self, False

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        if not prefix:
            self.subtrees = []
            self.weight = 0.0
            self.length = 0
        elif len(self.value) >= len(prefix) and \
                all([prefix[i] == self.value[i] for i in range(len(prefix))]):
            # prefix is the prefix of self.
            self.value = []
            self.weight = 0.0
            self.length = 0
        else:
            for subtree in self.subtrees:
                if len(subtree.value) >= len(prefix) and \
                        all([prefix[i] == subtree.value[i]
                             for i in range(len(prefix))]) and \
                        not subtree.is_leaf():
                    old_subtree_weight = float(subtree.weight)
                    old_subtree_length = len(subtree)
                    old_length = self.length
                    self.subtrees.remove(subtree)
                    # subtree is removed.
                    self.length = self.length - old_subtree_length
                    if self.weight_type == 'average':
                        self.weight = \
                            (self.weight * old_length - old_subtree_weight
                             * old_subtree_length) / self.length
                    else:
                        self.weight = float(self.weight -
                                            old_subtree_weight)
                        # need to check whether self is compressible?
                    if len(self.subtrees) == 1 and \
                            not self.subtrees[0].is_leaf():
                        temp = self.subtrees[0]
                        self.value = temp.value
                        self.subtrees = temp.subtrees
                        self.weight = temp.weight
                        self.length = temp.length
                    self.subtrees = sorted(self.subtrees,
                                           key=lambda x: x.weight,
                                           reverse=True)
                    return
                elif subtree.isprefix(prefix) and not subtree.is_leaf():
                    old_length = self.length
                    old_subtree_weight = subtree.weight
                    old_subtree_length = subtree.length
                    subtree.remove(prefix)
                    self.length = self.length - (old_subtree_length -
                                                 subtree.length)
                    if self.weight_type == 'average':
                        self.weight = (self.weight * old_length -
                                       (old_subtree_weight * old_subtree_length
                                        - subtree.weight * subtree.length)) / \
                                      self.length
                    else:
                        self.weight = float(self.weight -
                                            (old_subtree_weight -
                                             subtree.weight))
                        # need to check it!
                    if len(subtree.subtrees) == 1 and \
                            not subtree.subtrees[0].is_leaf():
                        index = self.subtrees.index(subtree)
                        self.subtrees[index] = subtree.subtrees[0]
                    self.subtrees = sorted(self.subtrees,
                                           key=lambda x: x.weight,
                                           reverse=True)
                    self.remove_empty_prefix()

    def remove_helper(self) -> None:
        """If self is compressible, will compress it to its only child."""
        if len(self.subtrees) == 1 and \
                not self.subtrees[0].is_leaf():
            temp = self.subtrees[0]
            self.value = temp.value
            self.subtrees = temp.subtrees
            self.weight = temp.weight
            self.length = temp.length
        else:
            return


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
