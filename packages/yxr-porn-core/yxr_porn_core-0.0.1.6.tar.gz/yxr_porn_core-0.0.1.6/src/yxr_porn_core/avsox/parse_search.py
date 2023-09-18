from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup


@dataclass
class ParseSearchItem:
    title: str
    product_id: str
    cover_url: str
    date_str: str  # yyyy-mm-dd
    href: str


ParseSearchResult = List[ParseSearchItem]


# https://avsox.click/cn/search/FC2-3059030
def parse_search(html: str) -> ParseSearchResult:
    soup = BeautifulSoup(html, "lxml")
    # htmltree = etree.fromstring(html, etree.HTMLParser())

    items = soup.find_all("div", class_="item")
    result = [
        ParseSearchItem(
            title=o.find("img")["title"],
            product_id=o.find_all("date")[0].text.strip(),
            cover_url=o.find("img")["src"],
            date_str=o.find_all("date")[1].text.strip(),
            href="https:" + o.a["href"],
        )
        for o in items
    ]

    return result
