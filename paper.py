from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

from main import HEADERS


@dataclass
class Paper:
    _url: str
    _text: str = field(default="", init=False)

    def fetch_text(self):
        print("Загружаем статью...")
        response = requests.get(self._url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        content = soup.find("div", id="post-content-body")
        if not content:
            raise RuntimeError("Не удалось найти контент статьи на странице.")

        for tag in content.find_all(["figure", "script", "style", "code", "pre"]):
            tag.decompose()

        self._text = content.get_text(separator="\n", strip=True)

    @property
    def text(self):
        return self._text