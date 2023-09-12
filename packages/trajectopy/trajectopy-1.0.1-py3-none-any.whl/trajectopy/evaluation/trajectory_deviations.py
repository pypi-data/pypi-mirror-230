"""
Trajectopy - Trajectory Evaluation in Python

Gereon Tombrink, 2023
mail@gtombrink.de
"""
import copy
import csv
from functools import cached_property
from typing import Any, Callable, Union

import numpy as np
import pandas as pd
from pointset import PointSet
from trajectopy.settings.comparison_settings import ComparisonSettings

import trajectopy.util.datahandling as datahandling
from trajectopy.trajectory import Trajectory
from trajectopy.io.trajectory_io import read_data
from trajectopy.util.rotationset import RotationSet
from trajectopy.util.spatialsorter import Sorting, complete_lap_dist
from trajectopy.util.definitions import Unit


class RelativeTrajectoryDeviations:
    """
    This class represents a set of relative trajectory deviations

    Relative trajectory deviations describe relative pose deviations between
    two trajectories. The deviations are calculated by comparing pairs of
    positions and orientations in the test and reference trajectory.
    """

    def __init__(
        self,
        result_dict: dict,
        name: str = "",
        pair_distance_unit: Unit = Unit.METER,
    ) -> None:
        if not self.check_result_dict(result_dict):
            raise ValueError("Invalid result dict")

        self.name = name
        self.result_dict = result_dict
        self.pair_distance_unit = pair_distance_unit

    def check_result_dict(self, result_dict: dict) -> bool:
        """Checks if the result dict contains all required keys and values are of the correct type"""
        if not isinstance(result_dict, dict):
            return False

        if "num_pairs" not in result_dict:
            return False

        if "pair_distance" not in result_dict:
            return False

        if "pos_dev" not in result_dict:
            return False

        if "rot_dev" not in result_dict:
            return False

        if not isinstance(result_dict["pos_dev"], dict):
            return False

        if not isinstance(result_dict["rot_dev"], dict):
            return False

        if not isinstance(result_dict["pair_distance"], dict):
            return False

        return isinstance(result_dict["num_pairs"], int)

    def __eq__(self, other) -> bool:
        for self_value, other_value in zip(self.property_dict.values(), other.property_dict.values()):
            assert self_value == other_value

        return True

    def __len__(self) -> int:
        return self.result_dict["num_pairs"]

    @property
    def has_rot_dev(self) -> bool:
        return any(self.result_dict["rot_dev"].values())

    @property
    def step(self) -> float:
        return np.mean(np.diff(self.mean_distances)) if len(self.mean_distances) > 1 else 0.0

    @property
    def pose_distance_unit(self) -> str:
        return "m" if self.pair_distance_unit == Unit.METER else "s"

    @property
    def pos_drift_unit(self) -> str:
        return "%" if self.pair_distance_unit == Unit.METER else "m/s"

    @property
    def rot_drift_unit(self) -> str:
        return "deg/100m" if self.pair_distance_unit == Unit.METER else "deg/s"

    @property
    def drift_factor(self) -> float:
        return 100.0 if self.pair_distance_unit == Unit.METER else 1.0

    def compute_metric(self, key: str, func: Callable[[Any], float], factor: float = 1.0) -> list[float]:
        return [float(func(values) * factor) for values in self.result_dict[key].values() if values]

    @property
    def num_pairs(self) -> list[int]:
        return [len(values) for values in self.result_dict["pair_distance"].values() if values]

    @property
    def mean_distances(self) -> list[float]:
        return self.compute_metric(key="pair_distance", func=np.mean)

    @property
    def mean_pos_devs(self) -> list[float]:
        return self.compute_metric(key="pos_dev", func=np.mean, factor=self.drift_factor)

    @property
    def min_pos_devs(self) -> list[float]:
        return self.compute_metric(key="pos_dev", func=np.min, factor=self.drift_factor)

    @property
    def max_pos_devs(self) -> list[float]:
        return self.compute_metric(key="pos_dev", func=np.max, factor=self.drift_factor)

    @property
    def median_pos_devs(self) -> list[float]:
        return self.compute_metric(key="pos_dev", func=np.median, factor=self.drift_factor)

    @property
    def mean_rot_devs(self) -> list[float]:
        if not self.has_rot_dev:
            return []

        return self.compute_metric(key="rot_dev", func=np.mean, factor=self.drift_factor)

    @property
    def min_rot_devs(self) -> list[float]:
        if not self.has_rot_dev:
            return []

        return self.compute_metric(key="rot_dev", func=np.min, factor=self.drift_factor)

    @property
    def max_rot_devs(self) -> list[float]:
        if not self.has_rot_dev:
            return []

        return self.compute_metric(key="rot_dev", func=np.max, factor=self.drift_factor)

    @property
    def median_rot_devs(self) -> list[float]:
        if not self.has_rot_dev:
            return []

        return self.compute_metric(key="rot_dev", func=np.median, factor=self.drift_factor)

    def get_all(self, key: str) -> list[float]:
        ret_list: list[float] = []

        if key not in self.result_dict:
            return ret_list

        for value in self.result_dict[key].values():
            ret_list.extend(value)

        return ret_list

    @property
    def all_distances(self) -> list[float]:
        return self.get_all(key="pair_distance")

    @property
    def all_pos_devs(self) -> list[float]:
        return self.get_all(key="pos_dev")

    @property
    def all_rot_devs(self) -> list[float]:
        return self.get_all(key="rot_dev")

    @property
    def dynamic_pos_dict(self) -> dict[str, str]:
        return {
            f"Average position drift at {dist:.3f} (avg) {self.pose_distance_unit}": f"{dev:.3f} {self.pos_drift_unit}"
            for dist, dev in zip(self.mean_distances, self.mean_pos_devs)
        }

    @property
    def dynamic_rot_dict(self) -> dict[str, str]:
        if not self.has_rot_dev:
            return {}

        return {
            f"Average rotation drift at {dist:.3f} (avg) {self.pose_distance_unit}": f"{np.rad2deg(dev):.3f} {self.rot_drift_unit}"
            for dist, dev in zip(self.mean_distances, self.mean_rot_devs)
        }

    @property
    def property_dict(self) -> dict[str, str]:
        """
        Returns a dictionary containing the properties of the deviation set
        relevant for time based comparisons. This is the case when pose-pairs
        are defined by a time difference.
        """
        basic_dict = {"Name": self.name, "Type": self.__class__.__name__, "Number of pose pairs": str(len(self))}
        dynamic_pos_dict = self.dynamic_pos_dict
        static_pos_dict = {
            "Maximum Position Drift": f"{np.max(self.max_pos_devs):.3f} {self.pos_drift_unit}",
            "Minimum Position Drift": f"{np.min(self.min_pos_devs):.3f} {self.pos_drift_unit}",
            "Average Position Drift": f"{np.mean(self.mean_pos_devs):.3f} {self.pos_drift_unit}",
            "Median Position Drift": f"{np.median(self.median_pos_devs):.3f} {self.pos_drift_unit}",
        }

        pos_dict = basic_dict | dynamic_pos_dict | static_pos_dict

        if not self.has_rot_dev:
            return pos_dict

        dynamic_rot_dict = self.dynamic_rot_dict
        static_rot_dict = {
            "Maximum Rotation Drift": f"{np.rad2deg(np.max(self.max_rot_devs)):.3f} {self.rot_drift_unit}",
            "Minimum Rotation Drift": f"{np.rad2deg(np.min(self.min_rot_devs)):.3f} {self.rot_drift_unit}",
            "Average Rotation Drift": f"{np.rad2deg(np.mean(self.mean_rot_devs)):.3f} {self.rot_drift_unit}",
            "Median Rotation Drift": f"{np.rad2deg(np.median(self.median_rot_devs)):.3f} {self.rot_drift_unit}",
        }
        return pos_dict | dynamic_rot_dict | static_rot_dict

    def to_dataframe(self) -> pd.DataFrame:
        if self.has_rot_dev:
            return pd.DataFrame(
                np.c_[self.all_distances, self.all_pos_devs, self.all_rot_devs],
                columns=["pair_distance", "pos_dev", "rot_dev"],
            )
        else:
            return pd.DataFrame(
                np.c_[self.all_distances, self.all_pos_devs],
                columns=["pair_distance", "pos_dev"],
            )

    def to_file(self, filename: str) -> None:
        with open(filename, "a", encoding="utf-8", newline="") as file:
            file.write(f"#relative_dist_unit {self.pair_distance_unit.name}\n")

            writer = csv.writer(file)
            file.write("#num_pairs ")
            writer.writerow(self.num_pairs)
        self.to_dataframe().to_csv(filename, header=False, index=False, mode="a", float_format="%.12f")

    @classmethod
    def from_file(cls, filename: str):
        """Reads a set of relative trajectory deviations from a file."""
        header_data, deviation_data = read_data(filename=filename)

        pos_dev: dict[float, list[float]] = {}
        rot_dev: dict[float, list[float]] = {}
        pair_distance: dict[float, list[float]] = {}

        last_index = 0
        for index in header_data.num_pairs:
            dev_block = deviation_data[last_index : last_index + index, :]
            mean_dist = np.mean(dev_block[:, 0])

            pair_distance[mean_dist] = list(dev_block[:, 0])
            pos_dev[mean_dist] = list(dev_block[:, 1])
            rot_dev[mean_dist] = list(dev_block[:, 2]) if dev_block.shape[1] > 2 else []

            last_index += index

        result_dict = {"pair_distance": pair_distance, "pos_dev": pos_dev, "rot_dev": rot_dev, "num_pairs": last_index}

        return cls(result_dict=result_dict, name=header_data.name, pair_distance_unit=header_data.relative_dist_unit)


