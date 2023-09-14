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

MessageMedia = Union[raw.types.MessageMediaContact, raw.types.MessageMediaDice, raw.types.MessageMediaDocument, raw.types.MessageMediaEmpty, raw.types.MessageMediaGame, raw.types.MessageMediaGeo, raw.types.MessageMediaGeoLive, raw.types.MessageMediaInvoice, raw.types.MessageMediaPhoto, raw.types.MessageMediaPoll, raw.types.MessageMediaUnsupported, raw.types.MessageMediaVenue, raw.types.MessageMediaWebPage]


# noinspection PyRedeclaration
class MessageMedia:  # type: ignore
    """This base type has 13 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageMediaContact <pyroherd.raw.types.MessageMediaContact>`
            - :obj:`MessageMediaDice <pyroherd.raw.types.MessageMediaDice>`
            - :obj:`MessageMediaDocument <pyroherd.raw.types.MessageMediaDocument>`
            - :obj:`MessageMediaEmpty <pyroherd.raw.types.MessageMediaEmpty>`
            - :obj:`MessageMediaGame <pyroherd.raw.types.MessageMediaGame>`
            - :obj:`MessageMediaGeo <pyroherd.raw.types.MessageMediaGeo>`
            - :obj:`MessageMediaGeoLive <pyroherd.raw.types.MessageMediaGeoLive>`
            - :obj:`MessageMediaInvoice <pyroherd.raw.types.MessageMediaInvoice>`
            - :obj:`MessageMediaPhoto <pyroherd.raw.types.MessageMediaPhoto>`
            - :obj:`MessageMediaPoll <pyroherd.raw.types.MessageMediaPoll>`
            - :obj:`MessageMediaUnsupported <pyroherd.raw.types.MessageMediaUnsupported>`
            - :obj:`MessageMediaVenue <pyroherd.raw.types.MessageMediaVenue>`
            - :obj:`MessageMediaWebPage <pyroherd.raw.types.MessageMediaWebPage>`

    See Also:
        This object can be returned by 3 methods:

        .. hlist::
            :columns: 2

            - :obj:`messages.GetWebPagePreview <pyroherd.raw.functions.messages.GetWebPagePreview>`
            - :obj:`messages.UploadMedia <pyroherd.raw.functions.messages.UploadMedia>`
            - :obj:`messages.UploadImportedMedia <pyroherd.raw.functions.messages.UploadImportedMedia>`
    """

    QUALNAME = "pyroherd.raw.base.MessageMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/message-media")
