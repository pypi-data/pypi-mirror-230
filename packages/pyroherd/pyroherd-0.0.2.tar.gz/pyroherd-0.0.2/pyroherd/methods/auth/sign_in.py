import logging
from typing import Union

import pyroherd
from pyroherd import raw
from pyroherd import types

log = logging.getLogger(__name__)


class SignIn:
    async def sign_in(
        self: "pyroherd.Client",
        phone_number: str,
        phone_code_hash: str,
        phone_code: str
    ) -> Union["types.User", "types.TermsOfService", bool]:
        """Authorize a user in Telegram with a valid confirmation code.

        Parameters:
            phone_number (``str``):
                Phone number in international format (includes the country prefix).

            phone_code_hash (``str``):
                Code identifier taken from the result of :meth:`~pyroherd.Client.send_code`.

            phone_code (``str``):
                The valid confirmation code you received (either as Telegram message or as SMS in your phone number).

        Returns:
            :obj:`~pyroherd.types.User` | :obj:`~pyroherd.types.TermsOfService` | bool: On success, in case the
            authorization completed, the user is returned. In case the phone number needs to be registered first AND the
            terms of services accepted (with :meth:`~pyroherd.Client.accept_terms_of_service`), an object containing
            them is returned. In case the phone number needs to be registered, but the terms of services don't need to
            be accepted, False is returned instead.

        Raises:
            BadRequest: In case the arguments are invalid.
            SessionPasswordNeeded: In case a password is needed to sign in.
        """
        phone_number = phone_number.strip(" +")

        r = await self.invoke(
            raw.functions.auth.SignIn(
                phone_number=phone_number,
                phone_code_hash=phone_code_hash,
                phone_code=phone_code
            )
        )

        if isinstance(r, raw.types.auth.AuthorizationSignUpRequired):
            if r.terms_of_service:
                return types.TermsOfService._parse(terms_of_service=r.terms_of_service)

            return False
        else:
            await self.storage.user_id(r.user.id)
            await self.storage.is_bot(False)

            return types.User._parse(self, r.user)
