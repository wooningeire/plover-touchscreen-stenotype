from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar
# from plover.gui_qt import Engine
from plover.engine import StenoEngine
from plover.steno import Stroke
from plover.oslayer import PLATFORM

from PyQt5.QtCore import (
    Qt,
    QSize,
    QSettings,
)
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QAction,
)
from PyQt5.QtGui import (
    QIcon,
)


from plover_touchscreen_stenotype.settings import Settings
from plover_touchscreen_stenotype.widgets.KeyboardWidget import KeyboardWidget
from plover_touchscreen_stenotype.widgets.StrokePreview import StrokePreview
from plover_touchscreen_stenotype.widgets.SettingsDialog import SettingsDialog


class Main(Tool):
    #region Overrides

    TITLE = "Touchscreen stenotype"
    ICON = ""
    ROLE = "touchscreen_stenotype"

    def __init__(self, engine: StenoEngine):
        super().__init__(engine)

        self.engine = engine # Override for type hint
        self.__last_stroke_from_widget = False
        """Whether the last emitted stroke originated from this Tool"""
        self.__last_stroke_keys: set[str] | None = None
        self.__last_stroke_engine_enabled = False

        self.__settings = Settings()
        self.restore_state()
        self.finished.connect(self.save_state)
        self.__setup_ui()

        engine.signal_stroked.connect(self._on_stroked)


    def _restore_state(self, settings: QSettings):
        self.__settings.key_layout = settings.value("key_layout", self.__settings.key_layout)
        self.__settings.stroke_preview_stroke = settings.value("stroke_preview_stroke", self.__settings.stroke_preview_stroke, type=bool)
        self.__settings.stroke_preview_translation = settings.value("stroke_preview_translation", self.__settings.stroke_preview_translation, type=bool)

    def _save_state(self, settings: QSettings):
        settings.setValue("key_layout", self.__settings.key_layout)
        settings.setValue("stroke_preview_stroke", self.__settings.stroke_preview_stroke)
        settings.setValue("stroke_preview_translation", self.__settings.stroke_preview_translation)

    #endregion

    def __setup_ui(self):
        self.setAttribute(Qt.WA_AcceptTouchEvents)
        # self.setAttribute(Qt.WA_ShowWithoutActivating)
        # self.setFocusPolicy(Qt.NoFocus)

        # https://stackoverflow.com/questions/71084136/how-to-set-focus-to-the-old-window-on-button-click-in-pyqt5-python
        # self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # For some reason (tested on Windows only), this has to be called before KeyboardWidget is created. Other attributes
        # must also be set before this, otherwise the window will steal focus again
        self.__prevent_window_focus()


        self.translation_display = translation_display = StrokePreview(self.engine, self.__settings, self)

        stenotype = KeyboardWidget(self.__settings, self)
        stenotype.end_stroke.connect(self._on_stenotype_input)
        stenotype.current_stroke_change.connect(self._on_stroke_change)

        settings_action = QAction(self)
        settings_action.setText("Settings")
        settings_action.setIcon(QIcon(r":/settings.svg")) # Loads from Plover's application-wide application resources
        settings_action.triggered.connect(self.__launch_settings_dialog)

        toolbar = ToolBar(settings_action)
        toolbar.setFocusPolicy(Qt.NoFocus)
        for button in toolbar.findChildren(QWidget):
            button.setFocusPolicy(Qt.NoFocus)

        toolbar.setIconSize(QSize(48, 48))


        layout = QGridLayout(self)
        layout.addWidget(translation_display, 0, 0)
        layout.addWidget(toolbar, 0, 0, Qt.AlignBottom | Qt.AlignLeft)
        layout.addWidget(stenotype, 0, 0)
        self.setLayout(layout)


        self.setWindowOpacity(0.9375)


    # https://stackoverflow.com/questions/24582525/how-to-show-clickable-qframe-without-loosing-focus-from-main-window
    # https://stackoverflow.com/questions/68276479/how-to-use-setwindowlongptr-hwnd-gwl-exstyle-ws-ex-noactivate

    # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowlongptrw
    def __prevent_window_focus(self):
        """
        Prevents the stenotype window from taking focus from other programs when the keys are touched. This is a
        cross-platform polyfill for the window flag `Qt.WindowDoesNotAcceptFocus` (which is nonfunctional on
        Windows).

        See https://bugreports.qt.io/browse/QTBUG-36230, https://forum.qt.io/topic/82493/the-windowdoesnotacceptfocus-flag-is-making-me-thirsty/7 for bug information.
        """

        if PLATFORM == "win":
            import ctypes
            from ctypes.wintypes import HWND
            import win32con

            window_handle = HWND(int(self.winId()))

            user32 = ctypes.windll.user32
            user32.SetWindowLongPtrW(
                window_handle,
                win32con.GWL_EXSTYLE,
                user32.GetWindowLongPtrW(window_handle, win32con.GWL_EXSTYLE) | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_APPWINDOW,
            )

        elif PLATFORM == "linux":
            self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)
            # self.setAttribute(Qt.WA_X11DoNotAcceptFocus)

        else:
            self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)


    def _on_stenotype_input(self, stroke_keys: set[str]):
        # Temporarily enable steno output (if not already waiting for a `stroked` hook dispatch)
        if not self.__last_stroke_from_widget:
            self.__last_stroke_engine_enabled = self.engine.output
            self.engine.output = True

        self.__last_stroke_from_widget = True
        self.__last_stroke_keys = stroke_keys
        self.engine._machine._notify(list(stroke_keys))

        # Wait until `stroked` hook is dispatched to reset `self.engine.output`, since it must be True for Suggestions to be shown

        # TODO The current implementation is not infallible because the `stroked` handler does not verify that the stroke it
        # received is the same stroke sent from this method. Multiple strokes may also be sent before the handler is called
        # (can use deque to resolve this)

        self.translation_display.finish_stroke()

    def _on_stroked(self, stroke: Stroke):
        if not self.__last_stroke_from_widget or self.__last_stroke_keys != set(stroke.keys()): return

        # self.last_stroke_label.setText(stroke.rtfcre or "…")
        self.engine.output = self.__last_stroke_engine_enabled
        
        self.__last_stroke_from_widget = False
        self.__last_stroke_keys = None


    def _on_stroke_change(self, stroke_keys: set[str]):
        self.translation_display.display_keys(stroke_keys)


    def resize_from_center(self, width: int, height: int):
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
            # self.last_stroke_label.setText(str(error))
            pass


    def __launch_settings_dialog(self):
        dialog = SettingsDialog(self.__settings, self)
        dialog.open()

# def command_open_window(engine: StenoEngine, arg: str):
#     new_window = Main(engine)
#     new_window.show()
