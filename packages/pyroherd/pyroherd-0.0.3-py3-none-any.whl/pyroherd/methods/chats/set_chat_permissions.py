from typing import Union

import pyroherd
from pyroherd import raw
from pyroherd import types


class SetChatPermissions:
    async def set_chat_permissions(
        self: "pyroherd.Client",
        chat_id: Union[int, str],
        permissions: "types.ChatPermissions",
    ) -> "types.Chat":
        """Set default chat permissions for all members.

        You must be an administrator in the group or a supergroup for this to work and must have the
        *can_restrict_members* admin rights.

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            permissions (:obj:`~pyroherd.types.ChatPermissions`):
                New default chat permissions.

        Returns:
            :obj:`~pyroherd.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                from pyroherd.types import ChatPermissions

                # Completely restrict chat
                await app.set_chat_permissions(chat_id, ChatPermissions())

                # Chat members can only send text messages and media messages
                await app.set_chat_permissions(
                    chat_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True
                    )
                )
        """

        r = await self.invoke(
            raw.functions.messages.EditChatDefaultBannedRights(
                peer=await self.resolve_peer(chat_id),
                banned_rights=raw.types.ChatBannedRights(
                    until_date=0,
                    send_messages=not permissions.can_send_messages,
                    send_media=not permissions.can_send_media_messages,
                    send_stickers=not permissions.can_send_other_messages,
                    send_gifs=not permissions.can_send_other_messages,
                    send_games=not permissions.can_send_other_messages,
                    send_inline=not permissions.can_send_other_messages,
                    embed_links=not permissions.can_add_web_page_previews,
                    send_polls=not permissions.can_send_polls,
                    change_info=not permissions.can_change_info,
                    invite_users=not permissions.can_invite_users,
                    pin_messages=not permissions.can_pin_messages,
                )
            )
        )

        return types.Chat._parse_chat(self, r.chats[0])
