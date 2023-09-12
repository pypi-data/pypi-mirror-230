import unittest

from calculations.columns.lap_times import calculate_lap_time
from calculations.test_data.utils import read_test_data


class TestCalculateLapTime(unittest.TestCase):
    def setUp(self):
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

    def test_calculate_lap_time(self):
        """It returns lap time for the end zone passed"""
        result = calculate_lap_time(
            lap_times=self.laptimes, end_zone=50, pool_length=50
        )

        self.assertEqual(result.total_seconds(), 22.33)

    def test_calculate_lap_time_none(self):
        """It returns empty string if the passed zone is not the end zone"""
        result = calculate_lap_time(
            lap_times=self.laptimes, end_zone=47, pool_length=50
        )

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
