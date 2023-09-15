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


class RequestSimpleWebView(TLObject):  # type: ignore
    """Telegram API method.

    Details:
        - Layer: ``158``
        - ID: ``299BEC8E``

    Parameters:
        bot: :obj:`InputUser <pyroherd.raw.base.InputUser>`
        url: ``str``
        platform: ``str``
        from_switch_webview (optional): ``bool``
        theme_params (optional): :obj:`DataJSON <pyroherd.raw.base.DataJSON>`

    Returns:
        :obj:`SimpleWebViewResult <pyroherd.raw.base.SimpleWebViewResult>`
    """

    __slots__: List[str] = ["bot", "url", "platform", "from_switch_webview", "theme_params"]

    ID = 0x299bec8e
    QUALNAME = "functions.messages.RequestSimpleWebView"

    def __init__(self, *, bot: "raw.base.InputUser", url: str, platform: str, from_switch_webview: Optional[bool] = None, theme_params: "raw.base.DataJSON" = None) -> None:
        self.bot = bot  # InputUser
        self.url = url  # string
        self.platform = platform  # string
        self.from_switch_webview = from_switch_webview  # flags.1?true
        self.theme_params = theme_params  # flags.0?DataJSON

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "RequestSimpleWebView":
        
        flags = Int.read(b)
        
        from_switch_webview = True if flags & (1 << 1) else False
        bot = TLObject.read(b)
        
        url = String.read(b)
        
        theme_params = TLObject.read(b) if flags & (1 << 0) else None
        
        platform = String.read(b)
        
        return RequestSimpleWebView(bot=bot, url=url, platform=platform, from_switch_webview=from_switch_webview, theme_params=theme_params)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.from_switch_webview else 0
        flags |= (1 << 0) if self.theme_params is not None else 0
        b.write(Int(flags))
        
        b.write(self.bot.write())
        
        b.write(String(self.url))
        
        if self.theme_params is not None:
            b.write(self.theme_params.write())
        
        b.write(String(self.platform))
        
        return b.getvalue()
