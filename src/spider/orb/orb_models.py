"""Implementation of a local HTML directory crawler (i.e., does not send requests over the network).
"""

from __future__ import annotations
from sys import stderr
from bs4 import BeautifulSoup
from queue import SimpleQueue
from typing import TextIO
from spider.spider_models import *

__author__ = "Boaty McBoatface, Planey McPlaneface"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Boaty McBoatface", "Planey McPlaneface", "Mike Ryu"]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"


class OrbDocFP(SpiderDocFP):
    """TODO: Implement this class and complete the class docstring."""

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
    """TODO: Implement this class and complete the class docstring."""

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
    """TODO: Implement this class and complete the class docstring."""

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, OrbURI):
            return False
        else:
            return self._uri == other.uri

    def __hash__(self):
        return hash((self.uri, self.uri))

class OrbContentProcessor(SpiderContentProcessor):
    """TODO: Implement this class and complete the class docstring.

    HINT:
        Lazily evaluate whether the content has been seen by checking if the document `__next__` method is about
        to return has its fingerprint already stored in `self._agent.doc_db`; skip any document that has its
        fingerprint already stored in the database, but add any new document's fingerprint to the database.

    """
    pass


class OrbLinkProcessor(SpiderLinkProcessor):
    """TODO: Implement this class and complete the class docstring.

    HINT:
        Do the similar lazy evaluation as `OrbContentProcessor`, except for the URIs using `self._agent.uri_db`.

        Your implementation must include instantiating `OrbURI`'s with its `props` attribute set as:
            {"parent": self._agent.uri.uri}

    """
    pass

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
        pass  # HINT: use `BeautifulSoup` in this method implementation.

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

    def __int__(self):
        self._database = []

    @abstractmethod
    def __len__(self) -> int:
        """Returns the number of `SpiderArtifact`'s that are currently in the database."""
        return len(self._database)
       #pass

    @abstractmethod
    def __contains__(self, item: SpiderArtifact) -> bool:
        """Returns `True` if the given `SpiderArtifact` is in the database, `False` otherwise."""
        return
        #pass

    @abstractmethod
    def add(self, item: SpiderArtifact) -> bool:
        """Attempts to add the given `SpiderArtifact` and returns `True` if the add operation was successful,
        and `False` if the operation was unsuccessful and the given `SpiderArtifact` was not added to the database.

        """

        #pass

    @abstractmethod
    def remove(self, item: SpiderArtifact) -> bool:
        """Attempts to remove the specified `SpiderArtifact` and returns `True` if the operation was successful,
        and `False` if the removal was unsuccessful and the given `SpiderArtifact` remains in the DB.

        """
        pass

    def add_all(self, *args):
        """Adds all `SpiderArtifact`'s passed in via `args` by invoking `self.add` on each `SpiderArtifact` instance.

        First instance in the `args` gets added first, and the last instance in the `args` gets added last.

        """
        for item in args:
            self.add(item)

    pass


class OrbDocDB(OrbDB, SpiderDocDB):
    """TODO: Depending on your implementation of OrbDB, this definition may not be needed."""
    pass


class OrbUriDB(OrbDB, SpiderUriDB):
    """TODO: Depending on your implementation of OrbDB, this definition may not be needed."""
    pass
