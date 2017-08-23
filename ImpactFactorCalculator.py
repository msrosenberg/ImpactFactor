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
        self.totalPubs = 0
        self.totalCites = 0
        self.citesPerPub = 0
        self.maxCites = 0
        self.cumulativeCites = []
        self.h_index = 0
        self.Hirsch_minConst = 0
        self.Hirsch_mQuotient = 0  # a.k.a. h-rate, age-normalized h-index (hN), and Carbon h-factor
        self.coreCites = 0
        self.g_index = 0
        self.a_index = 0
        self.h2_index = 0
        self.hg_index = 0
        self.q2_index = 0
        self.r_index = 0
        self.rm_index = 0
        self.m_index = 0
        self.ar_index = 0
        self.h2_lower = 0
        self.h2_center = 0
        self.h2_upper = 0
        self.Tol_t_index = 0
        self.Tol_f_index = 0
        self.gf_cite = 0
        self.gF_paper = 0
        self.Franceschini_f_index = 0
        self.k_index = 0
        self.contemp_h_index = 0
        self.tapered_h_index = 0
        self.rational_h_index = 0
        self.Wu_w_index = 0
        self.Wu_wq_index = 0
        self.mu_index = 0
        self.v_index = 0
        self.normalized_h_index = 0
        self.e_index = 0
        self.pi_index = 0
        self.p_index = 0
        self.fractional_p_index = 0
        self.harmonic_p_index = 0
        self.ph_ratio = 0
        self.maxprod_index = 0
        self.specificImpact_s_index = 0
        self.multiDim_h_index = []
        self.Woeginger_w_index = 0
        self.Wohlin_w_index = 0
        self.hpd_index = 0
        self.hi_index = 0
        self.pure_h_index = 0
        self.pure_h_proportional = 0
        self.pure_h_geometric = 0
        self.adapted_pure_h_index = 0
        self.adapted_pure_h_proportional = 0
        self.adapted_pure_h_geometric = 0
        self.weighted_h_index = 0
        self.j_index = 0
        self.real_h_index = 0
        self.hj_index = []
        self.dynamic_h_index = 0
        self.hF_hm_index = 0
        self.hf_norm_hi_index = 0
        self.b10_index = 0
        self.bavg_self_index = 0
        self.bavg_all_index = 0
        self.sharpself_h_index = 0
        self.sharpall_h_index = 0
        self.total_self_only_cites = 0
        self.total_self_all_cites = 0
        self.avg_self_only_cites = 0
        self.avg_self_all_cites = 0
        self.trend_h_index = 0
        self.impactVitality = 0
        self.profit_index = 0
        self.profit_adj_h_index = 0
        self.profit_h_index = 0
        self.posweighted_h_index = 0
        self.citation_aggreg_frac = 0
        self.citation_aggreg_prop = 0
        self.citation_hcut_frac = 0
        self.citation_hcut_prop = 0
        self.two_sided_h_index = []
        self.iteratively_weighted_h_index = 0
        self.em_index = 0
        self.emp_index = 0
        self.ls_hrate = 0


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
    metrics.totalPubs = 0
    metrics.totalCites = 0
    metrics.maxCites = 0
    firstyear = articlelist[0].year
    for article in articlelist:
        if article.year < firstyear:
            firstyear = article.year
        if article.citations[y] != -1:
            cur_list.append(article)
            metrics.totalPubs = metrics.totalPubs + 1
            metrics.totalCites = metrics.totalCites + article.citations[y]
            if metrics.maxCites < article.citations[y]:
                metrics.maxCites = article.citations[y]
    metrics.citesPerPub = metrics.totalCites / metrics.totalPubs

    # construct sublists for active articles only
    n = len(cur_list)
    cites = []
    rcites = []
    metrics.cumulativeCites = []
    fcum = []
    tcum = []
    cum_rank = []
    medarray = []
    cur_age = []
    cites_per_year = []
    is_core = []
    for i in range(n):
        cites.append(0)
        cur_age.append(0)
        cites_per_year.append(0)
        metrics.cumulativeCites.append(0)
        cum_rank.append(0)
        fcum.append(0)
        tcum.append(0)
        medarray.append(0)
        is_core.append(False)
        rcites.append(0)
    minfyear = 0
    maxfyear = 0
    i = -1
    for article in cur_list:
        i = i + 1
        if article.citations[y] > 0: 
            if minfyear == 0:
                minfyear = article.year
                maxfyear = minfyear
            else:
                if article.year > maxfyear:
                    maxfyear = article.year
                if article.year < minfyear:
                    minfyear = article.year
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
            metrics.cumulativeCites[i] = (metrics.cumulativeCites[i-1] +
                                          cites[tmpindex[n-i-1]])
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
                j = j + 1
                article.rank = rankorder[j]

    # basic indices
    metrics.h_index = 0
    metrics.coreCites = 0
    for i in range(n):
        if rankorder[i] <= cites[i]:
            is_core[i] = True
            metrics.h_index += 1
            metrics.coreCites = metrics.coreCites + cites[i]
    metrics.Hirsch_minConst = metrics.totalCites / metrics.h_index**2
    # if datelist[y].year - firstyear != 0:
    #     metrics.Hirsch_mQuotient = metrics.h_index / (datelist[y].year - firstyear)
    # else:
    #     metrics.Hirsch_mQuotient = -1
    # changed this to reflect logic in Todeschini and Baccini (2016)
    metrics.Hirsch_mQuotient = metrics.h_index / (datelist[y].year - firstyear + 1)

    # other indices
    metrics.g_index = calculate_g_index(n, rankorder, metrics.cumulativeCites)
    metrics.h2_index = calculate_h2_index(n, rankorder, cites)
    metrics.hg_index = calculate_hg_index(metrics.h_index, metrics.g_index)
    if incself:
        (metrics.avg_self_only_cites,
         metrics.total_self_only_cites,
         metrics.sharpself_h_index) = calculate_sharpened_h_index(n, y, cur_list, cites, False)
        metrics.bavg_self_index = calculate_b_index(metrics.h_index, 1-metrics.avg_self_only_cites)
        (metrics.avg_self_all_cites,
         metrics.total_self_all_cites,
         metrics.sharpall_h_index) = calculate_sharpened_h_index(n, y, cur_list, cites, True)
        metrics.bavg_all_index = calculate_b_index(metrics.h_index, 1-metrics.avg_self_all_cites)
        metrics.b10_index = calculate_b_index(metrics.h_index, 0.9)
    metrics.a_index = calculate_a_index(metrics.coreCites, metrics.totalPubs)
    metrics.real_h_index = calculate_real_h_index(n, rankorder, metrics.h_index, cites)
    metrics.r_index = calculate_r_index(metrics.coreCites)
    metrics.rm_index = calculate_rm_index(n, is_core, cites)
    metrics.ar_index = calculate_ar_index(n, is_core, cites_per_year)
    metrics.m_index = calculate_m_index(n, is_core, metrics.h_index, cites)
    metrics.q2_index = calculate_q2_index(metrics.h_index, metrics.m_index)
    metrics.k_index = calculate_k_index(metrics.totalCites, metrics.coreCites, metrics.totalPubs)
    metrics.Franceschini_f_index = calculate_franceschini_f_index(maxfyear, minfyear)
    metrics.weighted_h_index = calculate_weighted_h_index(n, cites, metrics.cumulativeCites, rankorder, metrics.h_index)
    metrics.normalized_h_index = calculate_normalized_h(metrics.h_index, metrics.totalPubs)
    metrics.v_index = calculate_v_index(metrics.h_index, metrics.totalPubs)
    metrics.e_index = calculate_e_index(metrics.coreCites, metrics.h_index)
    metrics.rational_h_index = calculate_rational_h(n, is_core, cites, metrics.h_index, rankorder)
    (metrics.h2_upper,
     metrics.h2_center,
     metrics.h2_lower) = calculate_h2percs(metrics.coreCites, metrics.h_index, metrics.totalCites)
    metrics.tapered_h_index = calculate_tapered_h_index(n, cites, rankorder)
    metrics.pi_index = calculate_pi_index(n, metrics.totalPubs, rankorder, cites)
    (metrics.p_index,
     metrics.ph_ratio,
     metrics.fractional_p_index) = calculate_prathap_p_index(metrics.totalCites, metrics.totalPubs, metrics.h_index,
                                                             cur_list, y)
    metrics.harmonic_p_index = calculate_prathap_harmonic_p(cur_list, y)
    metrics.hi_index, metrics.pure_h_index = calculate_hi_pure(n, is_core, cur_list, metrics.h_index)
    metrics.pure_h_proportional, metrics.pure_h_geometric = calculate_pure_order(n, is_core, cur_list, metrics.h_index)
    metrics.Tol_f_index, metrics.Tol_t_index = calculate_tol_indices(n, rankorder, fcum, tcum)
    metrics.mu_index = calculate_mu_index(n, rankorder, medarray)
    metrics.Wu_w_index, metrics.Wu_wq_index = calculate_wu_w(n, cites, rankorder)
    metrics.Wohlin_w_index = calculate_wohlin_w(n, metrics.maxCites, cites)
    metrics.contemp_h_index = calculate_contemporary_h(n, cites, cur_age)
    metrics.hpd_index = calculate_hpd_seniority(n, cites_per_year)
    metrics.specificImpact_s_index = calculate_impact_s_index(n, cur_age, metrics.totalCites)
    metrics.hF_hm_index, metrics.gF_paper = calculate_fractional_paper_indices(n, rankorder, cites, cum_rank,
                                                                               metrics.cumulativeCites)
    metrics.multiDim_h_index = calculate_multidimensional_h(metrics.h_index, n, is_core, rankorder, cites)
    metrics.two_sided_h_index = calculate_two_sided_h(metrics.h_index, metrics.multiDim_h_index, n, rankorder, cites)
    metrics.iteratively_weighted_h_index = calculate_iteratively_weighted_h_index(metrics.multiDim_h_index)
    metrics.hf_norm_hi_index, metrics.gf_cite = calculate_hinorm(n, cites, cur_list)
    (metrics.posweighted_h_index,
     metrics.citation_aggreg_prop,
     metrics.citation_hcut_prop) = calculate_weightedaggregate_prop(n, cites, cur_list)
    metrics.citation_aggreg_frac, metrics.citation_hcut_frac = calculate_weightedaggregate_fract(n, cites, cur_list)
    metrics.Woeginger_w_index = calculate_woeginger_w(n, rankorder, cites)
    metrics.maxprod_index = calculate_maxprod(n, cites, rankorder)
    metrics.j_index = calculate_j_index(n, cites, metrics.h_index)
    metrics.adapted_pure_h_index = calculate_adapated_pure_h(n, cites, cur_list)
    metrics.adapted_pure_h_proportional = calculate_adapated_pure_h_prop(n, cites, cur_list)
    metrics.adapted_pure_h_geometric = calculate_adapated_pure_h_geom(n, cites, cur_list)
    (metrics.profit_index,
     metrics.profit_adj_h_index,
     metrics.profit_h_index) = calculate_profit_indices(n, cur_list, cites, metrics.h_index)
    metrics.hj_index = calculate_hj_indices(metrics.totalPubs, metrics.h_index, rcites)
    metrics.trend_h_index = calculate_trend_h(n, cur_list, y, datelist)
    metrics.em_index, metrics.emp_index = calculate_em_index(n, rankorder, cites)

    return metrics


