from __future__ import annotations

import datetime
import json
import logging
import time
from typing import Any, List, Optional, Union

import datarobot as dr
import datarobot.errors
import requests
from datarobot.errors import AsyncProcessUnsuccessfulError
from dateutil.parser import parse

from dmm.constants import ExportType
from dmm.utils import wait_for_result_from_status_url, wait_for_result_raw

logger = logging.getLogger(__name__)

_global_client = None


def get_global_client():
    global _global_client
    if not _global_client:
        _global_client = dr.Client()
    return _global_client


class DataRobotApiClient:
    """
    Wrapper around dr.Client that exposes required operations against DataRobot API.
    """

    def __init__(self, token: str = None, base_url: str = None, client: Any = None):
        if (token and not base_url) or (not token and base_url):
            raise Exception("Two parameters need to be provided: token and base_url")

        _api = None
        if token and base_url:
            _api = dr.Client(token=token, endpoint=base_url)
        elif client:
            _api = client
        else:
            _api = dr.Client()
        self._client = _api

    def start_prediction_data_export(
        self,
        deployment_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
        model_id: Union[str, None],
        **kwargs,
    ) -> requests.Response:
        return self._start_prediction_data_export(
            deployment_id, start, end, model_id, batch_ids=None
        )

    def start_batch_prediction_data_export(
        self,
        batch_ids: List[str],
        deployment_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
        model_id: Union[str, None],
        **kwargs,
    ) -> requests.Response:
        return self._start_prediction_data_export(
            deployment_id, start, end, model_id, batch_ids=batch_ids
        )

    def _start_prediction_data_export(
        self,
        deployment_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
        model_id: Union[str, None],
        batch_ids: Optional[List[str]],
    ) -> requests.Response:
        """
        Starts prediction data export between start (inclusive) and end (exclusive).
        We cannot assume anything about the order of returned records.

        Parameters
        ----------
        deployment_id: str
        start: datetime
            Inclusive start of the time range.
        end: datetime
            Exclusive end of the time range.
        model_id: Optional[str]
        batch_ids: Optional[List[str]]
            If present, it will perform batch export for the passed IDs.
        """
        return self._client.post(
            f"deployments/{deployment_id}/predictionDataExports/",
            data={
                "start": start,
                "end": end,
                "modelId": model_id,
                "batch_ids": batch_ids,
            },
        )

    def start_actuals_export(
        self,
        deployment_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
        model_id: Union[str, None],
        only_matched_predictions: bool = True,
        **kwargs,
    ) -> requests.Response:
        """
        Starts actuals data export between start (inclusive) and end (exclusive).
        We cannot assume anything about the order of returned records.

        Parameters
        ----------
        deployment_id: str
        start: datetime
            Inclusive start of the time range.
        end: datetime
            Exclusive end of the time range.
        model_id: Optional[str]
        only_matched_predictions : bool
            If true, exports actuals with matching predictions only.
        """
        return self._client.post(
            f"deployments/{deployment_id}/actualsDataExports/",
            data={
                "start": start,
                "end": end,
                "modelId": model_id,
                "onlyMatchedPredictions": only_matched_predictions,
            },
        )

    def start_training_data_export(
        self,
        deployment_id: str,
        model_id: Union[str, None],
    ) -> requests.Response:
        """
        Starts export of training data for the given model.
        If model_id is not given, export for current deployment champion.
        We cannot assume anything about the order of returned records.

        Parameters
        ----------
        deployment_id: str
        model_id: Optional[str]
        """
        return self._client.post(
            f"deployments/{deployment_id}/trainingDataExports/",
            data={"modelId": model_id},
        )

    def get_export_id_sync(self, start_export_response: requests.Response) -> str:
        """
        Waits until ready and fetches export_id after the export finishes. This method is blocking.

        Parameters
        ----------
        start_export_response: requests.Response
            Result of relevant start export call
        """
        export_id_response = wait_for_result_raw(self._client, start_export_response)
        export_id_response = json.loads(export_id_response)
        if export_id_response["status"] == "FAILED":
            raise AsyncProcessUnsuccessfulError(export_id_response["error"]["message"])
        return export_id_response["id"]

    def get_prediction_export_dataset_ids(
        self, deployment_id: str, export_id: str
    ) -> List[str]:
        """
        Export data can be fetched as datasets. This method fetches identifiers of these datasets.

        Parameters
        ----------
        deployment_id: str
        export_id: str
            Identifier of a completed export.
        """
        response = self._client.get(
            f"deployments/{deployment_id}/predictionDataExports/{export_id}"
        )
        data = response.json()["data"]
        dataset_ids = []
        if data:
            for item in data:
                try:
                    self._client.get(f"datasets/{item['id']}")
                except datarobot.errors.ClientError:
                    logger.info(
                        f"dataset {item['id']} not found for prediction export id {export_id}"
                        f" - was previously deleted"
                    )
                else:
                    dataset_ids.append(item["id"])
            return dataset_ids
        else:
            logger.info(f"no datasets found for prediction export id {export_id}")
            return []

    def get_actuals_export_dataset_ids(
        self, deployment_id: str, export_id: str
    ) -> List[str]:
        """
        Export data can be fetched as datasets. This method fetches identifiers of these datasets.

        Parameters
        ----------
        deployment_id: str
        export_id: str
            Identifier of a completed export.
        """
        response = self._client.get(
            f"deployments/{deployment_id}/actualsDataExports/{export_id}"
        )
        data = response.json()["data"]
        dataset_ids = []
        if data:
            for item in data:
                try:
                    self._client.get(f"datasets/{item['id']}")
                except datarobot.errors.ClientError:
                    logger.info(
                        f"dataset {item['id']} not found for actuals export id {export_id}"
                        f" - was previously deleted"
                    )
                else:
                    dataset_ids.append(item["id"])
            return dataset_ids
        else:
            logger.info(f"no datasets found for actuals export id {export_id}")
            return []

    def get_training_export_dataset_id(self, status_url: str) -> str:
        """
        Export data can be fetched as datasets. This method fetches identifier of this dataset.

        Parameters
        ----------
        status_url: str
        """
        export_id_response = wait_for_result_from_status_url(self._client, status_url)
        return json.loads(export_id_response)["datasetId"]

    def get_deployment(self, deployment_id: str) -> dict:
        """
        Fetches deployment metadata (model target name and type etc.)

        Parameters
        ----------
        deployment_id: str
        """
        return self._client.get(f"deployments/{deployment_id}").json()

    def get_model_package(self, model_package_id: str) -> dict:
        """
        Fetches model package info (to get time series info, prediction threshold etc.)

        Parameters
        ----------
        model_package_id: str
        """
        return self._client.get(f"modelPackages/{model_package_id}").json()

    def get_deployment_settings(self, deployment_id: str) -> dict:
        """
        Fetches deployment settings

        Parameters
        ----------
        deployment_id: str
        """
        return self._client.get(f"deployments/{deployment_id}/settings").json()

    def get_association_id(self, deployment_id: str) -> str:
        """
        Fetches association id for the given deployment, returns None if no association id

        Parameters
        ----------
        deployment_id: str
        """
        deployment_settings = self.get_deployment_settings(deployment_id)
        column_names = deployment_settings["associationId"]["columnNames"]
        association_id = column_names[0] if column_names else None
        return association_id

    def get_champion_model_package(self, deployment_id: str) -> dict:
        """
        Fetches champion model package data

        Parameters
        ----------
        deployment_id: str
        """
        return self._client.get(
            f"deployments/{deployment_id}/championModelPackage"
        ).json()

    @staticmethod
    def fetch_dataset_sync(dataset_id: str, max_wait_sec: int = 600) -> dr.Dataset:
        """
        Fetches dataset synchronously.

        Parameters
        ----------
        dataset_id: str
        max_wait_sec: int
            Maximum await time in seconds. Throws if waiting time exceeds this threshold.
        """
        start = time.time()
        while start + max_wait_sec > time.time():
            dataset = dr.Dataset.get(dataset_id)
            if dataset.processing_state == "COMPLETED":
                return dataset
            elif dataset.processing_state == "ERROR":
                raise ValueError(
                    "Dataset creation failed, most likely you requested range with no predictions"
                )
            time.sleep(5)
        raise Exception(f"Failed to fetch dataset within {max_wait_sec} seconds")

    def remove_dataset_with_exported_data(self, dataset_id: str) -> None:
        """
        Removes a catalog item from AI catalog.

        Parameters
        ----------
        dataset_id: str
        """
        self._client.delete(f"datasets/{dataset_id}")

    def get_custom_metric(self, deployment_id: str, custom_metric_id: str) -> dict:
        """
        Fetches custom metric metadata
        """
        return self._client.get(
            f"deployments/{deployment_id}/customMetrics/{custom_metric_id}/"
        ).json()

    def list_custom_metric(self, deployment_id: str) -> dict:
        """
        Retrieve a list of custom metrics
        """
        return self._client.get(f"deployments/{deployment_id}/customMetrics/").json()

    def submit_custom_metric_values(
        self,
        deployment_id: str,
        custom_metric_id: str,
        model_id: str,
        buckets: List[dict],
        dry_run: bool = False,
    ) -> requests.Response:
        """
        Upload custom metric values
        """
        return self._client.post(
            f"deployments/{deployment_id}/customMetrics/{custom_metric_id}/fromJSON/",
            data={"buckets": buckets, "modelId": model_id, "dryRun": dry_run},
        )

    def find_data_export(
        self,
        deployment_id: str,
        model_id: str,
        start: datetime.datetime,
        end: datetime.datetime,
        export_type: ExportType,
        actuals_with_matched_predictions: bool,
    ) -> Optional[str]:
        """
        Fetches data export by deployment_id, model_id and export range
        """
        compare_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        export_id = None

        if export_type == ExportType.PREDICTIONS:
            url = f"deployments/{deployment_id}/predictionDataExports/"
        elif export_type == ExportType.ACTUALS:
            url = f"deployments/{deployment_id}/actualsDataExports/"
        else:
            return export_id

        start = start.strftime(compare_format)
        end = end.strftime(compare_format)
        while url:
            response = self._client.get(url).json()
            url = response["next"]
            for export in response["data"]:
                if (
                    export_type == ExportType.ACTUALS
                    and export["onlyMatchedPredictions"]
                    != actuals_with_matched_predictions
                ):
                    continue

                if (
                    parse(export["period"]["start"]).strftime(compare_format) <= start
                    and parse(export["period"]["end"]).strftime(compare_format) >= end
                    and export["status"] == "SUCCEEDED"
                    and export["modelId"] == str(model_id)
                ):
                    return export["id"]
        return export_id
