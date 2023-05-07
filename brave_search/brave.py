from dataclasses import dataclass
from typing import TypeVar, List

import requests
import typer
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from typing_extensions import Annotated

app = typer.Typer(add_completion=False)

P = TypeVar("P", bound=Panel)


@dataclass
class Result(object):
    index: int
    title: str
    href: str
    desc: str
    time: str


def display_results(results: List[Result], csv: bool) -> None:
    """
    Display results to terminal or csv style output
    :param results: List of Result objects from do_search
    :param csv: boolean for csv style output
    """

    if csv:
        print("link,title,description")
        for r in results:
            print(",".join([r.href, r.title, r.desc]))

    else:
        console = Console()

        for i, r in enumerate(results):
            console.print(f"{i + 1} [light blue]{r.title}")
            console.print(f"[gray]{r.href}")
            console.print(f"{r.desc}")
            if r.time:
                console.print(f"[light gray]{r.time}")
            console.rule()


def do_search(query: str, limit: int = 10) -> List[Result]:
    """
    Perform request to search.brave.com and return a list of Results

    :param query: search string
    :param limit: limit search results to int
    :return:
    """

    res = requests.get("https://search.brave.com/search", params={'q': query})

    soup = BeautifulSoup(res.text, 'html.parser')

    results = []

    for i, item in enumerate(soup.find_all("div", "snippet fdb")[:limit]):
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

    return results


@app.command(no_args_is_help=True)
def main(
        query: Annotated[str, typer.Argument(..., help="search query")],
        limit: int = typer.Option(10, help="number of search results"),
        csv: bool = typer.Option(False, help="output results as csv")
):
    """
    Search brave.com from the CLI
    """

    display_results(do_search(query, limit), csv)


if __name__ == '__main__':
    app()
