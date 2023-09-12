import unittest

from calculations.columns.velocity import calculate_velocity
from calculations.test_data.utils import read_test_data


class TestCalculateVelocity(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_calculate_velocity_first_zone(self):
        """It returns velocity for the first segment passed"""
        result = calculate_velocity(
            annotation=self.annotation["0"], pool_length=50, start_zone=0, end_zone=15
        )

        self.assertEqual(result, 2.25)

    def test_calculate_velocity_last_zone(self):
        """It returns velocity for the last segment passed"""
        result = calculate_velocity(
            annotation=self.annotation["0"], pool_length=50, start_zone=45, end_zone=50
        )

        self.assertEqual(result, 1.9)

    def test_calculate_velocity_no_breath(self):
        """It returns empty string if no breakout is found within the segment passed"""
        result = calculate_velocity(
            annotation=self.annotation["0"], pool_length=50, start_zone=0, end_zone=9.5
        )

        self.assertEqual(result, "")

    def test_calculate_velocity_breath_closer_to_end(self):
        """It returns empty string if breakout is less than 2m to the end zone of the segment"""
        result = calculate_velocity(
            annotation=self.annotation["0"], pool_length=50, start_zone=0, end_zone=10.5
        )

        self.assertEqual(result, "")


class TestCalculateVelocityFor400m(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/400meter_race/annotations.json")

    def test_calculate_velocity_first_zone(self):
        """It returns velocity for the first segment passed"""
        result = calculate_velocity(
            annotation=self.annotation["0"], pool_length=50, start_zone=0, end_zone=25
        )

        self.assertEqual(result, 1.67)

    def test_calculate_velocity_2ndlap(self):
        """It returns velocity for the second lap passed"""
        result = calculate_velocity(
            annotation=self.annotation["1"], pool_length=50, start_zone=50, end_zone=75
        )

        self.assertEqual(result, 1.44)


if __name__ == "__main__":
    unittest.main()
