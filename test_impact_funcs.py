import Impact_Funcs

# common data for conducting many of the tests
TEST_CITATION_DATA = [9, 14, 3, 9, 11, 2, 1, 2, 0, 1, 0, 42, 36, 2, 1, 0]
TEST_YEAR_DATA = [1997, 1997, 1997, 1997, 1998, 1999, 2000, 2000, 2001, 2001, 2001, 1997, 2000, 2001, 2000, 2000]
TEST_AUTHOR_CNT = [1, 3, 4, 4, 2, 4, 4, 1, 1, 2, 2, 3, 3, 1, 1, 4]
TEST_AUTHOR_ORDER = [1, 3, 3, 3, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3]
TEST_PRIMARY = [False, True, False, False, True, False, True, False, True, True, True, True, True, True, True, False]
# coauthor list is independent of the above data
TEST_COAUTHORS = ["Adams, D.C.;Gurevitch, J.", ".", "Adams, D.C.;Gurevitch, J.", ".",
                  "DiGiovanni, D.;Oden, N.L.;Sokal, R.R.", "DiGiovanni, D.;Oden, N.L.;Sokal, R.R.",
                  "Adams, D.C.", ".", "DiGiovanni, D.;Oden, N.L.;Sokal, R.R.", ".", "Adams, D.C.;Gurevitch, J.",
                  ".", "Oden, N.L.;Sokal, R.R.;Thomson, B.A.", "Oden, N.L.;Sokal, R.R.;Thomson, B.A.", ".",
                  "Kumar, S.", ".", "Kumar, S."]



def test_rank():
    indices = [8, 10, 15, 6, 9, 14, 5, 7, 13, 2, 0, 3, 4, 1, 12, 11]
    ranks = [10, 13, 9, 11, 12, 6, 3, 7, 0, 4, 1, 15, 14, 8, 5, 2]
    assert Impact_Funcs.rank(16, indices) == ranks


def test_sort_and_rank():
    # this is the index of the citations in ith order, i.e., the 0th entry lists the index of the smallest value,
    # the 1st entry lists the index of the second smallest value, etc.
    indices = [8, 10, 15, 6, 9, 14, 5, 7, 13, 2, 0, 3, 4, 1, 12, 11]
    # rank_order is the rank of the ith entry (starting at 1, not 0), from high to low
    rank_order = [6, 3, 7, 5, 4, 10, 13, 9, 16, 12, 15, 1, 2, 8, 11, 14]
    assert Impact_Funcs.sort_and_rank(TEST_CITATION_DATA, len(TEST_CITATION_DATA)) == (indices, rank_order)


def test_calculate_median_odd():
    # test when there are an odd number of values
    assert Impact_Funcs.calculate_median([1, 12, 3, 10, 4]) == 4


def test_calculate_median_even():
    # test when there are an even number of values
    assert Impact_Funcs.calculate_median([1, 10, 3, 4]) == 3.5


def test_calculate_ranks():
    rank_order = [6, 3, 7, 5, 4, 10, 13, 9, 16, 12, 15, 1, 2, 8, 11, 14]
    # the cumulative citation count, when pubs are ranked from most to fewest cites
    cumulative_cnt = [42, 78, 92, 103, 112, 121, 124, 126, 128, 130, 131, 132, 133, 133, 133, 133]
    assert Impact_Funcs.calculate_ranks(TEST_CITATION_DATA) == (rank_order, cumulative_cnt)


def test_publication_ages():
    year = 2018
    answer = [22, 22, 22, 22, 21, 20, 19, 19, 18, 18, 18, 22, 19, 18, 19, 19]
    assert Impact_Funcs.publication_ages(year, TEST_YEAR_DATA) == answer


def test_citations_per_year():
    answer = [9/22, 14/22, 3/22, 9/22, 11/21, 2/20, 1/19, 2/19, 0/18, 1/18, 0/18, 42/22, 36/19, 2/18, 1/19, 0/19]
    ages = Impact_Funcs.publication_ages(2018, TEST_YEAR_DATA)
    assert Impact_Funcs.citations_per_year(TEST_CITATION_DATA, ages) == answer

