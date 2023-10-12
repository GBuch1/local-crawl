"""Abstract data models for web crawler ("Spider") components.
"""

from __future__ import annotations
from abc import ABC, abstractmethod

__author__ = "Mike Ryu"
__copyright__ = "Copyright 2023, Mike Ryu"
__credits__ = ["Mike Ryu"]
__license__ = "MIT"
__email__ = "dongyub.ryu@gmail.com"


TRUNCATION_THRESHOLD = 20  # Constant used for formatting __str__ outputs.


class SpiderArtifact(ABC):
    """Abstract superclass defined mostly for polymorphism in type hints.

    This class is a parent class for: `SpiderDocFP`, `SpiderDoc`, and `SpiderURI`.

    """
    @abstractmethod
    def __hash__(self):
        pass


class SpiderDocFP(SpiderArtifact):
    """Abstract data type for a document fingerprint used in a web crawler.

    At the very least, a document fingerprint must provide a `__hash__` method representing
    the fingerprint value itself, as well as an efficient equality comparison and a `str`
    representation for debugging purposes.

    """
    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


class SpiderDoc(SpiderArtifact):
    """Abstract data type for a full document yielded as a result of a crawler parsing a web page.

    Notes:
        The `_fingerprint` attribute is computed "lazily," meaning that it has `None` as its value
        until its getter method is invoked (which, in turn, should compute the fingerprint on the spot).
        After the first invocation of the getter (`SpiderDoc.fingerprint`), the `_fingerprint` attribute
        should have a non-`None` value.

        A `SpiderDoc` is considered equal to another `SpiderDoc` if their `_fingerprint` attributes are the same.

    Attributes:
        _iid (int): instance ID (automatically increments per instantiation).
        _title (str): optional title for the document for easy identification by humans.
        _content (str): the actual document content; expected to be plain text.
        _fingerprint (SpiderDOcFP): lazily computed document fingerprint.

    """
    _iid = 0

    def __init__(self, content: str, title: str = None) -> None:
        SpiderDoc._iid += 1
        self._iid: int = SpiderDoc._iid
        self._title: str | None = title
        self._content: str = content
        self._fingerprint: SpiderDocFP | None = None

    def __hash__(self) -> int:
        return hash(self.fingerprint)

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, SpiderDoc):
            return False
        else:
            return self._fingerprint == other.fingerprint

    def __str__(self) -> str:
        is_truncate = len(self._content) >= TRUNCATION_THRESHOLD
        return "[{hash:20d}]: {content}{ellipses} {type}".format(
            hash=self.__hash__(),
            content=self._content[:TRUNCATION_THRESHOLD if is_truncate else len(self._content)],
            ellipses="..." if is_truncate else "    ",
            type=type(self)
        )

    @property
    def iid(self) -> int:
        return self._iid

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

    @property
    def fingerprint(self) -> SpiderDocFP:
        if not self._fingerprint:
            self._compute_fingerprint()
        return self._fingerprint

    @abstractmethod
    def _compute_fingerprint(self) -> None:
        pass


class SpiderURI(SpiderArtifact):
    """Abstract data type for a Universal Resource Identifier (URI) used by a web crawler to fetch a web page.

    Notes:
        Two `SpiderURI`'s are considered equal if they have the exact same `_uri` attributes.

    Attributes:
        _iid (int): instance ID (automatically increments per instantiation).
        _uri (str): actual URI string; in most cases, this should be a normalized URI.
        _props (dict): properties to attach to this URI, up to the implementing class.

    """
    _iid = 0

    def __init__(self, uri: str, props: dict = None) -> None:
        SpiderURI._iid += 1
        self._iid: int = SpiderURI._iid
        self._uri: str = uri
        self._props: dict | None = props

    @abstractmethod
    def __hash__(self) -> int:
        pass

    def __eq__(self, other) -> bool:
        if other is None or not isinstance(other, SpiderURI):
            return False
        else:
            return self._uri == other.uri

    def __str__(self) -> str:
        is_truncate = len(self._uri) >= TRUNCATION_THRESHOLD
        return "[{iid:09d}]: {ellipses}{uri} {type}".format(
            iid=self._iid,
            uri=self._uri[-TRUNCATION_THRESHOLD if is_truncate else len(self._uri):],
            ellipses="..." if is_truncate else "    ",
            type=type(self)
        )

    @property
    def iid(self) -> int:
        return self._iid

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def props(self) -> dict | None:
        return self._props


