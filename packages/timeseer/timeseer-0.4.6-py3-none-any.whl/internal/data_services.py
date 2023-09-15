"""Python client for Timeseer Data Services."""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pyarrow as pa
from kukur import Metadata, SeriesSelector

from timeseer_client.internal import (
    EventFrame,
    JSONFlightClient,
    Statistic,
    TimeoutException,
    TimeseerClientException,
)


class DataServiceEvaluationFailedException(TimeseerClientException):
    """Thrown when a data service evaluation fails."""

    def __init__(self, name: str, view_name: str):
        super().__init__(f'evaluation for data service "{name}"/"{view_name}" failed')


class DataServiceEvaluationsFailedException(TimeseerClientException):
    """Thrown when a data service evaluation fails."""

    def __init__(self, name: str):
        super().__init__(f'evaluations for data service "{name}" failed')


@dataclass
class DataServiceSelector:
    """Points to a series set inside a Data Service."""

    name: str
    series_set_name: str

    @classmethod
    def from_data(cls, data: Dict[str, str]) -> "DataServiceSelector":
        """Create a DataServiceSelector from a JSON dictionary."""
        return cls(data["name"], data["view"])

    def to_data(self) -> Dict[str, str]:
        """Convert to a dictionary suitable for JSON conversion."""
        return {"name": self.name, "view": self.series_set_name}


