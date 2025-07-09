"""
Impact Factor Functions

This module is designed to provide the functions necessary to calculate the various impact factors
from generic data, without the reliance on the special class structure of the greater program
"""

import math
import datetime
from typing import Tuple, Union, Optional
import scipy
import itertools


Number = Union[int, float]


# --- General Support Functions ---
def rank(n: int, indx: list) -> list:
    irank = [0 for _ in range(n)]
    for j in range(n):
        irank[indx[j]] = j
    return irank


def sort_and_rank(sort_list: list, n: int) -> Tuple[list, list]:
    tmpindex = sorted(range(n), key=lambda k: sort_list[k])
    tmprank = rank(n, tmpindex)
    # reverse so #1 is largest
    # NOTE: the ranks in rank_order go from 1 to n, rather than 0 to n-1
    rank_order = []
    for i in range(n):
        rank_order.append(n - tmprank[i])
    return tmpindex, rank_order


def calculate_median(values: list) -> Number:
    sort_values = [v for v in values]  # make sorted copy of input list
    sort_values.sort(reverse=True)
    n = len(values)
    j = n // 2
    if n % 2 == 0:  # odd number of values in list
        return (sort_values[j] + sort_values[j - 1]) / 2
    else:  # even number of values in list
        return sort_values[j]


def calculate_ranks(citations: list) -> Tuple[list, list]:
    n = len(citations)
    cumulative_citations = [0 for _ in range(n)]

    # sort by number of citations
    tmp_index, rank_order = sort_and_rank(citations, n)
    for i in range(n):
        if i > 0:
            cumulative_citations[i] = cumulative_citations[i-1] + citations[tmp_index[n-i-1]]
        else:
            cumulative_citations[i] = citations[tmp_index[n-i-1]]
    return rank_order, cumulative_citations


def publication_ages(year: int, pub_years: list) -> list:
    """
    returns a list containing the age of each publication
    """
    return [year - p + 1 for p in pub_years]


def citations_per_year(citations: list, pub_ages: list) -> list:
    """
    returns a list containing the citations per year for each publication
    """
    return [citations[i]/pub_ages[i] for i in range(len(citations))]


def total_citations_each_year(total_cite_list: list) -> list:
    """
    returns a list containing the total citations received (across all pubs) each year

    input is a cumulative citation count
    """
    tcpy = [total_cite_list[0]]
    for i in range(1, len(total_cite_list)):
        tcpy.append(total_cite_list[i] - total_cite_list[i - 1])
    return tcpy


def author_effort(measure: str, n_authors: int, author_pos: int = 1) -> float:
    """
    returns the estimated effort of an author for a publication
    """
    if measure == "fractional":
        return 1 / n_authors
    elif measure == "proportional":
        return 2*(n_authors + 1 - author_pos) / (n_authors*(n_authors + 1))
    elif measure == "geometric":
        return 2**(n_authors - author_pos) / (2**n_authors - 1)
    elif measure == "harmonic":
        n = 1 / author_pos
        d = sum(1/(i+1) for i in range(n_authors))
        return n/d
    elif measure == "harmonic_aziz":
        # this is a more complicated form of the harmonic that includes an additional factor
        if n_authors % 2 == 0:
            d = 0
        else:
            d = 1 / (2*n_authors)
        return (1 + abs(n_authors + 1 - 2*author_pos)) / ((n_authors**2)/2 + n_authors*(1 - d))
    else:
        return 1


def citations_per_pub_per_year(pub_list: list) -> list:
    def convert_none(x) -> int:
        if x is None:
            return 0
        else:
            return x

    # take total citations for each pub at each year and convert to yearly only totals
    pub_cites = []
    for p in pub_list:
        cites = [convert_none(p[0])]
        for i in range(1, len(p)):
            cites.append(convert_none(p[i]) - convert_none(p[i-1]))
        pub_cites.append(cites)
    return pub_cites


# --- Metric Calculations ---

# Total Publications
def calculate_total_pubs(citations: list) -> int:
    return len(citations)


# Total Citations
def calculate_total_cites(citations: list) -> int:
    return sum(citations)


# Maximum Citations
def calculate_max_cites(citations) -> int:
    return max(citations)


# Mean Citations
def calculate_mean_cites(total_cites: int, total_pubs: int) -> float:
    return total_cites / total_pubs


# Median Citations
def calculate_median_cites(citations: list) -> Number:
    return calculate_median(citations)


# h-index (Hirsch )
def calculate_h_index(citations: list, rank_order: list) -> Tuple[int, list]:
    """
    This function calculates both the h-index and returns a boolean list of
    whether a particular publication is part of the core
    """
    h = 0
    is_core = [False for _ in rank_order]
    for i in range(len(citations)):
        if rank_order[i] <= citations[i]:
            h += 1
            is_core[i] = True
    return h, is_core


# Hirsch core citations (Hirsch )
# this is the sum of the citations within the core
def calculate_h_core(citations: list, is_core: list) -> int:
    core_cites = 0
    for i in range(len(citations)):
        if is_core[i]:
            core_cites += citations[i]
    return core_cites


# Hirsch minimum constant
def calculate_hirsch_min_const(total_cites: int, h: int) -> float:
    return total_cites / h**2


# g-index (Egghe 2006)
def calculate_g_index(cumulative_citations: list, rank_order: list) -> int:
    g = 0
    for i in range(len(rank_order)):
        if rank_order[i]**2 <= cumulative_citations[rank_order[i]-1]:
            g += 1
    return g


# h2-index (Kosmulski 2006)
def calculate_h2_index(citations: list, rank_order: list) -> int:
    h2_index = 0
    for i in range(len(rank_order)):
        if rank_order[i] <= math.sqrt(citations[i]):
            h2_index += 1
    return h2_index


# hg-index (Alonso et al 2010)
def calculate_hg_index(h: int, g: int) -> float:
    return math.sqrt(h*g)


# total self citations
def calculate_total_self_cites(self_citations: list) -> int:
    return sum(self_citations)


# total self-citation rate
def calculate_total_self_cite_rate(total_self_cites: int, total_cites: int) -> float:
    return total_self_cites/total_cites


# mean self-citation rate
def calculate_mean_self_cite_rate(self_citations: list, all_citations: list) -> float:
    mean_rate = 0
    for i in range(len(self_citations)):
        if all_citations[i] != 0:
            mean_rate += self_citations[i] / all_citations[i]
    return mean_rate / len(self_citations)


# sharpened h-index (Schreiber 2007)
def calculate_sharpened_h_index(self_citations: list, all_citations: list) -> int:
    sharp_citations = [all_citations[i] - self_citations[i] for i in range(len(self_citations))]
    _, tmprank = sort_and_rank(sharp_citations, len(sharp_citations))
    sharp_h_index = 0
    for i in range(len(sharp_citations)):
        if tmprank[i] <= sharp_citations[i]:
            sharp_h_index += 1
    return sharp_h_index


# b-index (Brown 2009)
def calculate_b_index(h: int, avg_rate: float) -> float:
    return h * avg_rate**0.75


# real h-index (hr-index) (Guns and Rousseau 2009)
def calculate_real_h_index(citations: list, rank_order: list, h: int) -> Number:
    j = -1
    k = -1
    for i in range(len(citations)):
        if rank_order[i] == h:
            j = i
        elif rank_order[i] == h + 1:
            k = i
    if (k != -1) and (j != -1):
        return ((h + 1) * citations[j] - h * citations[k]) / (1 - citations[k] + citations[j])
    else:
        return h


# a-index (Jin 2006; Rousseau 2006)
# def calculate_a_index(core_cites: int, total_pubs: int) -> float:
def calculate_a_index(core_cites: int, h: int) -> float:
    return core_cites / h


# r-index (Jin et al 2007)
def calculate_r_index(core_cites: int) -> float:
    return math.sqrt(core_cites)


# rm-index (Panaretos and Malesios 2009)
def calculate_rm_index(citations: list, is_core: list) -> float:
    rm_index = 0
    for i in range(len(citations)):
        if is_core[i]:
            rm_index += math.sqrt(citations[i])
    rm_index = math.sqrt(rm_index)
    return rm_index


