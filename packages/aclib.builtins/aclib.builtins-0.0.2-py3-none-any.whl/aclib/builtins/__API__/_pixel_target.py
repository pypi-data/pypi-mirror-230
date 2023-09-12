from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self
    _Pos = tuple[int, int]


class BaseTargetMeta(type):
    none = property(lambda self: _none)

    def __new__(mcs, name, base, attr):
        attr['none'] = mcs.none
        return super().__new__(mcs, name, base, attr)


class BaseTarget(object, metaclass=BaseTargetMeta):
    none: BaseTarget

    def __init__(self, name: str, start: _Pos, end: _Pos, similarity: float):
        self.name = name
        self.start = start
        self.end = end
        self.similarity = similarity

    @property
    def center(self) -> _Pos:
        return int((self.start[0] + self.end[0]) / 2), int((self.start[1] + self.end[1]) / 2)

    def __repr__(self):
        if self != self.none:
            keys = ('name', 'start', 'center', 'end', 'similarity')
            values = (getattr(self, k) for k in keys)
            items = '{' + ", ".join([f"{k}: {v.__repr__()}" for k,v in zip(keys, values)]) + '}'
            return f'<{self.__class__.__name__} {items}>'
        else: return f'{self.__class__.__name__}.none'

    def __bool__(self):
        return self != self.none

    def offset(self, x: int, y: int) -> Self:
        if self != self.none:
            start = self.start[0]+x, self.start[1]+y
            end = self.end[0]+x, self.end[1]+y
            return self.__class__(self.name, start, end, self.similarity)
        else: return self


_none = BaseTarget('', (-1,-1), (-1,-1), 0.0)
