import unittest

from parameterized import parameterized

from calculations.utils.stroke_type import determine_stroke_type


class TestDetermineStrokeType(unittest.TestCase):
    @parameterized.expand([(0, "Backstroke"), (1, "Breaststroke"), (2, "Freestyle")])
    def test_determine_stroke_type_150IM(self, index, expected):
        stroke_type = determine_stroke_type(
            index, {"stroke_type": "Medley", "lap_distance": 150}
        )

        self.assertEqual(stroke_type, expected)

    @parameterized.expand(
        [(0, "Butterfly"), (1, "Backstroke"), (2, "Breaststroke"), (3, "Freestyle")]
    )
    def test_determine_stroke_type_200IM(self, index, expected):
        stroke_type = determine_stroke_type(
            index, {"stroke_type": "Medley", "lap_distance": 200}
        )

        self.assertEqual(stroke_type, expected)

    @parameterized.expand(
        [
            (0, "Butterfly"),
            (1, "Butterfly"),
            (2, "Backstroke"),
            (3, "Backstroke"),
            (4, "Breaststroke"),
            (5, "Breaststroke"),
            (6, "Freestyle"),
            (7, "Freestyle"),
        ]
    )
    def test_determine_stroke_type_400IM(self, index, expected):
        stroke_type = determine_stroke_type(
            index, {"stroke_type": "Medley", "lap_distance": 400}
        )

        self.assertEqual(stroke_type, expected)

    @parameterized.expand(
        [("Butterfly"), ("Backstroke"), ("Breaststroke"), ("Freestyle")]
    )
    def test_determine_stroke_type_for_others(self, expected):
        stroke_type = determine_stroke_type(
            0, {"stroke_type": expected, "lap_distance": 400}
        )

        self.assertEqual(stroke_type, expected)