# ar-index (Jin 2007; Jin et al 2007)
def calculate_ar_index(citations: list, pub_years: list, is_core: list, year: int) -> float:
    pub_ages = publication_ages(year, pub_years)
    cites_per_year = citations_per_year(citations, pub_ages)
    ar_index = 0
    for i in range(len(citations)):
        if is_core[i]:
            ar_index += cites_per_year[i]
    return math.sqrt(ar_index)


# m-index (median index) (Bornmann et al 2008)
def calculate_m_index(citations: list, is_core: list) -> float:
    core_cites = []
    for i, c in enumerate(citations):
        if is_core[i]:
            core_cites.append(c)
    return calculate_median(core_cites)


# q2-index (Cabrerizo et al 2010)
def calculate_q2_index(h: int, m: float) -> float:
    return math.sqrt(h * m)


# k-index (Ye and Rousseau 2010)
def calculate_k_index(total_cites: int, core_cites: int, total_pubs: int) -> float:
    try:
        return (total_cites * core_cites) / (total_pubs * (total_cites - core_cites))
    except ZeroDivisionError:
        return 0


# Franceschini f-index (Franceschini and Maisano 2010)
def calculate_franceschini_f_index(citations: list, pub_years: list) -> int:
    miny = max(pub_years)
    maxy = min(pub_years)
    for i in range(len(citations)):
        if citations[i] > 0:
            miny = min(miny, pub_years[i])
            maxy = max(maxy, pub_years[i])
    return maxy - miny + 1


# weighted h-index (Egghe and Rousseau 2008)
def calculate_weighted_h_index(citations: list, cumulative_citations: list, rank_order: list, h: int) -> float:
    weighted_h_index = 0
    for i in range(len(citations)):
        if citations[i] >= cumulative_citations[rank_order[i]-1] / h:
            weighted_h_index += citations[i]
    return math.sqrt(weighted_h_index)


# normalized h-index (Sidiropoulos et al 2007)
def calculate_normalized_h_index(h: int, total_pubs: int) -> float:
    return h / total_pubs


# apparent h-index (Mohammed et al 2020)
def calculate_apparent_h_index(citations: list, h: int) -> float:
    non_zero_cnt = count_non_zero(citations)
    return h * non_zero_cnt / len(citations)


# chi-index (Fenner et al 2018)
def calculate_chi_index(rec: int) -> float:
    return math.sqrt(rec)


# rec-index (Levene et al 2019)
def calculate_rec_index(sorted_citations: list) -> float:
    rec = 0
    for i, c in enumerate(sorted_citations):
        rec = max(rec, (i+1)*c)
    return rec


# reci-recp (Levene et al 2020)
def calculate_reci_recp(sorted_citations: list, h: int) -> list:
    reci, recp = h**2, h**2
    for i, c in enumerate(sorted_citations):
        if i + 1 <= h:
            reci = max(reci, (i + 1)*c)
        if i + 1 >= h:
            recp = max(recp, (i + 1)*min(c, h))
    return [reci, recp]


# v-index (Riikonen and Vihinen 2008)
def calculate_v_index(h: int, total_pubs: int) -> float:
    return 100 * h / total_pubs


# e-index (Zhang 2009)
def calculate_e_index(core_cites: int, h: int) -> float:
    return math.sqrt(core_cites - h**2)


# rational h-index (Ruane and Tol 2008)
def calculate_rational_h(citations: list, rank_order: list, is_core: list, h: int) -> float:
    j = 0
    for i in range(len(citations)):
        if is_core[i]:
            if citations[i] == h:
                j += 1
        else:
            if rank_order[i] == h + 1:
                j += (h + 1 - citations[i])
    return h + 1 - j/(2*h + 1)


# h2-upper index (Bornmann et al 2010)
def calculate_h2_upper_index(total_cites: int, core_cites: int, h: int) -> float:
    return 100 * (core_cites - h**2) / total_cites


# h2-center index (Bornmann et al 2010)
def calculate_h2_center_index(total_cites: int, h: int) -> float:
    return 100 * h**2 / total_cites


# h2-tail index (Bornmann et al 2010)
def calculate_h2_tail_index(total_cites: int, core_cites: int) -> float:
    return 100 * (total_cites - core_cites) / total_cites


# tapered h-index (Anderson et al 2008)
def calculate_tapered_h_index(citations: list, rank_order: list) -> float:
    n = len(citations)
    ht = []
    for i in range(n):
        ht.append(0)
        if citations[i] <= rank_order[i]:
            ht[i] = citations[i] / (2*rank_order[i] - 1)
        else:
            ht[i] = rank_order[i] / (2*rank_order[i] - 1)
            for j in range(rank_order[i]+1, citations[i]+1):
                ht[i] += 1 / (2*j - 1)
    tapered_h_index = 0
    for i in range(n):
        tapered_h_index += ht[i]
    return tapered_h_index


# pi-index (Vinkler 2009)
def calculate_pi_index(total_pubs: int, citations: list, rank_order: list) -> float:
    p_pi = math.floor(math.sqrt(total_pubs))
    pi_index = 0
    for i in range(len(citations)):
        if rank_order[i] <= p_pi:
            pi_index += citations[i]
    return pi_index / 100


# pi-rate
def calculate_pi_rate(total_pubs: int, pi_index: float) -> float:
    p_pi = math.floor(math.sqrt(total_pubs))
    c_pi = pi_index * 100
    return c_pi / p_pi


# p-index (originally called mock hm-index) (Prathap 2010b, 2011)
def calculate_prathap_p_index(total_cites: int, total_pubs: int) -> float:
    return (total_cites**2 / total_pubs)**(1/3)


# ph-ratio (Prathap 2010b, 2011)
def calculate_ph_ratio(p: float, h: int) -> float:
    return p / h


# fractional p-index (pf) (Prathap 2010b, 2011)
def calculate_fractional_p_index(citations: list, n_authors: list) -> float:
    pf = 0
    nf = 0
    for i in range(len(citations)):
        pf += 1 / n_authors[i]
        nf += citations[i] / n_authors[i]
    return (nf**2 / pf)**(1/3)


# harmonic p-index (Prathap 2011)
def calculate_harmonic_p_index(citations: list, n_authors: list, author_pos: list) -> float:
    ph = 0
    nh = 0
    for i in range(len(citations)):
        # num = 1 / author_pos[i]
        # denom = 0
        # for j in range(n_authors[i]):
        #     denom += 1 / (j + 1)
        # r = num / denom
        r = author_effort("harmonic", n_authors[i], author_pos[i])
        ph += r
        nh += citations[i] * r
    return (nh**2 / ph)**(1/3)


# hi-index (Batista et al 2006)
def calculate_hi_index(is_core: list, n_authors: list, h: int) -> float:
    suma = 0
    for i in range(len(n_authors)):
        if is_core[i]:
            suma += n_authors[i]
    return h**2 / suma


# fractional pure h-index (Wan et al 2007)
def calculate_pure_h_index_frac(is_core: list, n_authors: list, h: int) -> float:
    suma = 0
    for i in range(len(n_authors)):
        if is_core[i]:
            suma += n_authors[i]
    return h / math.sqrt(suma / h)


# proportional pure h-index (Wan et al 2007)
def calculate_pure_h_index_prop(is_core: list, n_authors: list, author_pos: list, h: int) -> float:
    sump = 0
    for i in range(len(is_core)):
        if is_core[i]:
            sump += 1 / author_effort("proportional", n_authors[i], author_pos[i])
    return h / math.sqrt(sump / h)


# geometric pure h-index (Wan et al 2007)
def calculate_pure_h_index_geom(is_core: list, n_authors: list, author_pos: list, h: int) -> float:
    sumg = 0
    for i in range(len(is_core)):
        if is_core[i]:
            sumg += 1 / author_effort("geometric", n_authors[i], author_pos[i])
    return h / math.sqrt(sumg / h)


