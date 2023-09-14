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


class UpdateStickerSetsOrder(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``143``
        - ID: ``BB2D201``

    Parameters:
        order: List of ``int`` ``64-bit``
        masks (optional): ``bool``
    """

    __slots__: List[str] = ["order", "masks"]

    ID = 0xbb2d201
    QUALNAME = "types.UpdateStickerSetsOrder"

    def __init__(self, *, order: List[int], masks: Optional[bool] = None) -> None:
        self.order = order  # Vector<long>
        self.masks = masks  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateStickerSetsOrder":
        
        flags = Int.read(b)
        
        masks = True if flags & (1 << 0) else False
        order = TLObject.read(b, Long)
        
        return UpdateStickerSetsOrder(order=order, masks=masks)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.masks else 0
        b.write(Int(flags))
        
        b.write(Vector(self.order, Long))
        
        return b.getvalue()
