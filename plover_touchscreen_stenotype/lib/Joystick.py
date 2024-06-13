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

class Joystick:
    def __init__(
        self,
        key_descriptors: tuple[tuple[str, str], ...],
        *,
        center: QPointF,
        angle: Ref[float]=Ref(0),
        aspect_ratio: Ref[float]=Ref(2),
        angle_center_offset=QPointF(0, 0),
    ):
        self.key_descriptors = key_descriptors

        self.__base_center = center

        self.center = Ref(center)
        self.angle = angle
        self.aspect_ratio = aspect_ratio

        self.displacement = Ref(QPointF(0, 0))

        self.angle_center_offset = angle_center_offset

        self.selected_key_index: "Ref[int | None]" = Ref(None)

    def reset_center(self):
        self.center.value = self.__base_center
        self.displacement.value = QPointF(0, 0)

    def distance(self, widget_touch_pos: QPoint):
        return widget_touch_pos.x()**2 + widget_touch_pos.y()**2