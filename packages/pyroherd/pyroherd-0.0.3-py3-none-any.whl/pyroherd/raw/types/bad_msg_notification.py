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


class BadMsgNotification(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.BadMsgNotification`.

    Details:
        - Layer: ``158``
        - ID: ``A7EFF811``

    Parameters:
        bad_msg_id: ``int`` ``64-bit``
        bad_msg_seqno: ``int`` ``32-bit``
        error_code: ``int`` ``32-bit``
    """

    __slots__: List[str] = ["bad_msg_id", "bad_msg_seqno", "error_code"]

    ID = 0xa7eff811
    QUALNAME = "types.BadMsgNotification"

    def __init__(self, *, bad_msg_id: int, bad_msg_seqno: int, error_code: int) -> None:
        self.bad_msg_id = bad_msg_id  # long
        self.bad_msg_seqno = bad_msg_seqno  # int
        self.error_code = error_code  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BadMsgNotification":
        # No flags
        
        bad_msg_id = Long.read(b)
        
        bad_msg_seqno = Int.read(b)
        
        error_code = Int.read(b)
        
        return BadMsgNotification(bad_msg_id=bad_msg_id, bad_msg_seqno=bad_msg_seqno, error_code=error_code)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(Long(self.bad_msg_id))
        
        b.write(Int(self.bad_msg_seqno))
        
        b.write(Int(self.error_code))
        
        return b.getvalue()
