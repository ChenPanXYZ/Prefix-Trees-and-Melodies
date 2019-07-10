"""CSC148 Assignment 2: Autocomplete engines

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module description ===
This file contains starter code for the three different autocomplete engines
you are writing for this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
import csv
from typing import Any, Dict, List, Optional, Tuple

from melody import Melody
from prefix_tree import SimplePrefixTree, CompressedPrefixTree


################################################################################
# Text-based Autocomplete Engines (Task 4)
################################################################################
class LetterAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few letters.

    The *prefix sequence* for a string is the list of characters in the string.
    This can include space characters.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a text file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Each line of the specified file counts as one input string.
        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one alphanumeric character, it is inserted into the
        Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given a weight of one.
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight (because of how Autocompleter.insert works).
        """
        # We've opened the file for you here. You should iterate over the
        # lines of the file and process them according to the description in
        # this method's docstring.
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        else:
            self.autocompleter = CompressedPrefixTree(config['weight_type'])
        with open(config['file'], encoding='utf8') as f:
            temp = f.readlines()
        for i in range(len(temp)):
            temp[i] = ''.join(c for c in temp[i] if c.isalnum() or c == ' ')
            temp[i] = temp[i].lower()

        inserted_value_list = []
        for item in temp:
            inserted_value_list.append((item.strip(), [c for c in item]))
        for inserted_value in inserted_value_list:
            if inserted_value[1] and \
                    not all([c == ' ' for c in inserted_value[1]]):
                self.autocompleter.insert(
                    inserted_value[0], 1.0, inserted_value[1])

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix = prefix.lower()
        prefix = [c for c in prefix if c.isalnum() or c == ' ']
        return self.autocompleter.autocomplete([c for c in prefix], limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix string.

        Note that the given prefix string must be transformed into a list
        of letters before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix = prefix.lower()
        prefix = [c for c in prefix if c.isalnum() or c == ' ']
        return self.autocompleter.remove([c for c in prefix])


class SentenceAutocompleteEngine:
    """An autocomplete engine that suggests strings based on a few words.

    A *word* is a string containing only alphanumeric characters.
    The *prefix sequence* for a string is the list of words in the string
    (separated by whitespace). The words themselves do not contain spaces.

    This autocomplete engine only stores and suggests strings with lowercase
    letters, numbers, and space characters; see the section on
    "Text sanitization" on the assignment handout.

    === Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has two entries:
            - the first entry is a string
            - the second entry is the a number representing the weight of that
              string

        Note that the line may or may not contain spaces.
        Each string must be sanitized, and if the resulting string contains
        at least one word, it is inserted into the Autocompleter.

        *Skip lines that do not contain at least one alphanumeric character!*

        When each string is inserted, it is given THE WEIGHT SPECIFIED ON THE
        LINE FROM THE CSV FILE. (Updated Nov 19)
        Note that it is possible for the same string to appear on more than
        one line of the input file; this would result in that string getting
        a larger weight.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        else:
            self.autocompleter = CompressedPrefixTree(config['weight_type'])
        with open(config['file'], encoding='utf8') as csvfile:
            temp = []
            reader = csv.reader(csvfile)
            for line in reader:
                temp.append(tuple(map(str, line)))
        inserted_value_list = []
        for item in temp:
            temp_prefix = ''.join(
                c for c in item[0].lower() if c.isalnum() or c == ' ')
            inserted_value_list.append((temp_prefix, item[1],
                                        temp_prefix.split()))

        for inserted_value in inserted_value_list:
            if inserted_value[2] and not \
                    all([c == ' ' for c in inserted_value[2]]):
                self.autocompleter.insert(
                    inserted_value[0], float(inserted_value[1]),
                    inserted_value[2])

    def autocomplete(self, prefix: str,
                     limit: Optional[int] = None) -> List[Tuple[str, float]]:
        """Return up to <limit> matches for the given prefix string.

        The return value is a list of tuples (string, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Preconditions:
            limit is None or limit > 0
            <prefix> contains only lowercase alphanumeric characters and spaces
        """
        prefix = ''.join(c for c in prefix.lower() if c.isalnum() or c == ' ')
        return self.autocompleter.autocomplete(prefix.split(), limit)

    def remove(self, prefix: str) -> None:
        """Remove all strings that match the given prefix.

        Note that the given prefix string must be transformed into a list
        of words before being passed to the Autocompleter.

        Precondition: <prefix> contains only lowercase alphanumeric characters
                      and spaces.
        """
        prefix = ''.join(c for c in prefix.lower() if c.isalnum() or c == ' ')
        return self.autocompleter.remove(prefix.split())


################################################################################
# Melody-based Autocomplete Engines (Task 5)
################################################################################
class MelodyAutocompleteEngine:
    """An autocomplete engine that suggests melodies based on a few intervals.

    The values stored are Melody objects, and the corresponding
    prefix sequence for a Melody is its interval sequence.

    Because the prefix is based only on interval sequence and not the
    starting pitch or duration of the notes, it is possible for different
    melodies to have the same prefix.

    # === Private Attributes ===
    autocompleter: An Autocompleter used by this engine.
    """
    autocompleter: Autocompleter

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize this engine with the given configuration.

        <config> is a dictionary consisting of the following keys:
            - 'file': the path to a CSV file
            - 'autocompleter': either the string 'simple' or 'compressed',
              specifying which subclass of Autocompleter to use.
            - 'weight_type': either 'sum' or 'average', which specifies the
              weight type for the prefix tree.

        Precondition:
        The given file is a *CSV file* where each line has the following format:
            - The first entry is the name of a melody (a string).
            - The remaining entries are grouped into pairs (as in Assignment 1)
              where the first number in each pair is a note pitch,
              and the second number is the corresponding duration.

            HOWEVER, there may be blank entries (stored as an empty string '');
            as soon as you encounter a blank entry, stop processing this line
            and move onto the next line the CSV file.

        Each melody is be inserted into the Autocompleter with a weight of 1.
        """
        # We haven't given you any starter code here! You should review how
        # you processed CSV files on Assignment 1.
        if config['autocompleter'] == 'simple':
            self.autocompleter = SimplePrefixTree(config['weight_type'])
        else:
            self.autocompleter = CompressedPrefixTree(config['weight_type'])

        with open(config['file'], encoding='utf8') as csvfile:
            temp = []
            reader = csv.reader(csvfile)
            for line in reader:
                temp.append(list(map(str, line)))

        inserted_value_list = []

        for item in temp:
            notes = []
            for i in range(1, len(item), 2):
                # Can we remove item[i] who is not digital at first?
                if item[i].isdigit() and item[i+1].isdigit():
                    temp_note = (int(item[i]), int(item[i+1]))
                    notes.append(temp_note)
            interval = []
            for k in range(len(notes) - 1):
                interval.append(notes[k + 1][0] - notes[k][0])
            inserted_value_list.append((Melody(item[0], notes), interval))

        for inserted_value in inserted_value_list:
            if inserted_value[1]:
                self.autocompleter.insert(inserted_value[0], 1.0,
                                          inserted_value[1])

    def autocomplete(self, prefix: List[int],
                     limit: Optional[int] = None) -> List[Tuple[Melody, float]]:
        """Return up to <limit> matches for the given interval sequence.

        The return value is a list of tuples (melody, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given interval sequence.

        Precondition:
            limit is None or limit > 0
        """
        return self.autocompleter.autocomplete(prefix, limit)

    def remove(self, prefix: List[int]) -> None:
        """Remove all melodies that match the given interval sequence.
        """
        return self.autocompleter.remove(prefix)


###############################################################################
# Sample runs
###############################################################################
def sample_letter_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the letter autocomplete engine."""
    engine = LetterAutocompleteEngine({
        # NOTE: you should also try 'data/google_no_swears.txt' for the file.
        'file': 'data/lotr.txt',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    return engine.autocomplete('frodo d', 20)


def sample_sentence_autocomplete() -> List[Tuple[str, float]]:
    """A sample run of the sentence autocomplete engine."""
    engine = SentenceAutocompleteEngine({
        'file': 'data/google_searches.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    return engine.autocomplete('how to', 20)


def sample_melody_autocomplete() -> None:
    """A sample run of the melody autocomplete engine."""
    engine = MelodyAutocompleteEngine({
        'file': 'data/random_melodies_c_scale.csv',
        'autocompleter': 'simple',
        'weight_type': 'sum'
    })
    melodies = engine.autocomplete([2, 2], 20)
    for melody, _ in melodies:
        melody.play()


if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'allowed-io': ['__init__'],
    #     'extra-imports': ['csv', 'prefix_tree', 'melody']
    # })
    #
    # This is used to increase the recursion limit so that your sample runs
    # work even for fairly tall simple prefix trees.
    import sys
    sys.setrecursionlimit(5000)

    print(sample_letter_autocomplete())
    print(sample_sentence_autocomplete())
    sample_melody_autocomplete()
