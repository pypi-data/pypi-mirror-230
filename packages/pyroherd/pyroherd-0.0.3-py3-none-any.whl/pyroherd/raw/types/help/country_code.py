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


class CountryCode(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.help.CountryCode`.

    Details:
        - Layer: ``158``
        - ID: ``4203C5EF``

    Parameters:
        country_code: ``str``
        prefixes (optional): List of ``str``
        patterns (optional): List of ``str``
    """

    __slots__: List[str] = ["country_code", "prefixes", "patterns"]

    ID = 0x4203c5ef
    QUALNAME = "types.help.CountryCode"

    def __init__(self, *, country_code: str, prefixes: Optional[List[str]] = None, patterns: Optional[List[str]] = None) -> None:
        self.country_code = country_code  # string
        self.prefixes = prefixes  # flags.0?Vector<string>
        self.patterns = patterns  # flags.1?Vector<string>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "CountryCode":
        
        flags = Int.read(b)
        
        country_code = String.read(b)
        
        prefixes = TLObject.read(b, String) if flags & (1 << 0) else []
        
        patterns = TLObject.read(b, String) if flags & (1 << 1) else []
        
        return CountryCode(country_code=country_code, prefixes=prefixes, patterns=patterns)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.prefixes else 0
        flags |= (1 << 1) if self.patterns else 0
        b.write(Int(flags))
        
        b.write(String(self.country_code))
        
        if self.prefixes:
            b.write(Vector(self.prefixes, String))
        
        if self.patterns:
            b.write(Vector(self.patterns, String))
        
        return b.getvalue()
