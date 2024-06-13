from typing import Callable, TypeVar, Optional

from plover.steno import Stroke

from PyQt5.QtCore import (
    Qt,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLayout,
)

T = TypeVar("T")

def empty_stroke() -> Stroke:
    return Stroke.from_integer(0)

def immediate(fn: Callable[[], T]) -> T:
    """Decorator that immediately calls a function"""
    return fn()

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