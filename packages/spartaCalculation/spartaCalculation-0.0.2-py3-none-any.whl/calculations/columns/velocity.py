from calculations.columns.breakout import calculate_breakout
from calculations.utils.time import calculate_distance_time
from calculations.utils.logging import Logger

logger = Logger()


def calculate_velocity(
    annotation,
    pool_length: int,
    start_zone: int,
    end_zone: int,
    exclude_roundoff: bool = False,
) -> float:
    """
    Calculate the velocity for the segments passed

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race
    start_zone: <number> start zone of a segment
    end_zone: <number> end zone of a segment

    Returns
    -------
    <number> calculated velocity for the segment passed
    <string> empty string if any of below condition passed
            - If the breakout distance is greater than the end zone.
            - If the breakout distance is less than 2m to the end zone.
    """
    breakout_distance = calculate_breakout(
        annotation=annotation, pool_length=pool_length, exclude_roundoff=True
    )

    if int(start_zone / pool_length) != 0:
        breakout_distance = (
            int(start_zone / pool_length) * pool_length
        ) + breakout_distance

    corrected_start, corrected_end = start_zone, end_zone

    if end_zone % pool_length == 0 and end_zone != 0:
        corrected_end = corrected_end - 2

    if breakout_distance > end_zone:
        logger.warn(
            f"The breakout distance {breakout_distance} is greater than the end_zone segment {end_zone}"
        )

        return ""

    if end_zone - breakout_distance < 2:
        logger.warn(
            f"The breakout distance {breakout_distance} is closer to the end_zone segment {end_zone}"
        )

        return ""

    if breakout_distance > start_zone:
        corrected_start = breakout_distance

    time_of_start_zone = calculate_distance_time(
        annotation, pool_length, corrected_start
    )
    time_of_end_zone = calculate_distance_time(annotation, pool_length, corrected_end)

    if (time_of_end_zone - time_of_start_zone) == 0:
        return ""

    if (time_of_end_zone - time_of_start_zone) == 0:
        return ""

    velocity = abs(
        (corrected_end - corrected_start) / (time_of_end_zone - time_of_start_zone)
    )

    if exclude_roundoff == True:
        return velocity

    return round(velocity, 2)
