import time
from typing import Any, Type, List, Dict, Union

from snowmate_collector.data_collection.metrics import BaseMetric


class MetricAttribute:
    def __init__(self, attribute: str, attribute_value: Any):
        self.attribute = attribute
        self.attribute_value = attribute_value
        self.attribute_type = self.get_attribute_type(attribute_value)

    @staticmethod
    def get_attribute_type(attribute_value: Any) -> str:
        if isinstance(attribute_value, str):
            attribute_value_key = "stringValue"
        else:
            attribute_value_key = "doubleValue"
        return attribute_value_key

    def to_json(self):
        return {
            "key": self.attribute,
            "value": {
                self.attribute_type: self.attribute_value
            },
        }


class MetricAttributes:
    def __init__(self, metric: Union[Type[BaseMetric], BaseMetric]):
        self.attributes: List[MetricAttribute] = []
        self.attributes_dict: Dict[str, Any] = {}
        metric_attributes = metric.get_attributes_as_dict()
        metric_attributes.setdefault("service_name", "snowmate_collector")
        for attribute, attribute_value in metric_attributes.items():
            self.attributes.append(
                MetricAttribute(
                    attribute=attribute,
                    attribute_value=attribute_value
                )
            )
            self.attributes_dict[attribute] = attribute_value

    def get(self, attribute: str) -> Any:
        return self.attributes_dict.get(attribute)

    def contains(self, attribute: str) -> bool:
        return attribute in self.attributes_dict

    def to_json(self):
        return [attribute.to_json() for attribute in self.attributes]


class Metric:
    def __init__(self, metric: BaseMetric, counter: int):
        self.name = metric.get_counter_name()
        self._metric = metric
        self._counter = counter
        self.attributes = MetricAttributes(metric)

    @property
    def counter(self) -> str:
        return str(self._counter)

    @property
    def metric_type(self):
        return type(self._metric)

    def to_json(self):
        return {
            "name": self.name,
            "unit": "10000",
            "sum": {
                "dataPoints": [
                    {
                        "attributes": self.attributes.to_json(),
                        "startTimeUnixNano": str(
                            int(time.time() * 1e9)
                        ),
                        "timeUnixNano": str(int(time.time() * 1e9)),
                        "asInt": self.counter,
                    },
                ],
                "aggregationTemporality": 2,
                "isMonotonic": True,
            },
        }


class Metrics:
    def __init__(self):
        self._metrics: List[Metric] = []
        self._index = -1

    def add_metric(self, metric: Metric):
        self._metrics.append(metric)

    def __iter__(self):
        return self

    def __next__(self):
        self._index += 1
        if self._index >= len(self._metrics):
            self._index = -1
            raise StopIteration
        return self._metrics[self._index]

    def get_metrics(self):
        return self._metrics

    def to_json(self):
        return {
            "resourceMetrics": [
                {
                    "resource": {
                        "attributes": [
                            {
                                "key": "resource-attr",
                                "value": {"stringValue": "resource-attr-val-1"},
                            }
                        ]
                    },
                    "instrumentationLibraryMetrics": [
                        {
                            "metrics": [metric.to_json() for metric in self._metrics],
                        }
                    ],
                }
            ]
        }
