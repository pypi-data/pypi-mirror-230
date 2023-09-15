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


class ReorderPinnedForumTopics(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``2950A18F``

    Parameters:
        channel: :obj:`InputChannel <pyroherd.raw.base.InputChannel>`
        order: List of ``int`` ``32-bit``
        force (optional): ``bool``

    Returns:
        :obj:`Updates <pyroherd.raw.base.Updates>`
    """

    __slots__: List[str] = ["channel", "order", "force"]

    ID = 0x2950a18f
    QUALNAME = "functions.channels.ReorderPinnedForumTopics"

    def __init__(self, *, channel: "raw.base.InputChannel", order: List[int], force: Optional[bool] = None) -> None:
        self.channel = channel  # InputChannel
        self.order = order  # Vector<int>
        self.force = force  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReorderPinnedForumTopics":
        
        flags = Int.read(b)
        
        force = True if flags & (1 << 0) else False
        channel = TLObject.read(b)
        
        order = TLObject.read(b, Int)
        
        return ReorderPinnedForumTopics(channel=channel, order=order, force=force)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.force else 0
        b.write(Int(flags))
        
        b.write(self.channel.write())
        
        b.write(Vector(self.order, Int))
        
        return b.getvalue()
