import unittest
from unittest.mock import patch

from calculations.segment_metrics import SegmentMetrics
from calculations.test_data.utils import read_test_data


class TestGetBreakout(unittest.TestCase):
    def setUp(self) -> None:
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_get_breakout_distance(self):
        segment_metrics = SegmentMetrics(
            annotations={
                "metrics": {
                    "legData": [
                        {"metadata": {"distance": 50, "strokeType": "Freestyle"}}
                    ]
                },
                "correctedAnnotations": self.annotation,
            },
            lap_times=None,
            pool_length=50,
            frame_rate=50,
        )

        result = segment_metrics.get_breakout("distance", "0")

        self.assertEqual(result, 9.8)

    def test_get_breakout_time(self):
        segment_metrics = SegmentMetrics(
            annotations={
                "metrics": {
                    "legData": [
                        {"metadata": {"distance": 50, "strokeType": "Freestyle"}}
                    ]
                },
                "correctedAnnotations": self.annotation,
            },
            lap_times=None,
            pool_length=50,
            frame_rate=50,
        )

        result = segment_metrics.get_breakout("time", "0")

        self.assertEqual(result, 3.2200000000000006)


class TestCalculateTotalTurn(unittest.TestCase):
    def setUp(self) -> None:
        self.annotation = read_test_data("lcm/100meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/100meter_race/lap_times.json")

    def test_calculate_total_turn(self):

        segment_metrics = SegmentMetrics(
            annotations={
                "metrics": {
                    "legData": [
                        {"metadata": {"distance": 50, "strokeType": "Freestyle"}}
                    ]
                },
                "correctedAnnotations": self.annotation,
            },
            pool_length=50,
            frame_rate=50,
            lap_times=self.laptimes,
        )

        result = segment_metrics.calculate_total_turn()

        self.assertEqual(result, 7.78)


class TestSegmentMetricsFor50m(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

    def test_segment_metrics_50m(self):
        calculation_result = read_test_data("lcm/50meter_race/calculation_result.json")

        segment_metrics = SegmentMetrics(
            annotations={
                "metrics": {
                    "legData": [
                        {"metadata": {"distance": 50, "strokeType": "Freestyle"}}
                    ]
                },
                "correctedAnnotations": self.annotation,
            },
            pool_length=50,
            frame_rate=50,
            lap_times=self.laptimes,
        )

        result = segment_metrics.calculate()

        self.assertEqual(result, calculation_result)


class TestSegmentMetricsFor200m(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/200_bf_meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/200_bf_meter_race/lap_times.json")

    def test_segment_metrics_200m(self):

        calculation_result = read_test_data(
            "lcm/200_bf_meter_race/calculation_result.json"
        )

        segment_metrics = SegmentMetrics(
            annotations=self.annotation,
            pool_length=50,
            frame_rate=50,
            lap_times=self.laptimes,
        )

        result = segment_metrics.calculate()

        self.assertEqual(result, calculation_result)


class TestSegmentMetricsFor400m(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/400meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/400meter_race/lap_times.json")

    def test_segment_metrics_400m(self):

        calculation_result = read_test_data("lcm/400meter_race/calculation_result.json")

        segment_metrics = SegmentMetrics(
            annotations={
                "metrics": {
                    "legData": [
                        {"metadata": {"distance": 400, "strokeType": "Freestyle"}}
                    ]
                },
                "correctedAnnotations": self.annotation,
            },
            pool_length=50,
            frame_rate=50,
            lap_times=self.laptimes,
        )

        result = segment_metrics.calculate()

        self.assertEqual(result, calculation_result)


class TestSegmentMetricsFor200mIM(unittest.TestCase):
    def setUp(self) -> None:
        self.annotation = read_test_data("lcm/200meter_IM_race/annotations.json")
        self.calculation_result = read_test_data(
            "lcm/200meter_IM_race/calculation_result.json"
        )

    def test_segment_metrics_200m_im(self):
        segment_metrics = SegmentMetrics(**self.annotation)

        result = segment_metrics.calculate()

        self.assertEqual(result, self.calculation_result)


class TestSegmentMetricsFor400mIM(unittest.TestCase):
    def setUp(self) -> None:
        self.annotation = read_test_data("lcm/400meter_IM_race/annotations.json")
        self.calculation_result = read_test_data(
            "lcm/400meter_IM_race/calculation_result.json"
        )

    def test_segment_metrics_400m_im(self):
        segment_metrics = SegmentMetrics(**self.annotation)

        result = segment_metrics.calculate()

        self.assertEqual(result, self.calculation_result)


class TestSegmentMetricsFor4x100mFS(unittest.TestCase):
    def setUp(self) -> None:
        self.annotation = read_test_data("lcm/4x100meter_fs_race/annotations.json")
        self.calculation_result = read_test_data(
            "lcm/4x100meter_fs_race/calculation_result.json"
        )

    def test_segment_metrics_4x100m_fs(self):
        segment_metrics = SegmentMetrics(**self.annotation)

        result = segment_metrics.calculate()

        self.assertEqual(result, self.calculation_result)


class TestSegmentMetricsForRelay(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/4x100meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/4x100meter_race/leg3_lap_times.json")
        self.calculation_result = read_test_data(
            "lcm/4x100meter_race/calculation_result.json"
        )

    def test_segment_metrics_4x100m(self):
        segment_metrics = SegmentMetrics(
            annotations=self.annotation,
            pool_length=50,
            frame_rate=50,
            relay=3,
            relay_type="4x100m",
            lap_times=self.laptimes,
        )

        result = segment_metrics.calculate()

        self.assertEqual(result, self.calculation_result)


if __name__ == "__main__":
    unittest.main()
