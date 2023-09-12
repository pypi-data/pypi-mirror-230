from typing import Union

from glom import glom

from calculations.utils.distance import get_frame_distance
from calculations.utils.logging import Logger

logger = Logger()


def calculate_breakout_distance(annotation) -> Union[float, str]:
    """
    Returns the breakout for the annotation

    Parameters
    ----------
    annotation: <jsonb> annotation data for the race

    Returns
    -------
    <number> breakout for the annotation
    <string> empty string if there is no breakout in annotation
    """
    distances = glom(annotation, "distances", default=[])
    breakouts = glom(annotation, "actions.breakouts", default=[])

    try:
        breakout_distance = get_frame_distance(annotation, breakouts[0])

        if breakout_distance == None:
            return ""

        breakout = abs(breakout_distance - distances[0])

        return breakout
    except IndexError:
        logger.warn(f"No breakouts available")

        return ""

    except Exception as error:
        logger.error(error)

        return ""


def calculate_breakout(
    annotation, pool_length: int = 50, zone: int = 0, exclude_roundoff: bool = False
) -> Union[float, str]:
    """
    Valdiate annotation and returns breakout value for the zone passed

    Parameters
    ---------
    annotation: <jsonb> annotation data for the race
    zone: <number> zone number of a segment

    Returns
    -------
    <number> breakout for the zone.
    <string> empty string if it is not the first zone in the segment
    """
    if (zone % pool_length) != 0:
        return ""

    if annotation == None or annotation == "":
        logger.warn(f"No segment available for {zone}")

        return ""

    breakout = calculate_breakout_distance(annotation)

    if exclude_roundoff == True or breakout == "":
        return breakout

    return round(breakout, 1)
