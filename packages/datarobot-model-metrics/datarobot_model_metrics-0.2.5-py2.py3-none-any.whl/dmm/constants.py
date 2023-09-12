class ColumnName:
    PREDICTIONS = "predictions"
    TARGET_VALUE = "target_value"
    ACTUALS = "actuals"
    TIMESTAMP = "timestamp"
    NR_SAMPLES = "samples"
    METRIC_VALUE = "value"
    DR_TIMESTAMP_COLUMN = "DR_RESERVED_PREDICTION_TIMESTAMP"
    DR_PREDICTION_COLUMN = "DR_RESERVED_PREDICTION_VALUE"
    DR_BATCH_ID_COLUMN = "DR_RESERVED_BATCH_ID"
    ASSOCIATION_ID_COLUMN = "association_id"
    BATCH_ID_COLUMN = "batch_id"
    LABEL = "label"
    PREDICTED_CLASS = "predicted_class"


class TimeBucket:
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    ALL = "all"


class DataGroups:
    SCORING = "scoring"
    PREDICTIONS = "predictions"
    ACTUALS = "actuals"


class CustomMetricDirectionality:
    HIGHER_IS_BETTER = "higherIsBetter"
    LOWER_IS_BETTER = "lowerIsBetter"


class CustomMetricAggregationType:
    SUM = "sum"
    AVERAGE = "average"
    GAUGE = "gauge"


class ExportType:
    PREDICTIONS = "predictions"
    ACTUALS = "actuals"

    @classmethod
    def all(cls):
        return [cls.PREDICTIONS, cls.ACTUALS]
