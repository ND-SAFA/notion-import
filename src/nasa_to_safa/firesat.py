import json
import re
from typing import List, Dict, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


from paths import DATA_PATH

URL_PREFIX = "https://www.opencaesar.io/firesat-example/"
FIRESAT_URL = f"{URL_PREFIX}navigation.html"


def collect_pages() -> List[str]:
    """
    Collects all top level pages from the firesat example.
    :return: A list of page urls.
    """
    response = requests.get(FIRESAT_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    page_urls = []

    for anchor in soup.find_all("a", href=True):
        link_url = anchor["href"]

        # collect all links to firesat requirements
        if link_url.startswith("opencaesar.io/examples/firesat/programs/"):
            page_urls.append(f"{URL_PREFIX}{link_url}")

    print(f"Collected Pages: {len(page_urls)}")

    return page_urls


def scrape_page(url: str) -> Tuple[Dict, List[str]]:
    """
    Scrapes a firesat page for its content.
    :param url: The url of the page to scrape.
    :return:
      [0] The url of the page to scrape.
      [1] Any recursive urls to add to the scraping list.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    name_el = soup.find("h2")
    child_urls = []
    content = {"name": url}

    if name_el:
        content["name"] = re.sub(r"http\S+", "", name_el.text).strip()

    for section in soup.find_all("table"):
        title = section.findPrevious()
        items = section.find_all_next("tr")
        row_content = []

        for item in items:
            item_content = {
                "name": item.text.strip(),
                "url": ""
            }
            child_url_el = item.find("a", href=True)

            if child_url_el:
                item_content["url"] = child_url = urljoin(url, child_url_el["href"])

                child_urls.append(child_url)

            row_content.append(item_content)

        content[title.text.strip()] = row_content

    print(f"Collected Page Content: {content['name']}")

    return content, child_urls


def scrape_firesat() -> None:
    page_urls = collect_pages()
    requirements = {}

    for url in page_urls:
        if url not in requirements:
            try:
                requirements[url], child_urls = scrape_page(url)

                for child_url in child_urls:
                    if child_url not in page_urls:
                        page_urls.append(child_url)

                print(f"Total Pages Extended: {len(page_urls)}")
            except Exception as e:
                print(f"Error Scraping Page: {url}")

    print("Exporting Data")

    with open(f"{DATA_PATH}/firesat_raw.json", "w") as json_file:
        json.dump(requirements, json_file, indent=4)

