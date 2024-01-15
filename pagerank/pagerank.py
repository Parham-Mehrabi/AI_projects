import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

    # ranks = iterate_pagerank(corpus, DAMPING)
    # print(f"PageRank Results from Iteration")
    # for page in sorted(ranks):
    #     print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()
    directory = 'pagerank/' + directory
    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    possibilities = dict()
    page_numbers = len(corpus) - 1

    # add dumpling Factor to all pages
    for _page in corpus:
        if _page != page:
            possibilities[_page] = (1 - damping_factor) / page_numbers
    link_numbers = len(corpus[page])

    # increase the chance of linked pages
    for link in corpus[page]:
        possibilities[link] += (damping_factor / link_numbers)

    return possibilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    possibilities = dict()
    page = random.choice(list(corpus.items()))[0]
    visited = list()
    for _ in range(n):

        # list other pages chance to get visited based on current page
        next_possible_pages = transition_model(
            corpus=corpus, page=page, damping_factor=damping_factor
        )

        # extract each page and its chanced to get visited based on current page
        pages, chance = zip(*next_possible_pages.items())

        # choose next page based on their chance from current page
        next_page = random.choices(pages, chance)[0]

        # add next page to visited page
        visited.append(next_page)

        # move to next page
        page = next_page

    for page, visits in Counter(visited).items():

        # calculate each page Value based on visits
        possibilities[page] = visits / n

    return possibilities


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    raise NotImplementedError


if __name__ == "__main__":
    main()
