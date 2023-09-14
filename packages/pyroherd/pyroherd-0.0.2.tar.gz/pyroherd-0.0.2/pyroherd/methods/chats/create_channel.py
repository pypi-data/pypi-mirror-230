import pyroherd
from pyroherd import raw
from pyroherd import types


class CreateChannel:
    async def create_channel(
        self: "pyroherd.Client",
        title: str,
        description: str = ""
    ) -> "types.Chat":
        """Create a new broadcast channel.

        Parameters:
            title (``str``):
                The channel title.

            description (``str``, *optional*):
                The channel description.

        Returns:
            :obj:`~pyroherd.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                await app.create_channel("Channel Title", "Channel Description")
        """
        r = await self.invoke(
            raw.functions.channels.CreateChannel(
                title=title,
                about=description,
                broadcast=True
            )
        )

        return types.Chat._parse_chat(self, r.chats[0])
