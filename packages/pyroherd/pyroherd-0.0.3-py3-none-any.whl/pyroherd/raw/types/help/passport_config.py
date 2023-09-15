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


class PassportConfig(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.help.PassportConfig`.

    Details:
        - Layer: ``158``
        - ID: ``A098D6AF``

    Parameters:
        hash: ``int`` ``32-bit``
        countries_langs: :obj:`DataJSON <pyroherd.raw.base.DataJSON>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPassportConfig <pyroherd.raw.functions.help.GetPassportConfig>`
    """

    __slots__: List[str] = ["hash", "countries_langs"]

    ID = 0xa098d6af
    QUALNAME = "types.help.PassportConfig"

    def __init__(self, *, hash: int, countries_langs: "raw.base.DataJSON") -> None:
        self.hash = hash  # int
        self.countries_langs = countries_langs  # DataJSON

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PassportConfig":
        # No flags
        
        hash = Int.read(b)
        
        countries_langs = TLObject.read(b)
        
        return PassportConfig(hash=hash, countries_langs=countries_langs)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.hash))
        
        b.write(self.countries_langs.write())
        
        return b.getvalue()
