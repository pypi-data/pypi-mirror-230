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

MessagesFilter = Union[raw.types.InputMessagesFilterChatPhotos, raw.types.InputMessagesFilterContacts, raw.types.InputMessagesFilterDocument, raw.types.InputMessagesFilterEmpty, raw.types.InputMessagesFilterGeo, raw.types.InputMessagesFilterGif, raw.types.InputMessagesFilterMusic, raw.types.InputMessagesFilterMyMentions, raw.types.InputMessagesFilterPhoneCalls, raw.types.InputMessagesFilterPhotoVideo, raw.types.InputMessagesFilterPhotos, raw.types.InputMessagesFilterPinned, raw.types.InputMessagesFilterRoundVideo, raw.types.InputMessagesFilterRoundVoice, raw.types.InputMessagesFilterUrl, raw.types.InputMessagesFilterVideo, raw.types.InputMessagesFilterVoice]


# noinspection PyRedeclaration
class MessagesFilter:  # type: ignore
    """This base type has 17 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`InputMessagesFilterChatPhotos <pyroherd.raw.types.InputMessagesFilterChatPhotos>`
            - :obj:`InputMessagesFilterContacts <pyroherd.raw.types.InputMessagesFilterContacts>`
            - :obj:`InputMessagesFilterDocument <pyroherd.raw.types.InputMessagesFilterDocument>`
            - :obj:`InputMessagesFilterEmpty <pyroherd.raw.types.InputMessagesFilterEmpty>`
            - :obj:`InputMessagesFilterGeo <pyroherd.raw.types.InputMessagesFilterGeo>`
            - :obj:`InputMessagesFilterGif <pyroherd.raw.types.InputMessagesFilterGif>`
            - :obj:`InputMessagesFilterMusic <pyroherd.raw.types.InputMessagesFilterMusic>`
            - :obj:`InputMessagesFilterMyMentions <pyroherd.raw.types.InputMessagesFilterMyMentions>`
            - :obj:`InputMessagesFilterPhoneCalls <pyroherd.raw.types.InputMessagesFilterPhoneCalls>`
            - :obj:`InputMessagesFilterPhotoVideo <pyroherd.raw.types.InputMessagesFilterPhotoVideo>`
            - :obj:`InputMessagesFilterPhotos <pyroherd.raw.types.InputMessagesFilterPhotos>`
            - :obj:`InputMessagesFilterPinned <pyroherd.raw.types.InputMessagesFilterPinned>`
            - :obj:`InputMessagesFilterRoundVideo <pyroherd.raw.types.InputMessagesFilterRoundVideo>`
            - :obj:`InputMessagesFilterRoundVoice <pyroherd.raw.types.InputMessagesFilterRoundVoice>`
            - :obj:`InputMessagesFilterUrl <pyroherd.raw.types.InputMessagesFilterUrl>`
            - :obj:`InputMessagesFilterVideo <pyroherd.raw.types.InputMessagesFilterVideo>`
            - :obj:`InputMessagesFilterVoice <pyroherd.raw.types.InputMessagesFilterVoice>`
    """

    QUALNAME = "pyroherd.raw.base.MessagesFilter"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/messages-filter")
