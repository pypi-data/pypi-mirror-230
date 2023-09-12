import copy

from glom import glom

from calculations.columns.breakout import calculate_breakout
from calculations.columns.breath import calculate_breath
from calculations.columns.dps import calculate_dps
from calculations.columns.in_time import calculate_in_time
from calculations.columns.kick import calculate_kick
from calculations.columns.lap_times import calculate_lap_time
from calculations.columns.out_time import calculate_out_time
from calculations.columns.segments import calculate_segments
from calculations.columns.split_time import (
    calculate_split_time,
    calculate_zone_difference,
)
from calculations.columns.stroke_rate import calculate_stroke_rate
from calculations.columns.strokes import calculate_strokes
from calculations.columns.turn_index import calculate_turn_index
from calculations.columns.velocity import calculate_velocity
from calculations.utils.annotation import Annotation
from calculations.utils.common import get_lane_information
from calculations.utils.meter_time import calculate_meter_specific_time
from calculations.utils.stroke_type import determine_stroke_type
from calculations.utils.time import calculate_breakout_time, format_time
from calculations.utils.logging import Logger

logger = Logger()


class SegmentMetrics:
    def __init__(
        self,
        annotations,
        lap_times,
        relay_type: str = None,
        pool_length: int = 50,
        frame_rate: int = 50,
        relay: int = 0,
        is_historical_update: bool = False,
    ):
        self._annotations = annotations
        self._pool_length = pool_length
        self._frame_rate = frame_rate
        self._relay = relay
        self._relay_type = relay_type
        self._lap_times = lap_times
        self._is_historical_update = is_historical_update
        self._annotation = Annotation(
            annotation=annotations,
            relay_type=self._relay_type,
            relay=self._relay,
            historical_update=self._is_historical_update,
        )

    def get_breakout(self, type: str, lap: str = "0"):
        lap_annotation = self._annotation[lap]

        breakout_distance = calculate_breakout(
            annotation=lap_annotation,
            pool_length=self._pool_length,
            exclude_roundoff=False,
        )

        if type == "distance":
            return breakout_distance

        return calculate_breakout_time(
            lap_annotation,
            self._pool_length,
            breakout_distance,
            start_frame=self._annotation.start_frame,
        )

    def calculate_finish_time(self):
        start_frame = self._annotation.start_frame
        last_lap_annotation = self._annotation.last()
        number_of_laps = self._annotation.length

        return calculate_zone_difference(
            last_lap_annotation,
            self._pool_length,
            self._lap_times,
            self._pool_length * number_of_laps - 5,
            self._pool_length * number_of_laps,
            start_frame,
        )

    def calculate_total_turn(self):
        lane_info = get_lane_information(annotations=self._annotations)
        start_frame = self._annotation.start_frame

        annotation_key = self.fetch_annotation_key()

        total_time = None

        for index, key in enumerate(annotation_key):
            segments = calculate_segments(
                self._pool_length, lane_info["lap_distance"], int(index)
            )

            for zone in segments:
                try:
                    in_time = calculate_in_time(
                        self._annotation[key],
                        self._pool_length,
                        self._lap_times,
                        zone["end_segment"],
                        start_frame,
                    )
                    out_time = calculate_out_time(
                        self._annotation[list(annotation_key)[index + 1]],
                        self._pool_length,
                        self._lap_times,
                        zone["end_segment"],
                        start_frame,
                    )

                    if out_time != "" and out_time != "":
                        summed = out_time + in_time

                        if total_time is None:
                            total_time = summed
                        else:
                            total_time += summed

                except IndexError:
                    pass

        if total_time == None:
            return 0

        return total_time.total_seconds()

    def fetch_annotation_key(self):
        if self._relay_type == None or self._is_historical_update == True:
            return self._annotation.keys

        return [str(self._relay * 2), str(self._relay * 2 + 1)]

    def adjust_split_times(self, end_segment, split_time):
        split_time_in_millisecond = split_time.total_seconds() * 1000

        if (
            end_segment % self._pool_length == 0
            or self._relay == 0
            or self._is_historical_update == True
        ):
            return split_time_in_millisecond

        return int(self._lap_times[-1]["time"]) + split_time_in_millisecond

    def calculate(self, exclude_roundoff: bool = False):
        result = []

        lane_info = get_lane_information(annotations=self._annotations)
        start_frame = self._annotation.start_frame

        if self._lap_times == None:
            logger.warn("No lap meta data is found")

            return None

        cumulative_split_time = None

        for index, current_annotation in self._annotation:
            segments = calculate_segments(
                self._pool_length, lane_info["lap_distance"], int(index)
            )

            stroke_type_for_segment = determine_stroke_type(index, lane_info)

            updated_lane = copy.deepcopy(lane_info)
            updated_lane["stroke_type"] = stroke_type_for_segment

            for zone in segments:
                start_segment = glom(zone, "start_segment")
                end_segment = glom(zone, "end_segment")

                in_time, out_time, turn = "", "", ""

                try:
                    in_time = calculate_in_time(
                        current_annotation,
                        self._pool_length,
                        self._lap_times,
                        end_segment,
                        start_frame,
                    )
                    out_time = calculate_out_time(
                        self._annotation.next_lap,
                        self._pool_length,
                        self._lap_times,
                        end_segment,
                        start_frame,
                    )

                    turn = ""
                    if out_time != "" and out_time != "":
                        turn = out_time + in_time
                except IndexError:
                    pass

                final_split_time = None

                if end_segment % self._pool_length == 0:
                    final_split_time = calculate_split_time(
                        current_annotation,
                        self._pool_length,
                        self._lap_times,
                        start_segment,
                        end_segment,
                        start_frame,
                    )
                    cumulative_split_time = final_split_time
                else:
                    split_time = calculate_split_time(
                        current_annotation,
                        self._pool_length,
                        self._lap_times,
                        start_segment,
                        end_segment,
                        start_frame,
                    )

                    if cumulative_split_time is None:
                        cumulative_split_time = split_time
                    else:
                        cumulative_split_time = cumulative_split_time + split_time

                    final_split_time = cumulative_split_time

                zone_result = {
                    "Segment": f"{start_segment} -- {end_segment}",
                    "Velocity": calculate_velocity(
                        annotation=current_annotation,
                        pool_length=self._pool_length,
                        start_zone=start_segment,
                        end_zone=end_segment,
                        exclude_roundoff=exclude_roundoff,
                    ),
                    "Stroke Rate": calculate_stroke_rate(
                        current_annotation,
                        self._pool_length,
                        start_segment,
                        end_segment,
                        updated_lane,
                        exclude_roundoff,
                    ),
                    "DPS": calculate_dps(
                        annotation=current_annotation,
                        pool_length=self._pool_length,
                        start=start_segment,
                        end=end_segment,
                        lane_info=updated_lane,
                        exclude_roundoff=exclude_roundoff,
                    ),
                    "Strokes": calculate_strokes(
                        current_annotation, self._pool_length, end_segment
                    ),
                    "Kicks": calculate_kick(
                        current_annotation, self._pool_length, start_segment
                    ),
                    "Breaths": calculate_breath(
                        current_annotation,
                        self._pool_length,
                        start_segment,
                        end_segment,
                    ),
                    "Breakout": calculate_breakout(
                        annotation=current_annotation,
                        pool_length=self._pool_length,
                        zone=start_segment,
                    ),
                    "In": format_time(in_time, "%S.%f"),
                    "Out": format_time(out_time, "%S.%f"),
                    "Turn": format_time(turn, "%S.%f"),
                    "Turn Index": calculate_turn_index(
                        annotation=current_annotation,
                        pool_length=self._pool_length,
                        next_annotation=self._annotation.next_lap,
                        end_zone=end_segment,
                        start_frame=start_frame,
                    ),
                    "Split Time": self.adjust_split_times(
                        end_segment, final_split_time
                    ),
                    "Lap Time": format_time(
                        calculate_lap_time(
                            self._lap_times, self._pool_length, end_segment
                        ),
                        "%S.%f",
                    ),
                }

                result.append(zone_result)

        return calculate_meter_specific_time(result)
