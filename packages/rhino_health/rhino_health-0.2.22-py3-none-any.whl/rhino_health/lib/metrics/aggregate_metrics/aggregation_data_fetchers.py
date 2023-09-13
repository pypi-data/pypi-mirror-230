"""
@autoapi False
Functions for fetching the relevant information for a given metric
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

from funcy import merge

from rhino_health.lib.metrics.base_metric import BaseMetric, MetricResponse


class MetricFetcher(ABC):
    if TYPE_CHECKING:
        from rhino_health.lib.rhino_session import RhinoSession

    @abstractmethod
    def fetch_metrics(
        self, session: RhinoSession, cohort_uids: List[str], metric_configuration: BaseMetric
    ) -> List[MetricResponse]:
        raise NotImplementedError


class DefaultMetricFetcher:
    if TYPE_CHECKING:
        from rhino_health.lib.rhino_session import RhinoSession

    def fetch_metrics(
        self, session: RhinoSession, cohort_uids: List[str], metric_configuration: BaseMetric
    ) -> List[MetricResponse]:
        return [
            session.cohort.get_cohort_metric(cohort_uid, metric_configuration)
            for cohort_uid in cohort_uids
        ]


class MultipleMetricFetcher(DefaultMetricFetcher):
    if TYPE_CHECKING:
        from rhino_health.lib.rhino_session import RhinoSession

    def __init__(self, metric_classes):
        self.metric_classes: List[BaseMetric] = metric_classes

    def get_configurations(self, metric_configuration: BaseMetric) -> List[BaseMetric]:
        return [
            metric_class(**metric_configuration.dict(exclude_unset=True))
            for metric_class in self.metric_classes
        ]

    def fetch_metrics(
        self, session: RhinoSession, cohort_uids: List[str], metric_configuration: BaseMetric
    ) -> List[MetricResponse]:
        results = []
        metric_configurations = self.get_configurations(metric_configuration)
        for cohort_uid in cohort_uids:
            per_cohort_result = {}
            for metric_configuration in metric_configurations:
                single_metric_result = session.cohort.get_cohort_metric(
                    cohort_uid, metric_configuration
                ).output
                if metric_configuration.group_by is None:
                    per_cohort_result = merge({}, per_cohort_result, single_metric_result)
                else:
                    for group_key, group_value in single_metric_result.items():
                        per_cohort_result[group_key] = merge(
                            {}, per_cohort_result.get(group_key, {}), group_value
                        )
            results.append(MetricResponse(output=per_cohort_result))
        return results
