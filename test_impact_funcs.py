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
TEST_YEARLY_PUBCITE_DATA = [[0, 3, 13, 17, 26],  # cumulative citations each year for each publication
                            [0, 1, 2, 7, 11],
                            [1, 7, 19, 32, 59],
                            [0, 0, 0, 0, 0],
                            [1, 2, 2, 3, 3],
                            [0, 0, 2, 8, 10],
                            [None, 3, 5, 11, 16],
                            [None, 0, 0, 0, 0],
                            [None, None, 1, 3, 4],
                            [None, None, None, 0, 3],
                            [None, None, None, 4, 11],
                            [None, None, None, 0, 1],
                            [None, None, None, 0, 2],
                            [None, None, None, 0, 0],
                            [None, None, None, None, 0],
                            [None, None, None, None, 1],
                            [None, None, None, None, 1],
                            [None, None, None, None, 0]]


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


def test_total_citations_each_year():
    data = [0, 3, 13, 17, 26, 32, 41, 48, 53, 71, 83, 107]
    answer = [0, 3, 10, 4, 9, 6, 9, 7, 5, 18, 12, 24]
    assert Impact_Funcs.total_citations_each_year(data) == answer


def test_author_effort():
    assert Impact_Funcs.author_effort("fractional", 5) == 0.2
    assert round(Impact_Funcs.author_effort("proportional", 5, 1), 4) == 0.3333
    assert Impact_Funcs.author_effort("fractional", 5, 3) == 0.2
    assert round(Impact_Funcs.author_effort("geometric", 5, 1), 4) == 0.5161
    assert round(Impact_Funcs.author_effort("geometric", 5, 3), 4) == 0.1290
    assert round(Impact_Funcs.author_effort("harmonic", 5, 1), 4) == 0.4380
    assert round(Impact_Funcs.author_effort("harmonic", 5, 3), 4) == 0.1460
    assert round(Impact_Funcs.author_effort("harmonic_aziz", 5, 1), 4) == 0.2941
    assert round(Impact_Funcs.author_effort("harmonic_aziz", 5, 3), 4) == 0.0588


