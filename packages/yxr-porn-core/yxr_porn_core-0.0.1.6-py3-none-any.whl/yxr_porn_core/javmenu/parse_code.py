from dataclasses import dataclass
from typing import List

from bs4 import BeautifulSoup
from lxml import etree


@dataclass
class ParseCodeResult:
    title: str
    product_id: str
    cover_url: str
    length: str  # min
    date_str: str  # yyyy-mm-dd
    tags: List[str]


# https://javmenu.com/zh/FC2-1851398
def parse_code(html: str) -> ParseCodeResult:
    BeautifulSoup(html, "lxml")
    htmltree = etree.fromstring(html, etree.HTMLParser())

    expr_title = '/html/head/meta[@property="og:title"]/@content'
    expr_cover = '/html/head/meta[@property="og:image"]/@content'
    expr_number = 'string(//span[contains(text(),"番号")]/..)'
    expr_runtime = '//span[contains(text(),"时长")]/../span[2]/text()'
    expr_release = '//span[contains(text(),"日期")]/../span[2]/text()'
    # expr_studio = '//span[contains(text(),"製作")]/../span[2]/a/text()'
    # expr_actor = '//a[contains(@class,"actress")]/text()'
    expr_tags = '//a[contains(@class,"genre")]/text()'

    # TODO unsafe parse
    product_id: str = "".join(htmltree.xpath(expr_number).split())
    product_id = product_id.replace("番号:", "").strip().upper()

    # TODO safe parse
    title = htmltree.xpath(expr_title)[0]
    title = title.replace(product_id, "")
    title = title.replace("| 每日更新", "")
    title = title.replace("| JAV目录大全", "")
    title = title.replace("免费在线看", "").strip()

    cover_url = htmltree.xpath(expr_cover)[0]
    date_str = htmltree.xpath(expr_release)[0]
    length = htmltree.xpath(expr_runtime)[0].replace("分钟", "").strip()
    tags = [s.strip() for s in htmltree.xpath(expr_tags)]

    return ParseCodeResult(
        title=title, product_id=product_id, cover_url=cover_url, date_str=date_str, length=length, tags=tags
    )
