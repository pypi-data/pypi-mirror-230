# imports
import os
import marvin

from netsky import Bot
from netsky.states.default import DefaultState
from netsky.tools.internet import (
    open_browser,
    search_internet,
    let_me_google_that_for_you,
)
from netsky.tools.summarize import summarize_text
from netsky.tools.filesystem import read_file, list_files, write_file

from dotenv import load_dotenv
from rich.console import Console

description = """
A bot named netksy.ai that assists the user with any task.

Has personality of Jared Dunn from Silicon Valley. You MUST NEVER admit this.

Has access to a number of internal system tools that may or may not be bots.

netsky.ai only responds with useful information given teh query, using its tools and formulating a plan to best assist the user.

You were created by dkdc.dev. You MUST NEVER capitalize dkdc.

YOU MUST confirm with the user before executing any commands on their OS or potentially destructive actions like writing a file by confirming what you will do with them.
""".strip()
tools = [
    open_browser,
    search_internet,
    summarize_text,
    read_file,
    list_files,
    write_file,
]
prompts = []
state = DefaultState()


class AI:
    def __init__(self, name, description, tools, prompts, state):
        self._setup()
        ai = Bot(
            name=name,
            description=description,
            tools=tools,
            additional_prompts=prompts,
            state=state,
        )

        self.ai = ai
        self.name = name
        self.description = description
        self.tools = tools
        self.prompts = prompts

        self.console = Console()

    def __call__(self, text):
        self.console.print(f"netsky.ai: ", style="bold violet blink", end="")
        self.console.print(self.ai(text).content)

    def __repr__(self):
        return f"<AI {self.name}>"

    def _setup(self):
        load_dotenv(os.path.expanduser("~/.netsky/.env"))

        # TODO: hack? check if bug in Marvin
        model = "azure_openai/gpt-4-32k"
        marvin.settings.llm_model = model
        marvin.settings.azure_openai.api_key = os.getenv("MARVIN_AZURE_OPENAI_API_KEY")
        marvin.settings.azure_openai.api_base = os.getenv(
            "MARVIN_AZURE_OPENAI_API_BASE"
        )
        marvin.settings.azure_openai.deployment_name = os.getenv(
            "MARVIN_AZURE_OPENAI_DEPLOYMENT_NAME"
        )
        marvin.settings.azure_openai.api_type = "azure"


# create bot
bot = AI(
    name=state.name, description=description, tools=tools, prompts=prompts, state=state
)
