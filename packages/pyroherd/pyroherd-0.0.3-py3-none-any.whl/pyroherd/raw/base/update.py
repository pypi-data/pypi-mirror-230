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

Update = Union[raw.types.UpdateAttachMenuBots, raw.types.UpdateAutoSaveSettings, raw.types.UpdateBotCallbackQuery, raw.types.UpdateBotChatInviteRequester, raw.types.UpdateBotCommands, raw.types.UpdateBotInlineQuery, raw.types.UpdateBotInlineSend, raw.types.UpdateBotMenuButton, raw.types.UpdateBotPrecheckoutQuery, raw.types.UpdateBotShippingQuery, raw.types.UpdateBotStopped, raw.types.UpdateBotWebhookJSON, raw.types.UpdateBotWebhookJSONQuery, raw.types.UpdateChannel, raw.types.UpdateChannelAvailableMessages, raw.types.UpdateChannelMessageForwards, raw.types.UpdateChannelMessageViews, raw.types.UpdateChannelParticipant, raw.types.UpdateChannelPinnedTopic, raw.types.UpdateChannelPinnedTopics, raw.types.UpdateChannelReadMessagesContents, raw.types.UpdateChannelTooLong, raw.types.UpdateChannelUserTyping, raw.types.UpdateChannelWebPage, raw.types.UpdateChat, raw.types.UpdateChatDefaultBannedRights, raw.types.UpdateChatParticipant, raw.types.UpdateChatParticipantAdd, raw.types.UpdateChatParticipantAdmin, raw.types.UpdateChatParticipantDelete, raw.types.UpdateChatParticipants, raw.types.UpdateChatUserTyping, raw.types.UpdateConfig, raw.types.UpdateContactsReset, raw.types.UpdateDcOptions, raw.types.UpdateDeleteChannelMessages, raw.types.UpdateDeleteMessages, raw.types.UpdateDeleteScheduledMessages, raw.types.UpdateDialogFilter, raw.types.UpdateDialogFilterOrder, raw.types.UpdateDialogFilters, raw.types.UpdateDialogPinned, raw.types.UpdateDialogUnreadMark, raw.types.UpdateDraftMessage, raw.types.UpdateEditChannelMessage, raw.types.UpdateEditMessage, raw.types.UpdateEncryptedChatTyping, raw.types.UpdateEncryptedMessagesRead, raw.types.UpdateEncryption, raw.types.UpdateFavedStickers, raw.types.UpdateFolderPeers, raw.types.UpdateGeoLiveViewed, raw.types.UpdateGroupCall, raw.types.UpdateGroupCallConnection, raw.types.UpdateGroupCallParticipants, raw.types.UpdateGroupInvitePrivacyForbidden, raw.types.UpdateInlineBotCallbackQuery, raw.types.UpdateLangPack, raw.types.UpdateLangPackTooLong, raw.types.UpdateLoginToken, raw.types.UpdateMessageExtendedMedia, raw.types.UpdateMessageID, raw.types.UpdateMessagePoll, raw.types.UpdateMessagePollVote, raw.types.UpdateMessageReactions, raw.types.UpdateMoveStickerSetToTop, raw.types.UpdateNewChannelMessage, raw.types.UpdateNewEncryptedMessage, raw.types.UpdateNewMessage, raw.types.UpdateNewScheduledMessage, raw.types.UpdateNewStickerSet, raw.types.UpdateNotifySettings, raw.types.UpdatePeerBlocked, raw.types.UpdatePeerHistoryTTL, raw.types.UpdatePeerLocated, raw.types.UpdatePeerSettings, raw.types.UpdatePendingJoinRequests, raw.types.UpdatePhoneCall, raw.types.UpdatePhoneCallSignalingData, raw.types.UpdatePinnedChannelMessages, raw.types.UpdatePinnedDialogs, raw.types.UpdatePinnedMessages, raw.types.UpdatePrivacy, raw.types.UpdatePtsChanged, raw.types.UpdateReadChannelDiscussionInbox, raw.types.UpdateReadChannelDiscussionOutbox, raw.types.UpdateReadChannelInbox, raw.types.UpdateReadChannelOutbox, raw.types.UpdateReadFeaturedEmojiStickers, raw.types.UpdateReadFeaturedStickers, raw.types.UpdateReadHistoryInbox, raw.types.UpdateReadHistoryOutbox, raw.types.UpdateReadMessagesContents, raw.types.UpdateRecentEmojiStatuses, raw.types.UpdateRecentReactions, raw.types.UpdateRecentStickers, raw.types.UpdateSavedGifs, raw.types.UpdateSavedRingtones, raw.types.UpdateServiceNotification, raw.types.UpdateStickerSets, raw.types.UpdateStickerSetsOrder, raw.types.UpdateTheme, raw.types.UpdateTranscribedAudio, raw.types.UpdateUser, raw.types.UpdateUserEmojiStatus, raw.types.UpdateUserName, raw.types.UpdateUserPhone, raw.types.UpdateUserStatus, raw.types.UpdateUserTyping, raw.types.UpdateWebPage, raw.types.UpdateWebViewResultSent]


