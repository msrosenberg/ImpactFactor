# Impact Factor Calculator
"""
This program is designed to calculate a large number of impact factors for
data collected over multiple years.

It now has two modes:

(1) It uses data pre-curated by the user (see below for the format).

(2) It attempst to retrieve data via Google Scholar. There are advantages,
disadvantages, and limitations to the second method, which works but is
still in early stages of development.
"""

import datetime
import math
import urllib.request
from typing import Tuple, Union

tb = '\t'
Number = Union[int, float]
INT = 0
FLOAT = 1
INTLIST = 2
FLOAT_NEG = 3

METRIC_NAMES = [
    "total pubs",
    "total cites",
    "cites per pub",
    "max cites",
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
    "time-scaled num papers",
    "time-scaled num citations",
    "annual h-index"
]

# [self-citing metric, output type, text title, html title (optional)]
METRIC_INFO = {
    "total pubs": [False, INT, "Total Publications"],
    "total cites": [False, INT, "Total Citations"],
    "cites per pub": [False, FLOAT, "Citations per Pub"],
    "max cites": [False, INT, "Max Citations"],
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
    "r-index": [False, FLOAT, "r-index", "<em>r-</em>index"],
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
    "ls h-rate": [False, FLOAT, "Least squares h-rate (slope)", "Least squares <em>h-</em>rate (slope)"],
    "time-scaled h-index": [False, FLOAT, "Time-scaled h-index (hTS)",
                            "Time-scaled <em>h-</em>index (<em>h<sup>TS</sup></em>)"],
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
    "annual h-index": [False, FLOAT, "annual h-index (hIa)", "annual <em>h</em>-index (hIa)"]
}

# these aren't really proper classes, but rather just simple
# multivariate data objects


class Article:
    def __init__(self):
        self.year = 0
        self.authors = 0
        self.authorrank = 0
        self.rank = 0
        self.title = ''
        self.citations = []
        self.selfcites = []
        self.coauthcites = []
        # for GoogleScholar
        self.authorList = []
        self.googleScholarURL = ''
        self.citationURL = ''
        self.citeList = []


class CitingArticle:
    def __init__(self):
        self.authos = []
        self.year = 0
        self.citations = 0


class MetricSet:
    def __init__(self):
        self.date = datetime.date(1970, 1, 1)
        self.cumulativeCites = []
        self.values = {}
        # self.totalPubs = 0
        # self.totalCites = 0
        # self.citesPerPub = 0
        # self.maxCites = 0
        # self.h_index = 0
        # self.Hirsch_minConst = 0
        # self.Hirsch_mQuotient = 0  # a.k.a. h-rate, age-normalized h-index (hN), and Carbon h-factor
        # self.coreCites = 0
        # self.g_index = 0
        # self.a_index = 0
        # self.h2_index = 0
        # self.hg_index = 0
        # self.q2_index = 0
        # self.r_index = 0
        # self.rm_index = 0
        # self.m_index = 0
        # self.ar_index = 0
        # self.h2_lower = 0
        # self.h2_center = 0
        # self.h2_upper = 0
        # self.Tol_t_index = 0
        # self.Tol_f_index = 0
        # self.gf_cite = 0
        # self.gF_paper = 0
        # self.Franceschini_f_index = 0
        # self.k_index = 0
        # self.contemp_h_index = 0
        # self.tapered_h_index = 0
        # self.rational_h_index = 0
        # self.Wu_w_index = 0
        # self.Wu_wq_index = 0
        # self.mu_index = 0
        # self.v_index = 0
        # self.normalized_h_index = 0
        # self.e_index = 0
        # self.pi_index = 0
        # self.p_index = 0
        # self.fractional_p_index = 0
        # self.harmonic_p_index = 0
        # self.ph_ratio = 0
        # self.maxprod_index = 0
        # self.specificImpact_s_index = 0
        # self.multiDim_h_index = []
        # self.Woeginger_w_index = 0
        # self.Wohlin_w_index = 0
        # self.hpd_index = 0
        # self.hi_index = 0
        # self.pure_h_index = 0
        # self.pure_h_proportional = 0
        # self.pure_h_geometric = 0
        # self.adapted_pure_h_index = 0
        # self.adapted_pure_h_proportional = 0
        # self.adapted_pure_h_geometric = 0
        # self.weighted_h_index = 0
        # self.j_index = 0
        # self.real_h_index = 0
        # self.hj_index = []
        # self.dynamic_h_index = 0
        # self.hF_hm_index = 0
        # self.hf_norm_hi_index = 0
        # self.b10_index = 0
        # self.bavg_self_index = 0
        # self.bavg_all_index = 0
        # self.sharpself_h_index = 0
        # self.sharpall_h_index = 0
        # self.total_self_only_cites = 0
        # self.total_self_all_cites = 0
        # self.avg_self_only_cites = 0
        # self.avg_self_all_cites = 0
        # self.trend_h_index = 0
        # self.impactVitality = 0
        # self.profit_index = 0
        # self.profit_adj_h_index = 0
        # self.profit_h_index = 0
        # self.posweighted_h_index = 0
        # self.citation_aggreg_frac = 0
        # self.citation_aggreg_prop = 0
        # self.citation_hcut_frac = 0
        # self.citation_hcut_prop = 0
        # self.two_sided_h_index = []
        # self.iteratively_weighted_h_index = 0
        # self.em_index = 0
        # self.emp_index = 0
        # self.ls_hrate = 0
        # self.time_scaled_h = 0
        # self.alpha_index = 0
        # self.time_scaled_papers = 0
        # self.time_scaled_citations = 0


def string_to_date(s: str) -> datetime.date:
    m, d, y = s.split('/')
    return datetime.date(int(y), int(m), int(d))


def date_to_string(d: datetime.date) -> str:
    return str(d.month) + '/' + str(d.day) + '/'+str(d.year)


def date_to_int(d: datetime.date) -> int:
    return datetime.date.toordinal(d)


def read_data_file(filename: str) -> Tuple[list, list]:
    """
    function to read basic citation input data

    The input file should be a tab-delimited text file. The first line is a
    header, with the following columns:
    * Year of the publication
    * # of authors of the publication
    * Author rank/position among the authors
    * A title/text description of the publication (citation, abbreviation).
      This is not actually used other than as for external tracking of which
      paper is which
    * The rest of the columns should contain dates for which the citation
      information is collected, in the form "mm/dd/yyyy". At least one such
      column must be included. For a few metrics, it works best if each
      column represents a single year.

    After the header row, each row represents a single publication. The first
    four columns contain the year of publication, # of authors, etc., as listed
    above, while columns 5+ contain the number of citations for that publication
    which have been recorded by the date in the header (cumulative count up
    through that date, not count for that date). If a publication has not been
    published by the specified date, the columns should containt the
    string "n/a".
      
    """
    with open(filename, "r") as inFile:
        a = -1
        article_list = []
        date_list = []
        for line in inFile:
            line = line.strip()
            a += 1
            # header
            if a == 0:
                # skip 1st 4 columns
                for i in range(4):
                    line = line[line.find(tb)+1:]
                tmp_list = line.split(tb)
                for d in tmp_list:
                    date_list.append(string_to_date(d))
            # read data
            elif line != '':
                new_article = Article()
                article_list.append(new_article)
                tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                new_article.year = int(tstr)
                tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                new_article.authors = int(tstr)
                tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]

                new_article.authorrank = int(tstr)
                tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]

                new_article.title = tstr
                cite_list = line.split(tb)
                for n in cite_list:
                    if n == 'n/a':
                        n = -1
                    new_article.citations.append(int(n))
    return date_list, article_list


