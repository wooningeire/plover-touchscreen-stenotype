from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QTimer,
)
from PyQt5.QtWidgets import (
    QWidget,
    QSizePolicy,
    QGraphicsView,
)
from PyQt5.QtGui import (
    QTouchEvent,
)

from typing import cast, TYPE_CHECKING
if TYPE_CHECKING:
    from ..Main import Main
else:
    Main = object


from .KeyWidget import KeyWidget
from .RotatableKeyContainer import RotatableKeyContainer
from .build_keyboard import use_build_keyboard
from ..settings import Settings, KeyLayout
from ..util import UseDpi, KEY_STYLESHEET


class KeyboardWidget(QWidget):
    end_stroke = pyqtSignal(set)  # set[str]
    current_stroke_change = pyqtSignal(set)  # set[str]
    after_touch_event = pyqtSignal()
    num_bar_pressed_change = pyqtSignal(bool)
    key_polish = pyqtSignal(KeyWidget)
    """Emitted when a `KeyWidget`s is repolished"""

    #region Overrides

    def __init__(self, settings: Settings, parent: QWidget=None):
        super().__init__(parent)

        self._current_stroke_keys: set[str] = set()
        self._key_widgets: list[KeyWidget] = []

        self.settings = settings

        self.__setup_ui()


    def event(self, event: QEvent) -> bool:
        if not isinstance(event, QTouchEvent):
            return super().event(event)

        self.after_touch_event.emit()

        touched_key_widgets = self.__find_touched_key_widgets(event.touchPoints())

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
        self.__dpi = dpi = UseDpi(self)
        self.__build_keyboard = build_keyboard = use_build_keyboard(self.settings, self, dpi)
        self.setLayout(build_keyboard[self.settings.key_layout](self._key_widgets))

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
        self._key_widgets = []
        # Detach listeners on the old key widgets to avoid leaking memory
        # TODO removing all listeners may become overzealous in the future
        self.__dpi.change.disconnect()
        self.num_bar_pressed_change.disconnect()

        # https://stackoverflow.com/questions/10416582/replacing-layout-on-a-qwidget-with-another-layout
        QWidget().setLayout(self.layout()) # Unparent and destroy the current layout so it can be replaced
        self.setLayout(self.__build_keyboard[value](self._key_widgets))
        


    def __find_touched_key_widgets(self, touch_points: list[QTouchEvent.TouchPoint]):
        touched_key_widgets: list[KeyWidget] = []
        for touch in touch_points:
            if touch.state() == Qt.TouchPointReleased: continue

            touched_widget = self.childAt(touch.pos().toPoint())
            if touched_widget is None: continue

            if isinstance(touched_widget, KeyWidget):
                key_widget = touched_widget

            # For some reason, `touched_widget` is a widget that is a child of the QGraphicsView rather than the
            # QGraphicsView itself
            elif isinstance(touched_widget.parent(), RotatableKeyContainer):
                view: RotatableKeyContainer = touched_widget.parent()
                key_widget: KeyWidget = view.key_widget_at_point(touch.pos().toPoint())

                if key_widget is None: continue
                
            else:
                raise TypeError

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
                self.key_polish.emit(key_widget)
