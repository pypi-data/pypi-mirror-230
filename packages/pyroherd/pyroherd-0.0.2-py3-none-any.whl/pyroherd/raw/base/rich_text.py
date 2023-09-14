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

RichText = Union[raw.types.TextAnchor, raw.types.TextBold, raw.types.TextConcat, raw.types.TextEmail, raw.types.TextEmpty, raw.types.TextFixed, raw.types.TextImage, raw.types.TextItalic, raw.types.TextMarked, raw.types.TextPhone, raw.types.TextPlain, raw.types.TextStrike, raw.types.TextSubscript, raw.types.TextSuperscript, raw.types.TextUnderline, raw.types.TextUrl]


# noinspection PyRedeclaration
class RichText:  # type: ignore
    """This base type has 16 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`TextAnchor <pyroherd.raw.types.TextAnchor>`
            - :obj:`TextBold <pyroherd.raw.types.TextBold>`
            - :obj:`TextConcat <pyroherd.raw.types.TextConcat>`
            - :obj:`TextEmail <pyroherd.raw.types.TextEmail>`
            - :obj:`TextEmpty <pyroherd.raw.types.TextEmpty>`
            - :obj:`TextFixed <pyroherd.raw.types.TextFixed>`
            - :obj:`TextImage <pyroherd.raw.types.TextImage>`
            - :obj:`TextItalic <pyroherd.raw.types.TextItalic>`
            - :obj:`TextMarked <pyroherd.raw.types.TextMarked>`
            - :obj:`TextPhone <pyroherd.raw.types.TextPhone>`
            - :obj:`TextPlain <pyroherd.raw.types.TextPlain>`
            - :obj:`TextStrike <pyroherd.raw.types.TextStrike>`
            - :obj:`TextSubscript <pyroherd.raw.types.TextSubscript>`
            - :obj:`TextSuperscript <pyroherd.raw.types.TextSuperscript>`
            - :obj:`TextUnderline <pyroherd.raw.types.TextUnderline>`
            - :obj:`TextUrl <pyroherd.raw.types.TextUrl>`
    """

    QUALNAME = "pyroherd.raw.base.RichText"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/rich-text")
