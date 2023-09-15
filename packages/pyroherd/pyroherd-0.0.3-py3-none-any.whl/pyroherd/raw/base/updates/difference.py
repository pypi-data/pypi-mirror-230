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

Difference = Union[raw.types.updates.Difference, raw.types.updates.DifferenceEmpty, raw.types.updates.DifferenceSlice, raw.types.updates.DifferenceTooLong]


# noinspection PyRedeclaration
class Difference:  # type: ignore
    """This base type has 4 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`updates.Difference <pyroherd.raw.types.updates.Difference>`
            - :obj:`updates.DifferenceEmpty <pyroherd.raw.types.updates.DifferenceEmpty>`
            - :obj:`updates.DifferenceSlice <pyroherd.raw.types.updates.DifferenceSlice>`
            - :obj:`updates.DifferenceTooLong <pyroherd.raw.types.updates.DifferenceTooLong>`

    See Also:
        This object can be returned by 1 method:

        .. hlist::
            :columns: 2

            - :obj:`updates.GetDifference <pyroherd.raw.functions.updates.GetDifference>`
    """

    QUALNAME = "pyroherd.raw.base.updates.Difference"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/difference")
