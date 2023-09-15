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


class PeerSettings(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.messages.PeerSettings`.

    Details:
        - Layer: ``158``
        - ID: ``6880B94D``

    Parameters:
        settings: :obj:`PeerSettings <pyroherd.raw.base.PeerSettings>`
        chats: List of :obj:`Chat <pyroherd.raw.base.Chat>`
        users: List of :obj:`User <pyroherd.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetPeerSettings <pyroherd.raw.functions.messages.GetPeerSettings>`
    """

    __slots__: List[str] = ["settings", "chats", "users"]

    ID = 0x6880b94d
    QUALNAME = "types.messages.PeerSettings"

    def __init__(self, *, settings: "raw.base.PeerSettings", chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.settings = settings  # PeerSettings
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PeerSettings":
        # No flags
        
        settings = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return PeerSettings(settings=settings, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.settings.write())
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
