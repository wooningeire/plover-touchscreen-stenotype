from PyQt5.QtCore import (
    Qt,
    QEvent,
    QRectF,
    pyqtSignal,
    QTimer,
    QPoint,
    QPointF,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QGridLayout,
    QToolButton,
)
from PyQt5.QtGui import (
    QTouchEvent,
    QPointingDeviceUniqueId,
)

import plover.log
from plover.steno import Stroke

import math
from enum import Enum, auto
from typing import TYPE_CHECKING

from .KeyWidget import KeyWidget
from ..settings import Settings
from ..lib.Joystick import Joystick, MAX_DISPLACEMENT, NEUTRAL_THRESHOLD_PROPORTION, TRIGGER_DISTANCE
from ..lib.reactivity import Ref, computed, on, on_many, watch, watch_many
from ..lib.UseDpi import UseDpi
from ..lib.constants import GRAPHICS_VIEW_STYLE, KEY_STYLESHEET, KEY_CONTAINER_STYLE
from ..lib.util import child, empty_stroke, render, not_none
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object


class JoysticksState(Enum):
    GATHERING_TOUCHES = auto()
    AWAITING_TAPS = auto()

class JoysticksWidget(QWidget):
    end_stroke = pyqtSignal(Stroke)
    current_stroke_change = pyqtSignal(Stroke)


    def __init__(self, settings: Settings, left_right_width_diff: Ref[float], parent: "QWidget | None"=None):
        super().__init__(parent)

        key_widgets: list[KeyWidget] = []

        tapped_joysticks: Ref[dict[Joystick, KeyWidget]] = Ref({})
        tapped_key_widgets = computed(lambda: set(key_widget for key_widget in tapped_joysticks.value.values()), tapped_joysticks)

        def compute_current_stroke():
            current_stroke = empty_stroke()
            for key_widget in tapped_joysticks.value.values():
                current_stroke += key_widget.substroke
            return current_stroke
        current_stroke = computed(compute_current_stroke, tapped_joysticks)
        
        @on(current_stroke.change)
        def emit_stroke_change():
            if len(current_stroke.value.keys()) == 0: return
            self.current_stroke_change.emit(current_stroke.value)

        selected_joysticks: "dict[int, _GridJoystickWidget | _VerticalJoystickWidget]" = {}
        selected_key_widgets: Ref[set[KeyWidget]] = Ref(set())

        used_joysticks: set[Joystick] = set()


        dpi = UseDpi(self)


        joysticks = (
            Joystick(
                (
                    ("^+S", ""),
                    ("S", "S"),
                    ("S", "S"),
                    ("+S", ""),
                    ("+", "+"),
                    ("^+", ""),
                    ("^", "^"),
                    ("^S", ""),
                    ("S", "S"),
                ),
                center=QPointF(dpi.cm(-10), -dpi.cm(2 * settings.pinky_stagger_fac)),
            ),
            Joystick(
                (
                    ("T", "T"),
                    ("TK", ""),
                    ("K", "K"),
                ),
                center=QPointF(dpi.cm(-7.5), -dpi.cm(2 * settings.ring_stagger_fac)),
            ),
            Joystick(
                (
                    ("P", "P"),
                    ("PW", ""),
                    ("W", "W"),
                ),
                center=QPointF(dpi.cm(-5), -dpi.cm(2 * settings.middle_stagger_fac)),
            ),
            Joystick(
                (
                    ("&HR", ""),
                    ("&", "&&"),
                    ("&", "&&"),
                    ("&R", ""),
                    ("R", "R"),
                    ("HR", ""),
                    ("H", "H"),
                    ("&H", ""),
                    ("&", "&&"),
                ),
                center=QPointF(dpi.cm(-2.5), -dpi.cm(2 * settings.index_stagger_fac)),
            ),
            Joystick(
                (
                    ("*FR", ""),
                    ("-FR", ""),
                    ("-R", "R"),
                    ("*R", ""),
                    ("*", "*"),
                    ("*", "*"),
                    ("*", "*"),
                    ("*F", ""),
                    ("-F", "F"),
                ),
                center=QPointF(dpi.cm(2.5), -dpi.cm(2 * settings.index_stagger_fac)),
            ),
            Joystick(
                (
                    ("-P", "P"),
                    ("-PB", ""),
                    ("-B", "B"),
                ),
                center=QPointF(dpi.cm(5), -dpi.cm(2 * settings.middle_stagger_fac)),
            ),
            Joystick(
                (
                    ("-L", "L"),
                    ("-LG", ""),
                    ("-G", "G"),
                ),
                center=QPointF(dpi.cm(7.5), -dpi.cm(2 * settings.ring_stagger_fac)),
            ),
            Joystick(
                (
                    ("-TSDZ", ""),
                    ("-DZ", ""),
                    ("-Z", "Z"),
                    ("-SZ", ""),
                    ("-S", "S"),
                    ("-TS", ""),
                    ("-T", "T"),
                    ("-TD", ""),
                    ("-D", "D"),
                ),
                center=QPointF(dpi.cm(10), -dpi.cm(2 * settings.pinky_stagger_fac)),
            ),
            Joystick(
                (
                    ("#AO", ""),
                    ("#O", ""),
                    ("#", "#"),
                    ("#", "#"),
                    ("#", "#"),
                    ("#A", ""),
                    ("A", "A"),
                    ("AO", ""),
                    ("O", "O"),
                ),
                center=QPointF(dpi.cm(-2), dpi.cm(2)),
                angle=settings.vowel_rows_angle_ref,
            ),
            Joystick(
                (
                    ("_EU", ""),
                    ("_U", ""),
                    ("_", "_"),
                    ("_", "_"),
                    ("_", "_"),
                    ("_E", ""),
                    ("E", "E"),
                    ("EU", ""),
                    ("U", "U"),
                ),
                center=QPointF(dpi.cm(2), dpi.cm(2)),
                angle=computed(lambda: -settings.vowel_rows_angle, settings.vowel_rows_angle_ref),
            ),
        )

        joystick_widgets: "dict[Joystick, _GridJoystickWidget | _VerticalJoystickWidget]" = {}

        for joystick in reversed(joysticks):
            @on(joystick.selected_key_index.change)
            def update_keys(key_widget: KeyWidget):
                new_selected_key_widgets = set()
                for joystick in joysticks:
                    if joystick.selected_key_index.value is None: continue
                    new_selected_key_widgets.add(joystick_widgets[joystick].key_widgets[joystick.selected_key_index.value])
                selected_key_widgets.value = new_selected_key_widgets


        @render(self, QGridLayout())
        def render_widget(widget: QWidget, layout: QGridLayout):
            scene = QGraphicsScene(widget)

            @child(self, QGraphicsView(scene))
            def render_widget(view: QGraphicsView, _: None):
                nonlocal joystick_widgets

                view.setStyleSheet(GRAPHICS_VIEW_STYLE)
            
                rect = QRectF(view.rect())
                rect.moveCenter(QPointF(0, 0))

                view.setSceneRect(rect)

                joystick_widgets = {
                    joysticks[0]: _GridJoystickWidget(view, joysticks[0]),
                    joysticks[1]: _VerticalJoystickWidget(view, joysticks[1]),
                    joysticks[2]: _VerticalJoystickWidget(view, joysticks[2]),
                    joysticks[3]: _GridJoystickWidget(view, joysticks[3]),
                    joysticks[4]: _GridJoystickWidget(view, joysticks[4]),
                    joysticks[5]: _VerticalJoystickWidget(view, joysticks[5]),
                    joysticks[6]: _VerticalJoystickWidget(view, joysticks[6]),
                    joysticks[7]: _GridJoystickWidget(view, joysticks[7]),
                    joysticks[8]: _GridJoystickWidget(view, joysticks[8]),
                    joysticks[9]: _GridJoystickWidget(view, joysticks[9]),
                }
                for joystick_widget in joystick_widgets.values():
                    key_widgets.extend(joystick_widget.key_widgets)

                left_bank = not_none(scene.createItemGroup(joystick_widgets[joystick].proxy for joystick in joysticks[0:4]))
                right_bank = not_none(scene.createItemGroup(joystick_widgets[joystick].proxy for joystick in joysticks[4:8]))

                @watch(settings.main_rows_angle_ref.change)
                def set_left_bank_angle():
                    left_bank.setRotation(settings.main_rows_angle)

                @watch(settings.main_rows_angle_ref.change)
                def set_right_bank_angle():
                    right_bank.setRotation(-settings.main_rows_angle)

                return ()
            
            return ()
        


        self.setStyleSheet(KEY_STYLESHEET)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        

        @on_many(tapped_key_widgets.change, selected_key_widgets.change, current_stroke.change)
        def update_key_widget_styles_and_state():
            for key_widget in key_widgets:
                old_touched, old_matched, old_matched_soft = key_widget.touched, key_widget.matched, key_widget.matched_soft

                if key_widget in tapped_key_widgets.value:
                    key_widget.touched = True
                    key_widget.matched = True
                    key_widget.matched_soft = False

                elif key_widget in selected_key_widgets.value:
                    key_widget.touched = False
                    key_widget.matched = False
                    key_widget.matched_soft = True

                elif key_widget.substroke in current_stroke.value:
                    key_widget.touched = False
                    key_widget.matched = True
                    key_widget.matched_soft = False

                else:
                    key_widget.touched = False
                    key_widget.matched = False
                    key_widget.matched_soft = False


                if (old_touched, old_matched, old_matched_soft) != (key_widget.touched, key_widget.matched, key_widget.matched_soft):
                    # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                    # self.style().unpolish(key_widget)
                    not_none(self.style()).polish(key_widget)
        

        n_expected_touches = 0
        state = JoysticksState.GATHERING_TOUCHES

        def joysticks_sorted_by_distance(touch: QTouchEvent.TouchPoint):
            filtered_joysticks: list[tuple[Joystick, int]] = []

            for joystick in joysticks:
                joystick_widget = joystick_widgets[joystick]
                distance = joystick.distance(joystick_widget.widget_touch_pos(touch))
                
                if distance > dpi.cm(TRIGGER_DISTANCE)**2:
                    continue

                filtered_joysticks.append((joystick, distance))

            sorted_joysticks = sorted(filtered_joysticks, key=lambda pair: pair[1])
            return tuple(pair[0] for pair in sorted_joysticks)


        def handle_touch_event(event: QTouchEvent):
            nonlocal current_stroke
            nonlocal selected_key_widgets
            nonlocal tapped_joysticks
            nonlocal selected_joysticks
            nonlocal n_expected_touches
            nonlocal state
            nonlocal used_joysticks

            touch_points = event.touchPoints()

            new_selected_joysticks = selected_joysticks.copy()

            new_press = False
            new_release = False

            for touch in touch_points:
                if touch.state() == Qt.TouchPointPressed:
                    for joystick in joysticks_sorted_by_distance(touch):
                        joystick_widget = joystick_widgets[joystick]

                        if joystick_widget in new_selected_joysticks.values():
                            continue

                        new_press = True
                        new_selected_joysticks[touch.id()] = joystick_widget
                        if joystick not in used_joysticks:
                            used_joysticks.add(joystick)
                            joystick_widget.on_initial_touch(touch)
                        else:
                            joystick_widget.on_touch_begin(touch)

                        if state == JoysticksState.AWAITING_TAPS:
                            tapped_joysticks.value[joystick] = joystick_widget.key_widgets[joystick.selected_key_index.value]
                            tapped_joysticks.emit()

                        break

                elif touch.state() == Qt.TouchPointMoved:
                    if touch.id() in new_selected_joysticks:
                        new_selected_joysticks[touch.id()].on_touch_update(touch)

                elif touch.state() == Qt.TouchPointReleased:
                    if touch.id() in new_selected_joysticks:
                        new_release = True
                        new_selected_joysticks[touch.id()].on_touch_end()
                        del new_selected_joysticks[touch.id()]

            selected_joysticks = new_selected_joysticks
            n_expected_touches = max(n_expected_touches, len(selected_joysticks))

            if new_release and state == JoysticksState.GATHERING_TOUCHES:
                state = JoysticksState.AWAITING_TAPS

            if new_release and len(selected_joysticks) == 0:
                state = JoysticksState.GATHERING_TOUCHES
                n_expected_touches = 0

                selected_key_widgets.value = set()
                tapped_joysticks.value = {}
                used_joysticks = set()

                for joystick in joysticks:
                    joystick.reset_center()
            

            if (
                state == JoysticksState.AWAITING_TAPS
                    and new_press
                    and len(selected_joysticks) >= n_expected_touches
                    and len(current_stroke.value.keys()) > 0
            ):
                self.end_stroke.emit(current_stroke.value)

                tapped_joysticks.value = {}

            update_key_widget_styles_and_state()
        self.__handle_touch_event = handle_touch_event


    def event(self, event: QEvent) -> bool:
        """(override)"""

        if not isinstance(event, QTouchEvent):
            return super().event(event)
        
        self.__handle_touch_event(event)

        return True
    

