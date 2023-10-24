"""Implementation of a local HTML directory crawler (i.e., does not send requests over the network).
"""

from __future__ import annotations
from sys import stderr
from bs4 import BeautifulSoup
from queue import SimpleQueue
from typing import TextIO
from spider.spider_models import *

__author__ = "Garrett Buchanan", "Livingstone Rwagatare"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Garrett Buchanan", "Livingstone Rwagatare", "Mike Ryu"]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"

from src.spider.spider_models import SpiderDB


class OrbDocFP(SpiderDocFP):
    """This class creates a fingerprint using the hash method. It also has equality and string methods.
       The eq method compares fingerprints and returns a boolean value of True or False. The str method
       returns the fingerprint as a string."""

    def __init__(self, doc_fp):
        self.doc_fp = doc_fp

    def __hash__(self):
        return hash(self.doc_fp)

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, OrbDocFP):
            return False
        else:
            return self.doc_fp == other.doc_fp

    def __str__(self) -> str:
        return f"{self.doc_fp}"


class OrbDoc(SpiderDoc):
    """ rrrr """

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, SpiderDoc) or self is None or not isinstance(other, SpiderDoc):
            return False
        else:
            return self.content == other.content and self.title == other.title

    def __hash__(self):
        return hash(self.content, self.title)

    def __str__(self) -> str:
        return f"{self.content}, {self.title}"

    def _compute_fingerprint(self) -> None:
        self._fingerprint = f"{self.content}{self.title}"


class OrbURI(SpiderURI):
    """Class that provides methods to deal with URIs. The eq method checks to see if one URI
       is equal to another URI. The hash method returns the hash value of the URI."""

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, OrbURI):
            return False
        else:
            return self._uri == other.uri

    def __hash__(self):
        return hash(self.uri)


class OrbContentProcessor(SpiderContentProcessor):
    """TODO: Implement this class and complete the class docstring.


    HINT:
        Lazily evaluate whether the content has been seen by checking if the document `__next__` method is about
        to return has its fingerprint already stored in `self._agent.doc_db`; skip any document that has its
        fingerprint already stored in the database, but add any new document's fingerprint to the database.

    """

    def __init__(self, agent: OrbAgent):
        super().__init__(agent)
        self._seen_docs = set()  # this set will track documents that have been seen.

    def process(self, soup: BeautifulSoup):
        doc = OrbDoc()
        doc._content = soup.get_text()  # extracts the text content of HTML
        doc._title = soup.title.string if soup.title else ""  # extracts the title of the document if present
        doc._compute_fingerprint()  # compute a unique fingerprint of the document

        if doc._fingerprint not in self._agent.doc_db:  # Checking if the document fingerprint is in the agent's doc_db
            self._agent.doc_db.add(doc._compute_fingerprint)  # if not seen before, add to the database.
            self._seen_docs.add(doc)  # add the set of seen documents


class OrbLinkProcessor(SpiderLinkProcessor):
    """TODO: Implement this class and complete the class docstring.

    HINT:
        Do the similar lazy evaluation as `OrbContentProcessor`, except for the URIs using `self._agent.uri_db`.

        Your implementation must include instantiating `OrbURI`'s with its `props` attribute set as:
            {"parent": self._agent.uri.uri}

    """

    def __init__(self, agent: OrbAgent):
        super().__init__(agent)
        self._seen_uris = set()  # set to track seen uris

    def process(self, link):
        uri = OrbURI(link.get('href'))
        uri._props = {"parent": self._agent.uri.uri}  # set the properties for the URI,specifically the parent link

        if uri not in self._agent.uri_db:  # check if the URI is in the agent's uri_db
            self._agent.uri_db.add(uri)  # if not seen before, add to the database
            self._seen_uris.add(uri)  # add to the set of seen URIs

    @staticmethod
    def is_link_external(agent: SpiderAgent, link: str) -> bool:
        """Determines if the given link is an external (web) link based on the definition of "external" tokens
        provided by the `agent`'s configuration (`agent.config`).

        Args:
            agent (SpiderAgent): a `SpiderAgent` to provide the configuration for the "external" tokens.
            link (str): actual link text to check.

        Returns:
            `True` if the link is determined to be an external link, `False` otherwise.
        """
        link_text_to_treat_as_external = agent.config["external"]
        is_external = False

        for txt in link_text_to_treat_as_external:
            if txt in link:
                is_external |= True

        return is_external