# Tol's f-index (Tol 2007)
def calculate_tol_f_index(citations: list) -> int:
    n = len(citations)
    harmonic_means = [0 for _ in range(n)]
    tmp_index, rank_order = sort_and_rank(citations, n)
    for i in range(n):
        if citations[tmp_index[n - i - 1]] > 0:
            harmonic_means[i] = harmonic_means[i - 1] + 1 / citations[tmp_index[n - i - 1]]
        else:
            harmonic_means[i] = harmonic_means[i - 1]
    f = 0
    for i in range(n):
        if rank_order[i] / harmonic_means[rank_order[i]-1] >= rank_order[i]:
            if rank_order[i] > f:
                f = rank_order[i]
    return f


# Tol's t-index (Tol 2007)
def calculate_tol_t_index(citations: list) -> int:
    n = len(citations)
    geometric_means = [0 for _ in range(n)]
    tmp_index, rank_order = sort_and_rank(citations, n)
    for i in range(n):
        if citations[tmp_index[n - i - 1]] > 0:
            geometric_means[i] = geometric_means[i - 1] + math.log(citations[tmp_index[n - i - 1]])
        else:
            geometric_means[i] = geometric_means[i - 1]
    t = 0
    for i in range(n):
        if math.exp(geometric_means[rank_order[i]-1]/rank_order[i]) >= rank_order[i]:
            if rank_order[i] > t:
                t = rank_order[i]
    return t


# mu-index (Glanzel and Schubert 2010)
def calculate_mu_index(citations: list) -> int:
    n = len(citations)
    tmp_cites = [c for c in citations]
    tmp_cites.sort(reverse=True)
    # calculate medians
    median_list = [calculate_median(tmp_cites[:i+1]) for i in range(0, n)]
    mu_index = 0
    for i in range(n):
        if median_list[i] >= i+1:
            mu_index = i+1
    return mu_index


# Wu w-index (Wu 2010)
def calculate_wu_w_index(citations: list, rank_order: list) -> int:
    w = 0
    for i in range(len(citations)):
        if citations[i] >= 10 * rank_order[i]:
            w += 1
    return w


# Wu w-index (Wu 2010)
def calculate_wu_wq(citations: list, rank_order: list, w: int) -> int:
    j = 0
    for i in range(len(citations)):
        if citations[i] >= 10 * rank_order[i]:
            if citations[i] < 10 * (w + 1):
                j += (10 * (w + 1) - citations[i])
        else:
            if rank_order[i] == w + 1:
                j += 10 * (w + 1) - citations[i]
    return j


# Wohlin w-index (Wohlin 2009)
def calculate_wohlin_w(citations: list, max_cites: int) -> float:
    j = 5
    nc = 1
    while max_cites > j-1:
        j *= 2
        nc += 1
    wval = []
    wclass = []
    for i in range(nc):
        if i + 1 == 1:
            wval.append(5)
        else:
            wval.append(2 * wval[i-1])
        wclass.append(0)
        for j in range(len(citations)):
            if citations[j] >= wval[i]:
                wclass[i] += 1
    wohlin_w_index = 0
    for i in range(nc):
        wohlin_w_index += math.log(wval[i]) * wclass[i]
    return wohlin_w_index


# contemporary h-index (Sidiropoulos et al 2007)
def calculate_contemporary_h_index(citations: list, pub_years: list, year: int) -> int:
    n = len(citations)
    pub_ages = publication_ages(year, pub_years)
    sc = [4*citations[i]/pub_ages[i] for i in range(n)]
    _, tmporder = sort_and_rank(sc, n)
    contemp_h_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            contemp_h_index += 1
    return contemp_h_index


# hpd-index (Kosmulski 2009)
def calculate_hpd_index(citations: list, pub_years: list, year: int) -> int:
    n = len(citations)
    pub_ages = publication_ages(year, pub_years)
    cites_per_year = citations_per_year(citations, pub_ages)
    sc = [10*c for c in cites_per_year]
    _, tmporder = sort_and_rank(sc, n)
    hpd_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hpd_index += 1
    return hpd_index


# specific impact s-index (De Visscher 2010)
def calculate_specific_impact_s_index(pub_years: list, year: int, total_cites: int) -> float:
    # uses a different measure of age of publication, allowing age to be zero
    pub_ages = [year - y for y in pub_years]
    specific_impact_s_index = 0
    for i in range(len(pub_years)):
        specific_impact_s_index += 1 - math.exp(-0.1 * pub_ages[i])
    if specific_impact_s_index != 0:
        specific_impact_s_index = total_cites / (10 * specific_impact_s_index)
    return specific_impact_s_index


# hm-index/hF-index (Schreiber 2008)
def calculate_hm_index(citations: list, n_authors: list) -> float:
    hm_index = 0
    cumulative_rank = 0
    data = []
    for i in range(len(citations)):
        data.append([citations[i], n_authors[i]])
    data.sort(reverse=True)
    for d in data:
        c = d[0]
        a = d[1]
        e = 1/a
        cumulative_rank += e
        if cumulative_rank <= c:
            hm_index = cumulative_rank
    return hm_index


# gF-index (fractional paper) (Egghe 2008)
def calculate_gf_paper_index(cumulative_citations: list, rank_order: list, n_authors: list, ) -> float:
    gf_paper = 0
    cumulative_rank = 0
    for i in range(len(cumulative_citations)):
        cumulative_rank += 1/n_authors[rank_order[i]-1]
        if cumulative_rank**2 <= cumulative_citations[i]:
            gf_paper = cumulative_rank
    return gf_paper


# multidimensional h-index (Garcia-Perez 2009)
def calculate_multidimensional_h_index(citations: list, rank_order: list, is_core: list, h: int) -> list:
    multi_dim_h_index = [h]
    multi_used = []
    for i in range(len(citations)):
        if is_core[i]:
            multi_used.append(True)
        else:
            multi_used.append(False)
    j = 0
    tmph = -1
    while tmph != 0:
        nc = len(multi_dim_h_index)
        j += multi_dim_h_index[nc-1]
        tmph = 0
        for i in range(len(citations)):
            if not multi_used[i]:
                if rank_order[i] - j <= citations[i]:
                    multi_used[i] = True
                    tmph += 1
        if tmph > 0:
            multi_dim_h_index.append(tmph)
    return multi_dim_h_index


# two-sided h-index (Garcia-Perez 2012)
def calculate_two_sided_h(citations: list, rank_order: list, h: int, multidim_h: list,
                          mk: Optional[int] = None) -> list:
    # only need to calculate the upper part of the index the center and tail are identical to multidimensional h
    # mk is the number of steps to match on either side of h; the default is to auto-calculate for as many steps in
    # core as equal to length of steps in tail
    if mk is None:
        mk = len(multidim_h)
    else:
        mk += 1  # need to add 1 so number of steps works out correctly
    two_sided_h = [i for i in multidim_h[:mk]]
    j = 0
    tmph = h
    k = 1
    while k < mk:
        j += tmph
        tmph = 0
        for i in range(len(citations)):
            if rank_order[i] <= citations[i] - j:
                tmph += 1
        two_sided_h.insert(0, tmph)
        k += 1
    return two_sided_h


# normalized hi-index/hf-index (Wohlin 2009)
def calculate_normal_hi_index(citations: list, n_authors: list) -> int:
    n = len(citations)
    sc = [citations[i] / n_authors[i] for i in range(n)]
    _, tmporder = sort_and_rank(sc, n)
    hi_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hi_index += 1
    return hi_index


# gf-index (Egghe 2008)
def calculate_gf_cite_index(citations: list, n_authors: list) -> int:
    n = len(citations)
    sc = [citations[i] / n_authors[i] for i in range(n)]
    tmpindex, tmporder = sort_and_rank(sc, n)
    acum = [sc[tmpindex[n-1]]]
    for i in range(1, n):
        acum.append(acum[i-1] + sc[tmpindex[n-i-1]])
    gf_cite = 0
    for i in range(n):
        if tmporder[i]**2 <= acum[tmporder[i]-1]:
            gf_cite += 1
    return gf_cite


