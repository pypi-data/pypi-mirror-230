from typing import Optional

import pyroherd
from pyroherd import raw
from pyroherd import types


class GetBotDefaultPrivileges:
    async def get_bot_default_privileges(
        self: "pyroherd.Client",
        for_channels: bool = None
    ) -> Optional["types.ChatPrivileges"]:
        """Get the current default privileges of the bot.

        Parameters:
            for_channels (``bool``, *optional*):
                Pass True to get default privileges of the bot in channels. Otherwise, default privileges of the bot
                for groups and supergroups will be returned.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                privileges = await app.get_bot_default_privileges()
        """

        bot_info = await self.invoke(
            raw.functions.users.GetFullUser(
                id=raw.types.InputUserSelf()
            )
        )

        field = "bot_broadcast_admin_rights" if for_channels else "bot_group_admin_rights"

        admin_rights = getattr(bot_info.full_user, field)

        return types.ChatPrivileges._parse(admin_rights) if admin_rights else None
