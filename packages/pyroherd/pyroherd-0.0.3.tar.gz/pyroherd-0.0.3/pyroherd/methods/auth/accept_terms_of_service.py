import pyroherd
from pyroherd import raw


class AcceptTermsOfService:
    async def accept_terms_of_service(
        self: "pyroherd.Client",
        terms_of_service_id: str
    ) -> bool:
        """Accept the given terms of service.

        Parameters:
            terms_of_service_id (``str``):
                The terms of service identifier.
        """
        r = await self.invoke(
            raw.functions.help.AcceptTermsOfService(
                id=raw.types.DataJSON(
                    data=terms_of_service_id
                )
            )
        )

        return bool(r)
