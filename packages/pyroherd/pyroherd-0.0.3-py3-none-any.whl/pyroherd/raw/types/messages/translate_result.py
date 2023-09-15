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


class TranslateResult(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.messages.TranslatedText`.

    Details:
        - Layer: ``158``
        - ID: ``33DB32F8``

    Parameters:
        result: List of :obj:`TextWithEntities <pyroherd.raw.base.TextWithEntities>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.TranslateText <pyroherd.raw.functions.messages.TranslateText>`
    """

    __slots__: List[str] = ["result"]

    ID = 0x33db32f8
    QUALNAME = "types.messages.TranslateResult"

    def __init__(self, *, result: List["raw.base.TextWithEntities"]) -> None:
        self.result = result  # Vector<TextWithEntities>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "TranslateResult":
        # No flags
        
        result = TLObject.read(b)
        
        return TranslateResult(result=result)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Vector(self.result))
        
        return b.getvalue()
