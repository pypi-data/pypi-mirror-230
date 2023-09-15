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


class MessageStats(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.stats.MessageStats`.

    Details:
        - Layer: ``158``
        - ID: ``8999F295``

    Parameters:
        views_graph: :obj:`StatsGraph <pyroherd.raw.base.StatsGraph>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`stats.GetMessageStats <pyroherd.raw.functions.stats.GetMessageStats>`
    """

    __slots__: List[str] = ["views_graph"]

    ID = 0x8999f295
    QUALNAME = "types.stats.MessageStats"

    def __init__(self, *, views_graph: "raw.base.StatsGraph") -> None:
        self.views_graph = views_graph  # StatsGraph

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageStats":
        # No flags
        
        views_graph = TLObject.read(b)
        
        return MessageStats(views_graph=views_graph)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.views_graph.write())
        
        return b.getvalue()
