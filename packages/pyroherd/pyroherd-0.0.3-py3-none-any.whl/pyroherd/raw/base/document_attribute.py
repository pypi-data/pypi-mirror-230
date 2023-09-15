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

DocumentAttribute = Union[raw.types.DocumentAttributeAnimated, raw.types.DocumentAttributeAudio, raw.types.DocumentAttributeCustomEmoji, raw.types.DocumentAttributeFilename, raw.types.DocumentAttributeHasStickers, raw.types.DocumentAttributeImageSize, raw.types.DocumentAttributeSticker, raw.types.DocumentAttributeVideo]


# noinspection PyRedeclaration
class DocumentAttribute:  # type: ignore
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`DocumentAttributeAnimated <pyroherd.raw.types.DocumentAttributeAnimated>`
            - :obj:`DocumentAttributeAudio <pyroherd.raw.types.DocumentAttributeAudio>`
            - :obj:`DocumentAttributeCustomEmoji <pyroherd.raw.types.DocumentAttributeCustomEmoji>`
            - :obj:`DocumentAttributeFilename <pyroherd.raw.types.DocumentAttributeFilename>`
            - :obj:`DocumentAttributeHasStickers <pyroherd.raw.types.DocumentAttributeHasStickers>`
            - :obj:`DocumentAttributeImageSize <pyroherd.raw.types.DocumentAttributeImageSize>`
            - :obj:`DocumentAttributeSticker <pyroherd.raw.types.DocumentAttributeSticker>`
            - :obj:`DocumentAttributeVideo <pyroherd.raw.types.DocumentAttributeVideo>`
    """

    QUALNAME = "pyroherd.raw.base.DocumentAttribute"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/document-attribute")