class SpiderProcessor(ABC):
    """Abstract superclass of Content and Document processors yielded by the crawler.

    This class is a superclass for: `SpiderContentProcessor` and `SpiderLinkProcessor`.

    Notes:
        `SpiderProcessor` expects iterator-like implementations to possibly allow just-in-time execution
        of the document and link parsers so not all expensive parsing operations can be deferred until the
        actual results (documents yielded from the web page content and URIs scarped from the same page)
        are required to further the crawling process.

        Due to this, the default implementation of `__iter__` method of `SpiderProcessor` simply returns `self`.

    Attributes:
        _agent (SpiderAgent): reference back to the `SpiderAgent` agent instance that yields this processor.

    """
    def __init__(self, agent: SpiderAgent) -> None:
        self._agent: SpiderAgent = agent

    @property
    def agent(self) -> SpiderAgent:
        return self._agent

    def __iter__(self) -> SpiderProcessor:
        """A default implementation that returns `self` as a `SpiderProcessor` is expected to be an iterator.

        Yields:
            The current `SpiderProcessor` instance itself.

        """
        return self

    @abstractmethod
    def __next__(self) -> SpiderArtifact:
        """Returns the next `SpiderArtifact` that resulted from a parsing content or link extraction process.

        The `SpiderArtifact` to be returned may be constructed upon the invocation of this method.

        Yields:
            `SpiderArtifact` containing the next document parsed or link extracted.

        """
        pass


class SpiderContentProcessor(SpiderProcessor):
    """Class responsible for processing the human-readable content of a web page for a crawler; behaves like
    an iterator that yields `SpiderDoc`'s. The underlying assumption here is that `SpiderContentProcessor`'s
    outputs will be used to construct an index or a database based on the contents of the web pages crawled.

    Attributes:
        _doc_db (SpiderDocDB): a direct reference to the `SpiderDocDB` used by the crawler agent (`self._agent`).

    """
    def __init__(self, agent: SpiderAgent) -> None:
        super().__init__(agent)
        self._doc_db: SpiderDocDB = self._agent.doc_db

    @abstractmethod
    def __next__(self) -> SpiderDoc:
        pass


class SpiderLinkProcessor(SpiderProcessor):
    """Class responsible for processing the hyperlinks of a web page for a crawler; behaves like
    an iterator that yields `SpiderURI`'s. The underlying assumption here is that `SpiderLinkProcessor`'s
    outputs will be re-consumed by the crawler engine, most likely by its URL Frontier and the subsequent
    crawler agents.

    Attributes:
        _uri_db (SpiderUriDB): a direct reference to the `SpiderUriDB` used by the crawler agent (`self._agent`).

    """
    def __init__(self, agent: SpiderAgent) -> None:
        super().__init__(agent)
        self._uri_db: SpiderUriDB = self._agent.uri_db

    @abstractmethod
    def __next__(self) -> SpiderURI:
        pass


class SpiderAgent(ABC):
    """Abstract data model that specifies attributes and behaviors for the actual crawler ("agent").

    Depending on the need of the implementing class, `_config` dictionary may be utilized to pass an arbitrary
    set of key-value pairs. This dictionary should contain information specific to the implementing class's purpose.
    For instance, for an implementing class intended for parsing plain HTML pages, it may be used to pass down
    a set of HTML tags and the name of HTML parser to be used.

    Attributes:
        _iid (int): instance ID (automatically increments per instantiation).
        _uri (SpiderURI): URI for a web page for the crawler agent to fetch and parse.
        _doc_db (SpiderDocDB): reference to a global Document Fingerprint database for the whole crawler system.
        _uri_db (SpiderUriDB): reference to a global URI database used for duplicate elimination in the system.
        _config (dict): arbitrary configuration key-value pairs for required by the implementing class.

    """
    _iid = 0

    def __init__(self, uri: SpiderURI, doc_db: SpiderDocDB, uri_db: SpiderUriDB, config: dict) -> None:
        SpiderAgent._iid += 1
        self._iid: int = SpiderAgent._iid
        self._uri: SpiderURI = uri
        self._doc_db: SpiderDocDB = doc_db
        self._uri_db: SpiderUriDB = uri_db
        self._config: dict = config

    def __str__(self) -> str:
        is_truncate = len(self._uri.uri) >= TRUNCATION_THRESHOLD
        return "[{iid:09d}]: {uri}{ellipses} {type}".format(
            iid=self._iid,
            uri=self._uri.uri[:TRUNCATION_THRESHOLD if is_truncate else len(self._uri.uri)],
            ellipses=" ..." if is_truncate else "    ",
            type=type(self)
        )

    @property
    def iid(self) -> int:
        return self._iid

    @property
    def uri(self) -> SpiderURI:
        return self._uri

    @property
    def doc_db(self) -> SpiderDocDB:
        return self._doc_db

    @property
    def uri_db(self) -> SpiderUriDB:
        return self._uri_db

    @property
    def config(self) -> dict:
        return self._config

    @abstractmethod
    def crawl(self) -> (SpiderContentProcessor, SpiderLinkProcessor):
        """Implementation for the web crawler content parsing and link extraction and normalizations.

        A typical implementation of this method involves fetching the page pointed by the URI (`self._uri`),
        parsing the content from the page to instantiate and populate `SpiderContentProcessor` to be yielded,
        and extracting the links from the page to instantiate and populate `SpiderLinkProcessor`.

        Yields:
            A tuple of size 2 containing `SpiderContentProcessor`, `SpiderLinkProcessor`, respectively.

        """
        pass


