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


class MessageMediaGeoLive(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.MessageMedia`.

    Details:
        - Layer: ``158``
        - ID: ``B940C666``

    Parameters:
        geo: :obj:`GeoPoint <pyroherd.raw.base.GeoPoint>`
        period: ``int`` ``32-bit``
        heading (optional): ``int`` ``32-bit``
        proximity_notification_radius (optional): ``int`` ``32-bit``

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyroherd.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyroherd.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyroherd.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["geo", "period", "heading", "proximity_notification_radius"]

    ID = 0xb940c666
    QUALNAME = "types.MessageMediaGeoLive"

    def __init__(self, *, geo: "raw.base.GeoPoint", period: int, heading: Optional[int] = None, proximity_notification_radius: Optional[int] = None) -> None:
        self.geo = geo  # GeoPoint
        self.period = period  # int
        self.heading = heading  # flags.0?int
        self.proximity_notification_radius = proximity_notification_radius  # flags.1?int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaGeoLive":
        
        flags = Int.read(b)
        
        geo = TLObject.read(b)
        
        heading = Int.read(b) if flags & (1 << 0) else None
        period = Int.read(b)
        
        proximity_notification_radius = Int.read(b) if flags & (1 << 1) else None
        return MessageMediaGeoLive(geo=geo, period=period, heading=heading, proximity_notification_radius=proximity_notification_radius)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.heading is not None else 0
        flags |= (1 << 1) if self.proximity_notification_radius is not None else 0
        b.write(Int(flags))
        
        b.write(self.geo.write())
        
        if self.heading is not None:
            b.write(Int(self.heading))
        
        b.write(Int(self.period))
        
        if self.proximity_notification_radius is not None:
            b.write(Int(self.proximity_notification_radius))
        
        return b.getvalue()
