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


class LangPackStringDeleted(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.LangPackString`.

    Details:
        - Layer: ``158``
        - ID: ``2979EEB2``

    Parameters:
        key: ``str``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`langpack.GetStrings <pyroherd.raw.functions.langpack.GetStrings>`
    """

    __slots__: List[str] = ["key"]

    ID = 0x2979eeb2
    QUALNAME = "types.LangPackStringDeleted"

    def __init__(self, *, key: str) -> None:
        self.key = key  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "LangPackStringDeleted":
        # No flags
        
        key = String.read(b)
        
        return LangPackStringDeleted(key=key)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.key))
        
        return b.getvalue()
