import unittest
from datetime import timedelta

from glom import glom
from parameterized import parameterized

from calculations.columns.breakout import calculate_breakout
from calculations.utils.time import (
    calculate_breakout_time,
    calculate_distance_time,
    calculate_frame_time,
    format_time,
    time_from_frame,
)
from calculations.test_data.utils import read_test_data


class TestTimeFromFrame(unittest.TestCase):
    @parameterized.expand(
        [
            (None, None),
            ("", None),
            (2312, 46.24),
            ("2312", 46.24),
        ]
    )
    def test_time_from_frame(self, frame, expected):
        """It returns the time for the frame passed"""
        result = time_from_frame(frame)

        self.assertEqual(result, expected)


class TestCalculateFrameTime(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_frame_time(self):
        """It returns the time for the frame index passed"""
        result = calculate_frame_time(self.annotation["0"], 4)

        self.assertEqual(result, 11.24)

    def test_calculate_frame_time_index_out_range(self):
        """It returns the time for the frame index passed"""
        result = calculate_frame_time(self.annotation["0"], 4554)

        self.assertEqual(result, None)


class TestCalculateDistanceTime(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_distance_time(self):
        """It returns the time for the distance passed"""
        result = calculate_distance_time(
            annotation=self.annotation["0"], pool_length=50, distance=40
        )

        self.assertEqual(result, 28.48)


class TestFormatTime(unittest.TestCase):
    def test_format_time(self):
        """it returns formatted time when timedelta passed"""
        result = format_time(timedelta(seconds=12))

        self.assertEqual(result, "00:12.00")

    def test_format_time_with_milliseconds(self):
        """it returns formatted time with seconds when timedelta passed"""
        result = format_time(timedelta(seconds=12.54))

        self.assertEqual(result, "00:12.54")

    @parameterized.expand([(None, ""), ("", "")])
    def test_format_time_with_none(self, time, expected):
        """It returns empty string when passed value is invalid"""
        result = format_time(time)

        self.assertEqual(result, expected)


class TestCalculateBreakoutTime(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_breakout_time(self):
        breakout_distance = calculate_breakout(
            annotation=self.annotation["0"], exclude_roundoff=False
        )

        breakout_time = calculate_breakout_time(
            annotation=self.annotation["0"], breakout_distance=breakout_distance
        )

        self.assertEqual(breakout_time, 14.38)


class TestCalculateBreakoutTimeWithTimesData(unittest.TestCase):
    def setUp(self):
        self.annotation = glom(
            read_test_data("lcm/200meter_IM_race/annotations.json"),
            "annotations.correctedAnnotations",
        )

    def test_calculate_breakout_time(self):
        breakout_distance = calculate_breakout(
            annotation=self.annotation["0"], exclude_roundoff=False
        )

        breakout_time = calculate_breakout_time(
            annotation=self.annotation["0"], breakout_distance=breakout_distance
        )

        self.assertEqual(breakout_time, 4.1)


if __name__ == "__main__":
    unittest.main()
