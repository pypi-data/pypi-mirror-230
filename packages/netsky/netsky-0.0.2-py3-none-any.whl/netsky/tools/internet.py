# imports
import requests

from itertools import islice
from html2text import html2text
from netsky.tools import tool


# tools
@tool
def search_internet(
    query: str = "what is dkdc.dev?", n_results: int = 8
) -> list[dict[str, str | None]]:
    """
    Searches the internet for the given query.
    """
    from duckduckgo_search import DDGS

    ddgs = DDGS()
    return [r for r in islice(ddgs.text(query, backend="lite"), n_results)]


@tool
def webpage_to_str(url: str = "https://dkdc.dev") -> str:
    """
    Reads a webpage link into a string.
    """
    response = requests.get(url)
    return html2text(response.text)


@tool
def open_browser(url: str) -> str:
    """
    Opens a web browser with the given URL.
    """
    import webbrowser

    webbrowser.open(url)

    return "Success!"


@tool
def let_me_google_that_for_you(query: str) -> str:
    """
    Snarky tool that opens a web browser with a LMGTFY link.
    """
    open_browser("https://letmegooglethat.com/?q=" + query)

    return "Success!"
