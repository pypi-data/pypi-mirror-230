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


class MessageInteractionCounters(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.MessageInteractionCounters`.

    Details:
        - Layer: ``158``
        - ID: ``AD4FC9BD``

    Parameters:
        msg_id: ``int`` ``32-bit``
        views: ``int`` ``32-bit``
        forwards: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["msg_id", "views", "forwards"]

    ID = 0xad4fc9bd
    QUALNAME = "types.MessageInteractionCounters"

    def __init__(self, *, msg_id: int, views: int, forwards: int) -> None:
        self.msg_id = msg_id  # int
        self.views = views  # int
        self.forwards = forwards  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageInteractionCounters":
        # No flags
        
        msg_id = Int.read(b)
        
        views = Int.read(b)
        
        forwards = Int.read(b)
        
        return MessageInteractionCounters(msg_id=msg_id, views=views, forwards=forwards)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Int(self.msg_id))
        
        b.write(Int(self.views))
        
        b.write(Int(self.forwards))
        
        return b.getvalue()