# position-weighted h-index (Abbas 2011)
def calculate_position_weighted_h_index(citations: list, n_authors: list, author_pos: list) -> int:
    n = len(citations)
    sc = []
    totalsum = 0
    for i in range(n):
        w = (2 * (n_authors[i] + 1 - author_pos[i])) / (n_authors[i] * (n_authors[i] + 1))
        sc.append(citations[i] * w)
        totalsum += citations[i] * w
    _, tmporder = sort_and_rank(sc, n)
    wh = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            wh += 1
    return wh


# proportional weighted citation aggregate (Abbas 2011)
def calculate_prop_weight_cite_agg(citations: list, n_authors: list, author_pos: list) -> float:
    weighted_aggregate = 0
    for i in range(len(citations)):
        w = author_effort("proportional", n_authors[i], author_pos[i])
        weighted_aggregate += citations[i] * w
    return weighted_aggregate


# proportional weighted citation h-cut (Abbas 2011)
def calculate_prop_weight_cite_h_cut(citations: list, n_authors: list, author_pos: list) -> float:
    n = len(citations)
    sc = []
    for i in range(n):
        w = author_effort("proportional", n_authors[i], author_pos[i])
        sc.append(citations[i] * w)
    _, tmporder = sort_and_rank(sc, n)
    hcut = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hcut += sc[i]
    return hcut


# fractional weighted citation aggregate (Abbas 2011)
def calculate_frac_weight_cite_agg(citations: list, n_authors: list) -> float:
    weighted_aggregate = 0
    for i in range(len(citations)):
        weighted_aggregate += citations[i] / n_authors[i]
    return weighted_aggregate


# fractional weighted citation h-cut (Abbas 2011)
def calculate_frac_weight_cite_h_cut(citations: list, n_authors: list) -> float:
    n = len(citations)
    sc = []
    for i in range(n):
        sc.append(citations[i] / n_authors[i])
    _, tmporder = sort_and_rank(sc, n)
    hcut = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hcut += sc[i]
    return hcut


# Woeginger w-index (Woeginger 2008)
def calculate_woeginger_w(citations: list, rank_order: list) -> int:
    w = 0
    for j in range(len(citations)):
        tmp_good = True
        for i in range(len(rank_order)):
            if rank_order[i] <= j:
                if citations[i] < j - rank_order[i] + 1:
                    tmp_good = False
        if tmp_good:
            w = j
    return w


# maxprod (Kosmulski 2007)
def calculate_maxprod_index(citations: list, rank_order: list) -> int:
    maxprod_index = 0
    for i in range(len(citations)):
        maxprod_index = max(maxprod_index, citations[i] * rank_order[i])
    return maxprod_index


# j-index (Todeschini 2011)
def calculate_todeschini_j_index(citations: list, h: int) -> float:
    # constants for j-index
    ndhk = 12
    dhk = (500, 250, 100, 50, 25, 10, 5, 4, 3, 2, 1.5, 1.25)

    sumw = 0
    sumwdhk = 0
    for j in range(ndhk):
        sumw += 1 / (j + 1)
        c = 0
        for i in range(len(citations)):
            if citations[i] >= h * dhk[j]:
                c += 1
        sumwdhk += c / (j + 1)
    return h + sumwdhk/sumw


# (general) adapted pure h-index (Chai et al 2008)
def calculate_adapt_pure_h_index(sc: list) -> float:
    """
    this is used to calculate the adapted pure h-index once the weighted citations (sc) are determined
    """
    n = len(sc)
    _, tmporder = sort_and_rank(sc, n)
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
    return (((j + 1)*cite_e) - (j*cite_e1)) / (cite_e - cite_e1 + 1)


# fractional adapted pure h-index (Chai et al 2008)
def calculate_adapt_pure_h_index_frac(citations: list, n_authors: list) -> float:
    sc = [citations[i] / math.sqrt(n_authors[i]) for i in range(len(citations))]
    return calculate_adapt_pure_h_index(sc)


# adapted pure h-index w/proportional author credit (Chai et al 2008)
def calculate_adapt_pure_h_index_prop(citations: list, n_authors: list, author_pos: list) -> float:
    sc = []
    for i in range(len(citations)):
        ea = author_effort("proportional", n_authors[i], author_pos[i])
        sc.append(citations[i] / math.sqrt(1/ea))
    return calculate_adapt_pure_h_index(sc)


# adapted pure h-index w/geometric author credit (Chai et al 2008)
def calculate_adapt_pure_h_index_geom(citations: list, n_authors: list, author_pos: list) -> float:
    sc = []
    for i in range(len(citations)):
        ea = author_effort("geometric", n_authors[i], author_pos[i])
        sc.append(citations[i] / math.sqrt(1/ea))
    return calculate_adapt_pure_h_index(sc)


# profit p-index (Aziz and Rozing 2013)
def calculate_profit_p_index(citations: list, n_authors: list, author_pos: list) -> float:
    mon_equiv = []
    for i in range(len(citations)):
        mon_equiv.append(author_effort("harmonic_aziz", n_authors[i], author_pos[i]))
    monograph_equiv = sum(mon_equiv)
    return 1 - monograph_equiv / len(citations)


# profit adjusted h-index (Aziz and Rozing 2013)
def calculate_profit_adj_h_index(citations: list, n_authors: list, author_pos: list) -> int:
    n = len(citations)
    mon_equiv = []
    for i in range(n):
        mon_equiv.append(author_effort("harmonic_aziz", n_authors[i], author_pos[i]))
    sc = [citations[i] * mon_equiv[i] for i in range(n)]
    _, tmporder = sort_and_rank(sc, n)
    profit_adj_h_index = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            profit_adj_h_index += 1
    return profit_adj_h_index


# profit h-index (Aziz and Rozing 2013)
def calculate_profit_h_index(profit_adj_h: int, h: int) -> float:
    return 1 - profit_adj_h / h


# hj-indices (Dorta-Gonzalez and Dorta-Gonzalez 2010)
def calculate_hj_indices(total_pubs: int, h: int, sorted_citations: list) -> list:
    if total_pubs < 2 * h - 1:
        j = total_pubs - h
    else:
        j = h - 1
    hj_index = [h**2]
    for i in range(1, j+1):
        hj_index.append(hj_index[i-1] + (h-i)*(sorted_citations[h-i-1] - sorted_citations[h-i])
                        + sorted_citations[h+i-1])
    return hj_index


# iteratively weighted h-index (Todeschini and Baccini 2016)
def calculate_iteratively_weighted_h_index(multidim_h_index: list) -> float:
    iteratively_weighted_h_index = 0
    for p, h in enumerate(multidim_h_index):
        iteratively_weighted_h_index += h / (p + 1)
    return iteratively_weighted_h_index


# subfunction from (Bihari and Tripathi 2017)
def calculate_em_components(values: list, rank_order: list) -> list:
    em_component = []
    tmp_values = [c for c in values]  # make a temporary copy of the citation counts
    non_zero_values = count_non_zero(tmp_values)
    while non_zero_values > 1:
        if max(tmp_values) == 1:
            em_component.append(1)
            non_zero_values = 0
        else:
            h = 0
            for i in range(len(values)):
                if rank_order[i] <= tmp_values[i]:
                    h += 1
            em_component.append(h)
            tmp_values = [max(0, c-h) for c in tmp_values]  # subtract previous h-index from citations
            non_zero_values = count_non_zero(tmp_values)

    # print(tmp_values)
    # across the different papers and examples, the authors are inconsistent about what to do when there is a single
    # publication left with one or more citation for it. Usually they add one more "1" onto the end of the em
    # component list, but occasionally they do not. I assume this is due to errors in their generation of the data
    # the 2017 paper makes it sound like one should quit when there is only a single paper left, but the
    # example in the 2021 paper requires one last value added to the component list in this case
    if (non_zero_values == 1) and max(tmp_values) > 0:
        em_component.append(1)
    return em_component

