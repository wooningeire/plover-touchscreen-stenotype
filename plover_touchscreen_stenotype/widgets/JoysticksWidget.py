from PyQt5.QtCore import (
    Qt,
    QEvent,
    QRectF,
    pyqtSignal,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QGridLayout,
)
from PyQt5.QtGui import (
    QTouchEvent,
    QPointingDeviceUniqueId,
)

import plover.log
from plover.steno import Stroke

import math
from typing import TYPE_CHECKING



from .KeyWidget import KeyWidget
from ..settings import Settings
from ..lib.reactivity import Ref, on, watch
from ..lib.UseDpi import UseDpi
from ..lib.constants import GRAPHICS_VIEW_STYLE, KEY_STYLESHEET
from ..lib.util import empty_stroke
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object


MAX_DISPLACEMENT = 1.25
NEUTRAL_THRESHOLD_PROPORTION = 2/4
COMPOUND_THRESHOLD_PROPORTION = 3/4
TRIGGER_DISTANCE = 2

class JoysticksWidget(QWidget):
    end_stroke = pyqtSignal(Stroke)
    current_stroke_change = pyqtSignal(Stroke)


    def __init__(self, settings: Settings, left_right_width_diff: Ref[float], parent: "QWidget | None"=None):
        super().__init__(parent)

        self.__current_stroke: Stroke = empty_stroke()
        self.__key_widgets: list[KeyWidget] = []
        self.__selected_key_widgets: set[KeyWidget] = set()

        self.__triggered_joysticks: "dict[int, _VerticalJoystickWidget]" = {}

        dpi = UseDpi(self)

        scene = QGraphicsScene(self)
        view = QGraphicsView(scene)
        view.setStyleSheet(GRAPHICS_VIEW_STYLE)
        view.setSceneRect(QRectF(view.rect()))
        view.centerOn(0, 0)

        self.__joysticks = (
            _GridJoystickWidget(view, (
                ("^+S", ""),
                ("S", "S"),
                ("S", "S"),
                ("+S", ""),
                ("+", "+"),
                ("^+", ""),
                ("^", "^"),
                ("^S", ""),
                ("S", "S"),
            )).set_center(dpi.cm(-10), -dpi.cm(2 * settings.pinky_stagger_fac)),
            _VerticalJoystickWidget(view, (
                ("T", "T"),
                ("TK", ""),
                ("K", "K"),
            )).set_center(dpi.cm(-7.5), -dpi.cm(2 * settings.ring_stagger_fac)),
            _VerticalJoystickWidget(view, (
                ("P", "P"),
                ("PW", ""),
                ("W", "W"),
            )).set_center(dpi.cm(-5), -dpi.cm(2 * settings.middle_stagger_fac)),
            _GridJoystickWidget(view, (
                ("&HR", ""),
                ("&", "&&"),
                ("&", "&&"),
                ("&R", ""),
                ("R", "R"),
                ("HR", ""),
                ("H", "H"),
                ("&H", ""),
                ("&", "&&"),
            )).set_center(dpi.cm(-2.5), -dpi.cm(2 * settings.index_stagger_fac)),
            _GridJoystickWidget(view, (
                ("*FR", ""),
                ("-FR", ""),
                ("-R", "R"),
                ("*R", ""),
                ("*", "*"),
                ("*", "*"),
                ("*", "*"),
                ("*F", ""),
                ("-F", "F"),
            )).set_center(dpi.cm(2.5), -dpi.cm(2 * settings.index_stagger_fac)),
            _VerticalJoystickWidget(view, (
                ("-P", "P"),
                ("-PB", ""),
                ("-B", "B"),
            )).set_center(dpi.cm(5), -dpi.cm(2 * settings.middle_stagger_fac)),
            _VerticalJoystickWidget(view, (
                ("-L", "L"),
                ("-LG", ""),
                ("-G", "G"),
            )).set_center(dpi.cm(7.5), -dpi.cm(2 * settings.ring_stagger_fac)),
            _GridJoystickWidget(view, (
                ("-TSDZ", ""),
                ("-DZ", ""),
                ("-Z", "Z"),
                ("-SZ", ""),
                ("-S", "S"),
                ("-TS", ""),
                ("-T", "T"),
                ("-TD", ""),
                ("-D", "D"),
            )).set_center(dpi.cm(10), -dpi.cm(2 * settings.pinky_stagger_fac)),
            _GridJoystickWidget(view, (
                ("#AO", ""),
                ("#O", ""),
                ("#", "#"),
                ("#", "#"),
                ("#", "#"),
                ("#A", ""),
                ("A", "A"),
                ("AO", ""),
                ("O", "O"),
            )).set_center(dpi.cm(-2), dpi.cm(4)),
            _GridJoystickWidget(view, (
                ("_EU", ""),
                ("_U", ""),
                ("_", "_"),
                ("_", "_"),
                ("_", "_"),
                ("_E", ""),
                ("E", "E"),
                ("EU", ""),
                ("U", "U"),
            )).set_center(dpi.cm(2), dpi.cm(4)),
        )

        for joystick in reversed(self.__joysticks):
            @on(joystick.key_change)
            def update_keys(key_widget: KeyWidget):
                self.__current_stroke = Stroke.from_keys(())
                self.__selected_key_widgets = set()
                for joystick in self.__joysticks:
                    if joystick.selected_key_widget is None: continue
                    self.__current_stroke += joystick.selected_key_widget.substroke
                    self.__selected_key_widgets.add(joystick.selected_key_widget)

                self.current_stroke_change.emit(self.__current_stroke)

            self.__key_widgets.extend(joystick.key_widgets())


        
        layout = QGridLayout()
        layout.addWidget(view)
        self.setLayout(layout)


        self.setStyleSheet(KEY_STYLESHEET)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def event(self, event: QEvent) -> bool:
        """(override)"""

        if not isinstance(event, QTouchEvent):
            return super().event(event)

        touch_points = event.touchPoints()

        new_triggered_joysticks = self.__triggered_joysticks.copy()

        joystick_released = False
        
        for touch in touch_points:
            if touch.state() == Qt.TouchPointPressed:
                for joystick in self.__joysticks:
                    if joystick in new_triggered_joysticks or not joystick.triggered_by_touch(touch):
                        continue

                    new_triggered_joysticks[touch.id()] = joystick
                    joystick.on_touch_begin(touch)
                    break

            elif touch.state() == Qt.TouchPointMoved:
                if touch.id() in new_triggered_joysticks:
                    new_triggered_joysticks[touch.id()].on_touch_update(touch)

            elif touch.state() == Qt.TouchPointReleased:
                if touch.id() in new_triggered_joysticks:
                    joystick_released = True
                    new_triggered_joysticks[touch.id()].on_touch_end()
                    del new_triggered_joysticks[touch.id()]

        self.__triggered_joysticks = new_triggered_joysticks

        if joystick_released and len(self.__current_stroke.keys()) > 0:
            self.end_stroke.emit(self.__current_stroke)

            self.__current_stroke = Stroke.from_keys(())
            self.__selected_key_widgets = set()


        self.__update_key_widget_styles_and_state()

        return True
        

    def __update_key_widget_styles_and_state(self):
        for key_widget in self.__key_widgets:
            old_touched, old_matched = key_widget.touched, key_widget.matched

            if key_widget in self.__selected_key_widgets:
                key_widget.touched = True
                key_widget.matched = True

            elif key_widget.substroke in self.__current_stroke:
                key_widget.touched = False
                key_widget.matched = True

            else:
                key_widget.touched = False
                key_widget.matched = False


            if (old_touched, old_matched) != (key_widget.touched, key_widget.matched):
                # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                # self.style().unpolish(key_widget)
                self.style().polish(key_widget)

