from typing import List


def find_distance_frame_index(
    distances: List[int], pool_length: int = 50, zone: int = 0
) -> int:
    """
    Find the nearest distance for the zone passed

    Parameter
    ---------
    distances: <list[number]> list of distances
    zone: <number> zone number of a segment

    Returns
    -------
    <number> the index of the nearest distances
    <None> if the zone is not defined
    """
    if zone is None:
        return None

    if int(zone / pool_length) % 2 == 0:
        corrected_zone = zone % pool_length
    else:
        corrected_zone = pool_length - (zone % pool_length)

    nearest_distances = []

    for i in distances:
        nearest_distances.append(abs(i - corrected_zone))

    return nearest_distances.index(min(nearest_distances))


def get_frame_distance(annotation, frame: int) -> float:
    """
    Returns the distance of the frame passed using distances list

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    frame: <number> frame number

    Returns
    -------
    <number> distance of the frame passed
    <None> if distance is not found for the frame
    """
    frames = annotation.get("frames", [])
    distances = annotation.get("distances", [])

    try:
        frame_index = frames.index(frame)

        return abs(distances[frame_index])
    except ValueError:
        return None


def get_frame_index(annotation, frame: int) -> int:
    """
    Returns the index of the frame passed

    Parameter
    ---------
    annotation: <jsonb> annotation data for the race
    frame: <number> frame number

    Returns
    -------
    <number> index of the frame passed
    <None> if given frame is not found in the frames
    """
    frames = annotation.get("frames", [])

    try:
        frame_index = frames.index(frame)

        return frame_index
    except ValueError:
        return None
