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


class PeerNotifySettings(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.PeerNotifySettings`.

    Details:
        - Layer: ``158``
        - ID: ``A83B0426``

    Parameters:
        show_previews (optional): ``bool``
        silent (optional): ``bool``
        mute_until (optional): ``int`` ``32-bit``
        ios_sound (optional): :obj:`NotificationSound <pyroherd.raw.base.NotificationSound>`
        android_sound (optional): :obj:`NotificationSound <pyroherd.raw.base.NotificationSound>`
        other_sound (optional): :obj:`NotificationSound <pyroherd.raw.base.NotificationSound>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetNotifySettings <pyroherd.raw.functions.account.GetNotifySettings>`
    """

    __slots__: List[str] = ["show_previews", "silent", "mute_until", "ios_sound", "android_sound", "other_sound"]

    ID = 0xa83b0426
    QUALNAME = "types.PeerNotifySettings"

    def __init__(self, *, show_previews: Optional[bool] = None, silent: Optional[bool] = None, mute_until: Optional[int] = None, ios_sound: "raw.base.NotificationSound" = None, android_sound: "raw.base.NotificationSound" = None, other_sound: "raw.base.NotificationSound" = None) -> None:
        self.show_previews = show_previews  # flags.0?Bool
        self.silent = silent  # flags.1?Bool
        self.mute_until = mute_until  # flags.2?int
        self.ios_sound = ios_sound  # flags.3?NotificationSound
        self.android_sound = android_sound  # flags.4?NotificationSound
        self.other_sound = other_sound  # flags.5?NotificationSound

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PeerNotifySettings":
        
        flags = Int.read(b)
        
        show_previews = Bool.read(b) if flags & (1 << 0) else None
        silent = Bool.read(b) if flags & (1 << 1) else None
        mute_until = Int.read(b) if flags & (1 << 2) else None
        ios_sound = TLObject.read(b) if flags & (1 << 3) else None
        
        android_sound = TLObject.read(b) if flags & (1 << 4) else None
        
        other_sound = TLObject.read(b) if flags & (1 << 5) else None
        
        return PeerNotifySettings(show_previews=show_previews, silent=silent, mute_until=mute_until, ios_sound=ios_sound, android_sound=android_sound, other_sound=other_sound)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.show_previews is not None else 0
        flags |= (1 << 1) if self.silent is not None else 0
        flags |= (1 << 2) if self.mute_until is not None else 0
        flags |= (1 << 3) if self.ios_sound is not None else 0
        flags |= (1 << 4) if self.android_sound is not None else 0
        flags |= (1 << 5) if self.other_sound is not None else 0
        b.write(Int(flags))
        
        if self.show_previews is not None:
            b.write(Bool(self.show_previews))
        
        if self.silent is not None:
            b.write(Bool(self.silent))
        
        if self.mute_until is not None:
            b.write(Int(self.mute_until))
        
        if self.ios_sound is not None:
            b.write(self.ios_sound.write())
        
        if self.android_sound is not None:
            b.write(self.android_sound.write())
        
        if self.other_sound is not None:
            b.write(self.other_sound.write())
        
        return b.getvalue()
