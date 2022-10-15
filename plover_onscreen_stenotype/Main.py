from plover.gui_qt.tool import Tool
# from plover.gui_qt import Engine
from plover.engine import StenoEngine
from plover.steno import Stroke

from PyQt5.QtCore import (
    Qt,
    QSize,
    QPoint,
)
from PyQt5.QtWidgets import (
    QLabel,
    QGridLayout,
)
from PyQt5.QtGui import (
    QFont,
)

import ctypes
from ctypes.wintypes import HWND
import win32con


from plover_onscreen_stenotype.widgets.KeyboardWidget import KeyboardWidget


class Main(Tool):
    #region Overrides

    TITLE = "On-screen stenotype"
    ICON = ""
    ROLE = "onscreen_stenotype"

    def __init__(self, engine: StenoEngine):
        super().__init__(engine)

        self.engine = engine
        self.__last_stroke_from_widget = False
        """Whether the last emitted stroke originated from the on-screen stenotype"""
        self.__last_stroke_keys: set[str] | None = None
        self.__last_stroke_engine_enabled = False

        self.__setup_ui()

        engine.signal_stroked.connect(self._on_stroked)

    #endregion

    def __setup_ui(self):
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        # self.setAttribute(Qt.WA_ShowWithoutActivating)
        # self.setFocusPolicy(Qt.NoFocus)

        # https://stackoverflow.com/questions/71084136/how-to-set-focus-to-the-old-window-on-button-click-in-pyqt5-python
        # self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # For some reason, this has to be called before KeyboardWidget is created. Other attributes must also be
        # set before this, otherwise the window will steal focus again
        self.__prevent_window_focus()


        self.last_stroke_label = last_stroke_label = QLabel(self)
        last_stroke_label.setFont(QFont("Atkinson Hyperlegible", 24))
        last_stroke_label.setText("…")

        stenotype = KeyboardWidget(self)
        stenotype.end_stroke.connect(self._on_stenotype_input)

        self.layout = layout = QGridLayout(self)
        layout.addWidget(last_stroke_label, 0, 0, Qt.AlignBottom | Qt.AlignRight)
        layout.addWidget(stenotype, 0, 0, Qt.AlignVCenter)
        self.setLayout(layout)


        self.setWindowOpacity(0.9375)


    # https://stackoverflow.com/questions/24582525/how-to-show-clickable-qframe-without-loosing-focus-from-main-window
    # https://stackoverflow.com/questions/68276479/how-to-use-setwindowlongptr-hwnd-gwl-exstyle-ws-ex-noactivate

    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
    def __prevent_window_focus(self):
        """
        Prevents the stenotype window from taking focus from other programs when the keys are touched. Currently, this
        is an alternative to the nonfunctional Qt window flag `Qt.WindowDoesNotAcceptFocus` and Unix-only attribute
        `Qt.WA_X11DoNotAcceptFocus`. This function is currently designed for Windows only.

        See https://bugreports.qt.io/browse/QTBUG-36230, https://forum.qt.io/topic/82493/the-windowdoesnotacceptfocus-flag-is-making-me-thirsty/7 for bug information.
        """

        window_handle = HWND(int(self.winId()))

        user32 = ctypes.windll.user32
        user32.SetWindowLongPtrW(
            window_handle,
            win32con.GWL_EXSTYLE,
            user32.GetWindowLongPtrW(window_handle, win32con.GWL_EXSTYLE) | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_APPWINDOW,
        )

    def _on_stenotype_input(self, stroke_keys: set[str]):
        # Temporarily enable steno output
        self.__last_stroke_engine_enabled = self.engine.output
        self.engine.output = True

        self.__last_stroke_from_widget = True
        self.__last_stroke_keys = stroke_keys
        self.engine._machine._notify(list(stroke_keys))

        # Wait until `stroked` hook is dispatched to reset `self.engine.output`, since it must be True for Suggestions to be shown

        # TODO The current implementation is not infallible because the `stroked` handler does not verify that the stroke it
        # received is the same stroke sent from this method. Multiple strokes may also be sent before the handler is called
        # (use deque to resolve this)

    def _on_stroked(self, stroke: Stroke):
        # if not self.__last_stroke_from_widget: return
        if not self.__last_stroke_from_widget or self.__last_stroke_keys != set(stroke.keys()): return

        self.last_stroke_label.setText(stroke.rtfcre or "…")
        self.engine.output = self.__last_stroke_engine_enabled
        
        self.__last_stroke_from_widget = False
        self.__last_stroke_keys = None

    def resize_from_center(self, width: int, height: int):
        self.last_stroke_label.setText("abc")
        try:
            rect = self.geometry()
            old_center = rect.center()

            # In practice, the new size will be constrained to the minimum size, so it is not necessarily the given size
            new_size = QSize(
                max(self.minimumWidth(), width),
                max(self.minimumHeight(), height),
            )

            rect.setSize(new_size)
            rect.moveCenter(old_center)
            
            self.setGeometry(rect)

        except Exception as error:
            self.last_stroke_label.setText(str(error))
        


# def command_open_window(engine: StenoEngine, arg: str):
#     new_window = Main(engine)
#     new_window.show()
