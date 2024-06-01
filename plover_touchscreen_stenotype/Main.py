from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar
from plover.gui_qt.engine import Engine
from plover.steno import Stroke
from plover.oslayer import PLATFORM

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QSize,
    QSettings,
    QPoint,
)
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QAction,
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence,
    QMouseEvent,
)


from .settings import Settings
from .lib.reactivity import Ref, on, on_many, watch
from .lib.UseDpi import UseDpi
from .widgets.KeyboardWidget import KeyboardWidget
from .widgets.StrokePreview import StrokePreview
from .widgets.SettingsDialog import SettingsDialog
from .widgets.CenterControls import CenterControls


_window_instance: "Main | None" = None

class Main(Tool):
    #region Overrides

    TITLE = "Touchscreen stenotype"
    ICON = ""
    ROLE = "touchscreen_stenotype"


    close_stroked = pyqtSignal()
    minimize_stroked = pyqtSignal()
    open_settings_stroked = pyqtSignal()


    __dpi: UseDpi

    def __init__(self, engine: Engine):
        global _window_instance
        
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

        engine.signal_stroked.connect(self.__on_stroked)

        _window_instance = self
        @on(self.finished)
        def clear_instance():
            global _window_instance

            _window_instance = None

        
        self.close_stroked.connect(lambda: self.close())
        self.minimize_stroked.connect(lambda: self.setWindowState(Qt.WindowMinimized))


    def _restore_state(self, settings: QSettings):
        self.__settings.load(settings)

    def _save_state(self, settings: QSettings):
        self.__settings.save(settings)
    

    # https://github.com/Kaoffie/plover_svg_layout_display/blob/master/plover_svg_layout_display/layout_ui.py#L91
    __drag_start_position: "QPoint | None" = None
    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.LeftButton): return
        self.move(event.globalPos() - self.__drag_start_position)

    def mousePressEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.LeftButton): return
        self.__drag_start_position = event.globalPos() - self.frameGeometry().topLeft()

    #endregion

    def __setup_ui(self):
        self.__dpi = dpi = UseDpi(self)

        self.setAttribute(Qt.WA_AcceptTouchEvents)
        # self.setAttribute(Qt.WA_ShowWithoutActivating)
        # self.setFocusPolicy(Qt.NoFocus)

        # https://stackoverflow.com/questions/71084136/how-to-set-focus-to-the-old-window-on-button-click-in-pyqt5-python
        # self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.WindowDoesNotAcceptFocus)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)

        # Cannot be moved to listener due to Qt5 bug
        self.setWindowFlag(Qt.FramelessWindowHint, on=self.__settings.frameless)
        self.setAttribute(Qt.WA_TranslucentBackground, on=self.__settings.frameless)

        # For some reason (tested on Windows only), this has to be called before KeyboardWidget is created. Other attributes
        # must also be set before this, otherwise the window will steal focus again
        self.__prevent_window_focus()


        left_right_width_diff = Ref(0)

        self.stroke_preview = stroke_preview = StrokePreview(self.engine, self.__settings, left_right_width_diff, self)

        stenotype = KeyboardWidget(self.__settings, left_right_width_diff, self)
        stenotype.end_stroke.connect(self.__on_stenotype_input)
        stenotype.current_stroke_change.connect(self.__on_stroke_change)

        settings_action = QAction(self)
        settings_action.setText("Settings")
        settings_action.setShortcut(QKeySequence("Ctrl+S"))
        settings_action.setIcon(QIcon(r":/settings.svg")) # Loads from Plover's application-wide application resources
        settings_action.triggered.connect(self.__launch_settings_dialog)
        @on(self.open_settings_stroked)
        def trigger_settings_action():
            settings_action.trigger()

        toolbar = ToolBar(settings_action)

        toolbar.setFocusPolicy(Qt.NoFocus)
        for button in toolbar.findChildren(QWidget):
            button.setFocusPolicy(Qt.NoFocus)

        @watch(dpi.change)
        def resize_toolbar_button_size():
            toolbar.setIconSize(QSize(dpi.dp(32), dpi.dp(32)))
        toolbar.setOrientation(Qt.Vertical)

        controls = CenterControls(self.mousePressEvent, toolbar, left_right_width_diff, self)

        layout = QGridLayout(self)
        layout.addWidget(stroke_preview, 0, 0)
        layout.addWidget(controls, 0, 0, Qt.AlignCenter)
        layout.addWidget(stenotype, 0, 0)
        self.setLayout(layout)


        @watch(self.__settings.window_opacity_ref.change)
        def set_window_opacity():
            self.setWindowOpacity(self.__settings.window_opacity)

        # @watch(self.__settings.frameless_ref.change)
        # def set_frameless():
        #     self.setAttribute(Qt.WA_TranslucentBackground, on=self.__settings.frameless)
        #     self.setWindowFlags(Qt.FramelessWindowHint, on=self.__settings.frameless)


        @on_many(self.__settings.window_width_ref.change, self.__settings.window_height_ref.change)
        def set_window_size():
            self.resize(dpi.cm(self.__settings.window_width), dpi.cm(self.__settings.window_height))


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

        # On Windows: does not work by itself, but prevents focus from being taken from other Plover windows
        self.setWindowFlag(Qt.WindowDoesNotAcceptFocus)

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

        # elif PLATFORM == "linux":
        #     # self.setAttribute(Qt.WA_X11DoNotAcceptFocus)


    def __on_stenotype_input(self, stroke_keys: set[str]):
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

        self.stroke_preview.finish_stroke()

    def __on_stroked(self, stroke: Stroke):
        if not self.__last_stroke_from_widget or self.__last_stroke_keys != set(stroke.keys()): return

        if self.engine.output == False:
            # The engine output was disabled before it was set again; {PLOVER:TOGGLE} was likely triggered
            self.engine.output = not self.__last_stroke_engine_enabled
        else:
            self.engine.output = self.__last_stroke_engine_enabled
        
        self.__last_stroke_from_widget = False
        self.__last_stroke_keys = None


    def __on_stroke_change(self, stroke_keys: set[str]):
        self.stroke_preview.display_keys(stroke_keys)


    """ def resize_from_center(self, width: int, height: int):
        rect = self.geometry()
        old_center = rect.center()

        # In practice, the new size will be constrained to the minimum size, so it is not necessarily the given size
        new_size = QSize(
            max(self.minimumWidth(), width),
            max(self.minimumHeight(), height),
        )

        rect.setSize(new_size)
        rect.moveCenter(old_center)
        
        self.setGeometry(rect) """


    def __launch_settings_dialog(self):
        # Lazily update the window size stored on the Settings object since they are only used for the settings dialog
        self.__settings.window_width = self.__dpi.px_to_cm(self.width())
        self.__settings.window_height = self.__dpi.px_to_cm(self.height())

        dialog = SettingsDialog(self.__settings, self)
        dialog.open()


# def command_open(engine: Engine, arg: str):
#     if _window_instance is not None: return
#     new_window = Main(engine)
#     new_window.show()

def command_close(engine: Engine, arg: str):
    if _window_instance is None: return
    _window_instance.close_stroked.emit()

def command_minimize(engine: Engine, arg: str):
    if _window_instance is None: return
    _window_instance.minimize_stroked.emit()
    
def command_open_settings(engine: Engine, arg: str):
    if _window_instance is None: return
    _window_instance.open_settings_stroked.emit()