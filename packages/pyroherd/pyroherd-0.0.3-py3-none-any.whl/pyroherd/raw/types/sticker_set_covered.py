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


class StickerSetCovered(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.StickerSetCovered`.

    Details:
        - Layer: ``158``
        - ID: ``6410A5D2``

    Parameters:
        set: :obj:`StickerSet <pyroherd.raw.base.StickerSet>`
        cover: :obj:`Document <pyroherd.raw.base.Document>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetAttachedStickers <pyroherd.raw.functions.messages.GetAttachedStickers>`
    """

    __slots__: List[str] = ["set", "cover"]

    ID = 0x6410a5d2
    QUALNAME = "types.StickerSetCovered"

    def __init__(self, *, set: "raw.base.StickerSet", cover: "raw.base.Document") -> None:
        self.set = set  # StickerSet
        self.cover = cover  # Document

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "StickerSetCovered":
        # No flags
        
        set = TLObject.read(b)
        
        cover = TLObject.read(b)
        
        return StickerSetCovered(set=set, cover=cover)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.set.write())
        
        b.write(self.cover.write())
        
        return b.getvalue()
