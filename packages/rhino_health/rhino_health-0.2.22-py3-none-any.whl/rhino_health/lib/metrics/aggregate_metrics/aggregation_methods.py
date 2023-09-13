from typing import List

from rhino_health.lib.metrics.base_metric import MetricResultDataType

"""
Various different aggregation methods are implemented here.
If you wish to leverage our utility functions to fetch data from
multiple cohorts but wish to use your own aggregation method
you can implement your own method with the same signature
and pass it in as an override.
"""


def sum_aggregation(
    metric: str, metric_results: List[MetricResultDataType], **kwargs
) -> MetricResultDataType:
    """
    Sums the values received
    """
    return {metric: sum([metric_result.get(metric, 0) for metric_result in metric_results])}


def weighted_average(
    metric: str, metric_results: List[MetricResultDataType], count_variable="variable", **kwargs
) -> MetricResultDataType:
    """
    Uses weighted average based on sample size to get the overall value
    """
    total_count = sum(
        [metric_result.get(f"{count_variable}_count", 0) for metric_result in metric_results]
    )
    return {
        metric: (
            sum(
                [
                    metric_result.get(f"{count_variable}_count", 0) * metric_result.get(metric, 0)
                    for metric_result in metric_results
                ]
            )
            / total_count
        )
    }


def standard_deviation(
    metric: str, metric_results: List[MetricResultDataType], **kwargs
) -> MetricResultDataType:
    """
    Calculates the overall standard deviation using the population unbiased estimator method.

    See https://math.stackexchange.com/a/2971563 for the formula.

    .. warning:: Combining standard deviation must be used with
    care as statistically this method assumes that the individual
    results are different samples from the same population.

    You may wish to consider using effect sizes and other metanalysis
    instead of aggregate standard deviation
    """
    # Filter out len 0 counts to avoid arithmetic error in combination formula.
    valid_results = [result for result in metric_results if result.get("variable_count", 0) > 0]
    if not len(valid_results):
        return {metric: 0}
    if len(valid_results) == 1:
        return {metric: valid_results[0].get(metric, 0)}
    current_standard_deviation = valid_results[0].get("std", 0)
    current_mean = valid_results[0].get("mean", 0)
    current_count = valid_results[0].get(f"variable_count", 0)
    for standard_deviation_result in valid_results[1:]:
        # Read variables for this iteration
        new_standard_deviation = standard_deviation_result.get("std", 0)
        new_mean = standard_deviation_result.get("mean", 0)
        new_count = standard_deviation_result.get(f"variable_count", 0)

        old_variance = current_standard_deviation**2
        new_variance = new_standard_deviation**2

        # Calculate the combined stddev of the two samples
        pooled_standard_variance = (
            (current_count - 1) * old_variance + (new_count - 1) * new_variance
        ) / (current_count + new_count - 1)
        bias_offset = (current_count * new_count * ((current_mean - new_mean) ** 2)) / (
            (current_count + new_count) * (current_count + new_count - 1)
        )
        combined_standard_deviation = (pooled_standard_variance + bias_offset) ** 0.5

        # Save variables for next iteration
        current_standard_deviation = combined_standard_deviation
        current_mean = (current_mean * current_count) + (new_mean * new_count) / (
            current_count + new_count
        )
        current_count = current_count + new_count
    return {metric: current_standard_deviation}
