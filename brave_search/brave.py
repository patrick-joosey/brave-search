import sys
from dataclasses import dataclass
from typing import TypeVar

import requests
from bs4 import BeautifulSoup
from rich import print
from rich.console import Console
from rich.panel import Panel

P = TypeVar("P", bound=Panel)


@dataclass
class Result(object):
    index: int
    title: str
    href: str
    desc: str
    time: str


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <query>")
        sys.exit(1)

    query = sys.argv[1]

    params = {
        'q': query
    }
    res = requests.get("https://search.brave.com/search", params=params)

    soup = BeautifulSoup(res.text, 'html.parser')

    results = []
    for i, item in enumerate(soup.find_all("div", "snippet fdb")[:10]):
        full_desc = item.p.text.strip()

        if "-" in full_desc:
            time, desc = full_desc.split("-", 1)
        else:
            time = ""
            desc = full_desc

        results.append(
            Result(i,
                   item.span.text.strip(),
                   item.a.get('href'),
                   desc.strip(),
                   time.strip())
        )

    console = Console()

    for r in results:
        console.print(f"[blue]{r.title}")
        console.print(f"[gray]{r.href}")
        console.print(f"{r.desc}")
        if r.time:
            console.print(f"[light gray]{r.time}")
        console.rule()


if __name__ == '__main__':
    main()