# noinspection PyRedeclaration
class Update:  # type: ignore
    """This base type has 111 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`UpdateAttachMenuBots <pyroherd.raw.types.UpdateAttachMenuBots>`
            - :obj:`UpdateAutoSaveSettings <pyroherd.raw.types.UpdateAutoSaveSettings>`
            - :obj:`UpdateBotCallbackQuery <pyroherd.raw.types.UpdateBotCallbackQuery>`
            - :obj:`UpdateBotChatInviteRequester <pyroherd.raw.types.UpdateBotChatInviteRequester>`
            - :obj:`UpdateBotCommands <pyroherd.raw.types.UpdateBotCommands>`
            - :obj:`UpdateBotInlineQuery <pyroherd.raw.types.UpdateBotInlineQuery>`
            - :obj:`UpdateBotInlineSend <pyroherd.raw.types.UpdateBotInlineSend>`
            - :obj:`UpdateBotMenuButton <pyroherd.raw.types.UpdateBotMenuButton>`
            - :obj:`UpdateBotPrecheckoutQuery <pyroherd.raw.types.UpdateBotPrecheckoutQuery>`
            - :obj:`UpdateBotShippingQuery <pyroherd.raw.types.UpdateBotShippingQuery>`
            - :obj:`UpdateBotStopped <pyroherd.raw.types.UpdateBotStopped>`
            - :obj:`UpdateBotWebhookJSON <pyroherd.raw.types.UpdateBotWebhookJSON>`
            - :obj:`UpdateBotWebhookJSONQuery <pyroherd.raw.types.UpdateBotWebhookJSONQuery>`
            - :obj:`UpdateChannel <pyroherd.raw.types.UpdateChannel>`
            - :obj:`UpdateChannelAvailableMessages <pyroherd.raw.types.UpdateChannelAvailableMessages>`
            - :obj:`UpdateChannelMessageForwards <pyroherd.raw.types.UpdateChannelMessageForwards>`
            - :obj:`UpdateChannelMessageViews <pyroherd.raw.types.UpdateChannelMessageViews>`
            - :obj:`UpdateChannelParticipant <pyroherd.raw.types.UpdateChannelParticipant>`
            - :obj:`UpdateChannelPinnedTopic <pyroherd.raw.types.UpdateChannelPinnedTopic>`
            - :obj:`UpdateChannelPinnedTopics <pyroherd.raw.types.UpdateChannelPinnedTopics>`
            - :obj:`UpdateChannelReadMessagesContents <pyroherd.raw.types.UpdateChannelReadMessagesContents>`
            - :obj:`UpdateChannelTooLong <pyroherd.raw.types.UpdateChannelTooLong>`
            - :obj:`UpdateChannelUserTyping <pyroherd.raw.types.UpdateChannelUserTyping>`
            - :obj:`UpdateChannelWebPage <pyroherd.raw.types.UpdateChannelWebPage>`
            - :obj:`UpdateChat <pyroherd.raw.types.UpdateChat>`
            - :obj:`UpdateChatDefaultBannedRights <pyroherd.raw.types.UpdateChatDefaultBannedRights>`
            - :obj:`UpdateChatParticipant <pyroherd.raw.types.UpdateChatParticipant>`
            - :obj:`UpdateChatParticipantAdd <pyroherd.raw.types.UpdateChatParticipantAdd>`
            - :obj:`UpdateChatParticipantAdmin <pyroherd.raw.types.UpdateChatParticipantAdmin>`
            - :obj:`UpdateChatParticipantDelete <pyroherd.raw.types.UpdateChatParticipantDelete>`
            - :obj:`UpdateChatParticipants <pyroherd.raw.types.UpdateChatParticipants>`
            - :obj:`UpdateChatUserTyping <pyroherd.raw.types.UpdateChatUserTyping>`
            - :obj:`UpdateConfig <pyroherd.raw.types.UpdateConfig>`
            - :obj:`UpdateContactsReset <pyroherd.raw.types.UpdateContactsReset>`
            - :obj:`UpdateDcOptions <pyroherd.raw.types.UpdateDcOptions>`
            - :obj:`UpdateDeleteChannelMessages <pyroherd.raw.types.UpdateDeleteChannelMessages>`
            - :obj:`UpdateDeleteMessages <pyroherd.raw.types.UpdateDeleteMessages>`
            - :obj:`UpdateDeleteScheduledMessages <pyroherd.raw.types.UpdateDeleteScheduledMessages>`
            - :obj:`UpdateDialogFilter <pyroherd.raw.types.UpdateDialogFilter>`
            - :obj:`UpdateDialogFilterOrder <pyroherd.raw.types.UpdateDialogFilterOrder>`
            - :obj:`UpdateDialogFilters <pyroherd.raw.types.UpdateDialogFilters>`
            - :obj:`UpdateDialogPinned <pyroherd.raw.types.UpdateDialogPinned>`
            - :obj:`UpdateDialogUnreadMark <pyroherd.raw.types.UpdateDialogUnreadMark>`
            - :obj:`UpdateDraftMessage <pyroherd.raw.types.UpdateDraftMessage>`
            - :obj:`UpdateEditChannelMessage <pyroherd.raw.types.UpdateEditChannelMessage>`
            - :obj:`UpdateEditMessage <pyroherd.raw.types.UpdateEditMessage>`
            - :obj:`UpdateEncryptedChatTyping <pyroherd.raw.types.UpdateEncryptedChatTyping>`
            - :obj:`UpdateEncryptedMessagesRead <pyroherd.raw.types.UpdateEncryptedMessagesRead>`
            - :obj:`UpdateEncryption <pyroherd.raw.types.UpdateEncryption>`
            - :obj:`UpdateFavedStickers <pyroherd.raw.types.UpdateFavedStickers>`
            - :obj:`UpdateFolderPeers <pyroherd.raw.types.UpdateFolderPeers>`
            - :obj:`UpdateGeoLiveViewed <pyroherd.raw.types.UpdateGeoLiveViewed>`
            - :obj:`UpdateGroupCall <pyroherd.raw.types.UpdateGroupCall>`
            - :obj:`UpdateGroupCallConnection <pyroherd.raw.types.UpdateGroupCallConnection>`
            - :obj:`UpdateGroupCallParticipants <pyroherd.raw.types.UpdateGroupCallParticipants>`
            - :obj:`UpdateGroupInvitePrivacyForbidden <pyroherd.raw.types.UpdateGroupInvitePrivacyForbidden>`
            - :obj:`UpdateInlineBotCallbackQuery <pyroherd.raw.types.UpdateInlineBotCallbackQuery>`
            - :obj:`UpdateLangPack <pyroherd.raw.types.UpdateLangPack>`
            - :obj:`UpdateLangPackTooLong <pyroherd.raw.types.UpdateLangPackTooLong>`
            - :obj:`UpdateLoginToken <pyroherd.raw.types.UpdateLoginToken>`
            - :obj:`UpdateMessageExtendedMedia <pyroherd.raw.types.UpdateMessageExtendedMedia>`
            - :obj:`UpdateMessageID <pyroherd.raw.types.UpdateMessageID>`
            - :obj:`UpdateMessagePoll <pyroherd.raw.types.UpdateMessagePoll>`
            - :obj:`UpdateMessagePollVote <pyroherd.raw.types.UpdateMessagePollVote>`
            - :obj:`UpdateMessageReactions <pyroherd.raw.types.UpdateMessageReactions>`
            - :obj:`UpdateMoveStickerSetToTop <pyroherd.raw.types.UpdateMoveStickerSetToTop>`
            - :obj:`UpdateNewChannelMessage <pyroherd.raw.types.UpdateNewChannelMessage>`
            - :obj:`UpdateNewEncryptedMessage <pyroherd.raw.types.UpdateNewEncryptedMessage>`
            - :obj:`UpdateNewMessage <pyroherd.raw.types.UpdateNewMessage>`
            - :obj:`UpdateNewScheduledMessage <pyroherd.raw.types.UpdateNewScheduledMessage>`
            - :obj:`UpdateNewStickerSet <pyroherd.raw.types.UpdateNewStickerSet>`
            - :obj:`UpdateNotifySettings <pyroherd.raw.types.UpdateNotifySettings>`
            - :obj:`UpdatePeerBlocked <pyroherd.raw.types.UpdatePeerBlocked>`
            - :obj:`UpdatePeerHistoryTTL <pyroherd.raw.types.UpdatePeerHistoryTTL>`
            - :obj:`UpdatePeerLocated <pyroherd.raw.types.UpdatePeerLocated>`
            - :obj:`UpdatePeerSettings <pyroherd.raw.types.UpdatePeerSettings>`
            - :obj:`UpdatePendingJoinRequests <pyroherd.raw.types.UpdatePendingJoinRequests>`
            - :obj:`UpdatePhoneCall <pyroherd.raw.types.UpdatePhoneCall>`
            - :obj:`UpdatePhoneCallSignalingData <pyroherd.raw.types.UpdatePhoneCallSignalingData>`
            - :obj:`UpdatePinnedChannelMessages <pyroherd.raw.types.UpdatePinnedChannelMessages>`
            - :obj:`UpdatePinnedDialogs <pyroherd.raw.types.UpdatePinnedDialogs>`
            - :obj:`UpdatePinnedMessages <pyroherd.raw.types.UpdatePinnedMessages>`
            - :obj:`UpdatePrivacy <pyroherd.raw.types.UpdatePrivacy>`
            - :obj:`UpdatePtsChanged <pyroherd.raw.types.UpdatePtsChanged>`
            - :obj:`UpdateReadChannelDiscussionInbox <pyroherd.raw.types.UpdateReadChannelDiscussionInbox>`
            - :obj:`UpdateReadChannelDiscussionOutbox <pyroherd.raw.types.UpdateReadChannelDiscussionOutbox>`
            - :obj:`UpdateReadChannelInbox <pyroherd.raw.types.UpdateReadChannelInbox>`
            - :obj:`UpdateReadChannelOutbox <pyroherd.raw.types.UpdateReadChannelOutbox>`
            - :obj:`UpdateReadFeaturedEmojiStickers <pyroherd.raw.types.UpdateReadFeaturedEmojiStickers>`
            - :obj:`UpdateReadFeaturedStickers <pyroherd.raw.types.UpdateReadFeaturedStickers>`
            - :obj:`UpdateReadHistoryInbox <pyroherd.raw.types.UpdateReadHistoryInbox>`
            - :obj:`UpdateReadHistoryOutbox <pyroherd.raw.types.UpdateReadHistoryOutbox>`
            - :obj:`UpdateReadMessagesContents <pyroherd.raw.types.UpdateReadMessagesContents>`
            - :obj:`UpdateRecentEmojiStatuses <pyroherd.raw.types.UpdateRecentEmojiStatuses>`
            - :obj:`UpdateRecentReactions <pyroherd.raw.types.UpdateRecentReactions>`
            - :obj:`UpdateRecentStickers <pyroherd.raw.types.UpdateRecentStickers>`
            - :obj:`UpdateSavedGifs <pyroherd.raw.types.UpdateSavedGifs>`
            - :obj:`UpdateSavedRingtones <pyroherd.raw.types.UpdateSavedRingtones>`
            - :obj:`UpdateServiceNotification <pyroherd.raw.types.UpdateServiceNotification>`
            - :obj:`UpdateStickerSets <pyroherd.raw.types.UpdateStickerSets>`
            - :obj:`UpdateStickerSetsOrder <pyroherd.raw.types.UpdateStickerSetsOrder>`
            - :obj:`UpdateTheme <pyroherd.raw.types.UpdateTheme>`
            - :obj:`UpdateTranscribedAudio <pyroherd.raw.types.UpdateTranscribedAudio>`
            - :obj:`UpdateUser <pyroherd.raw.types.UpdateUser>`
            - :obj:`UpdateUserEmojiStatus <pyroherd.raw.types.UpdateUserEmojiStatus>`
            - :obj:`UpdateUserName <pyroherd.raw.types.UpdateUserName>`
            - :obj:`UpdateUserPhone <pyroherd.raw.types.UpdateUserPhone>`
            - :obj:`UpdateUserStatus <pyroherd.raw.types.UpdateUserStatus>`
            - :obj:`UpdateUserTyping <pyroherd.raw.types.UpdateUserTyping>`
            - :obj:`UpdateWebPage <pyroherd.raw.types.UpdateWebPage>`
            - :obj:`UpdateWebViewResultSent <pyroherd.raw.types.UpdateWebViewResultSent>`
    """

    QUALNAME = "pyroherd.raw.base.Update"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/update")
