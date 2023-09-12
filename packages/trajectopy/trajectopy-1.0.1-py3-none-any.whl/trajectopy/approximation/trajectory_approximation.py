"""
Trajectopy - Trajectory Evaluation in Python

Gereon Tombrink, 2023
mail@gtombrink.de
"""
import copy
from typing import Union
import numpy as np
import logging
from pointset import PointSet
from trajectopy.approximation.cubic_approximation import CubicApproximation, piecewise_cubic
from trajectopy.approximation.rot_approximation import (
    rot_average_slerp,
    rot_average_window,
)
from trajectopy.util.rotationset import RotationSet
from trajectopy.trajectory import Sorting, Trajectory, TrajectoryProcessingState
from trajectopy.util.definitions import RotApprox
from trajectopy.settings.approximation_settings import ApproximationSettings

logger = logging.getLogger("root")


class TrajectoryApproximation(Trajectory):
    """Class representing an approximation"""

    def __init__(
        self,
        pos: PointSet,
        rot: Union[None, RotationSet] = None,
        tstamps: Union[np.ndarray, None] = None,
        name: str = "",
        sorting: Union[Sorting, None] = None,
        sort_index: Union[np.ndarray, None] = None,
        arc_lengths: Union[np.ndarray, None] = None,
        settings: Union[ApproximationSettings, None] = None,
        state: Union[TrajectoryProcessingState, None] = None,
    ) -> None:
        """Create new Approximation Trajectory

        During initialization, deep copies of the input
        trajectory field are made.

        Args:
            traj (Trajectory): Trajectory that should be approximated
            config (ApproximationConfig, optional): Contains approximation settings.
                                                    Defaults to ApproximationConfig().

        Raises:
            ValueError: _description_
        """
        super().__init__(
            pos=pos.copy(),
            rot=rot.copy() if rot is not None else None,
            tstamps=copy.deepcopy(tstamps) if tstamps is not None else None,
            name=copy.deepcopy(name),
            sorting=copy.deepcopy(sorting) if sorting is not None else None,
            sort_index=copy.deepcopy(sort_index) if sort_index is not None else None,
            arc_lengths=copy.deepcopy(arc_lengths) if arc_lengths is not None else None,
            state=copy.deepcopy(state) if state is not None else TrajectoryProcessingState(),
        )
        self._has_valid_sorting = sort_index is not None
        self.config = settings if settings is not None else ApproximationSettings()
        self.state_before_approximation = copy.deepcopy(state) if state is not None else TrajectoryProcessingState()
        self.approximation_epsg = self.pos.epsg
        self.state.approximated = True
        self.cubic_approximations: Union[None, list[CubicApproximation]] = None

        self._perform_approximation(self.config)

    def _perform_approximation(self, settings: ApproximationSettings):
        """Internal approximation method

        Approximates positions and orientations

        Args:
            settings (ApproximationSettings): Settings defining approximation
                                              techniques, window sizes, etc.

        """
        self.pos.xyz, self.cubic_approximations = piecewise_cubic(
            function_of=self.function_of,
            values=self.pos.xyz,
            int_size=settings.fe_int_size,
            min_obs=settings.fe_min_obs,
            return_approx_objects=True,
        )

        self._rotation_approximation(settings)

    def _rotation_approximation(self, settings: ApproximationSettings):
        """Internal approximation method

        Approximates orientations

        Args:
            settings (ApproximationSettings): Settings defining approximation
                                              techniques, window sizes, etc.

        Raises:
            ValueError: Raised when there is no valid sorting but lap interpolation
                        method is requested.
        """
        if self.rot is None:
            return

        if settings.rot_approx_technique == RotApprox.INTERP and self.state.sorting_known:
            self.set_sorting(Sorting.SPATIAL)
            quat_approx = rot_average_slerp(
                function_of=self.function_of, quat=self.rot.as_quat(), sort_switching_index=self.sort_switching_index
            )

        elif settings.rot_approx_technique == RotApprox.WINDOW:
            quat_approx = rot_average_window(
                function_of=self.function_of,
                quat=self.rot.as_quat(),
                win_size=settings.rot_approx_win_size,
            )
        else:
            raise ValueError("Please provide a sorter object for 'INTERP' rotation approximation")

        self.rot = RotationSet.from_quat(quat_approx)

    def _interpolate_positions(self, tstamps: np.ndarray) -> np.ndarray:
        """Overwrite parent method

        Positions can take advantage of the cubic approximation objects.
        Instead of interpolating the positions linearly, the cubic approximation
        objects can be evaluated at the desired time stamps. This only works if
        the trajectory is sorted chronologically.

        Args:
            tstamps (np.ndarray): Time stamps at which the positions should be interpolated.

        Returns:
            np.ndarray: Interpolated positions
        """
        if self.cubic_approximations is None or self.state_before_approximation.aligned != self.state.aligned:
            logger.warning(
                "Falling back to normal interpolation method for position interpolation. Reasons for this are: 1) No cubic approximation objects available, 2) Trajectory was not aligned before approximation."
            )
            return super()._interpolate_positions(tstamps)

        logger.info("Using cubic approximation for position interpolation")

        try:
            xyz_interpolated = np.column_stack([approx.eval(tstamps) for approx in self.cubic_approximations])
        except ValueError as e:
            logger.warning("Falling back to normal interpolation: %s", e)
            return super()._interpolate_positions(tstamps)
        return PointSet(xyz=xyz_interpolated, epsg=self.approximation_epsg).to_epsg(self.pos.epsg).xyz
