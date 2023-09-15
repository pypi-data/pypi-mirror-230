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


class MessageMediaGeo(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.MessageMedia`.

    Details:
        - Layer: ``158``
        - ID: ``56E0D474``

    Parameters:
        geo: :obj:`GeoPoint <pyroherd.raw.base.GeoPoint>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyroherd.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyroherd.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyroherd.raw.functions.messages.UploadImportedMedia>`
    """

    __slots__: List[str] = ["geo"]

    ID = 0x56e0d474
    QUALNAME = "types.MessageMediaGeo"

    def __init__(self, *, geo: "raw.base.GeoPoint") -> None:
        self.geo = geo  # GeoPoint

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageMediaGeo":
        # No flags
        
        geo = TLObject.read(b)
        
        return MessageMediaGeo(geo=geo)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.geo.write())
        
        return b.getvalue()
