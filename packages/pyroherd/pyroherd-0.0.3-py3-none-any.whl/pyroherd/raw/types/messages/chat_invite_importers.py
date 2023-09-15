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


class ChatInviteImporters(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.messages.ChatInviteImporters`.

    Details:
        - Layer: ``158``
        - ID: ``81B6B00A``

    Parameters:
        count: ``int`` ``32-bit``
        importers: List of :obj:`ChatInviteImporter <pyroherd.raw.base.ChatInviteImporter>`
        users: List of :obj:`User <pyroherd.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetChatInviteImporters <pyroherd.raw.functions.messages.GetChatInviteImporters>`
    """

    __slots__: List[str] = ["count", "importers", "users"]

    ID = 0x81b6b00a
    QUALNAME = "types.messages.ChatInviteImporters"

    def __init__(self, *, count: int, importers: List["raw.base.ChatInviteImporter"], users: List["raw.base.User"]) -> None:
        self.count = count  # int
        self.importers = importers  # Vector<ChatInviteImporter>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ChatInviteImporters":
        # No flags
        
        count = Int.read(b)
        
        importers = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return ChatInviteImporters(count=count, importers=importers, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.count))
        
        b.write(Vector(self.importers))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
