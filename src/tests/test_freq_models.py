"""Unit tests for classes, methods, and a function in `text_processing.freq_models`.
"""

import unittest
from text_processing.freq_models import Pair, TwoGram, Frequency

__author__ = "Boaty McBoatface, Planey McPlaneface"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Boaty McBoatface", "Planey McPlaneface",
               "Donald J. Patterson", "Mike Ryu", ]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"


class PairTest(unittest.TestCase):
    def setUp(self):
        self.p1 = Pair("hi", "hello")
        self.p2 = Pair("hi", "hello")
        self.p3 = Pair("hello", "hi")
        self.p4 = Pair(None, "something")
        self.p5 = Pair("something", None)
        self.p6 = Pair(None, None)
        self.p7 = Pair(1, "one")

    def test_constructor(self):
        self.assertEqual("hi",    self.p1.object1)
        self.assertEqual("hello", self.p1.object2)

    def test_getters_setters(self):
        p = Pair("original", "content")
        p.object1 = "changed"
        self.assertEqual("changed", p.object1)
        self.assertEqual("content", p.object2)

        p.object2 = "objects"
        self.assertEqual("objects", p.object2)
        self.assertEqual("changed", p.object1)

    def test_eq_1_self_and_none(self):
        self.assertEqual(self.p1, self.p1)
        self.assertEqual(self.p4, self.p4)
        self.assertEqual(self.p5, self.p5)
        self.assertEqual(self.p6, self.p6)
        self.assertNotEqual(None, self.p1)

    def test_eq_2_same_types(self):
        self.assertEqual(self.p1, self.p2)
        self.assertNotEqual(self.p1, self.p3)

    def test_eq_3_diff_types(self):
        self.assertNotEqual(self.p1, self.p4)
        self.assertNotEqual(self.p3, self.p5)
        self.assertNotEqual(self.p1, self.p7)

    def test_str(self):
        self.assertEqual("<hi:hello>",       str(self.p1))
        self.assertEqual("<something:None>", str(self.p5))
        self.assertEqual("<None:None>",      str(self.p6))
        self.assertEqual("<1:one>",          str(self.p7))

    def test_hash(self):
        self.assertEqual(hash(self.p1), hash(self.p1))
        self.assertEqual(hash(self.p1), hash(self.p2))
        self.assertNotEqual(hash(self.p2), hash(self.p3))


class TwoGramTest(unittest.TestCase):
    def setUp(self):
        self.tg1 = TwoGram("hi", "hello")
        self.tg2 = TwoGram("hello", "hi")
        self.tg3 = TwoGram("hello", "hi")
        self.tg4 = TwoGram(None, None)

        self.tg_top = TwoGram(None, None)
        self.tg_1st = TwoGram(None, 1)
        self.tg_2nd = TwoGram(None, 2)
        self.tg_3rd = TwoGram(1, None)
        self.tg_4th = TwoGram(1, 1)
        self.tg_5th = TwoGram(1, 2)
        self.tg_6th = TwoGram(2, 1)
        self.tg_6th_tied = TwoGram(2, 1)

    def test_constructor(self):
        self.assertEqual("hi",    self.tg1.object1)
        self.assertEqual("hello", self.tg1.object2)

        with self.assertRaises(ValueError):
            TwoGram(1, "one")

        try:
            TwoGram("one", "")
        except ValueError:
            self.fail()

        try:
            TwoGram("one", None)
        except ValueError:
            self.fail()

    def test_getters_setters(self):
        tg = TwoGram("something", "original")

        with self.assertRaises(ValueError):
            tg.object1 = 1

        with self.assertRaises(ValueError):
            tg.object2 = 2

        try:
            tg.object1 = "something else"
            self.assertEqual("something else", tg.object1)
            self.assertEqual("original",       tg.object2)

            tg.object2 = "brand new"
            self.assertEqual("brand new",      tg.object2)
            self.assertEqual("something else", tg.object1)

            tg.object1 = None
            self.assertEqual(None,        tg.object1)
            self.assertEqual("brand new", tg.object2)

            tg.object2 = None
            self.assertEqual(None, tg.object2)

        except ValueError:
            self.fail()

    def test_eq_1_self_and_none(self):
        self.assertEqual(self.tg1, self.tg1)
        self.assertEqual(self.tg4, self.tg4)
        self.assertNotEqual(self.tg1, None)

    def test_eq_2_same_tokens(self):
        self.assertEqual(self.tg2, self.tg3)

    def test_eq_3_diff_tokens(self):
        self.assertNotEqual(self.tg1, self.tg2)

    def test_lt(self):
        self.assertTrue(None < self.tg_1st)
        self.assertTrue(self.tg_top < self.tg_1st)
        self.assertTrue(self.tg_1st < self.tg_2nd)
        self.assertTrue(self.tg_2nd < self.tg_3rd)
        self.assertTrue(self.tg_3rd < self.tg_4th)
        self.assertTrue(self.tg_4th < self.tg_5th)
        self.assertTrue(self.tg_5th < self.tg_6th)

    def test_le(self):
        self.assertTrue(None <= self.tg_1st)
        self.assertTrue(self.tg_top <= self.tg_1st)
        self.assertTrue(self.tg_1st <= self.tg_2nd)
        self.assertTrue(self.tg_2nd <= self.tg_3rd)
        self.assertTrue(self.tg_3rd <= self.tg_4th)
        self.assertTrue(self.tg_4th <= self.tg_5th)
        self.assertTrue(self.tg_5th <= self.tg_6th)
        self.assertTrue(self.tg_6th <= self.tg_6th_tied)

    def test_gt(self):
        self.assertTrue(self.tg_top > None)
        self.assertTrue(self.tg_1st > self.tg_top)
        self.assertTrue(self.tg_2nd > self.tg_1st)
        self.assertTrue(self.tg_3rd > self.tg_2nd)
        self.assertTrue(self.tg_4th > self.tg_3rd)
        self.assertTrue(self.tg_5th > self.tg_4th)
        self.assertTrue(self.tg_6th > self.tg_5th)

    def test_ge(self):
        self.assertTrue(self.tg_top >= None)
        self.assertTrue(self.tg_1st >= self.tg_top)
        self.assertTrue(self.tg_2nd >= self.tg_1st)
        self.assertTrue(self.tg_3rd >= self.tg_2nd)
        self.assertTrue(self.tg_4th >= self.tg_3rd)
        self.assertTrue(self.tg_5th >= self.tg_4th)
        self.assertTrue(self.tg_6th >= self.tg_5th)
        self.assertTrue(self.tg_6th >= self.tg_6th_tied)


