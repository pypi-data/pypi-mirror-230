import pyroherd
from pyroherd import raw
from pyroherd import types


class GetMe:
    async def get_me(
        self: "pyroherd.Client"
    ) -> "types.User":
        """Get your own user identity.

        Returns:
            :obj:`~pyroherd.types.User`: Information about the own logged in user/bot.

        Example:
            .. code-block:: python

                me = await app.get_me()
                print(me)
        """
        r = await self.invoke(
            raw.functions.users.GetFullUser(
                id=raw.types.InputUserSelf()
            )
        )

        users = {u.id: u for u in r.users}

        return types.User._parse(self, users[r.full_user.id])
