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


class AutoDownloadSettings(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.account.AutoDownloadSettings`.

    Details:
        - Layer: ``158``
        - ID: ``63CACF26``

    Parameters:
        low: :obj:`AutoDownloadSettings <pyroherd.raw.base.AutoDownloadSettings>`
        medium: :obj:`AutoDownloadSettings <pyroherd.raw.base.AutoDownloadSettings>`
        high: :obj:`AutoDownloadSettings <pyroherd.raw.base.AutoDownloadSettings>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`account.GetAutoDownloadSettings <pyroherd.raw.functions.account.GetAutoDownloadSettings>`
    """

    __slots__: List[str] = ["low", "medium", "high"]

    ID = 0x63cacf26
    QUALNAME = "types.account.AutoDownloadSettings"

    def __init__(self, *, low: "raw.base.AutoDownloadSettings", medium: "raw.base.AutoDownloadSettings", high: "raw.base.AutoDownloadSettings") -> None:
        self.low = low  # AutoDownloadSettings
        self.medium = medium  # AutoDownloadSettings
        self.high = high  # AutoDownloadSettings

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AutoDownloadSettings":
        # No flags
        
        low = TLObject.read(b)
        
        medium = TLObject.read(b)
        
        high = TLObject.read(b)
        
        return AutoDownloadSettings(low=low, medium=medium, high=high)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.low.write())
        
        b.write(self.medium.write())
        
        b.write(self.high.write())
        
        return b.getvalue()
