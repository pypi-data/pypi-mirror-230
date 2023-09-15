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


class GlobalPrivacySettings(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.GlobalPrivacySettings`.

    Details:
        - Layer: ``158``
        - ID: ``BEA2F424``

    Parameters:
        archive_and_mute_new_noncontact_peers (optional): ``bool``

    See Also:
        This object can be returned by 2 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetGlobalPrivacySettings <pyroherd.raw.functions.account.GetGlobalPrivacySettings>`
            - :obj:`account.SetGlobalPrivacySettings <pyroherd.raw.functions.account.SetGlobalPrivacySettings>`
    """

    __slots__: List[str] = ["archive_and_mute_new_noncontact_peers"]

    ID = 0xbea2f424
    QUALNAME = "types.GlobalPrivacySettings"

    def __init__(self, *, archive_and_mute_new_noncontact_peers: Optional[bool] = None) -> None:
        self.archive_and_mute_new_noncontact_peers = archive_and_mute_new_noncontact_peers  # flags.0?Bool

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "GlobalPrivacySettings":
        
        flags = Int.read(b)
        
        archive_and_mute_new_noncontact_peers = Bool.read(b) if flags & (1 << 0) else None
        return GlobalPrivacySettings(archive_and_mute_new_noncontact_peers=archive_and_mute_new_noncontact_peers)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.archive_and_mute_new_noncontact_peers is not None else 0
        b.write(Int(flags))
        
        if self.archive_and_mute_new_noncontact_peers is not None:
            b.write(Bool(self.archive_and_mute_new_noncontact_peers))
        
        return b.getvalue()
