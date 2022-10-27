from typing import Iterable
from plover.engine import StenoEngine
from plover.steno import Stroke

from plover import system
from plover.translation import Translation, Translator, _mapping_to_macro

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QSpacerItem,
)
from PyQt5.QtGui import (
    QFont,
)


from plover_onscreen_stenotype.settings import Settings, KeyLayout
from plover_onscreen_stenotype.util import UseDpi
from plover_onscreen_stenotype.widgets.build_keyboard import KEY_WIDTH


class TranslationDisplay(QWidget):

    def __init__(self, engine: StenoEngine, settings: Settings, parent: QWidget=None):
        super().__init__(parent)

        self.__engine = engine
        self.__settings = settings

        self.__next_translation_defined = False

        self.__setup_ui()

    def __setup_ui(self):
        dpi = UseDpi(self)

        self.last_stroke_label = last_stroke_label = QLabel(self)
        self.last_translation_label = translation_label = QLabel(self)
        translation_label.setText("…")

        self.__labels_layout = labels_layout = QVBoxLayout()
        
        self.__top_spacer = top_spacer = QSpacerItem(0, -8)
        labels_layout.addSpacerItem(top_spacer)
        labels_layout.addWidget(last_stroke_label, 0, Qt.AlignCenter)
        labels_layout.addSpacerItem(middle_spacer := QSpacerItem(0, 0))
        labels_layout.addWidget(translation_label, 0, Qt.AlignCenter)

        def resize_labels(): # Set font sizes in px rather than pt so they fit in the keyboard gaps
            stroke_label_font = QFont("Atkinson Hyperlegible")
            translation_label_font = QFont("Atkinson Hyperlegible")

            if self.screen().physicalDotsPerInch() < 96: # Arbitrary cutoff
                stroke_label_font.setPixelSize(dpi.dp(19.2))
                translation_label_font.setPixelSize(dpi.dp(24))
            else:
                stroke_label_font.setPixelSize(dpi.dp(14.4))
                translation_label_font.setPixelSize(dpi.dp(18))

            last_stroke_label.setFont(stroke_label_font)
            middle_spacer.changeSize(0, dpi.dp(-5))
            translation_label.setFont(translation_label_font)

            labels_layout.invalidate()
        resize_labels()
        dpi.change.connect(resize_labels)


        labels_layout.setSpacing(0)


        display_alignment_layout = QGridLayout()
        display_alignment_layout.setColumnStretch(0, 1)
        display_alignment_layout.setColumnStretch(1, 0)

        def resize_display_alignment():
            display_alignment_layout.setColumnMinimumWidth(1, dpi.cm(KEY_WIDTH))
        resize_display_alignment()
        dpi.change.connect(resize_display_alignment)

        display_alignment_layout.addLayout(labels_layout, 0, 0)
        self.__move_translation_display()
        self.__settings.key_layout_change.connect(lambda: self.__move_translation_display())
        dpi.change.connect(self.__move_translation_display)
        
        display_alignment_layout.addItem(QSpacerItem(0, 0), 0, 1)
        display_alignment_layout.setSpacing(0)
        display_alignment_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(display_alignment_layout)


    def display_keys(self, stroke_keys: Iterable[str]):
        translation = _coming_translation(self.__engine, stroke_keys)
        self.__next_translation_defined = has_translation = translation.english is not None

        word = translation.english.replace("\n", "\\n") if has_translation else "[no match]"
        self.last_stroke_label.setText(" / ".join(translation.rtfcre))
        self.last_translation_label.setText(word)

        self.last_stroke_label.setStyleSheet("color: #41796a;")
        self.last_translation_label.setStyleSheet(f"""color: #{"ff" if has_translation else "5f"}41796a;""")

    def finish_stroke(self):
        self.last_stroke_label.setStyleSheet("")
        self.last_translation_label.setStyleSheet(f"""color: #{"ff" if self.__next_translation_defined else "3f"}000000;""")


    def __move_translation_display(self):
        if self.__settings.key_layout == KeyLayout.GRID:
            self.__labels_layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
            self.__top_spacer.changeSize(0, 0)
        else:
            self.__labels_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            self.__top_spacer.changeSize(0, -8)

        self.__labels_layout.invalidate() # Must be called for layout to move


def _coming_translation(engine: StenoEngine, keys: Iterable[str]) -> Translation:
    """Computes the translation that will result if the stroke defined by `keys` is sent to the engine."""

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