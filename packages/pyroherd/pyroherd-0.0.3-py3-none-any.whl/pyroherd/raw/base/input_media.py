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

InputMedia = Union[raw.types.InputMediaContact, raw.types.InputMediaDice, raw.types.InputMediaDocument, raw.types.InputMediaDocumentExternal, raw.types.InputMediaEmpty, raw.types.InputMediaGame, raw.types.InputMediaGeoLive, raw.types.InputMediaGeoPoint, raw.types.InputMediaInvoice, raw.types.InputMediaPhoto, raw.types.InputMediaPhotoExternal, raw.types.InputMediaPoll, raw.types.InputMediaUploadedDocument, raw.types.InputMediaUploadedPhoto, raw.types.InputMediaVenue]


# noinspection PyRedeclaration
class InputMedia:  # type: ignore
    """This base type has 15 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMediaContact <pyroherd.raw.types.InputMediaContact>`
            - :obj:`InputMediaDice <pyroherd.raw.types.InputMediaDice>`
            - :obj:`InputMediaDocument <pyroherd.raw.types.InputMediaDocument>`
            - :obj:`InputMediaDocumentExternal <pyroherd.raw.types.InputMediaDocumentExternal>`
            - :obj:`InputMediaEmpty <pyroherd.raw.types.InputMediaEmpty>`
            - :obj:`InputMediaGame <pyroherd.raw.types.InputMediaGame>`
            - :obj:`InputMediaGeoLive <pyroherd.raw.types.InputMediaGeoLive>`
            - :obj:`InputMediaGeoPoint <pyroherd.raw.types.InputMediaGeoPoint>`
            - :obj:`InputMediaInvoice <pyroherd.raw.types.InputMediaInvoice>`
            - :obj:`InputMediaPhoto <pyroherd.raw.types.InputMediaPhoto>`
            - :obj:`InputMediaPhotoExternal <pyroherd.raw.types.InputMediaPhotoExternal>`
            - :obj:`InputMediaPoll <pyroherd.raw.types.InputMediaPoll>`
            - :obj:`InputMediaUploadedDocument <pyroherd.raw.types.InputMediaUploadedDocument>`
            - :obj:`InputMediaUploadedPhoto <pyroherd.raw.types.InputMediaUploadedPhoto>`
            - :obj:`InputMediaVenue <pyroherd.raw.types.InputMediaVenue>`
    """

    QUALNAME = "pyroherd.raw.base.InputMedia"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/input-media")