# -----------------------------------------------------
# Special metric calculations that require data from multiple time points
# -----------------------------------------------------

# dynamic h-type-index (Rousseau and Ye 2008)
def calculate_dynamic_h(metric_list: list) -> None:
    metric = metric_list[0]
    metric.dynamic_h_index = -1
    for m in range(1, len(metric_list)):
        avgh = 0
        avgd = 0
        for i in range(m+1):
            metric = metric_list[i]
            avgh += metric.rational_h_index
            avgd += date_to_int(metric.date)
        avgh /= m + 1
        avgd /= m + 1
        sumxy = 0
        sumx2 = 0
        for i in range(m+1):
            metric = metric_list[i]
            sumxy += (metric.rational_h_index - avgh) * (date_to_int(metric.date) - avgd)
            sumx2 += (date_to_int(metric.date) - avgd)**2
        metric = metric_list[m]
        metric.dynamic_h_index = 365 * metric.r_index * (sumxy / sumx2)


# impact vitality (Rons and Amez 2008, 2009)
def calculate_impact_vitality(metric_list: list) -> None:
    if len(metric_list) < 6:
        for metric in metric_list:
            metric.impactVitality = -1        
    else:
        w = 5  # fix at a 5 year window
        for i in range(w-1):
            metric = metric_list[i]
            metric.impactVitality = -1
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
                tc = metric.totalCites
                if m - i != 0:
                    metric = metric_list[m - i - 1]
                    tc -= metric.totalCites
                nd += tc
                nn += tc / (i + 1)
                
            # calculate value
            metric = metric_list[m]
            metric.impactVitality = (w * (nn / nd) - 1) / d


