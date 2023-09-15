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


class InputBotInlineMessageID64(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.InputBotInlineMessageID`.

    Details:
        - Layer: ``158``
        - ID: ``B6D915D7``

    Parameters:
        dc_id: ``int`` ``32-bit``
        owner_id: ``int`` ``64-bit``
        id: ``int`` ``32-bit``
        access_hash: ``int`` ``64-bit``
    """

    __slots__: List[str] = ["dc_id", "owner_id", "id", "access_hash"]

    ID = 0xb6d915d7
    QUALNAME = "types.InputBotInlineMessageID64"

    def __init__(self, *, dc_id: int, owner_id: int, id: int, access_hash: int) -> None:
        self.dc_id = dc_id  # int
        self.owner_id = owner_id  # long
        self.id = id  # int
        self.access_hash = access_hash  # long

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InputBotInlineMessageID64":
        # No flags
        
        dc_id = Int.read(b)
        
        owner_id = Long.read(b)
        
        id = Int.read(b)
        
        access_hash = Long.read(b)
        
        return InputBotInlineMessageID64(dc_id=dc_id, owner_id=owner_id, id=id, access_hash=access_hash)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.dc_id))
        
        b.write(Long(self.owner_id))
        
        b.write(Int(self.id))
        
        b.write(Long(self.access_hash))
        
        return b.getvalue()
