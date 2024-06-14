from enum import Enum, auto
import math

from PyQt5.QtCore import (
    QPointF,
    QPoint,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from .reactivity import Ref, on
from .UseDpi import UseDpi


MAX_DISPLACEMENT = 0.375
NEUTRAL_THRESHOLD_PROPORTION = 1/2
TRIGGER_DISTANCE = 1.25

class JoystickLayout(Enum):
    VERTICAL = auto()
    SEMICIRCLE = auto()
    CIRCLE = auto()

class JoystickSemicircleSide(Enum):
    RIGHT = auto()
    LEFT = auto()
    UP = auto()

class Joystick:
    def __init__(
        self,
        key_descriptors: tuple[tuple[str, str], ...],
        *,
        layout: JoystickLayout,
        semicircle_flat_side: "JoystickSemicircleSide | None"=None,
        center: QPointF,
        angle: Ref[float]=Ref(0),
        aspect_ratio: Ref[float]=Ref(2),
    ):
        if layout == JoystickLayout.SEMICIRCLE:
            assert semicircle_flat_side is not None
        else:
            assert semicircle_flat_side is None

        self.key_descriptors = key_descriptors

        self.__base_center = center

        self.layout = layout
        self.semicircle_flat_side = semicircle_flat_side

        self.center = Ref(center)
        self.angle = angle
        self.aspect_ratio = aspect_ratio

        self.displacement = Ref(QPointF(0, 0))

        self.selected_key_index: "Ref[int | None]" = Ref(None)

    def reset_center(self):
        self.center.value = self.__base_center
        self.displacement.value = QPointF(0, 0)

    def set_center_to_current(self):
        self.center.value = self.center.value + self.displacement.value
        self.displacement.value = QPointF(0, 0)

    def distance(self, widget_touch_pos: QPoint):
        return widget_touch_pos.x()**2 + widget_touch_pos.y()**2
    
    @property
    def displacement_angle(self):
        return math.atan2(self.displacement.value.y(), self.displacement.value.x())
    
    @property
    def displacement_hypot(self):
        return math.hypot(self.displacement.value.x(), self.displacement.value.y())