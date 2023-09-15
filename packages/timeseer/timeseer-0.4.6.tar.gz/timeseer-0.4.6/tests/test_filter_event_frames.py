from datetime import datetime, timedelta

import pyarrow as pa

from timeseer_client import filter_event_frames


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
    types.append("type")
    references.append(None)
    return pa.Table.from_arrays(
        [
            pa.array(start_dates, type=pa.timestamp("us", tz="+00:00")),
            pa.array(end_dates, type=pa.timestamp("us", tz="+00:00")),
            pa.array(types),
            pa.array(references, type=references_type),
        ],
        ["start_date", "end_date", "type", "reference"],
    )


class TestFilterSeries:
    start_date = datetime.fromisoformat("2020-01-01T00:00:00.000+00:00")
    end_date = datetime.fromisoformat("2020-02-01T00:00:00.000+00:00")

    def test_filter_all(self):
        event_frames = _create_event_frame_data(
            [self.end_date], [self.end_date + timedelta(days=11)]
        )

        result = filter_event_frames(event_frames, self.start_date, self.end_date)
        assert len(result) == 0

    def test_filter_none(self):
        event_frames = _create_event_frame_data(
            [self.start_date + timedelta(days=11)], [self.end_date - timedelta(days=12)]
        )

        result = filter_event_frames(event_frames, self.start_date, self.end_date)
        assert len(result) == len(event_frames)
        assert result["start_date"][0].as_py() == self.start_date + timedelta(days=11)
        assert result["end_date"][0].as_py() == self.end_date - timedelta(days=12)

    def test_filter_change_start_date(self):
        event_frames = _create_event_frame_data(
            [self.start_date - timedelta(days=11)], [self.end_date - timedelta(days=12)]
        )

        result = filter_event_frames(event_frames, self.start_date, self.end_date)
        assert len(result) == len(event_frames)
        assert result["start_date"][0].as_py() == self.start_date
        assert result["end_date"][0].as_py() == self.end_date - timedelta(days=12)

    def test_filter_change_end_date(self):
        event_frames = _create_event_frame_data(
            [self.start_date + timedelta(days=11)], [self.end_date + timedelta(days=12)]
        )

        result = filter_event_frames(event_frames, self.start_date, self.end_date)
        assert len(result) == len(event_frames)
        assert result["start_date"][0].as_py() == self.start_date + timedelta(days=11)
        assert result["end_date"][0].as_py() == self.end_date
