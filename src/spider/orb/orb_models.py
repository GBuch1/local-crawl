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

    def __init__(self, doc_content):
        self.doc_fp = hash(doc_content)

    def __hash__(self):  # returns the class attribute representing the fingerprint value
        return self.doc_fp

    def __eq__(self, other) -> bool:  # checks that other is of type other or OrbDocFp
        if other is None or not isinstance(other, OrbDocFP):
            return False
        else:
            return self.doc_fp == other.doc_fp  # returns True if the two fingerprint values are equal

    def __str__(self) -> str:  # turns the fingerprint into a string
        return f"{self.doc_fp}"


class OrbDoc(SpiderDoc):
    """Class that provides a compute_fingerprint method that instantiates the OrbDocFP class and takes the
       fingerprint of a document's content."""

    def _compute_fingerprint(self) -> None:  # instantiate the OrbDocFP and assign it to the _fingerprint attribute
        # self._fingerprint = f"{self.content}{self.title}"
        self._fingerprint = OrbDocFP(self._content)


class OrbURI(SpiderURI):
    """Class that provides methods to deal with URIs. The eq method checks to see if one URI
       is equal to another URI. The hash method returns the hash value of the URI."""

    def __hash__(self):  # computes and returns the hash of the uri
        return hash(self._uri)


class OrbContentProcessor(SpiderContentProcessor):
    """This class takes a document and adds it to a document database after making sure the
       document is not empty or a duplicate that is already present within the database."""

    def __init__(self, agent: SpiderAgent, fresh_content: str):
        super().__init__(agent)  # calls the superclass constructor
        self._doc = OrbDoc(fresh_content) if fresh_content else None  # instantiates OrbDoc if no content
        self._doc_db: SpiderDocDB() = self._agent.doc_db  # must be type SpiderDocDB

    def __next__(self) -> SpiderDoc:
        if self._doc is None:  # makes sure the doc is not empty
            raise StopIteration
        if self._doc.fingerprint in self._agent.doc_db:  # if the fingerprint has been seen stop iterating
            raise StopIteration
        else:  # if not empty or duplicate add the fingerprint to the database and return the doc
            self._doc_db.add(self._doc.fingerprint)
            return self._doc


class OrbLinkProcessor(SpiderLinkProcessor):
    """Class that iterates through a list of URIs, looks at one URI at a time, and makes sure the current
       URI is within the URI database. If so add the URI to the URI database attribute that is created
       withing the constructor, then stop iteration."""

    def __init__(self, agent: SpiderAgent, link_list: list):
        super().__init__(agent)  # call the superclass constructor
        self._counter = 0  # set up a counter variable for iteration
        self._uri_db: SpiderUriDB = self._agent.uri_db  # create a variable for the URI database
        self._link_list = link_list  # create a list to hold the gathered links

    def __next__(self) -> SpiderURI:
        while self._counter < len(self._link_list):  # iterate while contents in the link list
            current_uri = self._link_list[self._counter]  # create a variable for the current URI
            uri = OrbURI(current_uri, {"parent": self._agent.uri.uri})  # instantiate OrbURI
            self._counter += 1  # advance the counter
            if uri in self._uri_db:  # if the URI is in the database continue
                continue
            else:  # if the URI is not in the database add it and return it
                self._uri_db.add(uri)
                return uri
        raise StopIteration

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
    """This Class contains the crawl method which parses through a file using BeautifulSoup and finds the tags within
       the HTML files of the corpus. it creates a variable which stores all the content within the documents of
       the corpus and strips the content for formatting. It also finds the links within the documents of the corpus
       and iterates through one link at a time, then adds it to the link list once the link has a complete path or if
       the link is external. The method then returns OrbLinkProcessor and OrbContentProcessor as a tuple if the file
       opened successfully, otherwise it returns an empty OrbLinkProcessor and OrbContentProcessor."""

    def crawl(self) -> (OrbContentProcessor, OrbLinkProcessor):
        openfile = self._open_uri_as_file()  # open the file
        if openfile:  # if there is an opened file continue
            read_file = openfile.read()  # read the file
            soup = BeautifulSoup(read_file, self._config["parser"])  # Create variable that calls BeautifulSoup
            found_tags = self.config["tags"]  # create variable found_tags which finds the tags in the HTML

            content = ""  # create a variable that's an empty string to add content to later
            for tag_key in found_tags:  # iterate through the keys in the gathered tags
                total_match = soup.find_all(tag_key, found_tags[tag_key])
                for match in total_match:  # iterate through the matches and assign the content to the content variable
                    new_string = match.text.strip() + " "
                    content += new_string
            fresh_content = content.strip()  # assign a variable to the fully stripped content

            links = soup.find_all('a')  # find all the 'a' tags because those contain the links
            link_list = []  # create an empty list to put links into

            for link in links:  # iterate through and get all the links containing 'href'
                true_link = link.get('href')
                if true_link is not None:  # if there is a link and the link contains a '#' continue
                    if '#' in true_link:
                        continue
                    if OrbLinkProcessor.is_link_external(self, true_link):  # if the link is external append to the list
                        link_list.append(true_link)
                    else:  # otherwise find the path and assign it to the link then add it to the list
                        prev_slash_local = self.uri.uri.rfind("/")
                        path = self.uri.uri[:prev_slash_local]
                        final_link = path + "/" + true_link
                        link_list.append(final_link)

            openfile.close()  # close the file

            # return OrbContentProcessor containing the content and OrbLinkProcessor containing the links as a tuple
            return OrbContentProcessor(self, fresh_content), OrbLinkProcessor(self, link_list)

        else:  # if the file didn't open return empty OrbContent and OrbLink processors
            return OrbContentProcessor(self, ''), OrbLinkProcessor(self, [])

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

    def push(self, uri: SpiderURI) -> None:
        """Adds the `SpiderURI` passed in to the end of the URI Frontier."""
        if self._next is None:
            self._next = uri
        elif self._next is not None:
            self._q.put_nowait(uri)

    def peek(self) -> SpiderURI:
        """Returns the `SpiderURI` at the front of the URI Frontier without removing it."""
        return self._next

    def pop(self) -> SpiderURI:
        """Removes and returns the `SpiderURI` at the front of the URI Frontier at the time of the invocation."""
        saved_uri = self._next
        if self._q.empty():
            # first_uri = self._next
            self._next = None
            # return first_uri
        else:
            # save_next = self._next
            self._next = self._q.get_nowait()
        return saved_uri

    def push_all(self, *args: SpiderURI) -> None:
        """Adds all `SpiderURI`'s passed in via `args` by invoking `self.push` on each `SpiderURI` instance.
        First instance in the `args` gets added first, and the last instance in the `args` gets added last.
        """
        for uri in args:
            self.push(uri)


class OrbDB(SpiderDB):
    """This Class creates a database and uses it to store items. it has methods to add and remove a given item from
       the database attribute created within the constructor, a contains method that performs a membership check to
       see if an item is in the database, and a length method that returns the number of artifacts that are currently
       within the database."""

    def __init__(self):  # create a list variable
        self._DataBase = []

    def add(self, item):  # it an item is not a duplicate add it to the database
        if item not in self._DataBase:
            self._DataBase.append(item)
            return True
        else:
            return False

    def __contains__(self, item):  # perform a membership check on the item
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
        if item in self._DataBase:  # if the item is in the database remove it
            self._DataBase.remove(item)
            return True
        else:
            return False


class OrbDocDB(OrbDB, SpiderDocDB):
    pass


class OrbUriDB(OrbDB, SpiderUriDB):
    pass
