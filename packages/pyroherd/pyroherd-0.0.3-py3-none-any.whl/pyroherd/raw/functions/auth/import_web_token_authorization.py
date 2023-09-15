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


class ImportWebTokenAuthorization(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``2DB873A9``

    Parameters:
        api_id: ``int`` ``32-bit``
        api_hash: ``str``
        web_auth_token: ``str``

    Returns:
        :obj:`auth.Authorization <pyroherd.raw.base.auth.Authorization>`
    """

    __slots__: List[str] = ["api_id", "api_hash", "web_auth_token"]

    ID = 0x2db873a9
    QUALNAME = "functions.auth.ImportWebTokenAuthorization"

    def __init__(self, *, api_id: int, api_hash: str, web_auth_token: str) -> None:
        self.api_id = api_id  # int
        self.api_hash = api_hash  # string
        self.web_auth_token = web_auth_token  # string

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ImportWebTokenAuthorization":
        # No flags
        
        api_id = Int.read(b)
        
        api_hash = String.read(b)
        
        web_auth_token = String.read(b)
        
        return ImportWebTokenAuthorization(api_id=api_id, api_hash=api_hash, web_auth_token=web_auth_token)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.api_id))
        
        b.write(String(self.api_hash))
        
        b.write(String(self.web_auth_token))
        
        return b.getvalue()
