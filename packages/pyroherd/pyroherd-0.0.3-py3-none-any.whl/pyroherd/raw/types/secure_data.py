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


class SecureData(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.SecureData`.

    Details:
        - Layer: ``158``
        - ID: ``8AEABEC3``

    Parameters:
        data: ``bytes``
        data_hash: ``bytes``
        secret: ``bytes``
    """

    __slots__: List[str] = ["data", "data_hash", "secret"]

    ID = 0x8aeabec3
    QUALNAME = "types.SecureData"

    def __init__(self, *, data: bytes, data_hash: bytes, secret: bytes) -> None:
        self.data = data  # bytes
        self.data_hash = data_hash  # bytes
        self.secret = secret  # bytes

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SecureData":
        # No flags
        
        data = Bytes.read(b)
        
        data_hash = Bytes.read(b)
        
        secret = Bytes.read(b)
        
        return SecureData(data=data, data_hash=data_hash, secret=secret)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Bytes(self.data))
        
        b.write(Bytes(self.data_hash))
        
        b.write(Bytes(self.secret))
        
        return b.getvalue()
