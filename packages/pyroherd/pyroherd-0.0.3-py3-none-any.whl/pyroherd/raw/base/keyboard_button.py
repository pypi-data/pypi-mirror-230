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

KeyboardButton = Union[raw.types.InputKeyboardButtonUrlAuth, raw.types.InputKeyboardButtonUserProfile, raw.types.KeyboardButton, raw.types.KeyboardButtonBuy, raw.types.KeyboardButtonCallback, raw.types.KeyboardButtonGame, raw.types.KeyboardButtonRequestGeoLocation, raw.types.KeyboardButtonRequestPeer, raw.types.KeyboardButtonRequestPhone, raw.types.KeyboardButtonRequestPoll, raw.types.KeyboardButtonSimpleWebView, raw.types.KeyboardButtonSwitchInline, raw.types.KeyboardButtonUrl, raw.types.KeyboardButtonUrlAuth, raw.types.KeyboardButtonUserProfile, raw.types.KeyboardButtonWebView]


# noinspection PyRedeclaration
class KeyboardButton:  # type: ignore
    """This base type has 16 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputKeyboardButtonUrlAuth <pyroherd.raw.types.InputKeyboardButtonUrlAuth>`
            - :obj:`InputKeyboardButtonUserProfile <pyroherd.raw.types.InputKeyboardButtonUserProfile>`
            - :obj:`KeyboardButton <pyroherd.raw.types.KeyboardButton>`
            - :obj:`KeyboardButtonBuy <pyroherd.raw.types.KeyboardButtonBuy>`
            - :obj:`KeyboardButtonCallback <pyroherd.raw.types.KeyboardButtonCallback>`
            - :obj:`KeyboardButtonGame <pyroherd.raw.types.KeyboardButtonGame>`
            - :obj:`KeyboardButtonRequestGeoLocation <pyroherd.raw.types.KeyboardButtonRequestGeoLocation>`
            - :obj:`KeyboardButtonRequestPeer <pyroherd.raw.types.KeyboardButtonRequestPeer>`
            - :obj:`KeyboardButtonRequestPhone <pyroherd.raw.types.KeyboardButtonRequestPhone>`
            - :obj:`KeyboardButtonRequestPoll <pyroherd.raw.types.KeyboardButtonRequestPoll>`
            - :obj:`KeyboardButtonSimpleWebView <pyroherd.raw.types.KeyboardButtonSimpleWebView>`
            - :obj:`KeyboardButtonSwitchInline <pyroherd.raw.types.KeyboardButtonSwitchInline>`
            - :obj:`KeyboardButtonUrl <pyroherd.raw.types.KeyboardButtonUrl>`
            - :obj:`KeyboardButtonUrlAuth <pyroherd.raw.types.KeyboardButtonUrlAuth>`
            - :obj:`KeyboardButtonUserProfile <pyroherd.raw.types.KeyboardButtonUserProfile>`
            - :obj:`KeyboardButtonWebView <pyroherd.raw.types.KeyboardButtonWebView>`
    """

    QUALNAME = "pyroherd.raw.base.KeyboardButton"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/keyboard-button")
