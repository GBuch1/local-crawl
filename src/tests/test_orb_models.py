"""Unit tests for functions in `spider.orb.orb_models`.
"""

import os
import unittest
from spider.orb.orb_models import *

__author__ = "Mike Ryu"
__copyright__ = "Copyright 2023, Mike Ryu"
__credits__ = ["Mike Ryu"]
__license__ = "MIT"
__email__ = "dongyub.ryu@gmail.com"


class OrbAgentTest(unittest.TestCase):
    def setUp(self):
        cwd = os.path.dirname(__file__)
        host_path = "./data"
        page_path = host_path + "/spider.orb_{:02d}.in.html"

        num_samples = 5
        sample_paths = [os.path.relpath(page_path.format(i), cwd) for i in range(num_samples)]

        self.host = os.path.relpath(host_path, cwd)
        self.uris = [OrbURI(sample_paths[i], dict()) for i in range(num_samples)]

        self.dummy_doc_db = OrbDocDB()
        self.dummy_uri_db = OrbUriDB()

        self.base_config = {
            "external": ["https://", "http://"],
            "encoding": "UTF-8",
            "parser": "html.parser",
            "debug": True
        }

    def test_crawl_io_error(self):
        config = dict(self.base_config)
        config["tags"] = {"p": {}}
        agent = OrbAgent(OrbURI("bad_uri.html (THIS ERROR MSG IS EXPECTED)"),
                         self.dummy_doc_db, self.dummy_uri_db, config)

        try:
            content, link = agent.crawl()
            self.assertEqual(0, len(list(content)))
            self.assertEqual(0, len(list(link)))
        except OSError as e:
            self.fail(f"OSError raised: {str(e)}")

    def test_crawl_0_empty_case(self):
        config = dict(self.base_config)
        config["tags"] = {"p": {}}
        agent = OrbAgent(self.uris[0], self.dummy_doc_db, self.dummy_uri_db, config)
        content, link = agent.crawl()

        with self.assertRaises(StopIteration):
            next_content = next(content)
            print(f"[{next_content}]")

        with self.assertRaises(StopIteration):
            next(link)

    def test_crawl_1_simple_case_content_only(self):
        config = dict(self.base_config)
        config["tags"] = {"h1": {}, "p": {}}
        agent = OrbAgent(self.uris[1], self.dummy_doc_db, self.dummy_uri_db, config)
        content, link = agent.crawl()

        try:
            self.assertEqual("Top-level Heading Paragraph content!", next(content).content)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(link)

    def test_crawl_2_simple_case_content_and_link(self):
        config = dict(self.base_config)
        config["tags"] = {"h2": {}, "p": {}}
        agent = OrbAgent(self.uris[2], self.dummy_doc_db, self.dummy_uri_db, config)
        content, link = agent.crawl()

        try:
            self.assertEqual("Subheading HTML links are defined with the <a> tag:", next(content).content)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(content)

        try:
            self.assertEqual("https://www.mikeryu.com", next(link).uri)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(link)

    def test_crawl_3_simple_case_content_and_links(self):
        config = dict(self.base_config)
        config["tags"] = {"p": {}}
        agent = OrbAgent(self.uris[3], self.dummy_doc_db, self.dummy_uri_db, config)
        content, link = agent.crawl()

        try:
            content_text = next(content).content
            self.assertTrue("Four score and seven years ago our fathers brought" in content_text)
            self.assertTrue("all men are created equal. Now we are engaged in a great civil war" in content_text)
            self.assertTrue("   The brave men, living and dead, who struggled here, have consecrated" in content_text)
            self.assertTrue("for the people, shall not perish from the earth" in content_text)
            self.assertFalse("Go to 01" in content_text)
            self.assertFalse("Go to 02" in content_text)
            self.assertFalse("Visit Mike's site!" in content_text)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(content)

        try:
            all_links = [_.uri for _ in link]
            self.assertTrue(f"{self.host}/spider.orb_01.in.html" in all_links)
            self.assertTrue(f"{self.host}/spider.orb_02.in.html" in all_links)
            self.assertTrue("https://www.mikeryu.com" in all_links)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(link)

    def test_crawl_4_realistic_case(self):
        config = dict(self.base_config)
        config["tags"] = {"dd": {}}
        agent = OrbAgent(self.uris[4], self.dummy_doc_db, self.dummy_uri_db, config)
        content, link = agent.crawl()

        try:
            content_text = next(content).content
            self.assertTrue("Then went Samson to Gaza, and saw there an harlot, and went in unto her." in content_text)
            self.assertTrue("Samson is come hither. And they compassed him in, and laid wait" in content_text)
            self.assertTrue("took hold of the two middle pillars upon which the" in content_text)
            self.assertTrue("And he said unto her, If they bind me fast" in content_text)
            self.assertFalse("Judges 15" in content_text)
            self.assertFalse("Index" in content_text)
            self.assertFalse("Judges 17" in content_text)
            self.assertFalse("Download Free Bible" in content_text)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(content)

        try:
            all_links = [_.uri for _ in link]
            self.assertTrue(f"{self.host}/index.htm" in all_links)
            self.assertTrue(f"{self.host}/07015.htm" in all_links)
            self.assertTrue(f"{self.host}/07017.htm" in all_links)
            self.assertTrue("http://www.truth.info/download/bible.htm" in all_links)
        except StopIteration:
            self.fail()

        with self.assertRaises(StopIteration):
            next(link)

    def test_crawl_5_handle_duplicates_with_dbs(self):
        config = dict(self.base_config)
        config["tags"] = {"dd": {}}
        docs, links = OrbAgent(self.uris[4], self.dummy_doc_db, self.dummy_uri_db, config).crawl()

        _ = [doc for doc in docs]
        _ = [uri for uri in links]

        agent = OrbAgent(self.uris[4], self.dummy_doc_db, self.dummy_uri_db, config)
        docs, links = agent.crawl()

        with self.assertRaises(StopIteration):
            next(docs)

        with self.assertRaises(StopIteration):
            next(links)


