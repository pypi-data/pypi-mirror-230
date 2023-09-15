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

SecureValueType = Union[raw.types.SecureValueTypeAddress, raw.types.SecureValueTypeBankStatement, raw.types.SecureValueTypeDriverLicense, raw.types.SecureValueTypeEmail, raw.types.SecureValueTypeIdentityCard, raw.types.SecureValueTypeInternalPassport, raw.types.SecureValueTypePassport, raw.types.SecureValueTypePassportRegistration, raw.types.SecureValueTypePersonalDetails, raw.types.SecureValueTypePhone, raw.types.SecureValueTypeRentalAgreement, raw.types.SecureValueTypeTemporaryRegistration, raw.types.SecureValueTypeUtilityBill]


# noinspection PyRedeclaration
class SecureValueType:  # type: ignore
    """This base type has 13 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`SecureValueTypeAddress <pyroherd.raw.types.SecureValueTypeAddress>`
            - :obj:`SecureValueTypeBankStatement <pyroherd.raw.types.SecureValueTypeBankStatement>`
            - :obj:`SecureValueTypeDriverLicense <pyroherd.raw.types.SecureValueTypeDriverLicense>`
            - :obj:`SecureValueTypeEmail <pyroherd.raw.types.SecureValueTypeEmail>`
            - :obj:`SecureValueTypeIdentityCard <pyroherd.raw.types.SecureValueTypeIdentityCard>`
            - :obj:`SecureValueTypeInternalPassport <pyroherd.raw.types.SecureValueTypeInternalPassport>`
            - :obj:`SecureValueTypePassport <pyroherd.raw.types.SecureValueTypePassport>`
            - :obj:`SecureValueTypePassportRegistration <pyroherd.raw.types.SecureValueTypePassportRegistration>`
            - :obj:`SecureValueTypePersonalDetails <pyroherd.raw.types.SecureValueTypePersonalDetails>`
            - :obj:`SecureValueTypePhone <pyroherd.raw.types.SecureValueTypePhone>`
            - :obj:`SecureValueTypeRentalAgreement <pyroherd.raw.types.SecureValueTypeRentalAgreement>`
            - :obj:`SecureValueTypeTemporaryRegistration <pyroherd.raw.types.SecureValueTypeTemporaryRegistration>`
            - :obj:`SecureValueTypeUtilityBill <pyroherd.raw.types.SecureValueTypeUtilityBill>`
    """

    QUALNAME = "pyroherd.raw.base.SecureValueType"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/secure-value-type")
