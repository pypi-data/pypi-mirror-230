import datetime
from datetime import timedelta

from glom import glom

from calculations.utils.distance import find_distance_frame_index, get_frame_index


def time_from_frame(frame: int) -> int:
    """
    Return the time in seconds by dividing the frame by 50

    Parameter
    ---------
    frame: <number> frame number

    Returns
    -------
    <number> time for the frame passed
    """
    if frame == None or frame == "":
        return None

    return int(frame) / 50


def calculate_frame_time(annotation, frame_index: int):
    """
    Calculate the time for the frame index passed

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    frame_index: <number> frame index

    Returns
    -------
    <number> time for the frame index passed
    <None> returns None if no frame is found for the index passed
    """
    frames = annotation.get("frames", [])

    try:
        frame_for_index = frames[frame_index]

        if frame_for_index is None:
            return None

        return time_from_frame(frame_for_index)
    except IndexError:
        return None


def calculate_distance_time(annotation, pool_length, distance: float) -> int:
    """
    Calculate the time for the distance passed

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    distance: <number> distance

    Returns
    -------
    <number> time for the distance passed
    """
    distances = annotation.get("distances", [])

    distance_frame_index = find_distance_frame_index(distances, pool_length, distance)

    return calculate_frame_time(annotation, distance_frame_index)


def format_time(delta_time: timedelta, format="%M:%S.%f") -> str:
    """
    Format the time based on the required format provided

    Parameter
    ---------
    delta_time: <timedelta> time in timedelta format
    format: <string> required time format. By default, it is set to Minutes:Seconds.MilliSeconds

    Returns
    -------
    <string> returns formatted time
    """
    if delta_time is None or delta_time == "":
        return ""

    seconds = delta_time.total_seconds()
    seconds_to_time = datetime.timedelta(seconds=seconds)

    mock_date = datetime.datetime(1970, 1, 1)

    formatted = mock_date + seconds_to_time

    return formatted.strftime(format)[:-4]


def time_difference(
    start_time: timedelta, end_time: timedelta, format="%M:%S.%f"
) -> str:
    """
    Format the time based on the required format provided

    Parameter
    ---------
    delta_time: <timedelta> time in timedelta format
    format: <string> required time format. By default, it is set to Minutes:Seconds.MilliSeconds

    Returns
    -------
    <string> returns formatted time
    """
    if start_time is None or start_time == "":
        return ""

    if end_time is None or end_time == "":
        return ""

    start_seconds = start_time.total_seconds()
    end_seconds = end_time.total_seconds()

    difference = datetime.timedelta(seconds=end_seconds - start_seconds)

    mock_date = datetime.datetime(1970, 1, 1)

    formatted = mock_date + difference

    return formatted.strftime(format)[:-4]


def calculate_breakout_time(
    annotation, pool_length: int = 50, breakout_distance: int = 0, start_frame: int = 0
) -> float:
    """
    Calculate breakout time for the breakout distance passed.

    Note: It will consider the "times" data if present (occurs during historical update)

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    breakout_distance: <number> breakout distance

    Returns
    -------
    <float> time for the breakout distance passed
    """
    times = glom(annotation, "times", default=[])
    breakouts = glom(annotation, "actions.breakouts", default=[])

    if len(times) != 0:
        try:
            frame_index = get_frame_index(annotation, breakouts[0])

            if times[frame_index] != None:
                return times[frame_index]
        except IndexError:
            pass

    start_time = time_from_frame(start_frame)

    return (
        calculate_distance_time(annotation, pool_length, breakout_distance) - start_time
    )