class _VerticalJoystickWidget(QWidget):
    key_change = pyqtSignal(KeyWidget)
    direction_change = pyqtSignal()

    def __init__(self, view: QGraphicsView, key_descriptors: tuple[tuple[str, str], ...]):
        super().__init__()

        self.__displacement = 0
        self.__center = 0

        self.__view = view
        self.__key_widgets: list[KeyWidget] = [KeyWidget(Stroke.from_steno(steno), label) for steno, label in key_descriptors]
        self.__selected_key_widget: "KeyWidget | None" = None

        self.__dpi = dpi = UseDpi(self)


        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for key_widget in self.__key_widgets:
            layout.addWidget(key_widget)

        @watch(dpi.change)
        def set_size():
            self.setFixedWidth(dpi.cm(MAX_DISPLACEMENT))
            self.__key_widgets[1].setFixedHeight(dpi.cm(MAX_DISPLACEMENT))
        
        self.setLayout(layout)
        self.setStyleSheet(KEY_STYLESHEET)

        self.__proxy = view.scene().addWidget(self)

    def set_center(self, x: float, y: float):
        widget_rect = self.__proxy.boundingRect()
        self.__proxy.setPos(x - widget_rect.width() / 2, y - widget_rect.height() / 2)
        return self
    
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
    
    def on_touch_begin(self, touch: QTouchEvent.TouchPoint):
        view_transform = self.__view.viewportTransform()
        touch_pos = view_transform.inverted()[0].map(touch.pos())
        self.__center = touch_pos.y()
        self.__displacement = 0

        self.set_center(touch_pos.x(), self.__center)

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
            self.key_change.emit(self.__selected_key_widget)

    def __new_selected_key_widget(self):
        if abs(self.__displacement) < self.__dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
            return None
        
        if abs(self.__displacement) < self.__dpi.cm(MAX_DISPLACEMENT * COMPOUND_THRESHOLD_PROPORTION):
            return self.__key_widgets[1]

        if self.__displacement > 0:
            return self.__key_widgets[2]
        
        return self.__key_widgets[0]

    def on_touch_end(self):
        self.__selected_key_widget = None

    def key_widgets(self):
        return self.__key_widgets.__iter__()