def test_citations_per_pub_per_year():
    answer = [[0, 3, 10, 4, 9],  # citations each year for each publication
              [0, 1, 1, 5, 4],
              [1, 6, 12, 13, 27],
              [0, 0, 0, 0, 0],
              [1, 1, 0, 1, 0],
              [0, 0, 2, 6, 2],
              [0, 3, 2, 6, 5],
              [0, 0, 0, 0, 0],
              [0, 0, 1, 2, 1],
              [0, 0, 0, 0, 3],
              [0, 0, 0, 4, 7],
              [0, 0, 0, 0, 1],
              [0, 0, 0, 0, 2],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 0],
              [0, 0, 0, 0, 1],
              [0, 0, 0, 0, 1],
              [0, 0, 0, 0, 0]]
    x = Impact_Funcs.citations_per_pub_per_year(TEST_YEARLY_PUBCITE_DATA)
    for r, row in enumerate(x):
        for c, col in enumerate(row):
            assert col == answer[r][c]


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
"""


def test_calculate_real_h_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, _ = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert round(Impact_Funcs.calculate_real_h_index(TEST_CITATION_DATA, rank_order, h), 4) == 6.4286

    # data and answer from original publication
    citations = [9, 7, 6, 5, 3, 0]
    rank_order = [1, 2, 3, 4, 5, 6]
    h = 4
    assert round(Impact_Funcs.calculate_real_h_index(citations, rank_order, h), 2) == 4.33


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


def test_calculate_ar_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    _, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert round(Impact_Funcs.calculate_ar_index(TEST_CITATION_DATA, TEST_YEAR_DATA, core, 2001), 4) == 5.9624


def test_calculate_m_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    _, core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_m_index(TEST_CITATION_DATA, core) == 12.5


def test_calculate_q2_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    m = Impact_Funcs.calculate_m_index(TEST_CITATION_DATA, is_core)
    assert round(Impact_Funcs.calculate_q2_index(h, m), 4) == 8.6603


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


def test_calculate_normalized_h_index():
    assert Impact_Funcs.calculate_normalized_h_index(6, 16) == 6/16


def test_calculate_apparent_h_index():
    assert Impact_Funcs.calculate_apparent_h_index(TEST_CITATION_DATA, 6) == 6*13/16


def test_calculate_chi_index():
    rec = Impact_Funcs.calculate_rec_index(TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_chi_index(rec), 4) == 8.4853


def test_calculate_rec_index():
    assert Impact_Funcs.calculate_rec_index(TEST_CITATION_DATA) == 72


def test_calculate_reci_recp():
    reci, recp = Impact_Funcs.calculate_reci_recp(TEST_CITATION_DATA, 6)
    assert reci == 72
    assert recp == 36


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


def test_calculate_rational_h():
    # data and answer from Guns and Rousseau 2009
    citations = [9, 7, 6, 5, 3, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_rational_h(citations, rank_order, is_core, h), 2) == 4.78


def test_h2_regions():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    core_cites = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, is_core)
    assert round(Impact_Funcs.calculate_h2_upper_index(total_cites, core_cites, h), 4) == 63.9098
    assert round(Impact_Funcs.calculate_h2_center_index(total_cites, h), 4) == 27.0677
    assert round(Impact_Funcs.calculate_h2_tail_index(total_cites, core_cites), 4) == 9.0226


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


def test_calculate_pi_index_rate():
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_pi_index(total_pubs, TEST_CITATION_DATA, rank_order) == 1.03


def test_calculate_pi_rate():
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    pi_index = Impact_Funcs.calculate_pi_index(total_pubs, TEST_CITATION_DATA, rank_order)
    assert round(Impact_Funcs.calculate_pi_rate(total_pubs, pi_index), 4) == 25.75


def test_calculate_prathap_p_index():
    # data and answers from original publication
    assert round(Impact_Funcs.calculate_prathap_p_index(100, 10), 1) == 10
    assert round(Impact_Funcs.calculate_prathap_p_index(250, 50), 1) == 10.8
    assert round(Impact_Funcs.calculate_prathap_p_index(300, 50), 1) == 12.2
    assert round(Impact_Funcs.calculate_prathap_p_index(250, 25), 1) == 13.6


def test_calculate_ph_ratio():
    # data and answers from original publication
    citations = [79, 34, 32, 25, 16, 13, 12, 11, 11, 11, 8, 8, 8, 8, 7, 7, 6, 6, 5, 5]
    total_citations = Impact_Funcs.calculate_total_cites(citations)
    total_pubs = Impact_Funcs.calculate_total_pubs(citations)
    p = Impact_Funcs.calculate_prathap_p_index(total_citations, total_pubs)
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_ph_ratio(p, h), 3) == 1.695


def test_calculate_fractional_p_index():
    # data and answers from original publication
    citations = [79, 34, 32, 25, 16, 13, 12, 11, 11, 11, 8, 8, 8, 8, 7, 7, 6, 6, 5, 5]
    n_authors = [3, 4, 4, 2, 4, 4, 10, 2, 3, 3, 3, 1, 2, 4, 2, 1, 2, 2, 2, 3]
    assert round(Impact_Funcs.calculate_fractional_p_index(citations, n_authors), 2) == 11.51

    citations = [42, 21, 16, 12, 12, 10, 9, 9, 9, 8, 8, 8, 8, 7, 7, 7, 5, 5, 4, 4]
    n_authors = [4, 3, 4, 8, 3, 6, 3, 5, 4, 3, 3, 6, 4, 3, 8, 8, 4, 6, 3, 5]
    assert round(Impact_Funcs.calculate_fractional_p_index(citations, n_authors), 2) == 8.30


def test_calculate_harmonic_p_index():
    assert round(Impact_Funcs.calculate_harmonic_p_index(TEST_CITATION_DATA, TEST_AUTHOR_CNT,
                                                         TEST_AUTHOR_ORDER), 4) == 7.8709


def test_calculate_hi_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_hi_index(is_core, TEST_AUTHOR_CNT, h) == 2.25


def test_calculate_pure_h_index_frac():
    # data and answers from original publication
    citations = [10, 5, 2, 2]
    n_authors = [1, 1, 2, 2]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h) == 2

    citations = [30, 2, 1]
    n_authors = [3, 2, 2]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h), 2) == 1.26

    citations = [30, 2, 1, 1]
    n_authors = [3, 3, 3, 2]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h), 2) == 1.15

    citations = [2, 2, 1]
    n_authors = [3, 2, 3]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h), 2) == 1.26

    citations = [30, 2, 2, 1]
    n_authors = [3, 3, 1, 3]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h), 2) == 1.41



def test_calculate_pure_h_index_prop():
    # data and answers from original publication
    citations = [10, 5, 2, 2]
    n_authors = [1, 1, 2, 2]
    author_pos = [1, 1, 2, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h) == 2

    citations = [30, 2, 1]
    n_authors = [3, 2, 2]
    author_pos = [3, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h), 2) == 1.03

    citations = [30, 2, 1, 1]
    n_authors = [3, 3, 3, 2]
    author_pos = [1, 1, 1, 2]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h), 2) == 1.41

    citations = [2, 2, 1]
    n_authors = [3, 2, 3]
    author_pos = [2, 2, 2]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h), 2) == 1.15

    citations = [30, 2, 2, 1]
    n_authors = [3, 3, 1, 3]
    author_pos = [2, 3, 1, 3]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h), 2) == 1.41


def test_calculate_pure_h_index_geom():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert round(Impact_Funcs.calculate_pure_h_index_geom(is_core, TEST_AUTHOR_CNT, TEST_AUTHOR_ORDER, h), 4) == 3.1334


def test_calculate_tol_f_index():
    assert Impact_Funcs.calculate_tol_f_index(TEST_CITATION_DATA) == 7


def test_calculate_tol_t_index():
    assert Impact_Funcs.calculate_tol_t_index(TEST_CITATION_DATA) == 8


def test_calculate_mu_index():
    assert Impact_Funcs.calculate_mu_index(TEST_CITATION_DATA) == 9


def test_calculate_wu_w_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_wu_w_index(TEST_CITATION_DATA, rank_order) == 2


def test_calculate_wu_wq():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    w = Impact_Funcs.calculate_wu_w_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_wu_wq(TEST_CITATION_DATA, rank_order, w) == 16


def test_calculate_wohlin_w():
    maxv = max(TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_wohlin_w(TEST_CITATION_DATA, maxv), 4) == 28.5473


def test_calculate_contemporary_h_index():
    assert Impact_Funcs.calculate_contemporary_h_index(TEST_CITATION_DATA,TEST_YEAR_DATA, 2001) == 7


def test_calculate_hpd_index():
    assert Impact_Funcs.calculate_hpd_index(TEST_CITATION_DATA,TEST_YEAR_DATA, 2001) == 9


def test_calculate_specific_impact_s_index():
    # data and answers from original publication
    pub_years = [2004, 2005, 2005, 2006, 2006, 2007, 2007, 2008, 2008, 2008]
    year = 2008
    total_cites = 28
    assert round(Impact_Funcs.calculate_specific_impact_s_index(pub_years, year, total_cites), 2) == 2

"""
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
"""

def test_calculate_multidimensional_h_index():
    # data and answers from original publication
    citations = [42, 13, 11, 11, 10, 10, 10, 10, 9, 8, 7, 7, 7, 6, 5, 5, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2,
                 2, 2, 2, 2, 1, 1, 1, 1]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert Impact_Funcs.calculate_multidimensional_h_index(citations, rank_order,
                                                           is_core, h) == [9, 5, 5, 4, 3, 2, 2, 2, 2, 1, 1, 1, 1]


def test_calculate_two_sided_h():
    citations = [386, 282, 172, 113, 87, 83, 80, 69, 40, 38, 30, 28, 27, 24, 17, 14, 11, 11, 10, 7, 7, 4, 2, 1, 1,
                 1, 0, 0]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    mdh = Impact_Funcs.calculate_multidimensional_h_index(citations, rank_order, is_core, h)
    assert Impact_Funcs.calculate_two_sided_h(citations, rank_order, h, mdh, 4) == [8, 8, 10, 12, 15, 6, 2, 1, 1]


"""

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
"""



"""
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
"""


def test_calculate_dci_index():
    cumulative_citations_per_year = [0, 3, 13, 17, 26, 32, 41, 48, 53, 71, 83, 107]
    answer = [0, 0.903089987, 4.057738755, 5.391072088, 8.596936772, 10.91805362, 14.79414264, 18.29414264,
              21.44879141, 39.44879141, 51.44879141, 75.44879141]
    dci = Impact_Funcs.calculate_dci_index(cumulative_citations_per_year, 2)
    for i, d in enumerate(dci):
        assert round(d, 4) == round(answer[i], 4)


def test_calculate_ddci_index():
    cumulative_citations_per_year = [0, 3, 13, 17, 26, 32, 41, 48, 53, 71, 83, 107]
    dci = Impact_Funcs.calculate_dci_index(cumulative_citations_per_year, 2)
    assert round(Impact_Funcs.calculate_ddci_index(dci), 4) == 75.4488


def test_calculate_history_h_index():
    # data and answers from original publication
    # the original paper has an error in their first example, with an extra 1 tacked onto the end of the vector
    #  (this is clearly seen by comparing the values in Table 1 to the text on p. 814)
    # the sum of values in the vector should be 77 and not 78
    citations = [850, 444, 430, 270, 218, 106, 101, 96, 90, 84, 82, 50, 45, 44, 31, 27, 23, 23, 21, 20]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert Impact_Funcs.calculate_history_h_index(citations, h) == 77

    citations = [20 for _ in range(20)]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    assert Impact_Funcs.calculate_history_h_index(citations, h) == 38


def test_calculate_quality_quotient():
    # data and answers from original publication
    # the original paper has an error in their first example, with an extra 1 tacked onto the end of the vector
    #  (this is clearly seen by comparing the values in Table 1 to the text on p. 814)
    # the sum of values in the vector should be 77 and not 78, making the quotient 3.85 and not 3.90
    citations = [850, 444, 430, 270, 218, 106, 101, 96, 90, 84, 82, 50, 45, 44, 31, 27, 23, 23, 21, 20]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    hhist = Impact_Funcs.calculate_history_h_index(citations, h)
    assert Impact_Funcs.calculate_quality_quotient(h, hhist) == 3.85

    citations = [20 for _ in range(20)]
    rank_order, _ = Impact_Funcs.calculate_ranks(citations)
    h, _ = Impact_Funcs.calculate_h_index(citations, rank_order)
    hhist = Impact_Funcs.calculate_history_h_index(citations, h)
    assert Impact_Funcs.calculate_quality_quotient(h, hhist) == 1.9


def test_calculate_scientist_level():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    v, l = Impact_Funcs.calculate_scientist_level(total_cites, total_pubs)
    assert v == 2
    assert l == 1

    # data and answers from original publication
    v, l = Impact_Funcs.calculate_scientist_level(2288, 88)
    assert v == 3
    assert l == 2


def test_calculate_scientist_level_nonint():
    # data and answers from original publication
    assert round(Impact_Funcs.calculate_scientist_level_nonint(2288, 91), 3) == 4.933


"""
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
"""


def test_calculate_career_years_h_index_pub():
    # data and answer from original publication
    data = [2003, 2005, 2005, 2005, 2006, 2006, 2006, 2006, 2006, 2006, 2009, 2009, 2009, 2009, 2009, 2009, 2012,
            2012, 2012, 2012, 2012, 2012, 2011, 2011, 2011, 2011, 2011, 2011, 2011, 2007, 2007, 2007, 2007, 2007,
            2007, 2007, 2007, 2010, 2010, 2010, 2010, 2010, 2010, 2010, 2010, 2010, 2008, 2008, 2008, 2008, 2008,
            2008, 2008, 2008, 2008, 2008]
    assert Impact_Funcs.calculate_career_years_h_index_pub(data) == 6


def test_calculate_career_years_h_index_cite():
    assert Impact_Funcs.calculate_career_years_h_index_cite(TEST_YEAR_DATA, TEST_CITATION_DATA) == 3

    # data and answer from original publication
    citations = [24, 21, 19, 16, 15, 12, 11, 9, 8, 5]
    pub_years = [1999, 2008, 2009, 1997, 1998, 2010, 2006, 2004, 2003, 1001]
    assert Impact_Funcs.calculate_career_years_h_index_cite(pub_years, citations) == 8


def test_calculate_career_years_h_index_avgcite():
    assert round(Impact_Funcs.calculate_career_years_h_index_avgcite(TEST_YEAR_DATA, TEST_CITATION_DATA), 3) == 3.714


def test_calculate_career_years_h_index_diffspeed():
    # in the original paper they calculate ageas current year - pub year, rather than cy - py + 1. This would mean
    # articles in the present year would have an age of zero and an infinite diffusion.
    # the function has been tested using their published values and way of calculating the year, but the function
    # is coded so as to use the +1 in th age of an article
    # citations = [8, 16, 24, 18, 8, 19, 8, 8, 11, 5, 3, 2, 2]
    # pub_years = [2010, 2009, 2007, 2008, 2006, 1999, 2003, 2004, 1998, 2001, 2002, 2005, 2000]
    # year = 2011
    # assert round(Impact_Funcs.calculate_career_years_h_index_diffspeed(pub_years, citations, year), 2) == 4.37
    assert round(Impact_Funcs.calculate_career_years_h_index_diffspeed(TEST_YEAR_DATA,
                                                                       TEST_CITATION_DATA, 2001), 3) == 3.000


def test_calculate_collaborative_index():
    assert Impact_Funcs.calculate_collaborative_index(TEST_AUTHOR_CNT) == 2.5


def test_calculate_degree_of_collaboration():
    assert Impact_Funcs.calculate_degree_of_collaboration(TEST_AUTHOR_CNT) == 0.6875


def test_calculate_collaborative_coefficient():
    assert round(Impact_Funcs.calculate_collaborative_coefficient(TEST_AUTHOR_CNT), 4) == 0.4531


def test_calculate_i10_index():
    assert Impact_Funcs.calculate_i10_index(TEST_CITATION_DATA) == 4


def test_calculate_i100_index():
    citations = [9, 14, 3, 9, 11, 2, 1, 2, 0, 1, 0, 42, 36, 2, 1, 0, 100, 200, 1000, 1100]
    assert Impact_Funcs.calculate_i100_index(citations) == 4


def test_calculate_i1000_index():
    citations = [9, 14, 3, 9, 11, 2, 1, 2, 0, 1, 0, 42, 36, 2, 1, 0, 100, 200, 1000, 1100]
    assert Impact_Funcs.calculate_i1000_index(citations) == 2


def test_calculate_p1_index():
    assert Impact_Funcs.calculate_p1_index(TEST_CITATION_DATA) == 13


def test_ca():
    assert Impact_Funcs.calculate_p1_index(TEST_CITATION_DATA) == 13


def test_calculate_cited_paper_percent():
    assert Impact_Funcs.calculate_cited_paper_percent(TEST_CITATION_DATA) == 100*13/16


def test_calculate_uncitedness_factor():
    assert Impact_Funcs.calculate_uncitedness_factor(TEST_CITATION_DATA) == 3


def test_calculate_uncited_paper_percent():
    assert Impact_Funcs.calculate_uncited_paper_percent(TEST_CITATION_DATA) == 100*(1-13/16)


"""
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
"""


def test_calculate_academic_trace():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    total_core = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, is_core)
    assert round(Impact_Funcs.calculate_academic_trace(TEST_CITATION_DATA, total_cites, total_core, h), 4) == 57.0935


"""
# scientific quality index (Pluskiewicz1 et al 2019)
def calculate_scientific_quality_index(citations, self_citations) -> float:
    cnt = 0
    sharp_citations = [citations[i] - self_citations[i] for i in range(len(self_citations))]
    total_cites = sum(sharp_citations)
    for c in sharp_citations:
        if c >= 10:
            cnt += 1
    return total_cites/len(sharp_citations) + 100*cnt/len(sharp_citations)
