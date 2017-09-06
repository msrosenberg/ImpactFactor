# metric definitions for impact factor calculator

import datetime
# from typing import Tuple

# --- Internal Constants ---
INT = 0
FLOAT = 1
INTLIST = 2
FLOAT_NEG = 3
LINE_CHART = 1

FSTR = "1.4f"  # constant formatting string


# --- General Class Definitions ---

class Metric:
    """
    This class represents a single metric, with all of its properties and values
    """
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

    def __str__(self):
        if self.metric_type == INT:
            return str(self.value)
        elif self.metric_type == FLOAT:
            return format(self.value, FSTR)
        elif self.metric_type == INTLIST:
            return str(self.value)
        elif self.metric_type == FLOAT_NEG:
            if self.value < 0:
                return "n/a"
            else:
                return format(self.value, FSTR)


class MetricSet:
    """
    This class contains all of the metric output for a single year
    """
    def __init__(self):
        self.date = datetime.date(1970, 1, 1)
        self.cumulativeCites = []
        self.citations = []
        tmp_list = load_all_metrics()
        self.metrics = {m.name: m for m in tmp_list}
        for m in self.metrics:
            self.metrics[m].parent_set = self
        self.metric_names = [m.name for m in tmp_list]


# --- Definitions and Calculations for Individual Metrics---

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


