from glom import glom

from calculations.utils.common import is_not_defined


def calculate_strokes(annotation, pool_length: int = 50, zone: int = 0) -> int:
    """
    Returns number of strokes for the lap.

    Parameters
    ---------
    annotation: <jsonb> annotation data for the race
    zone: <number> zone number of a segment

    Returns
    -------
    <number> number of strokes for the lap.
    <string> empty string if it is not the last zone in the lap
    """
    if (zone % pool_length) != 0 or zone == 0:
        return ""

    if is_not_defined(annotation):
        print(f"No segment available for {zone}")

        return ""

    actions = glom(annotation, "actions", default={})
    strokes = glom(actions, "strokes", default=[])

    return len(strokes)
