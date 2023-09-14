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

from io import BytesIO

from pyroherd.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyroherd.raw.core import TLObject
from pyroherd import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class UpdateShort(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.Updates`.

    Details:
        - Layer: ``143``
        - ID: ``78D4DEC1``

    Parameters:
        update: :obj:`Update <pyroherd.raw.base.Update>`
        date: ``int`` ``32-bit``

    See Also:
        This object can be returned by 77 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.GetNotifyExceptions <pyroherd.raw.functions.account.GetNotifyExceptions>`
            - :obj:`contacts.DeleteContacts <pyroherd.raw.functions.contacts.DeleteContacts>`
            - :obj:`contacts.AddContact <pyroherd.raw.functions.contacts.AddContact>`
            - :obj:`contacts.AcceptContact <pyroherd.raw.functions.contacts.AcceptContact>`
            - :obj:`contacts.GetLocated <pyroherd.raw.functions.contacts.GetLocated>`
            - :obj:`contacts.BlockFromReplies <pyroherd.raw.functions.contacts.BlockFromReplies>`
            - :obj:`messages.SendMessage <pyroherd.raw.functions.messages.SendMessage>`
            - :obj:`messages.SendMedia <pyroherd.raw.functions.messages.SendMedia>`
            - :obj:`messages.ForwardMessages <pyroherd.raw.functions.messages.ForwardMessages>`
            - :obj:`messages.EditChatTitle <pyroherd.raw.functions.messages.EditChatTitle>`
            - :obj:`messages.EditChatPhoto <pyroherd.raw.functions.messages.EditChatPhoto>`
            - :obj:`messages.AddChatUser <pyroherd.raw.functions.messages.AddChatUser>`
            - :obj:`messages.DeleteChatUser <pyroherd.raw.functions.messages.DeleteChatUser>`
            - :obj:`messages.CreateChat <pyroherd.raw.functions.messages.CreateChat>`
            - :obj:`messages.ImportChatInvite <pyroherd.raw.functions.messages.ImportChatInvite>`
            - :obj:`messages.StartBot <pyroherd.raw.functions.messages.StartBot>`
            - :obj:`messages.MigrateChat <pyroherd.raw.functions.messages.MigrateChat>`
            - :obj:`messages.SendInlineBotResult <pyroherd.raw.functions.messages.SendInlineBotResult>`
            - :obj:`messages.EditMessage <pyroherd.raw.functions.messages.EditMessage>`
            - :obj:`messages.GetAllDrafts <pyroherd.raw.functions.messages.GetAllDrafts>`
            - :obj:`messages.SetGameScore <pyroherd.raw.functions.messages.SetGameScore>`
            - :obj:`messages.SendScreenshotNotification <pyroherd.raw.functions.messages.SendScreenshotNotification>`
            - :obj:`messages.SendMultiMedia <pyroherd.raw.functions.messages.SendMultiMedia>`
            - :obj:`messages.UpdatePinnedMessage <pyroherd.raw.functions.messages.UpdatePinnedMessage>`
            - :obj:`messages.SendVote <pyroherd.raw.functions.messages.SendVote>`
            - :obj:`messages.GetPollResults <pyroherd.raw.functions.messages.GetPollResults>`
            - :obj:`messages.EditChatDefaultBannedRights <pyroherd.raw.functions.messages.EditChatDefaultBannedRights>`
            - :obj:`messages.SendScheduledMessages <pyroherd.raw.functions.messages.SendScheduledMessages>`
            - :obj:`messages.DeleteScheduledMessages <pyroherd.raw.functions.messages.DeleteScheduledMessages>`
            - :obj:`messages.SetHistoryTTL <pyroherd.raw.functions.messages.SetHistoryTTL>`
            - :obj:`messages.SetChatTheme <pyroherd.raw.functions.messages.SetChatTheme>`
            - :obj:`messages.HideChatJoinRequest <pyroherd.raw.functions.messages.HideChatJoinRequest>`
            - :obj:`messages.HideAllChatJoinRequests <pyroherd.raw.functions.messages.HideAllChatJoinRequests>`
            - :obj:`messages.ToggleNoForwards <pyroherd.raw.functions.messages.ToggleNoForwards>`
            - :obj:`messages.SendReaction <pyroherd.raw.functions.messages.SendReaction>`
            - :obj:`messages.GetMessagesReactions <pyroherd.raw.functions.messages.GetMessagesReactions>`
            - :obj:`messages.SetChatAvailableReactions <pyroherd.raw.functions.messages.SetChatAvailableReactions>`
            - :obj:`messages.SendWebViewData <pyroherd.raw.functions.messages.SendWebViewData>`
            - :obj:`help.GetAppChangelog <pyroherd.raw.functions.help.GetAppChangelog>`
            - :obj:`channels.CreateChannel <pyroherd.raw.functions.channels.CreateChannel>`
            - :obj:`channels.EditAdmin <pyroherd.raw.functions.channels.EditAdmin>`
            - :obj:`channels.EditTitle <pyroherd.raw.functions.channels.EditTitle>`
            - :obj:`channels.EditPhoto <pyroherd.raw.functions.channels.EditPhoto>`
            - :obj:`channels.JoinChannel <pyroherd.raw.functions.channels.JoinChannel>`
            - :obj:`channels.LeaveChannel <pyroherd.raw.functions.channels.LeaveChannel>`
            - :obj:`channels.InviteToChannel <pyroherd.raw.functions.channels.InviteToChannel>`
            - :obj:`channels.DeleteChannel <pyroherd.raw.functions.channels.DeleteChannel>`
            - :obj:`channels.ToggleSignatures <pyroherd.raw.functions.channels.ToggleSignatures>`
            - :obj:`channels.EditBanned <pyroherd.raw.functions.channels.EditBanned>`
            - :obj:`channels.DeleteHistory <pyroherd.raw.functions.channels.DeleteHistory>`
            - :obj:`channels.TogglePreHistoryHidden <pyroherd.raw.functions.channels.TogglePreHistoryHidden>`
            - :obj:`channels.EditCreator <pyroherd.raw.functions.channels.EditCreator>`
            - :obj:`channels.ToggleSlowMode <pyroherd.raw.functions.channels.ToggleSlowMode>`
            - :obj:`channels.ConvertToGigagroup <pyroherd.raw.functions.channels.ConvertToGigagroup>`
            - :obj:`channels.ToggleJoinToSend <pyroherd.raw.functions.channels.ToggleJoinToSend>`
            - :obj:`channels.ToggleJoinRequest <pyroherd.raw.functions.channels.ToggleJoinRequest>`
            - :obj:`payments.AssignAppStoreTransaction <pyroherd.raw.functions.payments.AssignAppStoreTransaction>`
            - :obj:`payments.AssignPlayMarketTransaction <pyroherd.raw.functions.payments.AssignPlayMarketTransaction>`
            - :obj:`payments.RestorePlayMarketReceipt <pyroherd.raw.functions.payments.RestorePlayMarketReceipt>`
            - :obj:`payments.RequestRecurringPayment <pyroherd.raw.functions.payments.RequestRecurringPayment>`
            - :obj:`phone.DiscardCall <pyroherd.raw.functions.phone.DiscardCall>`
            - :obj:`phone.SetCallRating <pyroherd.raw.functions.phone.SetCallRating>`
            - :obj:`phone.CreateGroupCall <pyroherd.raw.functions.phone.CreateGroupCall>`
            - :obj:`phone.JoinGroupCall <pyroherd.raw.functions.phone.JoinGroupCall>`
            - :obj:`phone.LeaveGroupCall <pyroherd.raw.functions.phone.LeaveGroupCall>`
            - :obj:`phone.InviteToGroupCall <pyroherd.raw.functions.phone.InviteToGroupCall>`
            - :obj:`phone.DiscardGroupCall <pyroherd.raw.functions.phone.DiscardGroupCall>`
            - :obj:`phone.ToggleGroupCallSettings <pyroherd.raw.functions.phone.ToggleGroupCallSettings>`
            - :obj:`phone.ToggleGroupCallRecord <pyroherd.raw.functions.phone.ToggleGroupCallRecord>`
            - :obj:`phone.EditGroupCallParticipant <pyroherd.raw.functions.phone.EditGroupCallParticipant>`
            - :obj:`phone.EditGroupCallTitle <pyroherd.raw.functions.phone.EditGroupCallTitle>`
            - :obj:`phone.ToggleGroupCallStartSubscription <pyroherd.raw.functions.phone.ToggleGroupCallStartSubscription>`
            - :obj:`phone.StartScheduledGroupCall <pyroherd.raw.functions.phone.StartScheduledGroupCall>`
            - :obj:`phone.JoinGroupCallPresentation <pyroherd.raw.functions.phone.JoinGroupCallPresentation>`
            - :obj:`phone.LeaveGroupCallPresentation <pyroherd.raw.functions.phone.LeaveGroupCallPresentation>`
            - :obj:`folders.EditPeerFolders <pyroherd.raw.functions.folders.EditPeerFolders>`
            - :obj:`folders.DeleteFolder <pyroherd.raw.functions.folders.DeleteFolder>`
    """

    __slots__: List[str] = ["update", "date"]

    ID = 0x78d4dec1
    QUALNAME = "types.UpdateShort"

    def __init__(self, *, update: "raw.base.Update", date: int) -> None:
        self.update = update  # Update
        self.date = date  # int

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateShort":
        # No flags
        
        update = TLObject.read(b)
        
        date = Int.read(b)
        
        return UpdateShort(update=update, date=date)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.update.write())
        
        b.write(Int(self.date))
        
        return b.getvalue()
