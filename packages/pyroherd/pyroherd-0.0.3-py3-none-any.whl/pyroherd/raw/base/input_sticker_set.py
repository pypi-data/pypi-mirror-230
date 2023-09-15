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

InputStickerSet = Union[raw.types.InputStickerSetAnimatedEmoji, raw.types.InputStickerSetAnimatedEmojiAnimations, raw.types.InputStickerSetDice, raw.types.InputStickerSetEmojiDefaultStatuses, raw.types.InputStickerSetEmojiDefaultTopicIcons, raw.types.InputStickerSetEmojiGenericAnimations, raw.types.InputStickerSetEmpty, raw.types.InputStickerSetID, raw.types.InputStickerSetPremiumGifts, raw.types.InputStickerSetShortName]


# noinspection PyRedeclaration
class InputStickerSet:  # type: ignore
    """This base type has 10 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputStickerSetAnimatedEmoji <pyroherd.raw.types.InputStickerSetAnimatedEmoji>`
            - :obj:`InputStickerSetAnimatedEmojiAnimations <pyroherd.raw.types.InputStickerSetAnimatedEmojiAnimations>`
            - :obj:`InputStickerSetDice <pyroherd.raw.types.InputStickerSetDice>`
            - :obj:`InputStickerSetEmojiDefaultStatuses <pyroherd.raw.types.InputStickerSetEmojiDefaultStatuses>`
            - :obj:`InputStickerSetEmojiDefaultTopicIcons <pyroherd.raw.types.InputStickerSetEmojiDefaultTopicIcons>`
            - :obj:`InputStickerSetEmojiGenericAnimations <pyroherd.raw.types.InputStickerSetEmojiGenericAnimations>`
            - :obj:`InputStickerSetEmpty <pyroherd.raw.types.InputStickerSetEmpty>`
            - :obj:`InputStickerSetID <pyroherd.raw.types.InputStickerSetID>`
            - :obj:`InputStickerSetPremiumGifts <pyroherd.raw.types.InputStickerSetPremiumGifts>`
            - :obj:`InputStickerSetShortName <pyroherd.raw.types.InputStickerSetShortName>`
    """

    QUALNAME = "pyroherd.raw.base.InputStickerSet"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/input-sticker-set")
