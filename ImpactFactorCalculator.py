# Impact Factor Calculator
"""
This program is designed to calculate a large number of impact factors for
data collected over multiple years. It does not automatically retrieve citation
information but assumes it has already been collected in a format as described
below.
"""

import datetime
import math

tb = '\t'

# these aren't really proper classes, but rather just simple
# mutlivariate data objects

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

class MetricSet:
    def __init__(self):
        self.date = datetime.date(1970,1,1)
        self.totalPubs = 0
        self.totalCites = 0
        self.citesPerPub = 0
        self.maxCites = 0
        self.cumulativeCites = []
        self.h_index = 0
        self.Hirsch_minConst = 0
        self.Hirsch_mQuotient = 0
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
        

def StringToDate(s):
    m,d,y = s.split('/')
    return datetime.date(int(y),int(m),int(d))

def DateToString(d):
    return str(d.month)+'/'+str(d.day)+'/'+str(d.year)

def DateToInt(d):
    return datetime.date.toordinal(d)


def readDataFile(inName):
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
    inFile = open(inName,"r")
    a = -1
    articleList = []
    for line in inFile:
        line = line.strip()
        a += 1
        # header
        if a == 0:
            # skip 1st 4 columns
            for i in range(4):
                line = line[line.find(tb)+1:]
            tmpList = line.split(tb)
            dateList = []
            for d in tmpList:
                dateList.append(StringToDate(d))
        # read data
        elif line != '':
            newArticle = Article()
            articleList.append(newArticle)
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            newArticle.year = int(tstr)
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            newArticle.authors = int(tstr)
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]

            newArticle.authorrank = int(tstr)
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]

            newArticle.title = tstr
            citList = line.split(tb)
            for n in citList:
                if n == 'n/a':
                    n = -1
                newArticle.citations.append(int(n))
    inFile.close()
    return dateList, articleList


def readSelfCitationFiles(articleList,sName,cName):
    """
    function to read self-citation information. This function uses two input
    files, one containing self-citation counts by the target author and one
    containing self-citation counts by co-authors of the target author on
    papers for which the target author was not an author. The format of these
    files is identical to the main citation data, above, except only listing
    the self-citation counts
    """
    # self cites
    sFile = open(sName,"r")
    a = -1
    for line in sFile:
        line = line.strip()
        a = a + 1
        # skip header
        if (a != 0) and (line != ''):
            article = articleList[a-1]
            # skip year
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            # skip authors
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            # skip author rank
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            # skip title
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            citList = line.split(tb)
            for n in citList:
                if n == 'n/a':
                    n = -1
                article.selfcites.append(int(n))
    sFile.close()

    # co-author cites
    cFile = open(cName,"r")
    a = -1
    for line in cFile:
        line = line.strip()
        a = a + 1
        # skip header
        if (a != 0) and (line != ''):
            article = articleList[a-1]
            # skip year
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            # skip authors
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            # skip author rank
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            # skip title
            tstr = line[:line.find(tb)]
            line = line[line.find(tb)+1:]
            citList = line.split(tb)
            for n in citList:
                if n == 'n/a':
                    n = -1
                article.coauthcites.append(int(n))
    cFile.close()


def rank(n,indx):
    irank = []
    for j in range(n):
        irank.append(0)
    for j in range(n):
        irank[indx[j]] = j
    return irank


def sortandrank(sortlist,n):
    tmpindex = sorted(range(n), key = lambda k: sortlist[k])        
    tmprank = rank(n,tmpindex)
    # reverse so #1 is largest
    # NOTE: the ranks in rankorder go from 1 to n, rather than 0 to n-1
    rankorder = []
    for i in range(n):
        rankorder.append(n - tmprank[i])
    return tmpindex, rankorder

#-----------------------------------------------------
# Metric Calculation Functions
#-----------------------------------------------------

# g-index (Egghe 2006)
def calculate_g_index(n,rankorder,cumulativeCites):
    g_index = 0
    for i in range(n):
        if rankorder[i]**2 <= cumulativeCites[rankorder[i]-1]:
            g_index += 1
    return g_index


# h2-index (Kosmulski 2006)
def calculate_h2_index(n,rankorder,Cites):
    h2_index = 0
    for i in range(n):
        if rankorder[i] <= math.sqrt(Cites[i]):
            h2_index += 1
    return h2_index


# hg-index (Alonso et al 2010)
def calculate_hg_index(h,g):
    return math.sqrt(h*g)


# sharpened h-index (Schreiber 2007)
# also returns total and avg self-citations
def calculate_sharpened_h_index(n,y,curList,Cites,incAll):
    selfCites = []
    avg_self_cites = 0
    total_self_cites = 0
    for i in range(n):
        article = curList[i]
        s = article.selfcites[y]
        if incAll:
            s += article.coauthcites[y]
        selfCites.append(Cites[i] - s)
        total_self_cites += s
        if Cites[i] != 0:
            avg_self_cites += s / Cites[i]
    avg_self_cites = avg_self_cites / n
    tmpindex, tmprank = sortandrank(selfCites,n)
    sharpself_h_index = 0
    for i in range(n):
        if tmprank[i] <= selfCites[i]:
            sharpself_h_index += 1
    return avg_self_cites, total_self_cites, sharpself_h_index


# b-index (Brown 2009)
def calculate_b_index(h,avgrate):
    return h * avgrate **0.75


# real h-index (hr-index) (Guns and Rousseau 2009)
def calculate_real_h_index(n,rankorder,h,Cites):
    j = -1
    k = -1
    for i in range(n):
        if rankorder[i] == h:
            j = i
        elif rankorder[i] == h + 1:
            k = i
    if (k != -1) and (j != -1):
        return ((h + 1) * Cites[j] - h * Cites[k]) / (1 - Cites[k] + Cites[j])
    else:
        return h

# a-index (Jin 2006; Rousseau 2006)
def calculate_a_index(coreCites,totalPubs):
    return coreCites/totalPubs


# r-index (Jin et al 2007)
def calculate_r_index(coreCites):
    return math.sqrt(coreCites)


