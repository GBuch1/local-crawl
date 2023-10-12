"""Unit tests for functions in `text_processing.freq_counter`.
"""

import os
import io
import sys
import unittest

from text_processing.freq_models import TwoGram
from text_processing.freq_utils import tokenize_file, print_frequencies
from text_processing.freq_counter import compute_word_freq, compute_twogram_freq

__author__ = "Boaty McBoatface, Planey McPlaneface"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Boaty McBoatface", "Planey McPlaneface",
               "Donald J. Patterson", "Mike Ryu", ]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"

"""By default, expected output is printed to the console to help with debugging.
    Change this to `True` to not see the long output to console.
"""
__SUPPRESS_DEBUG_LINES__ = True


class ComputeWordFreqTest(unittest.TestCase):
    def setUp(self):
        cwd = os.path.dirname(__file__)
        data_format = "./data/{}_{:02d}.in.txt"
        self.sample_paths = [os.path.relpath(data_format.format("word", i), cwd) for i in range(0, 5)]

    def test_compute_word_freq_check_mutation(self):
        l_original = ["this", "should", "not", "be", "changed"]
        l_duplicate = ["this", "should", "not", "be", "changed"]
        l_reference = l_original

        compute_word_freq(l_original)
        self.assertEqual(l_original, l_duplicate)
        self.assertIs(l_original, l_reference)

    def test_compute_word_freq_none_and_empty(self):
        self.assertEqual([], compute_word_freq(None))
        self.assertEqual([], compute_word_freq([]))

    def test_compute_word_freq_example(self):
        expected_list = ["sentence:2", "repeats:1", "the:1", "this:1",  "word:1"]
        actual_list = compute_word_freq(["this", "sentence", "repeats", "the", "word", "sentence"])
        self.assertEqual(expected_list, list(map(str, actual_list)))

    def test_compute_word_freq_sample_04(self):
        with open(self.sample_paths[4], 'r') as fo:
            words = tokenize_file(fo)
            freqs = compute_word_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(265, len(actual_out_lines))

            # First few lines.
            self.assertEqual("   413 total items\n",  actual_out_lines[0])
            self.assertEqual("   262 unique items\n", actual_out_lines[1])
            self.assertEqual("\n",                    actual_out_lines[2])
            self.assertEqual("    26 the\n",          actual_out_lines[3])
            self.assertEqual("    13 a\n",            actual_out_lines[4])

            # Arbitrary sampling of the rest of the lines.
            self.assertEqual("     6 is\n",    actual_out_lines[10])
            self.assertEqual("     2 arepo\n", actual_out_lines[30])
            self.assertEqual("     1 4\n",     actual_out_lines[55])
            self.assertEqual("     1 drab\n",  actual_out_lines[100])
            self.assertEqual("     1 plan\n",  actual_out_lines[200])

            # The last few lines
            self.assertEqual("     1 ונשרף\n", actual_out_lines[-5])
            self.assertEqual("     1 נתבער\n", actual_out_lines[-4])
            self.assertEqual("     1 פרשנו\n", actual_out_lines[-3])
            self.assertEqual("     1 רעבתן\n", actual_out_lines[-2])
            self.assertEqual("     1 שבדבש\n", actual_out_lines[-1])


