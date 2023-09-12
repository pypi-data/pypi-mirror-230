from typing import Union

from glom import glom

from calculations.utils.common import is_not_defined
from calculations.utils.logging import Logger

logger = Logger()


def calculate_kick(annotation, pool_length: int = 50, zone: int = 0) -> Union[str, int]:
    """
    Returns the number of kicks from the annotation for the zone

    Parameters
    ---------
    annotation: <jsonb> annotation data for the race
    zone: <number> zone number of a segment

    Returns
    -------
    <number> number of kicks for the zone.
    <string> empty string if it is not the last zone in the segment
    """
    if (zone % pool_length) != 0:
        return ""

    if is_not_defined(annotation):
        logger.warn(f"No segment available for {zone}")

        return ""

    actions = glom(annotation, "actions", default={})

    if not actions:
        logger.warn(f"No actions available for {zone}")

        return ""

    kicks = glom(actions, "kicks", default=[])

    if is_not_defined(kicks):
        logger.warn(f"No kicks available for {zone}")

        return ""

    return len(kicks)
