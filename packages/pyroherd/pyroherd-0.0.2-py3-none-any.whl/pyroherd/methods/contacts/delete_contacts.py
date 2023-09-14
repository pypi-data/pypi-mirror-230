from typing import List, Union

import pyroherd
from pyroherd import raw, types


class DeleteContacts:
    async def delete_contacts(
        self: "pyroherd.Client",
        user_ids: Union[int, str, List[Union[int, str]]]
    ) -> Union["types.User", List["types.User"], None]:
        """Delete contacts from your Telegram address book.

        Parameters:
            user_ids (``int`` | ``str`` | List of ``int`` or ``str``):
                A single user id/username o a list of user identifiers (id or username).

        Returns:
            :obj:`~pyroherd.types.User` | List of :obj:`~pyroherd.types.User` | ``None``: In case *user_ids* was an
            integer or a string, a single User object is returned. In case *user_ids* was a list, a list of User objects
            is returned. In case nothing changed after calling the method (for example, when deleting a non-existent
            contact), None is returned.

        Example:
            .. code-block:: python

                await app.delete_contacts(user_id)
                await app.delete_contacts([user_id1, user_id2, user_id3])
        """
        is_list = isinstance(user_ids, list)

        if not is_list:
            user_ids = [user_ids]

        r = await self.invoke(
            raw.functions.contacts.DeleteContacts(
                id=[await self.resolve_peer(i) for i in user_ids]
            )
        )

        if not r.updates:
            return None

        users = types.List([types.User._parse(self, i) for i in r.users])

        return users if is_list else users[0]
