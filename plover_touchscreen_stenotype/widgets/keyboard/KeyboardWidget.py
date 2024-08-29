from collections import Counter
from typing import Callable, Generator
from pathlib import Path


from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QPoint,
    QRectF,
    QTimer,
    QPoint,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGraphicsView,
    QGraphicsScene,
    QGridLayout,
    QGraphicsItem,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from plover.steno import Stroke
import plover.log


from .KeyGroupWidget import KeyGroupWidget
from .GroupObject import GroupObject
from ..KeyWidget import KeyWidget
from ..composables.UseDpi import UseDpi
from ...settings import Settings
from ...lib.reactivity import Ref, RefAttr, computed, on, watch
from ...lib.constants import GRAPHICS_VIEW_STYLE, KEY_STYLESHEET
from ...lib.util import empty_stroke, not_none, render, child
from ...lib.keyboard_layout.descriptors import KEYBOARD_LAYOUT_BUILDERS, DEFAULT_KEYBOARD_LAYOUT_NAME


POSITION_RESET_TIMEOUT = 1500

class KeyboardWidget(QWidget):
    end_stroke = pyqtSignal(Stroke)
    current_stroke_change = pyqtSignal(Stroke)

    
    num_bar_pressed = RefAttr(bool)
    num_bar_pressed_ref = num_bar_pressed.ref_getter()


    def __init__(
        self,
        settings: Settings,
        left_right_width_diff: Ref[float],
        parent: "QWidget | None"=None,
    ):
        super().__init__(parent)

        current_stroke = Ref(empty_stroke())

        touches_to_key_widgets: dict[int, KeyWidget] = {} # keys of dict are from QTouchPoint::id
        key_widget_touch_counter: Ref[Counter[KeyWidget]] = Ref(Counter())

        touched_key_widgets = computed(lambda: set(key_widget_touch_counter.value.keys()),
                key_widget_touch_counter)

        self.num_bar_pressed = False

        self.settings = settings

        
        #region Touch handling

        def handle_touch_event(event: QTouchEvent):
            if event.type() in (QEvent.TouchUpdate, QEvent.TouchEnd):
                for touch in event.touchPoints():
                    if touch.state() != Qt.TouchPointReleased: continue

                    result = key_and_group_widgets_at(touch.pos().toPoint())
                    if result is None: continue
                    key_widget, key_group_widget = result

                    key_group_widget.notify_touch_release(touch, key_widget)

            # Variables for detecting changes post-update
            had_num_bar = "#" in current_stroke.value

            if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
                old_stroke_length = len(current_stroke.value)

                for key_widget in updated_key_widgets(event.touchPoints()):
                    current_stroke.value = current_stroke.value + key_widget.substroke

                if len(current_stroke.value) > old_stroke_length and current_stroke.value:
                    self.current_stroke_change.emit(current_stroke.value)
                if not had_num_bar and "#" in current_stroke.value:
                    self.num_bar_pressed = True
                
                position_reset_timer.stop()

            elif event.type() == QEvent.TouchEnd:
                # This also filters out empty strokes (Plover accepts them and will insert extra spaces)

                touches_to_key_widgets.clear()
                key_widget_touch_counter.value.clear()
                key_widget_touch_counter.emit()

                if current_stroke.value:
                    self.end_stroke.emit(current_stroke.value)
                    current_stroke.value = empty_stroke()
                
                if had_num_bar:
                    self.num_bar_pressed = False

                position_reset_timer.start(POSITION_RESET_TIMEOUT)
        self.__handle_touch_event = handle_touch_event


        def updated_key_widgets(touch_points: list[QTouchEvent.TouchPoint]) -> Generator[KeyWidget, None, None]:
            for touch in touch_points:
                if touch.state() == Qt.TouchPointStationary: continue

                if touch.id() in touches_to_key_widgets:
                    old_key_widget = touches_to_key_widgets[touch.id()]
                    key_widget_touch_counter.value[old_key_widget] -= 1
                    key_widget_touch_counter.emit()

                    del touches_to_key_widgets[touch.id()]

                    if key_widget_touch_counter.value[old_key_widget] == 0:
                        del key_widget_touch_counter.value[old_key_widget]
                        key_widget_touch_counter.emit()


                result = key_and_group_widgets_at(touch.pos().toPoint())
                if result is None: continue
                key_widget, key_group_widget = result

                if touch.state() == Qt.TouchPointReleased: continue

                if not key_widget.matched:
                    yield key_widget

                touches_to_key_widgets[touch.id()] = key_widget
                key_widget_touch_counter.value[key_widget] += 1
                key_widget_touch_counter.emit()


        containers: list[KeyGroupWidget]
        group_objects: list[GroupObject]
        graphics_view: QGraphicsView
        def key_and_group_widgets_at(point: QPoint) -> "tuple[KeyWidget, KeyGroupWidget] | None":
            for key_group_widget in containers:
                proxy_transform = key_group_widget.proxy.deviceTransform(graphics_view.viewportTransform())
                widget_coords = proxy_transform.inverted()[0].map(point)

                key_widget = key_group_widget.childAt(widget_coords)
                if key_widget is not None:
                    return key_widget, key_group_widget

            return None
        

        position_reset_timer = QTimer(self)
        @on(position_reset_timer.timeout)
        def reset_group_positions():
            for container in containers:
                container.reset_position()

            for group_object in group_objects:
                group_object.reset_position()

        #endregion
        

        dpi = UseDpi(self)

        #region Render

        @render(self, QGridLayout())
        def render_widget(widget: QWidget, _: QGridLayout):
            scene = QGraphicsScene(self)

            @child(self, QGraphicsView(scene))
            def render_widget(view: QGraphicsView, _: None):
                nonlocal graphics_view

                view.setStyleSheet(GRAPHICS_VIEW_STYLE)
                
                @watch(settings.keyboard_layout_ref.change)
                def set_keyboard_layout():
                    nonlocal containers
                    nonlocal group_objects

                    scene.clear()

                    build_layout_descriptor = KEYBOARD_LAYOUT_BUILDERS.get(settings.keyboard_layout) or KEYBOARD_LAYOUT_BUILDERS[DEFAULT_KEYBOARD_LAYOUT_NAME]
                    layout_descriptor = build_layout_descriptor(self.settings, self)

                    group_object = GroupObject(layout_descriptor, scene, view, settings, current_stroke=current_stroke, touched_key_widgets=touched_key_widgets, dpi=dpi)
                    containers = group_object.key_group_widgets
                    group_objects = group_object.group_objects
                    
                    rect = QRectF(group_object.item_group.boundingRect())
                    # rect = QRectF(view.rect())
                    # rect.moveCenter(QPointF(0, 0))
                    view.setSceneRect(rect)


                    center_diff = layout_descriptor.out_center_diff
                    if center_diff is not None:
                        @watch(center_diff.change)
                        def set_left_right_width_diff():
                            left_right_width_diff.value = center_diff.value
                            view.setSceneRect(rect)

                graphics_view = view

                return ()
            
            return ()


        # build_keyboard, left_right_width_diff_src = use_build_keyboard(self.settings, self, dpi)

        # self.__build_keyboard = build_keyboard
        # layout, key_widgets = build_keyboard()
        # self.setLayout(layout)
        # key_widgets = key_widgets

        # @watch(left_right_width_diff_src.change)
        # def update_left_right_width_diff():
        #     left_right_width_diff.value = left_right_width_diff_src.value


        self.setStyleSheet(KEY_STYLESHEET)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #endregion
        

    def event(self, event: QEvent) -> bool:
        """(override)"""

        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.__handle_touch_event(event)
        return True