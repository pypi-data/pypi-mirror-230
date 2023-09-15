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

MessageAction = Union[raw.types.MessageActionBotAllowed, raw.types.MessageActionChannelCreate, raw.types.MessageActionChannelMigrateFrom, raw.types.MessageActionChatAddUser, raw.types.MessageActionChatCreate, raw.types.MessageActionChatDeletePhoto, raw.types.MessageActionChatDeleteUser, raw.types.MessageActionChatEditPhoto, raw.types.MessageActionChatEditTitle, raw.types.MessageActionChatJoinedByLink, raw.types.MessageActionChatJoinedByRequest, raw.types.MessageActionChatMigrateTo, raw.types.MessageActionContactSignUp, raw.types.MessageActionCustomAction, raw.types.MessageActionEmpty, raw.types.MessageActionGameScore, raw.types.MessageActionGeoProximityReached, raw.types.MessageActionGiftPremium, raw.types.MessageActionGroupCall, raw.types.MessageActionGroupCallScheduled, raw.types.MessageActionHistoryClear, raw.types.MessageActionInviteToGroupCall, raw.types.MessageActionPaymentSent, raw.types.MessageActionPaymentSentMe, raw.types.MessageActionPhoneCall, raw.types.MessageActionPinMessage, raw.types.MessageActionRequestedPeer, raw.types.MessageActionScreenshotTaken, raw.types.MessageActionSecureValuesSent, raw.types.MessageActionSecureValuesSentMe, raw.types.MessageActionSetChatTheme, raw.types.MessageActionSetChatWallPaper, raw.types.MessageActionSetMessagesTTL, raw.types.MessageActionSetSameChatWallPaper, raw.types.MessageActionSuggestProfilePhoto, raw.types.MessageActionTopicCreate, raw.types.MessageActionTopicEdit, raw.types.MessageActionWebViewDataSent, raw.types.MessageActionWebViewDataSentMe]


# noinspection PyRedeclaration
class MessageAction:  # type: ignore
    """This base type has 39 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`MessageActionBotAllowed <pyroherd.raw.types.MessageActionBotAllowed>`
            - :obj:`MessageActionChannelCreate <pyroherd.raw.types.MessageActionChannelCreate>`
            - :obj:`MessageActionChannelMigrateFrom <pyroherd.raw.types.MessageActionChannelMigrateFrom>`
            - :obj:`MessageActionChatAddUser <pyroherd.raw.types.MessageActionChatAddUser>`
            - :obj:`MessageActionChatCreate <pyroherd.raw.types.MessageActionChatCreate>`
            - :obj:`MessageActionChatDeletePhoto <pyroherd.raw.types.MessageActionChatDeletePhoto>`
            - :obj:`MessageActionChatDeleteUser <pyroherd.raw.types.MessageActionChatDeleteUser>`
            - :obj:`MessageActionChatEditPhoto <pyroherd.raw.types.MessageActionChatEditPhoto>`
            - :obj:`MessageActionChatEditTitle <pyroherd.raw.types.MessageActionChatEditTitle>`
            - :obj:`MessageActionChatJoinedByLink <pyroherd.raw.types.MessageActionChatJoinedByLink>`
            - :obj:`MessageActionChatJoinedByRequest <pyroherd.raw.types.MessageActionChatJoinedByRequest>`
            - :obj:`MessageActionChatMigrateTo <pyroherd.raw.types.MessageActionChatMigrateTo>`
            - :obj:`MessageActionContactSignUp <pyroherd.raw.types.MessageActionContactSignUp>`
            - :obj:`MessageActionCustomAction <pyroherd.raw.types.MessageActionCustomAction>`
            - :obj:`MessageActionEmpty <pyroherd.raw.types.MessageActionEmpty>`
            - :obj:`MessageActionGameScore <pyroherd.raw.types.MessageActionGameScore>`
            - :obj:`MessageActionGeoProximityReached <pyroherd.raw.types.MessageActionGeoProximityReached>`
            - :obj:`MessageActionGiftPremium <pyroherd.raw.types.MessageActionGiftPremium>`
            - :obj:`MessageActionGroupCall <pyroherd.raw.types.MessageActionGroupCall>`
            - :obj:`MessageActionGroupCallScheduled <pyroherd.raw.types.MessageActionGroupCallScheduled>`
            - :obj:`MessageActionHistoryClear <pyroherd.raw.types.MessageActionHistoryClear>`
            - :obj:`MessageActionInviteToGroupCall <pyroherd.raw.types.MessageActionInviteToGroupCall>`
            - :obj:`MessageActionPaymentSent <pyroherd.raw.types.MessageActionPaymentSent>`
            - :obj:`MessageActionPaymentSentMe <pyroherd.raw.types.MessageActionPaymentSentMe>`
            - :obj:`MessageActionPhoneCall <pyroherd.raw.types.MessageActionPhoneCall>`
            - :obj:`MessageActionPinMessage <pyroherd.raw.types.MessageActionPinMessage>`
            - :obj:`MessageActionRequestedPeer <pyroherd.raw.types.MessageActionRequestedPeer>`
            - :obj:`MessageActionScreenshotTaken <pyroherd.raw.types.MessageActionScreenshotTaken>`
            - :obj:`MessageActionSecureValuesSent <pyroherd.raw.types.MessageActionSecureValuesSent>`
            - :obj:`MessageActionSecureValuesSentMe <pyroherd.raw.types.MessageActionSecureValuesSentMe>`
            - :obj:`MessageActionSetChatTheme <pyroherd.raw.types.MessageActionSetChatTheme>`
            - :obj:`MessageActionSetChatWallPaper <pyroherd.raw.types.MessageActionSetChatWallPaper>`
            - :obj:`MessageActionSetMessagesTTL <pyroherd.raw.types.MessageActionSetMessagesTTL>`
            - :obj:`MessageActionSetSameChatWallPaper <pyroherd.raw.types.MessageActionSetSameChatWallPaper>`
            - :obj:`MessageActionSuggestProfilePhoto <pyroherd.raw.types.MessageActionSuggestProfilePhoto>`
            - :obj:`MessageActionTopicCreate <pyroherd.raw.types.MessageActionTopicCreate>`
            - :obj:`MessageActionTopicEdit <pyroherd.raw.types.MessageActionTopicEdit>`
            - :obj:`MessageActionWebViewDataSent <pyroherd.raw.types.MessageActionWebViewDataSent>`
            - :obj:`MessageActionWebViewDataSentMe <pyroherd.raw.types.MessageActionWebViewDataSentMe>`
    """

    QUALNAME = "pyroherd.raw.base.MessageAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/message-action")
