import math

from PyQt5.QtCore import (
    QPointF,
)
from PyQt5.QtWidgets import (
    QWidget,
    QGraphicsProxyWidget,
    QGraphicsView,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from ...lib.Joystick import Joystick, JoystickLayout, JoystickSemicircleSide, MAX_DISPLACEMENT, NEUTRAL_THRESHOLD_PROPORTION, TRIGGER_DISTANCE
from .UseDpi import UseDpi
from ...lib.reactivity import watch

class UseJoystickControl:
    """Composable that sets up a joystick control"""

    def __init__(self, joystick: Joystick, view: QGraphicsView, widget: QWidget, proxy: QGraphicsProxyWidget, *, dpi: UseDpi):
        proxy_rect = proxy.boundingRect()
        proxy_center = QPointF(proxy_rect.width(), proxy_rect.height()) / 2

        
        def proxy_transform():
            return proxy.deviceTransform(view.viewportTransform())
        def proxy_transform_center_inverse():
            return proxy_transform().translate(proxy_center.x(), proxy_center.y()).inverted()[0]

        def pos_from_offset(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy_transform().translate(-proxy.x(), -proxy.y())
            return widget_transform.inverted()[0].map(touch.pos())

        def pos_from_center(touch: QTouchEvent.TouchPoint):
            return proxy_transform_center_inverse().map(touch.pos())
        self.widget_touch_pos = pos_from_center

        def touch_movement(touch: QTouchEvent.TouchPoint):
            return proxy_transform_center_inverse().map(touch.pos()) - proxy_transform_center_inverse().map(touch.lastPos())

        @watch(joystick.center.change)
        def update_proxy_center():
            proxy.setPos(joystick.center.value - proxy_center)

        proxy.setTransformOriginPoint(proxy_center)
        @watch(joystick.angle.change)
        def update_proxy_angle():
            proxy.setRotation(joystick.angle.value)


        if joystick.layout == JoystickLayout.VERTICAL:
            def on_initial_touch(touch: QTouchEvent.TouchPoint):
                joystick.center.value = QPointF(joystick.center.value.x(), pos_from_offset(touch).y())
                joystick.displacement.value = QPointF(0, 0)

                on_touch_begin(touch)
            
            def on_touch_begin(touch: QTouchEvent.TouchPoint):
                on_touch_update(touch)

            def on_touch_update(touch: QTouchEvent.TouchPoint):
                movement = touch_movement(touch)
                max_displacement = dpi.cm(MAX_DISPLACEMENT)

                new_displacement = joystick.displacement.value + movement
                if new_displacement.y() > max_displacement:
                    joystick.center.value = joystick.center.value + QPointF(movement.x(), new_displacement.y() - max_displacement)
                    joystick.displacement.value = QPointF(0, max_displacement)
                elif new_displacement.y() < -max_displacement:
                    joystick.center.value = joystick.center.value + QPointF(movement.x(), max_displacement + new_displacement.y())
                    joystick.displacement.value = QPointF(0, -max_displacement)
                else:
                    joystick.center.value = joystick.center.value + QPointF(movement.x(), 0)
                    joystick.displacement.value = QPointF(0, new_displacement.y())

                if abs(joystick.displacement.value.y()) < dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
                    joystick.selected_key_index.value = 1
                elif joystick.displacement.value.y() > 0:
                    joystick.selected_key_index.value = 2
                else:
                    joystick.selected_key_index.value = 0
            self.on_touch_update = on_touch_update

        elif joystick.layout == JoystickLayout.SEMICIRCLE:
            def on_initial_touch(touch: QTouchEvent.TouchPoint):
                joystick.center.value = pos_from_offset(touch)

                on_touch_begin(touch)
            
            def on_touch_begin(touch: QTouchEvent.TouchPoint):
                on_touch_update(touch)

            def on_touch_update(touch: QTouchEvent.TouchPoint):
                movement = touch_movement(touch)
                new_displacement = joystick.displacement.value + movement

                new_displacement_angle = math.atan2(new_displacement.y(), new_displacement.x())
                new_displacement_hypot = math.hypot(new_displacement.x(), new_displacement.y())

                max_displacement = dpi.cm(MAX_DISPLACEMENT)

                if new_displacement_hypot > max_displacement:
                    joystick.center.value = joystick.center.value + (new_displacement_hypot - max_displacement) * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
                    joystick.displacement.value = max_displacement * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
                else:
                    joystick.displacement.value = new_displacement

                if joystick.displacement_hypot < dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
                    joystick.selected_key_index.value = 0
                else: 
                    angle = (joystick.displacement_angle + math.tau / 16) % math.tau
                    joystick.selected_key_index.value = math.floor(angle / (math.tau / 8)) + 1
                


        elif joystick.layout == JoystickLayout.CIRCLE:
            def on_initial_touch(touch: QTouchEvent.TouchPoint):
                joystick.center.value = pos_from_offset(touch)

                on_touch_begin(touch)
            
            def on_touch_begin(touch: QTouchEvent.TouchPoint):
                on_touch_update(touch)

            def on_touch_update(touch: QTouchEvent.TouchPoint):
                movement = touch_movement(touch)
                new_displacement = joystick.displacement.value + movement

                new_displacement_angle = math.atan2(new_displacement.y(), new_displacement.x())
                new_displacement_hypot = math.hypot(new_displacement.x(), new_displacement.y())

                max_displacement = dpi.cm(MAX_DISPLACEMENT)

                if new_displacement_hypot > max_displacement:
                    joystick.center.value = joystick.center.value + (new_displacement_hypot - max_displacement) * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
                    joystick.displacement.value = max_displacement * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
                else:
                    joystick.displacement.value = new_displacement

                if joystick.displacement_hypot < dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
                    joystick.selected_key_index.value = 0
                else: 
                    angle = (joystick.displacement_angle + math.tau / 16) % math.tau
                    joystick.selected_key_index.value = math.floor(angle / (math.tau / 8)) + 1
            

        def on_touch_end():
            joystick.selected_key_index.value = None

        self.on_initial_touch = on_initial_touch
        self.on_touch_begin = on_touch_begin
        self.on_touch_update = on_touch_update
        self.on_touch_end = on_touch_end