# subfunction from (Bihari and Tripathi 2017)
def calculate_emp_components(values: list, rank_order: list) -> list:
    # EM'-index
    emp_component = []
    tmp_values = [c for c in values]  # make a temporary copy of the citation counts
    tmp_ranks = [r for r in rank_order]  # make a temporary copy of the ranks
    non_zero_values = count_non_zero(tmp_values)
    while non_zero_values > 1:
        if max(tmp_values) == 1:
            emp_component.append(1)
            non_zero_values = 0
        else:
            h = 0
            for i in range(len(values)):
                if tmp_ranks[i] <= tmp_values[i]:
                    h += 1
            emp_component.append(h)
            # subtract h_index only from top h pubs
            for i in range(len(values)):
                if tmp_ranks[i] <= tmp_values[i]:
                    tmp_values[i] = max(0, tmp_values[i]-h)
            non_zero_values = count_non_zero(tmp_values)
            # rerank counts
            _, tmp_ranks = sort_and_rank(tmp_values, len(values))

    # the 2017 paper makes it sound like one should quit when there is only a single paper left, but the em
    # example in the 2021 paper requires one last value added to the component list in this case
    if (non_zero_values == 1) and max(tmp_values) > 0:
        emp_component.append(1)

    return emp_component


# EM-index (Bihari and Tripathi 2017)
def calculate_em_index(citations: list, rank_order: list) -> float:
    em_component = calculate_em_components(citations, rank_order)
    return math.sqrt(sum(em_component))


# EM'-index (Bihari and Tripathi 2017)
def calculate_emp_index(citations: list, rank_order: list) -> float:
    emp_component = calculate_emp_components(citations, rank_order)
    return math.sqrt(sum(emp_component))


# iterative weighted EM-index (Bihari et al 2021)
def calculate_iterative_weighted_em_index(citations: list, rank_order: list) -> float:
    em_component = calculate_em_components(citations, rank_order)
    iwem = 0
    for i, e in enumerate(em_component):
        iwem += e/(i+1)
    return iwem


# iterative weighted EM'-index (Bihari et al 2021)
def calculate_iterative_weighted_emp_index(citations: list, rank_order: list) -> float:
    emp_component = calculate_emp_components(citations, rank_order)
    iwemp = 0
    for i, e in enumerate(emp_component):
        iwemp += e/(i+1)
    return iwemp


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


# pubs per year (time-scaled)(Todeschini and Baccini 2016)
def calculate_pubs_per_year(total_pubs: int, age: int) -> float:
    return total_pubs / age


# citations per year (time-scaled)(Todeschini and Baccini 2016)
def calculate_cites_per_year(total_cites: int, age: int) -> float:
    return total_cites / age


# annual h-index (hIa) (Harzing et al 2014)
def calculate_annual_h_index(norm_h: int, age: int) -> float:
    return norm_h / age


# CDS-index (Vinkler 2011, 2013)
def calculate_cds_index(citations: list) -> int:
    maxg = 14  # largest category = more than 8192 citations
    cds = 0
    for c in citations:
        if c < 2:
            cds += 1
        else:
            g = 2
            while c > 2**g:
                g += 1
            if g > maxg:
                g = maxg
            cds += g
    return cds


# CDR-index (Vinkler 2011, 2013)
def calculate_cdr_index(total_pubs: int, cds: int) -> float:
    maxg = 14  # largest category = more than 8192 citations
    return 100 * cds / (maxg * total_pubs)


# Sangwal 2012
def calculate_circ_cite_area_radius(total_cites: int) -> float:
    return math.sqrt(total_cites / math.pi)


# Sangwal 2012
def calculate_citation_acceleration(total_cites: int, age: int) -> float:
    return total_cites / age**2


# Render index - Redner (2010)
def calculate_redner_index(total_cites: int) -> float:
    return math.sqrt(total_cites)


# Levene j-index - Levene et al (2012)
def calculate_levene_j_index(citations: list) -> float:
    j = 0
    for c in citations:
        j += math.sqrt(c)
    return j


# h-mixed synthetic indices (S-index and T-index) - Ye (2010)
def calculate_s_index_h_mixed(h: int, cpp: float) -> float:
    return 100 * math.log10(h * cpp)


# h-mixed synthetic indices (S-index and T-index) - Ye (2010)
def calculate_t_index_h_mixed(h: int, cpp: float, r: int) -> float:
    return 100 * math.log10(h * cpp * r)


# s-index / citation entropy p - Silagadze (2009)
def calculate_citation_entropy(total_cites: int, citations: list) -> float:
    # calculate Shannon entropy
    h = 0
    for c in citations:
        if c != 0:
            p = c / total_cites
            h += p * math.log(p, 2)
    h = -h
    # standardize Shannon entropy
    hstar = h / math.log(len(citations), 2)
    return 0.25 * math.sqrt(total_cites) * math.exp(hstar)


# Corrected Quality ratios - Lindsay (1978)
def calculate_cq_index(total_cites: int, total_pubs: int) -> float:
    return (total_cites / total_pubs) * math.sqrt(total_cites * total_pubs)


# Corrected Quality ratios / 60:40 (Lindsay 1978)
def calculate_cq04_index(total_cites: int, total_pubs: int) -> float:
    return math.pow(total_cites / total_pubs, 0.6) * math.pow(total_pubs, 0.4)


# Indifference (Egghe and Rousseau 1996)
def calculate_indifference(total_cites: int, total_pubs: int) -> float:
    return total_pubs / total_cites


# impact vitality (Rons and Amez 2008, 2009)
def calculate_impact_vitality(total_cite_list: list, w: int = 5) -> Union[str, float]:
    # w is the window to calculate over in years
    n = len(total_cite_list)
    if n < w:
        return "n/a"
    else:
        # calculate denominator of equation
        d = 0
        for i in range(1, w+1):
            d += 1 / i
        d -= 1

        # calculate numerator and denominator of numerator of equation
        total_cites_per_year = total_citations_each_year(total_cite_list)
        nn = 0
        nd = 0
        for i in range(1, w+1):
            nd += total_cites_per_year[n - i]
            nn += total_cites_per_year[n - i] / i

        # calculate value
        return (w * (nn / nd) - 1) / d


# least-squares h-rate (Burrell 2007)
def calculate_least_squares_h_rate(years: list, hs: list) -> float:
    first_year = min(years)
    years = [y - first_year + 1 for y in years]  # shift year list to years since start
    sumxy = 0
    sumx2 = 0
    for i in range(len(years)):
        sumxy += hs[i] * years[i]
        sumx2 += years[i]**2
    return sumxy/sumx2


# dynamic h-type-index (Rousseau and Ye 2008)
def calculate_dynamic_h_type_index(rational_h_list: list, date_list: list, r: float) -> Union[str, float]:
    def date_to_int(dd: datetime.date) -> int:
        return datetime.date.toordinal(dd)

    if len(rational_h_list) == 1:
        return "n/a"
    else:
        n = len(rational_h_list)
        avg_h = sum(rational_h_list) / n
        avg_d = 0
        for d in date_list:
            avg_d += date_to_int(d)
        avg_d /= n
        sumxy = 0
        sumx2 = 0
        for i in range(n):
            d = date_to_int(date_list[i]) - avg_d
            sumxy += (rational_h_list[i] - avg_h)*d
            sumx2 += d**2
        return 365 * r * (sumxy / sumx2)


# trend h-index
def calculate_trend_h_index(pub_list: list) -> int:
    pub_cites = citations_per_pub_per_year(pub_list)
    ny = len(pub_list[0])
    sc = [0 for _ in pub_list]
    for i, p in enumerate(pub_cites):
        for y, c in enumerate(p):
            sc[i] += c * (1 / (ny - y))
        sc[i] *= 4

    _, tmporder = sort_and_rank(sc, len(pub_list))
    trend_h_index = 0
    for i in range(len(pub_list)):
        if tmporder[i] <= sc[i]:
            trend_h_index += 1
    return trend_h_index


# average activity, at (Popov 2005)
def calculate_mean_at_index(total_cites: int, th: int) -> float:
    return total_cites / (2 * th)


# characteristic times scale, th (Popov 2005)
def calculate_th_index(citations: list, years: list, total_cites: int) -> int:
    target = total_cites / 2
    cite_sum = 0
    maxy = max(years)
    cur_y = maxy + 1
    while cite_sum < target:
        cur_y -= 1
        for i, y in enumerate(years):
            if y == cur_y:
                cite_sum += citations[i]
    return maxy - cur_y + 1


