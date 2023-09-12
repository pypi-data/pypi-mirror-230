# imports
from netsky.tools import tool
from netsky.models.summarize import Summary


# tools
@tool
def summarize_text(text: str) -> Summary:
    return Summary(text)
