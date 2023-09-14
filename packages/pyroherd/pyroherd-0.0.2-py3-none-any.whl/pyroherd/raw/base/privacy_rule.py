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

PrivacyRule = Union[raw.types.PrivacyValueAllowAll, raw.types.PrivacyValueAllowChatParticipants, raw.types.PrivacyValueAllowContacts, raw.types.PrivacyValueAllowUsers, raw.types.PrivacyValueDisallowAll, raw.types.PrivacyValueDisallowChatParticipants, raw.types.PrivacyValueDisallowContacts, raw.types.PrivacyValueDisallowUsers]


# noinspection PyRedeclaration
class PrivacyRule:  # type: ignore
    """This base type has 8 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PrivacyValueAllowAll <pyroherd.raw.types.PrivacyValueAllowAll>`
            - :obj:`PrivacyValueAllowChatParticipants <pyroherd.raw.types.PrivacyValueAllowChatParticipants>`
            - :obj:`PrivacyValueAllowContacts <pyroherd.raw.types.PrivacyValueAllowContacts>`
            - :obj:`PrivacyValueAllowUsers <pyroherd.raw.types.PrivacyValueAllowUsers>`
            - :obj:`PrivacyValueDisallowAll <pyroherd.raw.types.PrivacyValueDisallowAll>`
            - :obj:`PrivacyValueDisallowChatParticipants <pyroherd.raw.types.PrivacyValueDisallowChatParticipants>`
            - :obj:`PrivacyValueDisallowContacts <pyroherd.raw.types.PrivacyValueDisallowContacts>`
            - :obj:`PrivacyValueDisallowUsers <pyroherd.raw.types.PrivacyValueDisallowUsers>`
    """

    QUALNAME = "pyroherd.raw.base.PrivacyRule"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/privacy-rule")
