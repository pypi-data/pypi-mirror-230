from glom import glom

from calculations.columns.split_time import calculate_zone_difference


def calculate_out_time(
    annotation, pool_length: int, lap_times, end_zone: int, start_frame: int
):
    """
    Calculate the Out time for the segment passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    lap_times: <array[object]> array of lap times entered by user
    end_zone: <number> end zone of the segment
    start_frame: <number> start of the frame

    Returns
    -------
    <timedelta> out time for the end zone passed
    """
    if end_zone % pool_length != 0:
        return ""

    last_lap_entry = lap_times[-1]

    if glom(last_lap_entry, "distance", default="0") == str(end_zone):
        return ""

    start_segment = end_zone
    end_zone = end_zone + 10

    return calculate_zone_difference(
        annotation, pool_length, lap_times, start_segment, end_zone, start_frame
    )
