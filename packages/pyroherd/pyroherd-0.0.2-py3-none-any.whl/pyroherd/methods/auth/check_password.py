import logging

import pyroherd
from pyroherd import raw
from pyroherd import types
from pyroherd.utils import compute_password_check

log = logging.getLogger(__name__)


class CheckPassword:
    async def check_password(
        self: "pyroherd.Client",
        password: str
    ) -> "types.User":
        """Check your Two-Step Verification password and log in.

        Parameters:
            password (``str``):
                Your Two-Step Verification password.

        Returns:
            :obj:`~pyroherd.types.User`: On success, the authorized user is returned.

        Raises:
            BadRequest: In case the password is invalid.
        """
        r = await self.invoke(
            raw.functions.auth.CheckPassword(
                password=compute_password_check(
                    await self.invoke(raw.functions.account.GetPassword()),
                    password
                )
            )
        )

        await self.storage.user_id(r.user.id)
        await self.storage.is_bot(False)

        return types.User._parse(self, r.user)