"""


def total_citations_each_year(total_cite_list: list) -> list:
    tcpy = [total_cite_list[0]]
    for i in range(1, len(total_cite_list)):
        tcpy.append(total_cite_list[i] - total_cite_list[i - 1])
    return tcpy


def author_effort(measure: str, n_authors: int, author_pos: int = 1) -> float:
    if measure == "fractional":
        return 1 / n_authors
    elif measure == "proportional":
        return 2*(n_authors + 1 - author_pos) / (n_authors*(n_authors + 1))
    elif measure == "geometric":
        return 2**(n_authors - author_pos) / (2**n_authors - 1)
    elif measure == "harmonic":
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
"""


def test_calculate_total_pubs():
    assert Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA) == 16


def test_calculate_total_cites():
    assert Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA) == 133


def test_max_cites():
    assert Impact_Funcs.calculate_max_cites(TEST_CITATION_DATA) == 42


def test_calculate_mean_cites():
    p = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    c = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_mean_cites(c, p) == 133/16


def test_calculate_median_cites():
    assert Impact_Funcs.calculate_median(TEST_CITATION_DATA) == 2


def test_calculate_h_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    is_core = [True, True, False, True, True, False, False, False, False, False, False, True, True, False, False, False]
    assert Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order) == (6, is_core)


def test_calculate_h_core():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    _, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, core) == sum((9, 9, 11, 14, 36, 42))  # 121


def test_calculate_hirsch_min_const():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, _ = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_hirsch_min_const(total_cites, h) == 133/36


def test_calculate_g_index():
    # cumulative_cnt = [42, 78, 92, 103, 112, 121, 124, 126, 128, 130, 131, 132, 133, 133, 133, 133]
    # rank squared =   [1   4   9   16   25   36   49   64   81   100  121  144  <- g = 11
    rank_order, cumulative_cites = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_g_index(cumulative_cites, rank_order) == 11


def test_calculate_h2_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_h2_index(TEST_CITATION_DATA, rank_order) == 3


def test_calculate_hg_index():
    rank_order, cumulative_cites = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, _ = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    g = Impact_Funcs.calculate_g_index(cumulative_cites, rank_order)
    assert round(Impact_Funcs.calculate_hg_index(h, g), 3) == 8.124




"""


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
"""

def test_calculate_a_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    core_total = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, core)
    assert Impact_Funcs.calculate_a_index(core_total, h) == 121/6


def test_calculate_r_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    core_total = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, core)
    assert Impact_Funcs.calculate_r_index(core_total) == 11  # square-root of 121


def test_calculate_rm_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    _, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert round(Impact_Funcs.calculate_rm_index(TEST_CITATION_DATA, core), 4) == 5.0536


"""

# ar-index (Jin 2007; Jin et al 2007)
def calculate_ar_index(citations: list, pub_years: list, is_core: list, year: int) -> float:
    pub_ages = publication_ages(year, pub_years)
    cites_per_year = citations_per_year(citations, pub_ages)
    ar_index = 0
    for i in range(len(citations)):
        if is_core[i]:
            ar_index += cites_per_year[i]
    return math.sqrt(ar_index)
"""


def test_calculate_m_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    _, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_m_index(TEST_CITATION_DATA, core) == 12.5


"""
# q2-index (Cabrerizo et al 2010)
def calculate_q2_index(h: int, m: float) -> float:
    return math.sqrt(h * m)
"""

def test_calculate_k_index():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    _, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    core_cites = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, core)
    assert round(Impact_Funcs.calculate_k_index(total_cites, core_cites, total_pubs), 5) == 83.81771

    # data and answer from original paper by Ye and Rousseau (2010)
    total_cites = 863
    total_pubs = 102
    core_cites = 410
    assert round(Impact_Funcs.calculate_k_index(total_cites, core_cites, total_pubs), 2) == 7.66


def test_calculate_franceschini_f_index():
    assert Impact_Funcs.calculate_franceschini_f_index(TEST_CITATION_DATA, TEST_YEAR_DATA) == 5  # 2001 - 1997 + 1


def test_calculate_weighted_h_index():
    # data and answer from original paper, Egghe and Rousseau 2008
    citations = [10, 8, 7, 4, 3]
    h = 4
    rank_order = [1, 2, 3, 4, 5]
    cumulative_cites = [10, 18, 25, 29, 32]

    assert Impact_Funcs.calculate_weighted_h_index(citations, cumulative_cites, rank_order, h) == 5


"""
# normalized h-index (Sidiropoulos et al 2007)
def calculate_normalized_h_index(h: int, total_pubs: int) -> float:
    return h / total_pubs


# apparent h-index (Mohammed et al 2020)
def calculate_apparent_h_index(citations: list, h: int) -> float:
    non_zero_cnt = 0
    for i in range(len(citations)):
        if citations[i] > 0:
            non_zero_cnt += 1
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
"""

