from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from plover_touchscreen_stenotype.Main import Main
else:
    Main = object


from plover_touchscreen_stenotype.settings import Settings, KeyLayout
from plover_touchscreen_stenotype.widgets.KeyWidget import KeyWidget
from plover_touchscreen_stenotype.widgets.build_keyboard import build_keyboard
from plover_touchscreen_stenotype.util import UseDpi


class KeyboardWidget(QWidget):
    end_stroke = pyqtSignal(set)  # set[str]
    current_stroke_change = pyqtSignal(set)  # set[str]
    after_touch_event = pyqtSignal()
    num_bar_pressed_change = pyqtSignal(bool)

    #region Overrides

    def __init__(self, settings: Settings, parent: QWidget=None):
        super().__init__(parent)

        self._current_stroke_keys: set[str] = set()
        self._key_widgets: list[KeyWidget] = []

        self.__settings = settings

        self.__setup_ui()


    def event(self, event: QEvent) -> bool:
        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.after_touch_event.emit()

        touched_key_widgets = self._find_touched_key_widgets(event.touchPoints())

        # Variables for detecting changes post-update
        had_num_bar = "#" in self._current_stroke_keys

        if event.type() in (QEvent.TouchBegin, QEvent.TouchUpdate):
            old_stroke_length = len(self._current_stroke_keys)

            self._current_stroke_keys.update(
                key
                for key_widget in touched_key_widgets
                for key in key_widget.values
            )

            if len(self._current_stroke_keys) > old_stroke_length and self._current_stroke_keys:
                self.current_stroke_change.emit(self._current_stroke_keys)
            if not had_num_bar and "#" in self._current_stroke_keys:
                self.num_bar_pressed_change.emit(True)
            

        elif event.type() == QEvent.TouchEnd:
            # This also filters out empty strokes (Plover accepts them and will insert extra spaces)
            if self._current_stroke_keys and all(touch.state() == Qt.TouchPointReleased for touch in event.touchPoints()):
                self.end_stroke.emit(self._current_stroke_keys)
                self._current_stroke_keys = set()
            
            if had_num_bar:
                self.num_bar_pressed_change.emit(False)
        

        self._update_key_widget_styles(touched_key_widgets)

        return True

    #endregion

    def __setup_ui(self):
        self.dpi = UseDpi(self)
        self.setLayout(build_keyboard[self.__settings.key_layout](self, self._key_widgets))

        self.__settings.key_layout_change.connect(self.__rebuild_layout)


        self.setStyleSheet("""
KeyWidget[matched="true"] {
    background: #6f9f86;
    color: #fff;
    border: 1px solid;
    border-color: #2a6361 #2a6361 #1f5153 #2a6361;
}

KeyWidget[touched="true"] {
    background: #41796a;
}
""")

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        self.setFocusPolicy(Qt.NoFocus)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    # def __handle_dpi_change(self):
    #     # self.main_rows_layout.invalidate()
    #     # self.vowel_row_layout.invalidate()
    #     # self.layout().invalidate()

    #     self.dpi.change.emit()

    #     # self.window().setMinimumSize(self.window().sizeHint()) # Needed in order to use QWidget.resize
    #     # cast(Main, self.window()).resize_from_center(0, 0)


    def __rebuild_layout(self, value: KeyLayout):
        self._key_widgets = []
        # Detach listeners on the old key widgets to avoid leaking memory
        # TODO removing all listeners may become overzealous in the future
        self.dpi.change.disconnect()
        self.num_bar_pressed_change.disconnect()

        # https://stackoverflow.com/questions/10416582/replacing-layout-on-a-qwidget-with-another-layout
        QWidget().setLayout(self.layout()) # Unparent and destroy the current layout so it can be replaced
        self.setLayout(build_keyboard[value](self, self._key_widgets))
        


    def _find_touched_key_widgets(self, touch_points: list[QTouchEvent.TouchPoint]):
        touched_key_widgets: list[KeyWidget] = []
        for touch in touch_points:
            if touch.state() == Qt.TouchPointReleased: continue

            key_widget = self.childAt(touch.pos().toPoint())
            if not key_widget: continue

            touched_key_widgets.append(key_widget)

        return touched_key_widgets

    def _update_key_widget_styles(self, touched_key_widgets: list[KeyWidget]):
        for key_widget in self._key_widgets:
            old_touched, old_matched = key_widget.touched, key_widget.matched

            if key_widget in touched_key_widgets:
                key_widget.touched = True
                key_widget.matched = True

            elif all(key in self._current_stroke_keys for key in key_widget.values):
                key_widget.touched = False
                key_widget.matched = True

            else:
                key_widget.touched = False
                key_widget.matched = False


            if (old_touched, old_matched) != (key_widget.touched, key_widget.matched):
                # Reload stylesheet for dynamic properties: https://stackoverflow.com/questions/1595476/are-qts-stylesheets-really-handling-dynamic-properties
                # self.style().unpolish(key_widget)
                self.style().polish(key_widget)
