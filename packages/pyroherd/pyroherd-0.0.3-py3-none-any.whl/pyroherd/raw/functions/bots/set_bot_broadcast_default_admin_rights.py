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


class SetBotBroadcastDefaultAdminRights(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``788464E1``

    Parameters:
        admin_rights: :obj:`ChatAdminRights <pyroherd.raw.base.ChatAdminRights>`

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["admin_rights"]

    ID = 0x788464e1
    QUALNAME = "functions.bots.SetBotBroadcastDefaultAdminRights"

    def __init__(self, *, admin_rights: "raw.base.ChatAdminRights") -> None:
        self.admin_rights = admin_rights  # ChatAdminRights

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SetBotBroadcastDefaultAdminRights":
        # No flags
        
        admin_rights = TLObject.read(b)
        
        return SetBotBroadcastDefaultAdminRights(admin_rights=admin_rights)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.admin_rights.write())
        
        return b.getvalue()