def read_self_citation_files(article_list: list, sname: str, cname: str) -> None:
    """
    function to read self-citation information. This function uses two input
    files, one containing self-citation counts by the target author and one
    containing self-citation counts by co-authors of the target author on
    papers for which the target author was not an author. The format of these
    files is identical to the main citation data, above, except only listing
    the self-citation counts
    """
    # self cites
    with open(sname, "r") as sfile:
        a = -1
        for line in sfile:
            line = line.strip()
            a = a + 1
            # skip header
            if (a != 0) and (line != ''):
                article = article_list[a - 1]
                # skip year
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                # skip authors
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                # skip author rank
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                # skip title
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                cite_list = line.split(tb)
                for n in cite_list:
                    if n == 'n/a':
                        n = -1
                    article.selfcites.append(int(n))

    # co-author cites
    with open(cname, "r") as cfile:
        a = -1
        for line in cfile:
            line = line.strip()
            a = a + 1
            # skip header
            if (a != 0) and (line != ''):
                article = article_list[a - 1]
                # skip year
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                # skip authors
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                # skip author rank
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                # skip title
                # tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]
                cite_list = line.split(tb)
                for n in cite_list:
                    if n == 'n/a':
                        n = -1
                    article.coauthcites.append(int(n))


def rank(n: int, indx: list) -> list:
    irank = []
    for j in range(n):
        irank.append(0)
    for j in range(n):
        irank[indx[j]] = j
    return irank


def sortandrank(sortlist: list, n: int) -> Tuple[list, list]:
    tmpindex = sorted(range(n), key=lambda k: sortlist[k])
    tmprank = rank(n, tmpindex)
    # reverse so #1 is largest
    # NOTE: the ranks in rankorder go from 1 to n, rather than 0 to n-1
    rankorder = []
    for i in range(n):
        rankorder.append(n - tmprank[i])
    return tmpindex, rankorder


# -----------------------------------------------------
# Metric Calculation Functions
# -----------------------------------------------------

# g-index (Egghe 2006)
def calculate_g_index(n: int, rankorder: list, cumulative_cites: list) -> int:
    g_index = 0
    for i in range(n):
        if rankorder[i]**2 <= cumulative_cites[rankorder[i]-1]:
            g_index += 1
    return g_index


# h2-index (Kosmulski 2006)
def calculate_h2_index(n: int, rankorder: list, cites: list) -> int:
    h2_index = 0
    for i in range(n):
        if rankorder[i] <= math.sqrt(cites[i]):
            h2_index += 1
    return h2_index


# hg-index (Alonso et al 2010)
def calculate_hg_index(h: int, g: int) -> float:
    return math.sqrt(h*g)


# sharpened h-index (Schreiber 2007)
# also returns total and avg self-citations
def calculate_sharpened_h_index(n: int, y: int, cur_list: list, cites: list, inc_all: bool) -> Tuple[float, int, int]:
    self_cites = []
    avg_self_cites = 0
    total_self_cites = 0
    for i in range(n):
        article = cur_list[i]
        s = article.selfcites[y]
        if inc_all:
            s += article.coauthcites[y]
        self_cites.append(cites[i] - s)
        total_self_cites += s
        if cites[i] != 0:
            avg_self_cites += s / cites[i]
    avg_self_cites = avg_self_cites / n
    tmpindex, tmprank = sortandrank(self_cites, n)
    sharpself_h_index = 0
    for i in range(n):
        if tmprank[i] <= self_cites[i]:
            sharpself_h_index += 1
    return avg_self_cites, total_self_cites, sharpself_h_index


# b-index (Brown 2009)
def calculate_b_index(h: int, avgrate: float) -> float:
    return h * avgrate**0.75


# real h-index (hr-index) (Guns and Rousseau 2009)
def calculate_real_h_index(n: int, rankorder: list, h: int, cites: list) -> Number:
    j = -1
    k = -1
    for i in range(n):
        if rankorder[i] == h:
            j = i
        elif rankorder[i] == h + 1:
            k = i
    if (k != -1) and (j != -1):
        return ((h + 1) * cites[j] - h * cites[k]) / (1 - cites[k] + cites[j])
    else:
        return h


# a-index (Jin 2006; Rousseau 2006)
def calculate_a_index(core_cites: int, total_pubs: int) -> float:
    return core_cites/total_pubs


# r-index (Jin et al 2007)
def calculate_r_index(core_cites: int) -> float:
    return math.sqrt(core_cites)


# rm-index (Panaretos and Malesios 2009)
def calculate_rm_index(n: int, is_core: list, cites: list) -> float:
    rm_index = 0
    for i in range(n):
        if is_core[i]:
            rm_index += math.sqrt(cites[i])
    rm_index = math.sqrt(rm_index)
    return rm_index


# ar-index (Jin 2007; Jin et al 2007)
def calculate_ar_index(n: int, is_core: list, cites_per_year: list) -> float:
    ar_index = 0
    for i in range(n):
        if is_core[i]:
            ar_index += cites_per_year[i]
    ar_index = math.sqrt(ar_index)
    return ar_index


