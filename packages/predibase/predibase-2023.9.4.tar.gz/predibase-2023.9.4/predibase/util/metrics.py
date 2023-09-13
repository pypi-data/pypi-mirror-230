import re
from collections import namedtuple, OrderedDict
from typing import Dict

from tabulate import tabulate
from tqdm import tqdm

COMBINED = "combined"
LOSS = "loss"

TrainerMetric = namedtuple("TrainerMetric", ("epoch", "step", "value"))

metricsRegexString = "(train_metrics|test_metrics|validation_metrics)\\.(.+?)\\.(.*)"
metricsRegex = re.compile(metricsRegexString)


def split_sorter(split):
    if split.startswith("train"):
        return 0
    elif split.startswith("vali"):
        return 1
    elif split.startswith("test"):
        return 2
    return 3


class MetricsPrintedTable:
    """Maintains a table data structure used for logging metrics.

    ╒════════════╤════════════╤════════╤═════════════╤══════════╤═══════════╕
    │ Survived   │   accuracy │   loss │   precision │   recall │   roc_auc │
    ╞════════════╪════════════╪════════╪═════════════╪══════════╪═══════════╡
    │ train      │     0.7420 │ 0.7351 │      0.7107 │   0.5738 │    0.7659 │
    ├────────────┼────────────┼────────┼─────────────┼──────────┼───────────┤
    │ validation │     0.7079 │ 0.9998 │      0.6061 │   0.6061 │    0.7354 │
    ├────────────┼────────────┼────────┼─────────────┼──────────┼───────────┤
    │ test       │     0.7360 │ 0.7620 │      0.6667 │   0.5538 │    0.7358 │
    ╘════════════╧════════════╧════════╧═════════════╧══════════╧═══════════╛
    ╒════════════╤════════╕
    │ combined   │   loss │
    ╞════════════╪════════╡
    │ train      │ 0.7351 │
    ├────────────┼────────┤
    │ validation │ 0.9998 │
    ├────────────┼────────┤
    │ test       │ 0.7620 │
    ╘════════════╧════════╛
    """

    def __init__(self, metrics: Dict[str, float]):  # noqa
        # Construct a mapping of output_feature -> split -> metric_name
        output_features = {}
        for metric_name in metrics:
            match = metricsRegex.match(metric_name)
            if match:
                split, feature, name = match[1], match[2], match[3]
                if feature not in output_features:
                    output_features[feature] = {}
                if split not in output_features[feature]:
                    output_features[feature][split] = []
                output_features[feature][split].append(name)
        self.output_features = output_features

        self.printed_table = OrderedDict()
        for feature in output_features:
            metric_names = set()
            for split in output_features[feature]:
                metric_names = metric_names.union(set(output_features[feature][split]))
            self.printed_table[feature] = [[feature] + list(metric_names)]
        self.printed_table[COMBINED] = [[COMBINED, LOSS]]
        #
        # # Establish the printed table's order of metrics (used for appending metrics in the right order).
        self.metrics_headers = {}
        for output_feature_name in output_features.keys():
            # [0]: The header is the first row, which contains names of metrics.
            # [1:]: Skip the first column as it's just the name of the output feature, not an actual metric name.
            self.metrics_headers[output_feature_name] = self.printed_table[output_feature_name][0][1:]
        self.metrics_headers[COMBINED] = [LOSS]

        self.add_metrics_to_printed_table(metrics)

    def add_metrics_to_printed_table(self, metrics: Dict[str, float]):
        """Add metrics to tables by the order of the table's metric header."""
        for output_feature_name in self.output_features:
            for split, metric_names in sorted(
                self.output_features[output_feature_name].items(),
                key=lambda x: split_sorter(x[0]),
            ):
                printed_metrics = []
                for metric_name in self.metrics_headers[output_feature_name]:
                    full_metric_name = f"{split}.{output_feature_name}.{metric_name}"
                    if metric_name in metric_names and full_metric_name in metrics:
                        printed_metrics.append(metrics[full_metric_name])
                    else:
                        printed_metrics.append("")
                self.printed_table[output_feature_name].append([split[: split.index("_")]] + printed_metrics)

    def log_info(self):
        for output_feature, table in self.printed_table.items():
            tqdm.write(tabulate(table, headers="firstrow", tablefmt="fancy_grid", floatfmt=".4f"))
