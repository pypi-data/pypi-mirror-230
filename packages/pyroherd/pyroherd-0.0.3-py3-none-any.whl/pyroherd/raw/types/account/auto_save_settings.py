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


class AutoSaveSettings(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.account.AutoSaveSettings`.

    Details:
        - Layer: ``158``
        - ID: ``4C3E069D``

    Parameters:
        users_settings: :obj:`AutoSaveSettings <pyroherd.raw.base.AutoSaveSettings>`
        chats_settings: :obj:`AutoSaveSettings <pyroherd.raw.base.AutoSaveSettings>`
        broadcasts_settings: :obj:`AutoSaveSettings <pyroherd.raw.base.AutoSaveSettings>`
        exceptions: List of :obj:`AutoSaveException <pyroherd.raw.base.AutoSaveException>`
        chats: List of :obj:`Chat <pyroherd.raw.base.Chat>`
        users: List of :obj:`User <pyroherd.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAutoSaveSettings <pyroherd.raw.functions.account.GetAutoSaveSettings>`
    """

    __slots__: List[str] = ["users_settings", "chats_settings", "broadcasts_settings", "exceptions", "chats", "users"]

    ID = 0x4c3e069d
    QUALNAME = "types.account.AutoSaveSettings"

    def __init__(self, *, users_settings: "raw.base.AutoSaveSettings", chats_settings: "raw.base.AutoSaveSettings", broadcasts_settings: "raw.base.AutoSaveSettings", exceptions: List["raw.base.AutoSaveException"], chats: List["raw.base.Chat"], users: List["raw.base.User"]) -> None:
        self.users_settings = users_settings  # AutoSaveSettings
        self.chats_settings = chats_settings  # AutoSaveSettings
        self.broadcasts_settings = broadcasts_settings  # AutoSaveSettings
        self.exceptions = exceptions  # Vector<AutoSaveException>
        self.chats = chats  # Vector<Chat>
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AutoSaveSettings":
        # No flags
        
        users_settings = TLObject.read(b)
        
        chats_settings = TLObject.read(b)
        
        broadcasts_settings = TLObject.read(b)
        
        exceptions = TLObject.read(b)
        
        chats = TLObject.read(b)
        
        users = TLObject.read(b)
        
        return AutoSaveSettings(users_settings=users_settings, chats_settings=chats_settings, broadcasts_settings=broadcasts_settings, exceptions=exceptions, chats=chats, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.users_settings.write())
        
        b.write(self.chats_settings.write())
        
        b.write(self.broadcasts_settings.write())
        
        b.write(Vector(self.exceptions))
        
        b.write(Vector(self.chats))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
