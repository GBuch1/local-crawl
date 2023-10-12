"""Unit tests for functions in `spider.spider_models`.
"""

import unittest
from parameterized import parameterized_class
from spider.orb.orb_models import *

__author__ = "Mike Ryu"
__copyright__ = "Copyright 2023, Mike Ryu"
__credits__ = ["Mike Ryu"]
__license__ = "MIT"
__email__ = "dongyub.ryu@gmail.com"


@parameterized_class([
    {"SpiderImplDocFP": OrbDocFP}
])
class SpiderImplDocFPTest(unittest.TestCase):
    SpiderImplDocFP = None

    def setUp(self):
        self.content1 = "This is my document content."
        self.content2 = "This is a different document."

    def test_eq(self):
        fp1 = self.SpiderImplDocFP(self.content1)
        fp2 = self.SpiderImplDocFP(self.content2)
        fp1_dup = OrbDocFP(self.content1)
        self.assertNotEqual(fp1, None)
        self.assertNotEqual(fp1, fp2)
        self.assertEqual(fp1, fp1)
        self.assertEqual(fp1, fp1_dup)

    def test_str(self):
        fp = self.SpiderImplDocFP(self.content1)
        self.assertIsNotNone(str(fp))


@parameterized_class([
    {"SpiderDocImpl": OrbDoc}
])
class SpiderImplDocTest(unittest.TestCase):
    SpiderDocImpl = None

    def setUp(self):
        self.content1 = "This is my document content."
        self.content2 = "This is a different document."
        self.doc1 = self.SpiderDocImpl(self.content1)
        self.doc2 = self.SpiderDocImpl(self.content2, "some title")

    def test_constructor_and_simple_getters(self):
        self.assertTrue(self.doc1.iid > 0)
        self.assertEqual(self.doc1.iid + 1, self.doc2.iid)

        self.assertIsNone(self.doc1.title)
        self.assertEqual("some title", self.doc2.title)

        self.assertEqual(self.content1, self.doc1.content)
        self.assertEqual(self.content2, self.doc2.content)

    def test_get_fingerprint(self):
        self.assertIsNone(self.doc1._fingerprint)
        self.assertIsNone(self.doc2._fingerprint)

        self.assertIsNotNone(self.doc1.fingerprint)
        self.assertIsNotNone(self.doc2.fingerprint)

        self.assertIsNotNone(self.doc1._fingerprint)
        self.assertIsNotNone(self.doc2._fingerprint)

    def test_eq(self):
        doc1_dup = self.SpiderDocImpl(self.doc1.content, self.doc1.title)
        doc2_dup = self.SpiderDocImpl(self.doc2.content, self.doc2.title)

        self.assertNotEqual(self.doc1, None)
        self.assertNotEqual(self.doc1, self.doc2)

        self.assertEqual(self.doc1, doc1_dup, msg="{} != {}".format(self.doc1, doc1_dup))
        self.assertEqual(self.doc2, doc2_dup, msg="{} != {}".format(self.doc2, doc2_dup))


@parameterized_class([
    {
        "SpiderImplUri": OrbURI,
        "SpiderImplUriTypeStr": "<class 'spider.orb.orb_models.OrbURI'>"
    }
])
class SpiderImplUriTest(unittest.TestCase):
    SpiderImplUri = None
    SpiderImplUriTypeStr = ""

    def setUp(self):
        self.fake_uri = "https://fake-uri.com/some/page/that/is/fake"
        self.fake_props = {"fake_int_prop": 1, "fake_bool_prop": False, "fake_str_prop": "boo"}
        self.uri = self.SpiderImplUri(self.fake_uri, self.fake_props)

    def test_constructor_and_getters(self):
        self.assertGreater(self.uri.iid, 0)
        self.assertEqual(self.fake_uri, self.uri.uri)
        self.assertEqual(self.fake_props, self.uri.props)

    def test_hash(self):
        self.assertIsNotNone(hash(self.uri))

    def test_eq(self):
        self.assertNotEqual(self.uri, None)
        self.assertNotEqual(self.uri, self.SpiderImplUri(None, None))
        self.assertNotEqual(self.uri, self.SpiderImplUri("", self.fake_props))

        self.assertEqual(self.uri, self.uri)
        self.assertEqual(self.uri, self.SpiderImplUri(self.fake_uri, None))
        self.assertEqual(self.uri, self.SpiderImplUri(self.fake_uri, self.fake_props))

    def test_str(self):
        self.assertEqual(
            f"[{self.uri.iid:09d}]: ...me/page/that/is/fake {self.SpiderImplUriTypeStr}",
            str(self.uri)
        )


