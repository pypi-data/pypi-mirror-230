"""Test filtering time series in pyarrow Tables."""

import string
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pyarrow as pa
from kukur import InterpolationType

from timeseer_client import AugmentationStrategy, filter_series

START_DATE = datetime.fromisoformat("2020-01-01T00:00:00.000+00:00")


def _create_series_data(timestamps, values, quality=None) -> pa.Table:
    if quality is not None:
        df = pd.DataFrame(data={"ts": timestamps, "value": values, "quality": quality})
    else:
        df = pd.DataFrame(data={"ts": timestamps, "value": values})
    df = df.set_index("ts")
    return pa.Table.from_pandas(df)


def _create_event_frame_data(start_dates, end_dates):
    series_type = pa.struct(
        [
            ("series_source", pa.string()),
            ("series_name", pa.string()),
        ]
    )
    references_type = pa.list_(series_type)
    types = []
    references = []
    if len(start_dates) > 0:
        types.append("type")
        references.append(None)
    return pa.Table.from_arrays(
        [
            pa.array(start_dates, type=pa.timestamp("ns", tz="+00:00")),
            pa.array(end_dates, type=pa.timestamp("ns", tz="+00:00")),
            pa.array(types),
            pa.array(references, type=references_type),
        ],
        ["start_date", "end_date", "type", "reference"],
    )


def test_filter_empty_series() -> None:
    series = _create_series_data([], [])
    event_frames = _create_event_frame_data(
        [START_DATE], [START_DATE + timedelta(days=10)]
    )
    result = filter_series(series, event_frames)
    assert len(result) == 0


def test_filter_empty_event_frames() -> None:
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], np.random.normal(size=10)
    )
    event_frames = _create_event_frame_data([], [])
    result = filter_series(series, event_frames)
    assert len(result) == 10


def test_filter_all() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == 0


def test_filter_none() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=11)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == len(series)


def test_filter_one() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == 1
    assert result["ts"][0].as_py() == START_DATE


def test_filter_one_with_quality() -> None:
    values = np.random.normal(size=10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == 1
    assert result["ts"][0].as_py() == START_DATE
    assert result["quality"][0].as_py() == series["quality"][0].as_py()


def test_hold_last_value_filter_all() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == 0


def test_hold_last_value_filter_none() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=11)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series)


def test_hold_last_value_filter_some() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series)
    assert result["value"][1] == series["value"][0]
    assert result["ts"][1].as_py() == series["ts"][1].as_py()
    assert result["value"][2] == series["value"][0]
    assert result["ts"][2].as_py() == series["ts"][2].as_py()
    assert result["value"][3] == series["value"][0]
    assert result["ts"][3].as_py() == series["ts"][3].as_py()
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4].as_py() == series["ts"][4].as_py()


def test_hold_last_value_filter_some_with_quality() -> None:
    values = np.random.normal(size=10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series)
    assert result["value"][1] == series["value"][0]
    assert result["ts"][1].as_py() == series["ts"][1].as_py()
    assert result["quality"][1].as_py() == series["quality"][1].as_py()
    assert result["value"][2] == series["value"][0]
    assert result["ts"][2].as_py() == series["ts"][2].as_py()
    assert result["quality"][2].as_py() == series["quality"][2].as_py()
    assert result["value"][3] == series["value"][0]
    assert result["ts"][3].as_py() == series["ts"][3].as_py()
    assert result["quality"][3].as_py() == series["quality"][3].as_py()
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4].as_py() == series["ts"][4].as_py()
    assert result["quality"][4].as_py() == series["quality"][4].as_py()


def test_hold_last_value_filter_first() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE], [START_DATE + timedelta(hours=10)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series) - 1
    assert result["value"][0] == series["value"][1]
    assert result["ts"][0].as_py() == series["ts"][1].as_py()


def test_linear_interpolation_filter_all() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == 0


def test_linear_interpolation_filter_none() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=11)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series)


def test_linear_interpolation_filter_some() -> None:
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series)
    assert result["value"][1].as_py() == _get_interpolation(
        series["value"][0].as_py(),
        series["value"][4].as_py(),
        series["ts"][0].as_py(),
        series["ts"][4].as_py(),
        series["ts"][1].as_py(),
    )
    assert result["ts"][1].as_py() == series["ts"][1].as_py()
    assert result["value"][2].as_py() == _get_interpolation(
        series["value"][0].as_py(),
        series["value"][4].as_py(),
        series["ts"][0].as_py(),
        series["ts"][4].as_py(),
        series["ts"][2].as_py(),
    )
    assert result["ts"][2].as_py() == series["ts"][2].as_py()
    assert result["value"][3].as_py() == _get_interpolation(
        series["value"][0].as_py(),
        series["value"][4].as_py(),
        series["ts"][0].as_py(),
        series["ts"][4].as_py(),
        series["ts"][3].as_py(),
    )
    assert result["ts"][3].as_py() == series["ts"][3].as_py()
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4].as_py() == series["ts"][4].as_py()


