import unittest

from calculations.utils.annotation import Annotation


class TestAnnotation(unittest.TestCase):
    def setUp(self) -> None:
        self.annotation = Annotation(
            annotation={
                "correctedAnnotations": {
                    "first": {"value": 0},
                    "second": {"value": 1},
                    "third": {"value": 2},
                }
            }
        )

    def test_keys(self):
        self.assertEqual(self.annotation.keys, ["first", "second", "third"])

    def test_length(self):
        self.assertEqual(self.annotation.length, 3)

    def test_key_value(self):
        self.assertEqual(self.annotation["first"], {"value": 0})

    def test_value(self):
        self.assertEqual(
            self.annotation.value,
            {"first": {"value": 0}, "second": {"value": 1}, "third": {"value": 2}},
        )

    def test_first(self):
        self.assertEqual(self.annotation.first(), {"value": 0})

    def test_last(self):
        self.assertEqual(self.annotation.last(), {"value": 2})

    def test_next(self):
        index, value = self.annotation.__next__()

        self.assertEqual(index, 0)
        self.assertEqual(value, {"value": 0})

    def test_next_property(self):
        self.annotation.__next__()

        self.assertEqual(self.annotation.next_lap, {"value": 1})

    def test_previous_property(self):
        self.annotation.__next__()
        self.annotation.__next__()

        self.assertEqual(self.annotation.previous_lap, {"value": 0})

    def test_previous_property_last(self):
        self.annotation.__next__()
        self.annotation.__next__()
        self.annotation.__next__()

        self.assertEqual(self.annotation.previous_lap, {"value": 1})

    def test_previous_property_first(self):
        self.annotation.__next__()

        self.assertEqual(self.annotation.previous_lap, None)
