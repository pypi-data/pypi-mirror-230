from typing import Union

import pyroherd
from pyroherd import raw


class MarkChatUnread:
    async def mark_chat_unread(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
    ) -> bool:
        """Mark a chat as unread.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            ``bool``: On success, True is returned.
        """

        return await self.invoke(
            raw.functions.messages.MarkDialogUnread(
                peer=await self.resolve_peer(chat_id),
                unread=True
            )
        )
