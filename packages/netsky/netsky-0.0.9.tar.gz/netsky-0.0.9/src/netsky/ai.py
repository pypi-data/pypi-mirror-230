# imports
from netsky import Bot, Console

from netsky.tools import tools
from netsky.states import NetskyState
from netsky.systems import NetskySystem

# variables
state = NetskyState()
prompts = []
description = NetskySystem().content


# classes
class AI:
    def __init__(self, name, description, tools, prompts, state):
        ai = Bot(
            name=name,
            description=description,
            tools=tools,
            additional_prompts=prompts,
            state=state,
        )

        self.ai = ai
        self.name = name
        self.tools = tools
        self.prompts = prompts
        self.description = description

        self.console = Console()

    def __call__(self, text):
        self.console.print(f"netsky.ai:\n\n", style="bold violet blink", end="")
        self.console.print(self.ai(text).content)

    def __repr__(self):
        return f"<AI {self.name}>"


# create bot
bot = AI(
    name=state.name, description=description, tools=tools, prompts=prompts, state=state
)
