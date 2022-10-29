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

        self.__last_translation: Translation | None = None
        self.__last_stroke_matched = True

        self.__setup_ui()

    def __setup_ui(self):
        dpi = UseDpi(self)

        #region Labels
        self.__stroke_label = stroke_label = QLabel(self)
        self.__translation_label = translation_label = QLabel(self)

        labels_layout = QVBoxLayout()
        
        top_spacer = QSpacerItem(0, 0)
        labels_layout.addSpacerItem(top_spacer)
        labels_layout.addWidget(stroke_label, 0, Qt.AlignCenter)
        labels_layout.addSpacerItem(middle_spacer := QSpacerItem(0, 0))
        labels_layout.addWidget(translation_label, 0, Qt.AlignCenter)

        def resize_labels(): # Set font sizes in px rather than pt so they fit in the keyboard gaps
            stroke_label_font = QFont("Atkinson Hyperlegible")
            translation_label_font = QFont("Atkinson Hyperlegible")

            if self.screen().physicalDotsPerInch() < 120: # Arbitrary cutoff
                stroke_label_font.setPixelSize(dpi.dp(19.2 if self.__settings.stroke_preview_translation else 24))
                translation_label_font.setPixelSize(dpi.dp(24))
            else:
                stroke_label_font.setPixelSize(dpi.dp(14.4 if self.__settings.stroke_preview_translation else 18))
                translation_label_font.setPixelSize(dpi.dp(18))

            # stroke_label_font.setPixelSize(dpi.dp(18))
            # translation_label_font.setPixelSize(dpi.dp(24))

            stroke_label.setFont(stroke_label_font)
            middle_spacer.changeSize(0, dpi.dp(-5) if self.__settings.stroke_preview_full else 0)
            translation_label.setFont(translation_label_font)

            labels_layout.invalidate()
        resize_labels()
        dpi.change.connect(resize_labels)

        labels_layout.setSpacing(0)
        #endregion


        #region Display alignment
        display_alignment_layout = QGridLayout()
        display_alignment_layout.setColumnStretch(0, 1)
        display_alignment_layout.setColumnStretch(1, 0)

        def resize_display_alignment():
            display_alignment_layout.setColumnMinimumWidth(1, dpi.cm(KEY_WIDTH))
        resize_display_alignment()
        dpi.change.connect(resize_display_alignment)


        display_alignment_layout.addLayout(labels_layout, 0, 0)
        def move_translation_display():
            if self.__settings.key_layout == KeyLayout.GRID:
                labels_layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
                top_spacer.changeSize(0, 0)
            else:
                labels_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
                top_spacer.changeSize(0, -8)

            labels_layout.invalidate()  # Must be called for layout to move
        move_translation_display()
        self.__settings.key_layout_change.connect(move_translation_display)
        dpi.change.connect(move_translation_display)
        
        display_alignment_layout.addItem(QSpacerItem(0, 0), 0, 1)
        display_alignment_layout.setSpacing(0)
        display_alignment_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(display_alignment_layout)
        #endregion


        #region Settings reactivity
        def on_settings_change():
            stroke_label.setVisible(self.__settings.stroke_preview_stroke)
            translation_label.setVisible(self.__settings.stroke_preview_translation)

            resize_labels()

            self.__display_translation(self.__last_translation, self.__last_stroke_matched)
            self.finish_stroke()
        on_settings_change()
        self.__settings.stroke_preview_change.connect(on_settings_change)
        #endregion


    def display_keys(self, stroke_keys: Iterable[str]):
        if not self.__settings.stroke_preview_visible:
            return

        translation, stroke_matched = _coming_translation(self.__engine, stroke_keys)
        self.__display_translation(translation, stroke_matched)


    def __display_translation(self, translation: "Translation | None", stroke_matched: bool):
        self.__last_translation = translation
        self.__last_stroke_matched = stroke_matched
        if not self.__settings.stroke_preview_visible:
            return

        if not translation and self.__settings.stroke_preview_translation:
            self.__stroke_label.setText("")
            self.__translation_label.setText("…")
            return
        elif not translation:
            self.__stroke_label.setText("…")
            return
            

        if self.__settings.stroke_preview_stroke:
            self.__stroke_label.setText(" / ".join(translation.rtfcre))

            self.__stroke_label.setStyleSheet("color: #41796a;")

        if self.__settings.stroke_preview_translation:
            if translation.english is not None:
                word = translation.english.replace("\n", "\\n")
            else:
                word = "[no match]" if self.__settings.stroke_preview_stroke else translation.strokes[0].rtfcre
            self.__translation_label.setText(word)
        
            self.__translation_label.setStyleSheet(f"""color: #{"ff" if stroke_matched else "5f"}41796a;""")


    def finish_stroke(self):
        self.__stroke_label.setStyleSheet("")
        self.__translation_label.setStyleSheet(f"""color: #{"ff" if self.__last_stroke_matched else "3f"}000000;""")


def _coming_translation(engine: StenoEngine, keys: Iterable[str]) -> tuple[Translation, bool]:
    """Computes the translation that will result if the stroke defined by `keys` is sent to the engine.
    
    :returns: The translation that will result, and if a match was found
    :rtype: tuple[Translation, bool]
    """

    translator: Translator = engine._translator
    stroke: Stroke = Stroke(keys)

    # translator._state is temporarily cleared when engine output is set to False
    if not engine.output:
        translator.set_state(engine._running_state)
    
    
    # This is mostly the body of `Translator.translate_stroke`, but without the side effects

    max_key_length = translator._dictionary.longest_key
    mapping = translator._lookup_with_prefix(max_key_length, translator.get_state().translations, [stroke])


    translation = (
        translator._find_longest_match(2, max_key_length, stroke) or
        (mapping is not None and Translation([stroke], mapping)) or
        translator._find_longest_match(1, max_key_length, stroke, system.SUFFIX_KEYS) or
        Translation([stroke], None)
    )

    stroke_matched = translation.english is not None

    if translation.english is None:
        macro = _mapping_to_macro(mapping, stroke)
        if macro is not None:
            translation = Translation([stroke], f"={macro.name}")
    

    if not engine.output:
        translator.clear_state()

    
    return translation, stroke_matched