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

SendMessageAction = Union[raw.types.SendMessageCancelAction, raw.types.SendMessageChooseContactAction, raw.types.SendMessageChooseStickerAction, raw.types.SendMessageEmojiInteraction, raw.types.SendMessageEmojiInteractionSeen, raw.types.SendMessageGamePlayAction, raw.types.SendMessageGeoLocationAction, raw.types.SendMessageHistoryImportAction, raw.types.SendMessageRecordAudioAction, raw.types.SendMessageRecordRoundAction, raw.types.SendMessageRecordVideoAction, raw.types.SendMessageTypingAction, raw.types.SendMessageUploadAudioAction, raw.types.SendMessageUploadDocumentAction, raw.types.SendMessageUploadPhotoAction, raw.types.SendMessageUploadRoundAction, raw.types.SendMessageUploadVideoAction, raw.types.SpeakingInGroupCallAction]


# noinspection PyRedeclaration
class SendMessageAction:  # type: ignore
    """This base type has 18 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SendMessageCancelAction <pyroherd.raw.types.SendMessageCancelAction>`
            - :obj:`SendMessageChooseContactAction <pyroherd.raw.types.SendMessageChooseContactAction>`
            - :obj:`SendMessageChooseStickerAction <pyroherd.raw.types.SendMessageChooseStickerAction>`
            - :obj:`SendMessageEmojiInteraction <pyroherd.raw.types.SendMessageEmojiInteraction>`
            - :obj:`SendMessageEmojiInteractionSeen <pyroherd.raw.types.SendMessageEmojiInteractionSeen>`
            - :obj:`SendMessageGamePlayAction <pyroherd.raw.types.SendMessageGamePlayAction>`
            - :obj:`SendMessageGeoLocationAction <pyroherd.raw.types.SendMessageGeoLocationAction>`
            - :obj:`SendMessageHistoryImportAction <pyroherd.raw.types.SendMessageHistoryImportAction>`
            - :obj:`SendMessageRecordAudioAction <pyroherd.raw.types.SendMessageRecordAudioAction>`
            - :obj:`SendMessageRecordRoundAction <pyroherd.raw.types.SendMessageRecordRoundAction>`
            - :obj:`SendMessageRecordVideoAction <pyroherd.raw.types.SendMessageRecordVideoAction>`
            - :obj:`SendMessageTypingAction <pyroherd.raw.types.SendMessageTypingAction>`
            - :obj:`SendMessageUploadAudioAction <pyroherd.raw.types.SendMessageUploadAudioAction>`
            - :obj:`SendMessageUploadDocumentAction <pyroherd.raw.types.SendMessageUploadDocumentAction>`
            - :obj:`SendMessageUploadPhotoAction <pyroherd.raw.types.SendMessageUploadPhotoAction>`
            - :obj:`SendMessageUploadRoundAction <pyroherd.raw.types.SendMessageUploadRoundAction>`
            - :obj:`SendMessageUploadVideoAction <pyroherd.raw.types.SendMessageUploadVideoAction>`
            - :obj:`SpeakingInGroupCallAction <pyroherd.raw.types.SpeakingInGroupCallAction>`
    """

    QUALNAME = "pyroherd.raw.base.SendMessageAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/send-message-action")
