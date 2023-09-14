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


class UpdateChannelReadMessagesContents(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``143``
        - ID: ``44BDD535``

    Parameters:
        channel_id: ``int`` ``64-bit``
        messages: List of ``int`` ``32-bit``
    """

    __slots__: List[str] = ["channel_id", "messages"]

    ID = 0x44bdd535
    QUALNAME = "types.UpdateChannelReadMessagesContents"

    def __init__(self, *, channel_id: int, messages: List[int]) -> None:
        self.channel_id = channel_id  # long
        self.messages = messages  # Vector<int>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateChannelReadMessagesContents":
        # No flags
        
        channel_id = Long.read(b)
        
        messages = TLObject.read(b, Int)
        
        return UpdateChannelReadMessagesContents(channel_id=channel_id, messages=messages)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.channel_id))
        
        b.write(Vector(self.messages, Int))
        
        return b.getvalue()