class ComputeTwoGramFreqTest(unittest.TestCase):
    def setUp(self):
        cwd = os.path.dirname(__file__)
        data_format = "./data/{}_{:02d}.in.txt"
        self.in_paths = [os.path.relpath(data_format.format("twogram", i), cwd) for i in range(0, 7)]

    def test_compute_twogram_freq_check_mutation(self):
        l_original = ["this", "should", "not", "be", "changed"]
        l_duplicate = ["this", "should", "not", "be", "changed"]
        l_reference = l_original

        compute_twogram_freq(l_original)
        self.assertEqual(l_duplicate, l_original)
        self.assertIs(l_reference, l_original)

    def test_compute_twogram_freq_01(self):
        with open(self.in_paths[1], 'r') as fo:
            words = tokenize_file(fo)
            freqs = compute_twogram_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            # Check the contents of `freq` directly.
            self.assertEqual(25, len(freqs))
            self.assertEqual(TwoGram("a", "b"), freqs[0].token)
            self.assertEqual(TwoGram("m", "n"), freqs[12].token)
            self.assertEqual(TwoGram("y", "z"), freqs[24].token)
            self.assertEqual(1, freqs[0].freq)
            self.assertEqual(1, freqs[12].freq)
            self.assertEqual(1, freqs[24].freq)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(28, len(actual_out_lines))

            # First few lines.
            self.assertEqual("    25 total items\n",  actual_out_lines[0])
            self.assertEqual("    25 unique items\n", actual_out_lines[1])
            self.assertEqual("\n",                    actual_out_lines[2])
            self.assertEqual("     1 <a:b>\n",        actual_out_lines[3])
            self.assertEqual("     1 <b:c>\n",        actual_out_lines[4])

    def test_compute_twogram_freq_02(self):
        with open(self.in_paths[2], 'r') as fo:
            words = tokenize_file(fo)
            freqs = compute_twogram_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            # Check the contents of `freq` directly.
            self.assertEqual(25, len(freqs))
            self.assertEqual(TwoGram("aa", "bb"), freqs[0].token)
            self.assertEqual(TwoGram("mm", "nn"), freqs[12].token)
            self.assertEqual(TwoGram("yy", "zz"), freqs[24].token)
            self.assertEqual(1, freqs[7].freq)
            self.assertEqual(1, freqs[12].freq)
            self.assertEqual(1, freqs[24].freq)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(28, len(actual_out_lines))

            # First few lines.
            self.assertEqual("    25 total items\n", actual_out_lines[0])
            self.assertEqual("    25 unique items\n", actual_out_lines[1])
            self.assertEqual("\n", actual_out_lines[2])
            self.assertEqual("     1 <aa:bb>\n", actual_out_lines[3])
            self.assertEqual("     1 <bb:cc>\n", actual_out_lines[4])

    def test_compute_twogram_freq_03(self):
        with open(self.in_paths[3], 'r') as fo:
            words = tokenize_file(fo)
            freqs = compute_twogram_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            # Check the contents of `freq` directly.
            self.assertEqual(248, len(freqs))
            self.assertEqual(TwoGram("can", "not"), freqs[0].token)
            self.assertEqual(TwoGram("shall", "not"), freqs[12].token)
            self.assertEqual(TwoGram("years", "ago"), freqs[247].token)
            self.assertEqual(3, freqs[0].freq)
            self.assertEqual(2, freqs[12].freq)
            self.assertEqual(1, freqs[247].freq)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(251, len(actual_out_lines))

            # First few lines.
            self.assertEqual("   271 total items\n", actual_out_lines[0])
            self.assertEqual("   248 unique items\n", actual_out_lines[1])
            self.assertEqual("\n", actual_out_lines[2])
            self.assertEqual("     3 <can:not>\n", actual_out_lines[3])
            self.assertEqual("     3 <it:is>\n", actual_out_lines[4])

    def test_compute_twogram_freq_04(self):
        with open(self.in_paths[4], 'r') as fo:
            words = tokenize_file(fo)
            freqs = compute_twogram_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            # Check the contents of `freq` directly.
            self.assertEqual(43, len(freqs))
            self.assertEqual(TwoGram("0", "1"), freqs[0].token)
            self.assertEqual(TwoGram("but", "if"), freqs[12].token)
            self.assertEqual(TwoGram("testing", "whether"), freqs[33].token)
            self.assertEqual(1, freqs[0].freq)
            self.assertEqual(1, freqs[12].freq)
            self.assertEqual(1, freqs[33].freq)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(46, len(actual_out_lines))

            # First few lines.
            self.assertEqual("    43 total items\n", actual_out_lines[0])
            self.assertEqual("    43 unique items\n", actual_out_lines[1])
            self.assertEqual("\n", actual_out_lines[2])
            self.assertEqual("     1 <0:1>\n", actual_out_lines[3])
            self.assertEqual("     1 <1:2>\n", actual_out_lines[4])

    def test_compute_twogram_freq_05(self):
        with open(self.in_paths[5], 'r') as fo:
            words = tokenize_file(fo)
            freqs = compute_twogram_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            # Check the contents of `freq` directly.
            self.assertEqual(19, len(freqs))
            self.assertEqual(TwoGram("a", "m"), freqs[0].token)
            self.assertEqual(TwoGram("o", "dcbabcd"), freqs[12].token)
            self.assertEqual(TwoGram("u", "edcbaabcde"), freqs[18].token)
            self.assertEqual(1, freqs[0].freq)
            self.assertEqual(1, freqs[12].freq)
            self.assertEqual(1, freqs[18].freq)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(22, len(actual_out_lines))

            # First few lines.
            self.assertEqual("    19 total items\n", actual_out_lines[0])
            self.assertEqual("    19 unique items\n", actual_out_lines[1])
            self.assertEqual("\n", actual_out_lines[2])
            self.assertEqual("     1 <a:m>\n", actual_out_lines[3])
            self.assertEqual("     1 <aa:r>\n", actual_out_lines[4])

    def test_compute_twogram_freq_06(self):
        with open(self.in_paths[6], 'r', encoding="UTF-8") as fo:
            words = tokenize_file(fo)
            freqs = compute_twogram_freq(words)
            actual_out_stream = io.StringIO()
            print_frequencies(freqs, actual_out_stream)

            # Print out `freq` to help with debugging.
            if not __SUPPRESS_DEBUG_LINES__:
                print_frequencies(freqs, sys.stdout)

            # Check the contents of `freq` directly.
            self.assertEqual(1416, len(freqs))
            self.assertEqual(TwoGram("à", "à"), freqs[0].token)
            self.assertEqual(TwoGram("in", "arabic"), freqs[12].token)
            self.assertEqual(TwoGram("word", "and"), freqs[1320].token)
            self.assertEqual(86, freqs[0].freq)
            self.assertEqual(5,  freqs[12].freq)
            self.assertEqual(1,  freqs[1320].freq)

            actual_out_stream.seek(0)
            actual_out_lines = actual_out_stream.readlines()

            # Number of lines returned.
            self.assertEqual(1419, len(actual_out_lines))

            # First few lines.
            self.assertEqual("  1830 total items\n", actual_out_lines[0])
            self.assertEqual("  1416 unique items\n", actual_out_lines[1])
            self.assertEqual("\n", actual_out_lines[2])
            self.assertEqual("    86 <à:à>\n", actual_out_lines[3])
            self.assertEqual("    37 <à:¾à>\n", actual_out_lines[4])

            # Arbitrary sampling of the rest of the lines.
            self.assertEqual("     2 <t:h>\n", actual_out_lines[123])
            self.assertEqual("     1 <content2:7>\n", actual_out_lines[456])
            self.assertEqual("     1 <lived:as>\n", actual_out_lines[789])
            self.assertEqual("     1 <redirects:here>\n", actual_out_lines[1011])
            self.assertEqual("     1 <to:mawaddatuhu>\n", actual_out_lines[1223])

            # The last few lines
            self.assertEqual("     1 <ùˆù:ùˆù>\n", actual_out_lines[-5])
            self.assertEqual("     1 <ÿà:à>\n", actual_out_lines[-4])
            self.assertEqual("     1 <žà:¾à>\n", actual_out_lines[-3])
            self.assertEqual("     1 <žà:à>\n", actual_out_lines[-2])
            self.assertEqual("     1 <ˆà:à>\n", actual_out_lines[-1])


if __name__ == '__main__':
    unittest.main()