# Mean Citations
def calculate_mean_cites(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return total_cites / total_pubs


def metric_mean_cites() -> Metric:
    m = Metric()
    m.name = "c/p"
    m.full_name = "mean citations per publication (C/P index)"
    m.html_name = "mean citations per publication (<em>C/P</em> index)"
    m.metric_type = FLOAT
    m.description = "<p>This metric is the mean number of citations per publication. It has been described under " \
                    "many names, including the <em>C/P</em> index, the mean citation rate (<em>MCR</em>), the mean " \
                    "observed citation rate (<em>MOCR</em>), citations per publication (<em>CPP</em>), the observed " \
                    "citation rate (<em>OCR</em>), the generalized impact factor (<em>I<sub>f</sub><em>), and the " \
                    "journal paper citedness (<em>JPC</em>).</p>"
    m.calculate = calculate_mean_cites
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
                    "author\'s work. This metric is also just the inverse of the mean number of citations per " \
                    "publication (<em>C/P</em>).</p>"
    m.calculate = calculate_indifference
    return m


# --- main initialization loop ---
def load_all_metrics() -> list:
    """
    function to create a list containing an instance of every metric

    the order is important since some will need to be calculated prior to others
    """
    metric_list = [metric_total_pubs(),
                   metric_total_cites(),
                   metric_max_cites(),
                   metric_mean_cites(),
                   metric_indifference()]
    return metric_list

"""
    "h-index": [False, INT, "h-index", "<em>h-</em>index"],
    "core cites": [False, INT, "Hirsch-core Citations"],
    "Hirsch min const": [False, FLOAT, "Hirsch Min Constant (a)", "Hirsch Min Constant (<em>a</em>)"],
    "g-index": [False, INT, "g-index", "<em>g-</em>index"],
    "Tol f-index": [False, INT, "f-index (Tol)", "<em>f-</em>index (Tol)"],
    "Tol t-index": [False, INT, "t-index (Tol)", "<em>t-</em>index (Tol)"],
    "mu-index": [False, INT, "μ-index", "<em>μ-</em>index"],
    "Woeginger w-index": [False, INT, "w-index (Woeginger)", "<em>w-</em>index (Woeginger)"],
    "h(2)-index": [False, INT, "h(2)-index", "<em>h</em>(2)-index"],
    "Wu w-index": [False, INT, "w-index (Wu)", "<em>w-</em>index (Wu)"],
    "hg-index": [False, FLOAT, "hg-index", "<em>hg-</em>index"],
    "rational h-index": [False, FLOAT, "rational h-index", "rational <em>h-</em>index"],
    "real h-index": [False, FLOAT, "real h-index", "real <em>h-</em>index"],
    "Wu w(q)": [False, INT, "w(q) (Wu)", "<em>w</em>(<em>q</em>) (Wu)"],
    "tapered h-index": [False, FLOAT, "tapered h-index", "tapered <em>h-</em>index"],
    "j-index": [False, FLOAT, "j-index", "<em>j-</em>index"],
    "Wohlin w-index": [False, FLOAT, "w-index (Wohlin)", "<em>w-</em>index (Wohlin)"],
    "hj-indices": [False, INTLIST, "hj-indices", "<em>hj-</em>indices"],
    "v-index": [False, FLOAT, "v-index", "<em>v-</em>index"],
    "normalized h-index": [False, FLOAT, "normalized h-index", "normalized <em>h-</em>index"],
    "a-index": [False, FLOAT, "a-index", "<em>a-</em>index"],
    "m-index": [False, FLOAT, "m-index", "<em>m-</em>index"],
    "r-index": [False, FLOAT, "r-index", "<em>R-</em>index"],
    "rm-index": [False, FLOAT, "rm-index", "<em>rm-</em>index"],
    "weighted h-index": [False, FLOAT, "weighted h-index", "weighted <em>h-</em>index"],
    "pi-index": [False, FLOAT, "π-index", "<em>π-</em>index"],
    "q2-index": [False, FLOAT, "q2-index", "<em>q</em><sup>2</sup>-index"],
    "e-index": [False, FLOAT, "e-index", "<em>e-</em>index"],
    "maxprod-index": [False, INT, "maxprod-index"],
    "h2-upper": [False, FLOAT, "h2-upper index", "<em>h</em><sup>2</sup>-upper index"],
    "h2-center": [False, FLOAT, "h2-center index", "<em>h</em><sup>2</sup>-center index"],
    "h2-tail": [False, FLOAT, "h2-tail index", "<em>h</em><sup>2</sup>-tail index"],
    "k-index": [False, FLOAT, "k-index", "<em>k-</em>index"],
    "p-index": [False, FLOAT, "p-index", "<em>p-</em>index"],
    "ph-ratio": [False, FLOAT, "ph-ratio", "<em>ph-</em>ratio"],
    "multidim h-index": [False, INTLIST, "multidimensional h-index", "multidimensional <em>h-</em>index"],
    "twosided h-index": [False, INTLIST, "two-sided h-index", "two-sided <em>h-</em>index"],
    "iter weighted h-index": [False, FLOAT, "iteratively weighted h-index", "iteratively weighted <em>h-</em>index"],
    "em-index": [False, FLOAT, "EM-index", "<em>EM-</em>index"],
    "emp-index": [False, FLOAT, "EMʹ-index", "<em>EM</em>ʹ-index"],
    "hi-index": [False, FLOAT, "hi-index", "<em>h<sub>i</sub>-</em>index"],
    "frac pure h-index": [False, FLOAT, "pure h-index (fractional credit)",
                          "pure <em>h-</em>index (fractional credit)"],
    "prop pure h-index": [False, FLOAT, "pure h-index (proportional credit)",
                          "pure <em>h-</em>index (proportional credit)"],
    "geom pure h-index": [False, FLOAT, "pure h-index (geometric credit)",
                          "pure <em>h-</em>index (geometric credit)"],
    "frac adapt pure h-index": [False, FLOAT, "adapted pure h-index",
                                "adapted pure <em>h-</em>index (fractional credit)"],
    "prop adapt pure h-index": [False, FLOAT, "adapted pure h-index (proportional credit)",
                                "adapted pure <em>h-</em>index (proportional credit)"],
    "geom adapt pure h-index": [False, FLOAT, "adapted pure h-index (geometric credit)",
                                "adapted pure <em>h-</em>index (geometric credit)"],
    "hf/hi-index": [False, INT, "hf-index/normalized hi-index",
                    "<em>h<sub>f</sub>-</em>index/normalized <em>h<sub>i</sub>-</em>index"],
    "hF/hm-index": [False, FLOAT, "hF-index/hm-index", "<em>h<sub>F</sub>-</em>index/<em>h<sub>m</sub>-</em>index"],
    "position-weighted h-index": [False, INT, "position-weighted h-index (hp)",
                                  "position-weighted <em>h-</em>index (<em>h<sub>p</sub></em>)"],
    "frac weight citation aggregate": [False, FLOAT, "weighted citation aggregate (fractional)"],
    "prop weight citation aggregate": [False, FLOAT, "weighted citation aggregate (proportional)"],
    "frac weight citation H-cut": [False, FLOAT, "weighted citation H-cut (fractional)"],
    "prop weight citation H-cut": [False, FLOAT, "weighted citation H-cut (proportional)"],
    "gf-cite": [False, INT, "gf-index", "<em>g<sub>f</sub>-</em>index"],
    "gf-paper": [False, FLOAT, "gF-index", "<em>g<sub>F</sub>-</em>index"],
    "fractional p-index": [False, FLOAT, "fractional p-index", "fractional <em>p-</em>index"],
    "harmonic p-index": [False, FLOAT, "harmonic p-index", "harmonic <em>p-</em>index"],
    "profit p-index": [False, FLOAT, "profit p-index", "profit <em>p-</em>index"],
    "profit adj h-index": [False, INT, "profit adjusted h-index", "profit adjusted <em>h-</em>index"],
    "profit h-index": [False, FLOAT, "profit h-index", "profit <em>h-</em>index"],
    "total self citations": [True, INT, "total self citations"],
    "total self citation rate": [True, FLOAT, "total self citation rate"],
    "avg self citation rate": [True, FLOAT, "average self citation rate"],
    "self sharpened h-index": [True, INT, "sharpened h-index (self citations only)",
                               "sharpened <em>h-</em>index (self citations only)"],
    "avg self b-index": [True, FLOAT, "b-index (avg self citation rate)", "<em>b-</em>index (avg self citation rate)"],
    "total self/coauthor citations": [True, INT, "total self & coauthor citations",
                                      "total self &amp; coauthor citations"],
    "total self/coauthor citation rate": [True, FLOAT, "total self & coauthor citation rate",
                                          "total self &amp; coauthor citation rate"],
    "avg self/coauthor citation rate": [True, FLOAT, "average self & coauthor citation rate",
                                        "average self &amp; coauthor citation rate"],
    "all sharpened h-index": [True, INT, "sharpened h-index (self & coauthor citations)",
                              "sharpened <em>h-</em>index (self &amp; coauthor citations)"],
    "avg all b-index": [True, FLOAT, "b-index (avg self & coauthor citation rate)",
                        "<em>b-</em>index (avg self &amp; coauthor citation rate)"],
    "10% b-index": [True, FLOAT, "b-index (10% self-citation rate)", "<em>b-</em>index (10% self-citation rate)"],
    "h-rate": [False, FLOAT, "h-rate/Hirsch m-quotient (slope)", "<em>h-</em>rate/Hirsch <em>m-</em>quotient (slope)"],
    "ls h-rate": [False, FLOAT, "least squares h-rate (slope)", "least squares <em>h-</em>rate (slope)"],
    "time-scaled h-index": [False, FLOAT, "time-scaled h-index (hTS)",
                            "time-scaled <em>h-</em>index (<em>h<sup>TS</sup></em>)"],
    "alpha-index": [False, FLOAT, "α-index", "<em>α-</em>index"],
    "ar-index": [False, FLOAT, "ar-index", "<em>ar-</em>index"],
    "dynamic h-type-index": [False, FLOAT_NEG, "dynamic h-type-index", "dynamic <em>h-</em>type-index"],
    "hpd-index": [False, INT, "hpd-index", "<em>hpd-</em>index"],
    "contemporary h-index": [False, INT, "contemporary h-index", "contemporary <em>h-</em>index"],
    "trend h-index": [False, INT, "trend h-index", "trend <em>h-</em>index"],
    "impact vitality": [False, FLOAT_NEG, "impact vitality"],
    "specific impact s-index": [False, FLOAT, "specific impact s-index", "specific impact <em>s-</em>index"],
    "Franceschini f-index": [False, INT, "f-index (Franceschini & Maisano)",
                             "<em>f-</em>index (Franceschini &amp; Maisano)"],
    "time-scaled num papers": [False, FLOAT, "time-scaled number of publications (PTS)",
                               "time-scaled number of publications (<em>P<sup>TS</sup></em>)"],
    "time-scaled num citations": [False, FLOAT, "time-scaled citation index (CTS)",
                                  "time-scaled citation index (<em>C<sup>TS</sup></em>)"],
    "annual h-index": [False, FLOAT, "annual h-index (hIa)", "annual <em>h</em>-index (hIa)"],
    "CDS-index": [False, INT, "citation distribution score index (CDS-index)"],
    "CDR-index": [False, FLOAT, "citation distribution rate index (CDR-index)"],
    "circ cite area radius": [False, FLOAT, "circular citation area radius"],
    "citation acceleration": [False, FLOAT, "citation acceleration"],
    "median cites per pub": [False, FLOAT, "median citations per pub"],
    "Redner index": [False, FLOAT, "Redner index"],
    "Levene j-index": [False, FLOAT, "Levene j-index", "Levene <em>j-</em>index"],
    "S-index (h-mixed)": [False, FLOAT, "S-index (h-mixed synthetic index)",
                          "<em>S-</em>index (<em>h-</em>mixed synthetic index)"],
    "T-index (h-mixed)": [False, FLOAT, "T-index (h-mixed synthetic index)",
                          "<em>T-</em>index (<em>h-</em>mixed synthetic index)"],
    "citation entropy": [False, FLOAT, "citation entropy (s-index)", "citation entropy (<em>s-</em>index)"],
    "cq index": [False, FLOAT, "corrected quality ratio (CQ index)", "corrected quality ratio (<em>CQ</em> index)"],
    "cq0.4 index": [False, FLOAT, "CQ0.4 index", "CQ<sup>0.4</sup> index)"],

"""


if __name__ == "__main__":
    # simple test
    new_set = MetricSet()
    new_set.citations = [100, 20, 5, 1, 1]
    for i in new_set.metrics:
        metric = new_set.metrics[i]
        print(metric.value)