# least-squares h-rate (Burrell 2007)
def calcluate_least_squares_h_rate(metric_list: list) -> None:
    first_year = metric_list[0].date.year
    for m in range(len(metric_list)):
        avgh = 0
        avgd = 0
        for i in range(m+1):
            metric = metric_list[i]
            avgh += metric.h_index
            avgd += metric.date.year - first_year + 1
        avgh /= m + 1
        avgd /= m + 1
        sumxy = 0
        sumx2 = 0
        for i in range(m+1):
            metric = metric_list[i]
            sumxy += (metric.h_index - avgh) * (metric.date.year - avgd)
            sumx2 += (metric.date.year - avgd)**2
        metric = metric_list[m]
        metric.ls_hrate = sumxy/sumx2


# -----------------------------------------------------
# output all results
# -----------------------------------------------------
def write_output(fname: str, datelist: list, metriclist: list, incself: bool) -> None:
    fstr = '1.4f'  # constant formatting string
    with open(fname, "w") as outfile:
        # write header
        outfile.write('Date')
        for date in datelist:
            outfile.write(tb + date_to_string(date))
        outfile.write("\n")

        # write metrics
        # Raw data metrics
        outfile.write('Total Publications')
        for metric in metriclist:
            outfile.write(tb + str(metric.totalPubs))
        outfile.write("\n")

        outfile.write('Total Citations')
        for metric in metriclist:
            outfile.write(tb + str(metric.totalCites))
        outfile.write("\n")

        outfile.write('Citations per Pub')
        for metric in metriclist:
            outfile.write(tb + format(metric.citesPerPub, fstr))
        outfile.write("\n")

        outfile.write('Max Citations')
        for metric in metriclist:
            outfile.write(tb + str(metric.maxCites))
        outfile.write("\n")

        # Core definitions
        outfile.write('h-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.h_index))
        outfile.write("\n")

        outfile.write('Hirsch-core citations')
        for metric in metriclist:
            outfile.write(tb + str(metric.coreCites))
        outfile.write("\n")

        outfile.write('Hirsch Min Constant (a)')
        for metric in metriclist:
            outfile.write(tb + format(metric.Hirsch_minConst, fstr))
        outfile.write("\n")

        outfile.write('g-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.g_index))
        outfile.write("\n")

        outfile.write('f-index (Tol)')
        for metric in metriclist:
            outfile.write(tb + str(metric.Tol_f_index))
        outfile.write("\n")

        outfile.write('t-index (Tol)')
        for metric in metriclist:
            outfile.write(tb + str(metric.Tol_t_index))
        outfile.write("\n")

        outfile.write('mu-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.mu_index))
        outfile.write("\n")

        outfile.write('w-index (Woeginger)')
        for metric in metriclist:
            outfile.write(tb + str(metric.Woeginger_w_index))
        outfile.write("\n")

        outfile.write('h(2)-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.h2_index))
        outfile.write("\n")

        outfile.write('w-index (Wu)')
        for metric in metriclist:
            outfile.write(tb + str(metric.Wu_w_index))
        outfile.write("\n")

        outfile.write('hg-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.hg_index, fstr))
        outfile.write("\n")

        # Full citation indices
        outfile.write('rational h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.rational_h_index, fstr))
        outfile.write("\n")

        outfile.write('real h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.real_h_index, fstr))
        outfile.write("\n")

        outfile.write('w(q) (Wu)')
        for metric in metriclist:
            outfile.write(tb + str(metric.Wu_wq_index))
        outfile.write("\n")

        outfile.write('tapered h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.tapered_h_index, fstr))
        outfile.write("\n")

        outfile.write('j-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.j_index, fstr))
        outfile.write("\n")

        outfile.write('w-index (Wohlin)')
        for metric in metriclist:
            outfile.write(tb + format(metric.Wohlin_w_index, fstr))
        outfile.write("\n")

        outfile.write('hj-indices')
        for metric in metriclist:
            outfile.write(tb + str(metric.hj_index))
        outfile.write("\n")

        # Core description indices
        outfile.write('v-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.v_index, fstr))
        outfile.write("\n")

        outfile.write('normalized h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.normalized_h_index, fstr))
        outfile.write("\n")

        outfile.write('a-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.a_index, fstr))
        outfile.write("\n")

        outfile.write('m-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.m_index, fstr))
        outfile.write("\n")

        outfile.write('r-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.r_index, fstr))
        outfile.write("\n")

        outfile.write('rm-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.rm_index, fstr))
        outfile.write("\n")

        outfile.write('weighted h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.weighted_h_index, fstr))
        outfile.write("\n")

        outfile.write('pi-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.pi_index, fstr))
        outfile.write("\n")

        outfile.write('q2-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.q2_index, fstr))
        outfile.write("\n")

        outfile.write('e-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.e_index, fstr))
        outfile.write("\n")

        outfile.write('maxprod-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.maxprod_index))
        outfile.write("\n")

        # Core vs. tail indices
        outfile.write('h2-upper index')
        for metric in metriclist:
            outfile.write(tb + format(metric.h2_upper, fstr))
        outfile.write("\n")

        outfile.write('h2-center index')
        for metric in metriclist:
            outfile.write(tb + format(metric.h2_center, fstr))
        outfile.write("\n")

        outfile.write('h2-tail index')
        for metric in metriclist:
            outfile.write(tb + format(metric.h2_lower, fstr))
        outfile.write("\n")

        outfile.write('k-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.k_index, fstr))
        outfile.write("\n")

        outfile.write('p-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.p_index, fstr))
        outfile.write("\n")

        outfile.write('ph-ratio')
        for metric in metriclist:
            outfile.write(tb + format(metric.ph_ratio, fstr))
        outfile.write("\n")

        outfile.write('multidimensional h-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.multiDim_h_index))
        outfile.write("\n")

        outfile.write('two-sided h-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.two_sided_h_index))
        outfile.write("\n")

        outfile.write('iteratively weighted h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.iteratively_weighted_h_index, fstr))
        outfile.write("\n")

        outfile.write('EM-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.em_index, fstr))
        outfile.write("\n")

        outfile.write('EM\'-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.emp_index, fstr))
        outfile.write("\n")

        # Multiple-author indices
        outfile.write('hi-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.hi_index, fstr))
        outfile.write("\n")

        outfile.write('pure h-index (fractional credit)')
        for metric in metriclist:
            outfile.write(tb + format(metric.pure_h_index, fstr))
        outfile.write("\n")

        outfile.write('pure h-index (proportional credit)')
        for metric in metriclist:
            outfile.write(tb + format(metric.pure_h_proportional, fstr))
        outfile.write("\n")

        outfile.write('pure h-index (geometric credit)')
        for metric in metriclist:
            outfile.write(tb + format(metric.pure_h_geometric, fstr))
        outfile.write("\n")

        outfile.write('adapted pure h-index (fractional credit)')
        for metric in metriclist:
            outfile.write(tb + format(metric.adapted_pure_h_index, fstr))
        outfile.write("\n")

        outfile.write('adapted pure h-index (proportional credit)')
        for metric in metriclist:
            outfile.write(tb + format(metric.adapted_pure_h_proportional, fstr))
        outfile.write("\n")

        outfile.write('adapted pure h-index (geometric credit)')
        for metric in metriclist:
            outfile.write(tb + format(metric.adapted_pure_h_geometric, fstr))
        outfile.write("\n")

        outfile.write('hf-index/normalized hi-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.hf_norm_hi_index))
        outfile.write("\n")

        outfile.write('hF-index/hm-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.hF_hm_index, fstr))
        outfile.write("\n")

        outfile.write('position-weighted h-index hp')
        for metric in metriclist:
            outfile.write(tb + str(metric.posweighted_h_index))
        outfile.write("\n")

        outfile.write('weighted citation aggregate (fractional)')
        for metric in metriclist:
            outfile.write(tb + format(metric.citation_aggreg_frac, fstr))
        outfile.write("\n")

        outfile.write('weighted citation aggregate (proportional)')
        for metric in metriclist:
            outfile.write(tb + format(metric.citation_aggreg_prop, fstr))
        outfile.write("\n")

        outfile.write('weighted citation H-cut (fractional)')
        for metric in metriclist:
            outfile.write(tb + format(metric.citation_hcut_frac, fstr))
        outfile.write("\n")

        outfile.write('weighted citation H-cut (proportional)')
        for metric in metriclist:
            outfile.write(tb + format(metric.citation_hcut_prop, fstr))
        outfile.write("\n")

        outfile.write('gf-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.gf_cite))
        outfile.write("\n")

        outfile.write('gF-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.gF_paper, fstr))
        outfile.write("\n")

        outfile.write('fractional p-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.fractional_p_index, fstr))
        outfile.write("\n")

        outfile.write('harmonic p-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.harmonic_p_index, fstr))
        outfile.write("\n")

        outfile.write('profit p-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.profit_index, fstr))
        outfile.write("\n")

        outfile.write('profit adjusted h-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.profit_adj_h_index))
        outfile.write("\n")

        outfile.write('profit h-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.profit_h_index, fstr))
        outfile.write("\n")

        # Self-citation indices
        if incself:
            outfile.write('total self citations')
            for metric in metriclist:
                outfile.write(tb + str(metric.total_self_only_cites))
            outfile.write("\n")

            outfile.write('total self citation rate')
            for metric in metriclist:
                outfile.write(tb + format(metric.total_self_only_cites / metric.totalCites, fstr))
            outfile.write("\n")

            outfile.write('average self citation rate')
            for metric in metriclist:
                outfile.write(tb + format(metric.avg_self_only_cites, fstr))
            outfile.write("\n")

            outfile.write('sharpened h-index (self citations only)')
            for metric in metriclist:
                outfile.write(tb + str(metric.sharpself_h_index))
            outfile.write("\n")

            outfile.write('b-index (avg self citation rate)')
            for metric in metriclist:
                outfile.write(tb + format(metric.bavg_self_index, fstr))
            outfile.write("\n")

            outfile.write('total self & coauthor citations')
            for metric in metriclist:
                outfile.write(tb + str(metric.total_self_all_cites))
            outfile.write("\n")

            outfile.write('total self & coauthor citation rate')
            for metric in metriclist:
                outfile.write(tb + format(metric.total_self_all_cites / metric.totalCites, fstr))
            outfile.write("\n")

            outfile.write('average self & coauthor citation rate')
            for metric in metriclist:
                outfile.write(tb + format(metric.avg_self_all_cites, fstr))
            outfile.write("\n")

            outfile.write('sharpened h-index (self & coauthor citations)')
            for metric in metriclist:
                outfile.write(tb + str(metric.sharpall_h_index))
            outfile.write("\n")

            outfile.write('b-index (avg self & coauthor citation rate)')
            for metric in metriclist:
                outfile.write(tb + format(metric.bavg_all_index, fstr))
            outfile.write("\n")

            outfile.write('b-index (10% self-citation rate)')
            for metric in metriclist:
                outfile.write(tb + format(metric.b10_index, fstr))
            outfile.write("\n")

        # Time-based indices
        outfile.write('Hirsch m-quotient (slope)/h-rate')
        for metric in metriclist:
            outfile.write(tb + format(metric.Hirsch_mQuotient, fstr))
            # if metric.Hirsch_mQuotient == -1:
            #     outfile.write(tb + 'n/a')
            # else:
            #     outfile.write(tb + format(metric.Hirsch_mQuotient, fstr))
        outfile.write("\n")

        outfile.write('Least squares h-rate (slope)')
        for metric in metriclist:
            outfile.write(tb + format(metric.ls_hrate, fstr))
        outfile.write("\n")

        outfile.write('ar-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.ar_index, fstr))
        outfile.write("\n")

        outfile.write('dynamic h-type-index')
        for metric in metriclist:
            if metric.dynamic_h_index < 0:
                outfile.write(tb + 'n/a')
            else:
                outfile.write(tb + format(metric.dynamic_h_index, fstr))
        outfile.write("\n")

        outfile.write('hpd-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.hpd_index))
        outfile.write("\n")

        outfile.write('contemporary h-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.contemp_h_index))
        outfile.write("\n")

        outfile.write('trend h-index')
        for metric in metriclist:
            outfile.write(tb + str(metric.trend_h_index))
        outfile.write("\n")

        outfile.write('impact vitality')
        for metric in metriclist:
            if metric.impactVitality < 0:
                outfile.write(tb + 'n/a')
            else:
                outfile.write(tb + format(metric.impactVitality, fstr))
        outfile.write("\n")

        outfile.write('specific impact s-index')
        for metric in metriclist:
            outfile.write(tb + format(metric.specificImpact_s_index, fstr))
        outfile.write("\n")

        outfile.write('f-index (Franceschini & Maisano)')
        for metric in metriclist:
            outfile.write(tb + str(metric.Franceschini_f_index))
        outfile.write("\n")


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

    print("Finished")


if __name__ == "__main__":
    main()