class OrbUriFrontierTest(unittest.TestCase):
    def setUp(self):
        cwd = os.path.dirname(__file__)
        num_samples = 5

        sample_paths = [os.path.relpath("./data/spider.orb_{:02d}.in.html".format(i), cwd) for i in range(num_samples)]
        self.uris = [OrbURI(sample_paths[i], dict()) for i in range(num_samples)]

    def test_constructor_bool_and_len(self):
        with self.assertRaises(ValueError):
            OrbUriFrontier(list())

        frontier = OrbUriFrontier(self.uris)
        self.assertTrue(frontier)
        self.assertEqual(5, len(frontier))
        self.assertEqual(self.uris[0], frontier.peek())

    def test_str(self):
        frontier = OrbUriFrontier(self.uris)
        self.assertTrue(frontier)
        self.assertEqual(
            "Size: {:d}\nNext: {}".format(5, self.uris[0]),
            str(frontier)
        )

    def test_push_peek_and_pop(self):
        frontier = OrbUriFrontier(self.uris[:1])
        self.assertEqual(self.uris[0], frontier.peek())

        frontier.pop()
        self.assertFalse(bool(frontier))
        self.assertEqual(0, len(frontier))

        for i in range(len(self.uris)):
            frontier.push(self.uris[i])
            self.assertTrue(bool(frontier))
            self.assertEqual(i + 1, len(frontier))
            self.assertEqual(self.uris[0], frontier.peek())

        init_len = len(frontier)
        for j in range(init_len):
            self.assertEqual(self.uris[j], frontier.peek())
            self.assertEqual(self.uris[j], frontier.pop())
            self.assertEqual(init_len - j - 1, len(frontier))

        self.assertFalse(frontier)
