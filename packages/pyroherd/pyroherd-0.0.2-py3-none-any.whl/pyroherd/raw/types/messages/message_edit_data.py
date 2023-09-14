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


class MessageEditData(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.messages.MessageEditData`.

    Details:
        - Layer: ``143``
        - ID: ``26B5DDE6``

    Parameters:
        caption (optional): ``bool``

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetMessageEditData <pyroherd.raw.functions.messages.GetMessageEditData>`
    """

    __slots__: List[str] = ["caption"]

    ID = 0x26b5dde6
    QUALNAME = "types.messages.MessageEditData"

    def __init__(self, *, caption: Optional[bool] = None) -> None:
        self.caption = caption  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageEditData":
        
        flags = Int.read(b)
        
        caption = True if flags & (1 << 0) else False
        return MessageEditData(caption=caption)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.caption else 0
        b.write(Int(flags))
        
        return b.getvalue()
