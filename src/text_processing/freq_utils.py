#!/usr/bin/env python
"""Provides utility methods `tokenize_file` and `print_frequencies` for text processing.
"""

import sys
import re
from io import TextIOWrapper
from text_processing.freq_models import Frequency

__author__ = "Garrett Buchanan, Livingstone Rwagatare"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Garrett Buchanan", "Livingstone Rwagatare",
               "Donald J. Patterson", "Mike Ryu", ]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"


def tokenize_file(file_obj: TextIOWrapper) -> list:
    """Reads the input text file and splits it into alphanumeric tokens.

    Args:
        file_obj (TextIOWrapper): file to tokenize.

    Yields:
        A list of these tokens, ordered according to their occurrence in the original text file. #Iterate
        Non-alphanumeric characters except for `'` delineate tokens, and are discarded. #Find Proper Regex
        Tokens should not span multiple lines and words are also normalized to lower case. # Format Properly

    Example:
        Given the file object containing: "An input string, this is! (or isn't it?) 123-45"

        >>> fo = open("/path/to/file.txt", 'r')
        >>> tokenize_file(fo)
        ["an", "input", "string", "this", "is", "or", "isn't", "it", "123", "45"]
    """
    #Attempt 1:
    #How it works / Comment:
        #token_pattern will match words which may include numbers and apostrophes
        #Then we iterate over each line of the file_obj
        #Each line is converted to lower case then all words are found using re.findal and appended to the tokens list
        #finally tokes list is returned
        #downflows:
        #This code can't help us when dealing with large files - altenatively we can use yield
    token_pattern = re.compile(r"[\w']+")
    tokens = []
    # Process the file line by line
    for line in file_obj:
        # Normalize to lower case
        line = line.lower()
        # Find all tokens in the line and add them to the tokens list
        tokens.extend(re.findall(token_pattern, line)) 
    return tokens

def print_frequencies(freqs: list[Frequency], out: TextIOWrapper) -> None:
    """Takes a list of `Frequency`s and outputs it to the stream passed in via the `out` argument.

    Also prints out the total number of items, and the total number of unique items.

    Args:
        freqs (list[Frequency]): a list of `Frequencies`s
        out (TextIOWrapper): output stream to print to.

    Example:
        Given the input list of word frequencies: f1 = [sentence:2, the:1, this:1, repeats:1,  word:1]

        >>> f1 = [ ... ]
        >>> print_frequencies(f1, sys.stdout)
             6 total items
             5 unique items

             2 sentence
             1 the
             1 this
             1 repeats
             1 word

        Given a list of frequencies, the `__str__` method should be called on the item that is being counted.
        With a `TwoGram` frequencies list: f2 = [<you,think>:2, <how,you>:1, <know,how>:1, <think,you>:1, <you,know>:3]

        >>> f2 = [ ... ]
        >>> print_frequencies(f2, sys.stdout)
             8 total items
             5 unique items

             2 you think
             1 how you
             1 know you
             1 think you
             3 you know
    """
    
    total_items = 0
    for freq in freqs:
        total_items += freq.freq
            
    unique_items = len(set(freqs))
     
    # Print out total and unique items  
    out.write(f"{total_items:>6} total items\n")
    out.write(f"{unique_items:>6} unique items\n\n")
    
    for freq in freqs:
        out.write("{:6d} {}\n".format(freq.freq, freq.token))
    try:      
        pass
    except IOError as e:  # Leave this `except` block as-is.
        print("Encountered an error while printing:", e)
