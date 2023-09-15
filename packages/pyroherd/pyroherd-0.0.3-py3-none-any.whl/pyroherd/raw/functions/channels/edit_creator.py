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


class EditCreator(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``8F38CD1F``

    Parameters:
        channel: :obj:`InputChannel <pyroherd.raw.base.InputChannel>`
        user_id: :obj:`InputUser <pyroherd.raw.base.InputUser>`
        password: :obj:`InputCheckPasswordSRP <pyroherd.raw.base.InputCheckPasswordSRP>`

    Returns:
        :obj:`Updates <pyroherd.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "user_id", "password"]

    ID = 0x8f38cd1f
    QUALNAME = "functions.channels.EditCreator"

    def __init__(self, *, channel: "raw.base.InputChannel", user_id: "raw.base.InputUser", password: "raw.base.InputCheckPasswordSRP") -> None:
        self.channel = channel  # InputChannel
        self.user_id = user_id  # InputUser
        self.password = password  # InputCheckPasswordSRP

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "EditCreator":
        # No flags
        
        channel = TLObject.read(b)
        
        user_id = TLObject.read(b)
        
        password = TLObject.read(b)
        
        return EditCreator(channel=channel, user_id=user_id, password=password)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.channel.write())
        
        b.write(self.user_id.write())
        
        b.write(self.password.write())
        
        return b.getvalue()
