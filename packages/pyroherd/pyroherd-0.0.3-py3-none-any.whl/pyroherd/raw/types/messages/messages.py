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

from io import BytesIO

from pyroherd.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyroherd.raw.core import TLObject
from pyroherd import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class Messages(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.messages.Messages`.

    Details:
        - Layer: ``158``
        - ID: ``8C718E87``

    Parameters:
        messages: List of :obj:`Message <pyroherd.raw.base.Message>`
        chats: List of :obj:`Chat <pyroherd.raw.base.Chat>`
        users: List of :obj:`User <pyroherd.raw.base.User>`

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

    __slots__: List[str] = ["messages", "chats", "users"]

    ID = 0x8c718e87
    QUALNAME = "types.messages.Messages"

    def __init__(self, *, messages: List["raw.base.Message"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.messages = messages  # Vector<Message>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "Messages":
        # No flags
        
        messages = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return Messages(messages=messages, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.messages))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