# m-index (median index) (Bornmann et al 2008)
def calculate_m_index(n: int, is_core: list, h: int, cites: list) -> float:
    core_cites = []
    for i in range(n):
        if is_core[i]:
            core_cites.append(cites[i])
    core_cites.sort()
    if h % 2 == 1:
        # odd number in core
        m_index = core_cites[(h // 2)]
    else:
        # even number in core
        m_index = (core_cites[(h // 2) - 1] + core_cites[h // 2]) / 2
    return m_index


# q2-index (Cabrerizo et al 2010)
def calculate_q2_index(h: int, m: float) -> float:
    return math.sqrt(h * m)


# k-index (Ye and Rousseau 2010)
def calculate_k_index(total_cites: int, core_cites: int, total_pubs: int) -> float:
    return (total_cites * core_cites) / (total_pubs * (total_cites - core_cites))


# Franceschini f-index (Franceschini and Maisano 2010)
def calculate_franceschini_f_index(maxy: int, miny: int) -> int:
    return maxy - miny + 1


# weighted h-index (Egghe and Rousseau 2008)
def calculate_weighted_h_index(n: int, cites: list, cumulative_cites: list, rankorder: list, h: int) -> float:
    weighted_h_index = 0
    for i in range(n):
        if cites[i] >= cumulative_cites[rankorder[i]-1] / h:
            weighted_h_index += cites[i]
    return math.sqrt(weighted_h_index)


# normalized h-index (Sidiropoulos et al 2007)
def calculate_normalized_h(h: int, total_pubs: int) -> float:
    return h / total_pubs


# v-index (Riikonen and Vihinen 2008)
def calculate_v_index(h: int, total_pubs: int) -> float:
    return 100 * h / total_pubs


# e-index (Zhang 2009)
def calculate_e_index(core_cites: int, h: int) -> float:
    return math.sqrt(core_cites - h ** 2)


# rational h-index (Ruane and Tol 2008)
def calculate_rational_h(n: int, is_core: list, cites: list, h: int, rankorder: list) -> float:
    j = 0
    for i in range(n):
        if is_core[i]:
            if cites[i] == h:
                j += 1
        else:
            if rankorder[i] == h + 1:
                j = j + (h + 1 - cites[i])
    return h + 1 - j / (2 * h + 1)


# h2-lower, center and upper (Bornmann et al 2010)
def calculate_h2percs(core_cites: int, h: int, total_cites: int) -> Tuple[float, float, float]:
    h2_upper = 100 * (core_cites - h**2) / total_cites
    h2_center = 100 * h**2 / total_cites
    h2_lower = 100 * (total_cites - core_cites) / total_cites
    return h2_upper, h2_center, h2_lower


# tapered h-index (Anderson et al 2008)
def calculate_tapered_h_index(n: int, cites: list, rankorder: list) -> float:
    ht = []
    for i in range(n):
        ht.append(0)
        if cites[i] <= rankorder[i]:
            ht[i] = cites[i] / (2*rankorder[i] - 1)
        else:
            ht[i] = rankorder[i] / (2*rankorder[i] - 1)
            for j in range(rankorder[i]+1, n+1):
                ht[i] += 1/(2*j - 1)
    tapered_h_index = 0
    for i in range(n):
        tapered_h_index += ht[i]
    return tapered_h_index


# pi-index (Vinkler 2009)
def calculate_pi_index(n: int, total_pubs: int, rankorder: list, cites: list) -> float:
    j = math.floor(math.sqrt(total_pubs))
    pi_index = 0
    for i in range(n):
        if rankorder[i] <= j:
            pi_index += cites[i]
    return pi_index / 100


# p-index (originally called mock hm-index), ph-ratio, and pf-index (Prathap 2010b, 2011)
def calculate_prathap_p_index(total_cites: int, total_pubs: int, h: int, cur_list: list,
                              y: int) -> Tuple[float, float, float]:
    p_index = (total_cites**2 / total_pubs)**(1/3)
    ph_ratio = p_index / h
    pf = 0
    nf = 0
    for article in cur_list:
        pf += 1/article.authors
        nf += article.citations[y]/article.authors
    fractional_p_index = (nf**2 / pf)**(1/3)
    return p_index, ph_ratio, fractional_p_index


# harmonic p-index (Prathap 2011)
def calculate_prathap_harmonic_p(cur_list: list, y: int) -> float:
    ph = 0
    nh = 0
    for article in cur_list:
        num = 1 / article.authorrank
        denom = 0
        for i in range(article.authors):
            denom += 1 / (i + 1)
        r = num / denom        
        ph += r
        nh += article.citations[y] * r
    return (nh**2 / ph)**(1/3)


# hi-index (Batista et al 2006) and pure h-index (Wan et al 2007)
def calculate_hi_pure(n: int, is_core: list, cur_list: list, h: int) -> Tuple[float, float]:
    suma = 0
    for i in range(n):
        if is_core[i]:
            suma += cur_list[i].authors
    return h**2 / suma, h / math.sqrt(suma / h)


# pure h-index with author order (Wan et al 2007)
def calculate_pure_order(n: int, is_core: list, cur_list: list, h: int) -> Tuple[float, float]:
    sump = 0  # proportional counting
    sumg = 0  # geometric counting
    for i in range(n):
        if is_core[i]:
            sump += cur_list[i].authors*(cur_list[i].authors + 1) / (2*cur_list[i].authors + 1 - cur_list[i].authorrank)
            sumg += (2**cur_list[i].authors - 1) / (2**(cur_list[i].authors - cur_list[i].authorrank))
    pure_prop = h / math.sqrt(sump / h)
    pure_geom = h / math.sqrt(sumg / h)
    return pure_prop, pure_geom


# Tol's f-index and t-index
def calculate_tol_indices(n: int, rankorder: list, fcum: list, tcum: list) -> Tuple[int, int]:
    tol_f_index = 0
    for i in range(n):
        if rankorder[i] / fcum[rankorder[i]-1] >= rankorder[i]:
            if rankorder[i] > tol_f_index:
                tol_f_index = rankorder[i]
    tol_t_index = 0
    for i in range(n):
        if math.exp(tcum[rankorder[i]-1]/rankorder[i]) >= rankorder[i]:
            if rankorder[i] > tol_t_index:
                tol_t_index = rankorder[i]
    return tol_f_index, tol_t_index


# mu-index (Glanzel and Schubert 2010)
def calculate_mu_index(n: int, rankorder: list, medarray: list) -> int:
    mu_index = 0
    for i in range(n):
        if medarray[rankorder[i]-1] >= rankorder[i]:
            if rankorder[i] > mu_index:
                mu_index = rankorder[i]
    return mu_index


# Wu w-index (Wu 2010)
def calculate_wu_w(n: int, cites: list, rankorder: list) -> Tuple[int, int]:
    wu_w_index = 0
    for i in range(n):
        if cites[i] >= 10 * rankorder[i]:
            wu_w_index += 1
    j = 0
    for i in range(n):
        if cites[i] >= 10 * rankorder[i]:
            if cites[i] < 10 * (wu_w_index + 1):
                j = j + (10 * (wu_w_index + 1) - cites[i])
        else:
            if rankorder[i] == wu_w_index + 1:
                j = j + 10 * (wu_w_index + 1) - cites[i]
    return wu_w_index, j


# Wohlin w-index (Wohlin 2009)
def calculate_wohlin_w(n: int, max_cites: int, cites: list) -> float:
    j = 5
    nc = 1
    while max_cites > j:
        j = j * 2
        nc += 1
    wval = []
    wclass = []
    for i in range(nc):
        if i + 1 == 1:
            wval.append(5)
        else:
            wval.append(2 * wval[i-1])
        wclass.append(0)
        for j in range(n):
            if cites[j] >= wval[i]:
                wclass[i] += 1
    wohlin_w_index = 0
    for i in range(nc):
        wohlin_w_index += math.log(wval[i]) * wclass[i]
    return wohlin_w_index


# contemporary h-index (Sidiropoulos et al 2007)
def calculate_contemporary_h(n: int, cites: list, cur_age: list) -> int:
    sc = []
    for i in range(n):
        sc.append(4 * cites[i] / (1 + cur_age[i]))
    tmpindex, tmporder = sortandrank(sc, n)
    contemp_h_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            contemp_h_index += 1
    return contemp_h_index


# hpd seniority index (Kosmulski 2009)
def calculate_hpd_seniority(n: int, cites_per_year: list) -> int:
    sc = []
    for i in range(n):
        sc.append(10 * cites_per_year[i])
    tmpindex, tmporder = sortandrank(sc, n)
    hpd_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hpd_index += 1
    return hpd_index


# specific impact s-index (De Visscher 2010)
def calculate_impact_s_index(n: int, cur_age: list, total_cites: int) -> float:
    specific_impact_s_index = 0
    for i in range(n):
        specific_impact_s_index += 1 - math.exp(-0.1 * cur_age[i])
    if specific_impact_s_index != 0:
        specific_impact_s_index = total_cites / (10 * specific_impact_s_index)
    return specific_impact_s_index


# hm-index/hF-index and gF-index (fractional paper) (Schreiber 2008; Egghe 2008)
def calculate_fractional_paper_indices(n: int, rankorder: list, cites: list,
                                       cum_rank: list, cumulative_cites: list) -> Tuple[int, int]:
    hf_hm_index = 0
    gf_paper = 0
    for i in range(n):
        if cum_rank[rankorder[i]-1] <= cites[i]:
            if cum_rank[rankorder[i]-1] > hf_hm_index:
                hf_hm_index = cum_rank[rankorder[i] - 1]
        if cum_rank[rankorder[i]-1]**2 <= cumulative_cites[i]:
            if cum_rank[rankorder[i]-1] > gf_paper:
                gf_paper = cum_rank[rankorder[i] - 1]
    return hf_hm_index, gf_paper


# multidimensional h-index (Garcia-Perez 2009)
def calculate_multidimensional_h(h: int, n: int, is_core: list, rankorder: list, cites: list) -> list:
    multi_dim_h_index = [h]
    multi_used = []
    for i in range(n):
        if is_core[i]:
            multi_used.append(True)
        else:
            multi_used.append(False)
    j = 0
    tmph = -1
    while tmph != 0:
        nc = len(multi_dim_h_index)
        j = j + multi_dim_h_index[nc-1]
        tmph = 0
        for i in range(n):
            if not multi_used[i]:
                if rankorder[i] - j <= cites[i]:
                    multi_used[i] = True
                    tmph += 1              
        if tmph > 0:
            multi_dim_h_index.append(tmph)
    return multi_dim_h_index


# two-sided h-index (Garcia-Perez 2012)
def calculate_two_sided_h(h: int, multi_dim_h: list, n: int, rankorder: list, cites: list) -> list:
    # only need to calculate the upper part of the index
    # the center and tail are indentical to multidimensional h
    # auto-calculate for as many steps in core as equal to length of
    # steps in tail
    twosidedh = []
    for i in multi_dim_h:
        twosidedh.append(i)
    j = 0
    tmph = h
    k = 1
    while k < len(multi_dim_h):
        j = j + tmph
        tmph = 0
        for i in range(n):
            if rankorder[i] <= cites[i] - j:
                tmph += 1
        twosidedh.insert(0, tmph)
        k += 1
    return twosidedh


# normalized hi-index/hf-index and gf-index (Wohlin 2009; Egghe 2008)
def calculate_hinorm(n: int, cites: list, cur_list: list) -> Tuple[int, int]:
    sc = []
    for i in range(n):
        sc.append(cites[i] / cur_list[i].authors)
    tmpindex, tmporder = sortandrank(sc, n)
    acum = [sc[tmpindex[n-1]]]
    for i in range(1, n):
        acum.append(acum[i-1] + sc[tmpindex[n-i-1]])
    hf_norm_hi_index = 0
    gf_cite = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hf_norm_hi_index += 1
        if tmporder[i]**2 <= acum[tmporder[i]-1]:
            gf_cite += 1
    return hf_norm_hi_index, gf_cite


# position-weighted h-index, weighted aggregate, weighted h-cut (Abbas 2011)
def calculate_weightedaggregate_prop(n: int, cites: list, cur_list: list) -> Tuple[int, float, float]:
    sc = []
    totalsum = 0
    for i in range(n):
        w = ((2 * (cur_list[i].authors + 1 - cur_list[i].authorrank)) /
             (cur_list[i].authors * (cur_list[i].authors + 1)))
        sc.append(cites[i] * w)
        totalsum += cites[i] * w
    tmpindex, tmporder = sortandrank(sc, n)
    wh = 0
    hcut = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            wh += 1
            hcut += sc[i]
    return wh, totalsum, hcut


# equal-weighted aggregate, weighted h-cut (Abbas 2011)
def calculate_weightedaggregate_fract(n: int, cites: list, cur_list: list) -> Tuple[float, float]:
    sc = []
    totalsum = 0
    for i in range(n):
        w = 1 / cur_list[i].authors
        sc.append(cites[i] * w)
        totalsum += cites[i] * w
    tmpindex, tmporder = sortandrank(sc, n)
    hcut = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hcut += sc[i]
    return totalsum, hcut


# Woeginger w-index (Woeginger 2008)
def calculate_woeginger_w(n: int, rankorder: list, cites: list) -> int:
    woeginger_w_index = 0
    for j in range(n):
        tmp_good = True
        for i in range(n):
            if rankorder[i] <= j:
                if cites[i] < j - rankorder[i] + 1:
                    tmp_good = False
        if tmp_good:
            woeginger_w_index = j
    return woeginger_w_index


# maxprod (Kosmulski 2007)
def calculate_maxprod(n: int, cites: list, rankorder: list) -> int:
    maxprod_index = 0
    for i in range(n):
        if cites[i] * rankorder[i] > maxprod_index:
            maxprod_index = cites[i] * rankorder[i]
    return maxprod_index


# j-index (Todeschini 2011)
def calculate_j_index(n: int, cites: list, h: int) -> float:
    # constants for j-index
    ndhk = 12
    dhk = (500, 250, 100, 50, 25, 10, 5, 4, 3, 2, 1.5, 1.25)

    sumw = 0
    sumwdhk = 0
    for j in range(ndhk):
        sumw += 1 / (j + 1)
        c = 0
        for i in range(n):
            if cites[i] >= h * dhk[j]:
                c += 1
        sumwdhk = sumwdhk + c/(j + 1)
    return h + sumwdhk/sumw


# adapted pure h-index (Chai et al 2008)
def calculate_adapated_pure_h(n: int, cites: list, cur_list: list) -> float:
    sc = []
    for i in range(n):
        sc.append(cites[i] / math.sqrt(cur_list[i].authors))
    tmpindex, tmporder = sortandrank(sc, n)
    j = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            j += 1
    cite_e = 0
    cite_e1 = 0
    for i in range(n):
        if tmporder[i] == j:
            cite_e = sc[i]
        elif tmporder[i] == j + 1:
            cite_e1 = sc[i]
    return (((j + 1) * cite_e) - (j * cite_e1)) / (cite_e - cite_e1 + 1)


# adapted pure h-index w/proportional author credit (Chai et al 2008)
def calculate_adapated_pure_h_prop(n: int, cites: list, cur_list: list) -> float:
    sc = []
    for i in range(n):
        ea = cur_list[i].authors*(cur_list[i].authors + 1) / (2*(cur_list[i].authors + 1 - cur_list[i].authorrank))
        sc.append(cites[i] / math.sqrt(ea))
    tmpindex, tmporder = sortandrank(sc, n)
    j = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            j += 1
    cite_e = 0
    cite_e1 = 0
    for i in range(n):
        if tmporder[i] == j:
            cite_e = sc[i]
        elif tmporder[i] == j + 1:
            cite_e1 = sc[i]
    return (((j + 1) * cite_e) - (j * cite_e1)) / (cite_e - cite_e1 + 1)


# adapted pure h-index w/geometric author credit (Chai et al 2008)
def calculate_adapated_pure_h_geom(n: int, cites: list, cur_list: list) -> float:
    sc = []
    for i in range(n):
        ea = (2**cur_list[i].authors - 1) / (2**(cur_list[i].authors - cur_list[i].authorrank))
        sc.append(cites[i] / math.sqrt(ea))
    tmpindex, tmporder = sortandrank(sc, n)
    j = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            j += 1
    cite_e = 0
    cite_e1 = 0
    for i in range(n):
        if tmporder[i] == j:
            cite_e = sc[i]
        elif tmporder[i] == j + 1:
            cite_e1 = sc[i]
    return (((j + 1) * cite_e) - (j * cite_e1)) / (cite_e - cite_e1 + 1)


# profit p-index and related values (Aziz and Rozing 2013)
def calculate_profit_indices(n: int, cur_list: list, cites: list, h: int) -> Tuple[float, int, float]:
    mon_equiv = []
    for article in cur_list:
        if article.authors % 2 == 0:
            me_d = 0
        else:
            me_d = 1 / (2 * article.authors)
        mon_equiv.append((1 + abs(article.authors + 1 - 2*article.authorrank)) /
                         ((article.authors**2) / 2 + article.authors * (1 - me_d)))
    monograph_equiv = 0
    for i in range(n):
        monograph_equiv += mon_equiv[i]
    profit_index = 1 - monograph_equiv / n
    sc = []
    for i in range(n):
        sc.append(cites[i] * mon_equiv[i])
    tmpindex, tmporder = sortandrank(sc, n)
    profit_adj_h_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            profit_adj_h_index += 1
    profit_h_index = 1 - profit_adj_h_index / h
    return profit_index, profit_adj_h_index, profit_h_index


# hj-indices (Dorta-Gonzalez and Dorta-Gonzalez 2010)
def calculate_hj_indices(total_pubs: int, h: int, r_cites: list) -> list:
    if total_pubs < 2 * h - 1:
        j = total_pubs - h
    else:
        j = h - 1
    hj_index = [h**2]
    for i in range(1, j+1):
        hj_index.append(hj_index[i-1] + (h - i)*(r_cites[h - i - 1] - r_cites[h - i]) + r_cites[h + i - 1])
    return hj_index


# trend h-index
def calculate_trend_h(n: int, cur_list: list, y: int, date_list: list) -> int:
    sc = []
    for i in range(n):
        sc.append(0)
        article = cur_list[i]
        for yy in range(y+1):
            if article.citations[yy] == -1:
                cy = 0
            elif yy == 0:
                cy = article.citations[yy]
            else:
                if article.citations[yy-1] == -1:
                    cy = article.citations[yy]
                else:
                    cy = article.citations[yy] - article.citations[yy-1]
            sc[i] = sc[i] + cy * (1 / (date_list[y].year - date_list[yy].year + 1))
        sc[i] = 4 * sc[i]

    tmpindex, tmporder = sortandrank(sc, n)
    trend_h_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            trend_h_index += 1
    return trend_h_index


# iteratively weighted h-index (Todeschini and Baccini 2016)
def calculate_iteratively_weighted_h_index(multidim_h_index: list) -> float:
    iteratively_weighted_h_index = 0
    for p, h in enumerate(multidim_h_index):
        iteratively_weighted_h_index += h / (p + 1)
    return iteratively_weighted_h_index


# EM-index (Bihari and Tripathi 2017)
def calculate_em_index(n: int, rankorder: list, cites: list) -> Tuple[float, float]:
    def count_cited_articles(tmpc: list) -> int:
        cnt = 0
        for c in tmpc:
            if c > 0:
                cnt += 1
        return cnt

    # EM-index
    em_component = []
    tmpcites = [c for c in cites]  # make a temporary copy of the citation counts
    ncited = count_cited_articles(tmpcites)
    while ncited > 1:
        if max(tmpcites) == 1:
            em_component.append(1)
            ncited = 0
        else:
            h_index = 0
            for i in range(n):
                if rankorder[i] <= tmpcites[i]:
                    h_index += 1
            em_component.append(h_index)
            tmpcites = [max(0, c-h_index) for c in tmpcites]  # subtract previous h-index from citations
            ncited = count_cited_articles(tmpcites)
    em_index = math.sqrt(sum(em_component))

    # EM'-index
    em_component = []
    tmpcites = [c for c in cites]  # make a temporary copy of the citation counts
    tmpranks = [r for r in rankorder]  # make a temporary copy of the ranks
    ncited = count_cited_articles(tmpcites)
    while ncited > 1:
        if max(tmpcites) == 1:
            em_component.append(1)
            ncited = 0
        else:
            h_index = 0
            for i in range(n):
                if tmpranks[i] <= tmpcites[i]:
                    h_index += 1
            em_component.append(h_index)
            # subtract h_index only from top h pubs
            for i in range(n):
                if tmpranks[i] <= tmpcites[i]:
                    tmpcites[i] = max(0, tmpcites[i]-h_index)
            ncited = count_cited_articles(tmpcites)
            # rerank counts
            tmpranks = sortandrank(tmpcites, n)[1]
    emp_index = math.sqrt(sum(em_component))

    return em_index, emp_index


# alpha-index
def calculate_alpha_index(h: int, age: int) -> float:
    ndecades = math.ceil(age/10)
    return h / ndecades


# h-rate / m-quotient
def calculate_h_rate(h: int, age: int) -> float:
    return h / age


# time-scaled h-index (Todeschini and Baccini 2016)
def calculate_time_scaled_h_index(h: int, age: int) -> float:
    return h / math.sqrt(age)


# time-scaled papers and citations (Todeschini and Baccini 2016)
def calculate_time_scaled_rates(np: int, nc: int, age: int) -> Tuple[float, float]:
    return np / age, nc / age


# annual h-index (hIa) (Harzing et al 2014)
def calculate_annual_h_index(norm_h: int, age: int) -> float:
    return norm_h / age


# -----------------------------------------------------
# Main Calculation Loop
# -----------------------------------------------------

def calculate_metrics(y: int, datelist: list, articlelist: list, incself: bool) -> MetricSet:
    """
    function to calculate impact factor metrics for data for a given date 
    """

    # determine active articles and raw data summaries
    cur_list = []
    metrics = MetricSet()
    metrics.date = datelist[y]
    metrics.values["total pubs"] = 0
    metrics.values["total cites"] = 0
    metrics.values["max cites"] = 0
    firstyear = articlelist[0].year
    for article in articlelist:
        firstyear = min(article.year, firstyear)
        if article.citations[y] != -1:
            cur_list.append(article)
            metrics.values["total pubs"] += 1
            metrics.values["total cites"] += article.citations[y]
            metrics.values["max cites"] = max(metrics.values["max cites"], article.citations[y])
    metrics.values["cites per pub"] = metrics.values["total cites"] / metrics.values["total pubs"]

    # construct sublists for active articles only
    n = len(cur_list)
    cites = [0 for _ in range(n)]
    rcites = [0 for _ in range(n)]
    metrics.cumulativeCites = [0 for _ in range(n)]
    fcum = [0 for _ in range(n)]
    tcum = [0 for _ in range(n)]
    cum_rank = [0 for _ in range(n)]
    medarray = [0 for _ in range(n)]
    cur_age = [0 for _ in range(n)]
    cites_per_year = [0 for _ in range(n)]
    is_core = [False for _ in range(n)]
    # for i in range(n):
    #     cites.append(0)
    #     cur_age.append(0)
    #     cites_per_year.append(0)
    #     metrics.cumulativeCites.append(0)
    #     cum_rank.append(0)
    #     fcum.append(0)
    #     tcum.append(0)
    #     medarray.append(0)
    #     is_core.append(False)
    #     rcites.append(0)
    minfyear = 0
    maxfyear = 0
    i = -1
    for article in cur_list:
        i += 1
        if article.citations[y] > 0: 
            if minfyear == 0:
                minfyear = article.year
                maxfyear = minfyear
            else:
                maxfyear = max(maxfyear, article.year)
                # if article.year > maxfyear:
                #     maxfyear = article.year
                minfyear = min(minfyear, article.year)
                # if article.year < minfyear:
                #     minfyear = article.year
        cites[i] = article.citations[y]
        cur_age[i] = datelist[y].year - article.year
        if cur_age[i] < 0:
            cur_age[i] = 0
        if cur_age[i] == 0:
            cites_per_year[i] = cites[i]
        else:
            cites_per_year[i] = cites[i] / cur_age[i]
            
    # sort the articles by number of citations
    tmpindex, rankorder = sortandrank(cites, n)

    for i in range(n):
        article = cur_list[tmpindex[n-i-1]]
        if i > 0:
            metrics.cumulativeCites[i] = metrics.cumulativeCites[i-1] + cites[tmpindex[n-i-1]]
        else: 
            metrics.cumulativeCites[i] = cites[tmpindex[n-i-1]]
        rcites[i] = cites[tmpindex[n-i-1]]
        cum_rank[i] = cum_rank[i-1] + 1 / article.authors
        # for Tol's f and t-indices
        if cites[tmpindex[n-i-1]] > 0:
            fcum[i] = fcum[i-1] + 1 / cites[tmpindex[n-i-1]]
            tcum[i] = tcum[i-1] + math.log(cites[tmpindex[n-i-1]])
        else:
            fcum[i] = fcum[i-1]
            tcum[i] = tcum[i-1]
        # for mu-index
        j = (i + 1) // 2
        if (i + 1) % 2 == 0:      
            medarray[i] = (cites[tmpindex[n-j-1]] + cites[tmpindex[n-j]]) / 2
        else:
            medarray[i] = cites[tmpindex[n-j-1]]

    # attach ranks to articles
    if y == len(datelist) - 1:
        j = -1
        for article in articlelist:
            if article.citations[y] == -1:
                article.rank = -1
            else:
                j += 1
                article.rank = rankorder[j]

    # basic indices
    metrics.values["h-index"] = 0
    metrics.values["core cites"] = 0
    for i in range(n):
        if rankorder[i] <= cites[i]:
            is_core[i] = True
            metrics.values["h-index"] += 1
            metrics.values["core cites"] += cites[i]
    metrics.values["Hirsch min const"] = metrics.values["total cites"] / metrics.values["h-index"]**2
    # if datelist[y].year - firstyear != 0:
    #     metrics.Hirsch_mQuotient = metrics.values["h-index"] / (datelist[y].year - firstyear)
    # else:
    #     metrics.Hirsch_mQuotient = -1
    # changed this to reflect logic in Todeschini and Baccini (2016)
    academic_age = datelist[y].year - firstyear + 1

    # other indices
    metrics.values["h-rate"] = calculate_h_rate(metrics.values["h-index"], academic_age)
    metrics.values["time-scaled h-index"] = calculate_time_scaled_h_index(metrics.values["h-index"], academic_age)
    (metrics.values["time-scaled num papers"],
     metrics.values["time-scaled num citations"]) = calculate_time_scaled_rates(metrics.values["total pubs"],
                                                                                metrics.values["total cites"],
                                                                                academic_age)
    metrics.values["g-index"] = calculate_g_index(n, rankorder, metrics.cumulativeCites)
    metrics.values["h(2)-index"] = calculate_h2_index(n, rankorder, cites)
    metrics.values["hg-index"] = calculate_hg_index(metrics.values["h-index"], metrics.values["g-index"])
    if incself:
        (metrics.values["avg self citation rate"],
         metrics.values["total self citations"],
         metrics.values["self sharpened h-index"]) = calculate_sharpened_h_index(n, y, cur_list, cites, False)
        metrics.values["total self citation rate"] = (metrics.values["total self citations"] /
                                                      metrics.values["total cites"])
        metrics.values["avg self b-index"] = calculate_b_index(metrics.values["h-index"],
                                                               1-metrics.values["avg self citation rate"])
        (metrics.values["avg self/coauthor citation rate"],
         metrics.values["total self/coauthor citations"],
         metrics.values["all sharpened h-index"]) = calculate_sharpened_h_index(n, y, cur_list, cites, True)
        metrics.values["total self/coauthor citation rate"] = (metrics.values["total self/coauthor citations"] /
                                                               metrics.values["total cites"])
        metrics.values["avg all b-index"] = calculate_b_index(metrics.values["h-index"],
                                                              1-metrics.values["avg self/coauthor citation rate"])
        metrics.values["10% b-index"] = calculate_b_index(metrics.values["h-index"], 0.9)
    metrics.values["a-index"] = calculate_a_index(metrics.values["core cites"], metrics.values["total pubs"])
    metrics.values["real h-index"] = calculate_real_h_index(n, rankorder, metrics.values["h-index"], cites)
    metrics.values["r-index"] = calculate_r_index(metrics.values["core cites"])
    metrics.values["rm-index"] = calculate_rm_index(n, is_core, cites)
    metrics.values["ar-index"] = calculate_ar_index(n, is_core, cites_per_year)
    metrics.values["m-index"] = calculate_m_index(n, is_core, metrics.values["h-index"], cites)
    metrics.values["q2-index"] = calculate_q2_index(metrics.values["h-index"], metrics.values["m-index"])
    metrics.values["k-index"] = calculate_k_index(metrics.values["total cites"], metrics.values["core cites"],
                                                  metrics.values["total pubs"])
    metrics.values["Franceschini f-index"] = calculate_franceschini_f_index(maxfyear, minfyear)
    metrics.values["weighted h-index"] = calculate_weighted_h_index(n, cites, metrics.cumulativeCites, rankorder,
                                                                    metrics.values["h-index"])
    metrics.values["normalized h-index"] = calculate_normalized_h(metrics.values["h-index"],
                                                                  metrics.values["total pubs"])
    metrics.values["v-index"] = calculate_v_index(metrics.values["h-index"], metrics.values["total pubs"])
    metrics.values["e-index"] = calculate_e_index(metrics.values["core cites"], metrics.values["h-index"])
    metrics.values["rational h-index"] = calculate_rational_h(n, is_core, cites, metrics.values["h-index"], rankorder)
    (metrics.values["h2-upper"],
     metrics.values["h2-center"],
     metrics.values["h2-tail"]) = calculate_h2percs(metrics.values["core cites"], metrics.values["h-index"],
                                                    metrics.values["total cites"])
    metrics.values["tapered h-index"] = calculate_tapered_h_index(n, cites, rankorder)
    metrics.values["pi-index"] = calculate_pi_index(n, metrics.values["total pubs"], rankorder, cites)
    (metrics.values["p-index"],
     metrics.values["ph-ratio"],
     metrics.values["fractional p-index"]) = calculate_prathap_p_index(metrics.values["total cites"],
                                                                       metrics.values["total pubs"],
                                                                       metrics.values["h-index"], cur_list, y)
    metrics.values["harmonic p-index"] = calculate_prathap_harmonic_p(cur_list, y)
    metrics.values["hi-index"], metrics.values["frac pure h-index"] = calculate_hi_pure(n, is_core, cur_list,
                                                                                        metrics.values["h-index"])
    (metrics.values["prop pure h-index"],
     metrics.values["geom pure h-index"]) = calculate_pure_order(n, is_core, cur_list, metrics.values["h-index"])
    metrics.values["Tol f-index"], metrics.values["Tol t-index"] = calculate_tol_indices(n, rankorder, fcum, tcum)
    metrics.values["mu-index"] = calculate_mu_index(n, rankorder, medarray)
    metrics.values["Wu w-index"], metrics.values["Wu w(q)"] = calculate_wu_w(n, cites, rankorder)
    metrics.values["Wohlin w-index"] = calculate_wohlin_w(n, metrics.values["max cites"], cites)
    metrics.values["contemporary h-index"] = calculate_contemporary_h(n, cites, cur_age)
    metrics.values["hpd-index"] = calculate_hpd_seniority(n, cites_per_year)
    metrics.values["specific impact s-index"] = calculate_impact_s_index(n, cur_age, metrics.values["total cites"])
    (metrics.values["hF/hm-index"],
     metrics.values["gf-paper"]) = calculate_fractional_paper_indices(n, rankorder, cites, cum_rank,
                                                                      metrics.cumulativeCites)
    metrics.values["multidim h-index"] = calculate_multidimensional_h(metrics.values["h-index"], n, is_core, rankorder,
                                                                      cites)
    metrics.values["twosided h-index"] = calculate_two_sided_h(metrics.values["h-index"],
                                                               metrics.values["multidim h-index"], n, rankorder, cites)
    metrics.values["iter weighted h-index"] = calculate_iteratively_weighted_h_index(metrics.values["multidim h-index"])
    metrics.values["hf/hi-index"], metrics.values["gf-cite"] = calculate_hinorm(n, cites, cur_list)
    (metrics.values["position-weighted h-index"],
     metrics.values["prop weight citation aggregate"],
     metrics.values["prop weight citation H-cut"]) = calculate_weightedaggregate_prop(n, cites, cur_list)
    (metrics.values["frac weight citation aggregate"],
     metrics.values["frac weight citation H-cut"]) = calculate_weightedaggregate_fract(n, cites, cur_list)
    metrics.values["Woeginger w-index"] = calculate_woeginger_w(n, rankorder, cites)
    metrics.values["maxprod-index"] = calculate_maxprod(n, cites, rankorder)
    metrics.values["j-index"] = calculate_j_index(n, cites, metrics.values["h-index"])
    metrics.values["frac adapt pure h-index"] = calculate_adapated_pure_h(n, cites, cur_list)
    metrics.values["prop adapt pure h-index"] = calculate_adapated_pure_h_prop(n, cites, cur_list)
    metrics.values["geom adapt pure h-index"] = calculate_adapated_pure_h_geom(n, cites, cur_list)
    (metrics.values["profit p-index"],
     metrics.values["profit adj h-index"],
     metrics.values["profit h-index"]) = calculate_profit_indices(n, cur_list, cites, metrics.values["h-index"])
    metrics.values["hj-indices"] = calculate_hj_indices(metrics.values["total pubs"], metrics.values["h-index"], rcites)
    metrics.values["trend h-index"] = calculate_trend_h(n, cur_list, y, datelist)
    metrics.values["em-index"], metrics.values["emp-index"] = calculate_em_index(n, rankorder, cites)
    metrics.values["alpha-index"] = calculate_alpha_index(metrics.values["h-index"], academic_age)
    metrics.values["annual h-index"] =  calculate_annual_h_index(metrics.values["hf/hi-index"], academic_age)

    return metrics


# -----------------------------------------------------
# Special metric calculations that require data from multiple time points
# -----------------------------------------------------

# dynamic h-type-index (Rousseau and Ye 2008)
def calculate_dynamic_h(metric_list: list) -> None:
    metric = metric_list[0]
    metric.values["dynamic h-type-index"] = -1
    for m in range(1, len(metric_list)):
        avgh = 0
        avgd = 0
        for i in range(m+1):
            metric = metric_list[i]
            avgh += metric.values["rational h-index"]
            avgd += date_to_int(metric.date)
        avgh /= m + 1
        avgd /= m + 1
        sumxy = 0
        sumx2 = 0
        for i in range(m+1):
            metric = metric_list[i]
            sumxy += (metric.values["rational h-index"] - avgh) * (date_to_int(metric.date) - avgd)
            sumx2 += (date_to_int(metric.date) - avgd)**2
        metric = metric_list[m]
        metric.values["dynamic h-type-index"] = 365 * metric.values["r-index"] * (sumxy / sumx2)


# impact vitality (Rons and Amez 2008, 2009)
def calculate_impact_vitality(metric_list: list) -> None:
    if len(metric_list) < 6:
        for metric in metric_list:
            metric.values["impact vitality"] = -1
    else:
        w = 5  # fix at a 5 year window
        for i in range(w-1):
            metric = metric_list[i]
            metric.values["impact vitality"] = -1
        for m in range(w-1, len(metric_list)):
            # calculate denominator of equation
            d = 0
            for i in range(w):
                d += 1/(i+1)
            d -= 1

            # calculate numerator and denominator of numerator of equation
            nn = 0
            nd = 0
            for i in range(w):
                metric = metric_list[m - i]
                tc = metric.values["total cites"]
                if m - i != 0:
                    metric = metric_list[m - i - 1]
                    tc -= metric.values["total cites"]
                nd += tc
                nn += tc / (i + 1)
                
            # calculate value
            metric = metric_list[m]
            metric.values["impact vitality"] = (w * (nn / nd) - 1) / d


# least-squares h-rate (Burrell 2007)
def calculate_least_squares_h_rate(metric_list: list) -> None:
    first_year = metric_list[0].date.year
    for m in range(len(metric_list)):
        sumxy = 0
        sumx2 = 0
        for i in range(m+1):
            metric = metric_list[i]
            nyears = metric.date.year - first_year + 1
            sumxy += metric.values["h-index"] * nyears
            sumx2 += nyears**2
        metric = metric_list[m]
        metric.values["ls h-rate"] = sumxy/sumx2
        # for m in range(len(metric_list)):
        #     if m == 0:
        #         metric = metric_list[m]
        #         metric.ls_hrate = metric.h_index
        #     else:
        #         avgh = 0
        #         avgd = 0
        #         for i in range(m + 1):
        #             metric = metric_list[i]
        #             avgh += metric.h_index
        #             avgd += metric.date.year - first_year + 1
        #         avgh /= m + 1
        #         avgd /= m + 1
        #         sumxy = 0
        #         sumx2 = 0
        #         for i in range(m + 1):
        #             metric = metric_list[i]
        #             nyears = metric.date.year - first_year + 1
        #             sumxy += (metric.h_index - avgh) * (nyears - avgd)
        #             sumx2 += (nyears - avgd) ** 2
        #         metric = metric_list[m]
        #         metric.ls_hrate = sumxy / sumx2


# -----------------------------------------------------
# output a table of all results
# -----------------------------------------------------
def write_output(fname: str, datelist: list, metriclist: list, incself: bool) -> None:
    fstr = "1.4f"  # constant formatting string
    with open(fname, "w", encoding="utf-8") as outfile:
        # write header of dates
        outfile.write("Date")
        for date in datelist:
            outfile.write(tb + date_to_string(date))
        outfile.write("\n")

        for m in METRIC_NAMES:
            m_info = METRIC_INFO[m]
            is_self = m_info[0]
            metric_type = m_info[1]
            metric_name = m_info[2]
            if is_self and not incself:
                pass  # skip self-citation metrics
            else:
                outfile.write(metric_name)  # name of metric
                for metric in metriclist:
                    if metric_type == INT:
                        outfile.write(tb + str(metric.values[m]))
                    elif metric_type == FLOAT:
                        outfile.write(tb + format(metric.values[m], fstr))
                    elif metric_type == INTLIST:
                        outfile.write(tb + str(metric.values[m]))
                    elif metric_type == FLOAT_NEG:
                        if metric.values[m] < 0:
                            outfile.write(tb + "n/a")
                        else:
                            outfile.write(tb + format(metric.values[m], fstr))
                outfile.write("\n")


# -----------------------------------------------------
# Output results as set of webpages
# -----------------------------------------------------
def webheader(outfile, page_title: str, header: list, data: list, chart_title: str) -> None:
    outfile.write("<!DOCTYPE HTML>\n")
    outfile.write("<html lang=\"en\">\n")
    outfile.write("  <head>\n")
    outfile.write("    <meta charset=\"utf-8\" />\n")
    outfile.write("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n")
    outfile.write("    <title>" + page_title + "</title>\n")
    outfile.write("    <meta name=\"description\" content=\"xxx\" />\n")
    outfile.write("    <link rel=\"author\" href=\"mailto:msr@asu.edu\" />\n")
    outfile.write("    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?"
                  "config=TeX-MML-AM_CHTML\"></script>\n")
    # graph data
    outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
    outfile.write("    <script type=\"text/javascript\">\n")
    outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
    outfile.write("      google.setOnLoadCallback(drawChart);\n")
    outfile.write("      function drawChart() {\n")
    outfile.write("        var data1 = google.visualization.arrayToDataTable([\n")
    outfile.write("           [" + ",".join(header) + "],\n")
    for d in data:
        outfile.write("           [" + ",".join(d) + "],\n")
    outfile.write("		]);\n")
    outfile.write("\n")
    outfile.write("        var options1 = {\n")
    outfile.write("          title: \"" + chart_title + "\",\n")
    outfile.write("		  legend: {position: 'right'},\n")
    outfile.write("		  hAxis: {slantedText: true}\n")
    outfile.write("        };\n")
    outfile.write("\n")
    outfile.write("        var chart1 = new google.visualization." +
                  "LineChart(document.getElementById('impact_chart1_div'));\n")
    outfile.write("        chart1.draw(data1, options1);\n")
    outfile.write("\n")
    outfile.write("		}\n")
    outfile.write("    </script>\n")
    outfile.write("  </head>\n")


def write_paragraph(outfile, p: str) -> None:
    outfile.write("    <p>" + p + "</p>\n")


def webout_m_quotient(date_list: list, metric_list: list) -> None:
    """
    Output a webpage with the m_quotient and least squares h-rates
    """
    data1 = []
    data2 = []
    for i, d in enumerate(date_list):
        year = d.year
        m = metric_list[i]
        data1.append(["\'" + str(year) + "\'", str(m.Hirsch_mQuotient), str(m.ls_hrate)])
        data2.append(["\'" + str(year) + "\'", str(m.h_index)])

    with open("webout/m_quotient.html", "w", encoding="utf-8") as outfile:
        header = ["\'Year\'", "\'h-rate\'", "\'ls h-rate\'"]
        webheader(outfile, "h-rate", header, data1, "h-rate through time")

        # define equations and symbols
        m_equation = r"$$m=\frac{h}{Y-Y_{0}+1}$$"
        hstr = r"\(h\)"
        ystr = r"\(Y\)"
        y0str = r"\(Y_{0}\)"
        hts_equation = r"$$h^{TS}=\frac{h}{\sqrt{Y-Y_{0}+1}}$$"
        p1 = "Originaly defined by Hirsch (2005), this metric is also known as the " \
             "<strong><em>m-</em>quotient,</strong> " \
             "<strong><em>m-</em>ratio index,</strong> <strong>age-normalized <em>h-</em>index,</strong> and " \
             "<strong>Carbon <em>h-</em>factor.</strong> It measures the rate at which the <em>h-</em>index has " \
             "increased over the career of a researcher. It is calculated simply as:"
        p2 = "where " + hstr + " is the <em>h-</em>index in year " + ystr + " and " + y0str + \
             " is the year of the researcher's first publication (the denominator of this equation is the academic " \
             "age of the researcher)."
        p3 = "The above estimation is essentially just the slope of the line from the start of a researcher's " + \
             "career through the most recent estimate of the <em>h-</em>index. If one has access to yearly " \
             "estimates of " + hstr + ", an alternative would be to perform a linear regression of " + hstr + \
             " versus year of academic career (through the origin) and use the slope of that line for a more accurate" \
             " measure. This is known as the <strong>least squares <em>h-</em>rate</strong> (Burrell, 2007)."
        p4 = "Another similar measure, the <strong>time-scaled <em>h-</em>index</strong> (Mannella and Rossi 2013) " \
             "scales " + hstr + " by the square-root of the academic age."
        outfile.write("  <body>\n")
        outfile.write("    <h1><em>h-</em>rate</h1>\n")
        write_paragraph(outfile, p1)
        write_paragraph(outfile, m_equation)
        write_paragraph(outfile, p2)
        write_paragraph(outfile, p3)
        write_paragraph(outfile, p4)
        write_paragraph(outfile, hts_equation)
        outfile.write("   <div id=\"impact_chart1_div\"></div>\n")
        outfile.write("  </body>\n")
        outfile.write("</html>\n")


# def write_webpages(date_list: list, metric_list: list, inc_self: bool) -> None:
#     webout_m_quotient(date_list, metric_list)


# -----------------------------------------------------
# Google Scholar import functions
# -----------------------------------------------------
def get_webpage(url: str, encoding: str) -> str:
    """
    function to fetch the webpage specifed by url and 
    return a single string containing the contents of the page
    """
    webpage = urllib.request.urlopen(url)
    page = webpage.read()
    page = page.decode(encoding, "ignore")
    return page


def trim_header(page: str) -> str:
    """
    This function removes the header (including CSS and scripts) from
    the webpage, possibly increasing search efficiency a little
    """
    return page[page.find("<body>"):]


def find_scholar_name(page: str) -> str:
    """
    Find the name of the scholar from the Google Scholar profile
    """
    name_tag = "<div id=\"gsc_prf_in\">"
    x = page.find(name_tag)
    name = page[x+len(name_tag):]
    name = name[:name.find("<")]
    return name


def update_author_list(paper: Article) -> str:
    """
    This function tries to update the author list when it is abbreviated on
    the primary profile page
    """
    author_tag = "<div class=\"gsc_field\">Authors</div><div class=\"gsc_value\">"
    site = "https://scholar.google.com" + paper.googleScholarURL    
    page = get_webpage(site, "utf-8")
    page = trim_header(page)
    x = page.find(author_tag)
    tstr = page[x+len(author_tag):]
    return tstr[:tstr.find("</div>")]


def standardize_author(instr: str) -> str:
    """
    Standardize the name format to all uppecase, with just a single
    initial (no periods, middle names) and last name, e.g., M ROSENBERG
    """
    names = instr.strip().split(" ")  
    standard = names[0][0]
    # standard = ''
    # for n in names[:len(names)-1]:
    #    standard += n.strip()[0]
    standard += " " + names[len(names)-1]
    return standard.upper()


def clean_authors(article: Article, author_str: str) -> None:
    if author_str.find("...") > -1:
        author_str = update_author_list(article)
    if "," in author_str:
        tmp_list = author_str.split(",")
    else:
        tmp_list = [author_str]
    article.authors = len(tmp_list)
    for a in tmp_list:
        article.authorList.append(standardize_author(a))


def detect_author_order(article: Article, name: str) -> None:
    x = article.authorList.index(name)
    if x == -1:
        x = 0
    article.authorrank = x + 1    


def find_gs_articles(page: str) -> list:
    article_tag = "<td class=\"gsc_a_t\">"
    a_list = []
    x = page.find(article_tag)
    while x > -1:
        page = page[x+len(article_tag):]
        y = page.find("</tr>")
        pstr = page[:y]
        page = page[y:]
        new_article = Article()

        # Link to Scholar paper page
        y = pstr.find("href")
        tstr = pstr[y+6:]
        tstr = tstr[:tstr.find("\"")]
        new_article.googleScholarURL = tstr.replace("&amp;", "&")

        # Title
        tstr = pstr[pstr.find("gsc_a_at")+10:]
        tstr = tstr[:tstr.find("</a>")]
        new_article.title = tstr

        # Authors
        tstr = pstr[pstr.find("gs_gray")+9:]
        tstr = tstr[:tstr.find("</div>")]
        clean_authors(new_article, tstr)

        # Year
        y = pstr.find("gs_oph")
        if y == -1:
            tstr = pstr[pstr.find("gsc_a_h")+9:]
        else:
            tstr = pstr[y+10:]
        tstr = tstr[:tstr.find("</span>")]
        new_article.year = int(tstr)
     
        # Citations
        tstr = pstr[pstr.find("href", pstr.find("href")+1)+6:]
        new_article.citationURL = tstr[:tstr.find("\"")].replace("&amp;", "&")
        tstr = tstr[tstr.find("gsc_a_ac")+10:]
        tmpcnt = tstr[:tstr.find("</a>")]
        if tmpcnt == "&nbsp;":
            tmpcnt = "0"
        new_article.citations = [int(tmpcnt)]

        a_list.append(new_article)
        x = page.find(article_tag)
    return a_list


def get_citing_article_info(article: Article) -> None:
    site = article.citationURL
    print(site)
    site = "http://scholar.google.com/scholar?cites=12480068626253116047,8651933093376463528"
    page = get_webpage(site, "utf-8")
    page = trim_header(page)
    article_tag = "<h3 class=\"gs_rt\">"
    # alist = []
    x = page.find(article_tag)
    while x > -1:
        # new_cite = CitingArticle()
        y = page.find("<h3", page.find("<h3")+1)
        pstr = page[:y]
        page = page[y:]
        tstr = pstr[pstr.find("<div class=\"gs_a\">")+18:]
        tstr = tstr[:tstr.find(" - ")]
        print(tstr)
        x = page.find(article_tag)

            
# -----------------------------------------------------
# fetch data from Google Scholar
# -----------------------------------------------------
def get_data_from_google_scholar() -> Tuple[list, list]:
    # user input
    default_value = "exyen9EAAAAJ"
    in_code = input("Google Scholar ID number (example: " + default_value + "): ")
    if in_code == "":
        in_code = default_value
    max_papers = "1000"  # assume no one has published more than 1000 papers
    site = "https://scholar.google.com/citations?hl=en&pagesize=" + max_papers + "&user=" + in_code
    page = get_webpage(site, "utf-8")
    page = trim_header(page)
    scholar_name = find_scholar_name(page)
    standard_name = standardize_author(scholar_name)
    print("Impact factors for " + scholar_name)
    article_list = find_gs_articles(page)
    for a in article_list:
        detect_author_order(a, standard_name)
    date_list = [datetime.datetime.now()]
    print("Found", len(article_list), "publications")
    # checking citing articles
    # for a in article_list:
    #    getCitingArticleInfo(a)
    return date_list, article_list


# -----------------------------------------------------
# pre-determined data files
# -----------------------------------------------------
def prompt_file_name(prompt: str, default: str) -> str:
    file_name = input("Name of " + prompt + " (default: \"" + default + "\"): ")
    if file_name.strip() == "":
        file_name = default
    return file_name
    

def get_data_from_files(inc_self: bool) -> Tuple[list, list]:
    # user input
    in_name = prompt_file_name("citation file", "Citations.txt")
    date_list, article_list = read_data_file(in_name)
    if inc_self:
        self_name = prompt_file_name("self-citation file", "Citations-Self.txt")
        coauth_name = prompt_file_name("coauthor-citation file", "Citations-Coauthor.txt")
        read_self_citation_files(article_list, self_name, coauth_name)
    return date_list, article_list


# -----------------------------------------------------
# main loop
# -----------------------------------------------------
def main():
    print("Personal Impact Factor Calculator")
    print()
    print("Source of data:")
    print(" (1) Pre-determined data files")
    print(" (2) Retrieve data from Google Scholar")
    valid_choice = ("1", "2", "")
    data_choice = "x"
    while data_choice not in valid_choice:
        data_choice = input("Enter 1 or 2 (default = 1): ")
    print()

    if data_choice != "2":  # temp
        self_str = input("Include self-citation measures? (y/n) (default = y) ")
        if (self_str.strip() == "") or (self_str.strip().lower() == "y"):
            inc_self = True
        else:
            inc_self = False
        print()
    else:
        inc_self = False
        
    if data_choice == "1" or data_choice == "":
        date_list, article_list = get_data_from_files(inc_self)
    else:
        date_list, article_list = get_data_from_google_scholar()

    out_name = input("Name of output file (default = \"impactfactors.txt\"): ")
    if out_name.strip() == "":
        out_name = "impactfactors.txt"
    print()

    # webstr = input("Create webpages? (y/n) (deafult = y) ")
    # if (webstr.strip() == "") or (webstr.strip().lower() == "y"):
    #     do_web = True
    # else:
    #     do_web = False

    # calculate metrics for every year
    metric_list = []
    for y in range(len(date_list)):
        metric_list.append(calculate_metrics(y, date_list, article_list, inc_self))

    # calculate metrics which use cross-year data
    calculate_dynamic_h(metric_list)
    calculate_impact_vitality(metric_list)
    calculate_least_squares_h_rate(metric_list)

    # output
    write_output(out_name, date_list, metric_list, inc_self)

    # if do_web:
    #     write_webpages(date_list, metric_list, inc_self)

    print("Finished")


if __name__ == "__main__":
    main()
