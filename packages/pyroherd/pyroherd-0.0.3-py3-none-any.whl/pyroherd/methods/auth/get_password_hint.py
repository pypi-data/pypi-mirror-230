import logging

import pyroherd
from pyroherd import raw

log = logging.getLogger(__name__)


class GetPasswordHint:
    async def get_password_hint(
        self: "pyroherd.Client",
    ) -> str:
        """Get your Two-Step Verification password hint.

        Returns:
            ``str``: On success, the password hint as string is returned.
        """
        return (await self.invoke(raw.functions.account.GetPassword())).hint
