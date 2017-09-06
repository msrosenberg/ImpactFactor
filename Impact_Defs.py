# metric definitions for impact factor calculator

import datetime
from typing import Tuple

INT = 0
FLOAT = 1
INTLIST = 2
FLOAT_NEG = 3
LINE_CHART = 1


class Metric:
    def __init__(self):
        self.name = ""
        self.full_name = ""
        self.citation = ""
        self.__html_name = None
        self.is_self = False
        self.metric_type = FLOAT
        self.description = ""
        self.calculate = None
        self.__value = None
        self.parent_set = None

    @property
    def html_name(self):
        if self.__html_name is None:
            return self.full_name
        else:
            return self.__html_name

    @html_name.setter
    def html_name(self, value):
        self.__html_name = value

    @property
    def value(self):
        if self.__value is None:
            self.__value = self.calculate(self.parent_set)
        return self.__value


class MetricSet:
    def __init__(self):
        self.date = datetime.date(1970, 1, 1)
        self.cumulativeCites = []
        self.metrics = {}
        self.citations = []


# Total Publications
def calculate_total_pubs(metric_set: MetricSet) -> int:
    return len(metric_set.citations)


def metric_total_pubs() -> Metric:
    m = Metric()
    m.name = "total pubs"
    m.full_name = "total publications"
    m.metric_type = INT
    m.description = "<p>This metric is the total number of publications by an author.</p>"
    m.calculate = calculate_total_pubs
    return m


# Total Citations
def calculate_total_cites(metric_set: MetricSet) -> int:
    return sum(metric_set.citations)


def metric_total_cites() -> Metric:
    m = Metric()
    m.name = "total cites"
    m.full_name = "total citations"
    m.metric_type = INT
    m.description = "<p>This metric is the total number of citations to all publications by an author.</p>"
    m.calculate = calculate_total_cites
    return m


# Maximum Citations
def calculate_max_cites(metric_set: MetricSet) -> int:
    return max(metric_set.citations)


def metric_max_cites() -> Metric:
    m = Metric()
    m.name = "max cites"
    m.full_name = "maximum citations"
    m.metric_type = INT
    m.description = "<p>This metric is the largest number of citations found for a single publication by an author.</p>"
    m.calculate = calculate_max_cites
    return m


# Indifference - Egghe and Rousseau (1996)
def calculate_indifference(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return total_pubs / total_cites


def metric_indifference() -> Metric:
    m = Metric()
    m.name = "indifference"
    m.full_name = "indifference"
    m.citation = "Egghe and Rousseau (1996)"
    m.metric_type = FLOAT
    m.description = "<p>This metric is simply the total number of publications divided by the number of total " \
                    "number of citations. The larger this value, the more indifferent the community is to the " \
                    "author\'s work. This metric is also just the inverse of the average number of citations per " \
                    "publication.</p>"
    m.calculate = calculate_indifference
    return m


def load_all_metrics() -> list:
    metric_list = [metric_total_pubs(),
                   metric_total_cites(),
                   metric_max_cites(),
                   metric_indifference()]
    return metric_list

"""
    "max cites",
    "avg cites per pub",
    "median cites per pub",
    "time-scaled num papers",
    "time-scaled num citations",
    "h-index",
    "core cites",
    "Hirsch min const",
    "g-index",
    "Tol f-index",
    "Tol t-index",
    "mu-index",
    "Woeginger w-index",
    "h(2)-index",
    "Wu w-index",
    "hg-index",
    "rational h-index",
    "real h-index",
    "Wu w(q)",
    "tapered h-index",
    "j-index",
    "Wohlin w-index",
    "hj-indices",
    "v-index",
    "normalized h-index",
    "a-index",
    "m-index",
    "r-index",
    "rm-index",
    "weighted h-index",
    "pi-index",
    "q2-index",
    "e-index",
    "maxprod-index",
    "h2-upper",
    "h2-center",
    "h2-tail",
    "k-index",
    "p-index",
    "ph-ratio",
    "multidim h-index",
    "twosided h-index",
    "iter weighted h-index",
    "em-index",
    "emp-index",
    "hi-index",
    "frac pure h-index",
    "prop pure h-index",
    "geom pure h-index",
    "frac adapt pure h-index",
    "prop adapt pure h-index",
    "geom adapt pure h-index",
    "hf/hi-index",
    "hF/hm-index",
    "position-weighted h-index",
    "frac weight citation aggregate",
    "prop weight citation aggregate",
    "frac weight citation H-cut",
    "prop weight citation H-cut",
    "gf-cite",
    "gf-paper",
    "fractional p-index",
    "harmonic p-index",
    "profit p-index",
    "profit adj h-index",
    "profit h-index",
    "total self citations",
    "total self citation rate",
    "avg self citation rate",
    "self sharpened h-index",
    "avg self b-index",
    "total self/coauthor citations",
    "total self/coauthor citation rate",
    "avg self/coauthor citation rate",
    "all sharpened h-index",
    "avg all b-index",
    "10% b-index",
    "h-rate",
    "ls h-rate",
    "time-scaled h-index",
    "alpha-index",
    "ar-index",
    "dynamic h-type-index",
    "hpd-index",
    "contemporary h-index",
    "trend h-index",
    "impact vitality",
    "specific impact s-index",
    "Franceschini f-index",
    "annual h-index",
    "CDS-index",
    "CDR-index",
    "circ cite area radius",
    "citation acceleration",
    "Redner index",
    "Levene j-index",
    "S-index (h-mixed)",
    "T-index (h-mixed)",
    "citation entropy",
    "cq index",
    "cq0.4 index",

"""


if __name__ == "__main__":
    xmetric_list = load_all_metrics()
    metric_names = [m.name for m in xmetric_list]
    new_set = MetricSet()
    new_set.metrics = {m.name: m for m in xmetric_list}
    new_set.citations = [100, 20, 5, 1, 1]
    for m in xmetric_list:
        m.parent_set = new_set

    for m in new_set.metrics:
        metric = new_set.metrics[m]
        print(metric.value)
