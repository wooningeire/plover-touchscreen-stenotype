import math
from typing import Callable, TypeVar, Optional

from plover.steno import Stroke

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QPointF,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLayout,
)

T = TypeVar("T")

def empty_stroke() -> Stroke:
    return Stroke.from_integer(0)

def immediate(fn: Callable[[], None]) -> Callable[[], None]:
    """Decorator that immediately calls a function"""
    fn()
    return fn

W = TypeVar("W", bound=QWidget)
L = TypeVar("L", bound=Optional[QLayout])
def render(widget: W, layout: L=None) -> Callable[[Callable[[W, L], tuple[int, ...]]], tuple[int, ...]]:
    if layout is not None:
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        widget.setLayout(layout)

    def handler(fn: Callable[[W, L], tuple[int, ...]]):
        return fn(widget, layout)
    return handler

def child(parent: QWidget, widget: W, layout: L=None) -> "Callable[[Callable[[W, L], tuple[int, ...]]], None]":
    def handler(fn: Callable[[W, L], tuple[int, ...]]=lambda widget, layout: ()):
        layout_args = render(widget, layout)(fn)

        parent_layout = parent.layout()
        if parent_layout is None: return
        parent_layout.addWidget(widget, *layout_args)
    return handler

def tick(fn: Callable):
    QTimer.singleShot(0, fn)

def not_none(value: "T | None") -> T:
    if value is None:
        raise Exception("value is None")
    return value


class Point:
    def __init__(self, x: float, y: float):
        self.__tuple = (x, y)

    @property
    def x(self):
        return self.__tuple[0]
    
    @property
    def y(self):
        return self.__tuple[1]
    
    def __add__(self, other: "Point"):
        return Point(self.x + other.x, self.y + other.y)
    
    def __radd__(self, other: "Point"):
        return Point(other.x + self.x, other.y + self.y)
    
    def __sub__(self, other: "Point"):
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, other: float):
        return Point(self.x * other, self.y * other)
    
    def __rmul__(self, other: float):
        return Point(other * self.x, other * self.y)
    
    def __truediv__(self, other: float):
        return Point(self.x / other, self.y / other)
    
    def to_qpointf(self):
        return QPointF(self.x, self.y)
    
    @staticmethod
    def from_qpointf(qpointf: QPointF):
        return Point(qpointf.x(), qpointf.y())
    
    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"
    
    def sqdist(self):
        return self.x**2 + self.y**2
    
    def hypot(self):
        return math.hypot(self.x, self.y)
    
    def with_hypot(self, hypot: float):
        angle = math.atan2(self.y, self.x)
        return hypot * Point(math.cos(angle), math.sin(angle))