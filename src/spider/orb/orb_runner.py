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

__author__ = "Boaty McBoatface, Planey McPlaneface"
__copyright__ = "Copyright 2023, Westmont College"
__credits__ = ["Boaty McBoatface", "Planey McPlaneface", "Mike Ryu"]
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
    """TODO: Implement this function and complete the docstring to explain your logic.

    HINT:
        Interweave `debug_print_*` functions provided to you (below) in your code
        such that you can visually verify the crawling behavior you implemented.

    """
    pass


def remove_stopwords(words, config):
    """TODO: Implement this function and complete the docstring.

    HINT:
        Use the config dictionary to determine whether to remove stopwords and if so, which language to use;
        using NLTK's `stopwords` corpus, this should be a relatively simple function to implement.

    """
    pass


def print_twogram_freq(all_words, output_path, config):
    """TODO: Implement this function and complete the docstring."""
    pass


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