class SpiderUriFrontier(ABC):
    """Abstract data model for the URL Frontier to provide URIs for the crawler agents to crawl and to consume
    the extracted URIs crawler agents yield; by default, a `SpiderUriFrontier` supports FIFO ordering where
    `push` adds a `SpiderURI` to the back of the frontier and `pop` removes and returns a `SpiderURI` from the
    front of the frontier.

    At this time, there is no expectation that `SpiderUriFrontier` should support asynchronous operations, and
    all operations as defined by the methods in this class must be completed without blocking.

    Notes:
        `SpiderUriFrontier` must be instantiated with seed set of `SpiderURI`'s. An attempt to instantiate one
        with a None passed to the `seeds` argument of the constructor or an attempt to instantiate one with an
        empty list will raise a `ValueError`.

    """
    def __init__(self, seeds: list[SpiderURI]) -> None:
        if not seeds:
            raise ValueError("Seed list of URIs are required.")

        self.push_all(*seeds)

    def __bool__(self) -> bool:
        return len(self) > 0

    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def push(self, uri: SpiderURI) -> None:
        """Adds the `SpiderURI` passed in to the end of the URI Frontier."""
        pass

    @abstractmethod
    def peek(self) -> SpiderURI:
        """Returns the `SpiderURI` at the front of the URI Frontier without removing it."""
        pass

    @abstractmethod
    def pop(self) -> SpiderURI:
        """Removes and returns the `SpiderURI` at the front of the URI Frontier at the time of the invocation."""
        pass

    def push_all(self, *args: SpiderURI) -> None:
        """Adds all `SpiderURI`'s passed in via `args` by invoking `self.push` on each `SpiderURI` instance.

        First instance in the `args` gets added first, and the last instance in the `args` gets added last.

        """
        for uri in args:
            self.push(uri)


class SpiderDB(ABC):
    """Abstract superclass for a database to keep track of `SpiderArtifact`'s that have already been processed;
    provides efficient membership, size, and emptiness (using `bool(self)`) checks, as well as simple adding and
    removing of `SpiderArtifact`'s to and from the database.

    This class is a superclass for: `SpiderDocDB` and `SpiderUriDB`.

    """
    def __bool__(self) -> bool:
        """Returns `True` if the DB is empty, `False` otherwise."""
        return len(self) > 0

    @abstractmethod
    def __len__(self) -> int:
        """Returns the number of `SpiderArtifact`'s that are currently in the database."""
        pass

    @abstractmethod
    def __contains__(self, item: SpiderArtifact) -> bool:
        """Returns `True` if the given `SpiderArtifact` is in the database, `False` otherwise."""
        pass

    @abstractmethod
    def add(self, item: SpiderArtifact) -> bool:
        """Attempts to add the given `SpiderArtifact` and returns `True` if the add operation was successful,
        and `False` if the operation was unsuccessful and the given `SpiderArtifact` was not added to the database.

        """
        pass

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


class SpiderDocDB(SpiderDB):
    """Class responsible for keeping track of all `SpiderDoc`'s that have been seen by the crawling system
    by storing the `SpiderDocFP`'s (but not the `SpiderDoc`'s themselves); extends `SpiderDB`.

    """
    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __contains__(self, item: SpiderDocFP) -> bool:
        pass

    @abstractmethod
    def add(self, item: SpiderDocFP) -> bool:
        pass

    @abstractmethod
    def remove(self, item: SpiderDocFP) -> bool:
        pass


class SpiderUriDB(SpiderDB):
    """Class responsible for keeping track of all `SpiderURI`'s that have been seen by the crawling system
    by storing the `SpiderURI`'s themselves; extends `SpiderDB`.

    """
    @abstractmethod
    def __len__(self) -> int:
        pass

    @abstractmethod
    def __contains__(self, item: SpiderURI) -> bool:
        pass

    @abstractmethod
    def add(self, item: SpiderURI) -> bool:
        pass

    @abstractmethod
    def remove(self, item: SpiderURI) -> bool:
        pass
