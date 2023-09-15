from typing import Union

import pyroherd
from pyroherd import raw


class SendReaction:
    async def send_reaction(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
        message_id: int,
        emoji: str = "",
        big: bool = False
    ) -> bool:
        """Send a reaction to a message.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

            emoji (``str``, *optional*):
                Reaction emoji.
                Pass "" as emoji (default) to retract the reaction.
            
            big (``bool``, *optional*):
                Pass True to show a bigger and longer reaction.
                Defaults to False.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Send a reaction
                await app.send_reaction(chat_id, message_id, "🔥")

                # Retract a reaction
                await app.send_reaction(chat_id, message_id)
        """
        await self.invoke(
            raw.functions.messages.SendReaction(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                reaction=emoji,
                big=big
            )
        )

        return True
