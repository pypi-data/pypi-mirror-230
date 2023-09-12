from glom import glom

from calculations.utils.distance import find_distance_frame_index
from calculations.utils.time import time_from_frame
from calculations.utils.logging import Logger

logger = Logger()


def fetch_one_stroke_from_segment(annotation, pool_length, start_zone, end_zone):
    """
    Fetch one stroke for the segment passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment

    Returns
    -------
    <number> first stroke for the given segment
    <None> If no stroke is found for the given segment
    """
    frames = glom(annotation, "frames", default=[])
    distances = glom(annotation, "distances", default=[])
    strokes = glom(annotation, "actions.strokes", default=[])

    start_zone_frame = frames[
        find_distance_frame_index(distances, pool_length, start_zone)
    ]
    end_zone_frame = frames[find_distance_frame_index(distances, pool_length, end_zone)]

    selected_stroke = None

    if end_zone % pool_length == 0:
        for stroke in strokes:
            if stroke < start_zone_frame:
                selected_stroke = stroke
            else:
                break

        return selected_stroke

    for stroke in strokes:
        selected_stroke = stroke

        if selected_stroke > end_zone_frame:
            break

    return selected_stroke


def calculate_stroke_rate(
    annotation,
    pool_length,
    start_zone,
    end_zone,
    lane_info={},
    exclude_roundoff: bool = False,
):
    """
    Calculate the stroke rate for the segments passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment
    lane_info: <dict> lane information

    Returns
    -------
    <number> calculated stroke rate for the segment passed
    <string> empty string if any of below condition passed
            - If no strokes available for the given segment.
            - If the number of strokes is less than 2 for the given segment.
    """
    frames = glom(annotation, "frames", default=[])
    distances = glom(annotation, "distances", default=[])
    strokes = glom(annotation, "actions.strokes", default=[])
    stroke_type = glom(lane_info, "stroke_type", default="")

    start_zone_frame = frames[
        find_distance_frame_index(distances, pool_length, start_zone)
    ]
    end_zone_frame = frames[find_distance_frame_index(distances, pool_length, end_zone)]

    stroke_inside_zone = []

    for stroke in strokes:
        if stroke >= start_zone_frame and stroke <= end_zone_frame:
            stroke_inside_zone.append(stroke)

    if len(stroke_inside_zone) == 0:
        logger.warn(f"There is no stroke for segment {start_zone} - {end_zone}")

        return ""

    if len(stroke_inside_zone) % 2 == 0 and stroke_type in ["Freestyle", "Backstroke"]:
        pick_stroke_from_next = fetch_one_stroke_from_segment(
            annotation, pool_length, start_zone, end_zone
        )

        if pick_stroke_from_next is not None:
            stroke_inside_zone.append(pick_stroke_from_next)

    if len(stroke_inside_zone) < 2:
        logger.warn(
            f"The stroke length is less than 2 for segment {start_zone} - {end_zone}"
        )

        return ""

    stroke_inside_zone.sort()

    stroke_rates = []

    for index, stroke in enumerate(stroke_inside_zone):
        try:
            current_stroke_time = time_from_frame(stroke)
            next_stroke_time = time_from_frame(stroke_inside_zone[index + 1])

            stroke_rate = next_stroke_time - current_stroke_time

            if stroke_rate == 0:
                stroke_rates.append(0)

            if stroke_type in ["Freestyle", "Backstroke"]:
                stroke_rates.append(30 / stroke_rate)
            else:
                stroke_rates.append(60 / stroke_rate)

        except IndexError:
            pass

    average_stroke_rate = sum(stroke_rates) / len(stroke_rates)

    if exclude_roundoff == True:
        return average_stroke_rate

    return round(average_stroke_rate, 1)
