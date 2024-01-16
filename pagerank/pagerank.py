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

    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


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
        pages[filename] = set(link for link in pages[filename]if link in pages)

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
    total_pages = len(corpus) - 1

    # add dumpling Factor to all pages
    for _page in corpus:
        if _page != page:
            possibilities[_page] = (1 - damping_factor) / total_pages
    link_numbers = len(corpus[page])

    # increase the chance of linked pages
    for link in corpus[page]:
        possibilities[link] += damping_factor / link_numbers

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
    visited = list()

    # choose initial page randomly
    page = random.choice(list(corpus.keys()))

    for _ in range(n):
        # list other pages' chances to get visited based on current page
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

    # initializing ranks
    _values = dict()
    new_values = dict()
    total_pages = len(corpus)

    for page in corpus.keys():
        _values[page] = 1 / total_pages
        new_values[page] = 1 / total_pages

    # A page that has no links at all should be interpreted as having one link for every page in the corpus (including itself).
    for key, value in corpus.items():
        if len(set(value)) == 0 or ((len(set(value)) == 1) and key in value):
            corpus[key] = set([k for k in corpus.keys()])

    while True:
        _values = new_values.copy()

        for page in corpus:
            # check all other pages if they link our current page
            # each page has the dumpling chance
            new_value = (1 - damping_factor) / total_pages
            for other_page in corpus:
                # check other pages if they linked current page
                if page != other_page and (page in corpus[other_page]):
                    # count second page links except it link to itself
                    linker_total_links = (
                        len(corpus[other_page])
                        if other_page not in corpus[other_page]
                        else len(corpus[other_page])
                    )

                    # calculating the value of the link based on page's value
                    link_value = _values[other_page] / linker_total_links

                    # add link value times its chance to not dumpling on a random page
                    new_value += damping_factor * link_value
            new_values[page] = new_value

        if all(abs(new_values[page] - _values[page]) < 0.001 for page in corpus):
            # if we were close enough stop the processing
            return new_values
        else:
            _values = new_values.copy()
            # if we wasn't there yet, replace old ranks with new ones


if __name__ == "__main__":
    main()
