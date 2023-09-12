from datetime import timedelta

from calculations.utils.distance import find_distance_frame_index
from calculations.utils.time import format_time, time_from_frame


def get_time_from_lap_times(lap_times, zone: int) -> float:
    """
    Returns the lap time for the zone from laptimes data

    Parameter
    ---------
    lap_times: <array[object]> array of lap times entered by user
    zone: <number> zone number of a segment

    Returns
    -------
    <string> returns lap time for the zone
    <None> returns None when no lap time matched
    """
    interval_time = None

    for lap in lap_times:
        if lap["distance"] == str(zone):
            interval_time = int(lap["time"]) / 1000

    return interval_time


def calculate_zone_time(
    annotation, pool_length: int, lap_times, zone: int, start_frame: int
):
    """
    Returns time for the zone passed using annotations and lap times

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    lap_times: <array[object]> array of lap times entered by user
    zone: <number> zone number of a segment
    start_frame: <number> start of the frame

    Returns
    -------
    <number> time for the zone passed
    <string> empty string if no time for the zone
    """
    frames = annotation["frames"]
    distances = annotation["distances"]

    if zone % pool_length == 0 and zone != 0:
        return get_time_from_lap_times(lap_times, zone)

    frame_index = find_distance_frame_index(distances, pool_length, zone)

    if frames[frame_index] is None:
        return ""

    return time_from_frame(frames[frame_index] - start_frame)


def calculate_zone_difference(
    annotation,
    pool_length: int,
    lap_times,
    start_zone: int,
    end_zone: int,
    start_frame: int,
    format: str = "",
):
    """
    Returns lap time for the start and end zone passed based on the format passed

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    lap_times: <array[object]> array of lap times entered by user
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment
    start_frame: <number> start of the frame
    format: <string> what format the time is returned

    Returns
    -------
    <timedelta> returns time in timedelta format if no format is passed
    <string> returns time in required format
    """
    start_time = calculate_zone_time(
        annotation, pool_length, lap_times, start_zone, start_frame
    )
    end_time = calculate_zone_time(
        annotation, pool_length, lap_times, end_zone, start_frame
    )

    calculated = abs(end_time - start_time)

    if format != "":
        return format_time(timedelta(seconds=calculated), format)

    return timedelta(seconds=calculated)


def calculate_split_time(
    annotation, pool_length, lap_times, start_zone, end_zone, start_frame, format=""
):
    """
    Returns the split time for the segment passed based on the format passed

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    lap_times: <array[object]> array of lap times entered by user
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment
    start_frame: <number> start of the frame
    format: <string> what format the time is returned

    Returns
    -------
    <timedelta> returns split time in timedelta format if no format is passed
    <string> returns time in required format
    """
    if end_zone % pool_length == 0 and end_zone != 0:
        end_time = calculate_zone_time(
            annotation, pool_length, lap_times, end_zone, start_frame
        )

        return timedelta(seconds=end_time)

    return calculate_zone_difference(
        annotation, pool_length, lap_times, start_zone, end_zone, start_frame, format
    )
