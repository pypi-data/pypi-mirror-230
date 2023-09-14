import pyroherd
from pyroherd import raw
from .bot_command_scope import BotCommandScope


class BotCommandScopeAllPrivateChats(BotCommandScope):
    """Represents the scope of bot commands, covering all private chats.
    """

    def __init__(self):
        super().__init__("all_private_chats")

    async def write(self, client: "pyroherd.Client") -> "raw.base.BotCommandScope":
        return raw.types.BotCommandScopeUsers()
