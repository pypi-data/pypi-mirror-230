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


class GetAttachMenuBot(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``77216192``

    Parameters:
        bot: :obj:`InputUser <pyroherd.raw.base.InputUser>`

    Returns:
        :obj:`AttachMenuBotsBot <pyroherd.raw.base.AttachMenuBotsBot>`
    """

    __slots__: List[str] = ["bot"]

    ID = 0x77216192
    QUALNAME = "functions.messages.GetAttachMenuBot"

    def __init__(self, *, bot: "raw.base.InputUser") -> None:
        self.bot = bot  # InputUser

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetAttachMenuBot":
        # No flags
        
        bot = TLObject.read(b)
        
        return GetAttachMenuBot(bot=bot)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.bot.write())
        
        return b.getvalue()