def test_calculate_v_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, _ = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    n = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_v_index(h, n) == 37.5


def test_calculate_e_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    core_total = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, is_core)
    assert round(Impact_Funcs.calculate_e_index(core_total, h), 4) == 9.2195


"""

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
"""


def test_calculate_tapered_h_index():
    # data and answers from original publication, Anderson et al 2008
    citations = [100, 98, 98, 97, 96, 4, 3, 2, 1, 1]
    rank = [i+1 for i in range(10)]
    assert round(Impact_Funcs.calculate_tapered_h_index(citations, rank), 2) == 13.27

    citations = [9, 8, 8, 6, 5, 4, 4, 3, 2, 1]
    assert round(Impact_Funcs.calculate_tapered_h_index(citations, rank), 2) == 6.89

    citations = [10 for _ in range(10)]
    assert round(Impact_Funcs.calculate_tapered_h_index(citations, rank), 2) == 10

    citations = [9, 8, 7, 6, 5]
    rank = [i+1 for i in range(5)]
    assert round(Impact_Funcs.calculate_tapered_h_index(citations, rank), 2) == 5.79

    citations = [120, 110, 100, 90, 80]
    assert round(Impact_Funcs.calculate_tapered_h_index(citations, rank), 2) == 12.46


"""
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
        num = 1 / author_pos[i]
        denom = 0
        for j in range(n_authors[i]):
            denom += 1 / (j + 1)
        r = num / denom
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
    pub_ages = publication_ages(year, pub_years)
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
def calculate_two_sided_h(citations: list, rank_order: list, h: int, multidim_h: list) -> list:
    # only need to calculate the upper part of the index the center and tail are identical to multidimensional h
    # auto-calculate for as many steps in core as equal to length of steps in tail
    two_sided_h = [i for i in multidim_h]
    j = 0
    tmph = h
    k = 1
    while k < len(multidim_h):
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
        if citations[i] * rank_order[i] > maxprod_index:
            maxprod_index = citations[i] * rank_order[i]
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
        mon_equiv.append(author_effort("harmonic", n_authors[i], author_pos[i]))
    monograph_equiv = sum(mon_equiv)
    return 1 - monograph_equiv / len(citations)


# profit adjusted h-index (Aziz and Rozing 2013)
def calculate_profit_adj_h_index(citations: list, n_authors: list, author_pos: list) -> int:
    n = len(citations)
    mon_equiv = []
    for i in range(n):
        mon_equiv.append(author_effort("harmonic", n_authors[i], author_pos[i]))
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

"""

