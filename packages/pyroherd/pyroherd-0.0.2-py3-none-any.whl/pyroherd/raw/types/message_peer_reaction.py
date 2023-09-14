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


class MessagePeerReaction(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.MessagePeerReaction`.

    Details:
        - Layer: ``143``
        - ID: ``51B67EFF``

    Parameters:
        peer_id: :obj:`Peer <pyroherd.raw.base.Peer>`
        reaction: ``str``
        big (optional): ``bool``
        unread (optional): ``bool``
    """

    __slots__: List[str] = ["peer_id", "reaction", "big", "unread"]

    ID = 0x51b67eff
    QUALNAME = "types.MessagePeerReaction"

    def __init__(self, *, peer_id: "raw.base.Peer", reaction: str, big: Optional[bool] = None, unread: Optional[bool] = None) -> None:
        self.peer_id = peer_id  # Peer
        self.reaction = reaction  # string
        self.big = big  # flags.0?true
        self.unread = unread  # flags.1?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessagePeerReaction":
        
        flags = Int.read(b)
        
        big = True if flags & (1 << 0) else False
        unread = True if flags & (1 << 1) else False
        peer_id = TLObject.read(b)
        
        reaction = String.read(b)
        
        return MessagePeerReaction(peer_id=peer_id, reaction=reaction, big=big, unread=unread)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.big else 0
        flags |= (1 << 1) if self.unread else 0
        b.write(Int(flags))
        
        b.write(self.peer_id.write())
        
        b.write(String(self.reaction))
        
        return b.getvalue()