"""


def test_calculate_first_author_h_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    assert Impact_Funcs.calculate_first_author_h_index(h, TEST_AUTHOR_ORDER, is_core) == 9


def test_calculate_o_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, _ = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    max_cites = Impact_Funcs.calculate_max_cites(TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_o_index(h, max_cites), 4) == 15.8745

"""

# discounted h-index (Ferrara and Romero 2013)
def calculate_discounted_h_index(h: int, total_cites: int, total_self: int) -> float:
    return h * math.sqrt((total_cites - total_self)/total_cites)
"""


def test_calculate_mikhailov_j_index():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    assert Impact_Funcs.calculate_mikhailov_j_index(TEST_CITATION_DATA, rank_order) == 4


def test_calculate_year_based_em_pub():
    # data and answers from original publication
    cnts_year = {2014: 41, 2015: 41, 2016: 38, 2013: 31, 2012: 29, 2008: 22, 2011: 18, 2007: 17, 2010: 17, 2017: 15,
                 2009: 13, 2006: 9}
    pub_years = []
    for y in cnts_year:
        for i in range(cnts_year[y]):
            pub_years.append(y)
    assert round(Impact_Funcs.calculate_year_based_em_pub(pub_years), 2) == 6.40

    cnts_year = {2015: 26, 2016: 23, 2007: 16, 2014: 16, 2010: 15, 2012: 15, 2011: 13, 2013: 13, 2008: 11, 2017: 10,
                 2009: 9, 2006: 3}
    pub_years = []
    for y in cnts_year:
        for i in range(cnts_year[y]):
            pub_years.append(y)
    assert round(Impact_Funcs.calculate_year_based_em_pub(pub_years), 1) == 4.9


def test_calculate_year_based_em_pycites():
    # data and answers from original publication
    citations = [80, 59, 48, 46, 30, 22, 11, 8, 3, 1, 0]
    pub_years = [2006, 2009, 2011, 2008, 2012, 2013, 2007, 2010, 2014, 2016, 2015]
    assert round(Impact_Funcs.calculate_year_based_em_pycites(pub_years, citations), 2) == 7.75

    citations = [81, 77, 61, 35, 34, 22, 20, 16, 4, 2, 1]
    pub_years = [2010, 2011, 2006, 2012, 2014, 2009, 2008, 2013, 2016, 2015, 2007]
    assert round(Impact_Funcs.calculate_year_based_em_pycites(pub_years, citations), 2) == 8.83

def test_calculate_year_based_em_cites():
    # data and answers from original publication

    # this first example does not generate the same em component list as in the original publication; I have
    # examined it closely and am confident they made an error in the paper
    # cumulative_citations = [99, 172, 228, 281, 330, 369, 389, 400, 403, 405]
    # assert round(Impact_Funcs.calculate_year_based_em_cites(cumulative_citations), 2) == 8.54

    # the second example does work correctly
    cumulative_citations = [27, 49, 70, 90, 110, 129, 146, 162, 173, 183, 190]
    assert round(Impact_Funcs.calculate_year_based_em_cites(cumulative_citations), 2) == 4.80


def test_calculate_year_based_emp_pub():
    # data and answers from original publication
    cnts_year = {2014: 41, 2015: 41, 2016: 38, 2013: 31, 2012: 29, 2008: 22, 2011: 18, 2007: 17, 2010: 17, 2017: 15,
                 2009: 13, 2006: 9}
    pub_years = []
    for y in cnts_year:
        for i in range(cnts_year[y]):
            pub_years.append(y)
    assert round(Impact_Funcs.calculate_year_based_emp_pub(pub_years), 2) == 6.63


def test_calculate_year_based_emp_pycites():
    # based on the data provided in the original publication, the reported values in the tables do not match what
    # they should be

    # worked out by hand
    citations = [81, 77, 61, 35, 34, 22, 20, 16, 4, 2, 1]
    pub_years = [2010, 2011, 2006, 2012, 2014, 2009, 2008, 2013, 2016, 2015, 2007]
    assert round(Impact_Funcs.calculate_year_based_emp_pycites(pub_years, citations), 2) == 9


def test_calculate_year_based_emp_cites():
    # based on the data provided in the original publication, the reported values in the tables do not match what
    # they should be

    # worked out by hand
    cumulative_citations = [27, 49, 70, 90, 110, 129, 146, 162, 173, 183, 190]
    assert round(Impact_Funcs.calculate_year_based_emp_cites(cumulative_citations), 3) == 5.477


def test_calculate_h_prime():
    rank_order, _ = Impact_Funcs.calculate_ranks(TEST_CITATION_DATA)
    h, is_core = Impact_Funcs.calculate_h_index(TEST_CITATION_DATA, rank_order)
    core_cites = Impact_Funcs.calculate_h_core(TEST_CITATION_DATA, is_core)
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    e = Impact_Funcs.calculate_e_index(core_cites, h)
    assert round(Impact_Funcs.calculate_h_prime(h, e, total_cites, core_cites), 3) == 15.969


def test_calculate_hc():
    # data and answers from original paper
    assert Impact_Funcs.calculate_hc(0, 0) == 0
    assert Impact_Funcs.calculate_hc(1, 1) == 1
    assert Impact_Funcs.calculate_hc(1, 2) == 2
    # the following one is calculated incorrectly in the original paper, they give the answer as 3, but it is clear
    # from Table 1 in the paper that the answer should actually be 2
    assert Impact_Funcs.calculate_hc(2, 2) == 2
    assert Impact_Funcs.calculate_hc(1, 3) == 2


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


def test_calculate_h_norm():
    assert Impact_Funcs.calculate_h_norm(TEST_CITATION_DATA, TEST_AUTHOR_CNT) == 4


def test_calculate_k_norm_index():
    assert round(Impact_Funcs.calculate_k_norm_index(TEST_CITATION_DATA, TEST_AUTHOR_CNT), 4) == 4.6049


def test_calculate_w_norm_index():
    assert round(Impact_Funcs.calculate_w_norm_index(TEST_CITATION_DATA, TEST_AUTHOR_CNT), 4) == 4.7060


def test_calculate_yearly_h_index():
    assert Impact_Funcs.calculate_yearly_h_index(TEST_CITATION_DATA, TEST_YEAR_DATA) == 1.8


def test_calculate_t_index_singh():
    yh = Impact_Funcs.calculate_yearly_h_index(TEST_CITATION_DATA, TEST_YEAR_DATA)
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    age = max(TEST_YEAR_DATA) - min(TEST_YEAR_DATA) + 1
    assert round(Impact_Funcs.calculate_t_index_singh(TEST_CITATION_DATA, yh, age, total_cites), 4) == 11.7336


def test_calculate_fairness():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_fairness(total_cites, total_pubs, TEST_CITATION_DATA), 4) == 0.3103


def test_calculate_zynergy():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    fairness = Impact_Funcs.calculate_fairness(total_cites, total_pubs, TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_zynergy(total_cites, total_pubs, fairness), 4) == 7.0003


def test_calculate_p20():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_p20(TEST_CITATION_DATA, total_cites, total_pubs), 4) == 0.6917


def test_rmp_calculate_rmp():
    mp = Impact_Funcs.calculate_rec_index(TEST_CITATION_DATA)
    assert round(Impact_Funcs.calculate_rmp(mp), 4) == 8.4853


def test_calculate_css():
    assert round(Impact_Funcs.calculate_css(TEST_CITATION_DATA), 4) == 15.2735


def test_calculate_csr():
    assert round(Impact_Funcs.calculate_csr(TEST_CITATION_DATA), 4) == 8.8237


def test_calculate_slg():
    assert round(Impact_Funcs.calculate_slg(TEST_CITATION_DATA), 4) == 10.3935


def test_calculate_3dsi_pr():
    total_cites = Impact_Funcs.calculate_total_cites(TEST_CITATION_DATA)
    total_pubs = Impact_Funcs.calculate_total_pubs(TEST_CITATION_DATA)
    csr = Impact_Funcs.calculate_csr(TEST_CITATION_DATA)
    v1, v2, v3 = Impact_Funcs.calculate_3dsi_pr(total_pubs, total_cites, csr)
    assert v1 == total_pubs
    assert v2 == total_cites
    assert round(v3, 4) == 0.6155


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
