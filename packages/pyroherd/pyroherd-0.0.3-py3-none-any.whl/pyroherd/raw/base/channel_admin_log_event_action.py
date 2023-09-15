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

ChannelAdminLogEventAction = Union[raw.types.ChannelAdminLogEventActionChangeAbout, raw.types.ChannelAdminLogEventActionChangeAvailableReactions, raw.types.ChannelAdminLogEventActionChangeHistoryTTL, raw.types.ChannelAdminLogEventActionChangeLinkedChat, raw.types.ChannelAdminLogEventActionChangeLocation, raw.types.ChannelAdminLogEventActionChangePhoto, raw.types.ChannelAdminLogEventActionChangeStickerSet, raw.types.ChannelAdminLogEventActionChangeTitle, raw.types.ChannelAdminLogEventActionChangeUsername, raw.types.ChannelAdminLogEventActionChangeUsernames, raw.types.ChannelAdminLogEventActionCreateTopic, raw.types.ChannelAdminLogEventActionDefaultBannedRights, raw.types.ChannelAdminLogEventActionDeleteMessage, raw.types.ChannelAdminLogEventActionDeleteTopic, raw.types.ChannelAdminLogEventActionDiscardGroupCall, raw.types.ChannelAdminLogEventActionEditMessage, raw.types.ChannelAdminLogEventActionEditTopic, raw.types.ChannelAdminLogEventActionExportedInviteDelete, raw.types.ChannelAdminLogEventActionExportedInviteEdit, raw.types.ChannelAdminLogEventActionExportedInviteRevoke, raw.types.ChannelAdminLogEventActionParticipantInvite, raw.types.ChannelAdminLogEventActionParticipantJoin, raw.types.ChannelAdminLogEventActionParticipantJoinByInvite, raw.types.ChannelAdminLogEventActionParticipantJoinByRequest, raw.types.ChannelAdminLogEventActionParticipantLeave, raw.types.ChannelAdminLogEventActionParticipantMute, raw.types.ChannelAdminLogEventActionParticipantToggleAdmin, raw.types.ChannelAdminLogEventActionParticipantToggleBan, raw.types.ChannelAdminLogEventActionParticipantUnmute, raw.types.ChannelAdminLogEventActionParticipantVolume, raw.types.ChannelAdminLogEventActionPinTopic, raw.types.ChannelAdminLogEventActionSendMessage, raw.types.ChannelAdminLogEventActionStartGroupCall, raw.types.ChannelAdminLogEventActionStopPoll, raw.types.ChannelAdminLogEventActionToggleAntiSpam, raw.types.ChannelAdminLogEventActionToggleForum, raw.types.ChannelAdminLogEventActionToggleGroupCallSetting, raw.types.ChannelAdminLogEventActionToggleInvites, raw.types.ChannelAdminLogEventActionToggleNoForwards, raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden, raw.types.ChannelAdminLogEventActionToggleSignatures, raw.types.ChannelAdminLogEventActionToggleSlowMode, raw.types.ChannelAdminLogEventActionUpdatePinned]


