# imports
from pydantic import BaseModel


# states
class NetskyState(BaseModel):
    """State of netsky.ai"""

    # info about bot
    name: str = "netsky.ai"
    creator: str = "dkdc.dev"
    version: str = "infinity"

    # links to open
    ibis_docs: str = "https://www.ibis-project.org"
    ibis_github: str = "https://github.com/ibis-project/ibis"
    marvin_docs: str = "https://www.askmarvin.ai/components/overview"
    self_source_code: str = "https://github.com/lostmygithubaccount/netsky"

    # additional links
    links: list[str] = []
