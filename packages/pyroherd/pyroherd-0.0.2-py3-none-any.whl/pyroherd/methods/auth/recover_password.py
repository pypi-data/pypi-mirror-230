import logging

import pyroherd
from pyroherd import raw
from pyroherd import types

log = logging.getLogger(__name__)


class RecoverPassword:
    async def recover_password(
        self: "pyroherd.Client",
        recovery_code: str
    ) -> "types.User":
        """Recover your password with a recovery code and log in.

        Parameters:
            recovery_code (``str``):
                The recovery code sent via email.

        Returns:
            :obj:`~pyroherd.types.User`: On success, the authorized user is returned and the Two-Step Verification
            password reset.

        Raises:
            BadRequest: In case the recovery code is invalid.
        """
        r = await self.invoke(
            raw.functions.auth.RecoverPassword(
                code=recovery_code
            )
        )

        await self.storage.user_id(r.user.id)
        await self.storage.is_bot(False)

        return types.User._parse(self, r.user)