# noinspection PyRedeclaration
class ChannelAdminLogEventAction:  # type: ignore
    """This base type has 43 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`ChannelAdminLogEventActionChangeAbout <pyroherd.raw.types.ChannelAdminLogEventActionChangeAbout>`
            - :obj:`ChannelAdminLogEventActionChangeAvailableReactions <pyroherd.raw.types.ChannelAdminLogEventActionChangeAvailableReactions>`
            - :obj:`ChannelAdminLogEventActionChangeHistoryTTL <pyroherd.raw.types.ChannelAdminLogEventActionChangeHistoryTTL>`
            - :obj:`ChannelAdminLogEventActionChangeLinkedChat <pyroherd.raw.types.ChannelAdminLogEventActionChangeLinkedChat>`
            - :obj:`ChannelAdminLogEventActionChangeLocation <pyroherd.raw.types.ChannelAdminLogEventActionChangeLocation>`
            - :obj:`ChannelAdminLogEventActionChangePhoto <pyroherd.raw.types.ChannelAdminLogEventActionChangePhoto>`
            - :obj:`ChannelAdminLogEventActionChangeStickerSet <pyroherd.raw.types.ChannelAdminLogEventActionChangeStickerSet>`
            - :obj:`ChannelAdminLogEventActionChangeTitle <pyroherd.raw.types.ChannelAdminLogEventActionChangeTitle>`
            - :obj:`ChannelAdminLogEventActionChangeUsername <pyroherd.raw.types.ChannelAdminLogEventActionChangeUsername>`
            - :obj:`ChannelAdminLogEventActionChangeUsernames <pyroherd.raw.types.ChannelAdminLogEventActionChangeUsernames>`
            - :obj:`ChannelAdminLogEventActionCreateTopic <pyroherd.raw.types.ChannelAdminLogEventActionCreateTopic>`
            - :obj:`ChannelAdminLogEventActionDefaultBannedRights <pyroherd.raw.types.ChannelAdminLogEventActionDefaultBannedRights>`
            - :obj:`ChannelAdminLogEventActionDeleteMessage <pyroherd.raw.types.ChannelAdminLogEventActionDeleteMessage>`
            - :obj:`ChannelAdminLogEventActionDeleteTopic <pyroherd.raw.types.ChannelAdminLogEventActionDeleteTopic>`
            - :obj:`ChannelAdminLogEventActionDiscardGroupCall <pyroherd.raw.types.ChannelAdminLogEventActionDiscardGroupCall>`
            - :obj:`ChannelAdminLogEventActionEditMessage <pyroherd.raw.types.ChannelAdminLogEventActionEditMessage>`
            - :obj:`ChannelAdminLogEventActionEditTopic <pyroherd.raw.types.ChannelAdminLogEventActionEditTopic>`
            - :obj:`ChannelAdminLogEventActionExportedInviteDelete <pyroherd.raw.types.ChannelAdminLogEventActionExportedInviteDelete>`
            - :obj:`ChannelAdminLogEventActionExportedInviteEdit <pyroherd.raw.types.ChannelAdminLogEventActionExportedInviteEdit>`
            - :obj:`ChannelAdminLogEventActionExportedInviteRevoke <pyroherd.raw.types.ChannelAdminLogEventActionExportedInviteRevoke>`
            - :obj:`ChannelAdminLogEventActionParticipantInvite <pyroherd.raw.types.ChannelAdminLogEventActionParticipantInvite>`
            - :obj:`ChannelAdminLogEventActionParticipantJoin <pyroherd.raw.types.ChannelAdminLogEventActionParticipantJoin>`
            - :obj:`ChannelAdminLogEventActionParticipantJoinByInvite <pyroherd.raw.types.ChannelAdminLogEventActionParticipantJoinByInvite>`
            - :obj:`ChannelAdminLogEventActionParticipantJoinByRequest <pyroherd.raw.types.ChannelAdminLogEventActionParticipantJoinByRequest>`
            - :obj:`ChannelAdminLogEventActionParticipantLeave <pyroherd.raw.types.ChannelAdminLogEventActionParticipantLeave>`
            - :obj:`ChannelAdminLogEventActionParticipantMute <pyroherd.raw.types.ChannelAdminLogEventActionParticipantMute>`
            - :obj:`ChannelAdminLogEventActionParticipantToggleAdmin <pyroherd.raw.types.ChannelAdminLogEventActionParticipantToggleAdmin>`
            - :obj:`ChannelAdminLogEventActionParticipantToggleBan <pyroherd.raw.types.ChannelAdminLogEventActionParticipantToggleBan>`
            - :obj:`ChannelAdminLogEventActionParticipantUnmute <pyroherd.raw.types.ChannelAdminLogEventActionParticipantUnmute>`
            - :obj:`ChannelAdminLogEventActionParticipantVolume <pyroherd.raw.types.ChannelAdminLogEventActionParticipantVolume>`
            - :obj:`ChannelAdminLogEventActionPinTopic <pyroherd.raw.types.ChannelAdminLogEventActionPinTopic>`
            - :obj:`ChannelAdminLogEventActionSendMessage <pyroherd.raw.types.ChannelAdminLogEventActionSendMessage>`
            - :obj:`ChannelAdminLogEventActionStartGroupCall <pyroherd.raw.types.ChannelAdminLogEventActionStartGroupCall>`
            - :obj:`ChannelAdminLogEventActionStopPoll <pyroherd.raw.types.ChannelAdminLogEventActionStopPoll>`
            - :obj:`ChannelAdminLogEventActionToggleAntiSpam <pyroherd.raw.types.ChannelAdminLogEventActionToggleAntiSpam>`
            - :obj:`ChannelAdminLogEventActionToggleForum <pyroherd.raw.types.ChannelAdminLogEventActionToggleForum>`
            - :obj:`ChannelAdminLogEventActionToggleGroupCallSetting <pyroherd.raw.types.ChannelAdminLogEventActionToggleGroupCallSetting>`
            - :obj:`ChannelAdminLogEventActionToggleInvites <pyroherd.raw.types.ChannelAdminLogEventActionToggleInvites>`
            - :obj:`ChannelAdminLogEventActionToggleNoForwards <pyroherd.raw.types.ChannelAdminLogEventActionToggleNoForwards>`
            - :obj:`ChannelAdminLogEventActionTogglePreHistoryHidden <pyroherd.raw.types.ChannelAdminLogEventActionTogglePreHistoryHidden>`
            - :obj:`ChannelAdminLogEventActionToggleSignatures <pyroherd.raw.types.ChannelAdminLogEventActionToggleSignatures>`
            - :obj:`ChannelAdminLogEventActionToggleSlowMode <pyroherd.raw.types.ChannelAdminLogEventActionToggleSlowMode>`
            - :obj:`ChannelAdminLogEventActionUpdatePinned <pyroherd.raw.types.ChannelAdminLogEventActionUpdatePinned>`
    """

    QUALNAME = "pyroherd.raw.base.ChannelAdminLogEventAction"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/channel-admin-log-event-action")
