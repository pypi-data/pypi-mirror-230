from __future__ import annotations

import os

import datarobot as dr
import pandas as pd
import requests
from dateutil.parser import parse

from dmm.constants import CustomMetricAggregationType, CustomMetricDirectionality
from dmm.datarobot_api_client import DataRobotApiClient

_global_client = None


def get_global_client():
    global _global_client
    if not _global_client:
        _global_client = dr.Client()
    return _global_client


class CustomMetric:
    def __init__(
        self,
        custom_metric_id: str,
        deployment_id: str,
        model_id: str,
        name: str,
        directionality: CustomMetricDirectionality,
        units: str,
        aggregation_type: CustomMetricAggregationType,
        baseline_value: float,
        is_model_specific: bool,
        description: str = None,
        value: str = None,
        sample_count: str = None,
        timestamp: str = None,
        time_format: str = None,
        batch: str = None,
        client: dr.Client = None,
    ):
        self.custom_metric_id = custom_metric_id
        self.name = name
        self.directionality = directionality
        self.units = units
        self.aggregation_type = aggregation_type
        self.baseline_value = baseline_value
        self.is_model_specific = is_model_specific

        self.description = description
        self.timestamp = timestamp
        self.time_format = time_format
        self.value = value
        self.sample_count = sample_count
        self.batch = batch

        self.deployment_id = deployment_id
        self.model_id = model_id
        self._api = DataRobotApiClient(client.token, client.endpoint)

    @classmethod
    def from_id(
        cls,
        metric_id: str = None,
        deployment_id: str = None,
        model_id: str = None,
        client: dr.Client = None,
    ) -> CustomMetric:
        deployment_id = deployment_id or os.environ.get("DEPLOYMENT_ID")
        metric_id = metric_id or os.environ.get("CUSTOM_METRIC_ID")

        if not client:
            client = get_global_client()
        base_url = client.endpoint
        token = client.token

        api = DataRobotApiClient(token, base_url)
        cm_metadata = api.get_custom_metric(deployment_id, metric_id)

        # get champion model if metric is model specific and user does not explicitly pass the model_id
        if cm_metadata["isModelSpecific"] and not model_id:
            model_id = api.get_deployment(deployment_id)["model"]["id"]

        # set model_id to None if metric is deployment specific
        if not cm_metadata["isModelSpecific"]:
            model_id = None

        baseline_value = (
            cm_metadata["baselineValues"][0]["value"]
            if cm_metadata["baselineValues"]
            else None
        )

        custom_metric = cls(
            custom_metric_id=metric_id,
            deployment_id=deployment_id,
            model_id=model_id,
            name=cm_metadata["name"],
            directionality=cm_metadata["directionality"],
            units=cm_metadata["directionality"],
            aggregation_type=cm_metadata["directionality"],
            baseline_value=baseline_value,
            description=cm_metadata["description"],
            is_model_specific=cm_metadata["isModelSpecific"],
            value=cm_metadata["value"]["columnName"],
            sample_count=cm_metadata["sampleCount"]["columnName"],
            batch=cm_metadata["batch"]["columnName"],
            timestamp=cm_metadata["timestamp"]["columnName"],
            time_format=cm_metadata["timestamp"]["timeFormat"],
            client=client,
        )
        return custom_metric

    def report(self, df: pd.DataFrame, dry_run: bool = False) -> requests.Response:
        buckets = []
        for _, row in df.iterrows():
            buckets.append(
                {
                    "timestamp": parse(row["timestamp"]).isoformat(),
                    "sampleSize": row["samples"],
                    "value": row[self.name],
                }
            )
        response = self._api.submit_custom_metric_values(
            self.deployment_id, self.custom_metric_id, self.model_id, buckets, dry_run
        )
        return response