class OrbAgent(SpiderAgent):
    """TODO: Implement this class and complete the class docstring."""

    def crawl(self) -> (OrbContentProcessor, OrbLinkProcessor):
        openfile = self._open_uri_as_file()
        soup = BeautifulSoup(openfile, 'html.parser')
        for soup in soup.find_all('a'):
            soup.get_text()
        openfile.close()

    def _open_uri_as_file(self) -> TextIO | None:
        """If `self._uri.uri` is not an external link, opens the file specified by the URI and returns it.

        In case of a file operation error, this method simply returns `None` instead of raising an exception.
        If `_config` has a "debug" flag where it is set to `True`, the file operation error will be reported
        to `stderr`.

        Returns:
            The file object that was opened from the non-external URI (i.e., local file path) stored in
            `self._uri.uri` if the file opened successfully, otherwise `None`.
        """
        try:
            if not OrbLinkProcessor.is_link_external(self, self._uri.uri):
                return open(self._uri.uri, 'r', encoding=self._config["encoding"])
        except OSError as e:
            if self._config["debug"]:
                err_str = "Link from ...{} failed to open:\n".format(
                    self._uri.props['parent'][-40:] if self._uri.props else 'unknown'
                )
                print(err_str, e, file=stderr)
            return None


class OrbUriFrontier(SpiderUriFrontier):
    """URI Frontier implementation that utilizes Python's built-in `SimpleQueue`; `OrbUriFrontier` is a simple
    sequential FIFO queue that does not perform any prioritization or politeness enforcement.

    Notes:
        `SimpleQueue` does not support "peeking" due to thread-safety issues (which we are not concerned with).
        Therefore, we must manually manage the very front of the queue separately from to the rest of the queue
        backed by `SimpleQueue` in order to implement `peek`. In other words, `OrbUriFrontier`'s operations are
        actually backed by `SimpleQueue` plus a singular reference (`_next`) to the element at the very front of the
        queue -- which, when populated, is the element to be returned on the "next" call to `pop` or `peek`.

    Attributes:
        _q (SimpleQueue): actual queue that backs the operations of this URI Frontier.
        _next (OrbURI | None): `OrbURI` to be returned on the next call to `pop` or `peek`.

    """

    def __init__(self, seeds: list[OrbURI]) -> None:  # DO NOT MODIFY THIS CONSTRUCTOR!
        self._q: SimpleQueue = SimpleQueue()
        self._next: OrbURI | None = None
        super().__init__(seeds)

    def __len__(self):  # DO NOT MODIFY THIS DEFINITION!
        return self._q.qsize() + 1 if self._next else 0

    def __str__(self):  # DO NOT MODIFY THIS DEFINITION!
        return "Size: {:d}\nNext: {}".format(self.__len__(), self._next)


class OrbDB(SpiderDB):
    """TODO: Implement this class and complete the class docstring."""

    def __init__(self):
        self._DataBase = []

    def add(self, item):
        if item not in self._DataBase:
            self._DataBase.append(item)
            return True
        else:
            return False

    def __contains__(self, item):
        if item in self._DataBase:
            return True
        return False

    def __len__(self) -> int:
        """Returns the number of `SpiderArtifact`'s that are currently in the database."""
        return len(self._DataBase)

    def remove(self, item: SpiderArtifact) -> bool:
        """Attempts to remove the specified `SpiderArtifact` and returns `True` if the operation was successful,
        and `False` if the removal was unsuccessful and the given `SpiderArtifact` remains in the DB.

        """
        try:
            self._DataBase.remove(item)
        except:
            return False
        else:
            return True




class OrbDocDB(OrbDB, SpiderDocDB):
    """TODO: Depending on your implementation of OrbDB, this definition may not be needed."""
    pass


class OrbUriDB(OrbDB, SpiderUriDB):
    """TODO: Depending on your implementation of OrbDB, this definition may not be needed."""
    pass
