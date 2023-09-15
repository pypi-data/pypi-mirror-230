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


class PageBlockTable(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.PageBlock`.

    Details:
        - Layer: ``158``
        - ID: ``BF4DEA82``

    Parameters:
        title: :obj:`RichText <pyroherd.raw.base.RichText>`
        rows: List of :obj:`PageTableRow <pyroherd.raw.base.PageTableRow>`
        bordered (optional): ``bool``
        striped (optional): ``bool``
    """

    __slots__: List[str] = ["title", "rows", "bordered", "striped"]

    ID = 0xbf4dea82
    QUALNAME = "types.PageBlockTable"

    def __init__(self, *, title: "raw.base.RichText", rows: List["raw.base.PageTableRow"], bordered: Optional[bool] = None, striped: Optional[bool] = None) -> None:
        self.title = title  # RichText
        self.rows = rows  # Vector<PageTableRow>
        self.bordered = bordered  # flags.0?true
        self.striped = striped  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PageBlockTable":
        
        flags = Int.read(b)
        
        bordered = True if flags & (1 << 0) else False
        striped = True if flags & (1 << 1) else False
        title = TLObject.read(b)
        
        rows = TLObject.read(b)
        
        return PageBlockTable(title=title, rows=rows, bordered=bordered, striped=striped)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.bordered else 0
        flags |= (1 << 1) if self.striped else 0
        b.write(Int(flags))
        
        b.write(self.title.write())
        
        b.write(Vector(self.rows))
        
        return b.getvalue()