def test_linear_interpolation_filter_some_with_quality() -> None:
    values = np.random.normal(size=10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series)
    assert result["value"][1].as_py() == _get_interpolation(
        series["value"][0].as_py(),
        series["value"][4].as_py(),
        series["ts"][0].as_py(),
        series["ts"][4].as_py(),
        series["ts"][1].as_py(),
    )
    assert result["ts"][1].as_py() == series["ts"][1].as_py()
    assert result["quality"][1].as_py() == series["quality"][1].as_py()
    assert result["value"][2].as_py() == _get_interpolation(
        series["value"][0].as_py(),
        series["value"][4].as_py(),
        series["ts"][0].as_py(),
        series["ts"][4].as_py(),
        series["ts"][2].as_py(),
    )
    assert result["ts"][2].as_py() == series["ts"][2].as_py()
    assert result["quality"][2].as_py() == series["quality"][2].as_py()
    assert result["value"][3].as_py() == _get_interpolation(
        series["value"][0].as_py(),
        series["value"][4].as_py(),
        series["ts"][0].as_py(),
        series["ts"][4].as_py(),
        series["ts"][3].as_py(),
    )
    assert result["ts"][3].as_py() == series["ts"][3].as_py()
    assert result["quality"][3].as_py() == series["quality"][3].as_py()
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4].as_py() == series["ts"][4].as_py()
    assert result["quality"][4].as_py() == series["quality"][4].as_py()


def test_linear_interpolation_filter_first():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE], [START_DATE + timedelta(hours=10)]
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )

    assert len(result) == len(series) - 1
    assert result["value"][0] == series["value"][1]
    assert result["ts"][0].as_py() == series["ts"][1].as_py()


def test_linear_interpolation_filter_last_3():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=7)], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series) - 3
    assert result["value"][6] == series["value"][6]
    assert result["ts"][6].as_py() == series["ts"][6].as_py()


def test_linear_interpolation_filter_some_string_values():
    values = np.random.choice(np.array(list(string.ascii_lowercase + " ")), size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(
        series, event_frames, AugmentationStrategy.LINEAR_INTERPOLATION
    )
    assert len(result) == len(series)
    assert result["value"][1] == series["value"][0]
    assert result["ts"][1].as_py() == series["ts"][1].as_py()
    assert result["value"][2] == series["value"][0]
    assert result["ts"][2].as_py() == series["ts"][2].as_py()
    assert result["value"][3] == series["value"][0]
    assert result["ts"][3].as_py() == series["ts"][3].as_py()
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4].as_py() == series["ts"][4].as_py()


def test_median_filter_second():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)],
        np.concatenate(([0] * 5, [1] * 5)),
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=1)],
        [START_DATE + timedelta(days=1) + timedelta(hours=10)],
    )

    result = filter_series(series, event_frames, AugmentationStrategy.MEAN)
    assert len(result) == len(series)
    assert result["value"][1].as_py() == 0.5


def test_median_filter_last_half():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)],
        np.concatenate(([0] * 5, [1] * 5)),
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=5)],
        [START_DATE + timedelta(days=5) + timedelta(days=5)],
    )

    result = filter_series(series, event_frames, AugmentationStrategy.MEAN)
    assert len(result) == len(series)
    assert result["value"][5].as_py() == 0.5
    assert result["value"][6].as_py() == 0.5


def test_median_filter_last_half_with_quality():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)],
        np.concatenate(([0] * 5, [1] * 5)),
        [0, 1] * 5,
    )
    event_frames = _create_event_frame_data(
        [START_DATE + timedelta(days=5)],
        [START_DATE + timedelta(days=5) + timedelta(days=5)],
    )

    result = filter_series(series, event_frames, AugmentationStrategy.MEAN)
    assert len(result) == len(series)
    assert result["value"][5].as_py() == 0.5
    assert result["value"][6].as_py() == 0.5
    assert result["quality"][1].as_py() == series["quality"][1].as_py()


def _get_interpolation(last_acceptable, next_value, last_time, next_time, current_time):
    numerator = current_time - last_time
    denominator = next_time - last_time
    time_interpolation = numerator / denominator
    return last_acceptable * (1 - time_interpolation) + next_value * time_interpolation