class FrequencyTest(unittest.TestCase):
    def setUp(self):
        word = "word"
        self.tg = TwoGram("two", "words")
        self.f1 = Frequency(word)
        self.f2 = Frequency(self.tg)
        self.f3 = Frequency(word)
        self.f4 = Frequency(self.tg)

        self.f_1st = Frequency(self.tg, 6)
        self.f_2nd = Frequency(self.tg, 5)
        self.f_3rd = Frequency(self.tg, 4)
        self.f_4th = Frequency(word, 3)
        self.f_5th = Frequency(word, 2)
        self.f_6th = Frequency(word, 1)
        self.f_6th_tied = Frequency(word, 1)

    def test_constructor(self):
        with self.assertRaises(ValueError):
            Frequency(None)

        with self.assertRaises(ValueError):
            Frequency(1)

        try:
            self.assertEqual("word",   self.f1.token)
            self.assertEqual(0,        self.f1.freq)
            self.assertEqual(self.tg,  self.f2.token)
            self.assertEqual(0,        self.f2.freq)
        except ValueError:
            self.fail()

    def test_eq_1_self_and_none(self):
        self.assertEqual(self.f1, self.f1)
        self.assertEqual(self.f2, self.f2)
        self.assertNotEqual(None, self.f1)
        self.assertNotEqual(None, self.f2)

    def test_eq_2_same_attrs(self):
        self.assertEqual(self.f3, self.f1)
        self.assertEqual(self.f4, self.f4)

    def test_eq_3_diff_attrs(self):
        self.assertNotEqual(self.f1, self.f2)
        self.assertNotEqual(self.f_1st, self.f_2nd)

    def test_lt(self):
        self.assertTrue(None < self.f_1st)
        self.assertTrue(self.f_1st < self.f_2nd)
        self.assertTrue(self.f_2nd < self.f_3rd)
        self.assertTrue(self.f_3rd < self.f_4th)
        self.assertTrue(self.f_4th < self.f_5th)
        self.assertTrue(self.f_5th < self.f_6th)

    def test_le(self):
        self.assertTrue(None <= self.f_1st)
        self.assertTrue(self.f_1st <= self.f_2nd)
        self.assertTrue(self.f_2nd <= self.f_3rd)
        self.assertTrue(self.f_3rd <= self.f_4th)
        self.assertTrue(self.f_4th <= self.f_5th)
        self.assertTrue(self.f_5th <= self.f_6th)
        self.assertTrue(self.f_6th <= self.f_6th_tied)

    def test_gt(self):
        self.assertTrue(self.f_1st > None)
        self.assertTrue(self.f_2nd > self.f_1st)
        self.assertTrue(self.f_3rd > self.f_2nd)
        self.assertTrue(self.f_4th > self.f_3rd)
        self.assertTrue(self.f_5th > self.f_4th)
        self.assertTrue(self.f_6th > self.f_5th)

    def test_ge(self):
        self.assertTrue(self.f_1st >= None)
        self.assertTrue(self.f_2nd >= self.f_1st)
        self.assertTrue(self.f_3rd >= self.f_2nd)
        self.assertTrue(self.f_4th >= self.f_3rd)
        self.assertTrue(self.f_5th >= self.f_4th)
        self.assertTrue(self.f_6th >= self.f_5th)
        self.assertTrue(self.f_6th >= self.f_6th_tied)

    def test_str(self):
        self.assertEqual("<two:words>:4", str(self.f_3rd))
        self.assertEqual("word:3",        str(self.f_4th))

    def test_hash(self):
        self.assertEqual(hash(self.f1), hash(self.f1))
        self.assertEqual(hash(self.f1), hash(self.f3))
        self.assertNotEqual(hash(self.f1), hash(self.f2))

    def test_word_token_comparison(self):
        t1 = Frequency("a", 1)
        t2 = Frequency("b", 1)
        self.assertTrue(t1 < t2)
        self.assertTrue(t1 <= t2)
        self.assertTrue(t2 > t1)
        self.assertTrue(t2 >= t1)
        self.assertTrue(t2 != t1)


if __name__ == '__main__':
    unittest.main()
