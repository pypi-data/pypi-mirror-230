from netsky.states import BaseModel


class DefaultState(BaseModel):
    """
    Default state for bots.

    Increment execution_count on each response.
    """

    # info about bot
    name: str = "netsky.ai"
    creator: str = "dkdc.dev"
    version: str = "infinity"

    # links to open
    marvin_docs: str = "https://www.askmarvin.ai/components/overview"
    ibis_docs: str = "https://www.ibis-project.org"
