from rhino_health.lib.metrics.aggregate_metrics.aggregation_constants import (
    AGGREGATION_METHOD,
    METRIC_FETCHER,
)
from rhino_health.lib.metrics.aggregate_metrics.aggregation_data_fetchers import (
    MultipleMetricFetcher,
)
from rhino_health.lib.metrics.aggregate_metrics.aggregation_methods import (
    standard_deviation,
    sum_aggregation,
    weighted_average,
)
from rhino_health.lib.metrics.basic import Mean, StandardDeviation

"""
Configuration Mappings for different built in metrics that determines how we
should aggregate, fetch, etc.
"""

SUPPORTED_AGGREGATE_METRICS = {
    "mean": {
        AGGREGATION_METHOD: weighted_average,
    },
    "count": {
        AGGREGATION_METHOD: sum_aggregation,
    },
    "sum": {
        AGGREGATION_METHOD: sum_aggregation,
    },
    "std": {
        AGGREGATION_METHOD: standard_deviation,
        METRIC_FETCHER: MultipleMetricFetcher([StandardDeviation, Mean]),
    },
    "accuracy_score": {AGGREGATION_METHOD: weighted_average},
    "average_precision_score": {AGGREGATION_METHOD: weighted_average},
    "balanced_accuracy_score": {AGGREGATION_METHOD: weighted_average},
    "brier_score_loss": {AGGREGATION_METHOD: weighted_average},
    "cohen_kappa_score": {AGGREGATION_METHOD: weighted_average},
    "confusion_matrix": {AGGREGATION_METHOD: weighted_average},
    "dcg_score": {AGGREGATION_METHOD: weighted_average},
    "f1_score": {AGGREGATION_METHOD: weighted_average},
    "fbeta_score": {AGGREGATION_METHOD: weighted_average},
    "hamming_loss": {AGGREGATION_METHOD: weighted_average},
    "hinge_loss": {AGGREGATION_METHOD: weighted_average},
    "jaccard_score": {AGGREGATION_METHOD: weighted_average},
    "log_loss": {AGGREGATION_METHOD: weighted_average},
    "matthews_corrcoef": {AGGREGATION_METHOD: weighted_average},
    "ndcg_score": {AGGREGATION_METHOD: weighted_average},
    "precision_score": {AGGREGATION_METHOD: weighted_average},
    "recall_score": {AGGREGATION_METHOD: weighted_average},
    "top_k_accuracy_score": {AGGREGATION_METHOD: weighted_average},
    "zero_one_loss": {AGGREGATION_METHOD: weighted_average},
}
"""
A dictionary of metrics we currently support aggregating to configuration information.
See the keys for the latest list of metrics.
"""