class _GridJoystickWidget(QWidget):
    key_change = pyqtSignal(KeyWidget)
    direction_change = pyqtSignal()

    def __init__(self, view: QGraphicsView, key_descriptors: tuple[tuple[str, str], ...]):
        super().__init__()

        self.__displacement_x = 0
        self.__displacement_y = 0
        self.__center_x = 0
        self.__center_y = 0

        self.__view = view
        self.__key_widgets: list[KeyWidget] = [KeyWidget(Stroke.from_steno(steno), label) for steno, label in key_descriptors]
        self.__selected_key_widget: "KeyWidget | None" = None

        self.__dpi = dpi = UseDpi(self)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        @watch(dpi.change)
        def set_size():
            self.__key_widgets[0].setFixedSize(dpi.cm(MAX_DISPLACEMENT), dpi.cm(MAX_DISPLACEMENT))

        layout.addWidget(self.__key_widgets[0], 1, 1)
        layout.addWidget(self.__key_widgets[1], 1, 2)
        layout.addWidget(self.__key_widgets[2], 2, 2)
        layout.addWidget(self.__key_widgets[3], 2, 1)
        layout.addWidget(self.__key_widgets[4], 2, 0)
        layout.addWidget(self.__key_widgets[5], 1, 0)
        layout.addWidget(self.__key_widgets[6], 0, 0)
        layout.addWidget(self.__key_widgets[7], 0, 1)
        layout.addWidget(self.__key_widgets[8], 0, 2)
        
        self.setLayout(layout)
        self.setStyleSheet(KEY_STYLESHEET)

        self.__proxy = view.scene().addWidget(self)

    def set_center(self, x: float, y: float):
        widget_rect = self.__proxy.boundingRect()
        self.__proxy.setPos(x - widget_rect.width() / 2, y - widget_rect.height() / 2)
        return self
    
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
    
    def on_touch_begin(self, touch: QTouchEvent.TouchPoint):
        view_transform = self.__view.viewportTransform()
        touch_pos = view_transform.inverted()[0].map(touch.pos())
        self.__center_x = touch_pos.x()
        self.__center_y = touch_pos.y()
        self.__displacement_x = 0
        self.__displacement_y = 0

        self.set_center(self.__center_x, self.__center_y)

        self.on_touch_update(touch)

    def on_touch_update(self, touch: QTouchEvent.TouchPoint):
        movement = touch.pos() - touch.lastPos()

        new_displacement_x = self.__displacement_x + movement.x()
        new_displacement_y = self.__displacement_y + movement.y()

        new_displacement_angle = math.atan2(new_displacement_y, new_displacement_x)
        new_displacement_hypot = math.hypot(new_displacement_x, new_displacement_y)

        max_displacement = self.__dpi.cm(MAX_DISPLACEMENT)

        if new_displacement_hypot > max_displacement:
            self.__center_x += (new_displacement_hypot - max_displacement) * math.cos(new_displacement_angle)
            self.__center_y += (new_displacement_hypot - max_displacement) * math.sin(new_displacement_angle)
            self.__displacement_x = max_displacement * math.cos(new_displacement_angle)
            self.__displacement_y = max_displacement * math.sin(new_displacement_angle)
        else:
            self.__displacement_x = new_displacement_x
            self.__displacement_y = new_displacement_y

        self.set_center(self.__center_x, self.__center_y)


        old_selected_key_widget = self.__selected_key_widget
        self.__selected_key_widget = self.__new_selected_key_widget(new_displacement_angle, new_displacement_hypot)

        if old_selected_key_widget != self.__selected_key_widget:
            self.key_change.emit(self.__selected_key_widget)

    def __new_selected_key_widget(self, angle: float, hypot: float):
        if hypot < self.__dpi.cm(MAX_DISPLACEMENT * NEUTRAL_THRESHOLD_PROPORTION):
            return None
        
        if hypot < self.__dpi.cm(MAX_DISPLACEMENT * COMPOUND_THRESHOLD_PROPORTION):
            return self.__key_widgets[0]
        
        angle = (angle + math.tau / 16) % math.tau
        return self.__key_widgets[math.floor(angle / (math.tau / 8)) + 1]

    def on_touch_end(self):
        self.__selected_key_widget = None

    def key_widgets(self):
        return self.__key_widgets.__iter__()