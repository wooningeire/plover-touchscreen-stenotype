from PyQt5.QtCore import (
    pyqtBoundSignal,
    QPoint,
    QPointF,
)
from PyQt5.QtWidgets import (
    QWidget,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsView,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtGui import (
    QTouchEvent,
    QTransform,
)

from plover.steno import Stroke

from .KeyWidget import KeyWidget
from ..lib.keyboard_layout.LayoutDescriptor import Group, GroupOrganizationType, KeyGroup, GroupOrganizationType
from ..lib.reactivity import watch, watch_many, Ref, computed
from ..lib.UseDpi import UseDpi
from ..lib.constants import KEY_STYLESHEET
from ..lib.util import not_none, render, child, Point

def set_group_transforms(item: QGraphicsItem, group: "Group | KeyGroup", bounding_rect_change_signals: list[pyqtBoundSignal], *, pos: Ref[Point], dpi: UseDpi):
    @watch_many(pos.change, *bounding_rect_change_signals, dpi.change)
    def set_group_pos():
        rect = item.boundingRect()
        item.setPos(
            dpi.cm(pos.value.x) - rect.width() * group.alignment.value[0],
            dpi.cm(pos.value.y) - rect.height() * group.alignment.value[1],
        )

    if group.angle is not None:
        @watch_many(*bounding_rect_change_signals, dpi.change)
        def set_origin_point():
            item.setTransformOriginPoint(
                item.boundingRect().width() * group.alignment.value[0],
                item.boundingRect().height() * group.alignment.value[1],
            )

        @watch(group.angle.change)
        def set_group_angle():
            item.setRotation(group.angle.value)

class KeyGroupWidget(QWidget):
    def __init__(
        self,
        group: KeyGroup,
        scene: QGraphicsScene,
        view: QGraphicsView,
        parent: "QWidget | None"=None,
        *,
        touched_key_widgets: Ref[set[KeyWidget]],
        current_stroke: Ref[Stroke],
        dpi: UseDpi,
    ):
        super().__init__(parent)

        items: list[QGraphicsItem] = []
        bounding_rect_change_signals: list[pyqtBoundSignal] = []

        self.__key_widgets: list[KeyWidget] = []


        last_touch: "Ref[QTouchEvent.TouchPoint | None]" = Ref(None)
        last_touched_key_widget: "Ref[KeyWidget | None]" = Ref(None)

        def compute_effective_pos():
            if last_touched_key_widget.value is not None and last_touch.value is not None:
                proxy_rect = proxy.boundingRect()
                key_widget_geometry = last_touched_key_widget.value.geometry()
                key_widget_transform = proxy.deviceTransform(view.viewportTransform()).translate(-proxy_rect.x(), -proxy_rect.y())
                
                local_touch_pos = key_widget_transform.inverted()[0].map(last_touch.value.pos())
                return effective_pos.value + Point(
                    dpi.px_to_cm(local_touch_pos.x() - key_widget_geometry.center().x()),
                    dpi.px_to_cm(local_touch_pos.y() - key_widget_geometry.center().y()),
                )
            
            return Point(group.x.value, group.y.value)

        effective_pos = computed(compute_effective_pos,
                last_touch, last_touched_key_widget, group.x, group.y)


        def notify_touch_release(touch: QTouchEvent.TouchPoint, key_widget: KeyWidget):
            last_touch.value = touch
            last_touched_key_widget.value = key_widget
        self.notify_touch_release = notify_touch_release

        def reset_position():
            last_touch.value = None
            last_touched_key_widget.value = None
        self.reset_position = reset_position


        if group.organization.type == GroupOrganizationType.VERTICAL:
            @render(self, QVBoxLayout())
            def render_widget(widget: QWidget, _: QVBoxLayout):
                @watch_many(group.organization.width.change, dpi.change)
                def set_key_width():
                    widget.setFixedWidth(dpi.cm(group.organization.width.value))
                bounding_rect_change_signals.append(group.organization.width.change)

                for key in group.elements:
                    assert key.height is not None

                    @child(widget, KeyWidget(Stroke.from_steno(key.steno), key.label, touched_key_widgets=touched_key_widgets, current_stroke=current_stroke, dpi=dpi))
                    def render_widget(key_widget: KeyWidget, _: None):
                        self.__key_widgets.append(key_widget)
                        current_key = key

                        @watch_many(current_key.height.change, dpi.change)
                        def set_height():
                            key_widget.setFixedHeight(dpi.cm(current_key.height.value))
                        bounding_rect_change_signals.append(current_key.height.change)

                        return ()
                return ()

        elif group.organization.type == GroupOrganizationType.HORIZONTAL:
            @render(self, QHBoxLayout())
            def render_widget(widget: QWidget, _: QHBoxLayout):
                @watch_many(group.organization.height.change, dpi.change)
                def set_key_height():
                    widget.setFixedHeight(dpi.cm(group.organization.height.value))
                bounding_rect_change_signals.append(group.organization.height.change)

                for key in group.elements:
                    assert key.width is not None

                    @child(widget, KeyWidget(Stroke.from_steno(key.steno), key.label, touched_key_widgets=touched_key_widgets, current_stroke=current_stroke, dpi=dpi))
                    def render_widget(key_widget: KeyWidget, _: None):
                        self.__key_widgets.append(key_widget)
                        current_key = key

                        @watch_many(current_key.width.change, dpi.change)
                        def set_width():
                            key_widget.setFixedWidth(dpi.cm(current_key.width.value))
                        bounding_rect_change_signals.append(current_key.width.change)

                        return ()
                return ()
                
        elif group.organization.type == GroupOrganizationType.GRID:
            @render(self, QGridLayout())
            def render_widget(widget: QWidget, layout: QGridLayout):
                for i, height in enumerate(not_none(group.organization.row_heights)):
                    @watch_many(height.change, dpi.change)
                    def set_row_height():
                        layout.setRowMinimumHeight(i, dpi.cm(height.value))
                    bounding_rect_change_signals.append(height.change)

                for i, width in enumerate(not_none(group.organization.col_widths)):
                    @watch_many(width.change, dpi.change)
                    def set_col_width():
                        layout.setColumnMinimumWidth(i, dpi.cm(width.value))
                    bounding_rect_change_signals.append(width.change)


                for key in group.elements:
                    @child(widget, KeyWidget(Stroke.from_steno(key.steno), key.label, touched_key_widgets=touched_key_widgets, current_stroke=current_stroke, dpi=dpi))
                    def render_widget(key_widget: KeyWidget, _: None):
                        self.__key_widgets.append(key_widget)
                        return key.grid_location
                return ()
            
                    
        self.__proxy = proxy = not_none(scene.addWidget(self))
        items.append(proxy)

        set_group_transforms(self.__proxy, group, bounding_rect_change_signals, pos=effective_pos, dpi=dpi)
                    
        self.setStyleSheet(KEY_STYLESHEET)
    
    @property
    def proxy(self):
        return self.__proxy
    
    @property
    def key_widgets(self):
        return self.__key_widgets