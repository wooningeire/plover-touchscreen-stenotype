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
from ..lib.reactivity import Ref, computed, on, on_many, watch, watch_many
from ..lib.UseDpi import UseDpi
from ..lib.constants import GRAPHICS_VIEW_STYLE, KEY_STYLESHEET, KEY_CONTAINER_STYLE
from ..lib.util import child, empty_stroke, render
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object


MAX_DISPLACEMENT = 0.75
NEUTRAL_THRESHOLD_PROPORTION = 1/3
TRIGGER_DISTANCE = 1.5

class JoysticksState(Enum):
    GATHERING_TOUCHES = auto()
    AWAITING_TAPS = auto()

class JoysticksWidget(QWidget):
    end_stroke = pyqtSignal(Stroke)
    current_stroke_change = pyqtSignal(Stroke)


    def __init__(self, settings: Settings, left_right_width_diff: Ref[float], parent: "QWidget | None"=None):
        super().__init__(parent)

        key_widgets: list[KeyWidget] = []

        tapped_joysticks: Ref[dict[_VerticalJoystickWidget | _GridJoystickWidget, KeyWidget]] = Ref({})
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

        selected_joysticks: "dict[int, _VerticalJoystickWidget | _GridJoystickWidget]" = {}
        selected_key_widgets: Ref[set[KeyWidget]] = Ref(set())

        all_selected_joysticks: "set[_VerticalJoystickWidget | _GridJoystickWidget]" = set()


        dpi = UseDpi(self)

        scene = QGraphicsScene(self)
        view = QGraphicsView(scene)
        view.setStyleSheet(GRAPHICS_VIEW_STYLE)
        
        rect = QRectF(view.rect())
        rect.moveCenter(QPointF(0, 0))

        view.setSceneRect(rect)

        self.__joysticks = (
            _GridJoystickWidget(view,
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
                center=QPointF(dpi.cm(-11.25), -dpi.cm(2 * settings.pinky_stagger_fac)),
            ),
            _VerticalJoystickWidget(view,
                (
                    ("T", "T"),
                    ("TK", ""),
                    ("K", "K"),
                ),
                center=QPointF(dpi.cm(-7.5), -dpi.cm(2 * settings.ring_stagger_fac)),
            ),
            _VerticalJoystickWidget(view,
                (
                    ("P", "P"),
                    ("PW", ""),
                    ("W", "W"),
                ),
                center=QPointF(dpi.cm(-5), -dpi.cm(2 * settings.middle_stagger_fac)),
            ),
            _GridJoystickWidget(view,
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
            _GridJoystickWidget(view,
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
            _VerticalJoystickWidget(view,
                (
                    ("-P", "P"),
                    ("-PB", ""),
                    ("-B", "B"),
                ),
                center=QPointF(dpi.cm(5), -dpi.cm(2 * settings.middle_stagger_fac)),
            ),
            _VerticalJoystickWidget(view,
                (
                    ("-L", "L"),
                    ("-LG", ""),
                    ("-G", "G"),
                ),
                center=QPointF(dpi.cm(7.5), -dpi.cm(2 * settings.ring_stagger_fac)),
            ),
            _GridJoystickWidget(view,
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
                center=QPointF(dpi.cm(11.25), -dpi.cm(2 * settings.pinky_stagger_fac)),
            ),
            _GridJoystickWidget(view,
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
                center=QPointF(dpi.cm(-2), dpi.cm(4)),
            ),
            _GridJoystickWidget(view,
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
                center=QPointF(dpi.cm(2), dpi.cm(4)),
            ),
        )

        for joystick in reversed(self.__joysticks):
            @on(joystick.selected_key_change)
            def update_keys(key_widget: KeyWidget):
                new_selected_key_widgets = set()
                for joystick in self.__joysticks:
                    if joystick.selected_key_widget is None: continue
                    new_selected_key_widgets.add(joystick.selected_key_widget)
                selected_key_widgets.value = new_selected_key_widgets

            key_widgets.extend(joystick.key_widgets())


        
        layout = QGridLayout()
        layout.addWidget(view)
        self.setLayout(layout)


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
                    self.style().polish(key_widget)
        

        n_expected_touches = 0
        state = JoysticksState.GATHERING_TOUCHES

        def handle_touch_event(event: QTouchEvent):
            nonlocal current_stroke
            nonlocal selected_key_widgets
            nonlocal tapped_joysticks
            nonlocal selected_joysticks
            nonlocal n_expected_touches
            nonlocal state
            nonlocal all_selected_joysticks

            touch_points = event.touchPoints()

            new_triggered_joysticks = selected_joysticks.copy()

            new_press = False
            new_release = False

            for touch in touch_points:
                if touch.state() == Qt.TouchPointPressed:
                    for joystick in self.__joysticks:
                        if joystick in new_triggered_joysticks or not joystick.triggered_by_touch(touch):
                            continue

                        new_press = True
                        new_triggered_joysticks[touch.id()] = joystick
                        if joystick not in all_selected_joysticks:
                            all_selected_joysticks.add(joystick)
                            joystick.on_initial_touch(touch)
                        else:
                            joystick.on_touch_begin(touch)

                        if state == JoysticksState.AWAITING_TAPS:
                            tapped_joysticks.value[joystick] = joystick.selected_key_widget
                            tapped_joysticks.emit()

                        break

                elif touch.state() == Qt.TouchPointMoved:
                    if touch.id() in new_triggered_joysticks:
                        new_triggered_joysticks[touch.id()].on_touch_update(touch)

                elif touch.state() == Qt.TouchPointReleased:
                    if touch.id() in new_triggered_joysticks:
                        new_release = True
                        new_triggered_joysticks[touch.id()].on_touch_end()
                        del new_triggered_joysticks[touch.id()]

            selected_joysticks = new_triggered_joysticks
            n_expected_touches = max(n_expected_touches, len(selected_joysticks))

            if new_release and state == JoysticksState.GATHERING_TOUCHES:
                state = JoysticksState.AWAITING_TAPS

            if new_release and len(selected_joysticks) == 0:
                state = JoysticksState.GATHERING_TOUCHES
                n_expected_touches = 0

                selected_key_widgets.value = set()
                tapped_joysticks.value = {}
                all_selected_joysticks = set()

                for joystick in self.__joysticks:
                    joystick.restore_position()
            

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

class _VerticalJoystickWidget(QWidget):
    selected_key_change = pyqtSignal(KeyWidget)

    def __init__(self, view: QGraphicsView, key_descriptors: tuple[tuple[str, str], ...], *, center: QPointF, angle: float=0, aspect_ratio: float=2):
        super().__init__()

        self.__displacement = 0

        base_center = center
        self.__center = center.y()
        def restore_position():
            self.__center = base_center.y()
            self.__update_proxy_center(base_center.x())
        self.restore_position = restore_position

        self.__view = view
        self.__key_widgets: list[KeyWidget] = [KeyWidget(Stroke.from_steno(steno), label) for steno, label in key_descriptors]
        self.__selected_key_widget: "KeyWidget | None" = None

        self.__dpi = dpi = UseDpi(self)


        self.setStyleSheet(KEY_STYLESHEET)


        @render(self, QGridLayout())
        def render_widget(widget: QWidget, layout: QGridLayout):
            @child(widget, QToolButton())
            def render_widget(button: QToolButton, _: None):
                @watch(dpi.change)
                def set_button_size():
                    button.setFixedSize(dpi.cm(TRIGGER_DISTANCE * 2), dpi.cm(TRIGGER_DISTANCE * 2))

                return 0, 0
            
            @child(widget, QWidget(), QVBoxLayout())
            def render_widget(joystick_container: QWidget, layout: QVBoxLayout):
                for key_widget in self.__key_widgets:
                    layout.addWidget(key_widget)

                @watch(dpi.change)
                def set_size():
                    joystick_container.setFixedWidth(dpi.cm(MAX_DISPLACEMENT))
                    self.__key_widgets[1].setFixedHeight(dpi.cm(MAX_DISPLACEMENT * 2))
                
                return 0, 0

            return ()

        self.__proxy = view.scene().addWidget(self)

        widget_rect = self.__proxy.boundingRect()


        def update_proxy_center(x: float):
            self.__proxy.setPos(x - widget_rect.width() / 2, self.__center - widget_rect.height() / 2)
        self.__update_proxy_center = update_proxy_center
        update_proxy_center(base_center.x())

        self.__proxy.setRotation(angle)
    
    @property
    def pos(self):
        return self.__proxy.pos()
    
    @property
    def selected_key_widget(self):
        return self.__selected_key_widget
    
    def triggered_by_touch(self, touch: QTouchEvent.TouchPoint):
        widget_rect = self.__proxy.boundingRect()
        widget_transform = self.__proxy.deviceTransform(self.__view.viewportTransform()).translate(widget_rect.width() / 2, widget_rect.height() / 2)
        widget_touch_pos = widget_transform.inverted()[0].map(touch.pos())
        return widget_touch_pos.x()**2 + widget_touch_pos.y()**2 < self.__dpi.cm(TRIGGER_DISTANCE)**2
    
    
    def on_initial_touch(self, touch: QTouchEvent.TouchPoint):
        view_transform = self.__view.viewportTransform()
        touch_pos = view_transform.inverted()[0].map(touch.pos())
        self.__center = touch_pos.y()
        self.__displacement = 0

        self.__update_proxy_center(touch_pos.x())

        self.on_touch_begin(touch)
    
    def on_touch_begin(self, touch: QTouchEvent.TouchPoint):
        self.on_touch_update(touch)

    def on_touch_update(self, touch: QTouchEvent.TouchPoint):
        movement = touch.pos() - touch.lastPos()

        max_displacement = self.__dpi.cm(MAX_DISPLACEMENT)

        new_displacement = self.__displacement + movement.y()
        if new_displacement > max_displacement:
            self.__center += new_displacement - max_displacement
            self.__displacement = max_displacement
        elif new_displacement < -max_displacement:
            self.__center -= -max_displacement - new_displacement
            self.__displacement = -max_displacement
        else:
            self.__displacement = new_displacement

        widget_rect = self.__proxy.boundingRect()

        self.__proxy.setPos(self.pos.x() + movement.x(), self.__center - widget_rect.height() / 2)


        old_selected_key_widget = self.__selected_key_widget
        self.__selected_key_widget = self.__new_selected_key_widget()

        if old_selected_key_widget != self.__selected_key_widget:
            self.selected_key_change.emit(self.__selected_key_widget)

    def __new_selected_key_widget(self):
        if abs(self.__displacement) < self.__dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
            return self.__key_widgets[1]

        if self.__displacement > 0:
            return self.__key_widgets[2]
        
        return self.__key_widgets[0]

    def on_touch_end(self):
        self.__selected_key_widget = None

    def key_widgets(self):
        return self.__key_widgets.__iter__()

class _GridJoystickWidget(QWidget):
    selected_key_change = pyqtSignal(KeyWidget)

    def __init__(self, view: QGraphicsView, key_descriptors: tuple[tuple[str, str], ...], *, center: QPointF, angle: float=0, aspect_ratio: float=2):
        super().__init__()

        self.__displacement = QPointF(0, 0)
        base_center = center
        self.__center = center
        def restore_position():
            self.__center = base_center
            self.__update_proxy_center()
        self.restore_position = restore_position


        self.__view = view
        self.__key_widgets: list[KeyWidget] = [KeyWidget(Stroke.from_steno(steno), label) for steno, label in key_descriptors]
        self.__selected_key_widget: "KeyWidget | None" = None

        self.__dpi = dpi = UseDpi(self)

        
        self.setStyleSheet(KEY_STYLESHEET)


        @render(self, QGridLayout())
        def render_widget(widget: QWidget, layout: QGridLayout):
            @child(widget, QToolButton())
            def render_widget(button: QToolButton, _: None):
                @watch(dpi.change)
                def set_button_size():
                    button.setFixedSize(dpi.cm(TRIGGER_DISTANCE * 2), dpi.cm(TRIGGER_DISTANCE * 2))

                return 0, 0
            
            @child(widget, QWidget(), QGridLayout())
            def render_widget(joystick_container: QWidget, layout: QGridLayout):
                @watch(dpi.change)
                def set_size():
                    self.__key_widgets[0].setFixedSize(dpi.cm(MAX_DISPLACEMENT * 2), dpi.cm(MAX_DISPLACEMENT * 2))

                layout.addWidget(self.__key_widgets[0], 1, 1)
                layout.addWidget(self.__key_widgets[1], 1, 2)
                layout.addWidget(self.__key_widgets[2], 2, 2)
                layout.addWidget(self.__key_widgets[3], 2, 1)
                layout.addWidget(self.__key_widgets[4], 2, 0)
                layout.addWidget(self.__key_widgets[5], 1, 0)
                layout.addWidget(self.__key_widgets[6], 0, 0)
                layout.addWidget(self.__key_widgets[7], 0, 1)
                layout.addWidget(self.__key_widgets[8], 0, 2)
                
                return 0, 0

            return ()

        proxy = view.scene().addWidget(self)
        if proxy is None:
            raise Exception()
        
        self.__proxy = proxy

        widget_rect = self.__proxy.boundingRect()


        @watch(dpi.change)
        def update_proxy_center():
            self.__proxy.setPos(self.__center - QPointF(widget_rect.width(), widget_rect.height()) / 2)
        self.__update_proxy_center = update_proxy_center

        self.__proxy.setRotation(angle)
    
    @property
    def selected_key_widget(self):
        return self.__selected_key_widget
    
    def triggered_by_touch(self, touch: QTouchEvent.TouchPoint):
        widget_rect = self.__proxy.boundingRect()
        widget_transform = self.__proxy.deviceTransform(self.__view.viewportTransform()).translate(widget_rect.width() / 2, widget_rect.height() / 2)
        widget_touch_pos = widget_transform.inverted()[0].map(touch.pos())
        return widget_touch_pos.x()**2 + widget_touch_pos.y()**2 < self.__dpi.cm(TRIGGER_DISTANCE)**2
    
    def on_initial_touch(self, touch: QTouchEvent.TouchPoint):
        view_transform = self.__view.viewportTransform()
        touch_pos = view_transform.inverted()[0].map(touch.pos())
        self.__center = touch_pos

        self.__update_proxy_center()

        self.on_touch_begin(touch)
    
    def on_touch_begin(self, touch: QTouchEvent.TouchPoint):
        self.on_touch_update(touch)

    def on_touch_update(self, touch: QTouchEvent.TouchPoint):
        movement = touch.pos() - touch.lastPos()

        new_displacement = self.__displacement + movement

        new_displacement_angle = math.atan2(new_displacement.y(), new_displacement.x())
        new_displacement_hypot = math.hypot(new_displacement.x(), new_displacement.y())

        max_displacement = self.__dpi.cm(MAX_DISPLACEMENT)

        if new_displacement_hypot > max_displacement:
            self.__center += (new_displacement_hypot - max_displacement) * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
            self.__displacement = max_displacement * QPointF(math.cos(new_displacement_angle), math.sin(new_displacement_angle))
        else:
            self.__displacement = new_displacement

        self.__update_proxy_center()


        old_selected_key_widget = self.__selected_key_widget
        self.__selected_key_widget = self.__new_selected_key_widget(new_displacement_angle, new_displacement_hypot)

        if old_selected_key_widget != self.__selected_key_widget:
            self.selected_key_change.emit(self.__selected_key_widget)

    def __new_selected_key_widget(self, angle: float, hypot: float):
        if hypot < self.__dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
            return self.__key_widgets[0]
        
        angle = (angle + math.tau / 16) % math.tau
        return self.__key_widgets[math.floor(angle / (math.tau / 8)) + 1]

    def on_touch_end(self):
        self.__selected_key_widget = None

    def key_widgets(self):
        return self.__key_widgets.__iter__()