class _JoystickTriggerWidget(QToolButton):
    def __init__(self, trigger_distance: float):
        super().__init__()

        dpi = UseDpi(self)

        @watch(dpi.change)
        def set_button_size():
            self.setFixedSize(dpi.cm(trigger_distance * 2), dpi.cm(trigger_distance * 2))

class _VerticalJoystickWidget(QWidget):
    def __init__(self, view: QGraphicsView, joystick: Joystick):
        super().__init__()

        key_widgets: list[KeyWidget] = [KeyWidget(Stroke.from_steno(steno), label) for steno, label in joystick.key_descriptors]
        self.__key_widgets = key_widgets
        dpi = UseDpi(self)


        self.setStyleSheet(KEY_STYLESHEET)


        @render(self, QGridLayout())
        def render_widget(widget: QWidget, layout: QGridLayout):
            @child(widget, _JoystickTriggerWidget(TRIGGER_DISTANCE))
            def render_widget(button: _JoystickTriggerWidget, _: None):
                return 0, 0, Qt.AlignCenter
            
            @child(widget, QWidget(), QVBoxLayout())
            def render_widget(joystick_container: QWidget, layout: QVBoxLayout):
                for key_widget in key_widgets:
                    layout.addWidget(key_widget)

                @watch(dpi.change)
                def set_size():
                    joystick_container.setFixedWidth(dpi.cm(MAX_DISPLACEMENT))
                    key_widgets[1].setFixedHeight(dpi.cm(MAX_DISPLACEMENT * 2))
                
                return 0, 0, Qt.AlignCenter

            return ()

        self.__proxy = proxy = not_none(not_none(view.scene()).addWidget(self))
        widget_rect = proxy.boundingRect()

        @watch(joystick.center.change)
        def update_proxy_center():
            proxy.setPos(joystick.center.value - QPointF(widget_rect.width(), widget_rect.height()) / 2)

        proxy.setTransformOriginPoint(widget_rect.width() / 2, widget_rect.height() / 2)

        @watch(joystick.angle.change)
        def update_proxy_angle():
            proxy.setRotation(joystick.angle.value)

        def widget_touch_pos(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(widget_rect.width() / 2, widget_rect.height() / 2)
            return widget_transform.inverted()[0].map(touch.pos())
        self.widget_touch_pos = widget_touch_pos
    
    
        def on_initial_touch(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(-proxy.x(), -proxy.y())
            touch_pos = widget_transform.inverted()[0].map(touch.pos())
            joystick.center.value = QPointF(joystick.center.value.x(), touch_pos.y())
            joystick.displacement.value = QPointF(0, 0)

            update_proxy_center()

            on_touch_begin(touch)
        self.on_initial_touch = on_initial_touch

        
        def on_touch_begin(touch: QTouchEvent.TouchPoint):
            on_touch_update(touch)
        self.on_touch_begin = on_touch_begin


        def on_touch_update(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(widget_rect.width() / 2, widget_rect.height() / 2)
            movement = widget_transform.inverted()[0].map(touch.pos()) - widget_transform.inverted()[0].map(touch.lastPos())

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


            joystick.selected_key_index.value = new_selected_key_widget()
        self.on_touch_update = on_touch_update

        def new_selected_key_widget():
            if abs(joystick.displacement.value.y()) < dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
                return 1

            if joystick.displacement.value.y() > 0:
                return 2
            
            return 0

        def on_touch_end():
            joystick.selected_key_index.value = None
        self.on_touch_end = on_touch_end

    @property
    def key_widgets(self):
        return self.__key_widgets

    @property
    def proxy(self):
        return self.__proxy

class _GridJoystickWidget(QWidget):
    def __init__(self, view: QGraphicsView, joystick: Joystick):
        super().__init__()


        key_widgets: tuple[KeyWidget, ...] = tuple(KeyWidget(Stroke.from_steno(steno), label) for steno, label in joystick.key_descriptors)
        self.__key_widgets = key_widgets
        dpi = UseDpi(self)

        
        self.setStyleSheet(KEY_STYLESHEET)


        @render(self, QGridLayout())
        def render_widget(widget: QWidget, layout: QGridLayout):
            @child(widget, _JoystickTriggerWidget(TRIGGER_DISTANCE))
            def render_widget(button: _JoystickTriggerWidget, _: None):
                return 0, 0, Qt.AlignCenter
            
            @child(widget, QWidget(), QGridLayout())
            def render_widget(joystick_container: QWidget, layout: QGridLayout):
                @watch(dpi.change)
                def set_size():
                    key_widgets[0].setFixedSize(dpi.cm(MAX_DISPLACEMENT * 2), dpi.cm(MAX_DISPLACEMENT * 2))

                layout.addWidget(key_widgets[0], 1, 1)
                layout.addWidget(key_widgets[1], 1, 2)
                layout.addWidget(key_widgets[2], 2, 2)
                layout.addWidget(key_widgets[3], 2, 1)
                layout.addWidget(key_widgets[4], 2, 0)
                layout.addWidget(key_widgets[5], 1, 0)
                layout.addWidget(key_widgets[6], 0, 0)
                layout.addWidget(key_widgets[7], 0, 1)
                layout.addWidget(key_widgets[8], 0, 2)
                
                return 0, 0, Qt.AlignCenter

            return ()

        self.__proxy = proxy = not_none(not_none(view.scene()).addWidget(self))
        widget_rect = proxy.boundingRect()


        @watch(joystick.center.change)
        def update_proxy_center():
            proxy.setPos(joystick.center.value - QPointF(widget_rect.width(), widget_rect.height()) / 2)

        proxy.setTransformOriginPoint(widget_rect.width() / 2, widget_rect.height() / 2)

        @watch(joystick.angle.change)
        def update_proxy_angle():
            proxy.setRotation(joystick.angle.value)
    

        def widget_touch_pos(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(widget_rect.width() / 2, widget_rect.height() / 2)
            return widget_transform.inverted()[0].map(touch.pos())
        self.widget_touch_pos = widget_touch_pos
        
        def on_initial_touch(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(-proxy.x(), -proxy.y())
            touch_pos = widget_transform.inverted()[0].map(touch.pos())
            joystick.center.value = touch_pos

            update_proxy_center()

            on_touch_begin(touch)
        self.on_initial_touch = on_initial_touch
        
        def on_touch_begin(touch: QTouchEvent.TouchPoint):
            on_touch_update(touch)
        self.on_touch_begin = on_touch_begin

        def on_touch_update(touch: QTouchEvent.TouchPoint):
            widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(widget_rect.width() / 2, widget_rect.height() / 2)
            movement = widget_transform.inverted()[0].map(touch.pos()) - widget_transform.inverted()[0].map(touch.lastPos())

            new_displacement = joystick.displacement.value + movement

            new_displacement_angle = math.atan2(new_displacement.y(), new_displacement.x())
            new_displacement_hypot = math.hypot(new_displacement.x(), new_displacement.y())

            max_displacement = dpi.cm(MAX_DISPLACEMENT)

            if new_displacement_hypot > max_displacement:
                joystick.center.value = joystick.center.value + (new_displacement_hypot - max_displacement) * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
                joystick.displacement.value = max_displacement * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
            else:
                joystick.displacement.value = new_displacement

            shifted_new_displacement_angle = math.atan2(new_displacement.y() - joystick.angle_center_offset.y() * max_displacement, new_displacement.x() - joystick.angle_center_offset.x() * max_displacement)
            joystick.selected_key_index.value = new_selected_key_widget(shifted_new_displacement_angle, new_displacement_hypot)
        self.on_touch_update = on_touch_update

        def new_selected_key_widget(angle: float, hypot: float):
            if hypot < dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
                return 0
            
            angle = (angle + math.tau / 16) % math.tau
            return math.floor(angle / (math.tau / 8)) + 1

        def on_touch_end():
            joystick.selected_key_index.value = None
        self.on_touch_end = on_touch_end


    @property
    def key_widgets(self):
        return self.__key_widgets

    @property
    def proxy(self):
        return self.__proxy