# DCI-index: discounted cumulated impact (Jarvelin and Pearson, 2008; Ahlgren and Jarvelin 2010)
def calculate_dci_index(total_citations: list, logbase: int = 2) -> list:
    # create list of novel citation counts per year
    yearly_cites = total_citations_each_year(total_citations)
    y = len(yearly_cites)
    dci = []
    for i, c in enumerate(yearly_cites):
        if (i == 0) and (y == 1):
            d = c
        elif i == 0:
            d = c / max(1.0, math.log(y-1, logbase))
        elif i + 1 == y:
            d = dci[i-1] + c
        else:
            d = dci[i-1] + c / max(1.0, math.log(y-(i+1), logbase))
        dci.append(d)
    return dci


# dDCI-index: dynamic discounted cumulated impact (Jarvelin and Pearson, 2008; Ahlgren and Jarvelin 2010)
def calculate_ddci_index(dci: list) -> float:
    return dci[len(dci)-1]


# history h-index (Randic 2009)
def calculate_history_h_index(citations: list, h: int) -> int:
    tmp_cites = sorted(citations, reverse=True)
    max_cites = max(tmp_cites)
    hklist = [h]
    k = 0
    while max_cites > 2**k:
        hk = 0
        k += 1
        for i, c in enumerate(tmp_cites):
            if c >= (i+1) * 2**k:
                hk = i+1
        if hk != 0:
            hklist.append(hk)
    return sum(hklist)


# quality quotient (Randic 2009)
def calculate_quality_quotient(h: int, history_h: int) -> float:
    return history_h / h


# scientist's level (Mitropoulos 2009)
def calculate_scientist_level(total_cites: int, total_pubs: int) -> list:
    n = total_cites + total_pubs
    v = math.floor(math.log10(n))
    level = math.floor(n / 10**v)
    return [v, level]


# non-integer scientist's level (Todeschini and Baccini 2016)
def calculate_scientist_level_nonint(total_cites: int, total_pubs: int) -> float:
    return math.log(math.sqrt(total_cites) + total_pubs)


# q-index (Bartneck and Kokkelmans 2011)
def calculate_q_index(citations: list, self_citations: list, h: int) -> float:
    data = []
    for i in range(len(citations)):
        data.append([citations[i], self_citations[i]])
    data.sort(reverse=True)
    prev_a = 0
    q_index = 0
    for i, d in enumerate(data):
        c = d[0]
        s = d[1]
        if c <= h:
            if i + 1 <= h:
                a = 0
            elif c == data[i-1][0]:
                a = prev_a + 1
            else:
                a = prev_a
            if i + 1 < h:
                q = 0
            else:
                q = 1 / ((i+1) + 1 - a - h)
            prev_a = a
        else:
            q = 0
        q_index += q*s
    return q_index / len(citations)


# career years h-index by publications (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_pub(pub_years: list) -> int:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: pub_years.count(y) for y in range(miny, maxy+1)}
    data = []
    for y in year_cnts:
        data.append([year_cnts[y], y])
    data.sort(reverse=True)
    h = 0
    for i in range(len(data)):
        cnt = data[i][0]
        if cnt >= i + 1:
            h += 1
    return h


# career years h-index by citations (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_cite(pub_years: list, cites: list) -> int:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = []
    for y in year_cnts:
        data.append([year_cnts[y], y])
    data.sort(reverse=True)
    h = 0
    for i in range(len(data)):
        cnt = data[i][0]
        if cnt >= i + 1:
            h += 1
    return h


# career years h-index by avg citations/year (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_avgcite(pub_years: list, cites: list) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    year_pubs = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
        year_pubs[pub_years[i]] += 1
    data = []
    for y in year_cnts:
        if year_pubs[y] > 0:
            data.append(year_cnts[y]/year_pubs[y])
        else:
            data.append(0)
    data.sort(reverse=True)
    h = 0
    for i in range(len(data)):
        avg = data[i]
        if avg >= i + 1:
            h += 1
    if (h > 0) and (h < len(data)):
        ch = data[h-1]
        chp1 = data[h]
        hint = ((h+1)*ch - h*chp1) / (1 - chp1 + ch)
    else:
        hint = h
    return hint


# career years h-index by diffusion speed (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_diffspeed(pub_years: list, cites: list, cur_year: int) -> float:
    # in the original paper they calculate ageas current year - pub year, rather than cy - py + 1. This would mean
    # articles in the present year would have an age of zero and an infinite diffusion
    #   this coded version adds the 1, so an article published this year has an age of 1 and lat year an age of 2
    miny = min(pub_years)
    maxy = max(pub_years)
    cite_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        cite_cnts[pub_years[i]] += c
    data = []
    for y in cite_cnts:
        data.append(cite_cnts[y]/(cur_year - y + 1))
    data.sort(reverse=True)
    h = 0
    for i in range(len(data)):
        avg = data[i]
        if avg >= i + 1:
            h += 1
    if (h > 0) and (h < len(data)):
        ch = data[h-1]
        chp1 = data[h]
        hint = ((h+1)*ch - h*chp1) / (1 - chp1 + ch)
    else:
        hint = h
    return hint


    # miny = min(pub_years)
    # maxy = max(pub_years)
    # cite_cnts = {y: 0 for y in range(miny, maxy+1)}
    # for i, c in enumerate(cites):
    #     cite_cnts[pub_years[i]] += c
    # data = []
    # for y in cite_cnts:
    #     data.append([cite_cnts[y]/(cur_year - y + 1), y])
    # data.sort(reverse=True)
    # h = 0
    # for i in range(len(data)):
    #     avg = data[i][0]
    #     if avg >= i + 1:
    #         h += 1
    # if (h > 0) and (h < len(data)):
    #     ch = data[h-1][0]
    #     chp1 = data[h][0]
    #     hint = ((h+1)*ch - h*chp1) / (1 - chp1 + ch)
    # else:
    #     hint = h
    # return hint


# collaborative index (Lawani 1980)
def calculate_collaborative_index(author_cnts: list) -> float:
    return sum(author_cnts) / len(author_cnts)


# degree of collaboration (Subramanyam 1983)
def calculate_degree_of_collaboration(author_cnts: list) -> float:
    return 1 - author_cnts.count(1)/len(author_cnts)


# collaborative coefficient (Ajiferuke et al 1988)
def calculate_collaborative_coefficient(author_cnts: list) -> float:
    maxa = max(author_cnts)
    cc = 0
    for a in range(1, maxa+1):
        cc += author_cnts.count(a) / a
    return 1 - cc / len(author_cnts)


# i10 index (Google Scholar)
def calculate_i10_index(citations: list) -> int:
    cnt = 0
    for c in citations:
        if c >= 10:
            cnt += 1
    return cnt


# i100 index (Teixeira da Silva, 2021)
def calculate_i100_index(citations: list) -> int:
    cnt = 0
    for c in citations:
        if c >= 100:
            cnt += 1
    return cnt


# i1000 index (Teixeira da Silva, 2021)
def calculate_i1000_index(citations: list) -> int:
    cnt = 0
    for c in citations:
        if c >= 1000:
            cnt += 1
    return cnt


def count_non_zero(x: list) -> int:
    # support function to count the number of non-zero items in a list of numbers
    return len(x) - x.count(0)


# P1 index (van Eck and Waltman 2008)
def calculate_p1_index(citations: list) -> int:
    return count_non_zero(citations)


# cited paper percent
def calculate_cited_paper_percent(citations: list) -> float:
    return 100 * calculate_p1_index(citations) / len(citations)


# uncitedness factor
def calculate_uncitedness_factor(citations: list) -> int:
    return len(citations) - calculate_p1_index(citations)


# uncited paper percent
def calculate_uncited_paper_percent(citations: list) -> float:
    return 100 - calculate_cited_paper_percent(citations)


