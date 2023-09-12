import unittest

from parameterized import parameterized

from calculations.columns.strokes import calculate_strokes
from calculations.test_data.utils import read_test_data


class TestCalculateStrokes(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_strokes(self):
        """It returns number of strokes when last zone of the lap is passed."""
        result = calculate_strokes(annotation=self.annotation["0"], zone=50)

        self.assertEqual(result, 37)

    def test_calculate_strokes_empty_for_middle_zones(self):
        """It returns empty string when passed zone is not the last zone."""
        result = calculate_strokes(annotation=self.annotation["0"], zone=40)

        self.assertEqual(result, "")

    def test_calculate_strokes_empty_for_first_zones(self):
        """It returns empty string when passed zone is the first zone."""
        result = calculate_strokes(annotation=self.annotation["0"], zone=0)

        self.assertEqual(result, "")

    @parameterized.expand([(None,), ("",)])
    def test_calculate_strokes_empty_for_none_annotation(self, annotation):
        """It returns empty string when passed zone is the first zone."""
        result = calculate_strokes(annotation=annotation, zone=50)

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
