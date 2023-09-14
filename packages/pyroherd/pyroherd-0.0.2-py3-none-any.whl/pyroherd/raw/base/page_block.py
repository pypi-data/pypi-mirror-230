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

PageBlock = Union[raw.types.PageBlockAnchor, raw.types.PageBlockAudio, raw.types.PageBlockAuthorDate, raw.types.PageBlockBlockquote, raw.types.PageBlockChannel, raw.types.PageBlockCollage, raw.types.PageBlockCover, raw.types.PageBlockDetails, raw.types.PageBlockDivider, raw.types.PageBlockEmbed, raw.types.PageBlockEmbedPost, raw.types.PageBlockFooter, raw.types.PageBlockHeader, raw.types.PageBlockKicker, raw.types.PageBlockList, raw.types.PageBlockMap, raw.types.PageBlockOrderedList, raw.types.PageBlockParagraph, raw.types.PageBlockPhoto, raw.types.PageBlockPreformatted, raw.types.PageBlockPullquote, raw.types.PageBlockRelatedArticles, raw.types.PageBlockSlideshow, raw.types.PageBlockSubheader, raw.types.PageBlockSubtitle, raw.types.PageBlockTable, raw.types.PageBlockTitle, raw.types.PageBlockUnsupported, raw.types.PageBlockVideo]


# noinspection PyRedeclaration
class PageBlock:  # type: ignore
    """This base type has 29 constructors available.

    Constructors:
        .. hlist::
            :columns: 2

            - :obj:`PageBlockAnchor <pyroherd.raw.types.PageBlockAnchor>`
            - :obj:`PageBlockAudio <pyroherd.raw.types.PageBlockAudio>`
            - :obj:`PageBlockAuthorDate <pyroherd.raw.types.PageBlockAuthorDate>`
            - :obj:`PageBlockBlockquote <pyroherd.raw.types.PageBlockBlockquote>`
            - :obj:`PageBlockChannel <pyroherd.raw.types.PageBlockChannel>`
            - :obj:`PageBlockCollage <pyroherd.raw.types.PageBlockCollage>`
            - :obj:`PageBlockCover <pyroherd.raw.types.PageBlockCover>`
            - :obj:`PageBlockDetails <pyroherd.raw.types.PageBlockDetails>`
            - :obj:`PageBlockDivider <pyroherd.raw.types.PageBlockDivider>`
            - :obj:`PageBlockEmbed <pyroherd.raw.types.PageBlockEmbed>`
            - :obj:`PageBlockEmbedPost <pyroherd.raw.types.PageBlockEmbedPost>`
            - :obj:`PageBlockFooter <pyroherd.raw.types.PageBlockFooter>`
            - :obj:`PageBlockHeader <pyroherd.raw.types.PageBlockHeader>`
            - :obj:`PageBlockKicker <pyroherd.raw.types.PageBlockKicker>`
            - :obj:`PageBlockList <pyroherd.raw.types.PageBlockList>`
            - :obj:`PageBlockMap <pyroherd.raw.types.PageBlockMap>`
            - :obj:`PageBlockOrderedList <pyroherd.raw.types.PageBlockOrderedList>`
            - :obj:`PageBlockParagraph <pyroherd.raw.types.PageBlockParagraph>`
            - :obj:`PageBlockPhoto <pyroherd.raw.types.PageBlockPhoto>`
            - :obj:`PageBlockPreformatted <pyroherd.raw.types.PageBlockPreformatted>`
            - :obj:`PageBlockPullquote <pyroherd.raw.types.PageBlockPullquote>`
            - :obj:`PageBlockRelatedArticles <pyroherd.raw.types.PageBlockRelatedArticles>`
            - :obj:`PageBlockSlideshow <pyroherd.raw.types.PageBlockSlideshow>`
            - :obj:`PageBlockSubheader <pyroherd.raw.types.PageBlockSubheader>`
            - :obj:`PageBlockSubtitle <pyroherd.raw.types.PageBlockSubtitle>`
            - :obj:`PageBlockTable <pyroherd.raw.types.PageBlockTable>`
            - :obj:`PageBlockTitle <pyroherd.raw.types.PageBlockTitle>`
            - :obj:`PageBlockUnsupported <pyroherd.raw.types.PageBlockUnsupported>`
            - :obj:`PageBlockVideo <pyroherd.raw.types.PageBlockVideo>`
    """

    QUALNAME = "pyroherd.raw.base.PageBlock"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.pyroherd.org/telegram/base/page-block")
