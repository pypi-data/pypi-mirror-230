import pyroherd
from pyroherd import raw


class GetContactsCount:
    async def get_contacts_count(
        self: "pyroherd.Client"
    ) -> int:
        """Get the total count of contacts from your Telegram address book.

        Returns:
            ``int``: On success, the contacts count is returned.

        Example:
            .. code-block:: python

                count = await app.get_contacts_count()
                print(count)
        """

        return len((await self.invoke(raw.functions.contacts.GetContacts(hash=0))).contacts)
