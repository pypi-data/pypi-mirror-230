"""Test series filtering when providing Pandas DataFrames"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from kukur import InterpolationType

from timeseer_client import (
    AugmentationStrategy,
    UnknownAugmentationStrategyException,
    filter_series,
)

START_DATE = datetime.fromisoformat("2020-01-01T00:00:00.000+00:00")


def _create_series_data(timestamps, values, quality=None) -> pd.DataFrame:
    if quality is not None:
        return pd.DataFrame(
            data={"ts": timestamps, "value": values, "quality": quality}
        )
    return pd.DataFrame(data={"ts": timestamps, "value": values})


def _create_event_frame_data(types, start_dates, end_dates) -> pd.DataFrame:
    return pd.DataFrame(
        data={"type": types, "start_date": start_dates, "end_date": end_dates}
    )


def test_filter_empty_series():
    series = _create_series_data([], [])
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE], [START_DATE + timedelta(days=10)]
    )
    result = filter_series(series, event_frames)
    assert len(result) == 0


def test_filter_empty_event_frames():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], np.random.normal(size=10)
    )
    event_frames = _create_event_frame_data([], [], [])
    result = filter_series(series, event_frames)
    assert len(result) == 10


def test_filter_invalid():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], np.random.normal(size=10)
    )
    event_frames = _create_event_frame_data([], [], [])

    with pytest.raises(UnknownAugmentationStrategyException):
        filter_series(series, event_frames, "knn imputation")


def test_filter_all():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE], [START_DATE + timedelta(days=10)]
    )
    result = filter_series(series, event_frames)
    assert len(result) == 0


def test_filter_none():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=11)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == len(series)


def test_filter_one():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == 1
    assert result["ts"][0] == START_DATE


def test_filter_one_with_quality():
    values = np.random.normal(size=10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == 1
    assert result["ts"][0] == START_DATE
    assert result["quality"][0] == series["quality"][0]


def test_filter_datetime_index():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    ).set_index("ts")
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=11)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames)
    assert len(result) == len(series)
    assert len(result.columns) == 1
    assert result.index[0] == START_DATE


def test_hold_last_value_filter_all():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == 0


def test_hold_last_value_filter_none():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=11)], [START_DATE + timedelta(days=12)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series)


def test_hold_last_value_filter_some():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series)
    assert result["value"][1] == series["value"][0]
    assert result["ts"][1] == series["ts"][1]
    assert result["value"][2] == series["value"][0]
    assert result["ts"][2] == series["ts"][2]
    assert result["value"][3] == series["value"][0]
    assert result["ts"][3] == series["ts"][3]
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4] == series["ts"][4]


def test_hold_last_value_filter_some_with_quality():
    values = np.random.normal(size=10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=1)], [START_DATE + timedelta(days=3)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series)
    assert result["value"][1] == series["value"][0]
    assert result["ts"][1] == series["ts"][1]
    assert result["quality"][1] == series["quality"][1]
    assert result["value"][2] == series["value"][0]
    assert result["ts"][2] == series["ts"][2]
    assert result["quality"][2] == series["quality"][2]
    assert result["value"][3] == series["value"][0]
    assert result["ts"][3] == series["ts"][3]
    assert result["quality"][3] == series["quality"][3]
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4] == series["ts"][4]
    assert result["quality"][4] == series["quality"][4]


def test_hold_last_value_filter_first():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE], [START_DATE + timedelta(hours=10)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.HOLD_LAST)
    assert len(result) == len(series) - 1
    assert result["value"][0] == series["value"][1]
    assert result["ts"][0] == series["ts"][1]


def test_linear_interpolation_filter_all():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE, START_DATE + timedelta(days=10)
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == 0


def test_linear_interpolation_filter_none():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE + timedelta(days=11), START_DATE + timedelta(days=12)
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series)


def test_linear_interpolation_filter_some():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE + timedelta(days=1), START_DATE + timedelta(days=3)
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series)
    assert result["value"][1] == _get_interpolation(
        series["value"][0],
        series["value"][4],
        series["ts"][0],
        series["ts"][4],
        series["ts"][1],
    )
    assert result["ts"][1] == series["ts"][1]
    assert result["value"][2] == _get_interpolation(
        series["value"][0],
        series["value"][4],
        series["ts"][0],
        series["ts"][4],
        series["ts"][2],
    )
    assert result["ts"][2] == series["ts"][2]
    assert result["value"][3] == _get_interpolation(
        series["value"][0],
        series["value"][4],
        series["ts"][0],
        series["ts"][4],
        series["ts"][3],
    )
    assert result["ts"][3] == series["ts"][3]
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4] == series["ts"][4]


def test_linear_interpolation_filter_some_qith_quality():
    values = np.random.normal(size=10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE + timedelta(days=1), START_DATE + timedelta(days=3)
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series)
    assert result["value"][1] == _get_interpolation(
        series["value"][0],
        series["value"][4],
        series["ts"][0],
        series["ts"][4],
        series["ts"][1],
    )
    assert result["ts"][1] == series["ts"][1]
    assert result["quality"][1] == series["quality"][1]
    assert result["value"][2] == _get_interpolation(
        series["value"][0],
        series["value"][4],
        series["ts"][0],
        series["ts"][4],
        series["ts"][2],
    )
    assert result["ts"][2] == series["ts"][2]
    assert result["quality"][2] == series["quality"][2]
    assert result["value"][3] == _get_interpolation(
        series["value"][0],
        series["value"][4],
        series["ts"][0],
        series["ts"][4],
        series["ts"][3],
    )
    assert result["ts"][3] == series["ts"][3]
    assert result["quality"][3] == series["quality"][3]
    assert result["value"][4] == series["value"][4]
    assert result["ts"][4] == series["ts"][4]
    assert result["quality"][4] == series["quality"][4]


def test_linear_interpolation_filter_first():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE, START_DATE + timedelta(hours=10)
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series) - 1
    assert result["value"][0] == series["value"][1]
    assert result["ts"][0] == series["ts"][1]


def test_linear_interpolation_filter_last_3():
    values = np.random.normal(size=10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE + timedelta(days=7), START_DATE + timedelta(days=10)
    )

    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.LINEAR_INTERPOLATION,
        InterpolationType.LINEAR,
    )
    assert len(result) == len(series) - 3
    assert result["value"][6] == series["value"][6]
    assert result["ts"][6] == series["ts"][6]


def test_knn_imputation_at_beginning():
    values = np.arange(10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    context = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE, START_DATE + timedelta(hours=10)
    )
    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.KNN_IMPUTATION,
        InterpolationType.LINEAR,
        [context],
    )
    assert len(result) == len(series)
    assert result["value"][0] == 3
    assert result["ts"][6] == series["ts"][6]


def test_knn_imputation_at_beginning_with_quality():
    values = np.arange(10)
    quality = [0, 1] * 5
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    context = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values, quality
    )
    event_frames = _create_event_frame_data(
        ["random"], START_DATE, START_DATE + timedelta(hours=10)
    )
    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.KNN_IMPUTATION,
        InterpolationType.LINEAR,
        [context],
    )
    assert len(result) == len(series)
    assert result["value"][0] == 3
    assert result["ts"][6] == series["ts"][6]
    assert result["quality"][6] == series["quality"][6]


def test_knn_imputation_at_beginning_multiple_context():
    values = np.arange(10)
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)], values
    )
    context = [
        _create_series_data(
            [START_DATE + timedelta(days=i) for i in range(10)], values
        ),
        _create_series_data(
            [START_DATE + timedelta(days=i) for i in range(10)], values + 10
        ),
    ]

    event_frames = _create_event_frame_data(
        ["random"], START_DATE, START_DATE + timedelta(hours=10)
    )
    result = filter_series(
        series,
        event_frames,
        AugmentationStrategy.KNN_IMPUTATION,
        InterpolationType.LINEAR,
        context,
    )
    assert len(result) == len(series)
    assert result["value"][0] == 3
    assert result["ts"][6] == series["ts"][6]


def test_median_filter_second():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)],
        np.concatenate(([0] * 5, [1] * 5)),
    )
    event_frames = _create_event_frame_data(
        ["random"],
        [START_DATE + timedelta(days=1)],
        [START_DATE + timedelta(days=1) + timedelta(hours=10)],
    )

    result = filter_series(series, event_frames, AugmentationStrategy.MEAN)
    assert len(result) == len(series)
    assert result["value"][1] == 0.5


def test_median_filter_last_half():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)],
        np.concatenate(([0] * 5, [1] * 5)),
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=5)], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.MEAN)
    assert len(result) == len(series)
    assert result["value"][0] == 0
    assert result["value"][5] == 0.5
    assert result["value"][6] == 0.5


def test_median_filter_last_half_with_quality():
    series = _create_series_data(
        [START_DATE + timedelta(days=i) for i in range(10)],
        np.concatenate(([0] * 5, [1] * 5)),
        [0, 1] * 5,
    )
    event_frames = _create_event_frame_data(
        ["random"], [START_DATE + timedelta(days=5)], [START_DATE + timedelta(days=10)]
    )

    result = filter_series(series, event_frames, AugmentationStrategy.MEAN)
    assert len(result) == len(series)
    assert result["value"][0] == 0
    assert result["quality"][0] == series["quality"][0]
    assert result["value"][5] == 0.5
    assert result["quality"][5] == series["quality"][5]
    assert result["value"][6] == 0.5
    assert result["quality"][6] == series["quality"][6]


def _get_interpolation(last_acceptable, next_value, last_time, next_time, current_time):
    numerator = current_time - last_time
    denominator = next_time - last_time
    time_interpolation = numerator / denominator
    return last_acceptable * (1 - time_interpolation) + next_value * time_interpolation
