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


class PhotoSizeProgressive(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.PhotoSize`.

    Details:
        - Layer: ``158``
        - ID: ``FA3EFB95``

    Parameters:
        type: ``str``
        w: ``int`` ``32-bit``
        h: ``int`` ``32-bit``
        sizes: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["type", "w", "h", "sizes"]

    ID = 0xfa3efb95
    QUALNAME = "types.PhotoSizeProgressive"

    def __init__(self, *, type: str, w: int, h: int, sizes: List[int]) -> None:
        self.type = type  # string
        self.w = w  # int
        self.h = h  # int
        self.sizes = sizes  # Vector<int>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PhotoSizeProgressive":
        # No flags
        
        type = String.read(b)
        
        w = Int.read(b)
        
        h = Int.read(b)
        
        sizes = TLObject.read(b, Int)
        
        return PhotoSizeProgressive(type=type, w=w, h=h, sizes=sizes)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.type))
        
        b.write(Int(self.w))
        
        b.write(Int(self.h))
        
        b.write(Vector(self.sizes, Int))
        
        return b.getvalue()
