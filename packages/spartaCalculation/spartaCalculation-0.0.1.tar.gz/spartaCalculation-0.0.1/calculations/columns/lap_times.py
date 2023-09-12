from datetime import timedelta

from glom import glom


def calculate_lap_time(lap_times, pool_length: int, end_zone: int) -> timedelta:
    """
    Calculate the lap time for the end zone passed

    Parameters
    ----------
    lap_times: <array[object]> array of lap times entered by user
    end_zone: <number> end zone of the segment

    Returns
    -------
    <timedelta> lap time for the end zone passed
    """
    if end_zone % pool_length != 0:
        return ""

    for lap in lap_times:
        distance = glom(lap, "distance", default=None)
        splitTime = glom(lap, "splitTime", default="0")

        if distance == str(end_zone):
            lap_time = int(splitTime) / 1000

            break

    return timedelta(seconds=lap_time)