class DataServices:
    """Data Services provide access to analysis results, time series data and statistics.

    Args:
        client: the Timeseer Client
    """

    __client: JSONFlightClient

    def __init__(self, client: JSONFlightClient):
        self.__client = client

    def list(self) -> List[str]:
        """Return a list containing all the Data Service names."""
        return self.__client.do_action("data_services/list", {})

    def get(self, data_service_name: str) -> List[DataServiceSelector]:
        """Return a list containing a selector for each series set in a data service."""
        return [
            DataServiceSelector.from_data(data)
            for data in self.__client.do_action(
                "data_services/get", {"dataServiceName": data_service_name}
            )
        ]

    def wait_for_all_evaluations(
        self, data_service_name: str, *, timeout_seconds: float = 60.0
    ) -> None:
        """Wait until all the evaluations of a Data Service are complete.

        Args:
            data_service_name: The name of the Data Service to wait for.
            timeout_seconds: The number of seconds to wait until the evaluation is complete. (optional, keyword only)

        Raises:
            DataServiceEvaluationsFailedException when a failure is reported.
        """
        body = {"dataServiceName": data_service_name}
        while timeout_seconds > 0:
            job_states = self.__client.do_action(
                "data_services/get_all_view_states", body
            )
            if all(
                job_state["completed"] == job_state["total"] for job_state in job_states
            ):
                if any(job_state["failed"] > 0 for job_state in job_states):
                    raise DataServiceEvaluationsFailedException(data_service_name)
                return
            time.sleep(0.2)
            timeout_seconds = timeout_seconds - 0.2

        raise TimeoutException()

    def wait_for_evaluation(
        self, data_service: DataServiceSelector, *, timeout_seconds: int = 60
    ) -> None:
        """Wait until the evaluation of a Data Service is complete.

        Args:
            data_service: The series set in a Data Service to wait for.
            timeout_seconds: The number of seconds to wait until the evaluation is complete. (optional, keyword only)

        Raises:
            DataServiceEvaluationFailedException when a failure is reported.
        """
        body = {"dataService": data_service.to_data()}
        while timeout_seconds > 0:
            job_state = self.__client.do_action("data_services/get_view_state", body)
            if job_state["completed"] == job_state["total"]:
                if job_state["failed"] > 0:
                    raise DataServiceEvaluationFailedException(
                        data_service.name, data_service.series_set_name
                    )
                return
            time.sleep(1)
            timeout_seconds = timeout_seconds - 1

        raise TimeoutException()

    def get_data(
        self,
        data_service: DataServiceSelector,
        selector: SeriesSelector,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pa.Table:
        """Get data from a given Data Service.

        Falls back to the data source when no data is present.

        Args:
            data_service: The series set in the Data Service to look for data in.
            selector: Return data for the time series selected by this selector.
            start_date: the start date of the data
                Defaults to start date of the data service.
            end_date: the end date of the data
                Defaults to end date of the data service.

        Returns::
            A pyarrow Table with three columns: 'ts', 'value' and 'quality'.
        """
        body = {
            "query": "data_services/get_data",
            "dataService": data_service.to_data(),
            "selector": selector.to_data(),
            "startDate": start_date.isoformat() if start_date is not None else None,
            "endDate": end_date.isoformat() if end_date is not None else None,
        }
        return self.__client.do_get(body)

    def get_kpi_scores(self, data_service: DataServiceSelector) -> Dict[str, int]:
        """Get the kpi scores of a Data Service.

        Args:
            data_service: The series set in the Data Service to return scores for.

        Returns::
            The score per KPI as a percentage.
        """
        body = {
            "dataService": data_service.to_data(),
        }
        return self.__client.do_action("data_services/get_kpi_scores", body)

    def convert_to_event_frame(self, table: pa.Table) -> List[EventFrame]:
        """Convert a PyArrow table to an EventFrame object."""
        return [EventFrame.from_row(data) for data in table.to_pylist()]

    def get_event_frames(  # noqa: PLR0913
        self,
        data_service: DataServiceSelector,
        selector: Optional[SeriesSelector] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        frame_type: Optional[Union[str, List[str]]] = None,
    ) -> pa.Table:
        """Get all event frames matching the given criteria.

        Args:
            data_service: The series set in the Data Service to return event frames for.
            selector: the time series to which the event frames are linked.
            start_date: the start date of the range to find overlapping event frames in.
                Defaults to start date of the data service.
            end_date: the end date of the range to find overlapping event frames in.
                Defaults to end date of the data service.
            frame_type: the type or types of event frames to search for. Finds all types when empty.

        Returns::
            A pyarrow Table with 6 columns.
            The first column ('start_date') contains the start date.
            The second column ('end_date') contains the end date.
            The third column ('type') contains the type of the returned event frame as a string.
            The fourth column ('explanation') can contain the explanation for an event frame as a string.
            The fifth column ('status') can contain the status of an event frame as a string.
            Columns 6 contains possible multiple references for the event frame.
            the seventh column contains the properties of the event frame.
            The eight column contains the uuid of the event frame.
        """
        query: Dict[str, Any] = {
            "query": "data_services/get_event_frames",
            "dataService": data_service.to_data(),
            "selector": selector.to_data() if selector is not None else None,
            "startDate": start_date.isoformat() if start_date is not None else None,
            "endDate": end_date.isoformat() if end_date is not None else None,
        }

        if frame_type is not None:
            query["type"] = frame_type

        return self.__client.do_get(query)

    def update_event_frame(self, event_frame: EventFrame):
        """Update the properties on an event frame.

        Args:
            event_frame: The event frame to be updated.
        """
        data = {
            "eventFrame": event_frame.to_data(),
        }
        return self.__client.do_action("data_services/update_event_frame", data)

    def list_series(self, data_service: DataServiceSelector) -> List[SeriesSelector]:
        """Return all series in a Data Service Series Set.

        Args:
            data_service: The series set in the Data Service to list series for.

        Returns::
            A list of `SeriesSelector`s.
        """
        query = {"dataService": data_service.to_data()}
        return [
            SeriesSelector.from_data(data)
            for data in self.__client.do_action("data_services/list_series", query)
        ]

    def get_statistics(
        self,
        data_service: DataServiceSelector,
        selector: Optional[SeriesSelector] = None,
    ) -> List[Statistic]:
        """Return statistics stored in a Data Service.

        Returns multivariate and calculated statistics for a series set if no SeriesSelector is provided.

        Args:
            data_service: The series set in the Data Service to return statistics for.
            selector: The time series to return statistics for. (optional, keyword-only)

        Returns::
            A list of `Statistic`s.
        """
        query: Dict[str, Any] = {"dataService": data_service.to_data()}

        if selector is not None:
            query["selector"] = selector.to_data()

        return [
            Statistic.from_data(data)
            for data in self.__client.do_action("data_services/get_statistics", query)
        ]

    def get_calculated_metadata(
        self, data_service: DataServiceSelector, selector: SeriesSelector
    ) -> Metadata:
        """Return calculated metadata for a series in a Data Service.

        Args:
            data_service: The series set in a Data Service where the calculated metadata is kept.
            selector: The time series to return calculated metadata for.

        Returns::
            A `Metadata` object with the calculated metadata that's available.
        """
        query = {
            "dataService": data_service.to_data(),
            "selector": selector.to_data(),
        }
        return Metadata.from_data(
            self.__client.do_action("data_services/get_calculated_metadata", query),
            selector,
        )
