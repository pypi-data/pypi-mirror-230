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


class GetNotifyExceptions(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``53577479``

    Parameters:
        compare_sound (optional): ``bool``
        peer (optional): :obj:`InputNotifyPeer <pyroherd.raw.base.InputNotifyPeer>`

    Returns:
        :obj:`Updates <pyroherd.raw.base.Updates>`
    """

    __slots__: List[str] = ["compare_sound", "peer"]

    ID = 0x53577479
    QUALNAME = "functions.account.GetNotifyExceptions"

    def __init__(self, *, compare_sound: Optional[bool] = None, peer: "raw.base.InputNotifyPeer" = None) -> None:
        self.compare_sound = compare_sound  # flags.1?true
        self.peer = peer  # flags.0?InputNotifyPeer

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GetNotifyExceptions":
        
        flags = Int.read(b)
        
        compare_sound = True if flags & (1 << 1) else False
        peer = TLObject.read(b) if flags & (1 << 0) else None
        
        return GetNotifyExceptions(compare_sound=compare_sound, peer=peer)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.compare_sound else 0
        flags |= (1 << 0) if self.peer is not None else 0
        b.write(Int(flags))
        
        if self.peer is not None:
            b.write(self.peer.write())
        
        return b.getvalue()
