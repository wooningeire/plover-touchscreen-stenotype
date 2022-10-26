from typing import Iterable
from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar
# from plover.gui_qt import Engine
from plover.engine import StenoEngine
from plover.steno import Stroke
from plover.oslayer import PLATFORM

from plover import system
from plover.translation import Translation, Translator, _mapping_to_macro

from PyQt5.QtCore import (
    Qt,
    QSize,
    QPoint,
    QSettings,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QSpacerItem,
    QAction,
)
from PyQt5.QtGui import (
    QFont,
    QIcon,
)


from plover_onscreen_stenotype.settings import Settings, KeyLayout
from plover_onscreen_stenotype.widgets.KeyboardWidget import KeyboardWidget
from plover_onscreen_stenotype.widgets.SettingsDialog import SettingsDialog
from plover_onscreen_stenotype.widgets.build_keyboard import KEY_SIZE
from plover_onscreen_stenotype.util import UseDpi


class Main(Tool):
    #region Overrides

    TITLE = "On-screen stenotype"
    ICON = ""
    ROLE = "onscreen_stenotype"

    def __init__(self, engine: StenoEngine):
        super().__init__(engine)

        self.engine = engine # Override for type hint
        self.__last_stroke_from_widget = False
        """Whether the last emitted stroke originated from the on-screen stenotype"""
        self.__last_stroke_keys: set[str] | None = None
        self.__last_stroke_engine_enabled = False

        self.__next_translation_defined = False

        self.__settings = Settings()
        self.restore_state()
        self.finished.connect(self.save_state)
        self.__setup_ui()

        engine.signal_stroked.connect(self._on_stroked)


    def _restore_state(self, settings: QSettings):
        self.__settings.key_layout = settings.value("key_layout", self.__settings.key_layout)

    def _save_state(self, settings: QSettings):
        settings.setValue("key_layout", self.__settings.key_layout)

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


        dpi = UseDpi(self)

        self.last_stroke_label = last_stroke_label = QLabel(self)
        last_stroke_label.setFont(QFont("Atkinson Hyperlegible", 16))

        self.last_translation_label = translation_label = QLabel(self)
        translation_label.setFont(QFont("Atkinson Hyperlegible", 20))
        translation_label.setText("…")

        self.translation_display_layout = labels_layout = QVBoxLayout()
        labels_layout.addWidget(last_stroke_label, 0, Qt.AlignCenter)
        labels_layout.addSpacing(-8)
        labels_layout.addWidget(translation_label, 0, Qt.AlignCenter)

        labels_layout.setSpacing(0)


        display_alignment_layout = QGridLayout()
        display_alignment_layout.setColumnStretch(0, 1)
        display_alignment_layout.setColumnStretch(1, 0)
        def resize_display_alignment():
            display_alignment_layout.setColumnMinimumWidth(1, dpi.px(KEY_SIZE))
        resize_display_alignment()
        dpi.change.connect(resize_display_alignment)

        display_alignment_layout.addLayout(labels_layout, 0, 0)
        self._move_translation_display(self.__settings.key_layout)
        display_alignment_layout.addItem(QSpacerItem(0, 0), 0, 1)
        display_alignment_layout.setSpacing(0)


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
        layout.addLayout(display_alignment_layout, 0, 0)
        layout.addWidget(toolbar, 0, 0, Qt.AlignBottom | Qt.AlignLeft)
        layout.addWidget(stenotype, 0, 0)
        self.setLayout(layout)

        self.__settings.key_layout_change.connect(self._move_translation_display)


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

        self.last_stroke_label.setStyleSheet("")
        self.last_translation_label.setStyleSheet(f"""color: #{"ff" if self.__next_translation_defined else "3f"}000000;""")

    def _on_stroked(self, stroke: Stroke):
        if not self.__last_stroke_from_widget or self.__last_stroke_keys != set(stroke.keys()): return

        # self.last_stroke_label.setText(stroke.rtfcre or "…")
        self.engine.output = self.__last_stroke_engine_enabled
        
        self.__last_stroke_from_widget = False
        self.__last_stroke_keys = None


    def _on_stroke_change(self, stroke_keys: set[str]):
        translation = _coming_translation(self.engine, stroke_keys)
        self.__next_translation_defined = has_translation = translation.english is not None

        word = translation.english.replace("\n", "\\n") if has_translation else "[undefined]"
        self.last_stroke_label.setText(" / ".join(translation.rtfcre))
        self.last_translation_label.setText(word)

        self.last_stroke_label.setStyleSheet("color: #41796a;")
        self.last_translation_label.setStyleSheet(f"""color: #{"ff" if has_translation else "5f"}41796a;""")

    def _move_translation_display(self, key_layout: KeyLayout):
        if key_layout == KeyLayout.GRID:
            self.translation_display_layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        else:
            self.translation_display_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)


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
            self.last_stroke_label.setText(str(error))


    def __launch_settings_dialog(self):
        dialog = SettingsDialog(self.__settings, self)
        dialog.open()
        


def _coming_translation(engine: StenoEngine, keys: Iterable[str]) -> Translation:
    """Computes the translation that will result if the stroke indicated by `keys` is sent to the engine"""

    translator: Translator = engine._translator
    stroke: Stroke = Stroke(keys)

    # translator._state is temporarily cleared when engine output is set to False
    if not engine.output:
        translator.set_state(engine._running_state)
    
    
    # This is the body of `Translator.translate_stroke`, but without the side effects

    max_key_length = translator._dictionary.longest_key
    mapping = translator._lookup_with_prefix(max_key_length, translator.get_state().translations, [stroke])

    macro = _mapping_to_macro(mapping, stroke)
    if macro is not None:
        translation = Translation([stroke], f"={macro.name}")

    else:
        translation = (
            translator._find_longest_match(2, max_key_length, stroke) or
            (mapping is not None and Translation([stroke], mapping)) or
            translator._find_longest_match(1, max_key_length, stroke, system.SUFFIX_KEYS) or
            Translation([stroke], None)
        )
    

    if not engine.output:
        translator.clear_state()

    
    return translation

# def command_open_window(engine: StenoEngine, arg: str):
#     new_window = Main(engine)
#     new_window.show()
