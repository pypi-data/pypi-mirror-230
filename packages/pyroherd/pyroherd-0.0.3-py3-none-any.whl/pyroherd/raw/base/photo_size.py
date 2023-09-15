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

PhotoSize = Union[raw.types.PhotoCachedSize, raw.types.PhotoPathSize, raw.types.PhotoSize, raw.types.PhotoSizeEmpty, raw.types.PhotoSizeProgressive, raw.types.PhotoStrippedSize]


# noinspection PyRedeclaration
class PhotoSize:  # type: ignore
    """This base type has 6 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PhotoCachedSize <pyroherd.raw.types.PhotoCachedSize>`
            - :obj:`PhotoPathSize <pyroherd.raw.types.PhotoPathSize>`
            - :obj:`PhotoSize <pyroherd.raw.types.PhotoSize>`
            - :obj:`PhotoSizeEmpty <pyroherd.raw.types.PhotoSizeEmpty>`
            - :obj:`PhotoSizeProgressive <pyroherd.raw.types.PhotoSizeProgressive>`
            - :obj:`PhotoStrippedSize <pyroherd.raw.types.PhotoStrippedSize>`
    """

    QUALNAME = "pyroherd.raw.base.PhotoSize"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/photo-size")