class AbsoluteTrajectoryDeviations(Trajectory):
    """
    This class represents a set of absolute trajectory deviations

    Absolute trajectory deviations describe absolute pose deviations between
    two trajectories. The deviations are calculated by comparing pairs of
    positions and orientations in the test and reference trajectory.
    """

    def __init__(
        self,
        pos: PointSet,
        pos_dev: np.ndarray,
        directed_pos_dev: np.ndarray,
        rot: Union[RotationSet, None] = None,
        rot_dev: Union[RotationSet, None] = None,
        tstamps: Union[np.ndarray, None] = None,
        name: str = "",
        sorting: Union[Sorting, None] = None,
        sort_index: Union[np.ndarray, None] = None,
        arc_lengths: Union[np.ndarray, None] = None,
        rotations_used: bool = False,
        comparison_settings: ComparisonSettings = ComparisonSettings(),
    ) -> None:
        super().__init__(
            pos=pos.copy(),
            rot=rot.copy() if rot is not None else None,
            tstamps=copy.deepcopy(tstamps) if tstamps is not None else None,
            name=copy.deepcopy(name),
            sorting=copy.deepcopy(sorting) if sorting is not None else None,
            sort_index=copy.deepcopy(sort_index) if sort_index is not None else None,
            arc_lengths=copy.deepcopy(arc_lengths) if arc_lengths is not None else None,
        )
        self.pos_dev = pos_dev
        self.directed_pos_dev = directed_pos_dev
        self.rot_dev = rot_dev
        self.rotations_used = rotations_used
        self.comparison_settings = comparison_settings

    def __eq__(self, other: "AbsoluteTrajectoryDeviations") -> bool:
        super().__eq__(other=other)
        for self_value, other_value in zip(self.numeric_property_dict.values(), other.numeric_property_dict.values()):
            np.testing.assert_almost_equal(self_value, other_value, decimal=5)

        return True

    def set_sorting(self, sorting: Sorting, inplace: bool = True):
        return super().set_sorting(sorting=sorting, inplace=inplace)

    @property
    def property_dict(self) -> dict[str, str]:
        return {
            "Name": self.name,
            "Type": self.__class__.__name__,
            "Number of deviations": str(len(self)),
            "Deviation directions derived using": "Rotations" if self.rotations_used else "Positions / Unkown",
            "Maximum position deviation [m]": f"{self.max_pos:.4f}",
            "Mean position deviation [m]": f"{self.mean_pos:.4f}",
            "Median position deviation [m]": f"{self.median_pos:.4f}",
            "Minimum position deviation [m]": f"{self.min_pos:.4f}",
            "RMS Position [m]": f"{self.rms_pos:.4f}",
            "STD Position [m]": f"{self.std_pos:.4f}",
            "Bias X [m]": f"{self.bias_x:.4f}",
            "Bias Y [m]": f"{self.bias_y:.4f}",
            "Bias Z [m]": f"{self.bias_z:.4f}",
            "RMS X [m]": f"{self.rms_x:.4f}",
            "RMS Y [m]": f"{self.rms_y:.4f}",
            "RMS Z [m]": f"{self.rms_z:.4f}",
            "Bias Along-Track [m]": f"{self.bias_along:.4f}",
            "Bias Horizontal Cross-Track [m]": f"{self.bias_cross_h:.4f}",
            "Bias Vertical Cross-Track [m]": f"{self.bias_cross_v:.4f}",
            "RMS Along-Track [m]": f"{self.rms_along:.4f}",
            "RMS Horizontal Cross-Track [m]": f"{self.rms_cross_h:.4f}",
            "RMS Vertical Cross-Track [m]": f"{self.rms_cross_v:.4f}",
            "Maximum rotation deviation [°]": f"{np.rad2deg(self.max_rot):.4f}" if self.rot_dev is not None else "-",
            "Mean rotation deviation [°]": f"{np.rad2deg(self.mean_rot):.4f}" if self.rot_dev is not None else "-",
            "Median rotation deviation [°]": f"{np.rad2deg(self.median_rot):.4f}" if self.rot_dev is not None else "-",
            "Minimum rotation deviation [°]": f"{np.rad2deg(self.min_rot):.4f}" if self.rot_dev is not None else "-",
            "RMS Rotation [°]": f"{np.rad2deg(self.rms_rot):.4f}" if self.rot_dev is not None else "-",
            "STD Rotation [°]": f"{np.rad2deg(self.std_rot):.4f}" if self.rot_dev is not None else "-",
            "RMS Roll [°]": f"{np.rad2deg(self.rms_roll):.4f}" if self.rot_dev is not None else "-",
            "RMS Pitch [°]": f"{np.rad2deg(self.rms_pitch):.4f}" if self.rot_dev is not None else "-",
            "RMS Yaw [°]": f"{np.rad2deg(self.rms_yaw):.4f}" if self.rot_dev is not None else "-",
            "Bias Roll [°]": f"{np.rad2deg(self.bias_roll):.4f}" if self.rot_dev is not None else "-",
            "Bias Pitch [°]": f"{np.rad2deg(self.bias_pitch):.4f}" if self.rot_dev is not None else "-",
            "Bias Yaw [°]": f"{np.rad2deg(self.bias_yaw):.4f}" if self.rot_dev is not None else "-",
        }

    @property
    def numeric_property_dict(self) -> dict[str, Union[float, np.ndarray]]:
        return {
            "Number of deviations": len(self),
            "Maximum position deviation [m]": self.max_pos,
            "Mean position deviation [m]": self.mean_pos,
            "Median position deviation [m]": self.median_pos,
            "Minimum position deviation [m]": self.min_pos,
            "RMS Position [m]": self.rms_pos,
            "STD Position [m]": self.std_pos,
            "Bias X [m]": self.bias_x,
            "Bias Y [m]": self.bias_y,
            "Bias Z [m]": self.bias_z,
            "RMS X [m]": self.rms_x,
            "RMS Y [m]": self.rms_y,
            "RMS Z [m]": self.rms_z,
            "Bias Along-Track [m]": self.bias_along,
            "Bias Horizontal Cross-Track [m]": self.bias_cross_h,
            "Bias Vertical Cross-Track [m]": self.bias_cross_v,
            "RMS Along-Track [m]": self.rms_along,
            "RMS Horizontal Cross-Track [m]": self.rms_cross_h,
            "RMS Vertical Cross-Track [m]": self.rms_cross_v,
            "Maximum rotation deviation [deg]": np.rad2deg(self.max_rot) if self.rot_dev is not None else 0.0,
            "Mean rotation deviation [deg]": np.rad2deg(self.mean_rot) if self.rot_dev is not None else 0.0,
            "Median rotation deviation [deg]": np.rad2deg(self.median_rot) if self.rot_dev is not None else 0.0,
            "Minimum rotation deviation [deg]": np.rad2deg(self.min_rot) if self.rot_dev is not None else 0.0,
            "RMS Rotation [deg]": np.rad2deg(self.rms_rot) if self.rot_dev is not None else 0.0,
            "STD Rotation [deg]": np.rad2deg(self.std_rot) if self.rot_dev is not None else 0.0,
            "RMS Roll [deg]": np.rad2deg(self.rms_roll) if self.rot_dev is not None else 0.0,
            "RMS Pitch [deg]": np.rad2deg(self.rms_pitch) if self.rot_dev is not None else 0.0,
            "RMS Yaw [deg]": np.rad2deg(self.rms_yaw) if self.rot_dev is not None else 0.0,
            "Bias Roll [deg]": np.rad2deg(self.bias_roll) if self.rot_dev is not None else 0.0,
            "Bias Pitch [deg]": np.rad2deg(self.bias_pitch) if self.rot_dev is not None else 0.0,
            "Bias Yaw [deg]": np.rad2deg(self.bias_yaw) if self.rot_dev is not None else 0.0,
        }

    def apply_index(self, index: Union[list, np.ndarray], inplace: bool = True) -> "AbsoluteTrajectoryDeviations":
        traj_self: AbsoluteTrajectoryDeviations = super().apply_index(index=index, inplace=inplace)
        traj_self.pos_dev = traj_self.pos_dev[index]
        traj_self.directed_pos_dev = traj_self.directed_pos_dev[index]
        if traj_self.rot_dev is not None:
            quat_filtered = traj_self.rot_dev.as_quat()[index, :]
            traj_self.rot_dev = RotationSet.from_quat(quat_filtered)
        return traj_self

    @property
    def pos_dev_close_to_zero(self) -> bool:
        return np.allclose(self.pos_dev, np.zeros(self.pos_dev.shape))

    @property
    def rpy_dev_close_to_zero(self) -> bool:
        return np.allclose(self.rpy_dev, np.zeros(self.rpy_dev.shape))

    @property
    def has_orientation(self) -> bool:
        """
        Returns True if orientation is available
        """
        return self.rot_dev is not None

    @property
    def x(self) -> np.ndarray:
        """Returns x deviations"""
        return self.pos_dev[:, 0]

    @property
    def y(self) -> np.ndarray:
        """Returns y deviations"""
        return self.pos_dev[:, 1]

    @property
    def z(self) -> np.ndarray:
        """Returns z deviations"""
        return self.pos_dev[:, 2]

    @property
    def bias_x(self) -> float:
        """Returns x bias"""
        return np.mean(self.x)

    @property
    def bias_y(self) -> float:
        """Returns y bias"""
        return np.mean(self.y)

    @property
    def bias_z(self) -> float:
        """Returns z bias"""
        return np.mean(self.z)

    @property
    def bias_cross_h(self) -> float:
        """Returns horizontal cross track bias"""
        return np.mean(self.cross_h)

    @property
    def bias_cross_v(self) -> float:
        """Returns vertical cross track bias"""
        return np.mean(self.cross_v)

    @property
    def bias_along(self) -> float:
        """Returns along track bias"""
        return np.mean(self.along)

    @cached_property
    def bias_rpy(self) -> np.ndarray:
        """Returns roll, pitch and yaw bias"""
        return self.rot_dev.mean().as_euler(seq="xyz") if self.rot_dev is not None else np.zeros(3)

    @property
    def bias_roll(self) -> np.ndarray:
        """Returns roll bias"""
        return self.bias_rpy[0]

    @property
    def bias_pitch(self) -> np.ndarray:
        """Returns pitch bias"""
        return self.bias_rpy[1]

    @property
    def bias_yaw(self) -> np.ndarray:
        """Returns yaw bias"""
        return self.bias_rpy[2]

    @property
    def along(self) -> np.ndarray:
        """
        Returns deviations of along track deviations
        """
        return self.directed_pos_dev[:, 0]

    @property
    def cross(self) -> np.ndarray:
        """
        Returns deviations of horizontal and vertical cross track deviations
        """
        return self.directed_pos_dev[:, 1:3]

    @property
    def cross_h(self) -> np.ndarray:
        """
        Returns deviations of horizontal cross track deviations
        """
        return self.directed_pos_dev[:, 1]

    @property
    def cross_v(self) -> np.ndarray:
        """
        Returns deviations of vertical cross track deviations
        """
        return self.directed_pos_dev[:, 2]

    @cached_property
    def rpy_dev(self) -> np.ndarray:
        """
        Returns rpy deviations
        """
        return self.rot_dev.as_euler(seq="xyz") if self.rot_dev is not None else np.zeros_like(self.pos_dev)

    @property
    def comb_pos_devs(self) -> np.ndarray:
        """
        Returns position deviations combined using the L2 norm
        """
        return np.linalg.norm(self.pos_dev, axis=1)

    @property
    def comb_rot_devs(self) -> np.ndarray:
        """
        Returns rotation deviations as single rotation angles
        """
        return self.rot_dev.rotangle if self.rot_dev is not None else np.zeros_like(self.pos_dev)

    @property
    def rms_pos(self) -> float:
        """
        Returns RMS of 3d positions
        """
        return datahandling.rms(self.comb_pos_devs)

    @property
    def mean_pos(self) -> float:
        """
        Returns mean of 3d position deviations
        """
        return np.mean(self.comb_pos_devs)

    @property
    def max_pos(self) -> float:
        """
        Returns max of 3d position deviations
        """
        return np.max(self.comb_pos_devs)

    @property
    def min_pos(self) -> float:
        """
        Returns min of 3d position deviations
        """
        return np.min(self.comb_pos_devs)

    @property
    def median_pos(self) -> float:
        """
        Returns min of 3d position deviations
        """
        return np.median(self.comb_pos_devs)

    @property
    def std_pos(self) -> float:
        """
        Returns std of 3d position deviations
        """
        return np.std(self.comb_pos_devs)

    @property
    def rms_rot(self) -> float:
        """
        Returns RMS of rotations
        """
        return datahandling.rms(self.comb_rot_devs) if self.rot_dev is not None else 0.0

    @property
    def std_rot(self) -> float:
        """
        Returns STD of rotations
        """
        return float(np.std(self.comb_rot_devs))

    @property
    def mean_rot(self) -> float:
        """
        Returns mean of rotations
        """
        return float(np.mean(self.comb_rot_devs))

    @property
    def median_rot(self) -> float:
        """
        Returns median of rotations
        """
        return float(np.median(self.comb_rot_devs))

    @property
    def min_rot(self) -> float:
        """
        Returns min of rotations
        """
        return np.min(self.comb_rot_devs)

    @property
    def max_rot(self) -> float:
        """
        Returns max of rotations
        """
        return np.max(self.comb_rot_devs)

    @property
    def rms_along(self) -> float:
        """
        Returns RMS of along track deviations
        """
        return datahandling.rms(self.along)

    @property
    def rms_cross_h(self) -> float:
        """
        Returns RMS of horizontal cross track deviations
        """
        return datahandling.rms(self.cross_h)

    @property
    def rms_cross_v(self) -> float:
        """
        Returns RMS of vertical cross track deviations
        """
        return datahandling.rms(self.cross_v)

    @property
    def rms_x(self) -> float:
        """
        Returns RMS of x deviations
        """
        return datahandling.rms(self.x)

    @property
    def rms_y(self) -> float:
        """
        Returns RMS of y deviations
        """
        return datahandling.rms(self.y)

    @property
    def rms_z(self) -> float:
        """
        Returns RMS of z deviations
        """
        return datahandling.rms(self.z)

    @property
    def rms_roll(self) -> float:
        """
        Returns RMS of roll deviations
        """
        return datahandling.rms(self.rpy_dev[:, 0])

    @property
    def rms_pitch(self) -> float:
        """
        Returns RMS of pitch deviations
        """
        return datahandling.rms(self.rpy_dev[:, 1])

    @property
    def rms_yaw(self) -> float:
        """
        Returns RMS of yaw deviations
        """
        return datahandling.rms(self.rpy_dev[:, 2])

    @classmethod
    def from_file(cls, filename: str):
        header_data, deviation_data = read_data(filename=filename)

        tstamps = deviation_data[:, 0]
        arc_lengths = deviation_data[:, 1]
        pos = PointSet(xyz=deviation_data[:, 2:5], epsg=header_data.epsg)
        pos_dev = deviation_data[:, 5:8]
        directed_pos_dev = deviation_data[:, 8:11]

        if deviation_data.shape[1] == 15:
            rot_dev = RotationSet.from_quat(deviation_data[:, 11:])
        else:
            rot_dev = None

        if header_data.sorting == Sorting.SPATIAL:
            sort_index = np.argsort(np.argsort(tstamps))
        else:
            sort_index = np.argsort(tstamps)

        return AbsoluteTrajectoryDeviations(
            name=header_data.name,
            pos=pos,
            pos_dev=pos_dev,
            directed_pos_dev=directed_pos_dev,
            rot_dev=rot_dev,
            tstamps=tstamps,
            arc_lengths=arc_lengths,
            sorting=header_data.sorting,
            sort_index=sort_index,
        )

    @classmethod
    def from_csv(cls, filename: str) -> pd.DataFrame:
        """
        Init DataCollection from csv
        """
        dataframe = pd.read_csv(filename)
        tstamps = np.array(dataframe.get("time", []))
        arc_lengths = np.array(dataframe.get("arc_lengths", []))
        pos_x = np.array(dataframe.pos_x.to_numpy())
        pos_y = np.array(dataframe.pos_y.to_numpy())
        pos_z = np.array(dataframe.pos_z.to_numpy())
        pos = PointSet(xyz=np.c_[pos_x, pos_y, pos_z], epsg=0)

        pos_dev_x = np.array(dataframe.get("pos_dev_x", []))
        pos_dev_y = np.array(dataframe.get("pos_dev_y", []))
        pos_dev_z = np.array(dataframe.get("pos_dev_z", []))
        pos_dev = np.c_[pos_dev_x, pos_dev_y, pos_dev_z]

        pos_dev_along = np.array(dataframe.get("pos_dev_along", []))
        pos_dev_cross_h = np.array(dataframe.get("pos_dev_cross_h", []))
        pos_dev_cross_v = np.array(dataframe.get("pos_dev_cross_v", []))
        directed_pos_dev = np.c_[pos_dev_along, pos_dev_cross_h, pos_dev_cross_v]

        rot_dev_x = np.array(dataframe.get("rot_dev_x", []))

        if len(rot_dev_x) > 0:
            rot_dev_y = np.array(dataframe.get("rot_dev_y", []))
            rot_dev_z = np.array(dataframe.get("rot_dev_z", []))
            rot_dev_w = np.array(dataframe.get("rot_dev_w", []))
            quat_dev = np.c_[rot_dev_x, rot_dev_y, rot_dev_z, rot_dev_w]
            rot_dev = RotationSet.from_quat(quat_dev)
        else:
            rot_dev = None

        return cls(
            tstamps=tstamps,
            arc_lengths=arc_lengths,
            pos=pos,
            pos_dev=pos_dev,
            directed_pos_dev=directed_pos_dev,
            rot_dev=rot_dev,
        )

    def to_dataframe(self) -> pd.DataFrame:
        """
        Exports results as pandas dataframe
        """
        if self.rot_dev:
            return pd.DataFrame(
                np.c_[
                    self.tstamps,
                    self.arc_lengths,
                    self.pos.xyz,
                    self.pos_dev,
                    self.directed_pos_dev,
                    self.rot_dev.as_quat(),
                ],
                columns=[
                    "time",
                    "arc_lengths",
                    "pos_x",
                    "pos_y",
                    "pos_z",
                    "pos_dev_x",
                    "pos_dev_y",
                    "pos_dev_z",
                    "pos_dev_along",
                    "pos_dev_cross_h",
                    "pos_dev_cross_v",
                    "rot_dev_x",
                    "rot_dev_y",
                    "rot_dev_z",
                    "rot_dev_w",
                ],
            )
        else:
            return pd.DataFrame(
                np.c_[self.tstamps, self.arc_lengths, self.pos.xyz, self.pos_dev, self.directed_pos_dev],
                columns=[
                    "time",
                    "arc_lengths",
                    "pos_x",
                    "pos_y",
                    "pos_z",
                    "pos_dev_x",
                    "pos_dev_y",
                    "pos_dev_z",
                    "pos_dev_along",
                    "pos_dev_cross_h",
                    "pos_dev_cross_v",
                ],
            )


