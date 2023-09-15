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

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from pyroherd import raw
from pyroherd.raw.core import TLObject

MessageEntity = Union[raw.types.InputMessageEntityMentionName, raw.types.MessageEntityBankCard, raw.types.MessageEntityBlockquote, raw.types.MessageEntityBold, raw.types.MessageEntityBotCommand, raw.types.MessageEntityCashtag, raw.types.MessageEntityCode, raw.types.MessageEntityCustomEmoji, raw.types.MessageEntityEmail, raw.types.MessageEntityHashtag, raw.types.MessageEntityItalic, raw.types.MessageEntityMention, raw.types.MessageEntityMentionName, raw.types.MessageEntityPhone, raw.types.MessageEntityPre, raw.types.MessageEntitySpoiler, raw.types.MessageEntityStrike, raw.types.MessageEntityTextUrl, raw.types.MessageEntityUnderline, raw.types.MessageEntityUnknown, raw.types.MessageEntityUrl]


# noinspection PyRedeclaration
class MessageEntity:  # type: ignore
    """This base type has 21 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessageEntityMentionName <pyroherd.raw.types.InputMessageEntityMentionName>`
            - :obj:`MessageEntityBankCard <pyroherd.raw.types.MessageEntityBankCard>`
            - :obj:`MessageEntityBlockquote <pyroherd.raw.types.MessageEntityBlockquote>`
            - :obj:`MessageEntityBold <pyroherd.raw.types.MessageEntityBold>`
            - :obj:`MessageEntityBotCommand <pyroherd.raw.types.MessageEntityBotCommand>`
            - :obj:`MessageEntityCashtag <pyroherd.raw.types.MessageEntityCashtag>`
            - :obj:`MessageEntityCode <pyroherd.raw.types.MessageEntityCode>`
            - :obj:`MessageEntityCustomEmoji <pyroherd.raw.types.MessageEntityCustomEmoji>`
            - :obj:`MessageEntityEmail <pyroherd.raw.types.MessageEntityEmail>`
            - :obj:`MessageEntityHashtag <pyroherd.raw.types.MessageEntityHashtag>`
            - :obj:`MessageEntityItalic <pyroherd.raw.types.MessageEntityItalic>`
            - :obj:`MessageEntityMention <pyroherd.raw.types.MessageEntityMention>`
            - :obj:`MessageEntityMentionName <pyroherd.raw.types.MessageEntityMentionName>`
            - :obj:`MessageEntityPhone <pyroherd.raw.types.MessageEntityPhone>`
            - :obj:`MessageEntityPre <pyroherd.raw.types.MessageEntityPre>`
            - :obj:`MessageEntitySpoiler <pyroherd.raw.types.MessageEntitySpoiler>`
            - :obj:`MessageEntityStrike <pyroherd.raw.types.MessageEntityStrike>`
            - :obj:`MessageEntityTextUrl <pyroherd.raw.types.MessageEntityTextUrl>`
            - :obj:`MessageEntityUnderline <pyroherd.raw.types.MessageEntityUnderline>`
            - :obj:`MessageEntityUnknown <pyroherd.raw.types.MessageEntityUnknown>`
            - :obj:`MessageEntityUrl <pyroherd.raw.types.MessageEntityUrl>`
    """

    QUALNAME = "pyroherd.raw.base.MessageEntity"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/message-entity")
