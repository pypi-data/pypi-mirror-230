import pyroherd
from pyroherd import raw, enums


class SearchGlobalCount:
    async def search_global_count(
        self: "pyroherd.Client",
        query: str = "",
        filter: "enums.MessagesFilter" = enums.MessagesFilter.EMPTY,
    ) -> int:
        """Get the count of messages resulting from a global search.

        If you want to get the actual messages, see :meth:`~pyroherd.Client.search_global`.

        Parameters:
            query (``str``, *optional*):
                Text query string.
                Use "@" to search for mentions.

            filter (:obj:`~pyroherd.enums.MessagesFilter`, *optional*):
                Pass a filter in order to search for specific kind of messages only:

        Returns:
            ``int``: On success, the messages count is returned.
        """
        r = await self.invoke(
            raw.functions.messages.SearchGlobal(
                q=query,
                filter=filter.value(),
                min_date=0,
                max_date=0,
                offset_rate=0,
                offset_peer=raw.types.InputPeerEmpty(),
                offset_id=0,
                limit=1
            )
        )

        if hasattr(r, "count"):
            return r.count
        else:
            return len(r.messages)
