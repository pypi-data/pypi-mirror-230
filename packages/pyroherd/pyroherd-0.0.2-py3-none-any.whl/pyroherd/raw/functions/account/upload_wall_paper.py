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


class UploadWallPaper(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``143``
        - ID: ``DD853661``

    Parameters:
        file: :obj:`InputFile <pyroherd.raw.base.InputFile>`
        mime_type: ``str``
        settings: :obj:`WallPaperSettings <pyroherd.raw.base.WallPaperSettings>`

    Returns:
        :obj:`WallPaper <pyroherd.raw.base.WallPaper>`
    """

    __slots__: List[str] = ["file", "mime_type", "settings"]

    ID = 0xdd853661
    QUALNAME = "functions.account.UploadWallPaper"

    def __init__(self, *, file: "raw.base.InputFile", mime_type: str, settings: "raw.base.WallPaperSettings") -> None:
        self.file = file  # InputFile
        self.mime_type = mime_type  # string
        self.settings = settings  # WallPaperSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UploadWallPaper":
        # No flags
        
        file = TLObject.read(b)
        
        mime_type = String.read(b)
        
        settings = TLObject.read(b)
        
        return UploadWallPaper(file=file, mime_type=mime_type, settings=settings)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.file.write())
        
        b.write(String(self.mime_type))
        
        b.write(self.settings.write())
        
        return b.getvalue()
