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


class ExportedChatlistInvite(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.ExportedChatlistInvite`.

    Details:
        - Layer: ``158``
        - ID: ``C5181AC``

    Parameters:
        title: ``str``
        url: ``str``
        peers: List of :obj:`Peer <pyroherd.raw.base.Peer>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`chatlists.EditExportedInvite <pyroherd.raw.functions.chatlists.EditExportedInvite>`
    """

    __slots__: List[str] = ["title", "url", "peers"]

    ID = 0xc5181ac
    QUALNAME = "types.ExportedChatlistInvite"

    def __init__(self, *, title: str, url: str, peers: List["raw.base.Peer"]) -> None:
        self.title = title  # string
        self.url = url  # string
        self.peers = peers  # Vector<Peer>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ExportedChatlistInvite":
        
        flags = Int.read(b)
        
        title = String.read(b)
        
        url = String.read(b)
        
        peers = TLObject.read(b)
        
        return ExportedChatlistInvite(title=title, url=url, peers=peers)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        
        b.write(Int(flags))
        
        b.write(String(self.title))
        
        b.write(String(self.url))
        
        b.write(Vector(self.peers))
        
        return b.getvalue()
