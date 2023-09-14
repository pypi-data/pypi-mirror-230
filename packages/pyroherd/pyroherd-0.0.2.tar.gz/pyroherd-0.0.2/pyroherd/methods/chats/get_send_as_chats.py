from typing import List, Union

import pyroherd
from pyroherd import raw
from pyroherd import types


class GetSendAsChats:
    async def get_send_as_chats(
        self: "pyroherd.Client",
        chat_id: Union[int, str]
    ) -> List["types.Chat"]:
        """Get the list of "send_as" chats available.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            List[:obj:`~pyroherd.types.Chat`]: The list of chats.

        Example:
            .. code-block:: python

                chats = await app.get_send_as_chats(chat_id)
                print(chats)
        """
        r = await self.invoke(
            raw.functions.channels.GetSendAs(
                peer=await self.resolve_peer(chat_id)
            )
        )

        users = {u.id: u for u in r.users}
        chats = {c.id: c for c in r.chats}

        send_as_chats = types.List()

        for p in r.peers:
            if isinstance(p, raw.types.PeerUser):
                send_as_chats.append(types.Chat._parse_chat(self, users[p.user_id]))
            else:
                send_as_chats.append(types.Chat._parse_chat(self, chats[p.channel_id]))

        return send_as_chats