def test_calculate_em_components():
    # data and answer from original paper, Bihari Tripathi 2017
    answer = [10, 6, 5, 3, 2, 2, 2]
    citations = [30, 30, 25, 22, 22, 21, 15, 15, 14, 10, 10, 10, 9, 8, 1, 0, 0, 0, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert Impact_Funcs.calculate_em_components(citations, rank_order) == answer

    answer = [10, 7, 6, 4, 3, 3, 2, 2, 2, 2, 2, 2, 1]
    citations = [50, 45, 33, 30, 24, 23, 17, 12, 11, 10, 8, 8, 7, 6, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert Impact_Funcs.calculate_em_components(citations, rank_order) == answer


def test_calculate_emp_components():
    # data and answer from original paper, Bihari Tripathi 2017
    answer = [10, 9, 5, 4, 3, 2, 1, 1]
    citations = [30, 30, 25, 22, 22, 21, 15, 15, 14, 10, 10, 10, 9, 8, 1, 0, 0, 0, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert Impact_Funcs.calculate_emp_components(citations, rank_order) == answer

    answer = [10, 8, 6, 6, 5, 4, 3, 3, 2, 2, 1, 1]
    citations = [50, 45, 33, 30, 24, 23, 17, 12, 11, 10, 8, 8, 7, 6, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert Impact_Funcs.calculate_emp_components(citations, rank_order) == answer


def test_calculate_em_index():
    # data and answer from original paper, Bihari Tripathi 2017
    citations = [30, 30, 25, 22, 22, 21, 15, 15, 14, 10, 10, 10, 9, 8, 1, 0, 0, 0, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert round(Impact_Funcs.calculate_em_index(citations, rank_order), 2) == 5.48

    # data and answer from original paper, Bihari Tripathi 2021
    citations = [50, 45, 33, 30, 24, 23, 17, 12, 11, 10, 8, 8, 7, 6, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert round(Impact_Funcs.calculate_em_index(citations, rank_order), 2) == 6.78


def test_calculate_emp_index():
    # data from original paper, Bihari Tripathi 2017
    #    note: I've cross-checked the math, and the value reported in their paper is slightly inaccurate,
    #          as they appear to have truncated the value to one decimal rather than rounding it. They report
    #          5.91 when it should be 5.92, as the value calculated to more digits is 5.91608.
    citations = [30, 30, 25, 22, 22, 21, 15, 15, 14, 10, 10, 10, 9, 8, 1, 0, 0, 0, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert round(Impact_Funcs.calculate_emp_index(citations, rank_order), 3) == 5.916

    # data and answer from original paper, Bihari Tripathi 2021
    citations = [50, 45, 33, 30, 24, 23, 17, 12, 11, 10, 8, 8, 7, 6, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert round(Impact_Funcs.calculate_emp_index(citations, rank_order), 2) == 7.14


def test_calculate_iterative_weighted_em_index():
    # data from original paper, Bihari Tripathi 2021
    # as in the previous paper, the answer they present (18.96) seems to have a rounding issue and is only
    # accurate to a single decimal place, as the value should be 18.98334 (calculated independently).
    # I suspect they round/truncate calculated values at an early stage of the process and accuracy is lost a bit
    citations = [50, 45, 33, 30, 24, 23, 17, 12, 11, 10, 8, 8, 7, 6, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert round(Impact_Funcs.calculate_iterative_weighted_em_index(citations, rank_order), 5) == 18.98334


def test_calculate_iterative_weighted_emp_index():
    # data and answer from original paper, Bihari Tripathi 2021
    citations = [50, 45, 33, 30, 24, 23, 17, 12, 11, 10, 8, 8, 7, 6, 6, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    assert round(Impact_Funcs.calculate_iterative_weighted_emp_index(citations, rank_order), 2) == 20.57


"""

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
def calculate_impact_vitality(total_cite_list: list) -> Union[str, float]:
    w = 5  # fix at a 5 year window
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
def calculate_dci_index(total_citations: list, logbase: int) -> list:
    # create list of novel citation counts per year
    yearly_cites = []
    cold = None
    for c in total_citations:
        if cold is None:
            yearly_cites.append(c)
        else:
            yearly_cites.append(c - cold)
        cold = c
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
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = []
    for y in year_cnts:
        data.append([year_cnts[y], y])
    data.sort(reverse=True)
    h = 0
    for i in range(len(data)):
        avg = data[i][0]
        if avg >= i + 1:
            h += 1
    if (h > 0) and (h < len(data)):
        ch = data[h-1][0]
        chp1 = data[h][0]
        hint = ((h+1)*ch - h*chp1) / (1 - chp1 + ch)
    else:
        hint = h
    return hint


# career years h-index by diffusion speed (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_diffspeed(pub_years: list, cites: list, cur_year: int) -> float:
    miny = min(pub_years)
    maxy = max(pub_years)
    cite_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        cite_cnts[pub_years[i]] += c
    data = []
    for y in cite_cnts:
        data.append([cite_cnts[y]/(cur_year - y + 1), y])
    data.sort(reverse=True)
    h = 0
    for i in range(len(data)):
        avg = data[i][0]
        if avg >= i + 1:
            h += 1
    if (h > 0) and (h < len(data)):
        ch = data[h-1][0]
        chp1 = data[h][0]
        hint = ((h+1)*ch - h*chp1) / (1 - chp1 + ch)
    else:
        hint = h
    return hint


# collaborative index (Lawani 1980)
def calculate_collaborative_index(author_cnts: list) -> float:
    maxa = max(author_cnts)
    ci = 0
    for a in range(1, maxa+1):
        ci += a * author_cnts.count(a)
    return ci / len(author_cnts)


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


# P1 index (van Eck and Waltman 2008)
def calculate_p1_index(citations: list) -> int:
    cnt = 0
    for c in citations:
        if c > 0:
            cnt += 1
    return cnt


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
    # count pubs with zero citations
    pz = 0
    for c in citations:
        if c == 0:
            pz += 1
    t = (h**4 + (core_cites - h**2)**2) / total_cites + ((len(citations) - h - pz)**2 - pz**2) / len(citations)
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
    def count_pubs(tmpc: list) -> int:
        tcnt = 0
        for c in tmpc:
            if c > 0:
                tcnt += 1
        return tcnt

    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: pub_years.count(y) for y in range(miny, maxy+1)}
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)
    em_component = []
    tmp_data = [d for d in data]  # make a temporary copy of the data
    n_pubs = count_pubs(tmp_data)
    if n_pubs == 1:
        em_component = [1]
    else:
        while n_pubs > 1:
            if max(tmp_data) == 1:
                em_component.append(1)
                n_pubs = 0
            else:
                h = 0
                for i in range(len(tmp_data)):
                    cnt = tmp_data[i]
                    if cnt >= i + 1:
                        h += 1
                em_component.append(h)
                tmp_data = [max(0, d-h) for d in tmp_data]
                n_pubs = count_pubs(tmp_data)
    return math.sqrt(sum(em_component))


# year-based EM-index by publication year citations (Bihari and Tripathi 2018)
def calculate_year_based_em_pycites(pub_years: list, cites: list) -> float:
    def count_cites(tmpc: list) -> int:
        tcnt = 0
        for cc in tmpc:
            if cc > 0:
                tcnt += 1
        return tcnt

    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)

    em_component = []
    tmp_data = [d for d in data]  # make a temporary copy of the data
    n_cites = count_cites(tmp_data)
    if n_cites == 1:
        em_component = [1]
    else:
        while n_cites > 1:
            if max(tmp_data) == 1:
                em_component.append(1)
                n_cites = 0
            else:
                h = 0
                for i in range(len(tmp_data)):
                    cnt = tmp_data[i]
                    if cnt >= i + 1:
                        h += 1
                em_component.append(h)
                tmp_data = [max(0, d-h) for d in tmp_data]
                n_cites = count_cites(tmp_data)
    return math.sqrt(sum(em_component))


# year-based EM-index by citations (Bihari and Tripathi 2018)
def calculate_year_based_em_cites(total_cite_list: list) -> float:
    def count_cites(tmpc: list) -> int:
        tcnt = 0
        for cc in tmpc:
            if cc > 0:
                tcnt += 1
        return tcnt

    total_cites_per_year = total_citations_each_year(total_cite_list)
    total_cites_per_year.sort(reverse=True)

    em_component = []
    tmp_data = [d for d in total_cites_per_year]  # make a temporary copy of the data
    n_cites = count_cites(tmp_data)
    if n_cites == 1:
        em_component = [1]
    else:
        while n_cites > 1:
            if max(tmp_data) == 1:
                em_component.append(1)
                n_cites = 0
            else:
                h = 0
                for i in range(len(tmp_data)):
                    cnt = tmp_data[i]
                    if cnt >= i + 1:
                        h += 1
                em_component.append(h)
                tmp_data = [max(0, d-h) for d in tmp_data]
                n_cites = count_cites(tmp_data)
    return math.sqrt(sum(em_component))


# year-based EM'-index by publications (Bihari and Tripathi 2018)
def calculate_year_based_emp_pub(pub_years: list) -> float:
    def count_pubs(tmpc: list) -> int:
        tcnt = 0
        for c in tmpc:
            if c > 0:
                tcnt += 1
        return tcnt

    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: pub_years.count(y) for y in range(miny, maxy+1)}
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)
    em_component = []
    tmp_data = [d for d in data]  # make a temporary copy of the data
    n_pubs = count_pubs(tmp_data)
    if n_pubs == 1:
        em_component = [1]
    else:
        while n_pubs > 1:
            if max(tmp_data) == 1:
                em_component.append(1)
                n_pubs = 0
            else:
                h = 0
                for i in range(len(tmp_data)):
                    cnt = tmp_data[i]
                    if cnt >= i + 1:
                        h += 1
                em_component.append(h)
                # subtract h only from top h years
                for i in range(h):
                    tmp_data[i] = max(0, tmp_data[i]-h)
                tmp_data.sort(reverse=True)
                n_pubs = count_pubs(tmp_data)
    return math.sqrt(sum(em_component))


# year-based EM'-index by publication year citations (Bihari and Tripathi 2018)
def calculate_year_based_emp_pycites(pub_years: list, cites: list) -> float:
    def count_cites(tmpc: list) -> int:
        tcnt = 0
        for cc in tmpc:
            if cc > 0:
                tcnt += 1
        return tcnt

    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)

    em_component = []
    tmp_data = [d for d in data]  # make a temporary copy of the data
    n_cites = count_cites(tmp_data)
    if n_cites == 1:
        em_component = [1]
    else:
        while n_cites > 1:
            if max(tmp_data) == 1:
                em_component.append(1)
                n_cites = 0
            else:
                h = 0
                for i in range(len(tmp_data)):
                    cnt = tmp_data[i]
                    if cnt >= i + 1:
                        h += 1
                em_component.append(h)
                for i in range(h):
                    tmp_data[i] = max(0, tmp_data[i]-h)
                tmp_data.sort(reverse=True)
                n_cites = count_cites(tmp_data)
    return math.sqrt(sum(em_component))


# year-based EM'-index by citations (Bihari and Tripathi 2018)
def calculate_year_based_emp_cites(total_cite_list: list) -> float:
    def count_cites(tmpc: list) -> int:
        tcnt = 0
        for cc in tmpc:
            if cc > 0:
                tcnt += 1
        return tcnt

    total_cites_per_year = total_citations_each_year(total_cite_list)
    total_cites_per_year.sort(reverse=True)

    em_component = []
    tmp_data = [d for d in total_cites_per_year]  # make a temporary copy of the data
    n_cites = count_cites(tmp_data)
    if n_cites == 1:
        em_component = [1]
    else:
        while n_cites > 1:
            if max(tmp_data) == 1:
                em_component.append(1)
                n_cites = 0
            else:
                h = 0
                for i in range(len(tmp_data)):
                    cnt = tmp_data[i]
                    if cnt >= i + 1:
                        h += 1
                em_component.append(h)
                for i in range(h):
                    tmp_data[i] = max(0, tmp_data[i]-h)
                tmp_data.sort(reverse=True)
                n_cites = count_cites(tmp_data)
    return math.sqrt(sum(em_component))


# h' index (Zhang 2012)
def calculate_h_prime(h: int, e: float, t: float) -> float:
    return e*h/t


# hc index (Khurana and Sharma 2022)
def calculate_hc(h: int, m: int) -> int:
    if h <= 1:
        return h
    else:
        k = math.trunc(math.log(m-1, h))
        return h + k
"""

def test_calculate_k_index_anania_caruso():
    # data and answers from original publication, Anania and Caruso 2013
    citations = [20, 16, 15, 15, 15, 10, 6, 6, 6, 2, 2, 2, 1, 1, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    core_total = Impact_Funcs.calculate_h_core(citations, is_core)
    assert round(Impact_Funcs.calculate_k_index_anania_caruso(h, core_total), 2) == 6.60

    citations = [9, 8, 8, 7, 7, 6, 3, 2, 2, 1, 1, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    core_total = Impact_Funcs.calculate_h_core(citations, is_core)
    assert round(Impact_Funcs.calculate_k_index_anania_caruso(h, core_total), 2) == 6.20


def test_calculate_w_index_anania_caruso():
    # data and answers from original publication, Anania and Caruso 2013
    citations = [20, 16, 15, 15, 15, 10, 6, 6, 6, 2, 2, 2, 1, 1, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    total_cites = Impact_Funcs.calculate_total_cites(citations)
    assert round(Impact_Funcs.calculate_w_index_anania_caruso(h, total_cites), 2) == 6.69

    citations = [9, 8, 8, 7, 7, 6, 3, 2, 2, 1, 1, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    total_cites = Impact_Funcs.calculate_total_cites(citations)
    assert round(Impact_Funcs.calculate_w_index_anania_caruso(h, total_cites), 2) == 6.33

"""
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
    for i, c in enumerate(citations):
        s += 2*(i+0.5)*c  # it is i + 0.5 rather than i - 0.5 because i is counting from 0
    return s**(1/3)


# slg (Gagolewski et al 2022)
def calculate_slg(citations: list) -> float:
    return sum(math.log10(c+1) for c in citations)


# 3DSI w/pr (Gagolewski et al 2022)
def calculate_3dsi_pr(total_pubs: int, total_cites: int, csr: float) -> list:
    pr = (total_pubs - 2*csr**3/total_cites + 1) / (total_pubs - csr**3/total_cites)
    return [total_pubs, total_cites, pr]
"""

def test_calculate_total_collaborators():
    assert Impact_Funcs.calculate_total_collaborators(TEST_COAUTHORS) == 7


def test_calculate_partnership_ability():
    assert Impact_Funcs.calculate_partnership_ability(TEST_COAUTHORS) == 3


def test_calculate_stratified_h():
    """
    working out answer from test data

    TEST_CITATION_DATA = [9, 14, 3, 9, 11, 2, 1, 2, 0, 1, 0, 42, 36, 2, 1, 0]
    TEST_AUTHOR_CNT = [1, 3, 4, 4, 2, 4, 4, 1, 1, 2, 2, 3, 3, 1, 1, 4]
    TEST_AUTHOR_ORDER = [1, 3, 3, 3, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 3]

    cite_data_first = [9, 2, 2, 0, 1, 0, 42, 36, 2, 1], h = 3
    cite_data_second = [11], h = 1
    cite_data_third = [14, 3, 9, 1, 0], h = 3
    cite_dat_last = [9, 14, 11, 2, 0, 2, 1], h = 3
    """
    h = 6
    answer = [6, 3, 1, 3, 3]
    assert Impact_Funcs.calculate_stratified_h(h, TEST_AUTHOR_ORDER, TEST_AUTHOR_CNT, TEST_CITATION_DATA) == answer


def test_calculate_platinum_h():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, _ = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)  # 6
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)  # 133
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)  # 16
    age = max(TEST_YEAR_DATA) - min(TEST_YEAR_DATA) + 1  # 5
    assert Impact_Funcs.calculate_platinum_h(h, total_cites, total_pubs, age) == 9.975


def test_calculate_stochastic_h():
    # data and answer from original publication, Nair and Turlach 2012
    h = 10
    cites = [770, 124, 110, 55, 39, 36, 34, 17, 13, 11, 10, 9, 9, 8, 7, 6, 5, 4, 3, 3, 3, 3, 3, 2, 2, 1, 1, 1, 0, 0, 0]
    years = [2004, 2000, 2000, 2001, 2005, 1997, 2004, 1997, 1997, 1996, 1998, 2005, 1997, 1999, 2008, 1999, 1999,
             1996, 2006, 2005, 2002, 1999, 1997, 2008, 2004, 2009, 2007, 2004, 2010, 2007, 2000]
    cyear = 2010
    answer = 10.828
    hs = Impact_Funcs.calculate_stochastic_h(h, cites, cyear, years)
    assert round(hs, 3) == answer


def test_calculate_multiple_h_index():
    # data and answer from original publication, Yaminfirooz and Gholinia 2015
    answer = 42.45
    citations = [20, 18, 18, 13, 13, 12, 10, 9, 6, 5, 5, 4, 3, 2, 2, 2, 1, 1, 1, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    ages = [10, 8, 9, 7, 7, 8, 8, 6, 4, 5, 3, 3, 4, 2, 2, 1, 3, 3, 5, 1]
    # original paper gave the ages, not the publication year, so we're back calculating
    year = 2010
    pub_year = [year + 1 - a for a in ages]

    assert round(Impact_Funcs.calculate_multiple_h_index(citations, rank_order, is_core, h, year,
                                                         pub_year), 2) == answer


def test_calculate_hmaj_index():
    assert Impact_Funcs.calculate_hmaj_index(TEST_CITATION_DATA, TEST_PRIMARY) == 4


def test_calculate_total_pubs_coauthor_adj_fractional():
    assert Impact_Funcs.calculate_total_pubs_coauthor_adj("fractional", TEST_AUTHOR_CNT,
                                                          TEST_AUTHOR_ORDER) == 8.75


def test_calculate_total_pubs_coauthor_adj_proportional():
    assert round(Impact_Funcs.calculate_total_pubs_coauthor_adj("proportional", TEST_AUTHOR_CNT,
                                                                TEST_AUTHOR_ORDER), 3) == 9.033


def test_calculate_total_pubs_coauthor_adj_geometric():
    assert round(Impact_Funcs.calculate_total_pubs_coauthor_adj("geometric", TEST_AUTHOR_CNT,
                                                                TEST_AUTHOR_ORDER), 3) == 9.019


def test_calculate_total_pubs_coauthor_adj_harmonic():
    assert round(Impact_Funcs.calculate_total_pubs_coauthor_adj("harmonic", TEST_AUTHOR_CNT,
                                                                TEST_AUTHOR_ORDER), 3) == 9.059
