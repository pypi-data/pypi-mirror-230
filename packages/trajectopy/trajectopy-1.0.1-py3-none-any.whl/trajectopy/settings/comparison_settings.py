"""
Trajectopy - Trajectory Evaluation in Python

Gereon Tombrink, 2023
mail@gtombrink.de
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from trajectopy.settings.core import Settings, field_extractor
from trajectopy.util.definitions import Unit
from trajectopy.util.printing import dict2table


class ComparisonMethod(Enum):
    ABSOLUTE = auto()
    RELATIVE = auto()
    UNKNOWN = auto()

    @classmethod
    def from_string(cls, string: str):
        return comparison_method_from_string(string)


@dataclass
class RelativeSettings(Settings):
    """
    A class representing the settings for relative trajectory comparison.

    Attributes:
        relative_pair_min_distance (float): The minimum distance between two poses in a relative pair.
        relative_pair_max_distance (float): The maximum distance between two poses in a relative pair.
        relative_pair_distance_step (float): The step size for the distance between two poses in a relative pair.
        relative_pair_distance_unit (Unit): The unit of measurement for the distance between two poses in a relative pair.
        use_all_pose_pairs (bool): Whether to use all possible pose pairs for relative comparison.
    """

    pair_min_distance: float = 100.0
    pair_max_distance: float = 800.0
    pair_distance_step: float = 100.0
    pair_distance_unit: Unit = Unit.METER
    use_all_pose_pairs: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair_min_distance": self.pair_min_distance,
            "pair_max_distance": self.pair_max_distance,
            "pair_distance_step": self.pair_distance_step,
            "pair_distance_unit": self.pair_distance_unit.name,
            "use_all_pose_pairs": self.use_all_pose_pairs,
        }

    @classmethod
    def from_config_dict(cls, config_dict: dict):
        return relative_settings_from_dict(config_dict=config_dict)


@dataclass
class ComparisonSettings(Settings):
    """Dataclass defining comparison configuration"""

    relative_settings: RelativeSettings = field(default_factory=RelativeSettings)

    @classmethod
    def from_config_dict(cls, config_dict: dict):
        return field_extractor(
            config_class=cls(),
            config_dict=config_dict,
            fill_missing_with={"default": 0.0},
            field_handler={
                "relative_settings": relative_settings_from_dict,
            },
        )

    @classmethod
    def from_file(cls, file: str) -> Settings:
        return super().from_file(file)

    def __str__(self) -> str:
        return dict2table(self.to_dict(), title="Comparison Settings")

    def to_dict(self) -> dict[str, Any]:
        return {"relative_settings": self.relative_settings.to_dict()}


def comparison_method_from_string(string: str) -> ComparisonMethod:
    if "absolute" in string.lower():
        return ComparisonMethod.ABSOLUTE

    return ComparisonMethod.RELATIVE if "relative" in string.lower() else ComparisonMethod.UNKNOWN


def relative_settings_from_dict(config_dict: dict):
    return field_extractor(
        config_class=RelativeSettings(),
        config_dict=config_dict,
        fill_missing_with={"default": 0.0},
        field_handler={"pair_distance_unit": Unit.from_str},
    )
