from glom import glom


def is_not_defined(data) -> bool:
    """
    Returns True if the data passed is not defined

    Parameters
    ----------
    data -> any data type

    Returns
    -------
    <bool> - status of whether data is defined
    """
    if data == None or data == "":
        return True

    return False


def get_lane_information(annotations):
    """
    Returns the information for the lane of the race

    Returns
    -------
    <dict> - information of the lane
    """
    metrics = glom(annotations, "metrics", default=None)

    if metrics is None:
        raise Exception("There is no metrics data available.")

    leg_data = glom(metrics, "legData", default=[])

    if leg_data == None or len(leg_data) == 0:
        raise Exception("There is no summary data available.")

    meta_data = glom(leg_data[0], "metadata", default={})

    return {
        "lap_distance": int(meta_data.get("distance", 0)),
        "stroke_type": meta_data.get("strokeType", ""),
    }
