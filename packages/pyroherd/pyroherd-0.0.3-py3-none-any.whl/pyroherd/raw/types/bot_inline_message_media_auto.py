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


class BotInlineMessageMediaAuto(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.BotInlineMessage`.

    Details:
        - Layer: ``158``
        - ID: ``764CF810``

    Parameters:
        message: ``str``
        entities (optional): List of :obj:`MessageEntity <pyroherd.raw.base.MessageEntity>`
        reply_markup (optional): :obj:`ReplyMarkup <pyroherd.raw.base.ReplyMarkup>`
    """

    __slots__: List[str] = ["message", "entities", "reply_markup"]

    ID = 0x764cf810
    QUALNAME = "types.BotInlineMessageMediaAuto"

    def __init__(self, *, message: str, entities: Optional[List["raw.base.MessageEntity"]] = None, reply_markup: "raw.base.ReplyMarkup" = None) -> None:
        self.message = message  # string
        self.entities = entities  # flags.1?Vector<MessageEntity>
        self.reply_markup = reply_markup  # flags.2?ReplyMarkup

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "BotInlineMessageMediaAuto":
        
        flags = Int.read(b)
        
        message = String.read(b)
        
        entities = TLObject.read(b) if flags & (1 << 1) else []
        
        reply_markup = TLObject.read(b) if flags & (1 << 2) else None
        
        return BotInlineMessageMediaAuto(message=message, entities=entities, reply_markup=reply_markup)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.entities else 0
        flags |= (1 << 2) if self.reply_markup is not None else 0
        b.write(Int(flags))
        
        b.write(String(self.message))
        
        if self.entities:
            b.write(Vector(self.entities))
        
        if self.reply_markup is not None:
            b.write(self.reply_markup.write())
        
        return b.getvalue()
