from typing import Union

import pyroherd
from pyroherd import raw


class DeleteChatInviteLink:
    async def delete_chat_invite_link(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
        invite_link: str,
    ) -> bool:
        """Delete an already revoked invite link.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat or username of the target channel/supergroup
                (in the format @username).

            invite_link (``str``):
                The revoked invite link to delete.

        Returns:
            ``bool``: On success ``True`` is returned.
        """

        return await self.invoke(
            raw.functions.messages.DeleteExportedChatInvite(
                peer=await self.resolve_peer(chat_id),
                link=invite_link,
            )
        )