class DeviationCollection:
    """
    This class is used to store deviations of multiple trajectories
    e.g. for plotting
    """

    def __init__(self, deviations: list[AbsoluteTrajectoryDeviations]) -> None:
        self.lengths = [dev.arc_lengths for dev in deviations]
        self.times = [dev.tstamps for dev in deviations]
        self.xyz = [dev.pos.xyz for dev in deviations]
        self.pos_dev = [dev.pos_dev for dev in deviations]
        self.pos_bias = [[dev.bias_x, dev.bias_y, dev.bias_z] for dev in deviations]
        self.pos_rms = [[dev.rms_x, dev.rms_y, dev.rms_z] for dev in deviations]
        self.directed_pos_dev = [dev.directed_pos_dev for dev in deviations]
        self.directed_pos_bias = [[dev.bias_along, dev.bias_cross_h, dev.bias_cross_v] for dev in deviations]
        self.directed_pos_rms = [[dev.rms_along, dev.rms_cross_h, dev.rms_cross_v] for dev in deviations]
        self.rpy_dev = [dev.rpy_dev for dev in deviations if dev.rot_dev is not None]
        self.rpy_bias = [dev.bias_rpy for dev in deviations if dev.rot_dev is not None]
        self.rpy_rms = [[dev.rms_roll, dev.rms_pitch, dev.rms_yaw] for dev in deviations if dev.rot_dev is not None]
        self.complete = [complete_lap_dist(l) for l in self.xyz]
        self.names = [dev.name for dev in deviations]
        self.rpy_labels = [dev.name for dev in deviations if dev.rot_dev is not None]
        self.sortings = [dev.sorting for dev in deviations]
        self.function_of = [dev.function_of for dev in deviations]

    def __len__(self) -> int:
        return len(self.lengths)

    @property
    def all_sorted(self) -> bool:
        return all(s == Sorting.SPATIAL for s in self.sortings)
