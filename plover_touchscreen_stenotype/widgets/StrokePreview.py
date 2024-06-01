from plover.gui_qt.engine import Engine
from plover.steno import Stroke

from plover import system
from plover.translation import Translation, Translator, _mapping_to_macro # TODO access violation

from PyQt5.QtCore import (
    Qt,
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
)
from PyQt5.QtGui import (
    QFont,
)


from math import cos, radians
from typing import Iterable

from .DisplayAlignmentLayout import DisplayAlignmentLayout
from ..settings import Settings, KeyLayout
from ..lib.reactivity import Ref, watch, watch_many
from ..lib.UseDpi import UseDpi
from ..lib.constants import FONT_FAMILY

class StrokePreview(QWidget):
    def __init__(self, engine: Engine, settings: Settings, right_left_width_diff: Ref[float], parent: QWidget=None):
        super().__init__(parent)

        self.__engine = engine
        self.__settings = settings

        self.__last_translation: Translation | None = None
        self.__last_stroke_matched = True

        self.__setup_ui(right_left_width_diff)

    def __setup_ui(self, right_left_width_diff: Ref[float]):
        dpi = UseDpi(self)

        #region Labels
        self.__stroke_label = stroke_label = QLabel(self)
        self.__translation_label = translation_label = QLabel(self)

        stroke_label.setTextFormat(Qt.PlainText)
        translation_label.setTextFormat(Qt.PlainText)

        # The horizontal size policies of the labels must be set to Ignored, or otherwise they will cause the window to
        # resize to fit the text if the text is too long. However, that alone just causes the labels to resize to the
        # widest item in the QVBoxLayout `labels_layout`, which would have a width of 0 since the label widths are
        # ignored and the rest of the items are spacers. The strut is therefore needed to set the width of the layout
        # to the width of the parent column in the QGridLayout `display_alignment_layout`, allowing the labels the full
        # column width to display the text yet limiting them to that width so they do not resize the window.
        strut = QWidget(self)
        strut.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # https://stackoverflow.com/questions/21739119/qt-hboxlayout-stop-mainwindow-from-resizing-to-contents
        stroke_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        translation_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        labels_layout = QVBoxLayout()
        
        labels_layout.addSpacerItem(top_spacer := QSpacerItem(0, 0))
        labels_layout.addWidget(stroke_label, 0, Qt.AlignCenter)
        labels_layout.addSpacerItem(middle_spacer := QSpacerItem(0, 0))
        labels_layout.addWidget(translation_label, 0, Qt.AlignCenter)
        labels_layout.addWidget(strut)


        @watch(dpi.change)
        def resize_label_fonts(): # Set font sizes in px rather than pt so they fit in the keyboard gaps
            stroke_label_font = QFont(FONT_FAMILY)
            translation_label_font = QFont(FONT_FAMILY)

            stroke_label_font.setPixelSize(dpi.dp(16.8 if self.__settings.stroke_preview_translation else 21))
            translation_label_font.setPixelSize(dpi.dp(21))

            stroke_label.setFont(stroke_label_font)
            middle_spacer.changeSize(0, dpi.dp(-4) if self.__settings.stroke_preview_full else 0)
            translation_label.setFont(translation_label_font)

            labels_layout.invalidate()

        labels_layout.setSpacing(0)
        #endregion


        #region Display alignment
        display_alignment_layout = DisplayAlignmentLayout(right_left_width_diff)
        display_alignment_layout.addLayout(labels_layout, 0, 0)

        @watch_many(dpi.change, self.__settings.key_layout_ref.change)
        def reposition_labels():
            if self.__settings.key_layout == KeyLayout.GRID:
                labels_layout.setAlignment(Qt.AlignBottom)
                top_spacer.changeSize(0, 0)
            else:
                labels_layout.setAlignment(Qt.AlignTop)
                top_spacer.changeSize(0, -8)

            labels_layout.invalidate()  # Must be called for layout to move

        self.setLayout(display_alignment_layout)
        #endregion


        #region Settings reactivity
        @watch(self.__settings.stroke_preview_change)
        def on_settings_change():
            stroke_label.setVisible(self.__settings.stroke_preview_stroke)
            translation_label.setVisible(self.__settings.stroke_preview_translation)

            resize_label_fonts()

            self.__display_translation(self.__last_translation, self.__last_stroke_matched)
            self.finish_stroke()
        #endregion


    def display_keys(self, stroke_keys: Iterable[str]):
        if not self.__settings.stroke_preview_visible:
            # The coming translation will not be computed
            # When the stroke preview is reenabled, this will cause the placeholder to be shown again instead of an old
            # translation
            self.__last_translation = None
            return

        translation, stroke_matched = _coming_translation(self.__engine, stroke_keys)
        self.__display_translation(translation, stroke_matched)


    def __display_translation(self, translation: "Translation | None", stroke_matched: bool):
        self.__last_translation = translation
        self.__last_stroke_matched = stroke_matched
        if not self.__settings.stroke_preview_visible:
            return

        if translation is None and self.__settings.stroke_preview_translation:
            self.__stroke_label.setText("")
            self.__translation_label.setText("…")
            return
        elif translation is None:
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


def _coming_translation(engine: Engine, keys: Iterable[str]) -> tuple[Translation, bool]:
    """Computes the translation that will result if the stroke defined by `keys` is sent to the engine.
    
    :returns: The translation that will result, and if a match was found
    :rtype: tuple[Translation, bool]
    """
    # TODO access violations

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