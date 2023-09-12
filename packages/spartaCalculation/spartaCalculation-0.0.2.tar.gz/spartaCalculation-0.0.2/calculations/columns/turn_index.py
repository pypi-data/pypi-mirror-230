from calculations.utils.time import calculate_distance_time, time_from_frame


def calculate_turn_index(
    annotation, pool_length: int, next_annotation, end_zone: int, start_frame: int
):
    """
    Calculate the turn index for the segments passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment

    Returns
    -------
    <string> - empty when turn index is not applicable
    <number> - turn index for the segment
    """

    if int(end_zone % pool_length) != 0 or next_annotation == None:
        return ""

    velocity_swim_start_distance = end_zone - 15
    velocity_swim_mid_distance = end_zone - 5
    velocity_swim_end_distance = end_zone + 10

    velocity_swim_start_time = calculate_distance_time(
        annotation, pool_length, velocity_swim_start_distance
    ) - time_from_frame(start_frame)
    velocity_swim_mid_time = calculate_distance_time(
        annotation, pool_length, velocity_swim_mid_distance
    ) - time_from_frame(start_frame)
    velocity_swim_end_time = calculate_distance_time(
        next_annotation, pool_length, velocity_swim_end_distance
    ) - time_from_frame(start_frame)

    velocity_swim = abs(
        (velocity_swim_mid_distance - velocity_swim_start_distance)
        / (velocity_swim_mid_time - velocity_swim_start_time)
    )
    velocity_turn = abs(
        (velocity_swim_end_distance - velocity_swim_mid_distance)
        / (velocity_swim_end_time - velocity_swim_mid_time)
    )

    return round(velocity_turn / velocity_swim, 2)
