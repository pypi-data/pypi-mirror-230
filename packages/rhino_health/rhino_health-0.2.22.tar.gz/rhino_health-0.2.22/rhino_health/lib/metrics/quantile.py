from typing import Union

from rhino_health.lib.metrics.base_metric import BaseMetric
from rhino_health.lib.metrics.filter_variable import FilterVariableTypeOrColumnName


class Median(BaseMetric):
    """
    Returns the median of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName

    @classmethod
    def metric_name(cls):
        return "median"

    @classmethod
    def uses_cloud_aggregation(cls):
        return True


class Percentile(BaseMetric):
    """
    Returns the k-percentile of entries for a specified VARIABLE
    """

    variable: FilterVariableTypeOrColumnName
    percentile: Union[int, float]

    @classmethod
    def metric_name(cls):
        return "percentile"

    @classmethod
    def uses_cloud_aggregation(cls):
        return True