# rm-index (Panaretos and Malesios 2009)
def calculate_rm_index(n,IsCore,Cites):
    rm_index = 0
    for i in range(n):
        if IsCore[i]:
            rm_index += math.sqrt(Cites[i])
    rm_index = math.sqrt(rm_index)
    return rm_index


# ar-index (Jin 2007; Jin et al 2007)
def calculate_ar_index(n,IsCore,CitesPerYear):
    ar_index = 0
    for i in range(n):
        if IsCore[i]:
            ar_index += CitesPerYear[i]
    ar_index = math.sqrt(ar_index)
    return ar_index


# m-index (median index) (Bornmann et al 2008)
def calculate_m_index(n,IsCore,h,Cites):
    CoreCites = []
    for i in range(n):
        if IsCore[i]:
            CoreCites.append(Cites[i])
    CoreCites.sort()
    if h % 2 == 1:
        # odd number in core
        m_index = CoreCites[(h // 2)]
    else:
        # even number in core
        m_index = (CoreCites[(h // 2) - 1] + CoreCites[h // 2]) / 2
    return m_index


# q2-index (Cabrerizo et al 2010)
def calculate_q2_index(h,m):
    return math.sqrt(h * m)


# k-index (Ye and Rousseau 2010)
def calculate_k_index(totalCites,coreCites,totalPubs):
    return (totalCites * coreCites) / (totalPubs * (totalCites - coreCites))


# Franceschini f-index (Franceschini and Maisano 2010)
def calculate_Franceschini_f_index(maxy,miny):
    return maxy - miny + 1


# weighted h-index (Egghe and Rousseau 2008)
def calculate_weighted_h_index(n,Cites,cumulativeCites,rankorder,h):
    weighted_h_index = 0
    for i in range(n):
        if Cites[i] >= cumulativeCites[rankorder[i]-1] / h:
            weighted_h_index += Cites[i]
    return math.sqrt(weighted_h_index)


# normalized h-index (Sidiropoulos et al 2007)
def calculate_normalized_h(h,totalPubs):
    return h / totalPubs


# v-index (Riikonen and Vihinen 2008)
def calculate_v_index(h,totalPubs):
    return 100 * h / totalPubs


# e-index (Zhang 2009)
def caculate_e_index(coreCites,h):
    return math.sqrt(coreCites - h**2)


# rational h-index (Ruane and Tol 2008)
def calculate_rational_h(n,IsCore,Cites,h,rankorder):
    j = 0
    for i in range(n):
        if IsCore[i]:
            if Cites[i] == h:
                j += 1
        else:
            if rankorder[i] == h + 1:
                j = j + (h + 1 - Cites[i])
    return h + 1 - j / (2 * h + 1)


# h2-lower, center and upper (Bornmann et al 2010)
def calculate_h2percs(coreCites,h,totalCites):
    h2_upper = 100 * (coreCites - h**2) / totalCites
    h2_center = 100 * h**2 / totalCites
    h2_lower = 100 * (totalCites - coreCites) / totalCites
    return h2_upper, h2_center, h2_lower


# tapered h-index (Anderson et al 2008)
def calculate_tapered_h_index(n,Cites,rankorder):
    ht = []
    for i in range(n):
        ht.append(0)
        if Cites[i] <= rankorder[i]:
            ht[i] = Cites[i]/(2 * rankorder[i] - 1)
        else:
            ht[i] = rankorder[i] / (2 * rankorder[i] - 1)
            for j in range(rankorder[i]+1,n+1):
                ht[i] = ht[i] + 1 / (2 * j - 1)
    tapered_h_index = 0
    for i in range(n):
        tapered_h_index += ht[i]
    return tapered_h_index


# pi-index (Vinkler 2009)
def calculate_pi_index(n,totalPubs,rankorder,Cites):
    j = math.floor(math.sqrt(totalPubs))
    pi_index = 0
    for i in range(n):
        if rankorder[i] <= j:
            pi_index += Cites[i]
    return pi_index / 100


# p-index (originally called mock hm-index), ph-ratio, and pf-index (Prathap 2010b, 2011)
def calculate_Prathap_p_index(totalCites,totalPubs,h,curList,y):
    p_index = (totalCites**2 / totalPubs)**(1/3)
    ph_ratio = p_index / h
    pf = 0
    nf = 0
    for article in curList:
        pf = pf + 1 / article.authors
        nf = nf + article.citations[y] / article.authors
    fractional_p_index = (nf**2 / pf)**(1/3)
    return p_index,ph_ratio,fractional_p_index


# harmonic p-index (Prathap 2011)
def calculate_Prathap_harmonic_p(curList,y):
    ph = 0
    nh = 0
    for article in curList:
        num = 1 / article.authorrank
        denom = 0
        for i in range(article.authors):
            denom += 1 / (i + 1)
        r = num / denom        
        ph += r
        nh += article.citations[y] * r
    return (nh**2 / ph)**(1/3)


# hi-index (Batista et al 2006) and pure h-index (Wan et al 2007)
def calculate_hi_pure(n,IsCore,curList,h):
    suma = 0
    for i in range(n):
        if IsCore[i]:
            suma += curList[i].authors
    return h**2 / suma , h / math.sqrt(suma / h)


# pure h-index with author order (Wan et al 2007)
def calculate_pure_order(n,IsCore,curList,h):
    sump = 0 # proportional counting
    sumg = 0 # geometric counting
    for i in range(n):
        if IsCore[i]:
            sump += curList[i].authors * (curList[i].authors + 1) / (2 * curList[i].authors + 1 - curList[i].authorrank)
            sumg += (2**curList[i].authors - 1) / (2**(curList[i].authors - curList[i].authorrank))
    pure_prop = h / math.sqrt(sump / h)
    pure_geom = h / math.sqrt(sumg / h)
    return pure_prop, pure_geom


# Tol's f-index and t-index
def calculate_Tol_indices(n,rankorder,fcum,tcum):
    Tol_f_index = 0
    for i in range(n):
        if rankorder[i] / fcum[rankorder[i]-1] >= rankorder[i]:
            if rankorder[i] > Tol_f_index:
                Tol_f_index = rankorder[i]
    Tol_t_index = 0
    for i in range(n):
        if math.exp(tcum[rankorder[i]-1]/rankorder[i]) >= rankorder[i]:
            if rankorder[i] > Tol_t_index:
                Tol_t_index = rankorder[i]
    return Tol_f_index,Tol_t_index


# mu-index (Glanzel and Schubert 2010)
def calculate_mu_index(n,rankorder,medarray):
    mu_index = 0
    for i in range(n):
        if medarray[rankorder[i]-1] >= rankorder[i]:
            if rankorder[i] > mu_index:
                mu_index = rankorder[i]
    return mu_index


# Wu w-index (Wu 2010)
def calculate_Wu_w(n,Cites,rankorder):
    Wu_w_index = 0
    for i in range(n):
        if Cites[i] >= 10 * rankorder[i]:
            Wu_w_index += 1
    j = 0
    for i in range(n):
        if Cites[i] >= 10 * rankorder[i]:
            if Cites[i] < 10 * (Wu_w_index + 1):
                j = j + (10 * (Wu_w_index + 1) - Cites[i])
        else:
             if rankorder[i] == Wu_w_index + 1:
                j = j + 10 * (Wu_w_index + 1) - Cites[i]
    return Wu_w_index, j


# Wohlin w-index (Wohlin 2009)
def calculate_Wohlin_w(n,maxCites,Cites):
    j = 5
    nc = 1
    while maxCites > j:
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
            if Cites[j] >= wval[i]:
                wclass[i] += 1
    Wohlin_w_index = 0
    for i in range(nc):
        Wohlin_w_index += math.log(wval[i]) * wclass[i]
    return Wohlin_w_index


# contemporary h-index (Sidiropoulos et al 2007)
def calcualate_contemporary_h(n,Cites,CurAge):
    Sc = []
    for i in range(n):
        Sc.append(4 * Cites[i] / (1 + CurAge[i]))
    tmpindex, tmporder = sortandrank(Sc,n)
    contemp_h_index = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            contemp_h_index += 1
    return contemp_h_index


# hpd seniority index (Kosmulski 2009)
def calculate_hpd_seniority(n,CitesPerYear):
    Sc = []
    for i in range(n):
        Sc.append(10 * CitesPerYear[i])
    tmpindex, tmporder = sortandrank(Sc,n)
    hpd_index = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            hpd_index += 1
    return hpd_index


# specific impact s-index (De Visscher 2010)
def calculate_impact_s_index(n,CurAge,totalCites):
    specificImpact_s_index = 0
    for i in range(n):
        specificImpact_s_index += 1 - math.exp(-0.1*CurAge[i])
    if specificImpact_s_index != 0:
        specificImpact_s_index = totalCites / (10 * specificImpact_s_index)
    return specificImpact_s_index



# hm-index/hF-index and gF-index (fractional paper) (Schreiber 2008; Egghe 2008)
def calculate_fractional_paper_indices(n,rankorder,Cites,CumRank,cumulativeCites):
    hF_hm_index = 0
    gF_paper = 0
    for i in range(n):
        if CumRank[rankorder[i]-1] <= Cites[i]:
            if CumRank[rankorder[i]-1] > hF_hm_index:
                hF_hm_index = CumRank[rankorder[i]-1]
        if CumRank[rankorder[i]-1]**2 <= cumulativeCites[i]:
            if CumRank[rankorder[i]-1] > gF_paper:
                gF_paper = CumRank[rankorder[i]-1]
    return hF_hm_index, gF_paper


# multidimensional h-index (Garcia-Perez 2009)
def calculate_multidimensional_h(h,n,IsCore,rankorder,Cites):
    multiDim_h_index = []
    multiDim_h_index.append(h)
    multiUsed = []
    for i in range(n):
        if IsCore[i]:
            multiUsed.append(True)
        else:
            multiUsed.append(False)
    j = 0
    tmph = -1
    while tmph != 0:
        nc = len(multiDim_h_index)
        j = j + multiDim_h_index[nc-1]
        tmph = 0
        for i in range(n):
            if not multiUsed[i]:
                if rankorder[i] - j <= Cites[i]:
                    multiUsed[i] = True
                    tmph += 1              
        if tmph > 0:
            multiDim_h_index.append(tmph)
    return multiDim_h_index


# normalized hi-index/hf-index and gf-index (Wohlin 2009; Egghe 2008)
def calculate_hinorm(n,Cites,curList):
    Sc = []
    for i in range(n):
        Sc.append(Cites[i] / curList[i].authors)
    tmpindex, tmporder = sortandrank(Sc,n)
    acum = []
    acum.append(Sc[tmpindex[n-1]])
    for i in range(1,n):
        acum.append(acum[i-1] + Sc[tmpindex[n-i-1]])
    hf_norm_hi_index = 0
    gf_cite = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            hf_norm_hi_index += 1
        if tmporder[i]**2 <= acum[tmporder[i]-1]:
            gf_cite += 1
    return hf_norm_hi_index, gf_cite


# Woeginger w-index (Woeginger 2008)
def calculate_Woeginger_w(n,rankorder,Cites):
    Woeginger_w_index = 0
    for j in range(n):
        tmpGood = True
        for i in range(n):
            if rankorder[i] <= j:
                if Cites[i] < j - rankorder[i] + 1:
                    tmpGood = False
        if tmpGood:
            Woeginger_w_index = j
    return Woeginger_w_index


# maxprod (Kosmulski 2007)
def calculate_maxprod(n,Cites,rankorder):
    maxprod_index = 0
    for i in range(n):
        if Cites[i] * rankorder[i] > maxprod_index:
            maxprod_index = Cites[i] * rankorder[i]
    return maxprod_index


# j-index (Todeschini 2011)
def calculate_j_index(n,Cites,h):
    # constants for j-index
    ndhk = 12
    dhk = [500,250,100,50,25,10,5,4,3,2,1.5,1.25]

    sumw = 0
    sumwdhk = 0
    for j in range(ndhk):
        sumw = sumw + 1 / (j + 1)
        c = 0
        for i in range(n):
            if Cites[i] >= h * dhk[j]:
                c += 1
        sumwdhk = sumwdhk + c / (j + 1)
    return h + sumwdhk / sumw


# adapted pure h-index (Chai et al 2008)
def calculate_adapated_pure_h(n,Cites,curList):
    Sc = []
    for i in range(n):
        Sc.append(Cites[i] / math.sqrt(curList[i].authors))
    tmpindex, tmporder = sortandrank(Sc,n)
    j = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            j += 1
    citeE = 0
    citeE1 = 0
    for i in range(n):
        if tmporder[i] == j:
            citeE = Sc[i]
        elif tmporder[i] == j + 1:
            citeE1 = Sc[i]
    return (((j + 1) * citeE) - (j * citeE1)) / (citeE - citeE1 + 1)


# adapted pure h-index w/proportional author credit (Chai et al 2008)
def calculate_adapated_pure_h_prop(n,Cites,curList):
    Sc = []
    for i in range(n):
        EA = curList[i].authors * (curList[i].authors + 1) / (2 * (curList[i].authors + 1 - curList[i].authorrank))
        Sc.append(Cites[i] / math.sqrt(EA))
    tmpindex, tmporder = sortandrank(Sc,n)
    j = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            j += 1
    citeE = 0
    citeE1 = 0
    for i in range(n):
        if tmporder[i] == j:
            citeE = Sc[i]
        elif tmporder[i] == j + 1:
            citeE1 = Sc[i]
    return (((j + 1) * citeE) - (j * citeE1)) / (citeE - citeE1 + 1)


# adapted pure h-index w/geometric author credit (Chai et al 2008)
def calculate_adapated_pure_h_geom(n,Cites,curList):
    Sc = []
    for i in range(n):
        EA  = (2**curList[i].authors - 1) / (2**(curList[i].authors - curList[i].authorrank))
        Sc.append(Cites[i] / math.sqrt(EA))
    tmpindex, tmporder = sortandrank(Sc,n)
    j = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            j += 1
    citeE = 0
    citeE1 = 0
    for i in range(n):
        if tmporder[i] == j:
            citeE = Sc[i]
        elif tmporder[i] == j + 1:
            citeE1 = Sc[i]
    return (((j + 1) * citeE) - (j * citeE1)) / (citeE - citeE1 + 1)


# profit p-index and related values (Aziz and Rozing 2013)
def calculate_profit_indices(n,curList,Cites,h):
    monEquiv = []
    for article in curList:
        if article.authors % 2 == 0:
            meD = 0
        else:
            meD = 1 / (2 * article.authors)
        monEquiv.append((1 + abs(article.authors + 1 - 2 * article.authorrank)) / ((article.authors ** 2) / 2 + article.authors * (1 - meD)))
    monographEquiv = 0
    for i in range(n):
        monographEquiv += monEquiv[i]
    profit_index = 1 - monographEquiv / n
    Sc = []
    for i in range(n):
        Sc.append(Cites[i] * monEquiv[i])
    tmpindex, tmporder = sortandrank(Sc,n)
    profit_adj_h_index = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            profit_adj_h_index += 1
    profit_h_index = 1 - profit_adj_h_index / h
    return profit_index, profit_adj_h_index, profit_h_index


# hj-indices (Dorta-Gonzalez and Dorta-Gonzalez 2010)
def calculate_hj_indices(totalPubs,h,RCites):
    if totalPubs < 2 * h - 1:
        j = totalPubs - h
    else:
        j = h - 1
    hj_index = []
    hj_index.append(h**2)
    for i in range(1,j+1):
        hj_index.append(hj_index[i-1] +
           (h - i) * (RCites[h - i - 1] - RCites[h - i])
           + RCites[h + i - 1])
    return hj_index


# trend h-index
def calculate_trend_h(n,curList,y,dateList):
    Sc = []
    for i in range(n):
        Sc.append(0)
        article = curList[i]
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
            Sc[i] = Sc[i] + cy * (1 / (dateList[y].year - dateList[yy].year + 1))                
        Sc[i] = 4 * Sc[i]

    tmpindex, tmporder = sortandrank(Sc,n)
    trend_h_index = 0
    for i in range(n):
        if tmporder[i] <= Sc[i]:
            trend_h_index += 1
    return trend_h_index
 

#-----------------------------------------------------
# Main Calculation Loop
#-----------------------------------------------------

def CalculateMetrics(y,dateList,articleList):
    """
    function to calculate impact factor metrics for data for a given date 
    """

    # determine active articles and raw data summaries
    curList = []
    Metrics = MetricSet()
    Metrics.date = dateList[y]
    Metrics.totalPubs = 0
    Metrics.totalCites = 0
    Metrics.maxCites = 0
    firstyear = articleList[0].year
    for article in articleList:
        if article.year < firstyear:
            firstyear = article.year
        if article.citations[y] != -1:
            curList.append(article)
            Metrics.totalPubs = Metrics.totalPubs + 1
            Metrics.totalCites = Metrics.totalCites + article.citations[y]
            if Metrics.maxCites < article.citations[y]:
                Metrics.maxCites = article.citations[y]
    Metrics.citesPerPub = Metrics.totalCites / Metrics.totalPubs

    # construct sublists for active articles only
    n = len(curList) 
    Cites = []
    RCites= []
    Metrics.cumulativeCites = []
    fcum = []
    tcum = []
    CumRank = []
    medarray = []
    CurAge = []
    CitesPerYear = []
    IsCore = []
    for i in range(n):
        Cites.append(0)
        CurAge.append(0)
        CitesPerYear.append(0)
        Metrics.cumulativeCites.append(0)
        CumRank.append(0)
        fcum.append(0)
        tcum.append(0)
        medarray.append(0)
        IsCore.append(False)
        RCites.append(0)
    minfyear = 0
    maxfyear = 0
    i = -1
    for article in curList:
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
        Cites[i] = article.citations[y]
        CurAge[i] = dateList[y].year - article.year
        if CurAge[i] < 0:
            CurAge[i] = 0
        if CurAge[i] == 0:
            CitesPerYear[i] = Cites[i]
        else:
            CitesPerYear[i] = Cites[i] / CurAge[i]
            
    # sort the articles by number of citations
    tmpindex, rankorder = sortandrank(Cites,n)

    for i in range(n):
        article = curList[tmpindex[n-i-1]]
        if i > 0:
            Metrics.cumulativeCites[i] = Metrics.cumulativeCites[i-1] + Cites[tmpindex[n-i-1]]
        else: 
            Metrics.cumulativeCites[i] = Cites[tmpindex[n-i-1]]
        RCites[i] = Cites[tmpindex[n-i-1]]
        CumRank[i] = CumRank[i-1] + 1 / article.authors       
        # for Tol's f and t-indices
        if Cites[tmpindex[n-i-1]] > 0:
            fcum[i] = fcum[i-1] + 1 / Cites[tmpindex[n-i-1]]
            tcum[i] = tcum[i-1] + math.log(Cites[tmpindex[n-i-1]])
        else:
            fcum[i] = fcum[i-1]
            tcum[i] = tcum[i-1]
        # for mu-index
        j = (i + 1) // 2
        if (i + 1) % 2 == 0:      
            medarray[i] = (Cites[tmpindex[n-j-1]] + Cites[tmpindex[n-j]]) / 2
        else:
            medarray[i] = Cites[tmpindex[n-j-1]]

    #attach ranks to articles
    if y == len(dateList) - 1:
        j = -1
        for article in articleList:
            if article.citations[y] == -1:
                article.rank = -1
            else:
                j = j + 1
                article.rank = rankorder[j]

    # basic indices
    Metrics.h_index = 0
    Metrics.coreCites = 0
    for i in range(n):
        if rankorder[i] <= Cites[i]:
            IsCore[i] = True
            Metrics.h_index += 1
            Metrics.coreCites = Metrics.coreCites + Cites[i]
    Metrics.Hirsch_minConst = Metrics.totalCites / Metrics.h_index**2
    if dateList[y].year - firstyear != 0:
        Metrics.Hirsch_mQuotient = Metrics.h_index / (dateList[y].year - firstyear)
    else:
        Metrics.Hirsch_mQuotient = -1

    # other indices
    Metrics.g_index = calculate_g_index(n,rankorder,Metrics.cumulativeCites)
    Metrics.h2_index = calculate_h2_index(n,rankorder,Cites)    
    Metrics.hg_index = calculate_hg_index(Metrics.h_index,Metrics.g_index)
    Metrics.avg_self_only_cites, Metrics.total_self_only_cites, Metrics.sharpself_h_index = calculate_sharpened_h_index(n,y,curList,Cites,False)
    Metrics.bavg_self_index = calculate_b_index(Metrics.h_index,1-Metrics.avg_self_only_cites)
    Metrics.avg_self_all_cites, Metrics.total_self_all_cites, Metrics.sharpall_h_index = calculate_sharpened_h_index(n,y,curList,Cites,True)
    Metrics.bavg_all_index = calculate_b_index(Metrics.h_index,1-Metrics.avg_self_all_cites)
    Metrics.b10_index = calculate_b_index(Metrics.h_index,0.9)
    Metrics.a_index = calculate_a_index(Metrics.coreCites,Metrics.totalPubs)
    Metrics.real_h_index = calculate_real_h_index(n,rankorder,Metrics.h_index,Cites)
    Metrics.r_index = calculate_r_index(Metrics.coreCites)
    Metrics.rm_index = calculate_rm_index(n,IsCore,Cites)
    Metrics.ar_index = calculate_ar_index(n,IsCore,CitesPerYear)
    Metrics.m_index = calculate_m_index(n,IsCore,Metrics.h_index,Cites)
    Metrics.q2_index = calculate_q2_index(Metrics.h_index,Metrics.m_index)
    Metrics.k_index = calculate_k_index(Metrics.totalCites,Metrics.coreCites,Metrics.totalPubs)
    Metrics.Franceschini_f_index = calculate_Franceschini_f_index(maxfyear,minfyear)
    Metrics.weighted_h_index = calculate_weighted_h_index(n,Cites,Metrics.cumulativeCites,rankorder,Metrics.h_index)
    Metrics.normalized_h_index = calculate_normalized_h(Metrics.h_index,Metrics.totalPubs)
    Metrics.v_index = calculate_v_index(Metrics.h_index,Metrics.totalPubs)
    Metrics.e_index = caculate_e_index(Metrics.coreCites,Metrics.h_index)
    Metrics.rational_h_index = calculate_rational_h(n,IsCore,Cites,Metrics.h_index,rankorder)
    Metrics.h2_upper,Metrics.h2_center,Metrics.h2_lower = calculate_h2percs(Metrics.coreCites,Metrics.h_index,Metrics.totalCites)
    Metrics.tapered_h_index = calculate_tapered_h_index(n,Cites,rankorder)
    Metrics.pi_index = calculate_pi_index(n,Metrics.totalPubs,rankorder,Cites)
    Metrics.p_index,Metrics.ph_ratio,Metrics.fractional_p_index = calculate_Prathap_p_index(Metrics.totalCites,Metrics.totalPubs,Metrics.h_index,curList,y)
    Metrics.harmonic_p_index = calculate_Prathap_harmonic_p(curList,y)
    Metrics.hi_index,Metrics.pure_h_index = calculate_hi_pure(n,IsCore,curList,Metrics.h_index)
    Metrics.pure_h_proportional, Metrics.pure_h_geometric = calculate_pure_order(n,IsCore,curList,Metrics.h_index)
    Metrics.Tol_f_index, Metrics.Tol_t_index = calculate_Tol_indices(n,rankorder,fcum,tcum)
    Metrics.mu_index = calculate_mu_index(n,rankorder,medarray)
    Metrics.Wu_w_index, Metrics.Wu_wq_index = calculate_Wu_w(n,Cites,rankorder)
    Metrics.Wohlin_w_index = calculate_Wohlin_w(n,Metrics.maxCites,Cites)
    Metrics.contemp_h_index = calcualate_contemporary_h(n,Cites,CurAge)
    Metrics.hpd_index = calculate_hpd_seniority(n,CitesPerYear)
    Metrics.specificImpact_s_index = calculate_impact_s_index(n,CurAge,Metrics.totalCites)
    Metrics.hF_hm_index, Metrics.gF_paper = calculate_fractional_paper_indices(n,rankorder,Cites,CumRank,Metrics.cumulativeCites)
    Metrics.multiDim_h_index = calculate_multidimensional_h(Metrics.h_index,n,IsCore,rankorder,Cites)
    Metrics.hf_norm_hi_index, Metrics.gf_cite =  calculate_hinorm(n,Cites,curList)
    Metrics.Woeginger_w_index = calculate_Woeginger_w(n,rankorder,Cites)
    Metrics.maxprod_index = calculate_maxprod(n,Cites,rankorder)
    Metrics.j_index = calculate_j_index(n,Cites,Metrics.h_index)
    Metrics.adapted_pure_h_index = calculate_adapated_pure_h(n,Cites,curList)
    Metrics.adapted_pure_h_proportional = calculate_adapated_pure_h_prop(n,Cites,curList)
    Metrics.adapted_pure_h_geometric = calculate_adapated_pure_h_geom(n,Cites,curList)
    Metrics.profit_index, Metrics.profit_adj_h_index, Metrics.profit_h_index = calculate_profit_indices(n,curList,Cites,Metrics.h_index)
    Metrics.hj_index = calculate_hj_indices(Metrics.totalPubs,Metrics.h_index,RCites)
    Metrics.trend_h_index = calculate_trend_h(n,curList,y,dateList)
   
    return Metrics


#-----------------------------------------------------
# Special metric calculations that require data from multiple time points
#-----------------------------------------------------

# dynamic h-type-index (Rousseau and Ye 2008)
def calculateDynamic_h(metricList):
    metric = metricList[0]
    metric.dynamic_h_index = -1
    for m in range(1,len(metricList)):
        avgh = 0
        avgd = 0
        for i in range(m+1):
            metric = metricList[i]
            avgh = avgh + metric.rational_h_index
            avgd = avgd + DateToInt(metric.date)
        avgh = avgh / (m + 1)
        avgd = avgd / (m + 1)
        sumxy = 0
        sumx2 = 0
        for i in range(m+1):
            metric = metricList[i]
            sumxy = sumxy + (metric.rational_h_index - avgh) * (DateToInt(metric.date) - avgd)
            sumx2 = sumx2 + (DateToInt(metric.date) - avgd)**2
        metric = metricList[m]
        metric.dynamic_h_index = 365 * metric.r_index * (sumxy / sumx2)


# impact vitality (Rons and Amez 2008, 2009)
def calculateImpactVitality(metricList):
    w = 5 # fix at a 5 year window
    for i in range(w-1):
        metric = metricList[i]
        metric.impactVitality = -1
    for m in range(w-1,len(metricList)):
        # calculate denominator of equation
        d = 0
        for i in range(w):
            d = d + 1/(i+1)
        d = d - 1

        # calculate numerator and denominator of numerator of equation
        nn = 0
        nd = 0
        for i in range(w):
            metric = metricList[m-i]
            tC = metric.totalCites
            if m - i != 0:
                metric = metricList[m-i-1]
                tC = tC - metric.totalCites
            nd = nd + tC
            nn = nn + tC / (i + 1)
            
        # calculate value
        metric = metricList[m]
        metric.impactVitality = (w * (nn / nd) - 1) / d


#-----------------------------------------------------
# output all results
#-----------------------------------------------------
def WriteOutput(fname,dateList,metricList):
    fstr = '1.4f' # constant formatting string
    outFile = open(fname,"w")
    # write header
    outFile.write('Date')
    for date in dateList:
        outFile.write(tb+DateToString(date))
    outFile.write('\n')

    # write metrics
    # Raw data metrics
    outFile.write('Total Articles')
    for metric in metricList:
        outFile.write(tb+str(metric.totalPubs))
    outFile.write('\n')

    outFile.write('Total Citations')
    for metric in metricList:
        outFile.write(tb+str(metric.totalCites))
    outFile.write('\n')

    outFile.write('Citations per Pub')
    for metric in metricList:
        outFile.write(tb+format(metric.citesPerPub,fstr))
    outFile.write('\n')

    outFile.write('Max Citations')
    for metric in metricList:
        outFile.write(tb+str(metric.maxCites))
    outFile.write('\n')

    # Core definitions
    outFile.write('h-index')
    for metric in metricList:
        outFile.write(tb+str(metric.h_index))
    outFile.write('\n')

    outFile.write('Hirsch-core citations')
    for metric in metricList:
        outFile.write(tb+str(metric.coreCites))
    outFile.write('\n')

    outFile.write('Hirsch Min Constant (a)')
    for metric in metricList:
        outFile.write(tb+format(metric.Hirsch_minConst,fstr))
    outFile.write('\n')

    outFile.write('g-index')
    for metric in metricList:
        outFile.write(tb+str(metric.g_index))
    outFile.write('\n')

    outFile.write('f-index (Tol)')
    for metric in metricList:
        outFile.write(tb+str(metric.Tol_f_index))
    outFile.write('\n')

    outFile.write('t-index (Tol)')
    for metric in metricList:
        outFile.write(tb+str(metric.Tol_t_index))
    outFile.write('\n')

    outFile.write('mu-index')
    for metric in metricList:
        outFile.write(tb+str(metric.mu_index))
    outFile.write('\n')

    outFile.write('w-index (Woeginger)')
    for metric in metricList:
        outFile.write(tb+str(metric.Woeginger_w_index))
    outFile.write('\n')

    outFile.write('h(2)-index')
    for metric in metricList:
        outFile.write(tb+str(metric.h2_index))
    outFile.write('\n')

    outFile.write('w-index (Wu)')
    for metric in metricList:
        outFile.write(tb+str(metric.Wu_w_index))
    outFile.write('\n')

    outFile.write('hg-index')
    for metric in metricList:
        outFile.write(tb+format(metric.hg_index,fstr))
    outFile.write('\n')

    # Full citation indices
    outFile.write('rational h-index')
    for metric in metricList:
        outFile.write(tb+format(metric.rational_h_index,fstr))
    outFile.write('\n')

    outFile.write('real h-index')
    for metric in metricList:
        outFile.write(tb+format(metric.real_h_index,fstr))
    outFile.write('\n')

    outFile.write('w(q) (Wu)')
    for metric in metricList:
        outFile.write(tb+str(metric.Wu_wq_index))
    outFile.write('\n')

    outFile.write('tapered h-index')
    for metric in metricList:
        outFile.write(tb+format(metric.tapered_h_index,fstr))
    outFile.write('\n')

    outFile.write('j-index')
    for metric in metricList:
        outFile.write(tb+format(metric.j_index,fstr))
    outFile.write('\n')

    outFile.write('w-index (Wohlin)')
    for metric in metricList:
        outFile.write(tb+format(metric.Wohlin_w_index,fstr))
    outFile.write('\n')

    outFile.write('hj-indices')
    for metric in metricList:
        outFile.write(tb+str(metric.hj_index))
    outFile.write('\n')

    # Core description indices
    outFile.write('v-index')
    for metric in metricList:
        outFile.write(tb+format(metric.v_index,fstr))
    outFile.write('\n')

    outFile.write('normalized h-index')
    for metric in metricList:
        outFile.write(tb+format(metric.normalized_h_index,fstr))
    outFile.write('\n')

    outFile.write('a-index')
    for metric in metricList:
        outFile.write(tb+format(metric.a_index,fstr))
    outFile.write('\n')

    outFile.write('m-index')
    for metric in metricList:
        outFile.write(tb+format(metric.m_index,fstr))
    outFile.write('\n')

    outFile.write('r-index')
    for metric in metricList:
        outFile.write(tb+format(metric.r_index,fstr))
    outFile.write('\n')

    outFile.write('rm-index')
    for metric in metricList:
        outFile.write(tb+format(metric.rm_index,fstr))
    outFile.write('\n')

    outFile.write('weighted h-index')
    for metric in metricList:
        outFile.write(tb+format(metric.weighted_h_index,fstr))
    outFile.write('\n')

    outFile.write('pi-index')
    for metric in metricList:
        outFile.write(tb+format(metric.pi_index,fstr))
    outFile.write('\n')

    outFile.write('q2-index')
    for metric in metricList:
        outFile.write(tb+format(metric.q2_index,fstr))
    outFile.write('\n')

    outFile.write('e-index')
    for metric in metricList:
        outFile.write(tb+format(metric.e_index,fstr))
    outFile.write('\n')

    outFile.write('maxprod-index')
    for metric in metricList:
        outFile.write(tb+str(metric.maxprod_index))
    outFile.write('\n')

    # Core vs. tail indices
    outFile.write('h2-upper index')
    for metric in metricList:
        outFile.write(tb+format(metric.h2_upper,fstr))
    outFile.write('\n')

    outFile.write('h2-center index')
    for metric in metricList:
        outFile.write(tb+format(metric.h2_center,fstr))
    outFile.write('\n')

    outFile.write('h2_tail index')
    for metric in metricList:
        outFile.write(tb+format(metric.h2_lower,fstr))
    outFile.write('\n')

    outFile.write('k-index')
    for metric in metricList:
        outFile.write(tb+format(metric.k_index,fstr))
    outFile.write('\n')

    outFile.write('p-index')
    for metric in metricList:
        outFile.write(tb+format(metric.p_index,fstr))
    outFile.write('\n')

    outFile.write('ph-ratio')
    for metric in metricList:
        outFile.write(tb+format(metric.ph_ratio,fstr))
    outFile.write('\n')

    outFile.write('multidimensional h-index')
    for metric in metricList:
        outFile.write(tb+str(metric.multiDim_h_index))
    outFile.write('\n')

    # Multiple-author indices
    outFile.write('hi-index')
    for metric in metricList:
        outFile.write(tb+format(metric.hi_index,fstr))
    outFile.write('\n')

    outFile.write('pure h-index (fractional credit)')
    for metric in metricList:
        outFile.write(tb+format(metric.pure_h_index,fstr))
    outFile.write('\n')

    outFile.write('pure h-index (proportional credit)')
    for metric in metricList:
        outFile.write(tb+format(metric.pure_h_proportional,fstr))
    outFile.write('\n')

    outFile.write('pure h-index (geometric credit)')
    for metric in metricList:
        outFile.write(tb+format(metric.pure_h_geometric,fstr))
    outFile.write('\n')

    outFile.write('adapted pure h-index (fractional credit)')
    for metric in metricList:
        outFile.write(tb+format(metric.adapted_pure_h_index,fstr))
    outFile.write('\n')

    outFile.write('adapted pure h-index (proportional credit)')
    for metric in metricList:
        outFile.write(tb+format(metric.adapted_pure_h_proportional,fstr))
    outFile.write('\n')

    outFile.write('adapted pure h-index (geometric credit)')
    for metric in metricList:
        outFile.write(tb+format(metric.adapted_pure_h_geometric,fstr))
    outFile.write('\n')

    outFile.write('hf-index/normalized hi-index')
    for metric in metricList:
        outFile.write(tb+str(metric.hf_norm_hi_index))
    outFile.write('\n')

    outFile.write('hF-index/hm-index')
    for metric in metricList:
        outFile.write(tb+format(metric.hF_hm_index,fstr))
    outFile.write('\n')

    outFile.write('gf-index')
    for metric in metricList:
        outFile.write(tb+str(metric.gf_cite))
    outFile.write('\n')

    outFile.write('gF-index')
    for metric in metricList:
        outFile.write(tb+format(metric.gF_paper,fstr))
    outFile.write('\n')

    outFile.write('fractional p-index')
    for metric in metricList:
        outFile.write(tb+format(metric.fractional_p_index,fstr))
    outFile.write('\n')

    outFile.write('harmonic p-index')
    for metric in metricList:
        outFile.write(tb+format(metric.harmonic_p_index,fstr))
    outFile.write('\n')

    outFile.write('profit p-index')
    for metric in metricList:
        outFile.write(tb+format(metric.profit_index,fstr))
    outFile.write('\n')

    outFile.write('profit adjusted h-index')
    for metric in metricList:
        outFile.write(tb+str(metric.profit_adj_h_index))
    outFile.write('\n')

    outFile.write('profit h-index')
    for metric in metricList:
        outFile.write(tb+format(metric.profit_h_index,fstr))
    outFile.write('\n')


    # Self-citation indices
    outFile.write('total self citations')
    for metric in metricList:
        outFile.write(tb+str(metric.total_self_only_cites))
    outFile.write('\n')

    outFile.write('total self citation rate')
    for metric in metricList:
        outFile.write(tb+format(metric.total_self_only_cites/metric.totalCites,fstr))
    outFile.write('\n')

    outFile.write('average self citation rate')
    for metric in metricList:
        outFile.write(tb+format(metric.avg_self_only_cites,fstr))
    outFile.write('\n')

    outFile.write('sharpened h-index (self citations only)')
    for metric in metricList:
        outFile.write(tb+str(metric.sharpself_h_index))
    outFile.write('\n')

    outFile.write('b-index (avg self citation rate)')
    for metric in metricList:
        outFile.write(tb+format(metric.bavg_self_index,fstr))
    outFile.write('\n')

    outFile.write('total self & coauthor citations')
    for metric in metricList:
        outFile.write(tb+str(metric.total_self_all_cites))
    outFile.write('\n')

    outFile.write('total self & coauthor citation rate')
    for metric in metricList:
        outFile.write(tb+format(metric.total_self_all_cites/metric.totalCites,fstr))
    outFile.write('\n')

    outFile.write('average self & coauthor citation rate')
    for metric in metricList:
        outFile.write(tb+format(metric.avg_self_all_cites,fstr))
    outFile.write('\n')

    outFile.write('sharpened h-index (self & coauthor citations)')
    for metric in metricList:
        outFile.write(tb+str(metric.sharpall_h_index))
    outFile.write('\n')

    outFile.write('b-index (avg self & coauthor citation rate)')
    for metric in metricList:
        outFile.write(tb+format(metric.bavg_all_index,fstr))
    outFile.write('\n')

    outFile.write('b-index (10% self-citation rate)')
    for metric in metricList:
        outFile.write(tb+format(metric.b10_index,fstr))
    outFile.write('\n')

    # Time-based indices
    outFile.write('Hirsch m-quotient (slope)')
    for metric in metricList:
        if metric.Hirsch_mQuotient == -1:
            outFile.write(tb+'n/a')
        else:
            outFile.write(tb+format(metric.Hirsch_mQuotient,fstr))
    outFile.write('\n')

    outFile.write('ar-index')
    for metric in metricList:
        outFile.write(tb+format(metric.ar_index,fstr))
    outFile.write('\n')

    outFile.write('dynamic h-type-index')
    for metric in metricList:
        if metric.dynamic_h_index < 0:
            outFile.write(tb+'n/a')
        else:
            outFile.write(tb+format(metric.dynamic_h_index,fstr))
    outFile.write('\n')

    outFile.write('hpd-index')
    for metric in metricList:
        outFile.write(tb+str(metric.hpd_index))
    outFile.write('\n')

    outFile.write('contemporary h-index')
    for metric in metricList:
        outFile.write(tb+str(metric.contemp_h_index))
    outFile.write('\n')

    outFile.write('trend h-index')
    for metric in metricList:
        outFile.write(tb+str(metric.trend_h_index))
    outFile.write('\n')

    outFile.write('impact vitality')
    for metric in metricList:
        if metric.impactVitality < 0:
            outFile.write(tb+'n/a')
        else:
            outFile.write(tb+format(metric.impactVitality,fstr))
    outFile.write('\n')

    outFile.write('specific impact s-index')
    for metric in metricList:
        outFile.write(tb+format(metric.specificImpact_s_index,fstr))
    outFile.write('\n')

    outFile.write('f-index (Franceschini & Maisano)')
    for metric in metricList:
        outFile.write(tb+str(metric.Franceschini_f_index))
    outFile.write('\n')

    outFile.close()


#-----------------------------------------------------
# main loop
#-----------------------------------------------------
def main():
    # user input
    inName = input('Name of citation file (default: \"Citations.txt\"): ')
    if inName.strip() == '':
        inName = 'Citations.txt'
    outName = input('Name of output file (default: \"impactfactors.txt\"): ')
    if outName.strip() == '':
        outName = 'impactfactors.txt'
    selfStr = input('Include self-citation measures? (y/n) (default = y) ')
    if (selfStr.strip() == '') or (selfStr.strip() == 'y'):
        incSelf = True
        selfName = input('Name of self-citation file (default: \"Citations-Self.txt\"): ')
        if selfName.strip() == '':
            selfName = 'Citations-Self.txt'
        coauthName = input('Name of coauthor-citation file (default: \"Citations-Coauthor\"): ')
        if coauthName.strip() == '':
            coauthName = 'Citations-Coauthor.txt'
    else:
        incSelf = False

    # read data    
    dateList, articleList = readDataFile(inName)
    if incSelf:
        readSelfCitationFiles(articleList,selfName,coauthName)

    # calculate metrics for every year
    metricList = []
    for y in range(len(dateList)):
        metricList.append(CalculateMetrics(y,dateList,articleList))

    # calculate metrics which use cross-year data
    calculateDynamic_h(metricList)
    calculateImpactVitality(metricList)

    # output
    WriteOutput(outName,dateList,metricList)


main()
