# metric definitions for impact factor calculator

import Impact_Funcs
import datetime
from typing import Union

# --- Internal Constants ---
INT = 0
FLOAT = 1
INTLIST = 2
FLOAT_NA = 3
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
        elif self.metric_type == FLOAT_NA:
            if self.value == "n/a":
                return self.value
            else:
                return format(self.value, FSTR)


class MetricSet:
    """
    This class contains all of the metric output for a single year,
    as well as data used to calculate these metrics
    """
    def __init__(self):
        self.date = datetime.date(1970, 1, 1)
        self.citations = []  # number of citations for each pub, ordered by input
        self.rank_order = []  # rank of each pub, from most citations to fewest
        self.cumulative_citations = []  # cumulative number of citations per top i pubs, in order by rank
        self.median_citations = []  # median number of citations per top i pubs, in order by rank
        self.is_core = []  # boolean indicator of whether a pub is part of the h-core
        self.self_citations = None  # of self citations of each publication, in same order as citations
        self.coauthor_citations = None  # of coauthor citations of each publication, in same order as citations
        self.first_pub_year = None
        self.publications = []
        self.parent_list = None
        # add all defined metrics
        tmp_list = load_all_metrics()
        self.metrics = {m.name: m for m in tmp_list}
        for m in self.metrics:
            self.metrics[m].parent_set = self  # cross-point this set as parent of each child metric object
        self.metric_names = [m.name for m in tmp_list]

    def calculate_ranks(self) -> None:
        """
        given a list of citation totals for each pub, fill in various other lists of ranks and counts and
        flags used to calculate metrics
        """
        n = len(self.citations)
        self.is_core = [False for _ in range(n)]
        (self.rank_order,
         self.cumulative_citations,
         self.median_citations) = Impact_Funcs.calculate_ranks(self.citations)

    def academic_age(self) -> int:
        """
        number of years since author began publishing
        """
        if self.first_pub_year is None:
            return 0
        else:
            return self.date.year - self.first_pub_year + 1

    def sorted_citations(self) -> list:
        """
        returns the citation counts sorted from highest to lowest (rather than by pub order)
        """
        return sorted(self.citations, reverse=True)

    def self_coauthor_citations(self) -> list:
        """
        returns a list containing the sum of both self and coauthor citations for all pubs
        """
        return [self.self_citations[i] + self.coauthor_citations[i] for i in range(len(self.self_citations))]

    def author_counts(self) -> list:
        """
        returns a list with the count of authors for each pub
        """
        return [p.authors for p in self.publications]

    def author_position(self) -> list:
        """
        returns a list with the position of the author within the author list for each pub
        """
        return [p.author_rank for p in self.publications]

    def publication_years(self) -> list:
        """
        returns a list containing the publication year of each publication, in the same order as citations
        """
        return [p.year for p in self.publications]

    def year(self) -> int:
        return self.date.year


# --- Definitions and Calculations for Individual Metrics---
"""
the calculation functions in this section are designed to extract the key data from the MetricSet(s) and
send it to an identically named function in the Impact_Funcs module which is designed with more generic
data input in mind.

although slightly redundant in design, it allows the functions in the Impact_Func module to be used more
generally outside this specific code, if necessary
"""


