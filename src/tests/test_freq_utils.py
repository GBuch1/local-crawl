"""Unit tests for functions in `text_processing.freq_utils`.
"""

import io
import os
import unittest

from text_processing.freq_utils import tokenize_file, print_frequencies
from text_processing.freq_models import Frequency

__author__ = "Boaty McBoatface, Planey McPlaneface"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Boaty McBoatface", "Planey McPlaneface",
               "Donald J. Patterson", "Mike Ryu", ]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"


class TokenizeFileTest(unittest.TestCase):
    def setUp(self):
        cwd = os.path.dirname(__file__)
        data_format = "./data/word_{:02d}.in.txt"

        self.sample_paths = [os.path.relpath(data_format.format(i), cwd) for i in range(0, 5)]

    def test_sample_00(self):
        with open(self.sample_paths[0], 'r') as fo:
            self.assertEqual([], tokenize_file(fo))

    def test_sample_01(self):
        with open(self.sample_paths[1], 'r') as fo:
            words = tokenize_file(fo)
            self.assertEqual("an",            words[0])
            self.assertEqual("input",         words[1])
            self.assertEqual("string",        words[2])
            self.assertEqual("this",          words[3])
            self.assertEqual("is",            words[4])
            self.assertEqual("or",            words[5])
            self.assertEqual("is",            words[6])
            self.assertEqual("it",            words[7])
            self.assertEqual("這是一個輸入字符串", words[8])
            self.assertEqual("還是",           words[9])
            self.assertEqual("هذا",           words[10])
            self.assertEqual("هو",            words[11])
            self.assertEqual("سلسلة",         words[12])
            self.assertEqual("المدخلات",       words[13])
            self.assertEqual("أو",            words[14])
            self.assertEqual("هو",            words[15])
            self.assertEqual("c'est",         words[16])
            self.assertEqual("une",           words[17])
            self.assertEqual("chaîne",        words[18])
            self.assertEqual("d'entrée",      words[19])
            self.assertEqual("ou",            words[20])
            self.assertEqual("est",           words[21])
            self.assertEqual("ce",            words[22])
            self.assertEqual("esta",          words[23])
            self.assertEqual("es",            words[24])
            self.assertEqual("una",           words[25])
            self.assertEqual("cadena",        words[26])
            self.assertEqual("de",            words[27])
            self.assertEqual("entrada",       words[28])
            self.assertEqual("o",             words[29])
            self.assertEqual("es",            words[30])

    def test_sample_02(self):
        with open(self.sample_paths[2], 'r') as fo:
            words = tokenize_file(fo)
            self.assertEqual("an",     words[0])
            self.assertEqual("input",  words[1])
            self.assertEqual("string", words[2])
            self.assertEqual("this",   words[3])
            self.assertEqual("is",     words[4])
            self.assertEqual("or",     words[5])
            self.assertEqual("isn't",  words[6])
            self.assertEqual("it",     words[7])
            self.assertEqual("123",    words[8])
            self.assertEqual("45",     words[9])


class PrintFrequenciesTest(unittest.TestCase):
    def test_static(self):
        freqs = [
            Frequency("hi", 1),
            Frequency("hello", 2),
            Frequency("goodbye", 3)
        ]

        actual_out_stream = io.StringIO()
        expected_out_str = ("     6 total items\n     3 unique items\n\n" +
                            "     1 hi\n     2 hello\n     3 goodbye\n")

        print_frequencies(freqs, actual_out_stream)

        actual_out_stream.seek(0)
        actual_out_str = actual_out_stream.read()
        self.assertEqual(expected_out_str, actual_out_str)

    def test_dynamic(self):
        rng = range(0, 26)  # Number of English alphabet letters to enumerate A-Z
        freqs = [Frequency(str(chr(ord('A') + i)), i) for i in rng]

        actual_out_stream = io.StringIO()
        expected_out_str = ("   325 total items\n    26 unique items\n\n" +
                            "".join(["{:>6d} {}\n".format(i, str(chr(ord('A') + i))) for i in rng]))

        print_frequencies(freqs, actual_out_stream)

        actual_out_stream.seek(0)
        actual_out_str = actual_out_stream.read()
        self.assertEqual(expected_out_str, actual_out_str)


if __name__ == '__main__':
    unittest.main()