# beauty coefficient (Ke et al 2015)
def calculate_beauty_coefficient(pub_list: list) -> list:
    blist = []
    for p in pub_list:
        yearly_cites = []
        for i, n in enumerate(p):
            if n is not None:
                if len(yearly_cites) == 0:
                    yearly_cites.append(n)
                else:
                    yearly_cites.append(n - p[i-1])
        maxc = max(yearly_cites)
        tm = yearly_cites.index(maxc)
        c0 = yearly_cites[0]
        b = 0
        if tm != 0:
            for t in range(tm+1):
                b += (((maxc - c0)/tm)*t + c0 - yearly_cites[t]) / max(1, yearly_cites[t])
        blist.append(b)
    return blist


# awakening_time (Ke et al 2015)
def calculate_awakening_time(pub_list: list) -> list:
    ta_list = []
    for p in pub_list:
        yearly_cites = []
        for i, n in enumerate(p):
            if n is not None:
                if len(yearly_cites) == 0:
                    yearly_cites.append(n)
                else:
                    yearly_cites.append(n - p[i-1])
        maxc = max(yearly_cites)
        tm = yearly_cites.index(maxc)
        c0 = yearly_cites[0]
        ta = 0
        maxdt = 0
        if tm != 0:
            for t in range(tm+1):
                dt = abs((maxc-c0)*t - tm*yearly_cites[t] + tm*c0) / math.sqrt((maxc-c0)**2 + tm**2)
                if dt > maxdt:
                    ta = t
                    maxdt = dt
        ta_list.append(ta)
    return ta_list


# academic trace (Ye and Leydesdorff 2014)
def calculate_academic_trace(citations: list, total_cites: int, core_cites: int, h: int) -> float:
    pz = citations.count(0)
    p = len(citations)
    x1 = h**2 / p
    y2 = (total_cites - core_cites)**2 / total_cites
    z3 = ((core_cites - h**2)**2 / total_cites) - (pz**2 / p)
    t = x1 + y2 + z3
    return t


# scientific quality index (Pluskiewicz1 et al 2019)
def calculate_scientific_quality_index(citations, self_citations) -> float:
    cnt = 0
    sharp_citations = [citations[i] - self_citations[i] for i in range(len(self_citations))]
    total_cites = sum(sharp_citations)
    for c in sharp_citations:
        if c >= 10:
            cnt += 1
    return total_cites/len(sharp_citations) + 100*cnt/len(sharp_citations)


# first author h-index (Butson and Yu 2010)
def calculate_first_author_h_index(h: int, author_pos: list, is_core: list) -> int:
    cnt = 0
    for i in range(len(author_pos)):
        if (author_pos[i] == 1) and is_core[i]:
            cnt += 1
    return h + cnt


# o-index (Dorogovtsev and Mendes 2015)
def calculate_o_index(h: int, max_cites: int) -> float:
    return math.sqrt(h * max_cites)


# discounted h-index (Ferrara and Romero 2013)
def calculate_discounted_h_index(h: int, total_cites: int, total_self: int) -> float:
    return h * math.sqrt((total_cites - total_self)/total_cites)


# j-index (Mikhailov 2014)
def calculate_mikhailov_j_index(citations: list, rank_order: list) -> int:
    j = 0
    for i in range(len(citations)):
        if math.trunc(rank_order[i]**(3/2)) <= citations[i]:
            j += 1
    return j


# year-based EM-index by publications (Bihari and Tripathi 2018)
def calculate_year_based_em_pub(pub_years: list) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: pub_years.count(y) for y in range(miny, maxy+1)}
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)
    rank_order = [i+1 for i in range(len(data))]

    em_component = calculate_em_components(data, rank_order)
    return math.sqrt(sum(em_component))


# year-based EM-index by publication year citations (Bihari and Tripathi 2018)
def calculate_year_based_em_pycites(pub_years: list, cites: list) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)
    rank_order = [i+1 for i in range(len(data))]

    em_component = calculate_em_components(data, rank_order)
    return math.sqrt(sum(em_component))


# year-based EM-index by citations (Bihari and Tripathi 2018)
def calculate_year_based_em_cites(total_cite_list: list) -> float:
    total_cites_per_year = total_citations_each_year(total_cite_list)
    total_cites_per_year.sort(reverse=True)
    rank_order = [i+1 for i in range(len(total_cites_per_year))]

    em_component = calculate_em_components(total_cites_per_year, rank_order)
    return math.sqrt(sum(em_component))


# year-based EM'-index by publications (Bihari and Tripathi 2018)
def calculate_year_based_emp_pub(pub_years: list) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: pub_years.count(y) for y in range(miny, maxy+1)}
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)
    rank_order = [i+1 for i in range(len(data))]

    emp_component = calculate_emp_components(data, rank_order)
    return math.sqrt(sum(emp_component))


# year-based EM'-index by publication year citations (Bihari and Tripathi 2018)
def calculate_year_based_emp_pycites(pub_years: list, cites: list) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)
    rank_order = [i+1 for i in range(len(data))]

    emp_component = calculate_emp_components(data, rank_order)
    return math.sqrt(sum(emp_component))


# year-based EM'-index by citations (Bihari and Tripathi 2018)
def calculate_year_based_emp_cites(total_cite_list: list) -> float:
    total_cites_per_year = total_citations_each_year(total_cite_list)
    total_cites_per_year.sort(reverse=True)
    rank_order = [i+1 for i in range(len(total_cites_per_year))]

    emp_component = calculate_emp_components(total_cites_per_year, rank_order)
    return math.sqrt(sum(emp_component))


# h' index (Zhang 2012)
def calculate_h_prime(h: int, e: float, total_cites, core_cites) -> float:
    t = math.sqrt(total_cites - core_cites)
    return e*h/t


# hc index (Khurana and Sharma 2022)
def calculate_hc(h: int, m: int) -> int:
    if h > 1:
        k = math.trunc(math.log(m-1, h))
        return h + k
    elif m > 1:
        return 2
    else:
        return h


# k index (Anania and Caruso 2013)
def calculate_k_index_anania_caruso(h: int, core: int) -> float:
    return h + (1 - h**2/core)


# w index (Anania and Caruso 2013)
def calculate_w_index_anania_caruso(h: int, total: int) -> float:
    return h + (1 - h**2/total)


# h-norm index (Anania and Caruso 2013)
def calculate_h_norm(citations: list, n_authors: list) -> int:
    sc = [citations[i] / n_authors[i] for i in range(len(citations))]
    n = len(sc)
    _, tmporder = sort_and_rank(sc, n)
    hn = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hn += 1
    return hn


# k-norm index (Anania and Caruso 2013)
def calculate_k_norm_index(citations: list, n_authors: list) -> float:
    sc = [citations[i] / n_authors[i] for i in range(len(citations))]
    n = len(sc)
    _, tmporder = sort_and_rank(sc, n)
    hn = 0
    normcore = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hn += 1
            normcore += sc[i]
    try:
        return hn + (1 - hn**2/normcore)
    except ZeroDivisionError:
        return 0


# w-norm index (Anania and Caruso 2013)
def calculate_w_norm_index(citations: list, n_authors: list) -> float:
    sc = [citations[i] / n_authors[i] for i in range(len(citations))]
    n = len(sc)
    _, tmporder = sort_and_rank(sc, n)
    hn = 0
    for i in range(n):
        if tmporder[i] <= sc[i]:
            hn += 1
    normtotal = sum(sc)
    return hn + (1 - hn**2/normtotal)


# yearly h-index (Singh 2022)
def calculate_yearly_h_index(citations: list, pub_years: list) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    havg = 0
    yearcnt = 0
    # calculate h only for papers published in a single  year
    for year in range(miny, maxy+1):
        # create citation count list for a single year
        tmp_citations = []
        for i, y in enumerate(pub_years):
            if y == year:
                tmp_citations.append(citations[i])
        n = len(tmp_citations)
        _, tmporder = sort_and_rank(tmp_citations, n)
        # calculate h for the year
        hy = 0
        for i in range(n):
            if tmporder[i] <= tmp_citations[i]:
                hy += 1
        havg += hy
        yearcnt += 1
    return havg / yearcnt  # average across all years


