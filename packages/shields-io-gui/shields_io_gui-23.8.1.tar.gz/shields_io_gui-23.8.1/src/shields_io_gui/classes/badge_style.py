from enum import Enum


class BadgeStyle(Enum):
    FLAT = "flat"
    FLAT_SQUARE = "flat-square"
    PLASTIC = "plastic"
    FOR_THE_BADGE = "for-the-badge"
    SOCIAL = "social"

    @classmethod
    def from_string(cls, style_string):
        enum_key = style_string.upper().replace('-', '_')
        return cls[enum_key]

    @classmethod
    def get_all_styles(cls):
        return [style.value for style in cls]
