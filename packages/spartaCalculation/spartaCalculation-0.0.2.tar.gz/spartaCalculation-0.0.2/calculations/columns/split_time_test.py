import unittest

from calculations.columns.split_time import (
    calculate_split_time,
    calculate_zone_difference,
    calculate_zone_time,
    get_time_from_lap_times,
)
from calculations.test_data.utils import read_test_data


class TestGetTimeFromLapTimes(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

    def test_get_time_from_lap_times(self):
        """It returns lap time for the zone passed"""
        result = get_time_from_lap_times(self.laptimes, 50)

        self.assertEqual(result, 22.33)

    def test_get_time_from_lap_times_for_none(self):
        """It returns none if lap time is not present for zone"""
        result = get_time_from_lap_times(self.laptimes, 45)

        self.assertEqual(result, None)


class TestCalculateZoneTime(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

        self.start_frame = self.annotation["0"]["frames"][0]

    def test_calculate_zone_time_pick_from_laptimes(self):
        """It returns zone time if the lap time passed for the zone passed"""
        result = calculate_zone_time(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            zone=50,
            start_frame=self.start_frame,
            pool_length=50,
        )

        self.assertEqual(result, 22.33)

    def test_calculate_zone_time_not_in_laptimes(self):
        """It returns calculated zone time if the lap time is not passed for the zone passed"""
        result = calculate_zone_time(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            zone=45,
            start_frame=self.start_frame,
            pool_length=50,
        )

        self.assertEqual(result, 19.78)

    def test_calculate_zone_time_exclude_exceed_distance(self):
        """It returns calculated zone time if the lap time is not passed for the zone passed"""
        result = calculate_zone_time(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            zone=145,
            start_frame=self.start_frame,
            pool_length=50,
        )

        self.assertEqual(result, 19.78)


class TestCalculateZoneDifference(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

        self.start_frame = self.annotation["0"]["frames"][0]

    def test_calculate_zone_difference(self):
        """It returns zone difference for the zone passed"""
        result = calculate_zone_difference(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            start_zone=45,
            end_zone=50,
            start_frame=self.start_frame,
            pool_length=50,
        )

        self.assertEqual(result.total_seconds(), 9.09)

    def test_calculate_zone_difference(self):
        """It returns formatted zone difference for the zone passed"""
        result = calculate_zone_difference(
            annotation=self.annotation["0"],
            lap_times=self.laptimes,
            start_zone=45,
            end_zone=50,
            start_frame=self.start_frame,
            format="%S.%f",
            pool_length=50,
        )

        self.assertEqual(result, "02.55")


class TestCalculateSplitTime(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")
        self.laptimes = read_test_data("lcm/50meter_race/lap_times.json")

        self.start_frame = self.annotation["0"]["frames"][0]

    def test_calculate_split_times(self):
        """It returns time for the zones passed"""
        result = calculate_split_time(
            annotation=self.annotation["0"],
            pool_length=50,
            lap_times=self.laptimes,
            start_zone=15,
            end_zone=25,
            start_frame=self.start_frame,
        )

        self.assertEqual(result.total_seconds(), 4.52)

    def test_calculate_split_times_format(self):
        """It returns time as a string when format is passed"""
        result = calculate_split_time(
            annotation=self.annotation["0"],
            pool_length=50,
            lap_times=self.laptimes,
            start_zone=15,
            end_zone=25,
            start_frame=self.start_frame,
            format="%S.%f",
        )

        self.assertEqual(result, "04.52")


if __name__ == "__main__":
    unittest.main()
