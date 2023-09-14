import re
from bs4 import BeautifulSoup

FOOTNOTE = r"(\[)(\w+|\d+)(\])"
DAGGER = "\u2020"
DOUBLE_DAGGER = "\u2021"


def remove_footnotes(text: str) -> str:
    return re.sub(
        FOOTNOTE, "", text.replace(DAGGER, "").replace(DOUBLE_DAGGER, "")
    ).strip()


class Wikitable:
    def __init__(self, table):
        self.table = table

    @property
    def headers(self) -> list[BeautifulSoup]:
        return [
            remove_footnotes(
                next(el.text.strip() for el in th.contents if el.text.strip())
            )
            for th in self.table.find_all("th")
        ]

    @property
    def data(self) -> list[list[BeautifulSoup]]:
        de_footnoted_soup = lambda x: BeautifulSoup(
            remove_footnotes(str(x)), "html.parser"
        )

        return [
            [
                de_footnoted_soup(str(td.contents[0])).contents[0]
                if len(td.contents) == 1 and bool(str(td.contents[0]).strip())
                else de_footnoted_soup("".join(str(x) for x in td.contents))
                for td in tr.find_all("td")
            ]
            for tr in self.table.find_all("tr")
            if not tr.th
        ]

    def to_dicts(self) -> list[dict[BeautifulSoup, BeautifulSoup]]:
        return [dict(zip(self.headers, row)) for row in self.data]
