import unittest

from calculations.columns.out_time import calculate_out_time
from calculations.test_data.utils import read_test_data


class TestCalculateOutTime(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

        self.start_frame = self.annotation["0"]["frames"][0]

    def test_calculate_out_time_empty_last_lap(self):
        """It returns formatted out time for the end zone passed"""
        result = calculate_out_time(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            end_zone=50,
            start_frame=self.start_frame,
            pool_length=50,
        )

        self.assertEqual(result, "")

    def test_calculate_out_time_for_middle_segment(self):
        """It returns empty string if the passed zone is not the end zone"""
        result = calculate_out_time(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            end_zone=47,
            start_frame=self.start_frame,
            pool_length=50,
        )

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
