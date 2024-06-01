from PyQt5.QtCore import (
    QObject,
    pyqtSignal,
    QSettings,
)

from enum import Enum, auto
from weakref import WeakKeyDictionary
from typing import TypeVar, Generic, Any

from .lib.reactivity import Ref, RefAttr, on_many


T = TypeVar("T")
class _PersistentSetting(RefAttr, Generic[T]):
    """`RefAttr` whose class records which settings are on a `Settings` object so they can all be saved/loaded 
        easily.
    """

    setting_types_on_object: WeakKeyDictionary[Any, dict[str, type]] = WeakKeyDictionary()

    #region Overrides

    def __init__(self, expected_type: type[T], qsettings_type_arg: "type | None"=None):
        """
            :param qsettings_type_arg: The type object that should be passed as `type` to `QSettings::value`. If
            `NoneType` (`type(None)`), then the parameter should be omitted.
        """
        super().__init__(expected_type)
        self.__qsettings_type_arg = qsettings_type_arg if qsettings_type_arg is not None else expected_type

    def __set_name__(self, owner_class: type, attr_name: str):
        super().__set_name__(owner_class, attr_name)
        self.__attr_name = attr_name

    def __set__(self, instance: Any, value: T):
        # The owner instance is not accessible before any `__get__` and `__set__` calls, so the recording is done in
        # `__set__` (and `__set__` specifically since values are initialized in the constructor of `Settings`)
        if instance is not None:
            if instance not in _PersistentSetting.setting_types_on_object:
                _PersistentSetting.setting_types_on_object[instance] = {}
            setting_types_dict = _PersistentSetting.setting_types_on_object[instance]

            if self.__attr_name not in setting_types_dict:
                setting_types_dict[self.__attr_name] = self.__qsettings_type_arg

        return super().__set__(instance, value)

    #endregion

class KeyLayout(Enum):
    STAGGERED = auto()
    GRID = auto()


class Settings(QObject):
    key_layout = _PersistentSetting(KeyLayout, type(None))

    stroke_preview_stroke = _PersistentSetting(bool)
    stroke_preview_translation = _PersistentSetting(bool)

    key_width = _PersistentSetting(float)
    key_height = _PersistentSetting(float)
    compound_key_size = _PersistentSetting(float)

    index_stretch = _PersistentSetting(float)
    pinky_stretch = _PersistentSetting(float)

    vowel_set_offset_fac = _PersistentSetting(float)

    index_stagger_fac = _PersistentSetting(float)
    middle_stagger_fac = _PersistentSetting(float)
    ring_stagger_fac = _PersistentSetting(float)
    pinky_stagger_fac = _PersistentSetting(float)

    main_rows_angle = _PersistentSetting(float)
    vowel_rows_angle = _PersistentSetting(float)

    window_opacity = _PersistentSetting(float)
    # Window size is not preserved through the Settings object; Setting object only allows window size to be edited
    # through the settings dialog.
    window_width = RefAttr(float)
    window_height = RefAttr(float)
    frameless = _PersistentSetting(bool)


    key_layout_ref = key_layout.ref_getter()

    stroke_preview_stroke_ref = stroke_preview_stroke.ref_getter()
    stroke_preview_translation_ref = stroke_preview_translation.ref_getter()

    key_width_ref = key_width.ref_getter()
    key_height_ref = key_height.ref_getter()
    compound_key_size_ref = compound_key_size.ref_getter()

    index_stretch_ref = index_stretch.ref_getter()
    pinky_stretch_ref = pinky_stretch.ref_getter()

    vowel_set_offset_fac_ref = vowel_set_offset_fac.ref_getter()

    index_stagger_fac_ref = index_stagger_fac.ref_getter()
    middle_stagger_fac_ref = middle_stagger_fac.ref_getter() 
    ring_stagger_fac_ref = ring_stagger_fac.ref_getter() 
    pinky_stagger_fac_ref = pinky_stagger_fac.ref_getter()

    main_rows_angle_ref = main_rows_angle.ref_getter()
    vowel_rows_angle_ref = vowel_rows_angle.ref_getter()

    window_opacity_ref = window_opacity.ref_getter()
    window_width_ref = window_width.ref_getter()
    window_height_ref = window_height.ref_getter()
    frameless_ref = frameless.ref_getter()


    stroke_preview_change = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.key_layout = KeyLayout.STAGGERED

        self.stroke_preview_stroke = True
        self.stroke_preview_translation = True

        self.key_width = 1.9
        self.key_height = 2.1
        self.compound_key_size = 1.2

        self.index_stretch = -0.1
        self.pinky_stretch = 0.4

        self.vowel_set_offset_fac = 0.6

        self.index_stagger_fac = 0.5
        self.middle_stagger_fac = 0.85
        self.ring_stagger_fac = 0.5
        self.pinky_stagger_fac = 0

        self.main_rows_angle = 22.5
        self.vowel_rows_angle = 20.5

        self.window_opacity = 0.675
        self.window_width_ref = Ref(30)
        self.window_height_ref = Ref(12.5)
        self.frameless = False

        @on_many(self.stroke_preview_stroke_ref.change, self.stroke_preview_translation_ref.change)
        def emit_stroke_preview_change():
            self.stroke_preview_change.emit()
        

    def load(self, settings: QSettings):
        for attr_name, setting_type in _PersistentSetting.setting_types_on_object[self].items():
            default_value = getattr(self, attr_name)
            if setting_type is type(None):
                setattr(self, attr_name, settings.value(attr_name, default_value))
            else:
                setattr(self, attr_name, settings.value(attr_name, default_value, type=setting_type))

    def save(self, settings: QSettings):
        for attr_name in _PersistentSetting.setting_types_on_object[self].keys():
            settings.setValue(attr_name, getattr(self, attr_name))

    @property
    def stroke_preview_full(self):
        return self.stroke_preview_stroke and self.stroke_preview_translation

    @property
    def stroke_preview_visible(self):
        return (self.stroke_preview_stroke or self.stroke_preview_translation)
