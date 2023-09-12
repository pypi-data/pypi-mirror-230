import unittest

from calculations.columns.turn_index import calculate_turn_index
from calculations.test_data.utils import read_test_data


class Test_Calculate_Turn_Index(unittest.TestCase):
    def setUp(self) -> None:
        self.annotations = read_test_data(
            "lcm/historical_data/200meter_bs_race/annotations.json"
        )
        self.ams_rows = read_test_data(
            "lcm/historical_data/200meter_bs_race/ams_rows.json"
        )
        self.calculation = read_test_data(
            "lcm/historical_data/200meter_bs_race/calculation_result.json"
        )

    def test_calculate_turn_index_for_historical_1500m(self):
        first_lap_annotation = self.annotations["annotations"]["correctedAnnotations"][
            "0"
        ]
        second_lap_annotation = self.annotations["annotations"]["correctedAnnotations"][
            "1"
        ]

        start_frame = first_lap_annotation["frames"][0]

        result = calculate_turn_index(
            annotation=first_lap_annotation,
            next_annotation=second_lap_annotation,
            end_zone=50,
            start_frame=start_frame,
            pool_length=50,
        )

        self.assertEqual(result, 1.13)

    def test_calculate_turn_index_when_not_applicable(self):
        first_lap_annotation = self.annotations["annotations"]["correctedAnnotations"][
            "0"
        ]

        start_frame = first_lap_annotation["frames"][0]

        result = calculate_turn_index(
            annotation=first_lap_annotation,
            next_annotation=None,
            end_zone=50,
            start_frame=start_frame,
            pool_length=50,
        )

        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
