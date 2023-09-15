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


class WallPaperNoFile(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.WallPaper`.

    Details:
        - Layer: ``158``
        - ID: ``E0804116``

    Parameters:
        id: ``int`` ``64-bit``
        default (optional): ``bool``
        dark (optional): ``bool``
        settings (optional): :obj:`WallPaperSettings <pyroherd.raw.base.WallPaperSettings>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetWallPaper <pyroherd.raw.functions.account.GetWallPaper>`
            - :obj:`account.UploadWallPaper <pyroherd.raw.functions.account.UploadWallPaper>`
            - :obj:`account.GetMultiWallPapers <pyroherd.raw.functions.account.GetMultiWallPapers>`
    """

    __slots__: List[str] = ["id", "default", "dark", "settings"]

    ID = 0xe0804116
    QUALNAME = "types.WallPaperNoFile"

    def __init__(self, *, id: int, default: Optional[bool] = None, dark: Optional[bool] = None, settings: "raw.base.WallPaperSettings" = None) -> None:
        self.id = id  # long
        self.default = default  # flags.1?true
        self.dark = dark  # flags.4?true
        self.settings = settings  # flags.2?WallPaperSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "WallPaperNoFile":
        
        id = Long.read(b)
        
        flags = Int.read(b)
        
        default = True if flags & (1 << 1) else False
        dark = True if flags & (1 << 4) else False
        settings = TLObject.read(b) if flags & (1 << 2) else None
        
        return WallPaperNoFile(id=id, default=default, dark=dark, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        
        b.write(Long(self.id))
        flags = 0
        flags |= (1 << 1) if self.default else 0
        flags |= (1 << 4) if self.dark else 0
        flags |= (1 << 2) if self.settings is not None else 0
        b.write(Int(flags))
        
        if self.settings is not None:
            b.write(self.settings.write())
        
        return b.getvalue()
