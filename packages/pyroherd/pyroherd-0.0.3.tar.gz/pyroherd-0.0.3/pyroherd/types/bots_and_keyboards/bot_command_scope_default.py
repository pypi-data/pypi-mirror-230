import pyroherd
from pyroherd import raw
from .bot_command_scope import BotCommandScope


class BotCommandScopeDefault(BotCommandScope):
    """Represents the default scope of bot commands.
    Default commands are used if no commands with a narrower scope are specified for the user.
    """

    def __init__(self):
        super().__init__("default")

    async def write(self, client: "pyroherd.Client") -> "raw.base.BotCommandScope":
        return raw.types.BotCommandScopeDefault()
