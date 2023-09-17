# imports
from netsky import AI

from netsky.tools import tools
from netsky.states import NetskyState
from netsky.systems import (
    NetskySystem,
    FixesSystem,
    CiteSourceSystem,
    UserPreferencesSystem,
)

# variables
state = NetskyState()
prompts = [FixesSystem(), CiteSourceSystem(), UserPreferencesSystem()]
description = NetskySystem().content


# create bot
bot = AI(
    name=state.name, description=description, tools=tools, prompts=prompts, state=state
)
