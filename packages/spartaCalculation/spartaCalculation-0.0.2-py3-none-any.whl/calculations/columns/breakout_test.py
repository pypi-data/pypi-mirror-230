import unittest

from parameterized import parameterized

from calculations.columns.breakout import (
    calculate_breakout,
    calculate_breakout_distance,
)
from calculations.test_data.utils import read_test_data


class TestBreakout(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_breakout(self):
        """It returns breakout value for the first zone in segment"""
        result = calculate_breakout(annotation=self.annotation["0"], zone=0)

        self.assertEqual(result, 9.8)

    def test_calculate_breakout_for_middle_segment(self):
        """It returns empty string for the middle zone in segment"""
        result = calculate_breakout(annotation=self.annotation["0"], zone=25)

        self.assertEqual(result, "")

    @parameterized.expand([(None, 25), ("", 25)])
    def test_calculate_breakout_for_none(self, annotation, zone):
        """It returns empty string for invalid annotations"""
        result = calculate_breakout(annotation=annotation, zone=zone)

        self.assertEqual(result, "")


class TestCalculateBreakoutDistance(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_breakout_distance(self):
        """It returns breakout value for annotations"""
        result = calculate_breakout_distance(self.annotation["0"])

        self.assertEqual(result, 9.779991194167359)

    def test_calculate_breakout_distance_with_no_distance(self):
        """It returns empty string when distance is none"""
        first_annotation = self.annotation["0"]
        first_annotation["distances"] = None

        result = calculate_breakout_distance(first_annotation)

        self.assertEqual(result, "")

    def test_calculate_breakout_distance_index_out_of_range(self):
        """It returns empty string when breakout is empty"""
        first_annotation = self.annotation["0"]
        first_annotation["actions"]["breakouts"] = None

        result = calculate_breakout_distance(first_annotation)

        self.assertEqual(result, "")


class TestCalculateBreakoutDistanceFor4x100(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/4x100meter_race/annotations.json")

    def test_calculate_breakout_distance(self):
        """It returns breakout value for annotations"""
        result = calculate_breakout_distance(
            self.annotation["correctedAnnotations"]["6"]
        )

        self.assertEqual(result, 11.953734225450564)


if __name__ == "__main__":
    unittest.main()
