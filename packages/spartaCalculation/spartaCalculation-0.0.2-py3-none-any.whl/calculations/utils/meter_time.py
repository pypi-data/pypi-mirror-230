from glom import glom


def calculate_meter_specific_time(segments_table):
    total_lap_times = 0
    last_100m = 0
    last_200m = 0
    last_500m = 0

    for segment in segments_table:
        segment_range = glom(segment, "Segment").split(" -- ")
        lap_time = glom(segment, "Lap Time")

        if lap_time == "":
            continue

        total_lap_times += float(lap_time)

        if int(segment_range[1]) % 100 == 0:
            lap_100m = total_lap_times - last_100m
            segment["100 m"] = lap_100m * 1000
            last_100m += lap_100m

        if int(segment_range[1]) % 200 == 0:
            lap_200m = total_lap_times - last_200m
            segment["200 m"] = lap_200m * 1000
            last_200m += lap_200m

        if int(segment_range[1]) % 500 == 0:
            lap_500m = total_lap_times - last_500m
            segment["500 m"] = lap_500m * 1000
            last_500m += lap_500m

    return segments_table
