from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QTimer,
    QPoint,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGraphicsView,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from collections import Counter
from typing import cast, TYPE_CHECKING, Generator
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object


from .KeyWidget import KeyWidget
from .RotatableKeyContainer import RotatableKeyContainer
from .build_keyboard import use_build_keyboard
from ..settings import Settings, KeyLayout
from ..lib.reactivity import Ref, watch
from ..lib.UseDpi import UseDpi
from ..lib.constants import KEY_STYLESHEET


class KeyboardWidget(QWidget):
    end_stroke = pyqtSignal(set)  # set[str]
    current_stroke_change = pyqtSignal(set)  # set[str]
    after_touch_event = pyqtSignal()
    num_bar_pressed_change = pyqtSignal(bool)


    def __init__(self, settings: Settings, left_right_width_diff: Ref[float], parent: QWidget=None):
        super().__init__(parent)

        self.__current_stroke_keys: set[str] = set()
        self.__key_widgets: list[KeyWidget] = []

        self.__touches_to_key_widgets: dict[int, KeyWidget] = {} # keys of dict are from QTouchPoint::id
        self.__key_widget_touch_counter: Counter[KeyWidget] = Counter()

        self.settings = settings

        self.__setup_ui(left_right_width_diff)

    def __setup_ui(self, left_right_width_diff: Ref[float]):
        self.__dpi = dpi = UseDpi(self)
        build_keyboard, left_right_width_diff_src = use_build_keyboard(self.settings, self, dpi)

        self.__build_keyboard = build_keyboard
        self.setLayout(build_keyboard[self.settings.key_layout](self.__key_widgets))

        @watch(left_right_width_diff_src.change)
        def update_left_right_width_diff():
            left_right_width_diff.value = left_right_width_diff_src.value

        self.settings.key_layout_ref.change.connect(self.__rebuild_layout)


        self.setStyleSheet(KEY_STYLESHEET)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    # def __handle_dpi_change(self):
    #     # self.main_rows_layout.invalidate()
    #     # self.vowel_row_layout.invalidate()
    #     # self.layout().invalidate()

    #     self.__dpi.change.emit()

    #     # self.window().setMinimumSize(self.window().sizeHint()) # Needed in order to use QWidget.resize
    #     # cast(Main, self.window()).resize_from_center(0, 0)


    def __rebuild_layout(self, value: KeyLayout):
        self.__key_widgets = []
        # Detach listeners on the old key widgets to avoid leaking memory
        # TODO removing all listeners may become overzealous in the future
        self.__dpi.change.disconnect()
        self.num_bar_pressed_change.disconnect()

        # https://stackoverflow.com/questions/10416582/replacing-layout-on-a-qwidget-with-another-layout
        QWidget().setLayout(self.layout()) # Unparent and destroy the current layout so it can be replaced
        self.setLayout(self.__build_keyboard[value](self.__key_widgets))
        

    def event(self, event: QEvent) -> bool:
        """(override)"""

        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.after_touch_event.emit()

        # Variables for detecting changes post-update
        had_num_bar = "#" in self.__current_stroke_keys

        if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
            old_stroke_length = len(self.__current_stroke_keys)

            self.__current_stroke_keys.update(
                key
                for key_widget in self.__find_updated_key_widgets(event.touchPoints())
                for key in key_widget.values
            )

            if len(self.__current_stroke_keys) > old_stroke_length and self.__current_stroke_keys:
                self.current_stroke_change.emit(self.__current_stroke_keys)
            if not had_num_bar and "#" in self.__current_stroke_keys:
                self.num_bar_pressed_change.emit(True)
            

        elif event.type() == QEvent.TouchEnd:
            # This also filters out empty strokes (Plover accepts them and will insert extra spaces)
            if self.__current_stroke_keys and all(touch.state() == Qt.TouchPointReleased for touch in event.touchPoints()):
                self.end_stroke.emit(set(self.__current_stroke_keys))
                self.__current_stroke_keys.clear()
                self.__touches_to_key_widgets.clear()
                self.__key_widget_touch_counter.clear()
            
            if had_num_bar:
                self.num_bar_pressed_change.emit(False)

            
        self.__update_key_widget_styles_and_state(self.__key_widget_touch_counter.keys())
        
        return True

    
    def __find_updated_key_widgets(self, touch_points: list[QTouchEvent.TouchPoint]) -> Generator[KeyWidget, None, None]:
        for touch in touch_points:
            if touch.state() == Qt.TouchPointStationary: continue

            if touch.id() in self.__touches_to_key_widgets:
                old_key_widget = self.__touches_to_key_widgets[touch.id()]
                self.__key_widget_touch_counter[old_key_widget] -= 1

                del self.__touches_to_key_widgets[touch.id()]

                if self.__key_widget_touch_counter[old_key_widget] == 0:
                    del self.__key_widget_touch_counter[old_key_widget]

            if touch.state() == Qt.TouchPointReleased: continue


            key_widget = self.__key_widget_at(touch.pos().toPoint())
            if key_widget is None: continue


            self.__touches_to_key_widgets[touch.id()] = key_widget
            self.__key_widget_touch_counter[key_widget] += 1

            
            if not key_widget.matched:
                yield key_widget


    def __key_widget_at(self, point: QPoint):
        touched_widget = self.childAt(point)
        if touched_widget is None: return

        if isinstance(touched_widget, KeyWidget):
            return touched_widget
        
        # Loop through all the key containers; since `childAt` can only return the topmost child at a point,
        # a container that obscures another container with its empty space will cause `childAt` to fail to find a
        # touched key if one is underneath. The container list is also `reversed` so that containers rendered last
        # (i.e., on top) are processed first
        for view in reversed(self.findChildren(RotatableKeyContainer)):
            view: RotatableKeyContainer = view
            key_widget: KeyWidget = view.key_widget_at_point(point)

            if key_widget is None: continue
            return key_widget

        return

        """ # For some reason, `touched_widget` is a widget that is a child of the QGraphicsView rather than the
        # QGraphicsView itself
        elif isinstance(touched_widget.parent(), RotatableKeyContainer):
            view: RotatableKeyContainer = touched_widget.parent()
            key_widget: KeyWidget = view.key_widget_at_point(point)

            if key_widget is None: return
            return key_widget """
        
        raise TypeError
        

    def __update_key_widget_styles_and_state(self, touched_key_widgets: list[KeyWidget]):
        stroke_has_ended = len(self.__key_widget_touch_counter) == 0

        for key_widget in self.__key_widgets:
            old_touched, old_matched = key_widget.touched, key_widget.matched

            if key_widget in touched_key_widgets:
                key_widget.touched = True
                key_widget.matched = True

            elif ((not stroke_has_ended and key_widget.matched) # optimization assumes keys will not be removed mid-stroke
                    or all(key in self.__current_stroke_keys for key in key_widget.values)):
                key_widget.touched = False
                key_widget.matched = True

            else:
                key_widget.touched = False
                key_widget.matched = False


            if (old_touched, old_matched) != (key_widget.touched, key_widget.matched):
                # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                # self.style().unpolish(key_widget)
                self.style().polish(key_widget)
