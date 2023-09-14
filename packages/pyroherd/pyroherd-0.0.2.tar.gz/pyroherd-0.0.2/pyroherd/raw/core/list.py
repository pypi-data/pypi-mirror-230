from typing import List as TList, Any

from .tl_object import TLObject


class List(TList[Any], TLObject):
    def __repr__(self) -> str:
        return f"pyroherd.raw.core.List([{','.join(TLObject.__repr__(i) for i in self)}])"
