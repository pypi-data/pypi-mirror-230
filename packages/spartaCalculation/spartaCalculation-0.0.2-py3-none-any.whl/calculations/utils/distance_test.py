import unittest

from calculations.utils.distance import (
    find_distance_frame_index,
    get_frame_distance,
)
from calculations.test_data.utils import read_test_data


class TestDistanceFrameIndex(unittest.TestCase):
    def test_distance_frame_index(self):
        """It returns the index of the nearest distance"""
        result = find_distance_frame_index(distances=[11, 12, 12.9, 13.2, 14], zone=13)

        self.assertEqual(result, 2)

    def test_distance_frame_index_when_no_distance_matched(self):
        """It returns the last index when no distance near to the passed value"""
        result = find_distance_frame_index(distances=[11, 12, 12.9, 13.2, 14], zone=50)

        self.assertEqual(result, 4)

    def test_distance_frame_index_when_no_distance_matched(self):
        """It returns None when passed value is none"""
        result = find_distance_frame_index(
            distances=[11, 12, 12.9, 13.2, 14], zone=None
        )

        self.assertEqual(result, None)


class TestGetFrameDistance(unittest.TestCase):
    def setUp(self):
        self.annotation = read_test_data("lcm/50meter_race/annotations.json")

    def test_get_frame_distance(self):
        """It returns the distance of the frame passed"""
        result = get_frame_distance(self.annotation["0"], 1068)

        self.assertEqual(result, 25.329902137865002)

    def test_get_frame_distance_when_frame_not_found(self):
        """It returns None if frame passed is not found"""
        result = get_frame_distance(self.annotation["0"], 557)

        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()
