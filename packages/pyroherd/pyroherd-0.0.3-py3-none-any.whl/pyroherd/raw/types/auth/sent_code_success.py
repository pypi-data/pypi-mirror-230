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


class SentCodeSuccess(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.auth.SentCode`.

    Details:
        - Layer: ``158``
        - ID: ``2390FE44``

    Parameters:
        authorization: :obj:`auth.Authorization <pyroherd.raw.base.auth.Authorization>`

    See Also:
        This object can be returned by 6 methods:

        .. hlist::
            :columns: 2

            - :obj:`auth.SendCode <pyroherd.raw.functions.auth.SendCode>`
            - :obj:`auth.ResendCode <pyroherd.raw.functions.auth.ResendCode>`
            - :obj:`auth.ResetLoginEmail <pyroherd.raw.functions.auth.ResetLoginEmail>`
            - :obj:`account.SendChangePhoneCode <pyroherd.raw.functions.account.SendChangePhoneCode>`
            - :obj:`account.SendConfirmPhoneCode <pyroherd.raw.functions.account.SendConfirmPhoneCode>`
            - :obj:`account.SendVerifyPhoneCode <pyroherd.raw.functions.account.SendVerifyPhoneCode>`
    """

    __slots__: List[str] = ["authorization"]

    ID = 0x2390fe44
    QUALNAME = "types.auth.SentCodeSuccess"

    def __init__(self, *, authorization: "raw.base.auth.Authorization") -> None:
        self.authorization = authorization  # auth.Authorization

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "SentCodeSuccess":
        # No flags
        
        authorization = TLObject.read(b)
        
        return SentCodeSuccess(authorization=authorization)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.authorization.write())
        
        return b.getvalue()