# total publications
def calculate_total_pubs(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_total_pubs(metric_set.citations)


def metric_total_pubs() -> Metric:
    m = Metric()
    m.name = "total pubs"
    m.full_name = "total publications"
    m.metric_type = INT
    m.description = "<p>This metric is the total number of publications by an author.</p>"
    m.calculate = calculate_total_pubs
    return m


# total citations
def calculate_total_cites(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_total_cites(metric_set.citations)


def metric_total_cites() -> Metric:
    m = Metric()
    m.name = "total cites"
    m.full_name = "total citations"
    m.metric_type = INT
    m.description = "<p>This metric is the total number of citations to all publications by an author.</p>"
    m.calculate = calculate_total_cites
    return m


# maximum citations
def calculate_max_cites(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_max_cites(metric_set.citations)


def metric_max_cites() -> Metric:
    m = Metric()
    m.name = "max cites"
    m.full_name = "maximum citations"
    m.metric_type = INT
    m.description = "<p>This metric is the largest number of citations found for a single publication by an author.</p>"
    m.calculate = calculate_max_cites
    return m


# mean citations
def calculate_mean_cites(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_mean_cites(total_cites, total_pubs)


def metric_mean_cites() -> Metric:
    m = Metric()
    m.name = "c/p"
    m.full_name = "mean citations per publication (C/P index)"
    m.html_name = "mean citations per publication (<em>C/P</em> index)"
    m.metric_type = FLOAT
    m.description = "<p>This metric is the mean number of citations per publication. It has been described under " \
                    "many names, including the <em>C/P</em> index, the mean citation rate (<em>MCR</em>), the mean " \
                    "observed citation rate (<em>MOCR</em>), citations per publication (<em>CPP</em>), the observed " \
                    "citation rate (<em>OCR</em>), the generalized impact factor (<em>I<sub>f</sub></em>), and the " \
                    "journal paper citedness (<em>JPC</em>).</p>"
    m.calculate = calculate_mean_cites
    return m


# median citations
def calculate_median_cites(metric_set: MetricSet) -> float:
    median_list = metric_set.median_citations
    return Impact_Funcs.calculate_median_cites(median_list)


def metric_median_cites() -> Metric:
    m = Metric()
    m.name = "median cites per pub"
    m.full_name = "median citations per publication"
    m.metric_type = FLOAT
    m.description = "<p>This metric is the median number of citations per publication.</p>"
    m.calculate = calculate_median_cites
    return m


# pubs per year
def calculate_pubs_per_year(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_pubs_per_year(total_pubs, age)


def metric_pubs_per_year() -> Metric:
    m = Metric()
    m.name = "pubs per year"
    m.full_name = "publications per year (PTS)"
    m.html_name = "publications per year (<em>P<sup>TS</sup></em>)"
    m.metric_type = FLOAT
    m.description = "<p>... a.k.a. time-scaled number of publications...</p>"
    m.calculate = calculate_pubs_per_year
    return m


# citations per year
def calculate_cites_per_year(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_cites_per_year(total_cites, age)


def metric_cites_per_year() -> Metric:
    m = Metric()
    m.name = "citations per year"
    m.full_name = "citations per year (CTS)"
    m.html_name = "citations per year (<em>C<sup>TS</sup></em>)"
    m.metric_type = FLOAT
    m.description = "<p>...a.k.a. time-scaled citation index...</p>"
    m.calculate = calculate_cites_per_year
    return m


# h-index (Hirsch )
def calculate_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    metric_set.is_core = is_core
    return h


def metric_h_index() -> Metric:
    m = Metric()
    m.name = "h-index"
    m.full_name = "h-index"
    m.html_name = "<em>h-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_h_index
    return m


# Hirsch core citations (Hirsch )
def calculate_h_core(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    is_core = metric_set.is_core
    return Impact_Funcs.calculate_h_core(citations, is_core)


def metric_h_core() -> Metric:
    m = Metric()
    m.name = "h-core cites"
    m.full_name = "Hirsch core citations"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_h_core
    return m


# Hirsch minimum constant (Hirsch )
def calculate_hirsch_min_const(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_hirsch_min_const(total_cites, h)


def metric_hirsch_min_const() -> Metric:
    m = Metric()
    m.name = "Hirsch min const"
    m.full_name = "Hirsch Min Constant (a)"
    m.html_name = "Hirsch Min Constant (<em>a</em>)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_hirsch_min_const
    return m


# g-index (Egghe 2006)
def calculate_g_index(metric_set: MetricSet) -> int:
    cumulative_citations = metric_set.cumulative_citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_g_index(cumulative_citations, rank_order)


def metric_g_index() -> Metric:
    m = Metric()
    m.name = "g-index"
    m.full_name = "g-index"
    m.html_name = "<em>g-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_g_index
    return m


# h2-index (Kosmulski 2006)
def calculate_h2_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_h2_index(citations, rank_order)


def metric_h2_index() -> Metric:
    m = Metric()
    m.name = "h(2)-index"
    m.full_name = "h(2)-index"
    m.html_name = "<em>h</em>(2)-index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_h2_index
    return m


# mu-index (Glanzel and Schubert 2010)
def calculate_mu_index(metric_set: MetricSet) -> int:
    median_list = metric_set.median_citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_mu_index(rank_order, median_list)


def metric_mu_index() -> Metric:
    m = Metric()
    m.name = "mu-index"
    m.full_name = "μ-index"
    m.html_name = "<em>μ-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_mu_index
    return m


# Tol's f-index (Tol 2007)
def calculate_tol_f_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_tol_f_index(citations)


def metric_tol_f_index() -> Metric:
    m = Metric()
    m.name = "Tol f-index"
    m.full_name = "f-index (Tol)"
    m.html_name = "<em>f-</em>index (Tol)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_tol_f_index
    return m


# Tol's t-index (Tol 2007)
def calculate_tol_t_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_tol_t_index(citations)


def metric_tol_t_index() -> Metric:
    m = Metric()
    m.name = "Tol t-index"
    m.full_name = "t-index (Tol)"
    m.html_name = "<em>t-</em>index (Tol)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_tol_t_index
    return m


# Woeginger w-index (Woeginger 2008)
def calculate_woeginger_w_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_woeginger_w(citations, rank_order)


def metric_woeginger_w_index() -> Metric:
    m = Metric()
    m.name = "Woeginger w-index"
    m.full_name = "w-index (Woeginger)"
    m.html_name = "<em>w-</em>index (Woeginger)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_woeginger_w_index
    return m


# Wu w-index (Wu 2010)
def calculate_wu_w_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_wu_w_index(citations, rank_order)


def metric_wu_w_index() -> Metric:
    m = Metric()
    m.name = "Wu w-index"
    m.full_name = "w-index (Wu)"
    m.html_name = "<em>w-</em>index (Wu)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_wu_w_index
    return m


# Wu w(q) (Wu 2010)
def calculate_wu_wq(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    w = metric_set.metrics["Wu w-index"].value
    return Impact_Funcs.calculate_wu_wq(citations, rank_order, w)


def metric_wu_wq() -> Metric:
    m = Metric()
    m.name = "Wu w(q)"
    m.full_name = "w(q) (Wu)"
    m.html_name = "<em>w</em>(<em>q</em>) (Wu)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_wu_wq
    return m


# hg-index (Alonso et al 2010)
def calculate_hg_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    g = metric_set.metrics["g-index"].value
    return Impact_Funcs.calculate_hg_index(h, g)


def metric_hg_index() -> Metric:
    m = Metric()
    m.name = "hg-index"
    m.full_name = "hg-index"
    m.html_name = "<em>hg-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_hg_index
    return m


# a-index (Jin 2006; Rousseau 2006)
def calculate_a_index(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_a_index(core_cites, total_pubs)


def metric_a_index() -> Metric:
    m = Metric()
    m.name = "a-index"
    m.full_name = "a-index"
    m.html_name = "<em>a-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_a_index
    return m


# R-index (Jin et al 2007)
def calculate_r_index(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    return Impact_Funcs.calculate_r_index(core_cites)


def metric_r_index() -> Metric:
    m = Metric()
    m.name = "R-index"
    m.full_name = "R-index"
    m.html_name = "<em>R-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_r_index
    return m


# indifference (Egghe and Rousseau 1996)
def calculate_indifference(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_indifference(total_cites, total_pubs)


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


# rational h-index (Ruane and Tol 2008)
def calculate_rational_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    is_core = metric_set.is_core
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_rational_h(citations, rank_order, is_core, h)


def metric_rational_h_index() -> Metric:
    m = Metric()
    m.name = "rational h-index"
    m.full_name = "rational h-index"
    m.html_name = "rational <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_rational_h_index
    return m


# real h-index (hr-index) (Guns and Rousseau 2009)
def calculate_real_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_real_h_index(citations, rank_order, h)


def metric_real_h_index() -> Metric:
    m = Metric()
    m.name = "real h-index"
    m.full_name = "real h-index"
    m.html_name = "real <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_real_h_index
    return m


# tapered h-index (Anderson et al 2008)
def calculate_tapered_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_tapered_h_index(citations, rank_order)


def metric_tapered_h_index() -> Metric:
    m = Metric()
    m.name = "tapered h-index"
    m.full_name = "tapered h-index"
    m.html_name = "tapered <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_tapered_h_index
    return m


# j-index (Todeschini 2011)
def calculate_todeschini_j_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_todeschini_j_index(citations, h)


def metric_todeschini_j_index() -> Metric:
    m = Metric()
    m.name = "Todeschini j-index"
    m.full_name = "j-index (Todeschini)"
    m.html_name = "<em>j-</em>index (Todeschini))"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_todeschini_j_index
    return m


# Wohlin w-index (Wohlin 2009)
def calculate_wohlin_w_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    max_cites = metric_set.metrics["max cites"].value
    return Impact_Funcs.calculate_wohlin_w(citations, max_cites)


def metric_wohlin_w_index() -> Metric:
    m = Metric()
    m.name = "Wohlin w-index"
    m.full_name = "w-index (Wohlin)"
    m.html_name = "<em>w-</em>index (Wohlin)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_wohlin_w_index
    return m


# hj-indices (Dorta-Gonzalez and Dorta-Gonzalez 2010)
def calculate_hj_indices(metric_set: MetricSet) -> list:
    # citations = metric_set.citations
    total_pubs = metric_set.metrics["total pubs"].value
    h = metric_set.metrics["h-index"].value
    sorted_citations = metric_set.sorted_citations()
    return Impact_Funcs.calculate_hj_indices(total_pubs, h, sorted_citations)


def metric_hj_indices() -> Metric:
    m = Metric()
    m.name = "hj-indices"
    m.full_name = "hj-indices"
    m.html_name = "<em>hj-</em>indices"
    m.metric_type = INTLIST
    m.description = "<p>...</p>"
    m.calculate = calculate_hj_indices
    return m


# v-index (Riikonen and Vihinen 2008)
def calculate_v_index(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_v_index(h, total_pubs)


def metric_v_index() -> Metric:
    m = Metric()
    m.name = "v-index"
    m.full_name = "v-index"
    m.html_name = "<em>v-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_v_index
    return m


# normalized h-index (Sidiropoulos et al 2007)
def calculate_normalized_h_index(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_normalized_h_index(h, total_pubs)


def metric_normalized_h_index() -> Metric:
    m = Metric()
    m.name = "normalized h-index"
    m.full_name = "normalized h-index"
    m.html_name = "normalized <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_normalized_h_index
    return m


# m-index (median index) (Bornmann et al 2008)
def calculate_m_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    is_core = metric_set.is_core
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_m_index(citations, is_core, h)


def metric_m_index() -> Metric:
    m = Metric()
    m.name = "m-index"
    m.full_name = "m-index"
    m.html_name = "<em>m-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_m_index
    return m


# rm-index (Panaretos and Malesios 2009)
def calculate_rm_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    is_core = metric_set.is_core
    return Impact_Funcs.calculate_rm_index(citations, is_core)


def metric_rm_index() -> Metric:
    m = Metric()
    m.name = "rm-index"
    m.full_name = "rm-index"
    m.html_name = "<em>rm-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_rm_index
    return m


# weighted h-index (Egghe and Rousseau 2008)
def calculate_weighted_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    cumulative_citations = metric_set.cumulative_citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_weighted_h_index(citations, cumulative_citations, rank_order, h)


def metric_weighted_h_index() -> Metric:
    m = Metric()
    m.name = "weighted h-index"
    m.full_name = "weighted h-index"
    m.html_name = "weighted <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_weighted_h_index
    return m


# pi-index (Vinkler 2009)
def calculate_pi_index(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_pi_index(total_pubs, citations, rank_order)


def metric_pi_index() -> Metric:
    m = Metric()
    m.name = "pi-index"
    m.full_name = "π-index"
    m.html_name = "<em>π-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_pi_index
    return m


# q2-index (Cabrerizo et al 2010)
def calculate_q2_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    m = metric_set.metrics["m-index"].value
    return Impact_Funcs.calculate_q2_index(h, m)


def metric_q2_index() -> Metric:
    m = Metric()
    m.name = "q2-index"
    m.full_name = "q2-index"
    m.html_name = "<em>q</em><sup>2</sup>-index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_q2_index
    return m


# e-index (Zhang 2009)
def calculate_e_index(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_e_index(core_cites, h)


def metric_e_index() -> Metric:
    m = Metric()
    m.name = "e-index"
    m.full_name = "e-index"
    m.html_name = "<em>e-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_e_index
    return m


# maxprod (Kosmulski 2007)
def calculate_maxprod_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_maxprod_index(citations, rank_order)


def metric_maxprod_index() -> Metric:
    m = Metric()
    m.name = "maxprod-index"
    m.full_name = "maxprod-index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_maxprod_index
    return m


# h2-upper index (Bornmann et al 2010)
def calculate_h2_upper_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_h2_upper_index(total_cites, core_cites, h)


def metric_h2_upper_index() -> Metric:
    m = Metric()
    m.name = "h2-upper index"
    m.full_name = "h2-upper index"
    m.html_name = "<em>h</em><sup>2</sup>-upper index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_h2_upper_index
    return m


# h2-center index (Bornmann et al 2010)
def calculate_h2_center_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_h2_center_index(total_cites, h)


def metric_h2_center_index() -> Metric:
    m = Metric()
    m.name = "h2-center index"
    m.full_name = "h2-center index"
    m.html_name = "<em>h</em><sup>2</sup>-center index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_h2_center_index
    return m


# h2-tail index (Bornmann et al 2010)
def calculate_h2_tail_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    return Impact_Funcs.calculate_h2_tail_index(total_cites, core_cites)


def metric_h2_tail_index() -> Metric:
    m = Metric()
    m.name = "h2-tail index"
    m.full_name = "h2-tail index"
    m.html_name = "<em>h</em><sup>2</sup>-tail index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_h2_tail_index
    return m


# k-index (Ye and Rousseau 2010)
def calculate_k_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_k_index(total_cites, core_cites, total_pubs)


def metric_k_index() -> Metric:
    m = Metric()
    m.name = "k-index"
    m.full_name = "k-index"
    m.html_name = "<em>k-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_k_index
    return m


# Prathap p-index (originally called mock hm-index) (Prathap 2010b, 2011)
def calculate_prathap_p_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_prathap_p_index(total_cites, total_pubs)


def metric_prathap_p_index() -> Metric:
    m = Metric()
    m.name = "p-index"
    m.full_name = "p-index"
    m.html_name = "<em>p-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_prathap_p_index
    return m


# ph-ratio (Prathap 2010b, 2011)
def calculate_ph_ratio(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    p = metric_set.metrics["p-index"].value
    return Impact_Funcs.calculate_ph_ratio(p, h)


def metric_ph_ratio() -> Metric:
    m = Metric()
    m.name = "ph-ratio"
    m.full_name = "ph-ratio"
    m.html_name = "<em>ph-</em>ratio"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_ph_ratio
    return m


# fractional p-index (pf) (Prathap 2010b, 2011)
def calculate_p_index_frac(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_fractional_p_index(citations, n_authors)


def metric_p_index_frac() -> Metric:
    m = Metric()
    m.name = "fractional p-index"
    m.full_name = "fractional p-index"
    m.html_name = "fractional <em>p-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_p_index_frac
    return m


# multidimensional h-index (Garcia-Perez 2009)
def calculate_multidimensional_h_index(metric_set: MetricSet) -> list:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    is_core = metric_set.is_core
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_multidimensional_h_index(citations, rank_order, is_core, h)


def metric_multdim_h_index() -> Metric:
    m = Metric()
    m.name = "multidim h-index"
    m.full_name = "multidimensional h-index"
    m.html_name = "multidimensional <em>h-</em>index"
    m.metric_type = INTLIST
    m.description = "<p>...</p>"
    m.calculate = calculate_multidimensional_h_index
    return m


# two-sided h-index (Garcia-Perez 2012)
def calculate_two_sided_h_index(metric_set: MetricSet) -> list:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    h = metric_set.metrics["h-index"].value
    multidim_h = metric_set.metrics["multidim h-index"].value
    return Impact_Funcs.calculate_two_sided_h(citations, rank_order, h, multidim_h)


def metric_two_sided_h_index() -> Metric:
    m = Metric()
    m.name = "two-sided h-index"
    m.full_name = "two-sided h-index"
    m.html_name = "two-sided <em>h-</em>index"
    m.metric_type = INTLIST
    m.description = "<p>...</p>"
    m.calculate = calculate_two_sided_h_index
    return m


# iteratively weighted h-index (Todeschini and Baccini 2016)
def calculate_iter_weighted_h_index(metric_set: MetricSet) -> float:
    multidim_h = metric_set.metrics["multidim h-index"].value
    return Impact_Funcs.calculate_iteratively_weighted_h_index(multidim_h)


def metric_iter_weighted_h_index() -> Metric:
    m = Metric()
    m.name = "iter weighted h-index"
    m.full_name = "iteratively weighted p-index"
    m.html_name = "iteratively weighted <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_iter_weighted_h_index
    return m


# EM-index (Bihari and Tripathi 2017)
def calculate_em_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_em_index(citations, rank_order)


def metric_em_index() -> Metric:
    m = Metric()
    m.name = "EM-index"
    m.full_name = "EM-index"
    m.html_name = "<em>EM-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_em_index
    return m


# EM'-index (Bihari and Tripathi 2017)
def calculate_emp_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_emp_index(citations, rank_order)


def metric_emp_index() -> Metric:
    m = Metric()
    m.name = "EMp-index"
    m.full_name = "EM\'-index"
    m.html_name = "<em>EM</em>'-index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_emp_index
    return m


# total self citations
def calculate_total_self_cites(metric_set: MetricSet) -> int:
    self_citations = metric_set.self_citations
    return Impact_Funcs.calculate_total_self_cites(self_citations)


def metric_total_self_cites() -> Metric:
    m = Metric()
    m.name = "total self cites"
    m.full_name = "total self citations"
    m.metric_type = INT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_total_self_cites
    return m


# total self-citation rate
def calculate_total_self_cite_rate(metric_set: MetricSet) -> float:
    total_self_cites = metric_set.metrics["total self cites"].value
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_total_self_cite_rate(total_self_cites, total_cites)


def metric_total_self_cite_rate() -> Metric:
    m = Metric()
    m.name = "total self cite rate"
    m.full_name = "total self-citation rate"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_total_self_cite_rate
    return m


# mean self-citation rate
def calculate_mean_self_cite_rate(metric_set: MetricSet) -> float:
    all_citations = metric_set.citations
    self_citations = metric_set.self_citations
    return Impact_Funcs.calculate_mean_self_cite_rate(self_citations, all_citations)


def metric_mean_self_cite_rate() -> Metric:
    m = Metric()
    m.name = "mean self cite rate"
    m.full_name = "mean self-citation rate"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_mean_self_cite_rate
    return m


# sharpened h-index (Schreiber 2007)
def calculate_sharpened_h_index_self(metric_set: MetricSet) -> float:
    all_citations = metric_set.citations
    self_citations = metric_set.self_citations
    return Impact_Funcs.calculate_sharpened_h_index(self_citations, all_citations)


def metric_sharpened_h_index_self() -> Metric:
    m = Metric()
    m.name = "sharpened h-index (self)"
    m.full_name = "sharpened h-index (self)"
    m.html_name = "sharpened <em>h-</em>index (self)"
    m.metric_type = INT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_sharpened_h_index_self
    return m


# b-index (Brown 2009)
def calculate_b_index_mean_self(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    mean_rate = 1 - metric_set.metrics["mean self cite rate"].value
    return Impact_Funcs.calculate_b_index(h, mean_rate)


def metric_b_index_mean_self() -> Metric:
    m = Metric()
    m.name = "b-index mean self"
    m.full_name = "b-index (mean self-citation rate)"
    m.html_name = "<em>b-</em>index (mean self-citation rate)"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_b_index_mean_self
    return m


# total self & coauthor citations
def calculate_total_coauthor_cites(metric_set: MetricSet) -> int:
    coauthor_citations = metric_set.self_coauthor_citations()
    return Impact_Funcs.calculate_total_self_cites(coauthor_citations)


def metric_total_coauthor_cites() -> Metric:
    m = Metric()
    m.name = "total coauthor cites"
    m.full_name = "total self & coauthor citations"
    m.html_name = "total self &amp; coauthor citations"
    m.metric_type = INT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_total_coauthor_cites
    return m


# total self & coauthor-citation rate
def calculate_total_coauthor_cite_rate(metric_set: MetricSet) -> float:
    total_coauthor_cites = metric_set.metrics["total coauthor cites"].value
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_total_self_cite_rate(total_coauthor_cites, total_cites)


def metric_total_coauthor_cite_rate() -> Metric:
    m = Metric()
    m.name = "total coauthor cite rate"
    m.full_name = "total self & coauthor-citation rate"
    m.html_name = "total self &amp; coauthor-citation rate"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_total_coauthor_cite_rate
    return m


# mean self & coauthor-citation rate
def calculate_mean_coauthor_cite_rate(metric_set: MetricSet) -> float:
    all_citations = metric_set.citations
    coauthor_citations = metric_set.self_coauthor_citations()
    return Impact_Funcs.calculate_mean_self_cite_rate(coauthor_citations, all_citations)


def metric_mean_coauthor_cite_rate() -> Metric:
    m = Metric()
    m.name = "mean coauthor cite rate"
    m.full_name = "mean coauthor & self-citation rate"
    m.html_name = "mean coauthor &amp; self-citation rate"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_mean_coauthor_cite_rate
    return m


# sharpened h-index (Schreiber 2007)
def calculate_sharpened_h_index_coauthor(metric_set: MetricSet) -> float:
    all_citations = metric_set.citations
    coauthor_citations = metric_set.self_coauthor_citations()
    return Impact_Funcs.calculate_sharpened_h_index(coauthor_citations, all_citations)


def metric_sharpened_h_index_coauthor() -> Metric:
    m = Metric()
    m.name = "sharpened h-index (coauthor)"
    m.full_name = "sharpened h-index (self & coauthor)"
    m.html_name = "sharpened <em>h-</em>index (self &amp; coauthor)"
    m.metric_type = INT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_sharpened_h_index_coauthor
    return m


# b-index (Brown 2009)
def calculate_b_index_mean_coauthor(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    mean_rate = 1 - metric_set.metrics["mean coauthor cite rate"].value
    return Impact_Funcs.calculate_b_index(h, mean_rate)


def metric_b_index_mean_coauthor() -> Metric:
    m = Metric()
    m.name = "b-index mean coauthor"
    m.full_name = "b-index (mean self & coauthor-citation rate)"
    m.html_name = "<em>b-</em>index (mean self &amp; coauthor-citation rate)"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_b_index_mean_coauthor
    return m


# b-index (Brown 2009)
def calculate_b_index_10_percent(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_b_index(h, 0.9)


def metric_b_index_10_percent() -> Metric:
    m = Metric()
    m.name = "b-index 10%"
    m.full_name = "b-index (10% rate)"
    m.html_name = "<em>b-</em>index (10% rate)"
    m.metric_type = FLOAT
    m.is_self = True
    m.description = "<p>...</p>"
    m.calculate = calculate_b_index_10_percent
    return m


# hi-index (Batista et al 2006)
def calculate_hi_index(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_hi_index(is_core, n_authors, h)


def metric_hi_index() -> Metric:
    m = Metric()
    m.name = "hi-index"
    m.full_name = "hi-index "
    m.html_name = "<em>h<sub>i</sub>-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_hi_index
    return m


# fractional pure h-index (Wan et al 2007)
def calculate_pure_h_index_frac(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h)


def metric_pure_h_index_frac() -> Metric:
    m = Metric()
    m.name = "pure h-index frac"
    m.full_name = "pure h-index (fractional credit)"
    m.html_name = "pure <em>h-</em>index (fractional credit)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_pure_h_index_frac
    return m


# proportional pure h-index (Wan et al 2007)
def calculate_pure_h_index_prop(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h)


def metric_pure_h_index_prop() -> Metric:
    m = Metric()
    m.name = "pure h-index prop"
    m.full_name = "pure h-index (proportional credit)"
    m.html_name = "pure <em>h-</em>index (proportional credit)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_pure_h_index_prop
    return m


# geometric pure h-index (Wan et al 2007)
def calculate_pure_h_index_geom(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_pure_h_index_geom(is_core, n_authors, author_pos, h)


def metric_pure_h_index_geom() -> Metric:
    m = Metric()
    m.name = "pure h-index geom"
    m.full_name = "pure h-index (geometric credit)"
    m.html_name = "pure <em>h-</em>index (geometric credit)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_pure_h_index_geom
    return m


# fractional adapted pure h-index (Chai et al 2008)
def calculate_adapt_pure_h_index_frac(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_adapt_pure_h_index_frac(citations, n_authors)


def metric_adapt_pure_h_index_frac() -> Metric:
    m = Metric()
    m.name = "adapt pure h-index frac"
    m.full_name = "adapted pure h-index (fractional credit)"
    m.html_name = "adapted pure <em>h-</em>index (fractional credit)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_adapt_pure_h_index_frac
    return m


# proportional adapted pure h-index (Chai et al 2008)
def calculate_adapt_pure_h_index_prop(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_adapt_pure_h_index_prop(citations, n_authors, author_pos)


def metric_adapt_pure_h_index_prop() -> Metric:
    m = Metric()
    m.name = "adapt pure h-index prop"
    m.full_name = "adapted pure h-index (proportional credit)"
    m.html_name = "adapted pure <em>h-</em>index (proportional credit)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_adapt_pure_h_index_prop
    return m


# geometric adapted pure h-index (Chai et al 2008)
def calculate_adapt_pure_h_index_geom(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_adapt_pure_h_index_geom(citations, n_authors, author_pos)


def metric_adapt_pure_h_index_geom() -> Metric:
    m = Metric()
    m.name = "adapt pure h-index geom"
    m.full_name = "adapted pure h-index (geometric credit)"
    m.html_name = "adapted pure <em>h-</em>index (geometric credit)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_adapt_pure_h_index_geom
    return m


# harmonic p-index (Prathap 2011)
def calculate_p_index_harm(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_harmonic_p_index(citations, n_authors, author_pos)


def metric_p_index_harm() -> Metric:
    m = Metric()
    m.name = "harmonic p-index"
    m.full_name = "harmonic p-index"
    m.html_name = "harmonic <em>p-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_p_index_harm
    return m


# profit p-index (Aziz and Rozing 2013)
def calculate_profit_p_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_profit_p_index(citations, n_authors, author_pos)


def metric_profit_p_index() -> Metric:
    m = Metric()
    m.name = "profit p-index"
    m.full_name = "profit p-index"
    m.html_name = "profit <em>p-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_profit_p_index
    return m


# profit adjusted h-index (Aziz and Rozing 2013)
def calculate_profit_adj_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_profit_adj_h_index(citations, n_authors, author_pos)


def metric_profit_adj_h_index() -> Metric:
    m = Metric()
    m.name = "profit adj h-index"
    m.full_name = "profit adjusted h-index"
    m.html_name = "profit adjusted <em>h-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_profit_adj_h_index
    return m


# profit h-index (Aziz and Rozing 2013)
def calculate_profit_h_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    profit_adj_h = metric_set.metrics["profit adj h-index"].value
    return Impact_Funcs.calculate_profit_h_index(profit_adj_h, h)


def metric_profit_h_index() -> Metric:
    m = Metric()
    m.name = "profit h-index"
    m.full_name = "profit h-index"
    m.html_name = "profit <em>h-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_profit_h_index
    return m


# normalized hi-index/hf-index (Wohlin 2009)
def calculate_normal_hi_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_normal_hi_index(citations, n_authors)


def metric_normal_hi_index() -> Metric:
    m = Metric()
    m.name = "normal hi-index"
    m.full_name = "normalized hi-index"
    m.html_name = "normalized <em>h<sub>i</sub>-</em>index"
    m.metric_type = INT
    m.description = "<p>...a.k.a. <em>h<sub>f</sub>-</em>index</p>"
    m.calculate = calculate_normal_hi_index
    return m


# gf-index (citation based) (Egghe 2008)
def calculate_gf_cite_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_gf_cite_index(citations, n_authors)


def metric_gf_cite_index() -> Metric:
    m = Metric()
    m.name = "gf-cite"
    m.full_name = "gf-index"
    m.html_name = "<em>g<sub>f</sub>-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_gf_cite_index
    return m


# hm-index/hF-index (Schreiber 2008)
def calculate_hm_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_hm_index(citations, rank_order, n_authors)


def metric_hm_index() -> Metric:
    m = Metric()
    m.name = "hm-index"
    m.full_name = "hm-index"
    m.html_name = "<em>h<sub>m</sub>-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...a.k.a. <em>h<sub>F</sub>-</em>index</p>"
    m.calculate = calculate_hm_index
    return m


# gF-index (fractional paper) (Egghe 2008)
def calculate_gf_paper_index(metric_set: MetricSet) -> float:
    cumulative_citations = metric_set.cumulative_citations
    n_authors = metric_set.author_counts()
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_gf_paper_index(cumulative_citations, rank_order, n_authors)


def metric_gf_paper_index() -> Metric:
    m = Metric()
    m.name = "gf-paper"
    m.full_name = "gF-index"
    m.html_name = "<em>g<sub>F</sub>-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_gf_paper_index
    return m


# position-weighted h-index (Abbas 2011)
def calculate_pos_weight_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_position_weighted_h_index(citations, n_authors, author_pos)


def metric_pos_weight_h_index() -> Metric:
    m = Metric()
    m.name = "position-weighted h-index"
    m.full_name = "position-weighted h-index (hp)"
    m.html_name = "position-weighted <em>h-</em>index (<em>h<sub>p</sub></em>)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_pos_weight_h_index
    return m


# proportional weighted citation aggregate (Abbas 2011)
def calculate_prop_weight_cite_agg(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_prop_weight_cite_agg(citations, n_authors, author_pos)


def metric_prop_weight_cite_agg() -> Metric:
    m = Metric()
    m.name = "prop weight cite agg"
    m.full_name = "weighted citation aggregate (proportional)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_prop_weight_cite_agg
    return m


# proportional weighted citation h-cut (Abbas 2011)
def calculate_prop_weight_cite_h_cut(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_prop_weight_cite_h_cut(citations, n_authors, author_pos)


def metric_prop_weight_cite_h_cut() -> Metric:
    m = Metric()
    m.name = "prop weight cite h-cut"
    m.full_name = "weighted citation H-cut (proportional)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_prop_weight_cite_h_cut
    return m


# fractional weighted citation aggregate (Abbas 2011)
def calculate_frac_weight_cite_agg(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_frac_weight_cite_agg(citations, n_authors)


def metric_frac_weight_cite_agg() -> Metric:
    m = Metric()
    m.name = "frac weight cite agg"
    m.full_name = "weighted citation aggregate (fractional)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_frac_weight_cite_agg
    return m


# fractional weighted citation h-cut (Abbas 2011)
def calculate_frac_weight_cite_h_cut(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_frac_weight_cite_h_cut(citations, n_authors)


def metric_frac_weight_cite_h_cut() -> Metric:
    m = Metric()
    m.name = "frac weight cite h-cut"
    m.full_name = "weighted citation H-cut (fractional)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_frac_weight_cite_h_cut
    return m


# h-rate (Hirsch m-quotient)
def calculate_h_rate(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_h_rate(h, age)


def metric_h_rate() -> Metric:
    m = Metric()
    m.name = "h-rate"
    m.full_name = "h-rate/Hirsch m-quotient (slope)"
    m.html_name = "<em>h-</em>rate/Hirsch <em>m-</em>quotient (slope)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_h_rate
    return m


# least-squares h-rate
def calculate_ls_h_rate(metric_set: MetricSet) -> float:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    h_list = [m.metrics["h-index"].value for m in metric_list[:metric_pos+1]]
    year_list = [m.year() for m in metric_list[:metric_pos+1]]
    return Impact_Funcs.calculate_least_squares_h_rate(year_list, h_list)


def metric_ls_h_rate() -> Metric:
    m = Metric()
    m.name = "ls h-rate"
    m.full_name = "least squares h-rate (slope)"
    m.html_name = "least squares <em>h-</em>rate (slope)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_ls_h_rate
    return m


# time-scaled h-index (Todeschini and Baccini 2016)
def calculate_time_scaled_h_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_time_scaled_h_index(h, age)


def metric_time_scaled_h_index() -> Metric:
    m = Metric()
    m.name = "time-scaled h-index"
    m.full_name = "time-scaled h-index (hTS)"
    m.html_name = "time-scaled <em>h-</em>index (<em>h<sup>TS</sup></em>)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_time_scaled_h_index
    return m


# alpha index
def calculate_alpha_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_alpha_index(h, age)


def metric_alpha_index() -> Metric:
    m = Metric()
    m.name = "alpha-index"
    m.full_name = "α-index"
    m.html_name = "<em>α-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_alpha_index
    return m


# ar-index (Jin 2007; Jin et al 2007)
def calculate_ar_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    is_core = metric_set.is_core
    year = metric_set.year()
    return Impact_Funcs.calculate_ar_index(citations, pub_years, is_core, year)


def metric_ar_index() -> Metric:
    m = Metric()
    m.name = "ar-index"
    m.full_name = "ar-index"
    m.html_name = "<em>ar-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_ar_index
    return m


# dynamic h-type-index
def calculate_dynamic_h_type_index(metric_set: MetricSet) -> float:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    rational_h_list = [m.metrics["rational h-index"].value for m in metric_list[:metric_pos + 1]]
    date_list = [m.date for m in metric_list[:metric_pos + 1]]
    r = metric_set.metrics["R-index"].value
    return Impact_Funcs.calculate_dynamic_h_type_index(rational_h_list, date_list, r)


def metric_dynamic_h_type_index() -> Metric:
    m = Metric()
    m.name = "dynamic h-type-index"
    m.full_name = "dynamic h-type-index"
    m.html_name = "dynamic <em>h-</em>type-index"
    m.metric_type = FLOAT_NA
    m.description = "<p>...</p>"
    m.calculate = calculate_dynamic_h_type_index
    return m


# hpd-index (Kosmulski 2009)
def calculate_hpd_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    return Impact_Funcs.calculate_hpd_index(citations, pub_years, year)


def metric_hpd_index() -> Metric:
    m = Metric()
    m.name = "hpd-index"
    m.full_name = "hpd-index"
    m.html_name = "<em>hpd-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_hpd_index
    return m


# contemporary h-index (Sidiropoulos et al 2007)
def calculate_contemporary_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    return Impact_Funcs.calculate_contemporary_h_index(citations, pub_years, year)


def metric_contemporary_h_index() -> Metric:
    m = Metric()
    m.name = "contemporary h-index"
    m.full_name = "contemporary h-index"
    m.html_name = "contemporary <em>h-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_contemporary_h_index
    return m


# trend h-index
def calculate_trend_h_index(metric_set: MetricSet) -> int:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    return Impact_Funcs.calculate_trend_h_index(pub_data)


def metric_trend_h_index() -> Metric:
    m = Metric()
    m.name = "trend h-index"
    m.full_name = "trend h-index"
    m.html_name = "trend <em>h-</em>index"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_trend_h_index
    return m


# impact vitality
def calculate_impact_vitality(metric_set: MetricSet) -> Union[str, float]:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_list[:metric_pos+1]]
    return Impact_Funcs.calculate_impact_vitality(total_cite_list)


def metric_impact_vitality() -> Metric:
    m = Metric()
    m.name = "impact vitality"
    m.full_name = "impact vitality"
    m.metric_type = FLOAT_NA
    m.description = "<p>...</p>"
    m.calculate = calculate_impact_vitality
    return m


# specific impact s-index (De Visscher 2010)
def calculate_specific_impact_s_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    return Impact_Funcs.calculate_specific_impact_s_index(pub_years, year, total_cites)


def metric_specific_impact_s_index() -> Metric:
    m = Metric()
    m.name = "specific impact s-index"
    m.full_name = "specific impact s-index"
    m.html_name = "specific impact <em>s-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_specific_impact_s_index
    return m


# Franceschini f-index (Franceschini and Maisano 2010)
def calculate_franceschini_f_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    return Impact_Funcs.calculate_franceschini_f_index(citations, pub_years)


def metric_franceschini_f_index() -> Metric:
    m = Metric()
    m.name = "Franceschini f-index"
    m.full_name = "f-index (Franceschini & Maisano)"
    m.html_name = "<em>f-</em>index (Franceschini &amp; Maisano)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_franceschini_f_index
    return m


# annual h-index (hIa) (Harzing et al 2014)
def calculate_annual_h_index(metric_set: MetricSet) -> float:
    norm_h = metric_set.metrics["normal hi-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_annual_h_index(norm_h, age)


def metric_annual_h_index() -> Metric:
    m = Metric()
    m.name = "annual h-index"
    m.full_name = "annual h-index (hIa)"
    m.html_name = "annual <em>h</em>-index (hIa)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_annual_h_index
    return m


# CDS index (Vinkler 2011, 2013)
def calculate_cds_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_cds_index(citations)


def metric_cds_index() -> Metric:
    m = Metric()
    m.name = "CDS-index"
    m.full_name = "citation distribution score index (CDS-index)"
    m.metric_type = INT
    m.description = "<p>...</p>"
    m.calculate = calculate_cds_index
    return m


# CDR index (Vinkler 2011, 2013)
def calculate_cdr_index(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    cds = metric_set.metrics["CDS-index"].value
    return Impact_Funcs.calculate_cdr_index(total_pubs, cds)


def metric_cdr_index() -> Metric:
    m = Metric()
    m.name = "CDR-index"
    m.full_name = "citation distribution rate index (CDR-index)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_cdr_index
    return m


# circular citation area radius (Sangwal 2012)
def calculate_circ_cite_area_radius(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_circ_cite_area_radius(total_cites)


def metric_circ_cite_area_radius() -> Metric:
    m = Metric()
    m.name = "circ cite area radius"
    m.full_name = "circular citation area radius"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_circ_cite_area_radius
    return m


# citation acceleration (Sangwal 2012)
def calculate_citation_acceleration(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_citation_acceleration(total_cites, age)


def metric_citation_acceleration() -> Metric:
    m = Metric()
    m.name = "citation acceleration"
    m.full_name = "citation acceleration"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_citation_acceleration
    return m


# Render index (Redner 2010)
def calculate_redner_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_redner_index(total_cites)


def metric_redner_index() -> Metric:
    m = Metric()
    m.name = "Redner index"
    m.full_name = "Redner index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_redner_index
    return m


# Levene j-index (Levene et al 2012)
def calculate_levene_j_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_levene_j_index(citations)


def metric_levene_j_index() -> Metric:
    m = Metric()
    m.name = "Levene j-index"
    m.full_name = "Levene j-index"
    m.html_name = "Levene <em>j-</em>index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_levene_j_index
    return m


# h-mixed synthetic indices: S-index (Ye 2010)
def calculate_s_index_h_mixed(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    cpp = metric_set.metrics["c/p"].value
    return Impact_Funcs.calculate_s_index_h_mixed(h, cpp)


def metric_s_index_h_mixed() -> Metric:
    m = Metric()
    m.name = "S-index (h-mixed)"
    m.full_name = "S-index (h-mixed synthetic index)"
    m.html_name = "<em>S-</em>index (<em>h-</em>mixed synthetic index)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_s_index_h_mixed
    return m


# h-mixed synthetic indices: T-index (Ye 2010)
def calculate_t_index_h_mixed(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    cpp = metric_set.metrics["c/p"].value
    r = metric_set.metrics["R-index"].value
    return Impact_Funcs.calculate_t_index_h_mixed(h, cpp, r)


def metric_t_index_h_mixed() -> Metric:
    m = Metric()
    m.name = "T-index (h-mixed)"
    m.full_name = "T-index (h-mixed synthetic index)"
    m.html_name = "<em>T-</em>index (<em>h-</em>mixed synthetic index)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_t_index_h_mixed
    return m


# s-index / citation entropy p (Silagadze 2009)
def calculate_citation_entropy(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    citations = metric_set.citations
    return Impact_Funcs.calculate_citation_entropy(total_cites, citations)


def metric_citation_entropy() -> Metric:
    m = Metric()
    m.name = "citation entropy"
    m.full_name = "citation entropy (s-index)"
    m.html_name = "citation entropy (<em>s-</em>index)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_citation_entropy
    return m


# Corrected Quality ratios (Lindsay 1978)
def calculate_cq_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_cq_index(total_cites, total_pubs)


def metric_cq_index() -> Metric:
    m = Metric()
    m.name = "cq index"
    m.full_name = "corrected quality ratio (CQ index)"
    m.html_name = "corrected quality ratio (<em>CQ</em> index)"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_cq_index
    return m


# Corrected Quality ratios / 60:40 (Lindsay 1978)
def calculate_cq04_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_cq04_index(total_cites, total_pubs)


def metric_cq04_index() -> Metric:
    m = Metric()
    m.name = "cq0.4 index"
    m.full_name = "CQ0.4 index"
    m.html_name = "CQ<sup>0.4</sup> index"
    m.metric_type = FLOAT
    m.description = "<p>...</p>"
    m.calculate = calculate_cq04_index
    return m


# --- main initialization loop ---
def load_all_metrics() -> list:
    """
    function to create a list containing an instance of every metric
    """
    metric_list = [metric_total_pubs(),
                   metric_total_cites(),
                   metric_max_cites(),
                   metric_mean_cites(),
                   metric_median_cites(),
                   metric_pubs_per_year(),
                   metric_cites_per_year(),
                   metric_h_index(),
                   metric_h_core(),
                   metric_hirsch_min_const(),
                   metric_g_index(),
                   metric_tol_f_index(),
                   metric_tol_t_index(),
                   metric_mu_index(),
                   metric_woeginger_w_index(),
                   metric_h2_index(),
                   metric_wu_w_index(),
                   metric_hg_index(),
                   metric_a_index(),
                   metric_r_index(),
                   metric_rational_h_index(),
                   metric_real_h_index(),
                   metric_wu_wq(),
                   metric_tapered_h_index(),
                   metric_todeschini_j_index(),
                   metric_wohlin_w_index(),
                   metric_hj_indices(),
                   metric_v_index(),
                   metric_normalized_h_index(),
                   metric_m_index(),
                   metric_rm_index(),
                   metric_weighted_h_index(),
                   metric_pi_index(),
                   metric_q2_index(),
                   metric_e_index(),
                   metric_maxprod_index(),
                   metric_h2_upper_index(),
                   metric_h2_center_index(),
                   metric_h2_tail_index(),
                   metric_k_index(),
                   metric_prathap_p_index(),
                   metric_ph_ratio(),
                   metric_multdim_h_index(),
                   metric_two_sided_h_index(),
                   metric_iter_weighted_h_index(),
                   metric_em_index(),
                   metric_emp_index(),
                   metric_hi_index(),
                   metric_pure_h_index_frac(),
                   metric_pure_h_index_prop(),
                   metric_pure_h_index_geom(),
                   metric_adapt_pure_h_index_frac(),
                   metric_adapt_pure_h_index_prop(),
                   metric_adapt_pure_h_index_geom(),
                   metric_normal_hi_index(),
                   metric_hm_index(),
                   metric_pos_weight_h_index(),
                   metric_frac_weight_cite_agg(),
                   metric_prop_weight_cite_agg(),
                   metric_frac_weight_cite_h_cut(),
                   metric_prop_weight_cite_h_cut(),
                   metric_gf_cite_index(),
                   metric_gf_paper_index(),
                   metric_p_index_frac(),
                   metric_p_index_harm(),
                   metric_profit_p_index(),
                   metric_profit_adj_h_index(),
                   metric_profit_h_index(),
                   metric_total_self_cites(),
                   metric_total_self_cite_rate(),
                   metric_mean_self_cite_rate(),
                   metric_sharpened_h_index_self(),
                   metric_b_index_mean_self(),
                   metric_total_coauthor_cites(),
                   metric_total_coauthor_cite_rate(),
                   metric_mean_coauthor_cite_rate(),
                   metric_sharpened_h_index_coauthor(),
                   metric_b_index_mean_coauthor(),
                   metric_b_index_10_percent(),
                   metric_h_rate(),
                   metric_ls_h_rate(),
                   metric_time_scaled_h_index(),
                   metric_alpha_index(),
                   metric_ar_index(),
                   metric_dynamic_h_type_index(),
                   metric_hpd_index(),
                   metric_contemporary_h_index(),
                   metric_trend_h_index(),
                   metric_impact_vitality(),
                   metric_specific_impact_s_index(),
                   metric_franceschini_f_index(),
                   metric_annual_h_index(),
                   metric_cds_index(),
                   metric_cdr_index(),
                   metric_circ_cite_area_radius(),
                   metric_citation_acceleration(),
                   metric_redner_index(),
                   metric_levene_j_index(),
                   metric_s_index_h_mixed(),
                   metric_t_index_h_mixed(),
                   metric_citation_entropy(),
                   metric_cq_index(),
                   metric_cq04_index(),
                   metric_indifference()]
    return metric_list
