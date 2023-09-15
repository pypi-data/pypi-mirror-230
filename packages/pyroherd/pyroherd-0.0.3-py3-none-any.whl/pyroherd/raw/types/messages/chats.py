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


class Chats(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.messages.Chats`.

    Details:
        - Layer: ``158``
        - ID: ``64FF9FD5``

    Parameters:
        chats: List of :obj:`Chat <pyroherd.raw.base.Chat>`

    See Also:
        This object can be returned by 7 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChats <pyroherd.raw.functions.messages.GetChats>`
            - :obj:`messages.GetCommonChats <pyroherd.raw.functions.messages.GetCommonChats>`
            - :obj:`messages.GetAllChats <pyroherd.raw.functions.messages.GetAllChats>`
            - :obj:`channels.GetChannels <pyroherd.raw.functions.channels.GetChannels>`
            - :obj:`channels.GetAdminedPublicChannels <pyroherd.raw.functions.channels.GetAdminedPublicChannels>`
            - :obj:`channels.GetLeftChannels <pyroherd.raw.functions.channels.GetLeftChannels>`
            - :obj:`channels.GetGroupsForDiscussion <pyroherd.raw.functions.channels.GetGroupsForDiscussion>`
    """

    __slots__: List[str] = ["chats"]

    ID = 0x64ff9fd5
    QUALNAME = "types.messages.Chats"

    def __init__(self, *, chats: List["raw.base.Chat"]) -> None:
        self.chats = chats  # Vector<Chat>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "Chats":
        # No flags
        
        chats = TLObject.read(b)
        
        return Chats(chats=chats)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.chats))
        
        return b.getvalue()
