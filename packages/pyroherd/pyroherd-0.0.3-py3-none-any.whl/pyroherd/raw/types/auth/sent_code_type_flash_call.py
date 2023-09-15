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


class SentCodeTypeFlashCall(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.auth.SentCodeType`.

    Details:
        - Layer: ``158``
        - ID: ``AB03C6D9``

    Parameters:
        pattern: ``str``
    """

    __slots__: List[str] = ["pattern"]

    ID = 0xab03c6d9
    QUALNAME = "types.auth.SentCodeTypeFlashCall"

    def __init__(self, *, pattern: str) -> None:
        self.pattern = pattern  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SentCodeTypeFlashCall":
        # No flags
        
        pattern = String.read(b)
        
        return SentCodeTypeFlashCall(pattern=pattern)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.pattern))
        
        return b.getvalue()
