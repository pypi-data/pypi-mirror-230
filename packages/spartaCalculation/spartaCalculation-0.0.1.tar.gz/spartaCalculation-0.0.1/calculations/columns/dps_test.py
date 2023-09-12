import unittest

from parameterized import parameterized

from calculations.columns.dps import calculate_dps
from calculations.test_data.utils import read_test_data


class TestCalculateDps(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

        self.start_frame = self.annotation["0"]["frames"][0]

    @parameterized.expand([("Freestyle"), ("Backstroke")])
    def test_calculate_dps(self, stroke_type):
        """It returns the dps for the segment passed"""
        result = calculate_dps(
            annotation=self.annotation["0"],
            start=0,
            end=15,
            lane_info={"stroke_type": stroke_type},
            pool_length=50,
        )

        self.assertEqual(result, 2.15)

    @parameterized.expand([("Breaststroke")])
    def test_calculate_dps_other_stroke_types(self, stroke_type):
        """It returns the dps for the other stroke types"""
        result = calculate_dps(
            annotation=self.annotation["0"],
            start=0,
            end=15,
            lane_info={"stroke_type": stroke_type},
            pool_length=50,
        )

        self.assertEqual(result, 1.05)


if __name__ == "__main__":
    unittest.main()
