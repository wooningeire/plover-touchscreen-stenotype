from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    QSettings,
)

from enum import Enum, auto

from plover_touchscreen_stenotype.util import RefAttr, on_many


class KeyLayout(Enum):
    STAGGERED = auto()
    GRID = auto()


class Settings(QObject):
    key_layout = RefAttr(KeyLayout)

    stroke_preview_stroke = RefAttr(bool)
    stroke_preview_translation = RefAttr(bool)

    key_width = RefAttr(float)
    key_height = RefAttr(float)
    compound_key_size = RefAttr(float)


    key_layout_change = key_layout.signal

    stroke_preview_stroke_change = stroke_preview_stroke.signal
    stroke_preview_translation_change = stroke_preview_translation.signal

    key_width_change = key_width.signal
    key_height_change = key_height.signal
    compound_key_size_change = compound_key_size.signal


    stroke_preview_change = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.key_layout = KeyLayout.STAGGERED

        self.stroke_preview_stroke = True
        self.stroke_preview_translation = True

        self.key_width = 2
        self.key_height = 2.25
        self.compound_key_size = 0.95

        @on_many(self.stroke_preview_stroke_change, self.stroke_preview_translation_change)
        def emit_stroke_preview_change():
            self.stroke_preview_change.emit()
        

    def load(self, settings: QSettings):
        self.key_layout = settings.value("key_layout", self.key_layout)
        self.stroke_preview_stroke = settings.value("stroke_preview_stroke", self.stroke_preview_stroke, type=bool)
        self.stroke_preview_translation = settings.value("stroke_preview_translation", self.stroke_preview_translation, type=bool)

    def save(self, settings: QSettings):
        settings.setValue("key_layout", self.key_layout)
        settings.setValue("stroke_preview_stroke", self.stroke_preview_stroke)
        settings.setValue("stroke_preview_translation", self.stroke_preview_translation)

    @property
    def stroke_preview_full(self):
        return self.stroke_preview_stroke and self.stroke_preview_translation

    @property
    def stroke_preview_visible(self):
        return self.stroke_preview_stroke or self.stroke_preview_translation
