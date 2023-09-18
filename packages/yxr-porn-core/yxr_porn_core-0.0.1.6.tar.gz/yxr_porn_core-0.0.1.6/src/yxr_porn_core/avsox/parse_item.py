from dataclasses import dataclass

from lxml import etree


@dataclass
class ParseItemResult:
    title: str
    product_id: str
    cover_url: str
    length: str  # min
    date_str: str  # yyyy-mm-dd


# https://javmenu.com/zh/FC2-1851398
def parse_item(html: str) -> ParseItemResult:
    # soup = BeautifulSoup(html, "lxml")
    htmltree = etree.fromstring(html, etree.HTMLParser())

    expr_number = '//span[contains(text(),"识别码:")]/../span[2]/text()'
    # expr_actor = '//a[@class="avatar-box"]'
    # expr_actorphoto = '//a[@class="avatar-box"]'
    expr_title = "/html/body/div[2]/h3/text()"
    # expr_studio = '//p[contains(text(),"制作商: ")]/following-sibling::p[1]/a/text()'
    expr_release = '//span[contains(text(),"发行时间:")]/../text()'
    expr_cover = "/html/body/div[2]/div[1]/div[1]/a/img/@src"
    # expr_smallcover = '//*[@id="waterfall"]/div/a/div[1]/img/@src'
    # expr_tags = '/html/head/meta[@name="keywords"]/@content'
    # expr_label = '//p[contains(text(),"系列:")]/following-sibling::p[1]/a/text()'
    # expr_series = '//span[contains(text(),"系列:")]/../span[2]/text()'
    expr_runtime = '//span[contains(text(),"长度:")]/../text()'

    product_id = htmltree.xpath(expr_number)[0].upper()
    title = htmltree.xpath(expr_title)[0].replace("/", "_").strip(product_id).strip()
    cover_url = htmltree.xpath(expr_cover)[0]
    date_str = htmltree.xpath(expr_release)[0].strip()
    length = htmltree.xpath(expr_runtime)[0].replace("分钟", "").strip()

    return ParseItemResult(
        title=title,
        product_id=product_id.replace("FC2-PPV", "FC2"),
        cover_url=cover_url,
        date_str=date_str,
        length=length,
    )
