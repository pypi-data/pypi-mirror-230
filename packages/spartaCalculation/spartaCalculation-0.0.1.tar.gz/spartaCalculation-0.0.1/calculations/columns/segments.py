def create_50m_zones_less_eq_100_segment(which_lap):
    """
    Generate the zone series for 50 and 100 m races for 50m pool

    Parameters
    ----------
    which_lap: <number> indicates the lap number for the zone creation

    Returns
    -------
    <array[object]> returns the zone list for the lap
    """
    zones = []
    start_zone = 50 * which_lap
    total_zones = 5
    i = 0

    while i < total_zones:
        zone = {"start_segment": start_zone}

        if start_zone % 50 == 0:
            start_zone += 15
        elif (start_zone + 5) % 50 == 0:
            start_zone += 5
        else:
            start_zone += 10

        zone["end_segment"] = start_zone

        zones.append(zone)

        i += 1

    return zones


def create_25m_zones_less_eq_100_segment(which_lap):
    """
    Generate the zone series for 50 and 100 m races for 25 m pool

    Parameters
    ----------
    which_lap: <number> indicates the lap number for the zone creation

    Returns
    -------
    <array[object]> returns the zone list for the lap

    Note: Since the segment split is not in a proper format, the required result is hardcoded.
    """
    if which_lap == 0:
        return [
            {
                "start_segment": 0,
                "end_segment": 15,
            },
            {
                "start_segment": 15,
                "end_segment": 20,
            },
            {
                "start_segment": 20,
                "end_segment": 25,
            },
        ]

    if which_lap == 1:
        return [
            {
                "start_segment": 25,
                "end_segment": 35,
            },
            {
                "start_segment": 35,
                "end_segment": 45,
            },
            {
                "start_segment": 45,
                "end_segment": 50,
            },
        ]

    if which_lap == 2:
        return [
            {
                "start_segment": 50,
                "end_segment": 60,
            },
            {
                "start_segment": 60,
                "end_segment": 70,
            },
            {
                "start_segment": 70,
                "end_segment": 75,
            },
        ]

    return [
        {
            "start_segment": 75,
            "end_segment": 85,
        },
        {
            "start_segment": 85,
            "end_segment": 95,
        },
        {
            "start_segment": 95,
            "end_segment": 100,
        },
    ]


def create_50m_zones_greater_eq_150_segment(which_lap):
    """
    Generate the zone series for 150 m and above races for 50m pool

    Parameters
    ----------
    which_lap: <number> indicates the lap number for the zone creation

    Returns
    -------
    <array[object]> returns the zone list for the lap
    """
    zones = []
    start_zone = 50 * which_lap
    total_zones = 2
    i = 0

    while i < total_zones:
        zone = {"start_segment": start_zone}

        start_zone += 25

        zone["end_segment"] = start_zone

        zones.append(zone)

        i += 1

    return zones


def create_25m_zones_greater_eq_150_segment(which_lap):
    """
    Generate the zone series for 150 m and above races for 25m pool

    Parameters
    ----------
    which_lap: <number> indicates the lap number for the zone creation

    Returns
    -------
    <array[object]> returns the zone list for the lap
    """
    zones = []
    start_zone = 25 * which_lap
    total_zones = 1
    i = 0

    while i < total_zones:
        zone = {"start_segment": start_zone}

        start_zone += 25

        zone["end_segment"] = start_zone

        zones.append(zone)

        i += 1

    return zones


def calculate_segments(pool_length, lap_meter, which_lap):
    """
    Generate the zone series for races

    Parameters
    ----------
    pool_length: <number> indicates the length of pool
    lap_meter: <number> indicates the meter of the race
    which_lap: <number> indicates the lap number for the zone creation
                (First lap is indicated as 0, second lap is indicated as 1 and so on)

    Returns
    -------
    <array[object]> returns the zone list for the lap
    """

    if lap_meter <= 100:
        if pool_length == 50:
            return create_50m_zones_less_eq_100_segment(which_lap)
        else:
            return create_25m_zones_less_eq_100_segment(which_lap)

    if pool_length == 50:
        return create_50m_zones_greater_eq_150_segment(which_lap)

    return create_25m_zones_greater_eq_150_segment(which_lap)
