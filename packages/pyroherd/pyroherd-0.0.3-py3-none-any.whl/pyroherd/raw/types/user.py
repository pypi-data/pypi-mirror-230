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


class User(TLObject):  # type: ignore
    """This object is a constructor of the base type :obj:`~pyroherd.raw.base.User`.

    Details:
        - Layer: ``158``
        - ID: ``8F97C628``

    Parameters:
        id: ``int`` ``64-bit``
        is_self (optional): ``bool``
        contact (optional): ``bool``
        mutual_contact (optional): ``bool``
        deleted (optional): ``bool``
        bot (optional): ``bool``
        bot_chat_history (optional): ``bool``
        bot_nochats (optional): ``bool``
        verified (optional): ``bool``
        restricted (optional): ``bool``
        min (optional): ``bool``
        bot_inline_geo (optional): ``bool``
        support (optional): ``bool``
        scam (optional): ``bool``
        apply_min_photo (optional): ``bool``
        fake (optional): ``bool``
        bot_attach_menu (optional): ``bool``
        premium (optional): ``bool``
        attach_menu_enabled (optional): ``bool``
        bot_can_edit (optional): ``bool``
        access_hash (optional): ``int`` ``64-bit``
        first_name (optional): ``str``
        last_name (optional): ``str``
        username (optional): ``str``
        phone (optional): ``str``
        photo (optional): :obj:`UserProfilePhoto <pyroherd.raw.base.UserProfilePhoto>`
        status (optional): :obj:`UserStatus <pyroherd.raw.base.UserStatus>`
        bot_info_version (optional): ``int`` ``32-bit``
        restriction_reason (optional): List of :obj:`RestrictionReason <pyroherd.raw.base.RestrictionReason>`
        bot_inline_placeholder (optional): ``str``
        lang_code (optional): ``str``
        emoji_status (optional): :obj:`EmojiStatus <pyroherd.raw.base.EmojiStatus>`
        usernames (optional): List of :obj:`Username <pyroherd.raw.base.Username>`

    See Also:
        This object can be returned by 5 methods:

        .. hlist::
            :columns: 2

            - :obj:`account.UpdateProfile <pyroherd.raw.functions.account.UpdateProfile>`
            - :obj:`account.UpdateUsername <pyroherd.raw.functions.account.UpdateUsername>`
            - :obj:`account.ChangePhone <pyroherd.raw.functions.account.ChangePhone>`
            - :obj:`users.GetUsers <pyroherd.raw.functions.users.GetUsers>`
            - :obj:`contacts.ImportContactToken <pyroherd.raw.functions.contacts.ImportContactToken>`
    """

    __slots__: List[str] = ["id", "is_self", "contact", "mutual_contact", "deleted", "bot", "bot_chat_history", "bot_nochats", "verified", "restricted", "min", "bot_inline_geo", "support", "scam", "apply_min_photo", "fake", "bot_attach_menu", "premium", "attach_menu_enabled", "bot_can_edit", "access_hash", "first_name", "last_name", "username", "phone", "photo", "status", "bot_info_version", "restriction_reason", "bot_inline_placeholder", "lang_code", "emoji_status", "usernames"]

    ID = 0x8f97c628
    QUALNAME = "types.User"

    def __init__(self, *, id: int, is_self: Optional[bool] = None, contact: Optional[bool] = None, mutual_contact: Optional[bool] = None, deleted: Optional[bool] = None, bot: Optional[bool] = None, bot_chat_history: Optional[bool] = None, bot_nochats: Optional[bool] = None, verified: Optional[bool] = None, restricted: Optional[bool] = None, min: Optional[bool] = None, bot_inline_geo: Optional[bool] = None, support: Optional[bool] = None, scam: Optional[bool] = None, apply_min_photo: Optional[bool] = None, fake: Optional[bool] = None, bot_attach_menu: Optional[bool] = None, premium: Optional[bool] = None, attach_menu_enabled: Optional[bool] = None, bot_can_edit: Optional[bool] = None, access_hash: Optional[int] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, username: Optional[str] = None, phone: Optional[str] = None, photo: "raw.base.UserProfilePhoto" = None, status: "raw.base.UserStatus" = None, bot_info_version: Optional[int] = None, restriction_reason: Optional[List["raw.base.RestrictionReason"]] = None, bot_inline_placeholder: Optional[str] = None, lang_code: Optional[str] = None, emoji_status: "raw.base.EmojiStatus" = None, usernames: Optional[List["raw.base.Username"]] = None) -> None:
        self.id = id  # long
        self.is_self = is_self  # flags.10?true
        self.contact = contact  # flags.11?true
        self.mutual_contact = mutual_contact  # flags.12?true
        self.deleted = deleted  # flags.13?true
        self.bot = bot  # flags.14?true
        self.bot_chat_history = bot_chat_history  # flags.15?true
        self.bot_nochats = bot_nochats  # flags.16?true
        self.verified = verified  # flags.17?true
        self.restricted = restricted  # flags.18?true
        self.min = min  # flags.20?true
        self.bot_inline_geo = bot_inline_geo  # flags.21?true
        self.support = support  # flags.23?true
        self.scam = scam  # flags.24?true
        self.apply_min_photo = apply_min_photo  # flags.25?true
        self.fake = fake  # flags.26?true
        self.bot_attach_menu = bot_attach_menu  # flags.27?true
        self.premium = premium  # flags.28?true
        self.attach_menu_enabled = attach_menu_enabled  # flags.29?true
        self.bot_can_edit = bot_can_edit  # flags2.1?true
        self.access_hash = access_hash  # flags.0?long
        self.first_name = first_name  # flags.1?string
        self.last_name = last_name  # flags.2?string
        self.username = username  # flags.3?string
        self.phone = phone  # flags.4?string
        self.photo = photo  # flags.5?UserProfilePhoto
        self.status = status  # flags.6?UserStatus
        self.bot_info_version = bot_info_version  # flags.14?int
        self.restriction_reason = restriction_reason  # flags.18?Vector<RestrictionReason>
        self.bot_inline_placeholder = bot_inline_placeholder  # flags.19?string
        self.lang_code = lang_code  # flags.22?string
        self.emoji_status = emoji_status  # flags.30?EmojiStatus
        self.usernames = usernames  # flags2.0?Vector<Username>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "User":
        
        flags = Int.read(b)
        
        is_self = True if flags & (1 << 10) else False
        contact = True if flags & (1 << 11) else False
        mutual_contact = True if flags & (1 << 12) else False
        deleted = True if flags & (1 << 13) else False
        bot = True if flags & (1 << 14) else False
        bot_chat_history = True if flags & (1 << 15) else False
        bot_nochats = True if flags & (1 << 16) else False
        verified = True if flags & (1 << 17) else False
        restricted = True if flags & (1 << 18) else False
        min = True if flags & (1 << 20) else False
        bot_inline_geo = True if flags & (1 << 21) else False
        support = True if flags & (1 << 23) else False
        scam = True if flags & (1 << 24) else False
        apply_min_photo = True if flags & (1 << 25) else False
        fake = True if flags & (1 << 26) else False
        bot_attach_menu = True if flags & (1 << 27) else False
        premium = True if flags & (1 << 28) else False
        attach_menu_enabled = True if flags & (1 << 29) else False
        flags2 = Int.read(b)
        
        bot_can_edit = True if flags2 & (1 << 1) else False
        id = Long.read(b)
        
        access_hash = Long.read(b) if flags & (1 << 0) else None
        first_name = String.read(b) if flags & (1 << 1) else None
        last_name = String.read(b) if flags & (1 << 2) else None
        username = String.read(b) if flags & (1 << 3) else None
        phone = String.read(b) if flags & (1 << 4) else None
        photo = TLObject.read(b) if flags & (1 << 5) else None
        
        status = TLObject.read(b) if flags & (1 << 6) else None
        
        bot_info_version = Int.read(b) if flags & (1 << 14) else None
        restriction_reason = TLObject.read(b) if flags & (1 << 18) else []
        
        bot_inline_placeholder = String.read(b) if flags & (1 << 19) else None
        lang_code = String.read(b) if flags & (1 << 22) else None
        emoji_status = TLObject.read(b) if flags & (1 << 30) else None
        
        usernames = TLObject.read(b) if flags2 & (1 << 0) else []
        
        return User(id=id, is_self=is_self, contact=contact, mutual_contact=mutual_contact, deleted=deleted, bot=bot, bot_chat_history=bot_chat_history, bot_nochats=bot_nochats, verified=verified, restricted=restricted, min=min, bot_inline_geo=bot_inline_geo, support=support, scam=scam, apply_min_photo=apply_min_photo, fake=fake, bot_attach_menu=bot_attach_menu, premium=premium, attach_menu_enabled=attach_menu_enabled, bot_can_edit=bot_can_edit, access_hash=access_hash, first_name=first_name, last_name=last_name, username=username, phone=phone, photo=photo, status=status, bot_info_version=bot_info_version, restriction_reason=restriction_reason, bot_inline_placeholder=bot_inline_placeholder, lang_code=lang_code, emoji_status=emoji_status, usernames=usernames)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 10) if self.is_self else 0
        flags |= (1 << 11) if self.contact else 0
        flags |= (1 << 12) if self.mutual_contact else 0
        flags |= (1 << 13) if self.deleted else 0
        flags |= (1 << 14) if self.bot else 0
        flags |= (1 << 15) if self.bot_chat_history else 0
        flags |= (1 << 16) if self.bot_nochats else 0
        flags |= (1 << 17) if self.verified else 0
        flags |= (1 << 18) if self.restricted else 0
        flags |= (1 << 20) if self.min else 0
        flags |= (1 << 21) if self.bot_inline_geo else 0
        flags |= (1 << 23) if self.support else 0
        flags |= (1 << 24) if self.scam else 0
        flags |= (1 << 25) if self.apply_min_photo else 0
        flags |= (1 << 26) if self.fake else 0
        flags |= (1 << 27) if self.bot_attach_menu else 0
        flags |= (1 << 28) if self.premium else 0
        flags |= (1 << 29) if self.attach_menu_enabled else 0
        flags |= (1 << 0) if self.access_hash is not None else 0
        flags |= (1 << 1) if self.first_name is not None else 0
        flags |= (1 << 2) if self.last_name is not None else 0
        flags |= (1 << 3) if self.username is not None else 0
        flags |= (1 << 4) if self.phone is not None else 0
        flags |= (1 << 5) if self.photo is not None else 0
        flags |= (1 << 6) if self.status is not None else 0
        flags |= (1 << 14) if self.bot_info_version is not None else 0
        flags |= (1 << 18) if self.restriction_reason else 0
        flags |= (1 << 19) if self.bot_inline_placeholder is not None else 0
        flags |= (1 << 22) if self.lang_code is not None else 0
        flags |= (1 << 30) if self.emoji_status is not None else 0
        b.write(Int(flags))
        flags2 = 0
        flags2 |= (1 << 1) if self.bot_can_edit else 0
        flags2 |= (1 << 0) if self.usernames else 0
        b.write(Int(flags2))
        
        b.write(Long(self.id))
        
        if self.access_hash is not None:
            b.write(Long(self.access_hash))
        
        if self.first_name is not None:
            b.write(String(self.first_name))
        
        if self.last_name is not None:
            b.write(String(self.last_name))
        
        if self.username is not None:
            b.write(String(self.username))
        
        if self.phone is not None:
            b.write(String(self.phone))
        
        if self.photo is not None:
            b.write(self.photo.write())
        
        if self.status is not None:
            b.write(self.status.write())
        
        if self.bot_info_version is not None:
            b.write(Int(self.bot_info_version))
        
        if self.restriction_reason:
            b.write(Vector(self.restriction_reason))
        
        if self.bot_inline_placeholder is not None:
            b.write(String(self.bot_inline_placeholder))
        
        if self.lang_code is not None:
            b.write(String(self.lang_code))
        
        if self.emoji_status is not None:
            b.write(self.emoji_status.write())
        
        if self.usernames:
            b.write(Vector(self.usernames))
        
        return b.getvalue()
