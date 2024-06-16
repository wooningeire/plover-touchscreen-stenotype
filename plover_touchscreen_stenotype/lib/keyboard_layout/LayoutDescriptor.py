from dataclasses import dataclass
from enum import Enum, auto

from ..reactivity import Ref
from ..util import Point


"""The factor any change in displacement will be multiplied by. Useful for counteracting misstrokes and generally avoiding drastic movements."""
ADAPTATION_RATE = 1


KeyColumnsTuple = tuple[
    tuple[
        # [keys], label, rowSpan?
        tuple[tuple[str], "str | Ref[str]", "int | None"]
    ]
]
KeyGridTuple = tuple[
    tuple[
        tuple[str],
        "str | Ref[str]",
        "tuple[int, int] | tuple[int, int, int, int]",
    ]
]
SizeTuple = tuple[Ref[float]]

@dataclass
class Key:
    steno: str
    label: "str | Ref[str]" = ""

    width: "Ref[float] | None" = None
    height: "Ref[float] | None" = None
    x: "Ref[float] | None" = None
    y: "Ref[float] | None" = None
    grid_location: tuple[int, ...] = ()

    center_offset_x: "Ref[float] | None" = None
    center_offset_y: "Ref[float] | None" = None

class GroupAlignment(Enum):
    CENTER = (0.5, 0.5)
    
    TOP_LEFT = (0, 0)
    TOP_RIGHT = (1, 0)
    BOTTOM_LEFT = (0, 1)
    BOTTOM_RIGHT = (1, 1)

class GroupOrganizationType(Enum):
    AUTO = auto()
    HORIZONTAL = auto()
    VERTICAL = auto()
    GRID = auto()

class GroupOrganization:
    def __init__(
        self,
        type: GroupOrganizationType,
        *,
        width: "Ref[float] | None"=None,
        height: "Ref[float] | None"=None,
        row_heights: "tuple[Ref[float], ...] | None"=None,
        col_widths: "tuple[Ref[float], ...] | None"=None,
    ):
        self.type = type

        self.width = width
        self.height = height
        self.col_widths = col_widths
        self.row_heights = row_heights

    AUTO: "GroupOrganization"

    @staticmethod
    def vertical(width: Ref[float]):
        return GroupOrganization(GroupOrganizationType.VERTICAL, width=width)

    @staticmethod
    def horizontal(height: Ref[float]):
        return GroupOrganization(GroupOrganizationType.HORIZONTAL, height=height)

    @staticmethod
    def grid(*, row_heights: tuple[Ref[float], ...], col_widths: tuple[Ref[float], ...]):
        return GroupOrganization(GroupOrganizationType.GRID, row_heights=row_heights, col_widths=col_widths)

GroupOrganization.AUTO = GroupOrganization(GroupOrganizationType.AUTO)

@dataclass
class Group:
    elements: "tuple[Group | KeyGroup, ...]"

    alignment: GroupAlignment
    
    x: Ref[float]
    y: Ref[float]
    angle: "Ref[float] | None" = None

    adaptive_transform: bool = False

@dataclass
class KeyGroup:
    elements: "tuple[Key, ...]"
    
    alignment: GroupAlignment
    organization: GroupOrganization

    x: Ref[float]
    y: Ref[float]
    angle: "Ref[float] | None" = None
    transform_origin_x: "Ref[float] | None" = None
    transform_origin_y: "Ref[float] | None" = None

    adaptive_transform: bool = True

@dataclass
class LayoutDescriptor:
    elements: "tuple[Group | KeyGroup, ...]"