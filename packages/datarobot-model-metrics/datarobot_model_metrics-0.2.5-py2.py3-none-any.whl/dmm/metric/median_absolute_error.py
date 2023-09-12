from dmm.metric.sklearn_metric import SklearnMetric


class MedianAbsoluteError(SklearnMetric):
    """
    Metric that calculates the median absolute error of the difference between predictions and actuals
    """

    def __init__(self):
        super().__init__(
            metric="median_absolute_error",
        )
