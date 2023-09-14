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


class PremiumPromo(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.help.PremiumPromo`.

    Details:
        - Layer: ``143``
        - ID: ``8A4F3C29``

    Parameters:
        status_text: ``str``
        status_entities: List of :obj:`MessageEntity <pyroherd.raw.base.MessageEntity>`
        video_sections: List of ``str``
        videos: List of :obj:`Document <pyroherd.raw.base.Document>`
        currency: ``str``
        monthly_amount: ``int`` ``64-bit``
        users: List of :obj:`User <pyroherd.raw.base.User>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`help.GetPremiumPromo <pyroherd.raw.functions.help.GetPremiumPromo>`
    """

    __slots__: List[str] = ["status_text", "status_entities", "video_sections", "videos", "currency", "monthly_amount", "users"]

    ID = 0x8a4f3c29
    QUALNAME = "types.help.PremiumPromo"

    def __init__(self, *, status_text: str, status_entities: List["raw.base.MessageEntity"], video_sections: List[str], videos: List["raw.base.Document"], currency: str, monthly_amount: int, users: List["raw.base.User"]) -> None:
        self.status_text = status_text  # string
        self.status_entities = status_entities  # Vector<MessageEntity>
        self.video_sections = video_sections  # Vector<string>
        self.videos = videos  # Vector<Document>
        self.currency = currency  # string
        self.monthly_amount = monthly_amount  # long
        self.users = users  # Vector<User>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "PremiumPromo":
        # No flags
        
        status_text = String.read(b)
        
        status_entities = TLObject.read(b)
        
        video_sections = TLObject.read(b, String)
        
        videos = TLObject.read(b)
        
        currency = String.read(b)
        
        monthly_amount = Long.read(b)
        
        users = TLObject.read(b)
        
        return PremiumPromo(status_text=status_text, status_entities=status_entities, video_sections=video_sections, videos=videos, currency=currency, monthly_amount=monthly_amount, users=users)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.status_text))
        
        b.write(Vector(self.status_entities))
        
        b.write(Vector(self.video_sections, String))
        
        b.write(Vector(self.videos))
        
        b.write(String(self.currency))
        
        b.write(Long(self.monthly_amount))
        
        b.write(Vector(self.users))
        
        return b.getvalue()
