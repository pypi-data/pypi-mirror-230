import unittest

from parameterized import parameterized

from calculations.columns.stroke_rate import (
    calculate_stroke_rate,
    fetch_one_stroke_from_segment,
)
from calculations.test_data.utils import read_test_data


class TestFetchOneStrokeFromSegment(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_fetch_one_stroke_from_segment(self):
        """It returns one stroke for the given segment"""
        result = fetch_one_stroke_from_segment(
            annotation=self.annotation["0"], pool_length=50, start_zone=25, end_zone=35
        )

        self.assertEqual(result, 1309)

    def test_fetch_one_stroke_from_segment_last_segment(self):
        """It returns one stroke for the last segment"""
        result = fetch_one_stroke_from_segment(
            annotation=self.annotation["0"], pool_length=50, start_zone=45, end_zone=50
        )

        self.assertEqual(result, 1542)


class TestCalculateStrokeRate(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    @parameterized.expand([("Freestyle"), ("Backstroke")])
    def test_calculate_stroke_rate_even_stroke(self, stroke_type):
        """It returns stroke rate for the given segment and selected stroke type"""
        result = calculate_stroke_rate(
            annotation=self.annotation["0"],
            pool_length=50,
            start_zone=15,
            end_zone=25,
            lane_info={"stroke_type": stroke_type},
        )

        self.assertEqual(result, 61.3)

    @parameterized.expand([("Freestyle"), ("Backstroke")])
    def test_calculate_stroke_rate_old_stroke(self, stroke_type):
        """It returns stroke rate for the given segment and selected stroke type"""
        result = calculate_stroke_rate(
            annotation=self.annotation["0"],
            pool_length=50,
            start_zone=25,
            end_zone=35,
            lane_info={"stroke_type": stroke_type},
        )

        self.assertEqual(result, 60.4)

    def test_calculate_stroke_rate_other_strokes(self):
        """It returns stroke rate for the given segment and other stroke type"""
        result = calculate_stroke_rate(
            annotation=self.annotation["0"],
            pool_length=50,
            start_zone=25,
            end_zone=35,
            lane_info={"stroke_type": "Breaststroke"},
        )

        self.assertEqual(result, 120.7)

    def test_calculate_stroke_rate_for_less_strokes(self):
        """It returns empty if the strokes count is less than 2"""
        result = calculate_stroke_rate(
            annotation=self.annotation["0"], pool_length=50, start_zone=34, end_zone=35
        )

        self.assertEqual(result, "")

    def test_calculate_stroke_rate_for_no_strokes(self):
        """It returns empty when there is no strokes for the given segment"""
        result = calculate_stroke_rate(
            annotation=self.annotation["0"], pool_length=50, start_zone=60, end_zone=75
        )

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
