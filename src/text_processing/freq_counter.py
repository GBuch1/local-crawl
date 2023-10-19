#!/usr/bin/env python3
"""Counts the total number of either words of `TwoGram`s in a text file.
"""

import sys
import argparse
from text_processing.freq_models import TwoGram, Frequency
from text_processing.freq_utils import tokenize_file, print_frequencies

__author__ = "Garrett Buchanan, Livingstone Rwagatare"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Garrett Buchanan", "Livingstone Rwagatare",
               "Donald J. Patterson", "Mike Ryu", ]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"


def main() -> None:
    pars = setup_argument_parser()
    args = pars.parse_args()
    if args.processing_mode not in [1, 2]:
        pars.error("Processing mode must be either 1 (word) or 2 (twogram).")

    try:
        with open(args.input_file_path, 'r', encoding="UTF-8") as input_file:
            tokens = tokenize_file(input_file)
        if args.processing_mode == 1:
            frequencies = compute_word_freq(tokens)
        elif args.processing_mode == 2:
            frequencies = compute_twogram_freq(tokens)
        with open(args.output_file_path, 'w', encoding="UTF-8") as output_file:
            if args.verbose:
                print_frequencies(frequencies, sys.stdout)
            print_frequencies(frequencies, output_file)
        if args.verbose:  # DO NOT get rid of this -- this will be useful in debugging.
            pass
    except OSError as e:  # Leave this `except` block as-is.
        print("An error occurred while trying to open files:\n  ", e, file=sys.stderr)


def setup_argument_parser():
    pars = argparse.ArgumentParser()
    pars.add_argument("processing_mode", type=int,
                      help="required integer to select desired processing mode, either 1 (word) or 2 (twogram)")
    pars.add_argument("input_file_path", type=str,
                      help="required string containing the path to a text file to process")
    pars.add_argument("output_file_path", type=str,
                      help="required string containing the path to a text file to write the output to")
    pars.add_argument("-v", "--verbose", action="store_true",
                      help="switch to enable verbose mode to mirror (print) the output to console")
    return pars


def compute_word_freq(tokens: list[str]) -> list[Frequency]:
    """Takes the input list of words and processes it, returning a list of `Frequency`s.

    This function expects a list of lowercase alphanumeric strings (in any spoken language).
    If the input list is `None` or empty, an empty list is returned.

    There is one `Frequency` in the output list for every unique word in the original list.
    The frequency of each word is equal to the number of times that word occurs in the original list.

    Args:
        tokens (list[str]): list of lowercase words in any spoken language including numbers (e.g., 1, 123).
                            This list will not be modified.

    Yields:
        A list ordered by decreasing frequency, with tied words sorted lexicographically.

    Example:
        >>> word_freq = compute_word_freq(["this", "sentence", "repeats", "the", "word", "sentence"])
        >>> print(list(map(str, word_freq)))
        ["sentence:2", "repeats:1", "the:1", "this:1",  "word:1"]
    """
    # Returns an empty list if tokens is type None of there is nothing in the inputed list
    if tokens is None or len(tokens) == 0:
        return[]
    # Create a dictionary
    wordsFrequency = {}
    # Iterate through tokens until there is nothing left in tokens
    for token in tokens:
        if token in wordsFrequency:
            wordsFrequency[token] += 1
        else:
            wordsFrequency[token] = 1
    # Create a list freq_list       
    freq_list = [Frequency(word, count) for word, count in wordsFrequency.items()]
    # Return the sorted freq list
    return sorted(freq_list, key=lambda x: (-x.freq, x.token))

def compute_twogram_freq(tokens: list[str]) -> list[Frequency]:
    """Takes the input list of words and processes it, returning a list of `Frequency`s.

    This function expects a list of tokens. If the input list is `None` or empty, an empty list is returned.

    There is one `Frequency` in the output list for every unique `TwoGram` in the original list.
    The frequency of each `TwoGram`s is equal to the number of times that `TwoGram` occurs in the original list.

    Args:
        tokens (list[str]): list of `TwoGrams`. This list will not be modified.

    Yields:
        A list ordered by decreasing frequency, with tied `TwoGram`s sorted lexicographically.

    Example:
        >>> import sys
        >>> from text_processing.freq_utils import print_frequencies
        >>> twogram_freq = compute_twogram_freq(["you", "think", "you", "know", "how", "you", "think"])
        >>> print_frequencies(twogram_freq, sys.stdout)
             6 total items
             5 unique items

             2 <you:think>
             1 <how:you>
             1 <know:how>
             1 <think:you>
             1 <you:know>
    """
    # Returns an empty list if tokens is type None of there is nothing in the inputed list
    if tokens is None or len(tokens) == 0:
        return []
    # Create a dictionary for twogramFrequencies
    twogramFrequencies = {}
    # Iterate through tokens until there is nothing left in tokens
    for i in range(len(tokens) - 1):
        twogram = TwoGram(tokens[i], tokens[i+1])
        if twogram in twogramFrequencies:
            twogramFrequencies[twogram] += 1
        else:
            twogramFrequencies[twogram] = 1
    # Create a list freq_list
    freq_list = [Frequency(twogram, count) for twogram, count in twogramFrequencies.items()]
    # Return the sorted list
    return sorted(freq_list, key=lambda x: (-x.freq, x.token))


if __name__ == '__main__':
    main()
