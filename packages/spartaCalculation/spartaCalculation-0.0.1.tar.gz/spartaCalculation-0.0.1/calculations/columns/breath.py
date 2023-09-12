from typing import Union

from glom import glom

from calculations.utils.distance import find_distance_frame_index


def calculate_breath(
    annotation, pool_length, start_zone: int, end_zone: int
) -> Union[int, str]:
    """
    Calculate the breath count for the segments passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment
    lane_info: <dict> lane information

    Returns
    -------
    <number> calculated breath count for the segment passed
    """
    frames = glom(annotation, "frames", default=[])
    distances = glom(annotation, "distances", default=[])
    breaths = glom(annotation, "actions.breaths", default=[])

    start_zone_frame = frames[
        find_distance_frame_index(distances, pool_length, start_zone)
    ]
    end_zone_frame = frames[find_distance_frame_index(distances, pool_length, end_zone)]

    breath_inside_zone = []

    for breath in breaths:
        if breath >= start_zone_frame and breath < end_zone_frame:
            breath_inside_zone.append(breath)

    if len(breath_inside_zone) == 0:
        return ""

    return len(breath_inside_zone)
