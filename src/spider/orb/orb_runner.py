#!/usr/bin/env python3
"""Runs local sequential crawl using `spider.orb` package based on the configuration provided.
"""

import io
import sys
import json
import argparse
from spider.orb.orb_models import OrbURI, OrbDoc, OrbUriFrontier, OrbDocDB, OrbUriDB, OrbAgent
from text_processing.freq_utils import tokenize_file, print_frequencies
from text_processing.freq_counter import compute_twogram_freq
from nltk.corpus import stopwords

__author__ = "Garrett Buchanan", "Livingstone Rwagatare"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Garrett Buchanan", "Livingstone Rwagatare", "Mike Ryu"]
__license__ = "MIT"
__email__ = "mryu@westmont.edu"

VALID_CONFIG_SCHEMA = {
  "seeds": [],
  "options": {
    "remove_stopwords": False,
    "stopwords_lang": ""
  },
  "agent_config": {
    "external": [],
    "encoding": "",
    "parser": "",
    "tags": {},
    "debug": False
  }
}


def main() -> None:
    pars = setup_argument_parser()
    args = pars.parse_args()

    try:
        config = json.loads(open(args.config_file_path, 'r').read())
        if not validate_config(config, VALID_CONFIG_SCHEMA):
            raise OSError(f"Invalid configuration file: {args.config_file_path}")
    except OSError as e:
        print("An error occurred while trying to open files:\n  ", e, file=sys.stderr)
        exit(1)

    doc_stream = io.StringIO()
    uri_frontier = OrbUriFrontier(list(map(OrbURI, config["seeds"])))
    run_sequential_crawl(doc_stream, uri_frontier, OrbDocDB(), OrbUriDB(), config)
    print_twogram_freq(remove_stopwords(tokenize_file(doc_stream), config), args.output_file_path, config)


def setup_argument_parser() -> argparse.ArgumentParser:
    pars = argparse.ArgumentParser(prog="python3 -m spider.orb.orb_runner")
    pars.add_argument("config_file_path", type=str,
                      help="required string containing the path to a config JSON file")
    pars.add_argument("output_file_path", type=str, nargs='?',
                      help="optional string containing the path to an output text file")
    return pars


def validate_config(config, schema, sub=""):
    is_valid = True

    for key in schema.keys():
        config_exists = key in config.keys()
        is_valid &= config_exists

        if not config_exists:
            print(f"Required {sub}key [{key}] is not present in the config file provided.", file=sys.stderr)
        elif isinstance(schema[key], dict):
            is_valid &= validate_config(config[key], schema[key], "sub")

    return is_valid


def run_sequential_crawl(doc_str, uri_frontier, doc_db, uri_db, config):
    """This method runs the crawl process on all the URIs that we have gathered
       with our crawler."""
    while uri_frontier:
        next_uri = uri_frontier.pop()   # pop the URI to move to the net one
        if next_uri is None:
            break   # if next_uri return None that means all URIs have been crawled
        agent = OrbAgent(next_uri, doc_db, uri_db, config["agent_config"])
        debug_print_current_uri(next_uri, config)   # goes through the URIs and prints the current URI then pops it
        content_processor, link_processor = agent.crawl()
        documents = [document for document in content_processor]
        links = [link for link in link_processor]
        for document in documents:
            debug_print_current_doc(document, config)
            doc_str.write(document.content)  # writes the current document's content
        uri_frontier.push_all(*links)

    doc_str.seek(0)


def remove_stopwords(words, config):
    """This function removes all the stopwords from the content of a corpus using NLTK's stopwords corpus.
       This is done so that only relevant words are returned."""
    if not config['options']['remove_stopwords']:   # if no option to remove stopwords return the given words
        return words
    stop_words = set(stopwords.words(config['options']['stopwords_lang']))  # set of unique stopwords from config
    not_stopwords = [word for word in words if word not in stop_words]  # if a word is not in stopwords add to list
    return not_stopwords


def print_twogram_freq(all_words, output_path, config):
    """This function computes the frequencies of the words within a corpus and returns the frequencies of the two
       grams present within the corpus."""
    frequencies = compute_twogram_freq(all_words)   # computes the two gram frequencies to return
    encoding = config['agent_config']['encoding']
    with open(output_path, 'w', encoding=encoding) as output_file:  # write the contents to the output file
        print_frequencies(frequencies, output_file)


def debug_print_current_uri(uri, config):
    """Provided for debugging, interweave calls to this function in `run_sequential_crawl` implementation."""
    if config["agent_config"]["debug"]:
        debug_print_current_uri.uri_counter += 1
        print("┌ URI #{:04d} | [IID {:04d}] {} has document:".format(
            debug_print_current_uri.uri_counter,
            uri.iid,
            uri.uri)
        )


def debug_print_current_doc(doc, config):
    """Provided for debugging, interweave calls to this function in `run_sequential_crawl` implementation."""
    if config["agent_config"]["debug"]:
        if not doc:
            print(f"└{'─'*100} (none)")
        else:
            debug_print_current_doc.doc_counter += 1
            print("└ DOC #{:04d} | [IID {:04d}] '{} ...' (FP: {:20d})".format(
                debug_print_current_doc.doc_counter,
                doc.iid,
                doc.content[:80].replace("\n", " "),
                int(str(doc.fingerprint)))
            )


if __name__ == '__main__':
    debug_print_current_uri.uri_counter = 0
    debug_print_current_doc.doc_counter = 0
    main()


