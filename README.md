## conflict

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/vfdoOmrd)
# Assignment 2: Local Crawl
**Westmont College Fall 2023**

**CS 128 Information Retrieval and Big Data**

*Assistant Professor* Mike Ryu (mryu@westmont.edu) 

## Autor Information
* **Name(s)**: Garrett Buchanan, Livingstone Rwagatare
* **Email(s)**: gbuchanan@westmont.edu, lrwagatare@westmont.edu

## Problem Description

### The problem that needed to be solved was implementing multiple different classes and methods that provide the necessary functionality to run a simple web crawler that parses through two different corpuses and returns the frequencies of two grams within the corpus.

## Description of the Solution

### The necessary components for the solution to this assignment are the implementation of classes that allow for manipulation and sorting of documents, their contents, and the URIs within them. It also includes implemetation of link, and content processors that work in congruence with a crawl method to parse through the HTML files using BeautifulSoup and return the content and links in a format that allows for the contents to be crawled.

### OrbDocFP
Creates the fingerprint of a document by taking its hash. Includes methods for equality comparisons and conversion of the fingerprint to a string.

### OrbDoc
Contains a compute_fingerprint method that is the insantiation of the OrbDocFP class of the document content and assigns it to the '_fingerprint' attribute.

### OrbURI
Includes a hash method to compute and return the hash of a URI.

### OrbContentProcessor
implement a constructor with a call to the superclass and two attributes that represent the current document and a database for the documents. Also implements a next method that adds the fingerprint of a current document to the document database if the doc is not empty or a duplicate.

### OrbLinkProcessor
Similar to OrbContentProcessor but instead iterates through URIs and adds the current URI to a list called link_list if the URI is in the database.

### OrbAgent
Main implementation of this class is the crawl method which goes through a file and uses BeautifulSoup to find the content within an HTML document and add it to a content variable as well as iterate through a list of links and return the links with all the proper paths to the link_list.

### OrbUriFrontier
implements push, peek, and pop methods that are used to manipulate URIs within a SimpleQueue.

### OrbDB
Creates a constructor with a '_database' attribute that is an empty list (gets filled later). intantiated add adn remove methods that add or remove a given item to the database list if it is not a duplicate. Also instantiated a contains method which perfoms a membership check on an item for the database. Lastly contains a len method which returns the length of a database.

### OrbDocDB and OrbUriDB
were provided classes but were not necessary for the solution

### orb_runner.py methods
- the run_sequential_crawl method runs the crawl process on all the URIs that were gathered within the crawler (orb_models.py).
- the remove_stopwords method utilizes NLTK's stopword corpus and the config dictionary to remove all the determined stopwords from the corpus.
- the print_twogram_frequency method outputs all the two grams withini the corpus and their frequencies.


## Key Takeaways

The key takeaways from this assignment were how to become more proficient in object oriented programming, which is something that I really struggled with. After this assignment I feel like I have a much better grasp on this concept. I also learned a lot about how to use BeautifulSoup and the process of a web crawler in general which was really cool to see after learning about the concepts in class. I also learned that it is reallt beneficial to be around people who are doing the same assignment so that I can better understand the necessary components that I need to implement (basically being in community is very beneficial).

## Teamwork Report

TODO: Answer the following questions. Your response is required to receive full credit. This section is not required if you worked alone.

1. **How did you and your partner collaborate to complete this assignment?**

    We agreed on times to meet in the CS lounge during the first week of the project and bounced ideas off of each other. We also        worked remotely and pushed and pulled each other's code occasionally.


2. **How did you and your partner [equitably](https://www.marinhhs.org/sites/default/files/boards/general/equality_v._equity_04_05_2021.pdf) divide up the responsibilities?**

    


3. **What is one thing you learned from each other by collaborating?**

    TODO: Respond here.

# TODO: DELETE ALL INSTRUCTIONS STARTING WITH "TODO" BEFORE YOUR FINAL SUBMISSION!
