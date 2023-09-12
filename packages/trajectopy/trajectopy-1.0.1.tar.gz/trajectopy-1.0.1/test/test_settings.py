from pathlib import Path
import unittest

from trajectopy.settings.alignment_settings import (
    AlignmentEstimationSettings,
    AlignmentSettings,
    AlignmentPreprocessing,
    AlignmentStochastics,
)
from trajectopy.settings.approximation_settings import ApproximationSettings
from trajectopy.settings.comparison_settings import ComparisonSettings, RelativeSettings
from trajectopy.settings.matching_settings import MatchingSettings
from trajectopy.settings.core import Settings
from trajectopy.settings.plot_settings import PlotSettings
from trajectopy.settings.processing_settings import ProcessingSettings
from trajectopy.settings.sorting_settings import SortingSettings


class TestSettings(unittest.TestCase):
    _file = 0

    def setUp(self) -> None:
        super().setUp()
        Path("./test/tmp").mkdir(parents=True, exist_ok=True)

    def settings_io_test(self, Settings: Settings) -> None:
        filename = f"./test/tmp/settings{TestSettings._file}.yaml"
        created_settings = Settings()
        created_settings.to_file(filename)
        imported_settings = Settings.from_file(filename)
        self.assertTrue(imported_settings == created_settings)
        TestSettings._file += 1

    def test_alignment_settings(self) -> None:
        self.settings_io_test(AlignmentSettings)

    def test_alignment_preprocessing_settings(self) -> None:
        self.settings_io_test(AlignmentPreprocessing)

    def test_comparison_settings(self) -> None:
        self.settings_io_test(ComparisonSettings)

    def test_alignment_estimation_settings(self) -> None:
        self.settings_io_test(AlignmentEstimationSettings)

    def test_alignment_stochastics_settings(self) -> None:
        self.settings_io_test(AlignmentStochastics)

    def test_approximation_settings(self) -> None:
        self.settings_io_test(ApproximationSettings)

    def test_matching_settings(self) -> None:
        self.settings_io_test(MatchingSettings)

    def test_relative_settings(self) -> None:
        self.settings_io_test(RelativeSettings)

    def test_plot_settings(self) -> None:
        self.settings_io_test(PlotSettings)

    def test_processing_settings(self) -> None:
        self.settings_io_test(ProcessingSettings)

    def test_sorting_settings(self) -> None:
        self.settings_io_test(SortingSettings)
