#  Pyroherd - Telegram MTProto API Client Library for Python
#  Copyright (C) 2023-present OnTheHerd <https://github.com/OnTheHerd>
#
#  This file is part of Pyroherd.
#
#  Pyroherd is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyroherd is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyroherd.  If not, see <http://www.gnu.org/licenses/>.

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyroherd import raw
from pyroherd.raw.core import TLObject

Messages = Union[raw.types.messages.ChannelMessages, raw.types.messages.Messages, raw.types.messages.MessagesNotModified, raw.types.messages.MessagesSlice]


# noinspection PyRedeclaration
class Messages:  # type: ignore
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`messages.ChannelMessages <pyroherd.raw.types.messages.ChannelMessages>`
            - :obj:`messages.Messages <pyroherd.raw.types.messages.Messages>`
            - :obj:`messages.MessagesNotModified <pyroherd.raw.types.messages.MessagesNotModified>`
            - :obj:`messages.MessagesSlice <pyroherd.raw.types.messages.MessagesSlice>`

    See Also:
        This object can be returned by 13 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessages <pyroherd.raw.functions.messages.GetMessages>`
            - :obj:`messages.GetHistory <pyroherd.raw.functions.messages.GetHistory>`
            - :obj:`messages.Search <pyroherd.raw.functions.messages.Search>`
            - :obj:`messages.SearchGlobal <pyroherd.raw.functions.messages.SearchGlobal>`
            - :obj:`messages.GetUnreadMentions <pyroherd.raw.functions.messages.GetUnreadMentions>`
            - :obj:`messages.GetRecentLocations <pyroherd.raw.functions.messages.GetRecentLocations>`
            - :obj:`messages.GetScheduledHistory <pyroherd.raw.functions.messages.GetScheduledHistory>`
            - :obj:`messages.GetScheduledMessages <pyroherd.raw.functions.messages.GetScheduledMessages>`
            - :obj:`messages.GetReplies <pyroherd.raw.functions.messages.GetReplies>`
            - :obj:`messages.GetUnreadReactions <pyroherd.raw.functions.messages.GetUnreadReactions>`
            - :obj:`messages.SearchSentMedia <pyroherd.raw.functions.messages.SearchSentMedia>`
            - :obj:`channels.GetMessages <pyroherd.raw.functions.channels.GetMessages>`
            - :obj:`stats.GetMessagePublicForwards <pyroherd.raw.functions.stats.GetMessagePublicForwards>`
    """

    QUALNAME = "pyroherd.raw.base.messages.Messages"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/messages")
