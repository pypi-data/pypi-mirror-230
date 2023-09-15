from typing import List

import pyroherd
from pyroherd import raw
from pyroherd import types
from pyroherd import utils


class GetNearbyChats:
    async def get_nearby_chats(
        self: "pyroherd.Client",
        latitude: float,
        longitude: float
    ) -> List["types.Chat"]:
        """Get nearby chats.

        Parameters:
            latitude (``float``):
                Latitude of the location.

            longitude (``float``):
                Longitude of the location.

        Returns:
            List of :obj:`~pyroherd.types.Chat`: On success, a list of nearby chats is returned.

        Example:
            .. code-block:: python

                chats = await app.get_nearby_chats(latitude, longitude)
                print(chats)
        """

        r = await self.invoke(
            raw.functions.contacts.GetLocated(
                geo_point=raw.types.InputGeoPoint(
                    lat=latitude,
                    long=longitude
                )
            )
        )

        if not r.updates:
            return []

        chats = types.List([types.Chat._parse_chat(self, chat) for chat in r.chats])
        peers = r.updates[0].peers

        for peer in peers:
            if isinstance(peer.peer, raw.types.PeerChannel):
                chat_id = utils.get_channel_id(peer.peer.channel_id)

                for chat in chats:
                    if chat.id == chat_id:
                        chat.distance = peer.distance
                        break

        return chats
