from calculations.columns.stroke_rate import fetch_one_stroke_from_segment
from calculations.utils.distance import find_distance_frame_index, get_frame_distance


def calculate_dps(
    annotation,
    pool_length: int,
    start: int,
    end: int,
    lane_info,
    exclude_roundoff: bool = False,
) -> float:
    """
    Calculate the DPS (distance per stroke) for the segment passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment
    lane_info: <dict> lane information

    Returns
    -------
    <number> calculated dps for the segment passed
    <string> empty string if the length of strokes within segment is less than 2
    """
    corrected_start, corrected_end = start, end

    stroke_type = lane_info["stroke_type"]

    if end % pool_length == 0 and end != 0:
        corrected_end = corrected_end - 2

    frames = annotation.get("frames", [])
    distances = annotation.get("distances", [])
    actions = annotation.get("actions", {})
    strokes = actions.get("strokes", [])

    start_zone_frame = frames[
        find_distance_frame_index(distances, pool_length, corrected_start)
    ]
    end_zone_frame = frames[
        find_distance_frame_index(distances, pool_length, corrected_end)
    ]

    stroke_inside_zone = []

    for stroke in strokes:
        if stroke >= start_zone_frame and stroke <= end_zone_frame:
            stroke_inside_zone.append(stroke)

    if len(stroke_inside_zone) == 0:
        print(f"There is no stroke for segment {start} - {end}")

        return ""

    if len(stroke_inside_zone) % 2 == 0 and stroke_type in ["Freestyle", "Backstroke"]:
        pick_stroke_from_next = fetch_one_stroke_from_segment(
            annotation, pool_length, start, end
        )

        if pick_stroke_from_next != None:
            stroke_inside_zone.append(pick_stroke_from_next)

    if len(stroke_inside_zone) < 2:
        print(f"The stroke length is less than 2 for segment {start} - {end}")

        return ""

    stroke_inside_zone.sort()

    stroke_distances = []

    for index, stroke in enumerate(stroke_inside_zone):
        try:
            current_stroke_distance = get_frame_distance(annotation, stroke)
            next_stroke_distance = get_frame_distance(
                annotation, stroke_inside_zone[index + 1]
            )

            distance_diff = abs(current_stroke_distance - next_stroke_distance)

            if stroke_type in ["Freestyle", "Backstroke"]:
                stroke_distances.append(distance_diff * 2)
            else:
                stroke_distances.append(distance_diff)

        except IndexError:
            pass

    # print(stroke_distances)
    dps = sum(stroke_distances) / len(stroke_distances)
    # print(dps)

    if exclude_roundoff == True:
        return dps

    return round(dps, 2)
