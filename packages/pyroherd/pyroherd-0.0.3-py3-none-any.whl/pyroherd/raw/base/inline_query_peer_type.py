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

InlineQueryPeerType = Union[raw.types.InlineQueryPeerTypeBotPM, raw.types.InlineQueryPeerTypeBroadcast, raw.types.InlineQueryPeerTypeChat, raw.types.InlineQueryPeerTypeMegagroup, raw.types.InlineQueryPeerTypePM, raw.types.InlineQueryPeerTypeSameBotPM]


# noinspection PyRedeclaration
class InlineQueryPeerType:  # type: ignore
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InlineQueryPeerTypeBotPM <pyroherd.raw.types.InlineQueryPeerTypeBotPM>`
            - :obj:`InlineQueryPeerTypeBroadcast <pyroherd.raw.types.InlineQueryPeerTypeBroadcast>`
            - :obj:`InlineQueryPeerTypeChat <pyroherd.raw.types.InlineQueryPeerTypeChat>`
            - :obj:`InlineQueryPeerTypeMegagroup <pyroherd.raw.types.InlineQueryPeerTypeMegagroup>`
            - :obj:`InlineQueryPeerTypePM <pyroherd.raw.types.InlineQueryPeerTypePM>`
            - :obj:`InlineQueryPeerTypeSameBotPM <pyroherd.raw.types.InlineQueryPeerTypeSameBotPM>`
    """

    QUALNAME = "pyroherd.raw.base.InlineQueryPeerType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/inline-query-peer-type")