# t-index (Singh 2022)
def calculate_t_index_singh(citations, year_h, age: int, total_cites: int) -> float:
    t_prime = math.log(10*age)
    t = 0
    for c in citations:
        if c > 0:
            t += -(c/total_cites) * math.log(c/total_cites)
    return 4 * math.exp(t/t_prime) * year_h


# fairness
def calculate_fairness(total_cites: int, total_pubs: int, citations: list) -> float:
    sumc2 = 0
    for c in citations:
        sumc2 += c**2
    return total_cites**2 / (total_pubs * sumc2)


# Zynergy (Prathap 2014)
def calculate_zynergy(total_cites: int, total_pubs: int, fairness: float) -> float:
    return ((fairness * total_cites**2) / total_pubs)**(1/3)


# p20 (Gagolewski et al 2022)
def calculate_p20(citations: list, total_cites: int, total_pubs: int) -> float:
    sorted_cites = sorted(citations)
    sorted_cites.reverse()
    p = round(total_pubs / 5)  # index of top 20%
    core = sum(sorted_cites[:p])
    return core / total_cites


# rmp (Gagolewski et al 2022)
def calculate_rmp(mp: int) -> float:
    return math.sqrt(mp)


# css (Gagolewski et al 2022)
def calculate_css(citations: list) -> float:
    s = sum(c**2 for c in citations)
    return s**(1/3)


# csr (Gagolewski et al 2022)
def calculate_csr(citations: list) -> float:
    s = 0
    tmpcites = sorted(citations)
    tmpcites.reverse()
    for i, c in enumerate(tmpcites):
        s += 2*(i+0.5)*c  # it is i + 0.5 rather than i - 0.5 because i is counting from 0
    return s**(1/3)


# slg (Gagolewski et al 2022)
def calculate_slg(citations: list) -> float:
    return sum(math.log10(c+1) for c in citations)


# 3DSI w/pr (Gagolewski et al 2022)
def calculate_3dsi_pr(total_pubs: int, total_cites: int, csr: float) -> list:
    pr = (total_pubs - 2*csr**3/total_cites + 1) / (total_pubs - csr**3/total_cites)
    return [total_pubs, total_cites, pr]


# total collaborators
def calculate_total_collaborators(coauthor_list: list) -> int:
    c = []
    for coauthors in coauthor_list:
        if coauthors != ".":
            if ";" in coauthors:
                c.extend(coauthors.split(";"))
            else:
                c.append(coauthors)
    return len(set(c))


# partnership ability index (Schubert 2012)
def calculate_partnership_ability(coauthor_list: list):
    # create counts of publications per coauthor
    coauthor_cnts = {}
    for coauthors in coauthor_list:
        if coauthors != ".":
            if ";" in coauthors:
                coa_list = coauthors.split(";")
            else:
                coa_list = [coauthors]
            for a in coa_list:
                if a in coauthor_cnts:
                    coauthor_cnts[a] += 1
                else:
                    coauthor_cnts[a] = 1
    phi = 0
    cnts = list(coauthor_cnts.values())
    n = len(cnts)
    _, tmporder = sort_and_rank(cnts, n)
    # calculate phi
    for i in range(n):
        if tmporder[i] <= cnts[i]:
            phi += 1
    return phi


# stratified h-index (Wurtz and Schmidt 2016)
def calculate_stratified_h(h: int, author_pos: list, author_cnts: list, citations: list) -> list:
    def calc_h(cites: list) -> int:
        hn = 0
        n = len(cites)
        _, tmporder = sort_and_rank(cites, n)
        for j in range(n):
            if tmporder[j] <= cites[j]:
                hn += 1
        return hn

    # sort citations of publications into lists based on author position
    pub1, pub2, pub3, publast = [], [], [], []
    for i, p in enumerate(author_pos):
        if p == 1:
            pub1.append(citations[i])
        elif p == 2:
            pub2.append(citations[i])
        elif p == 3:
            pub3.append(citations[i])
        # elif p == author_cnts[i]:
        if p == author_cnts[i]:  # do this separately, because for solo-authored papers, one is both 1st and last author
            publast.append(citations[i])

    h1 = calc_h(pub1)
    h2 = calc_h(pub2)
    h3 = calc_h(pub3)
    hlast = calc_h(publast)

    return [h, h1, h2, h3, hlast]


# platinum h-index (Smith 2015)
def calculate_platinum_h(h: int, total_cites: int, total_pubs: int, age: int) -> float:
    return (h / age) * (total_cites / total_pubs)


# stochastic h-index (Nair and Turlach 2012)
def calculate_stochastic_h(h: int, citations: list, year: int, pub_years: list) -> float:
    # main function codde
    pub_ages = publication_ages(year, pub_years)
    sub_ages = []  # age of publications with h or fewer citations
    sub_cites = []  # the citation count for the publications in l_pubs
    l0 = 0  # count of publications with h+1 or more citations
    for i, c in enumerate(citations):
        if c <= h:
            sub_ages.append(pub_ages[i])
            sub_cites.append(c)
        else:
            l0 += 1
    k = h - l0  # number of publications which have to reach h+1 citations for h to increase by 1

    # calculate probability of a publication not reaching h+1 citations in a year
    pub_q = []
    for i, c in enumerate(sub_cites):
        age = sub_ages[i]
        if c == 0:
            rate = -math.log((age + 1)/(age + 2))
        else:
            rate = c / age  # citations per year
        m = h - c
        pub_q.append(scipy.stats.poisson.cdf(m, rate))
    hs = h + 1
    for i in range(k+1):  # go from 0 to k
        all_indices = range(len(pub_q))
        p_indices = itertools.combinations(all_indices, i)
        qi = 0
        product = 1
        for p_inds in p_indices:
            for j in all_indices:
                if j in p_inds:
                    product *= (1 - pub_q[j])
                else:
                    product *= pub_q[j]
            qi += product
        hs -= qi
    return hs


# multiple h-index (Yaminfirooz and Gholinia 2015)
def calculate_multiple_h_index(citations: list, rank_order: list, is_core: list, h: int, year: int,
                               pub_years: list) -> float:
    multi_dim_h_index = [h]
    multi_used = []
    matching_h = [0 for _ in citations]  # the value of h associated with each publication
    for i in range(len(citations)):
        if is_core[i]:
            multi_used.append(True)
            matching_h[i] = h
        else:
            multi_used.append(False)
    j = 0
    tmph = -1
    while tmph != 0:
        nc = len(multi_dim_h_index)
        j += multi_dim_h_index[nc-1]
        tmph = 0
        for i in range(len(citations)):
            if not multi_used[i]:
                if rank_order[i] - j <= citations[i]:
                    multi_used[i] = True
                    tmph += 1
        if tmph > 0:
            multi_dim_h_index.append(tmph)
            # replace the default h of 0 with tmph for the newly used publications
            for i in range(len(citations)):
                if multi_used[i] and (matching_h[i] == 0):
                    matching_h[i] = tmph

    pub_ages = publication_ages(year, pub_years)
    mh = 0
    for i, c in enumerate(citations):
        mh += (matching_h[i] * c**2) / pub_ages[i]
    return math.sqrt(mh)


# hmaj-index (Hu et al 2010; Bucur et al 2015)
# def calculate_hmaj_index(citations: list, ht: int, primary: list) -> list:
def calculate_hmaj_index(citations: list, primary: list) -> int:
    # create list containing only the publications in which the author is primary
    tmp_cites = []
    for i, c in enumerate(citations):
        if primary[i]:
            tmp_cites.append(c)
    hp = 0
    n = len(tmp_cites)
    _, tmporder = sort_and_rank(tmp_cites, n)
    for j in range(n):
        if tmporder[j] <= tmp_cites[j]:
            hp += 1
    return hp


def calculate_total_pubs_coauthor_adj(measure: str, author_cnts: list, author_pos: list) -> float:
    cnt = 0
    for i, a in enumerate(author_cnts):
        cnt += author_effort(measure, a, author_pos[i])
    return cnt


# only used for spot testing new functions
if __name__ == "__main__":
    pass