@parameterized_class([
    {
        "SpiderImplURI": OrbURI,
        "SpiderImplAgent": OrbAgent,
        "SpiderImplAgentTypeStr": "<class 'spider.orb.orb_models.OrbAgent'>"
     }
])
class SpiderImplAgentTest(unittest.TestCase):
    SpiderImplURI = None
    SpiderImplAgent = None
    SpiderImplAgentTypeStr = ""

    def setUp(self):
        self.fake_uri = "https://fake-uri.com/some/page/that/is/fake"
        self.fake_doc_db = OrbDocDB()
        self.fake_uri_db = OrbUriDB()
        self.fake_props = {"fake_int_prop": 1, "fake_bool_prop": False, "fake_str_prop": "boo"}
        self.fake_config = {"fake_config": "This is completely fake for testing only."}
        self.uri = self.SpiderImplURI(self.fake_uri, self.fake_props)
        self.agent = self.SpiderImplAgent(self.uri, self.fake_doc_db, self.fake_uri_db, self.fake_config)

    def test_constructor_and_getters(self):
        agent_iid = self.agent.iid
        self.assertGreater(agent_iid, 0)
        self.assertEqual(self.uri, self.agent.uri)
        self.assertEqual(self.fake_doc_db, self.agent.doc_db)
        self.assertEqual(self.fake_uri_db, self.agent.uri_db)
        self.assertEqual(self.fake_config, self.agent.config)

        another_agent = self.SpiderImplAgent(self.uri, self.fake_doc_db, self.fake_uri_db, self.fake_config)
        self.assertEqual(agent_iid + 1, another_agent.iid)

    def test_str(self):
        self.assertEqual(
            f"[{self.agent.iid:09d}]: https://fake-uri.com ... {self.SpiderImplAgentTypeStr}",
            str(self.agent)
        )


@parameterized_class([
    {
        "SpiderImplDocDB": OrbDocDB,
        "SpiderImplDocFP": OrbDocFP
    }
])
class SpiderImplDocDBTest(unittest.TestCase):
    SpiderImplDocDB = None
    SpiderImplDocFP = None

    def setUp(self):
        content1 = "This is my document content."
        content2 = "This is a different document."
        self.doc_fp1 = self.SpiderImplDocFP(content1)
        self.doc_fp2 = self.SpiderImplDocFP(content2)

    def test_constructor(self):
        db = self.SpiderImplDocDB()
        self.assertIsNotNone(db)
        self.assertFalse(db)
        self.assertEqual(0, len(db))

    def test_add_check_remove(self):
        db = self.SpiderImplDocDB()

        self.assertFalse(self.doc_fp1 in db)
        self.assertFalse(self.doc_fp2 in db)

        self.assertFalse(db.remove(self.doc_fp1))
        self.assertFalse(db.remove(self.doc_fp2))
        self.assertEqual(0, len(db))

        self.assertTrue(db.add(self.doc_fp1))
        self.assertTrue(self.doc_fp1 in db)
        self.assertEqual(1, len(db))
        self.assertTrue(db)

        self.assertTrue(db.add(self.doc_fp2))
        self.assertTrue(self.doc_fp2 in db)
        self.assertEqual(2, len(db))
        self.assertTrue(db)

        self.assertFalse(db.add(self.doc_fp1))
        self.assertFalse(db.add(self.doc_fp2))

        self.assertTrue(db.remove(self.doc_fp1))
        self.assertFalse(self.doc_fp1 in db)
        self.assertEqual(1, len(db))
        self.assertTrue(db)

        self.assertTrue(db.remove(self.doc_fp2))
        self.assertFalse(self.doc_fp2 in db)
        self.assertEqual(0, len(db))
        self.assertFalse(db)


@parameterized_class([
    {
        "SpiderImplUri": OrbURI,
        "SpiderImplUriDB": OrbUriDB
    }
])
class SpiderImplUriDBTest(unittest.TestCase):
    SpiderImplUri = None
    SpiderImplUriDB = None

    def setUp(self):
        self.uri1 = self.SpiderImplUri("https://www.westmont.edu/")
        self.uri2 = self.SpiderImplUri("https://www.mikeryu.com/")

    def test_constructor(self):
        db = self.SpiderImplUriDB()
        self.assertIsNotNone(db)
        self.assertFalse(db)
        self.assertEqual(0, len(db))

    def test_add_check_remove(self):
        db = self.SpiderImplUriDB()

        self.assertFalse(self.uri1 in db)
        self.assertFalse(self.uri2 in db)

        self.assertFalse(db.remove(self.uri1))
        self.assertFalse(db.remove(self.uri2))
        self.assertEqual(0, len(db))

        self.assertTrue(db.add(self.uri1))
        self.assertTrue(self.uri1 in db)
        self.assertEqual(1, len(db))
        self.assertTrue(db)

        self.assertTrue(db.add(self.uri2))
        self.assertTrue(self.uri2 in db)
        self.assertEqual(2, len(db))
        self.assertTrue(db)

        self.assertFalse(db.add(self.uri1))
        self.assertFalse(db.add(self.uri2))

        self.assertTrue(db.remove(self.uri1))
        self.assertFalse(self.uri1 in db)
        self.assertEqual(1, len(db))
        self.assertTrue(db)

        self.assertTrue(db.remove(self.uri2))
        self.assertFalse(self.uri2 in db)
        self.assertEqual(0, len(db))
        self.assertFalse(db)
