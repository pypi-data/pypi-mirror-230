import unittest

from calculations.utils.common import get_lane_information


class TestGetLaneInformation(unittest.TestCase):
    def test_lane_info(self):
        lane_information = get_lane_information(
            {
                "metrics": {
                    "legData": [
                        {"metadata": {"distance": 50, "strokeType": "Freestyle"}}
                    ]
                },
            }
        )

        self.assertEqual(
            lane_information,
            {"lap_distance": 50, "stroke_type": "Freestyle"},
        )

    def test_lane_info_no_metrics(self):
        try:
            get_lane_information({})
        except Exception as error:
            self.assertEqual(str(error), "There is no metrics data available.")

    def test_lane_info_no_legdata(self):
        try:
            get_lane_information(annotations={"metrics": {}})
        except Exception as error:
            self.assertEqual(str(error), "There is no summary data available.")

    def test_lane_info_empty_legdata(self):
        try:
            get_lane_information(
                {
                    "metrics": {"legData": None},
                }
            )
        except Exception as error:
            self.assertEqual(str(error), "There is no summary data available.")
