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


class ShippingOption(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.ShippingOption`.

    Details:
        - Layer: ``158``
        - ID: ``B6213CDF``

    Parameters:
        id: ``str``
        title: ``str``
        prices: List of :obj:`LabeledPrice <pyroherd.raw.base.LabeledPrice>`
    """

    __slots__: List[str] = ["id", "title", "prices"]

    ID = 0xb6213cdf
    QUALNAME = "types.ShippingOption"

    def __init__(self, *, id: str, title: str, prices: List["raw.base.LabeledPrice"]) -> None:
        self.id = id  # string
        self.title = title  # string
        self.prices = prices  # Vector<LabeledPrice>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ShippingOption":
        # No flags
        
        id = String.read(b)
        
        title = String.read(b)
        
        prices = TLObject.read(b)
        
        return ShippingOption(id=id, title=title, prices=prices)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.id))
        
        b.write(String(self.title))
        
        b.write(Vector(self.prices))
        
        return b.getvalue()
