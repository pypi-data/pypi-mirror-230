import unittest

from calculations.columns.segments import calculate_segments


class TestCalculateSegmentsfor50m(unittest.TestCase):
    def setUp(self):
        self.pool_length = 50

    def test_calculate_segments_first_50segment(self):
        """It returns segments with zone details for lap 1 in 50m race"""
        result = calculate_segments(self.pool_length, 50, 0)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 0,
                    "end_segment": 15,
                },
                {
                    "start_segment": 15,
                    "end_segment": 25,
                },
                {
                    "start_segment": 25,
                    "end_segment": 35,
                },
                {
                    "start_segment": 35,
                    "end_segment": 45,
                },
                {
                    "start_segment": 45,
                    "end_segment": 50,
                },
            ],
        )

    def test_calculate_segments_second_50segment(self):
        """It returns segments with zone details for lap 2 in 50m race"""

        result = calculate_segments(self.pool_length, 50, 1)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 50,
                    "end_segment": 65,
                },
                {
                    "start_segment": 65,
                    "end_segment": 75,
                },
                {
                    "start_segment": 75,
                    "end_segment": 85,
                },
                {
                    "start_segment": 85,
                    "end_segment": 95,
                },
                {
                    "start_segment": 95,
                    "end_segment": 100,
                },
            ],
        )

    def test_calculate_segments_first_150segment(self):
        """It returns segments with zone details for lap 1 in 150m race"""

        result = calculate_segments(self.pool_length, 150, 0)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 0,
                    "end_segment": 25,
                },
                {
                    "start_segment": 25,
                    "end_segment": 50,
                },
            ],
        )

    def test_calculate_segments_second_150segment(self):
        """It returns segments with zone details for lap 2 in 150m race"""

        result = calculate_segments(self.pool_length, 150, 1)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 50,
                    "end_segment": 75,
                },
                {
                    "start_segment": 75,
                    "end_segment": 100,
                },
            ],
        )


class TestCalculateSegmentsfor25m(unittest.TestCase):
    def setUp(self):
        self.pool_length = 25

    def test_calculate_segments_first_50segment(self):
        """It returns segments with zone details for lap 1 in 50m race"""
        result = calculate_segments(self.pool_length, 50, 0)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 0,
                    "end_segment": 15,
                },
                {
                    "start_segment": 15,
                    "end_segment": 20,
                },
                {
                    "start_segment": 20,
                    "end_segment": 25,
                },
            ],
        )

    def test_calculate_segments_second_50segment(self):
        """It returns segments with zone details for lap 2 in 50m race"""

        result = calculate_segments(self.pool_length, 50, 1)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 25,
                    "end_segment": 35,
                },
                {
                    "start_segment": 35,
                    "end_segment": 45,
                },
                {
                    "start_segment": 45,
                    "end_segment": 50,
                },
            ],
        )

    def test_calculate_segments_first_150segment(self):
        """It returns segments with zone details for lap 1 in 150m race"""

        result = calculate_segments(self.pool_length, 150, 0)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 0,
                    "end_segment": 25,
                }
            ],
        )

    def test_calculate_segments_second_150segment(self):
        """It returns segments with zone details for lap 2 in 150m race"""

        result = calculate_segments(self.pool_length, 150, 1)

        self.assertEqual(
            result,
            [
                {
                    "start_segment": 25,
                    "end_segment": 50,
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
