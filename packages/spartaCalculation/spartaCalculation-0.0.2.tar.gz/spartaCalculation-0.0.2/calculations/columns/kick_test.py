import unittest

from parameterized import parameterized

from calculations.columns.kick import calculate_kick
from calculations.test_data.utils import read_test_data


class TestKick(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_kick(self):
        """It returns the number of kicks for the start zone in annotation."""
        result = calculate_kick(annotation=self.annotation["0"], zone=0)

        self.assertEqual(result, 5)

    def test_calculate_kick_for_middle_segment(self):
        """It returns empty string when it is a middle zone."""
        result = calculate_kick(annotation=self.annotation["0"], zone=25)

        self.assertEqual(result, "")

    def test_calculate_kick_for_none_kicks(self):
        """It returns empty string when there is no kicks value in annotation."""
        first_annotation = self.annotation["0"]
        first_annotation["actions"]["kicks"] = None

        result = calculate_kick(annotation=first_annotation, zone=50)

        self.assertEqual(result, "")

    def test_calculate_kick_for_none_action(self):
        """It returns empty string when there is no actions in annotation."""
        first_annotation = self.annotation["0"]
        first_annotation["actions"] = None

        result = calculate_kick(annotation=first_annotation, zone=50)

        self.assertEqual(result, "")

    @parameterized.expand([(None,), ("",)])
    def test_calculate_kick_for_none_annotation(self, annotation):
        """It returns empty string when there is no annotation."""
        result = calculate_kick(annotation=annotation, zone=50)

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
