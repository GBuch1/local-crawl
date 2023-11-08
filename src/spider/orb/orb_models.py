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
    """  """

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

    def __hash__(self):
        return hash(self._uri)


class OrbContentProcessor(SpiderContentProcessor):
    """TODO: Implement this class and complete the class docstring.


    HINT:
        Lazily evaluate whether the content has been seen by checking if the document `__next__` method is about
        to return has its fingerprint already stored in `self._agent.doc_db`; skip any document that has its
        fingerprint already stored in the database, but add any new document's fingerprint to the database.

    """
    def __int__(self, agent: SpiderAgent, fresh_content: str):
        super().__init__(agent)
        self._doc = OrbDoc(fresh_content) if fresh_content else None
        self._doc_db: SpiderDocDB() = self._agent.doc_db

    def __next__(self) -> SpiderDoc:
        if self._doc is None:
            raise StopIteration
        if self._doc.fingerprint in self._agent.doc_db:
            raise StopIteration
        else:
            self._doc_db.add(self._doc.fingerprint)
            return self._doc

    # need to go through all the doc_fingerprints and add them to the list
    # If they already exist, skip
    # Add all FPs only once until there is nothing left


class OrbLinkProcessor(SpiderLinkProcessor):
    """TODO: Implement this class and complete the class docstring.

    HINT:
        Do the similar lazy evaluation as `OrbContentProcessor`, except for the URIs using `self._agent.uri_db`.

        Your implementation must include instantiating `OrbURI`'s with its `props` attribute set as:
            {"parent": self._agent.uri.uri}

    """

    def __int__(self, agent: SpiderAgent, link_list: list):
        super().__init__(agent)
        self._counter = 0
        self._uri_db: SpiderUriDB = self._agent.uri_db
        self._link_list = link_list

    def __next__(self) -> SpiderURI:
        while self._counter < len(self._link_list):
            current_uri = self._link_list[self._counter]
            uri = OrbURI(current_uri, {"parent": self._agent.uri.uri})
            self._counter += 1
            if uri in self._uri_db:
                continue
            else:
                self._uri_db.add(uri)
                return uri
        raise StopIteration

        # while self._counter < len(self._link_list):
        #     link = self._link_list[self._counter]
        #     # construct OrbURI with link
        #     uri = OrbURI(link, {"parent": self._agent.uri.uri})
        #     # check if the instance you created from above is in self._uri_db
        #     if self._counter > len(self._uri_db):
        #         raise StopIteration
        #     elif uri in self._uri_db:
        #         self._counter += 1
        #     else:
        #         self._counter += 1
        #         self._uri_db += uri
        #         return uri

    # list empty?
    # at the end of the list?
    # is the link we have a duplicate
    # if any of above three stop the iteration

    # else
    # 1. normalize link
    # 2. OrbURI(link)
    # 3. Update the agentDB
    # 4. Return

    # return OrbURI(link)
    # Update the agent URI DB
    # Pass in a list of links that are strings into link processor

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
        openfile = self._open_uri_as_file()  # open the file
        if openfile:
            read_file = openfile.read()
            soup = BeautifulSoup(read_file, self._config["parser"])  # Create variable that calls BeautifulSoup
            found_tags = self.config["tags"]  # create variable found_tags which finds the tags in the HTML

            content = ""
            for tag_key in found_tags:
                total_match = soup.find_all(tag_key, found_tags[tag_key])
                for match in total_match:
                    new_string = match.text.strip() + " "
                    content += new_string
            fresh_content = content.strip()

            links = soup.find_all('a')
            link_list = []

            for link in links:
                true_link = link.get('href')
                if true_link is not None:
                    if '#' in true_link:
                        continue
                    if OrbLinkProcessor.is_link_external(self, true_link):
                        link_list.append(true_link)
                    else:
                        prev_slash_local = self.uri.uri.rfind("/")
                        path = self.uri.uri[:prev_slash_local]
                        final_link = path + "/" + true_link
                        link_list.append(final_link)

            openfile.close()

            return OrbContentProcessor(self, fresh_content), OrbLinkProcessor(self, link_list)

        else:
            return OrbContentProcessor(self, ''), OrbLinkProcessor(self, [])

        # for key in found_tags:  # create a loop to find the keys within the found tags
        #     attr = self._config["tags"][key]  # create an attribute that contains the key
        #     content = soup.find_all(found_tags, attr)  # for the keys in the "tags" config find the attributes
        #     empty_string = ""
        #     for tag in content:
        #         empty_string += tag.text.strip() + " "  # add the content to an empty string and strip it
        #     print(empty_string)
        #     empty_string.strip()  # strip the contents of the string again
        #
        # links = soup.find_all('a')
        # link_list = []
        # for link in links:
        #     true_link = link.get('href')
        #     if link_list is not None:
        #         if OrbLinkProcessor.is_link_external(self, true_link):
        #             link_list.append(true_link)
        #         else:
        #             text = self._uri.uri
        #             prev_slash = text.rfind("/")
        #             path = text[:prev_slash]
        #             link_list.append(path + '/' + true_link)

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
        if self._q.empty():
            first_uri = self._next
            self._next = None
            return first_uri
        else:
            save_next = self._next
            self._next = self._q.get_nowait()
            return save_next

    def push_all(self, *args: SpiderURI) -> None:
        """Adds all `SpiderURI`'s passed in via `args` by invoking `self.push` on each `SpiderURI` instance.

        First instance in the `args` gets added first, and the last instance in the `args` gets added last.

        """
        for uri in args:
            self.push(uri)


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
