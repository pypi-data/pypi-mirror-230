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


class AttachMenuBots(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.AttachMenuBots`.

    Details:
        - Layer: ``143``
        - ID: ``3C4301C0``

    Parameters:
        hash: ``int`` ``64-bit``
        bots: List of :obj:`AttachMenuBot <pyroherd.raw.base.AttachMenuBot>`
        users: List of :obj:`User <pyroherd.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAttachMenuBots <pyroherd.raw.functions.messages.GetAttachMenuBots>`
    """

    __slots__: List[str] = ["hash", "bots", "users"]

    ID = 0x3c4301c0
    QUALNAME = "types.AttachMenuBots"

    def __init__(self, *, hash: int, bots: List["raw.base.AttachMenuBot"], users: List["raw.base.User"]) -> None:
        self.hash = hash  # long
        self.bots = bots  # Vector<AttachMenuBot>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AttachMenuBots":
        # No flags
        
        hash = Long.read(b)
        
        bots = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return AttachMenuBots(hash=hash, bots=bots, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.hash))
        
        b.write(Vector(self.bots))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
