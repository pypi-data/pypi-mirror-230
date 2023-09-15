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


class UpdateBotInlineQuery(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``158``
        - ID: ``496F379C``

    Parameters:
        query_id: ``int`` ``64-bit``
        user_id: ``int`` ``64-bit``
        query: ``str``
        offset: ``str``
        geo (optional): :obj:`GeoPoint <pyroherd.raw.base.GeoPoint>`
        peer_type (optional): :obj:`InlineQueryPeerType <pyroherd.raw.base.InlineQueryPeerType>`
    """

    __slots__: List[str] = ["query_id", "user_id", "query", "offset", "geo", "peer_type"]

    ID = 0x496f379c
    QUALNAME = "types.UpdateBotInlineQuery"

    def __init__(self, *, query_id: int, user_id: int, query: str, offset: str, geo: "raw.base.GeoPoint" = None, peer_type: "raw.base.InlineQueryPeerType" = None) -> None:
        self.query_id = query_id  # long
        self.user_id = user_id  # long
        self.query = query  # string
        self.offset = offset  # string
        self.geo = geo  # flags.0?GeoPoint
        self.peer_type = peer_type  # flags.1?InlineQueryPeerType

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateBotInlineQuery":
        
        flags = Int.read(b)
        
        query_id = Long.read(b)
        
        user_id = Long.read(b)
        
        query = String.read(b)
        
        geo = TLObject.read(b) if flags & (1 << 0) else None
        
        peer_type = TLObject.read(b) if flags & (1 << 1) else None
        
        offset = String.read(b)
        
        return UpdateBotInlineQuery(query_id=query_id, user_id=user_id, query=query, offset=offset, geo=geo, peer_type=peer_type)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.geo is not None else 0
        flags |= (1 << 1) if self.peer_type is not None else 0
        b.write(Int(flags))
        
        b.write(Long(self.query_id))
        
        b.write(Long(self.user_id))
        
        b.write(String(self.query))
        
        if self.geo is not None:
            b.write(self.geo.write())
        
        if self.peer_type is not None:
            b.write(self.peer_type.write())
        
        b.write(String(self.offset))
        
        return b.getvalue()
