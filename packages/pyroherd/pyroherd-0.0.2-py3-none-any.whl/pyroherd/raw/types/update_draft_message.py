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


class UpdateDraftMessage(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.Update`.

    Details:
        - Layer: ``143``
        - ID: ``EE2BB969``

    Parameters:
        peer: :obj:`Peer <pyroherd.raw.base.Peer>`
        draft: :obj:`DraftMessage <pyroherd.raw.base.DraftMessage>`
    """

    __slots__: List[str] = ["peer", "draft"]

    ID = 0xee2bb969
    QUALNAME = "types.UpdateDraftMessage"

    def __init__(self, *, peer: "raw.base.Peer", draft: "raw.base.DraftMessage") -> None:
        self.peer = peer  # Peer
        self.draft = draft  # DraftMessage

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateDraftMessage":
        # No flags
        
        peer = TLObject.read(b)
        
        draft = TLObject.read(b)
        
        return UpdateDraftMessage(peer=peer, draft=draft)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.peer.write())
        
        b.write(self.draft.write())
        
        return b.getvalue()
