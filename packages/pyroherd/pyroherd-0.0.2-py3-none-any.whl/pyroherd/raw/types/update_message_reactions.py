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


class UpdateMessageReactions(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``143``
        - ID: ``154798C3``

    Parameters:
        peer: :obj:`Peer <pyroherd.raw.base.Peer>`
        msg_id: ``int`` ``32-bit``
        reactions: :obj:`MessageReactions <pyroherd.raw.base.MessageReactions>`
    """

    __slots__: List[str] = ["peer", "msg_id", "reactions"]

    ID = 0x154798c3
    QUALNAME = "types.UpdateMessageReactions"

    def __init__(self, *, peer: "raw.base.Peer", msg_id: int, reactions: "raw.base.MessageReactions") -> None:
        self.peer = peer  # Peer
        self.msg_id = msg_id  # int
        self.reactions = reactions  # MessageReactions

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateMessageReactions":
        # No flags
        
        peer = TLObject.read(b)
        
        msg_id = Int.read(b)
        
        reactions = TLObject.read(b)
        
        return UpdateMessageReactions(peer=peer, msg_id=msg_id, reactions=reactions)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(Int(self.msg_id))
        
        b.write(self.reactions.write())
        
        return b.getvalue()
