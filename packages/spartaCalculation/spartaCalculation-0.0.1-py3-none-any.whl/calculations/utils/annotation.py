from glom import glom


class Annotation:
    def __init__(
        self,
        annotation,
        relay_type: str = None,
        relay: int = 0,
        historical_update: bool = False,
    ):
        self._annotation = glom(annotation, "correctedAnnotations", default={})
        self._is_historical_update = historical_update
        self._relay_type = relay_type
        self._relay = relay
        self._current_iter_index = 0

    def __getitem__(self, key):
        return glom(self._annotation, key, default={})

    def __iter__(self):
        return self

    def __next__(self):
        annotation_keys = self.keys

        if self._current_iter_index >= len(annotation_keys):
            self._current_iter_index = 0
            raise StopIteration

        current_key = annotation_keys[self._current_iter_index]
        current_iter_value = glom(self._annotation, current_key, default={})
        self._current_iter_index += 1

        return self._current_iter_index - 1, current_iter_value

    @property
    def previous_lap(self):
        annotation_keys = self.keys
        next_key_index = self._current_iter_index - 2

        if next_key_index < 0:
            return None

        return glom(self._annotation, annotation_keys[next_key_index], default={})

    @property
    def next_lap(self):
        annotation_keys = self.keys

        if self._current_iter_index >= len(annotation_keys):
            return None

        return glom(
            self._annotation, annotation_keys[self._current_iter_index], default={}
        )

    @property
    def value(self):
        return self._annotation

    @property
    def keys(self):
        if self._relay_type == None or self._is_historical_update == True:
            return list(self._annotation.keys())

        return [str(self._relay * 2), str(self._relay * 2 + 1)]

    @property
    def length(self) -> int:
        return len(self.keys)

    @property
    def start_frame(self):
        first_key = list(self._annotation.keys())[0]
        first_annotation = glom(self._annotation, first_key, default={})

        frames = glom(first_annotation, "frames", default=[])

        return frames[0]

    def first(self):
        first_annotation_key = self.keys[0]

        return glom(self._annotation, first_annotation_key, default={})

    def last(self):
        last_annotation_key = self.keys[-1]

        return glom(self._annotation, last_annotation_key, default={})
