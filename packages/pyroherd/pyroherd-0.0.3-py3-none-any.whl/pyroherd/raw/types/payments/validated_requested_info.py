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


class ValidatedRequestedInfo(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.payments.ValidatedRequestedInfo`.

    Details:
        - Layer: ``158``
        - ID: ``D1451883``

    Parameters:
        id (optional): ``str``
        shipping_options (optional): List of :obj:`ShippingOption <pyroherd.raw.base.ShippingOption>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`payments.ValidateRequestedInfo <pyroherd.raw.functions.payments.ValidateRequestedInfo>`
    """

    __slots__: List[str] = ["id", "shipping_options"]

    ID = 0xd1451883
    QUALNAME = "types.payments.ValidatedRequestedInfo"

    def __init__(self, *, id: Optional[str] = None, shipping_options: Optional[List["raw.base.ShippingOption"]] = None) -> None:
        self.id = id  # flags.0?string
        self.shipping_options = shipping_options  # flags.1?Vector<ShippingOption>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ValidatedRequestedInfo":
        
        flags = Int.read(b)
        
        id = String.read(b) if flags & (1 << 0) else None
        shipping_options = TLObject.read(b) if flags & (1 << 1) else []
        
        return ValidatedRequestedInfo(id=id, shipping_options=shipping_options)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.id is not None else 0
        flags |= (1 << 1) if self.shipping_options else 0
        b.write(Int(flags))
        
        if self.id is not None:
            b.write(String(self.id))
        
        if self.shipping_options:
            b.write(Vector(self.shipping_options))
        
        return b.getvalue()
