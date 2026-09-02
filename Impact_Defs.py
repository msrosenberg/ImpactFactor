# metric definitions for impact factor calculator

import Impact_Funcs
import Impact_Graphs
import datetime
import math
from typing import Union

# --- Internal Constants ---
"""
the various specific list types has been deprecated for a more flexible approach
# INTLIST = 2         
# LISTLIST = 4
# FLOATLIST = 5
# MIXLIST = 6
"""
INT = 0
FLOAT = 1
FLOAT_NA = 3
LIST = 7
STR = 8

FSTR = "1.4f"  # constant formatting string

NBEQ = "&nbsp;=&nbsp;"  # an equals symbol with non-breaking spaces around it
NBPLUS = "&nbsp;+&nbsp;"  # a plus symbol with non-breaking spaces around it
NBMINUS = "&nbsp;&minus;&nbsp;"  # a minus symbol with non-breaking spaces around it

PROPERTY_TYPES = ("Metric Type",
                  "Metric Property",
                  "Considerations and Adjustments",
                  "Publication Focus",
                  "Citation Focus")

PROPERTY_DICT = {"Metric Type": ["Basic Statistic",
                                 "Core Metric",
                                 "Core Property",
                                 "Alternative Metric"],
                 "Metric Property": ["Compound Metric",
                                     "Multidimensional Metric"],
                 "Considerations and Adjustments": ["Time",
                                                    "Coauthorship",
                                                    "Self-Citation"],
                 "Publication Focus": ["All Publications",
                                       "Core Publications",
                                       "Tail Publications",
                                       "Uncited Publications"],
                 "Citation Focus": ["All Citations",
                                    "Core Citations",
                                    "Tail Citations"]
                 }


# --- General Class Definitions ---

class Metric:
    """
    This class represents a single metric, with all of its properties and values
    """
    def __init__(self):
        self.name = ""
        self.full_name = ""
        self.citation = ""
        self.symbol = ""
        self.__html_name = None
        self.__axis_name = None
        self.is_self = False
        self.is_coauthor = False
        self.metric_type = FLOAT
        self.description = ""
        self.synonyms = []
        self.references = []
        self.calculate = None
        self.draw_graph = None
        self.__value = None
        self.parent_set = None
        self.description_graphs = []
        self.example = None
        self.list_formats = []
        self.properties = {}
        for y in PROPERTY_TYPES:
            for x in PROPERTY_DICT[y]:
                self.properties[x] = False

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
    def axis_name(self):
        if self.__axis_name is None:
            return self.full_name
        else:
            return self.__axis_name

    @axis_name.setter
    def axis_name(self, value):
        self.__axis_name = value

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
        elif self.metric_type == FLOAT_NA:
            if self.value == "n/a":
                return self.value
            else:
                return format(self.value, FSTR)
        elif self.metric_type == STR:
            return self.value
        elif self.metric_type == LIST:
            value_list = self.value
            formatted_values = []
            if self.list_formats == INT:  # all values are integers
                formats = [INT for _ in value_list]          # PyCharm is wrong, this is reachable
            elif self.list_formats == FLOAT:  # all values are float
                formats = [FLOAT for _ in value_list]        # PyCharm is wrong, this is reachable
            else:  # mixed types
                formats = [x for x in self.list_formats]

            for i, v in enumerate(value_list):
                if formats[i] == INT:
                    formatted_values.append(str(v))
                elif formats[i] == FLOAT:
                    formatted_values.append(format(v, FSTR))
                else:
                    formatted_values.append(v)
            return f"[{", ".join(formatted_values)}]"
        return ""  # should never reach this


class MetricSet:
    """
    This class contains all metric output for a single year, as well as data used to calculate these metrics
    """
    def __init__(self):
        self.date = datetime.date(1970, 1, 1)
        self.citations = []  # number of citations for each pub, ordered by input
        self.rank_order = []  # rank of each pub, from most citations to fewest
        self.cumulative_citations = []  # cumulative number of citations per top i pubs, in order by rank
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
        self.rank_order, self.cumulative_citations = Impact_Funcs.calculate_ranks(self.citations)

    def academic_age(self) -> int:
        """
        number of years since author began publishing
        """
        if self.first_pub_year is None:
            return 0
        else:
            return self.date.year - self.first_pub_year + 1

    # def sorted_citations(self) -> list:
    #     """
    #     returns the citation counts sorted from highest to lowest (rather than by pub order)
    #     """
    #     return sorted(self.citations, reverse=True)

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

    def coauthors(self) -> list:
        """
        returns a list containing the coauthor string for each publication, in the same order as citations
        """
        return [p.coauthors for p in self.publications]

    def primary_authorship(self) -> list:
        """
        returns a list containing the primary authorship for each publication, in the same order as citations
        """
        return [p.primary_author for p in self.publications]


    def year(self) -> int:
        return self.date.year

    def references(self) -> list:
        tmp_set = set()
        for m in self.metrics:
            tmp_set |= set(self.metrics[m].references)
        tmp_list = list(tmp_set)
        tmp_list.sort()
        return tmp_list


class DescriptionGraph:
    """
    This class will hold plotting information for speciality graphs used as part of the description of
    particular metrics, rather than just a recording of the metric values over time
    """
    def __init__(self):
        self.name = ""  # a label which will be used to identify specific plots
        self.data = None


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
    m.symbol = "<em>P</em>"
    m.axis_name = r"$\text{total publications } \left(P\right)$"
    m.metric_type = INT
    m.description = ('<p>This metric is simply the total number of publications by an author. Many works might be '
                     'considered a publication, including journal articles, books, book chapters, published '
                     'conference abstracts, software, reports, dissertations, and theses.</p>')
    m.synonyms = ["<em>P</em>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_pubs
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    return m


# total citations
def calculate_total_cites(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_total_cites(metric_set.citations)


def metric_total_cites() -> Metric:
    m = Metric()
    m.name = "total cites"
    m.full_name = "total citations"
    m.symbol = "<em>C<sup>P</sup></em>"
    m.axis_name = r"$\text{total citations } \left(C^P\right)$"
    m.metric_type = INT
    equation = r"$$C^P=\sum\limits_{i=1}^{P}{C_i}.$$"
    m.description = ('<p>This metric (sometimes called <span class="metric_name"><em>C<sub>T</sub></em></span>) is '
                     f'the total number of citations to all publications by an author, or</p>{equation}')
    m.synonyms = ["<em>C<sub>T</sub></em>",
                  "citation count",
                  "<em>C<sup>P</sup></em>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_cites
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# maximum citations
def calculate_max_cites(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_max_cites(metric_set.citations)


def metric_max_cites() -> Metric:
    m = Metric()
    m.name = "max cites"
    m.full_name = "maximum citations"
    m.metric_type = INT
    m.description = ('<p>This metric is the largest number of citations found for a single publication by an '
                     'author. When publications are in rank order by citations, <em>C</em><sub>max</sub> = '
                     '<em>C</em><sub>1</sub>.</p>')
    m.symbol = "<em>C</em><sub>max</sub>"
    m.synonyms = ["<em>C</em><sub>max</sub>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_max_cites
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    return m


# mean citations
def calculate_mean_cites(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_mean_cites(total_cites, total_pubs)


def metric_mean_cites() -> Metric:
    m = Metric()
    m.name = "c/p"
    m.full_name = "mean citations per publication"
    m.metric_type = FLOAT
    equation = r"$$C/P\text{ index}=\frac{C^P}{P}$$"
    m.description = ('<p>This metric is the mean number of citations per publication. It has been described under '
                     'many names, including the <span class="metric_name"><em>C/P</em> index</span>, the '
                     '<span class="metric_name">mean citation rate (<em>MCR</em>)</span>, the '
                     '<span class="metric_name">mean observed citation rate (<em>MOCR</em>)</span>, '
                     '<span class="metric_name">citations per publication (<em>CPP</em>)</span>, the '
                     '<span class="metric_name">observed citation rate (<em>OCR</em>)</span>, '
                     'the <span class="metric_name">generalized impact factor (<em>I<sub>f</sub></em>)</span>, and '
                     f'the <span class="metric_name">journal paper citedness (<em>JPC</em>)</span>.</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.synonyms = ["<em>C/P</em> index",
                  "mean citation rate",
                  "mean observed citation rate",
                  "citations per publication",
                  "observed citation rate",
                  "generalized impact factor",
                  "journal paper citedness",
                  "<em>MCR</em>",
                  "<em>MOCR</em>",
                  "<em>CPP</em>",
                  "<em>OCR</em>",
                  "<em>I<sub>f</sub></em>",
                  "<em>JPC</em>"]
    m.symbol = "<em>C/P</em>"
    m.calculate = calculate_mean_cites
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# median citations
def calculate_median_cites(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_median_cites(citations)


def metric_median_cites() -> Metric:
    m = Metric()
    m.name = "median cites per pub"
    m.full_name = "median citations per publication"
    m.metric_type = FLOAT
    m.symbol = r"\(\tilde{C}\)"
    m.description = ('<p>This metric is the median number of citations per publication. It may be a better '
                     'indicator of the average impact of an author\'s publications than the __c/p__ since it is less '
                     'prone to bias under a heavily skewed citation distribution.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_median_cites
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# pubs per year
def calculate_pubs_per_year(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_pubs_per_year(total_pubs, age)


def metric_pubs_per_year() -> Metric:
    m = Metric()
    m.name = "pubs per year"
    m.full_name = "publications per year"
    m.symbol = "<em>P<sup>TS</sup></em>"
    m.metric_type = FLOAT
    equation = r"$$P^{TS}=\frac{P}{\text{academic age}}=\frac{P}{Y-Y_0+1},$$"
    ystr = r"\(Y\)"
    y0str = r"\(Y_{0}\)"
    m.description = ('<p>This metric, also called the '
                     '<span class="metric_name">time-scaled number of publications</span> is just the mean '
                     'number of publications per year, calculated as the total number of publications of an author '
                     f'divided by their academic age (number of years since their first publication),</p>{equation}'
                     f'<p>where {ystr} is the current year and {y0str} is the year of their first publication.</p>')
    m.synonyms = ["time-scaled number of publications",
                  "<em>P<sup>TS</sup></em>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pubs_per_year
    m.properties["Basic Statistic"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    return m


# citations per year
def calculate_cites_per_year(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_cites_per_year(total_cites, age)


def metric_cites_per_year() -> Metric:
    m = Metric()
    m.name = "citations per year"
    m.full_name = "citations per year"
    m.symbol = "<em>C<sup>TS</sup></em>"
    m.metric_type = FLOAT
    equation = r"$$C^{TS}=\frac{C^P}{\text{academic age}}=\frac{C^P}{Y-Y_0+1},$$"
    ystr = r"\(Y\)"
    y0str = r"\(Y_{0}\)"
    m.description = ('<p>This metric, also called the <span class="metric_name">time-scaled citation index</span>, '
                     'is just the mean number of citations per year, calculated as the total number of citations of '
                     'an author divided by their academic age (number of years since their first publication),</p>'
                     f'{equation}<p>where {ystr} is the current year and {y0str} is the year of their first '
                     f'publication.</p>')
    m.synonyms = ["time-scaled citation index",
                  "<em>C<sup>TS</sup></em>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_cites_per_year
    m.properties["Basic Statistic"] = True
    m.properties["Time"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# h-index (Hirsch )
def calculate_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    rank_order = metric_set.rank_order
    h, is_core = Impact_Funcs.calculate_h_index(citations, rank_order)
    metric_set.is_core = is_core
    return h


# def write_h_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'y=x', 'h-square', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     # write citation count for ranked publication x
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#         outstr += ", {}, null, null, null],\n".format(v)
#         output.append(outstr)
#     # write y for x=y
#     output.append("           [{}, null, {}, null, null],\n".format(0, 0))
#     output.append("           [{}, null, {}, null, null],\n".format(maxv, maxv))
#     output.append("           [null, null, null, null, null],\n")
#     # write h-square
#     output.append("           [{}, null, null, {}, null],\n".format(0, h))
#     output.append("           [{}, null, null, {}, \'h\'],\n".format(h, h))
#     output.append("           [{}, null, null, {}, null],\n".format(h, 0))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     # output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4]},\n")
#     output.append("		               2: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true, bold: true}}}}
#     \n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def create_h_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    h = metric_set.metrics["h-index"].value

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = [h, h+1]
    point_data.y = [h, h+1]
    point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [0, max(cite_data.y)]
    threshold_data.y = [0, max(cite_data.y)]
    threshold_data.style = "--"
    threshold_data.label = r"$y = x$"

    # square lines
    square_data = Impact_Graphs.LineData()
    output.append(square_data)
    square_data.x = [0, 0, h, h, 0]
    square_data.y = [0, h, h, 0, 0]
    square_data.style = ":"
    square_data.label = r"$h\text{-square}$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$h = {h}$"
    annotation.pos = (h, h)
    annotation.textpos = (h+20, h)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$h+1 = {h+1}$"
    annotation.pos = (h+1, h+1)
    annotation.textpos = (h+20, h+15)


    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc
    general_data.y_max = general_data.x_max

    return output


def write_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    for i, c in enumerate(citations):
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em>&nbsp;≤&nbsp;<em>C<sub>i</sub></em> is {h}.</p>'
    return outstr


def metric_h_index() -> Metric:
    m = Metric()
    m.name = "h-index"
    m.full_name = "h-index"
    m.html_name = "<em>h-</em>index"
    m.symbol = "<em>h</em>"
    m.axis_name = r"$h$"
    m.metric_type = INT
    m.example = write_h_index_example

    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h_index_desc"
    graph.data = create_h_index_desc_graph_data

    equation = r"$$h=\underset{i}{\max}\left(i\leq C_i\right).$$"
    m.description = ('<p>The <span class="metric_name"><em>h-</em>index</span> (Hirsch 2005) is the most ' 
                     'important personal impact factor one needs ' 
                     'to be familiar with, not because it is necessarily the best, but because (1) it was the first '
                     'major index of its type and most of the other indices are based on it in some way, and (2) it ' 
                     'is the single factor with which most other people (<em>e.g.</em>, ' 
                     'administrators) are likely to be somewhat familiar. You may find another index which you ' 
                     'prefer, but everything starts with <em>h.</em></p><p>The <em>h-</em>index is defined as the ' 
                     'largest value for which <em>h</em> publications have at least <em>h</em> citations. Put another ' 
                     'way, a scientist has an impact factor of <em>h</em> if <em>h</em> of their publications have at ' 
                     'least <em>h</em> citations and the other <em>P - h</em> publications have ≤ <em>h</em> ' 
                     'citations. Note that <em>h</em> is measured in publications. In formal notation, one might ' 
                     f'write</p>{equation}<p>These top <em>h</em> publications are often referred ' 
                     'to as the &ldquo;Hirsch core.&rdquo;</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>'
                     "<p>One way to graphically visualize <em>h</em> is to imagine a " 
                     "plot of citation count versus rank for all publications (often called the citation curve). An " 
                     "alternative way of thinking of this is a plot of minimum number of citations for a publication " 
                     "in the top <em>i</em> publications vs. <em>i</em>. By " 
                     "definition, this plot will generally trend from upper left (highest ranked publications with " 
                     "most citations) to lower right (lowest ranked publications with fewest citations), depending on " 
                     "the precise citation distribution of the author. If one were to add a (threshold) line with a " 
                     "slope of one to this plot, the point where the threshold line crosses the citation curve " 
                     "(truncated to an integer) is <em>h.</em> Alternatively, one can visualize <em>h</em> as the " 
                     "size (length of sides) of the largest (integer) square that one can fit under the citation " 
                     "curve.</p>")
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.references = ["Hirsch, J.E. (2005) An index to quantify an individual\'s scientific research output. "
                    "<em>Proceedings of the National Academy of Sciences USA</em> 102(46):16569&ndash;16572."]
    m.calculate = calculate_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# Hirsch core citations (Hirsch )
def calculate_h_core(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    is_core = metric_set.is_core
    return Impact_Funcs.calculate_sum_h_core(citations, is_core)


def write_h_core_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    hc = metric_set.metrics["h-core cites"].value
    for i, c in enumerate(citations):
        if i + 1 <= h:
            ec = ' class="box"'
        else:
            ec = ""
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
        else:
            v = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The sum of the citations for the top <em>h</em> publications is {hc}.</p>'
    return outstr


def metric_h_core() -> Metric:
    m = Metric()
    m.name = "h-core cites"
    m.full_name = "Hirsch core citations"
    m.symbol = "<em>C<sup>H</sup></em>"
    m.axis_name = r"$\text{Hirsch core citations }\left(C^H\right)$"
    m.example = write_h_core_example
    m.metric_type = INT
    equation = r"$$C^H=\sum\limits_{i=1}^{h}{C_i}.$$"
    m.description = ('<p>This is the sum of the citations for all publications that contribute to the __h-index__, '
                     f'<em>i.e.</em> the Hirsch core,</p>{equation}')
    m.synonyms = ["<em>C<sup>H</sup></em>"]
    m.references = ["Hirsch, J.E. (2005) An index to quantify an individual\'s scientific research output. "
                    "<em>Proceedings of the National Academy of Sciences USA</em> 102(46):16569&ndash;16572."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h_core
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Property"] = True
    return m


# Hirsch minimum constant (Hirsch )
def calculate_hirsch_min_const(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_hirsch_min_const(total_cites, h)


def metric_hirsch_min_const() -> Metric:
    m = Metric()
    m.name = "Hirsch min const"
    m.full_name = "Hirsch proportionality constant"
    m.symbol = "<em>a</em>"
    m.axis_name = r"$a$"
    m.metric_type = FLOAT
    equation = r"$$a=\frac{C^P}{h^2}.$$"
    m.description = ('<p>This metric (Hirsch 2005) describes a relationship between the __h-index__ and the '
                     f'__total cites__ and is defined as</p>{equation}')
    m.references = ["Hirsch, J.E. (2005) An index to quantify an individual\'s scientific research output. "
                    "<em>Proceedings of the National Academy of Sciences USA</em> 102(46):16569&ndash;16572."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hirsch_min_const
    m.properties["All Citations"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Property"] = True
    m.properties["All Publications"] = True
    m.properties["Core Publications"] = True
    return m


# g-index (Egghe 2006)
def calculate_g_index(metric_set: MetricSet) -> int:
    cumulative_citations = metric_set.cumulative_citations
    return Impact_Funcs.calculate_g_index(cumulative_citations)


def create_g_index_desc_graph_data1(metric_set: MetricSet) -> list:
    output = []

    g = metric_set.metrics["g-index"].value
    n = len(metric_set.citations)

    # cumulative citation curve
    cumulative_cite_data = Impact_Graphs.LineData()
    output.append(cumulative_cite_data)
    cumulative_cite_data.x = [i+1 for i in range(n)]
    tmp_cites = [c for c in metric_set.citations]
    tmp_cites.sort(reverse=True)
    total_cites = sum(tmp_cites)
    cumulative_cite_data.y = [tmp_cites[0]]
    for i, c in enumerate(tmp_cites[1:]):
        cumulative_cite_data.y.append(cumulative_cite_data.y[i] + c)
    cumulative_cite_data.label = "Cumulative Citations"

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = [g, g+1]
    point_data.y = [g**2, (g+1)**2]
    point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [i for i in range(n+1)]
    threshold_data.y = [i**2 for i in range(n+1)]
    threshold_data.style = "--"
    threshold_data.label = r"$y = x^2$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$g = {g}$"
    annotation.pos = (g, g**2)
    annotation.textpos = (g+20, g**2 - 30)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$g+1 = {g+1}$"
    annotation.pos = (g+1, (g+1)**2)
    annotation.textpos = (g+30, (g+1)**2)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Cumulative Citation Count"
    general_data.inc_legend = True
    general_data.x_max = max(total_cites + 5, (g+1)**2 + 5)
    general_data.y_max = general_data.x_max

    return output


def create_g_index_desc_graph_data2(metric_set: MetricSet) -> list:
    output = []

    g = metric_set.metrics["g-index"].value
    n = len(metric_set.citations)

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(n)]

    tmp_cites = [c for c in metric_set.citations]
    tmp_cites.sort(reverse=True)
    tmp_cumulative = [tmp_cites[0]]
    for i, c in enumerate(tmp_cites[1:]):
        tmp_cumulative.append(tmp_cumulative[i] + c)
    cite_data.y = [c/(i+1) for i, c in enumerate(tmp_cumulative)]
    cite_data.label = "Mean Citations"
    maxc = max(cite_data.y)

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = [g, g+1]
    point_data.y = [g, g+1]
    point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [0, max(cite_data.y)]
    threshold_data.y = [0, max(cite_data.y)]
    threshold_data.style = "--"
    threshold_data.label = r"$y = x$"

    # square lines
    square_data = Impact_Graphs.LineData()
    output.append(square_data)
    square_data.x = [0, 0, g, g, 0]
    square_data.y = [0, g, g, 0, 0]
    square_data.style = ":"
    square_data.label = r"$g\text{-square}$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$g = {g}$"
    annotation.pos = (g, g)
    annotation.textpos = (g+20, g-5)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$g+1 = {g+1}$"
    annotation.pos = (g+1, g+1)
    annotation.textpos = (g+1, g+20)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Mean Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc
    general_data.y_max = general_data.x_max

    return output


# def write_g_index_desc_data1(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["g-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Cumulative Citations', 'y=x^2', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     cum_cites = [tmp_cites[0]]
#     for i, c in enumerate(tmp_cites[1:]):
#         cum_cites.append(cum_cites[i] + c)
#     g = metric_set.metrics["g-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 150
#     # write cumulative citation count for ranked publication x
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write cumulative citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = cum_cites[x - 1]
#         outstr += ", {}, null, null],\n".format(v)
#         output.append(outstr)
#     # write y for y=x^2
#     for x in range(maxx + 1):
#         outstr = "           [{}, null".format(x)  # write rank
#         v = x**2
#         if v > maxv:
#             v = "null"
#         if x == g:
#             a = "\'g\'"
#         else:
#             a = "null"
#         outstr += ", {}, {}],\n".format(v, a)
#         output.append(outstr)
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     # output.append("		     chartArea: {width:\'75%\', height:\'75%\'},\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 20, 40, 60, 80, 100, 120, 140],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Cumulative Citation Count\',\n")
#     output.append("		             ticks: [0, 20, 40, 60, 80, 100, 120, 140],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true, bold:
#     true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output
#
#
# def write_g_index_desc_data2(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["g-index"]
#     graph = metric.description_graphs[1]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Mean Citations', 'y=x', 'g-square', "
#                   "{'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     avg_cites = []
#     for i in range(len(tmp_cites)):
#         avg_cites.append(sum(tmp_cites[:i+1])/(i+1))
#     g = metric_set.metrics["g-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 45
#     # write avg citation count for top x ranked publications
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x == 0:
#             v = "null"
#         else:
#             v = avg_cites[x - 1]
#         outstr += ", {}, null, null, null],\n".format(v)
#         output.append(outstr)
#     # write y for y=x
#     output.append("           [{}, null, {}, null, null],\n".format(0, 0))
#     output.append("           [{}, null, {}, null, null],\n".format(maxv, maxv))
#     # write g-square
#     output.append("           [{}, null, null, {}, null],\n".format(0, g))
#     output.append("           [{}, null, null, {}, \'g\'],\n".format(g, g))
#     output.append("           [{}, null, null, {}, null],\n".format(g, 0))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Mean Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4]},\n")
#     output.append("		               2: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def write_g_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Cumulative Citations (Σ<em>C<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Rank Squared (<em>i</em><sup>2</sup>)</th>'
    rows[3] = '<tr><th></th>'
    rows[4] = '<tr class="top_row"><th>Rank (<em>i</em>)</th>'
    rows[5] = '<tr><th>Mean Citations (Σ<em>C<sub>i</sub></em> / <em>i</em>)</th>'

    g = metric_set.metrics["g-index"].value
    s = 0
    for i, c in enumerate(citations):
        s += c
        if i + 1 == g:
            v = f'<em>g</em>{NBEQ}{g}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td{ec}>{s}</td>'
        rows[2] += f'<td{ec}>{(i+1)**2}</td>'
        rows[3] += f'<td>{v}</td>'
        rows[4] += f'<td{ec}>{i+1}</td>'
        rows[5] += f'<td{ec}>{s/(i+1):1.1f}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest rank where <em>i</em><sup>2</sup> ≤ Σ<em>C<sub>i</sub></em> (or '
               f'<em>i</em> ≤ mean <em>C<sub>i</sub></em>) is {g}.</p>')
    return outstr


def metric_g_index() -> Metric:
    m = Metric()
    m.name = "g-index"
    m.full_name = "g-index"
    m.html_name = "<em>g-</em>index"
    m.symbol = "<em>g</em>"
    m.axis_name = r"$g$"
    m.metric_type = INT

    graph1 = DescriptionGraph()
    m.description_graphs.append(graph1)
    graph1.name = "g_index_desc1"
    graph1.data = create_g_index_desc_graph_data1

    graph2 = DescriptionGraph()
    m.description_graphs.append(graph2)
    graph2.name = "g_index_desc2"
    graph2.data = create_g_index_desc_graph_data2

    # graph1 = DescriptionGraph()
    # m.description_graphs.append(graph1)
    # graph1.name = "g_index_desc1"
    # graph1.data = write_g_index_desc_data1
    # graph2 = DescriptionGraph()
    # m.description_graphs.append(graph2)
    # graph2.name = "g_index_desc2"
    # graph2.data = write_g_index_desc_data2
    m.example = write_g_index_example
    equation = (r"$$g=\underset{i}{\max}\left(i^2\leq \sum\limits_{j=1}^{i}{C_j}\right)="
                r"\underset{i}{\max}\left(i\leq\frac{\sum\limits_{j=1}^{i}{C_j}}{i} \right)$$")
    m.description = ('<p>The best known and most widely studied alternative to the __h-index__ is known as the '
                     '<em>g-</em>index (Egghe 2006a, b, c). The <em>g-</em>index is designed to give more credit for '
                     'publications cited in excess of the <em>h</em> threshold. The primary difference between the '
                     'formal definitions of the <em>h-</em> and <em>g-</em>indices is that <em>g</em> is based on '
                     'cumulative citation counts rather than individual citation counts. Formally, the '
                     '<em>g-</em>index is the largest value for which <em>g</em> publications have jointly received '
                     f'at least <em>g</em><sup>2</sup> citations.</p>{equation}'                     
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph1.name}.svg" />'
                     f'<img class="impact_fig" src="impact_figs/img_{graph2.name}.svg" /></figure>'                     
                     '<p>Although not usually '
                     'formulated this way, the above also shows an alternative interpretation of the <em>g-</em>'
                     'index, which makes it\'s meaning and relationship to <em>h</em> much clearer: the <em>g-</em>'
                     'index is the largest value for which the top <em>g</em> publications average <em>g</em> '
                     'citations, while <em>h</em> is the largest value for which the top <em>h</em> publications '
                     'have a minimum of <em>h</em> citations.</p><p>Stricly speaking, it is possible for the number '
                     'of citations in the <em>g-</em>core to exceed the square of the total number of publications '
                     '(<em>C<sup>P</sup></em> > <em>P</em><sup>2</sup>), or using the alternate definition, for '
                     'the average number of citations per publication to exceed the number of publications. Under '
                     'this scenario, the threshold curve and the citation curve do not actually cross. Some authors '
                     'have suggested adding phantom publications with zero citations until the curves cross '
                     '(essentially, making <em>g</em> equal to the square-root of <em>C<sup>P</sup></em>); '
                     'a more conservative approach, illustrated here, is to set the maximum possible value of '
                     '<em>g</em> equal to the number of publications.</p>')
    m.references = ["Egghe, L. (2006) How to improve the <em>h-</em>index: Letter. <em>The Scientist</em> 20(3):14.",
                    "Egghe, L. (2006) An improvement of the <em>h-</em>index: The <em>g-</em>index. <em>ISSI "
                    "Newsletter</em> 2(1):8&ndash;9.",
                    "Egghe, L. (2006) Theory and practice of the <em>g-</em>index. <em>Scientometrics</em> "
                    "69(1):131&ndash;152."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_g_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# h2-index (Kosmulski 2006)
def calculate_h2_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_h2_index(citations)


# def write_h2_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h(2)-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'y=x^2', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h(2)-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#         outstr += ", {}".format(v)
#         # write y for y=x^2
#         v = x**2
#         if v > maxv:
#             v = "null"
#         if x == h:
#             a = "\'h(2)\'"
#         else:
#             a = "null"
#         outstr += ", {}, {}".format(v, a)
#         outstr += "],\n"
#         output.append(outstr)
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     # output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true, bold:
#     true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def create_h2_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    h2 = metric_set.metrics["h(2)-index"].value
    n = len(metric_set.citations)

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(n)]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = [h2, h2+1]
    point_data.y = [h2**2, (h2+1)**2]
    point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [i for i in range(n+1)]
    threshold_data.y = [i**2 for i in range(n+1)]
    threshold_data.style = "--"
    threshold_data.label = r"$y = x^2$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = r"$h\left(2\right) = " + f"{h2}$"
    annotation.pos = (h2, h2**2)
    annotation.textpos = (h2 + 20, h2**2)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = r"$h\left(2\right) + 1 = " + f"{h2+1}$"
    annotation.pos = (h2+1, (h2+1)**2)
    annotation.textpos = (h2 + 20, (h2+1)**2)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc + 5
    general_data.y_max = general_data.x_max

    return output


def write_h2_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank-squared (<em>i</em><sup>2</sup>)'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    h = metric_set.metrics["h(2)-index"].value
    for i, c in enumerate(citations):
        if i + 1 == h:
            v = f'<em>h</em>(2){NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{(i+1)**2}</td>'
        rows[2] += f'<td>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em><sup>2</sup> ≤ <em>C<sub>i</sub></em> is {h}.</p>'
    return outstr


def metric_h2_index() -> Metric:
    m = Metric()
    m.name = "h(2)-index"
    m.full_name = "h(2)-index"
    m.html_name = "<em>h</em>(2)-index"
    m.symbol = "<em>h</em>(2)"
    m.axis_name = r"$h\left(2\right)$"
    m.metric_type = INT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h2_index_desc"
    graph.data = create_h2_index_desc_graph_data
    # graph.data = write_h2_index_desc_data
    m.example = write_h2_index_example
    equation = r"$$h\left(2\right)=\underset{i}{\max}\left(i^2 \leq C_i\right).$$"
    m.description = ('<p>The <em>h</em>(2)-index (Kosmulski 2006) is similar to the __h-index__, but rather than '
                     'define the core based on <em>h</em> publications having <em>h</em> citations, this index '
                     f'requires the <em>h</em> publications to each have <em>h</em><sup>2</sup> citations:</p>'
                     f'{equation}'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>'
                     '<p>This leads to <em>h</em>(2) having a stricter definition of the core publications than '
                     'many other metrics.</p>')
    m.references = ["Kosmulski, M. (2006) A new Hirsch-type index saves time and works equally well as the original "
                    "<em>h-</em>index. <em>ISSI Newsletter</em> 2(3):4&ndash;6."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h2_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# mu-index (Glanzel and Schubert 2010)
def calculate_mu_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_mu_index(citations)


def write_mu_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = "<tr><th>Citations (<em>C<sub>i</sub></em>)</th>"
    rows[1] = "<tr class=\"top_row\"><th>Rank (<em>i</em>)</th>"
    rows[2] = "<tr><th>Median Citations</th>"
    rows[3] = "<tr><th></th>"
    mu = metric_set.metrics["mu-index"].value
    for i, c in enumerate(citations):
        s = Impact_Funcs.calculate_median(citations[:i+1])
        if i + 1 == mu:
            v = f'<em>μ</em>{NBEQ}{mu}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += "<td>{}</td>".format(c)
        rows[1] += "<td" + ec + ">{}</td>".format(i + 1)
        rows[2] += "<td" + ec + ">{:0.1f}</td>".format(s)
        rows[3] += "<td>{}</td>".format(v)

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em> ≤ median citations is {mu}.</p>'
    return outstr


def metric_mu_index() -> Metric:
    m = Metric()
    m.name = "mu-index"
    m.full_name = "μ-index"
    m.html_name = "<em>μ-</em>index"
    m.symbol = "<em>μ</em>"
    m.axis_name = r"$\mu$"
    m.example = write_mu_index_example
    m.metric_type = INT
    m.description = ('<p>If the __h-index__ and __g-index__ are the largest value <em>x</em> for which '
                     '<em>x</em> publications have a minimum (<em>h</em>) or mean (<em>g</em>) number of citations '
                     'equal to <em>x,</em> then the <em>μ-</em>index (Glänzel and Schubert 2010) is the same idea, '
                     'except based on the median number of citations for the top <em>μ</em> publications.</p>')
    m.references = ["Glänzel, W., and A. Schubert (2010) Hirsch-type characteristics of the tail of distributions. "
                    "The generalized <em>h-</em>index. <em>Journal of Informetrics</em> 4:118&ndash;123."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_mu_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# Tol's f-index (Tol 2007)
def calculate_tol_f_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_tol_f_index(citations)


def write_tol_f_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = "<tr><th>Citations (<em>C<sub>i</sub></em>)</th>"
    rows[1] = "<tr class=\"top_row\"><th>Rank (<em>i</em>)</th>"
    rows[2] = "<tr><th>Harmonic Mean Citations</th>"
    rows[3] = "<tr><th></th>"
    f = metric_set.metrics["Tol f-index"].value
    s = 0
    for i, c in enumerate(citations):
        if c != 0:
            s += 1/c
        if i + 1 == f:
            v = f'<em>f</em>{NBEQ}{f}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += "<td>{}</td>".format(c)
        rows[1] += "<td" + ec + ">{}</td>".format(i + 1)
        rows[2] += "<td" + ec + ">{:0.1f}</td>".format(1/(s/(i+1)))
        rows[3] += "<td>{}</td>".format(v)
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += "<p>The largest rank where <em>i</em> ≤ harmonic mean citations is {}.</p>".format(f)
    return outstr


def metric_tol_f_index() -> Metric:
    m = Metric()
    m.name = "Tol f-index"
    m.full_name = "f-index (Tol)"
    m.html_name = "<em>f-</em>index (Tol)"
    m.symbol = "<em>f</em>"
    m.axis_name = r"$f$"
    m.example = write_tol_f_index_example
    m.metric_type = INT
    equation = (r"$$f=\underset{i}{\max}\left(\frac{1}{\frac{1}{i}\sum\limits_{j=1}^{i}{\frac{1}{C_j}}}\geq "
                r"i\right)=\underset{i}{\max}\left(\frac{i}{\sum\limits_{j=1}^{i}{\frac{1}{C_j}} }\geq i\right)$$")
    m.description = ('<p>If the __h-index__ and __g-index__ are the largest value <em>x</em> for which '
                     '<em>x</em> publications have a minimum (<em>h</em>) or mean (<em>g</em>) number of citations '
                     'equal to <em>x,</em> then Tol\'s <em>f-</em>index (Tol 2007) is the same idea, except based on '
                     f'the harmonic mean number of citations for the top <em>f</em> publications.</p>{equation}')
    m.references = ["Tol, R.S.J. (2007) Of the <em>h-</em>index and its alternatives: An application to the 100 "
                    "most prolific economists (FNU-146). Sustainability and Global Change, Hamburg University."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_tol_f_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# Tol's t-index (Tol 2007)
def calculate_tol_t_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_tol_t_index(citations)


def write_tol_t_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = "<tr><th>Citations (<em>C<sub>i</sub></em>)</th>"
    rows[1] = "<tr class=\"top_row\"><th>Rank (<em>i</em>)</th>"
    rows[2] = "<tr><th>Geometric Mean Citations</th>"
    rows[3] = "<tr><th></th>"
    t = metric_set.metrics["Tol t-index"].value
    s = 0
    for i, c in enumerate(citations):
        if c != 0:
            s += math.log(c)
        if i + 1 == t:
            v = f'<em>t</em>{NBEQ}{t}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += "<td>{}</td>".format(c)
        rows[1] += "<td" + ec + ">{}</td>".format(i + 1)
        rows[2] += "<td" + ec + ">{:0.1f}</td>".format(math.exp(s/(i+1)))
        rows[3] += "<td>{}</td>".format(v)
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += "<p>The largest rank where <em>i</em> ≤ geometic mean citations is {}.</p>".format(t)
    return outstr


def metric_tol_t_index() -> Metric:
    m = Metric()
    m.name = "Tol t-index"
    m.full_name = "t-index (Tol)"
    m.html_name = "<em>t-</em>index (Tol)"
    m.symbol = "<em>t</em>"
    m.axis_name = r"$t$"
    m.example = write_tol_t_index_example
    m.metric_type = INT
    equation = (r"$$t=\underset{i}{\max}\left(\exp\left(\frac{1}{i}\sum\limits_{j=1}^{i}\ln{C_j}\right)\geq "
                r"i\right)$$")
    m.description = ('<p>If the __h-index__ and __g-index__ are the largest value <em>x</em> for which '
                     '<em>x</em> publications have a minimum (<em>h</em>) or mean (<em>g</em>) number of citations '
                     'equal to <em>x,</em> then Tol\'s <em>t-</em>index (Tol 2007) is the same idea, except based on '
                     f'the geometric mean number of citations for the top <em>t</em> publications.</p>{equation}')
    m.references = ["Tol, R.S.J. (2007) Of the <em>h-</em>index and its alternatives: An application to the 100 "
                    "most prolific economists (FNU-146). Sustainability and Global Change, Hamburg University."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_tol_t_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# Woeginger w-index (Woeginger 2008)
def calculate_woeginger_w_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_woeginger_w(citations)


# def write_woeginger_w_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["Woeginger w-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'w-triangle', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     w = metric_set.metrics["Woeginger w-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     # write citation count for ranked publication x
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#         outstr += ", {}, null, null],\n".format(v)
#         output.append(outstr)
#     # write w-triangle
#     output.append("           [{}, null, {}, null],\n".format(0, w))
#     output.append("           [{}, null, {}, \'w\'],\n".format(w, 0))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output

def create_woeginger_w_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    w = metric_set.metrics["Woeginger w-index"].value

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # triangle line
    triangle_data = Impact_Graphs.LineData()
    output.append(triangle_data)
    triangle_data.x = [0, w]
    triangle_data.y = [w, 0]
    triangle_data.style = ":"
    triangle_data.label = r"$w\text{-triangle}$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$w = {w}$"
    annotation.pos = (0, w)
    annotation.textpos = (w+5, w+5)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = ""
    annotation.pos = (w, 0)
    annotation.textpos = (w+5, w+5)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc
    general_data.y_max = general_data.x_max

    return output


def write_woeginger_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(2)]
    rows[0] = '<tr><td></td><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><td></td><th>Rank (<em>k</em>)</th><td><em>k</em>…1</td>'
    w = metric_set.metrics["Woeginger w-index"].value
    for i, c in enumerate(citations):
        if i + 1 == w:
            v = f'<td><em>w</em>{NBEQ}{w}</td>'
            ec = ' class="box"'
        else:
            v = '<td></td>'
            ec = ""
        rows[0] += "<td>{}</td>".format(c)
        if i != 0:
            rows[1] += '<td></td>'
        newrow = f'<tr>{v}<th>{i+1}</th>'
        for j in range(i+1):
            newrow += f'<td{ec}>{i+1-j}</td>'
        for j in range(i+1, len(citations)+1):
            newrow += '<td></td>'
        rows.append(newrow)

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest rank where the minimum number of citations for publications 1…<em>k</em> '
               f'≤ <em>k</em>…1 is {w}.</p>')
    return outstr


def metric_woeginger_w_index() -> Metric:
    m = Metric()
    m.name = "Woeginger w-index"
    m.full_name = "w-index (Woeginger)"
    m.html_name = "<em>w-</em>index (Woeginger)"
    m.symbol = "<em>w</em>"
    m.axis_name = r"$w$"
    m.metric_type = INT
    m.example = write_woeginger_index_example
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "woeginger_w_index_desc"
    graph.data = create_woeginger_w_index_desc_graph_data
    equation = r"$$w=\underset{k}{\max}\left(C_i \geq k-i+1\right),$$"
    m.description = ('<p>Woeginger\'s <em>w-</em>index (Woeginger 2008) is somewhat similar to the __h-index__. '
                     'It is the largest value of <em>w</em> for which publications have at least 1, 2, 3, …<em>w</em> '
                     f'citations:</p>{equation}<p>for all <em>i</em> ≤ <em>k</em>. Put another way, the top '
                     '1…<em>k</em> publications have to have at least <em>k</em>…1 citations, respectively.</p>'
                     '<p>Graphically, if the '
                     '<em>h-</em>index is the largest square with sides <em>h</em> that can fit under the citation '
                     'curve, <em>w</em> is the largest right-angled isoceles triangle with perpendicular sides of '
                     '<em>w</em> which fits under the curve.'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Woeginger, G.J. (2008) An axiomatic characterization of the Hirsch-index. <em>Mathematical "
                    "Social Sciences</em> 56(2):224&ndash;242."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_woeginger_w_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# Wu w-index (Wu 2010)
def calculate_wu_w_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_wu_w_index(citations)


def create_wu_w_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    w = metric_set.metrics["Wu w-index"].value

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = [w, w+1]
    point_data.y = [w*10, (w+1)*10]
    point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [0, max(cite_data.y)]
    threshold_data.y = [0, max(cite_data.y)*10]
    threshold_data.style = "--"
    threshold_data.label = r"$y = 10x$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$w = {w}$"
    annotation.pos = (w, w*10)
    annotation.textpos = (w+20, w*10)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$w+1 = {w+1}$"
    annotation.pos = (w+1, (w+1)*10)
    annotation.textpos = (w+20, (w+1)*10)


    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = max(maxc, (w+1)*10)
    general_data.y_max = general_data.x_max

    return output

# def write_wu_w_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["Wu w-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'y=10x', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     w = metric_set.metrics["Wu w-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     # write citation count for ranked publication x
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#         outstr += ", {}, null, null],\n".format(v)
#         output.append(outstr)
#     # write y for y=10x
#     output.append("           [{}, null, {}, null],\n".format(0, 0))
#     output.append("           [{}, null, {}, \'w\'],\n".format(w, 10*w))
#     output.append("           [{}, null, {}, null],\n".format(maxv/10, maxv))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def write_wu_w_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>10&times;Rank (10<em>i</em>)'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    w = metric_set.metrics["Wu w-index"].value
    for i, c in enumerate(citations):
        if i + 1 == w:
            v = f'<em>w</em>{NBEQ}{w}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{(i+1)*10}</td>'
        rows[2] += f'<td>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where 10<em>i</em> ≤ <em>C<sub>i</sub></em> is {w}.</p>'
    return outstr


def metric_wu_w_index() -> Metric:
    m = Metric()
    m.name = "Wu w-index"
    m.full_name = "w-index (Wu)"
    m.html_name = "<em>w-</em>index (Wu)"
    m.symbol = "<em>w</em>"
    m.axis_name = r"$w$"
    m.metric_type = INT
    m.example = write_wu_w_index_example
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "wu_w_index_desc"
    graph.data = create_wu_w_index_desc_graph_data
    equation = r"$$w=\underset{i}{\max}\left(i \leq 10C_i\right)$$"
    m.description = ('<p>Wu\'s <em>w-</em>index (Wu 2010) is very similar to the __h-index__, but defines a '
                     'stricter core by requiring that each of the <em>w</em> publications have at least 10<em>w</em> '
                     f'citations.</p>{equation}'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>'
                     '<p>One can view this graphically as identical to the '
                     '<em>h-</em>index, except the threshold line has a slope of 10 rather than 1.</p>')
    m.references = ["Wu, Q. (2010) The <em>w-</em>index: A measure to assess scientific impact by focusing on widely "
                    "cited papers. <em>Journal of the American Society for Information Science and Technology</em> "
                    "61(3):609&ndash;614."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_wu_w_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# Wu w(q) (Wu 2010)
def calculate_wu_wq(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    w = metric_set.metrics["Wu w-index"].value
    return Impact_Funcs.calculate_wu_wq(citations, w)


def metric_wu_wq() -> Metric:
    m = Metric()
    m.name = "Wu w(q)"
    m.full_name = "w(q) (Wu)"
    m.html_name = "<em>w</em>(<em>q</em>) (Wu)"
    m.symbol = "<em>q</em>"
    m.axis_name = r"$q$"
    m.metric_type = INT
    m.description = ('<p>A corollary measure of the __Wu w-index__, <em>q</em> (Wu 2010) is the number of '
                     'additional citations needed by an author to raise their <em>w-</em>index by one. It is similar '
                     'to the __rational h-index__, except expressed as an integer rather than a fractional '
                     'component.</p>')
    m.references = ["Wu, Q. (2010) The <em>w-</em>index: A measure to assess scientific impact by focusing on widely "
                    "cited papers. <em>Journal of the American Society for Information Science and Technology</em> "
                    "61(3):609&ndash;614."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_wu_wq
    m.properties["Core Property"] = True
    return m


# hg-index (Alonso et al. 2010)
def calculate_hg_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    g = metric_set.metrics["g-index"].value
    return Impact_Funcs.calculate_hg_index(h, g)


def metric_hg_index() -> Metric:
    m = Metric()
    m.name = "hg-index"
    m.full_name = "hg-index"
    m.html_name = "<em>hg-</em>index"
    m.symbol = "<em>hg</em>"
    m.axis_name = r"$hg$"
    m.metric_type = FLOAT
    equation = r"$$hg=\sqrt{h \times g}.$$"
    m.description = ('<p>The <em>hg-</em>index (Alonso <em>et al.</em> 2010) is an aggregate index which tries to '
                     'keep the advantages of both the __h-index__ and __g-index__ while minimizing their '
                     'disadvantages. The index is simply the geometric mean of <em>h</em> and <em>g,</em> or</p>' +
                     equation)
    m.references = ["Alonso, S., F.J. Cabrerizo, E. Herrera-Viedma, and F. Herrera (2010) <em>hg-</em>index: A new "
                    "index to characterize the scientific outpuf of researchers based on the <em>h-</em> and "
                    "<em>g-</em>indices. <em>Scientometrics</em> 82:391&ndash;400."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hg_index
    m.properties["Core Property"] = True
    m.properties["Compound Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# a-index (Jin 2006; Rousseau 2006)
def calculate_a_index(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    # total_pubs = metric_set.metrics["total pubs"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_a_index(core_cites, h)


def metric_a_index() -> Metric:
    m = Metric()
    m.name = "a-index"
    m.full_name = "a-index"
    m.html_name = "<em>a-</em>index"
    m.symbol = "<em>a</em>"
    m.axis_name = r"$a$"
    m.metric_type = FLOAT
    equation = r"$$a=\frac{C^H}{h}=\frac{\sum\limits_{i=1}^{h}{C_i}}{h}.$$"
    m.description = ('<p>The <em>a-</em>index (Jin 2006; Rousseau 2006) is used to describe the citations within '
                     'the __h-index__ core itself, being simply the average number of citations per core publication, '
                     f'or</p>{equation}<p>The minimum value of <em>a</em> is <em>h</em> (since every one of the '
                     f'<em>h</em> publications must have at least <em>h</em> citations).</p>')
    m.references = ["Jin, B. (2006) <em>h-</em>index: An evaluation indicator proposed by scientist. "
                    "<em>Science Focus</em> 1(1):8&ndash;9.",
                    "Rousseau, R. (2006) New developments related to the Hirsch index. <em>Science Focus</em> "
                    "1(4):23&ndash;25."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_a_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# R-index (Jin et al. 2007)
def calculate_r_index(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    return Impact_Funcs.calculate_r_index(core_cites)


def metric_r_index() -> Metric:
    m = Metric()
    m.name = "R-index"
    m.full_name = "R-index"
    m.html_name = "<em>R-</em>index"
    m.symbol = "<em>R</em>"
    m.axis_name = r"$R$"
    m.metric_type = FLOAT
    equation = r"$$R=\sqrt{C^H}=\sqrt{\sum\limits_{i=1}^{h}{C_i}}.$$"
    m.description = ('<p>The <em>R-</em>index (Jin <em>et al.</em> 2007) is a measure of the quality of the '
                     '__h-index__ core, designed to avoid punishing scientists with larger cores. As a simple '
                     'arithmetic average, the __a-index__ has the size of the core in the divisor and therefore can '
                     'lead to smaller values for scientists with much larger cores than those with much smaller '
                     'cores (this is not an issue if the indices are only being used to compare those with similar '
                     'sized cores). The <em>R-</em>index is the square-root of the citations in the core rather than '
                     f'average:</p>{equation}')
    m.references = ["Jin, B., L. Liang, R. Rousseau, and L. Egghe (2007) The <em>R-</em> and <em>AR-</em>indices: "
                    "Complementing the <em>h-</em>index. <em>Chinese Science Bulletin</em> 52(6):855&ndash;863."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_r_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
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
    equation = r"$$D=\frac{P}{C^P}$$"
    m.description = ('<p>This metric is simply the total number of publications divided by the number of total '
                     'number of citations (Egghe and Rousseau 1996); it was originally proposed to evaluate journals '
                     'but can be applied to individuals as well. The larger this value, the more indifferent the '
                     f'community is to the author\'s work. This metric is also just the inverse of '
                     f'__c/p__.</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.symbol = "<em>D</em>"
    m.synonyms = ["D"]
    m.references = ["Egghe, L., and R. Rousseau (1996) Average and global impact of a set of journals. "
                    "<em>Scientometrics</em> 36:97&ndash;107."]
    m.calculate = calculate_indifference
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# rational h-index (Ruane and Tol 2008)
def calculate_rational_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_rational_h(citations, h)


def write_rational_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    rath = metric_set.metrics["rational h-index"].value
    hnext = h + 1 - citations[h]
    hin = 0
    for i, c in enumerate(citations):
        if i < h:
            if c == h:
                hin += 1
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h}. To reach an <em>h</em> of {h+1}, we would need to add {hin} '
               f'citations to the publications within the core and {hnext} citations to the {h+1}<sup>th</sup> '
               f'publication (for a total of {hnext}). The maximum number of citations that could be required is '
               f'{2*h+1} (if all {h} core publications had exactly {h} citations and the {h+1}<sup>th</sup> '
               f'publication had zero), thus the rational <em>h</em> is {h} + 1 - {hnext}/{2*h+1} = {rath:0.4f}.</p>')
    return outstr


def metric_rational_h_index() -> Metric:
    m = Metric()
    m.name = "rational h-index"
    m.full_name = "rational h-index"
    m.html_name = "rational <em>h-</em>index"
    m.metric_type = FLOAT
    m.example = write_rational_h_index_example
    equation = r"$$h^\Delta = h + 1 -\frac{n}{2h+1},$$"
    nstr = r"\(n\)"
    hstr = r"\(h\)"
    hp1 = r"\(h+1\)"
    maxh = r"\(2h+1\)"
    remh = r"\(h+1-C_{h+1}\)"
    m.description = ('<p>The rational <em>h-</em>index (Ruane and Tol 2008) (<em>h</em><sup>Δ</sup> or '
                     '<em>h</em><sub>rat</sub>) is a continuous version of the __h-index__ which not only measures '
                     'the standard <em>h-</em>index but includes the fractional progress toward the next higher '
                     f'value of <em>h.</em> It is calculated as</p>{equation}'
                     f'where {nstr} is the number of citations necessary to reach the next value of {hstr}. '
                     f'The divisor, {maxh}, is the maximum number of possible citations needed to move from '
                     f'{hstr} to {hp1} (one additional citation for each of the {hstr} publications in '
                     f'the core plus {hp1} citations for a publication outside of the core with no '
                     f'citations). Practically speaking, {nstr} is the number of publications in the core with '
                     f'exactly {hstr} citations (thus needing one more to allow a move to {hp1}) plus {remh} '
                     f'(the number of citations the {hp1}<sup>th</sup> ranked publication needs to reach {hp1} '
                     f'citations).</p>')
    m.references = ["Ruane, F., and R.S.J. Tol (2008) Rational (successive) <em>h-</em>indices: An application to "
                    "economics in the Republic of Ireland. <em>Scientometrics</em> 75(2):395&ndash;405."]
    m.synonyms = ["h<sub>rat</sub>", "h<sup>Δ</sup>"]
    m.symbol = "<em>h</em><sup>Δ</sup>"
    m.axis_name = r"$h^{\Delta}$"
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_rational_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# real h-index (hr-index) (Guns and Rousseau 2009)
def calculate_real_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_real_h_index(citations, h)


# def write_real_h_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["real h-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'y=x', {'type': 'string', 'role': 'annotation'}, 'h-square', "
#                   "'h+1-square'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     hr = metric_set.metrics["real h-index"].value
#     h = int(hr)
#     minv = h - 4
#     maxv = h + 4
#     ticks = list(range(minv, maxv + 1))
#     # write citation count for ranked publication x
#     for x in range(minv, maxv + 1):
#         v = tmp_cites[x - 1]
#         output.append("           [{}, {}, null, null, null, null],\n".format(x, v))
#     # write x = y
#     output.append("           [0, null, 0, null, null, null],\n")
#     output.append("           [{}, null, {}, \'h\', null, null],\n".format(int(h), int(h)))
#     output.append("           [{}, null, {}, \'real h\', null, null],\n".format(hr, hr))
#     output.append("           [{}, null, {}, \'h+1\', null, null],\n".format(int(h)+1, int(h)+1))
#     output.append("           [{}, null, {}, null, null, null],\n".format(maxv, maxv))
#     # write squares
#     output.append("           [{}, null, null, null, {}, null],\n".format(0, int(h)))
#     output.append("           [{}, null, null, null, {}, null],\n".format(int(h), int(h)))
#     output.append("           [{}, null, null, null, {}, null],\n".format(int(h), 0))
#     output.append("           [null, null, null, null, null, null],\n")
#     output.append("           [{}, null, null, null, null, {}],\n".format(0, int(h)+1))
#     output.append("           [{}, null, null, null, null, {}],\n".format(int(h)+1, int(h)+1))
#     output.append("           [{}, null, null, null, null, {}],\n".format(int(h)+1, 0))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'bottom'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: " + str(ticks) + ",\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + ", minv: " + str(minv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + ", minv: " + str(minv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: " + str(ticks) + ",\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}},\n")
#     output.append("		               2: {lineDashStyle: [2, 2], visibleInLegend: false},\n")
#     output.append("		               3: {lineDashStyle: [2, 2], visibleInLegend: false}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output

def create_real_h_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    hr = metric_set.metrics["real h-index"].value
    h = math.floor(hr)

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = [h, h+1, hr]
    point_data.y = [h, h+1, hr]
    point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [0, max(cite_data.y)]
    threshold_data.y = [0, max(cite_data.y)]
    threshold_data.style = "--"
    threshold_data.label = r"$y = x$"

    # square lines
    square_data = Impact_Graphs.LineData()
    output.append(square_data)
    square_data.x = [0, 0, h, h, 0]
    square_data.y = [0, h, h, 0, 0]
    square_data.style = ":"
    square_data.label = r"$h\text{-square}$"

    # annotation
    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$h = {h}$"
    annotation.pos = (h, h)
    annotation.textpos = (h+3, h-1)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$h+1 = {h+1}$"
    annotation.pos = (h+1, h+1)
    annotation.textpos = (h+1, h+4)

    annotation = Impact_Graphs.AnnotationData()
    output.append(annotation)
    annotation.label = f"$h_r = {hr:0.2f}$"
    annotation.pos = (hr, hr)
    annotation.textpos = (hr+3, hr)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = h*2
    general_data.y_max = general_data.x_max

    return output


def write_real_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    realh = metric_set.metrics["real h-index"].value
    for i, c in enumerate(citations):
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    ch = citations[h-1]
    ch1 = citations[h]
    outstr += (f'<p>The <em>h-</em>index is {h}. The {h}<sup>th</sup> publication has '
               f'<em>C<sub>h</sub></em>{NBEQ}{ch} citations, '
               f'while the {h+1}<sup>th</sup> publication has <em>C<sub>h+1</sub></em>{NBEQ}{ch1} '
               f'citations. <em>h<sub>r</sub>{NBEQ}({h+1}&times;{ch}{NBMINUS}{h}&times;{ch1})/'
               f'(1{NBMINUS}{ch1}{NBPLUS}{ch}){NBEQ}{realh:0.4f}</em>')
    return outstr


def metric_real_h_index() -> Metric:
    m = Metric()
    m.name = "real h-index"
    m.full_name = "real h-index"
    m.html_name = "real <em>h-</em>index"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "real_h_index_desc"
    graph.data = create_real_h_index_desc_graph_data
    equation = r"$$h_r=\frac{\left(h+1\right)C_h-hC_{h+1}}{1-C_{h+1}+C_h}.$$"
    m.description = ('<p>One can calculate the real <em>h-</em>index (Guns and Rousseau 2009), also known as the '
                     '<span class="metric_name">interpolated <em>h-</em>index</span>, as the point at which '
                     'the linear interpolation between the citation counts associated with publications <em>h</em> '
                     f'and <em>h</em> + 1 crosses a line with slope one,</p>{equation}'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>'
                     'The real <em>h-</em>index has the same graphical definition as the __h-index__, except it is '
                     'not restricted to integer values and thus represents the actual point where the citation and '
                     'threshold curves cross.</p>')
    m.references = ["Guns, R., and R. Rousseau (2009) Real and rational variants of the <em>h-</em>index and the "
                    "<em>g-</em>index. <em>Journal of Informetrics</em> 3:64&ndash;71."]
    m.symbol = "<em>h<sub>r</sub></em>"
    m.axis_name = r"$h_r$"
    m.example = write_real_h_index_example
    m.synonyms = ["<em>h<sub>r</sub></em>", "interpolated <em>h-</em>index"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_real_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# tapered h-index (Anderson et al. 2008)
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
    equation1 = (r"$$h_{T\left(i\right)}=\left |\begin{matrix} \frac{C_i}{2i-1} & \text{if } C_i \leq i \\ "
                 r"\frac{i}{2i-1}+\sum\limits_{j=i+1}^{C_i}{\frac{1}{2j-1}} & \text{if } C_i > i \end{matrix}\right. "
                 r",$$")
    equation2 = r"$$h_T=\sum\limits_{i=1}^{P}{h_{T\left(i\right)}}.$$"
    hdstr = r"\(h^\Delta=3.71\)"
    ferrers_graph = ('<table class="ferrers">'
                     '<tr><th></th><th></th><th colspan=7>Citation</th></tr>'
                     '<tr><td></td><td></td><td class="tc_bb">1</td><td class="tc_bb">2</td>'
                     '  <td class="tc_bb">3</td><td class="tc_bb">4</td>'
                     '  <td class="tc_bb">5</td><td class="tc_bb">6</td><td class="tc_bb">→</td></tr>'
                     '<tr><th rowspan=6>Ranked<br/>publication</th>'
                     '  <td class="tc_rb">1</td><td class="tc_bdb tc_rdb">1</td><td class="tc_rdb">1/3</td>'
                     '  <td class="tc_rdb">1/5</td><td>1/7</td><td>1/9</td><td>1/11</td></tr>'
                     '<tr><td class="tc_rb">2</td><td class="tc_bdb">1/3</td><td class="tc_bdb tc_rdb">1/3</td>'
                     '  <td class="tc_rdb">1/5</td><td>1/7</td></tr>'
                     '<tr><td class="tc_rb">3</td><td class="tc_bdb">1/5</td><td class="tc_bdb">1/5</td>'
                     '  <td class="tc_bdb tc_rdb">1/5</td><td>1/7</td></tr>'
                     '<tr><td class="tc_rb">4</td><td>1/7</td><td>1/7</td></tr>'
                     '<tr><td class="tc_rb">5</td><td>1/9</td></tr>'
                     '<tr><td class="tc_rb">↓</td></tr>'
                     '</table>')
    m.description =  ('<p>While the __rational h-index__ gives a fractional value to those citations necessary '
                     'to reach the next value of <em>h,</em> the tapered <em>h-</em>index (Anderson <em>et al.</em> '
                     '2008) is designed to give every citation for every publication some fractional value. The best '
                     'way to understand this index is to first consider the contribution of every citation to the '
                     '__h-index__. To have an <em>h-</em>index of 1, an author needs a single paper with a '
                     'single citation. That citation has a weight (or score) of 1, because it accounts for the '
                     'entire <em>h</em> value of 1. To move to an <em>h-</em>index of 2, the author needs three '
                     'additional citations: one additional citation for the original publication and two citations '
                     'for a second publication. As <em>h</em> has increased by one, each of these three citations is '
                     'contributing a weight (or score) of 1/3 to the total <em>h-</em>index. This is most easily '
                     'illustrated by a Ferrers graph of ranked publications versus citations which shows the specific '
                     f'contribution of every citation to a specific value of <em>h</em></p>{ferrers_graph}'
                     '<p>The largest filled-in square in the upper left corner (the Durfee square) has a length equal '
                     'to <em>h;</em> the contents of the square also sum to <em>h.</em> Using this logic, one can '
                     'determine the credit each citation would give to a larger value of <em>h,</em> regardless of '
                     'whether that <em>h</em> has been reached. Consider this graph with respect to the rational '
                     '<em>h-</em>index. In the above example, <em>h</em> is 3. If one just considers the citations '
                     'necessary to reach an <em>h</em> of 4, we can see that 5 of the 7 necessary citations are '
                     'already present. Each of these has a weight of 1/7 (since 7 total citations are necessary); '
                     f'adding these to <em>h</em> we get the rational <em>h-</em>index, {hdstr}. '
                     'The tapered <em>h-</em>index is simply taking this same concept but expanding it to include '
                     'all citations for all publications.</p><p>The tapered <em>h-</em>index for a specific '
                     'publication is the sum of all of its scores and the total score of the index is the sum across '
                     'all publications. In simple formulaic terms, the score <em>h<sub>T</sub></em>(<em>i</em>) for '
                     f'the <em>i</em><sup>th</sup> ranked publication is calculated as</p>{equation1}'
                     '<p>and the total tapered <em>h-</em>index is the sum of these scores for all publications,</p>'
                     f'{equation2}This index is consistent with the concept of the <em>h-</em>index, while also '
                     'giving every citation some small influence on the score.</p>')
    m.references = ["Anderson, T.R., R.K.S. Hankin, and P.D. Killworth (2008) Beyond the Durfee square: Enhancing "
                    "the <em>h-</em>index to score total publication output. <em>Scientometrics</em> "
                    "76(3):577&ndash;588."]
    m.symbol = "<em>h<sub>T</sub></em>"
    m.axis_name = r"$h_T$"
    m.synonyms = ["<em>h<sub>T</sub></em>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_tapered_h_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# j-index (Todeschini 2011)
def calculate_todeschini_j_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_todeschini_j_index(citations, h)


def write_todeschini_j_index_example(metric_set: MetricSet) -> str:
    dhk = (500, 250, 100, 50, 25, 10, 5, 4, 3, 2, 1.5, 1.25)
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    j = metric_set.metrics["Todeschini j-index"].value
    for i, c in enumerate(citations):
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    cnts = [0 for _ in dhk]
    for k, d in enumerate(dhk):
        for c in citations:
            if c >= d * h:
                cnts[k] += 1
    outstr += '<p></p><table class="example_table">'
    rows = ["" for _ in range(6)]
    rows[0] = '<tr class="top_row"><th><em>k</em></th>'
    rows[1] = '<tr><th>Δ<em>h<sub>k</sub></em></th>'
    rows[2] = '<tr><th><em>h</em>&times;Δ<em>h<sub>k</sub></em></th>'
    rows[3] = ('<tr><th><em>X<sub>k</sub></em> = Count <em>C<sub>i</sub></em> ≥ '
            '<em>h</em>&times;Δ<em>h<sub>k</sub></em></th>')
    rows[4] = '<tr><th>Weight (<em>w<sub>k</sub></em>)</th>'
    rows[5] = '<tr><th><em>w<sub>k</sub></em><em>X<sub>k</sub></em></th>'
    sumwkxk = 0
    sumw = 0
    for k, d in enumerate(dhk):
        rows[0] += f'<td>{k+1}</td>'
        rows[1] += f'<td>{d}</td>'
        rows[2] += f'<td>{h*d}</td>'
        rows[3] += f'<td>{cnts[k]}</td>'
        rows[4] += f'<td>{1/(k+1):0.2f}</td>'
        rows[5] += f'<td>{cnts[k]/(k+1):0.2f}</td>'
        sumw += 1/(k+1)
        sumwkxk += cnts[k]/(k+1)
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The sum of <em>w<sub>k</sub></em><em>X<sub>k</sub></em> = {sumwkxk:0.4f} and the sum of '
               f'<em>w<sub>k</sub></em> = {sumw:0.4f}, therefore <em>j</em> = {h} + {sumwkxk:0.4f}/{sumw:0.4f} = '
               f'{j:0.4f}.</p>')
    return outstr


def metric_todeschini_j_index() -> Metric:
    m = Metric()
    m.name = "Todeschini j-index"
    m.full_name = "j-index (Todeschini)"
    m.html_name = "<em>j-</em>index (Todeschini)"
    m.symbol = "<em>j</em>"
    m.axis_name = r"$j$"
    m.metric_type = FLOAT
    m.example = write_todeschini_j_index_example
    j_table = ('<table class="j_table">'
               '<tr class="top_row"><th><em>k</em></th><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td>'
               '<td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>11</td><td>12</td></tr>'
               '<tr><th>Δ<em>h<sub>k</sub></em></th>'
               '<td>500</td><td>250</td><td>100</td><td>50</td><td>25</td><td>10</td><td>5</td><td>4</td>'
               '<td>3</td><td>2</td><td>1.5</td><td>1.25</td></tr>'
               '</table>')
    equation = (r"$$j=h+\frac{\sum\limits_{k=1}^{12}{w_kX_k\left(h\times "
                r"\Delta h_k\right)}}{\sum\limits_{k=1}^{12}{w_k} } ,$$")
    xkstr = r"\(X_k\left(h \times \Delta h_k\right)\)"
    hxhk = r"\(h \times \Delta h_k\)"
    wk = r"\(w_k\)"
    invk = r"\(1/k\)"
    m.description = ('<p>The <em>j-</em>index (Todeschini 2011) is a modification of the __h-index__ which '
                     'allows for over-cited publications in the core to increase the overall value of the index. '
                     f'It uses a set of fixed categorical increases over <em>h:</em></p>{j_table}{equation}'
                     f'<p>where {wk}, the weight given to each category, is simply {invk}, '
                     f'and {xkstr} is the count of publications whose citations are at least equal to {hxhk}.</p><p>'
                     'Essentially this metric adds additional scores to <em>h</em> for publications which are cited '
                     'well more than that necessary for the core, with larger weight given to those much higher than '
                     'the core value (500 times the core get a weight of 1, 250 times the core get a weight of 0.5, '
                     'etc.).</p>')
    m.references = ["Todeschini, R. (2011) The <em>j-</em>index: A new bibliometric index and multivariate "
                    "comparisons between other common indices. <em>Scientometrics</em> 87:621&ndash;639."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_todeschini_j_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# Wohlin w-index (Wohlin 2009)
def calculate_wohlin_w_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_wohlin_w(citations)


def write_wohlin_w_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    row1 = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    for c in citations:
        row1 += f'<td>{c}</td>'
    row1 += '</tr>\n'
    outstr += row1 + '</table>\n'
    outstr += ('<p></p><table class="cds_table">'
               '<tr><th>Class<br/>(<em>c</em>)</th><th>Citation<br/>Range</th><th>Count of Pubs<br/>in '
               'Range<br/>(<em>X<sub>c</sub></em>)</th>'
               '<th>ln (lower limit)<br/>(<em>T<sub>c</sub></em>)</th>'
               '<th>Cumulative<br/>Sum of <em>T<sub>c</sub></em><br />(<em>V<sub>c</sub></em>)</th>'
               '<th><em>X<sub>c</sub></em><em>V<sub>c</sub></em></th></tr>')
    max_cites = max(citations)
    j = 5
    nc = 1
    while max_cites > j-1:
        j *= 2
        nc += 1
    v = 0
    low = 0
    high = 4
    for i in range(nc):
        x = 0
        if i == 0:
            t = 0
        else:
            low = high + 1
            high = high*2 + 1
            t = math.log(low)
        v += t
        for c in citations:
            if (c >= low) and (c <= high):
                x += 1
        outstr += (f'<tr><td>{i}</td><td>{low}&ndash;{high}</td><td>{x}</td><td>{t:0.4f}</td><td>{v:0.4f}</td>'
                   f'<td>{x*v:0.4f}</td></tr>')
    outstr += "</table>"
    w = metric_set.metrics["Wohlin w-index"].value
    outstr += ('<p>The index is the sum of <em>X<sub>c</sub></em><em>V<sub>c</sub></em>, thus '
               f'<em>w</em> = {w:0.4f}.</p>')
    return outstr


def metric_wohlin_w_index() -> Metric:
    m = Metric()
    m.name = "Wohlin w-index"
    m.full_name = "w-index (Wohlin)"
    m.html_name = "<em>w-</em>index (Wohlin)"
    m.symbol = "<em>w</em>"
    m.axis_name = r"$w$"
    m.example = write_wohlin_w_index_example
    m.metric_type = FLOAT
    table = ('<table class="cds_table">'
             '<tr><th>Class<br/>(<em>c</em>)</th><th>Citation Range</th>'
             '<th>ln (lower limit)<br/>(<em>T<sub>c</sub></em>)</th>'
             '<th>Cumulative<br/>Sum of <em>T<sub>c</sub></em><br />(<em>V<sub>c</sub></em>)</th></tr>')
    v = 0
    low = 0
    high = 4
    for i in range(11):
        if i == 0:
            t = 0
        else:
            low = high + 1
            high = high*2 + 1
            t = math.log(low)
        v += t
        table += f'<tr><td>{i}</td><td>{low}&ndash;{high}</td><td>{t:0.4f}</td><td>{v:0.4f}</td></tr>'
    table += '<tr><td>etc.</td></tr></table>'
    equation = r"$$w=\sum\limits_{c=1}^{c^\prime}{X_c V_c}$$"
    m.description = ('<p>Wohlin\'s <em>w-</em>index (Wohlin 2009) is similar to others that try to address the issue '
                     'where not all citations are included in the __h-index__ and that many different '
                     'distributions of citations can have identical <em>h-</em>indices. Unlike the other indices, '
                     'however, it does not start with <em>h,</em> and instead uses a somewhat complicated procedure '
                     'of dividing papers into classes based on the number of citations. Rather than give '
                     'publications more weight for every citation, this index gives more weight to citations as the '
                     'publication moves from one class to the next. Publications with fewer than five citations are '
                     'ignored (given a weight of 0). The first class represents publications with 5-9 citations; '
                     'each subsequent class has a width double that of the previous class, thus the second class '
                     'represents 10-19 citations, the third class 20-39 citations, etc. This structure was '
                     'chosen (other classification schemes could be substituted) because citations curves are '
                     'usually skewed with many publications with relatively smaller numbers of citations, and few '
                     f'publications with relative large numbers of citations.</p>{table}'
                     '<p>To calculate the metric, for each of '
                     'the <em>c\'</em> classes, one can count the number of publications within the '
                     '<em>c</em><sup>th</sup> class, <em>X<sub>c</sub>.</em> Skewed distributions are often '
                     'normalized using a logarithmic transform. Therefore, one calculates the natural logarithm of '
                     'the lower limit of each class as <em>T<sub>c</sub></em> = ln(<em>B<sub>c</sub></em>) where '
                     '<em>B<sub>c</sub></em> is the lower limit of the <em>c</em><sup>th</sup> class. One can also '
                     'calculate <em>V<sub>c</sub></em> as the cumulative sum of <em>T<sub>c</sub></em> for all '
                     f'classes from 1 to <em>c.</em> The <em>w-</em>index is then calculated as</p>{equation}'
                     '<p>The <em>w-</em>index increases as a publication moves from one class to the next. Moving '
                     'between larger classes gives more weight than moving between smaller classes. Because it '
                     'considers citations more broadly, the <em>w-</em>index is more fine-grained than the '
                     '<em>h-</em>index.</p>')
    m.references = ["Wohlin, C. (2009) A new index for the citation curve of researchers. <em>Scientometrics</em> "
                    "81(2):521&ndash;533."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_wohlin_w_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# hj-indices (Dorta-Gonzalez and Dorta-Gonzalez 2010)
def calculate_hj_indices(metric_set: MetricSet) -> list:
    citations = metric_set.citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_hj_indices(h, citations)


def write_hj_indices_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    for i, c in enumerate(citations):
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h}. From here we calculate the <em>H<sub>j</sub></em>-indices as '
               f'follows:</p>\n')
    hj_list = metric_set.metrics["hj-indices"].value
    outstr += '<table class="example_table">\n'
    for i in range(len(hj_list)):
        outstr += f'<tr><th><em>H</em><sub>{i}</sub></th><td>=</td>'
        if i == 0:
            outstr += f'<td><em>h</em><sup>2</sup></td><td>=</td><td>{h}<sup>2</sup>{NBEQ}{hj_list[i]}</td>'
        else:
            outstr += (f'<td><em>H</em><sub>{i-1}</sub>{NBPLUS}(<em>C</em><sub>{h-i}</sub>{NBMINUS}'
                       f'<em>C</em><sub>{h-i+1}</sub>)&times;(h{NBMINUS}{i}){NBPLUS}<em>C</em><sub>{h+i}</sub></td>'
                       f'<td>=</td><td>{hj_list[i-1]}{NBPLUS}({citations[h-i-1]}{NBMINUS}{citations[h-i]})&times;'
                       f'({h}{NBMINUS}{i}){NBPLUS}{citations[h+i-1]}{NBEQ}{hj_list[i]}</td>')
        outstr += '</tr>\n'
    outstr += '</table>\n'
    return outstr


def metric_hj_indices() -> Metric:
    m = Metric()
    m.name = "hj-indices"
    m.full_name = "Hj-indices"
    m.html_name = "<em>H<sub>j</sub>-</em>indices"
    m.metric_type = LIST
    m.list_formats = INT
    equation1 = r"$$H_0=h^2.$$"
    equation2 = r"$$H_j=H_{j-1}+\left( C_{h-j} - C_{h-j+1} \right) \left(h-j\right)+C_{h+j}.$$"
    m.description = ('<p>The <em>H<sub>j</sub></em>-indices (Dorta-González and Dorta-González 2010) are essentially '
                     'a multivariate cross between the __rational h-index__ (<em>h</em><sup>Δ</sup>) and __Wu w(q)__. '
                     'Like <em>h</em><sup>Δ</sup>, they '
                     'attempt to discriminate amongst researchers with identical <em>h</em> values by comparing the '
                     'upper and lower parts of the core to measure how close an author is to moving from one '
                     '<em>h</em> to the next larger <em>h</em>. These indices are repeated for a series of '
                     '<em>j</em>\'s, where each <em>j</em> indicates the next higher value of <em>h</em> or '
                     '<em>h</em> + <em>j</em>. Like <em>w</em>(<em>q</em>), the measures are in raw numbers of '
                     'publications (rather than scaled) so can be a bit more cumbersome to interpret; furthermore '
                     'they don\'t measure the missing number of citations, but rather total numbers and can include '
                     'citations above-and-beyond those necessary to reach a particular <em>j</em>.</p><p>The basic '
                     f'calculation starts with the number of papers in the central core, thus</p>{equation1}'
                     f'<p>Each subsequent value is then calculated as</p>{equation2}'
                     'For <em>H</em><sub>1</sub>, this is essentially the number of citations necessary to reach '
                     '<em>h,</em> plus the citations currently in the next paper outside of the core, plus the '
                     'minimum number of citations over <em>h</em> common to all publications within the core. It is '
                     'this last part that can make interpretation so difficult since a well over-cited core can lead '
                     'to very large increases in subsequent values of <em>H<sub>j</sub>.</em></p><p>The total '
                     'number of factors calculated (beyond <em>H</em><sub>0</sub>) can either be equal to '
                     f'<em>h</em>{NBMINUS}1 or the number of publication outside the Hirsch core (the citation tail), '
                     f'whichever is smaller.</p>')
    m.symbol = "<em>H<sub>j</sub></em>"
    m.example = write_hj_indices_example
    m.axis_name = r"$H_j$"
    m.references = ["Dorta-González, P., and M.I. Dorta-González (2010) Indicador bibliométrico basado en el "
                    "índice <em>h.</em> <em>Revista Española de Documentación Cientifica</em> 33(2):225&ndash;245."]
    m.draw_graph = Impact_Graphs.draw_graph_multiline_left_chart
    m.calculate = calculate_hj_indices
    m.properties["Multidimensional Metric"] = True
    m.properties["Core Property"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
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
    equation = r"$$v=100h^n=100\frac{h}{P}$$"
    m.description = ('<p>The v-index (Riikonen and Vihinen 2008) is the percentage of publications reflected in the '
                     f'__h-index__ (or the __normalized h-index__ expressed as a percent):</p>{equation}')
    m.references = ["Riikonen, P., and M. Vihinen (2008) National research contributions: A case study on Finnish "
                    "biomedical research. <em>Scientometrics</em> 77(2):207&ndash;222."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.symbol = "<em>v</em>"
    m.axis_name = r"$v$"
    m.calculate = calculate_v_index
    m.properties["Core Property"] = True
    m.properties["All Publications"] = True
    return m


# normalized h-index (Sidiropoulos et al. 2007)
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
    equation = r"$$h^n=\frac{h}{P}.$$"
    m.description = ('<p>The normalized <em>h-</em>index (Sidiropoulos et al. 2007) is simply the __h-index__ '
                     'divided by the number of publications (or the __v-index__ expressed as a proportion rather '
                     f'than a percentage):</p>{equation}')
    m.symbol = "<em>h<sup>n</sup></em>"
    m.axis_name = r"$h^n$"
    m.synonyms = ["<em>h<sup>n</sup></em>"]
    m.references = ["Sidiropoulos, A., D. Katsaros, and Y. Manolopoulos (2007) Generalized Hirsch <em>h-</em>index "
                    "for disclosing latent facts in citation networks. <em>Scientometrics</em> 72(2):253&ndash;280."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_normalized_h_index
    m.properties["Core Property"] = True
    m.properties["All Publications"] = True
    return m


# m-index (median index) (Bornmann et al. 2008)
def calculate_m_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    is_core = metric_set.is_core
    return Impact_Funcs.calculate_m_index(citations, is_core)


def metric_m_index() -> Metric:
    m = Metric()
    m.name = "m-index"
    m.full_name = "m-index"
    m.html_name = "<em>m-</em>index"
    m.symbol = "<em>m</em>"
    m.axis_name = r"$m$"
    m.metric_type = FLOAT
    m.description = ('<p>Similar to the __a-index__, the <em>m-</em>index (Bornmann <em>et al.</em> 2008) is '
                     'the median number of citations for papers in the __h-index__ core.</p>')
    m.references = ["Bornmann, L., R. Mutz, and H.-D. Daniel (2008) Are there better indices for evaluation purposes "
                    "than the <em>h</em> index? A comparison of nine different variants of the <em>h</em> index using "
                    "data from biomedicine. <em>Journal of the American Society for Information Science and "
                    "Technology</em> 59(5):830&ndash;837."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_m_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
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
    m.html_name = "<em>r<sub>m</sub>-</em>index"
    m.symbol = "<em>r<sub>m</sub></em>"
    m.axis_name = r"$r_m$"
    m.metric_type = FLOAT
    equation = r"$$r_m=\sqrt{\sum\limits_{i=1}^{h}{\sqrt{C_i}}}.$$"
    m.description = ('<p>The <em>r<sub>m</sub>-</em>index (Panaretos and Malesios 2009) is a modification of the '
                     '__R-index__, where one sums the square-root of the citations within the core rather than '
                     f'the total count:</p>{equation}')
    m.references = ["Panaretos, J., and C. Malesios (2009) Assessing scientific research performance and impact "
                    "with single indices. <em>Scientometrics</em> 81(3):635&ndash;670."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_rm_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# weighted h-index (Egghe and Rousseau 2008)
def calculate_weighted_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_weighted_h_index(citations, h)


def write_weighted_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    rows[3] = '<tr class="top_row"><th>Cumulative Citations (Σ<em>C<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th><em>r<sub>w</sub></em>(<em>i</em>) = Σ<em>C<sub>i</sub></em> / <em>h</em></th>'
    rows[5] = '<tr><th></th>'

    h = metric_set.metrics["h-index"].value
    hw = metric_set.metrics["weighted h-index"].value
    s = 0
    r0 = 0
    for i, c in enumerate(citations):
        s += c
        if s/h <= c:
            r0 += 1
    s = 0
    root_sum = 0
    for i, c in enumerate(citations):
        s += c
        v = ""
        v2 = ""
        ec = ""
        ec2 = ""
        if i + 1 == h:
            v = f'<em>h</em> = {h}'
            ec = ' class="dark_box"'
        if i + 1 == r0:
            v2 = f'<em>r</em><sub>0</sub>{NBEQ}{r0}'
            ec2 = ' class="box"'
            root_sum = s
        rows[0] += f'<td{ec}{ec2}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
        rows[3] += f'<td>{s}</td>'
        rows[4] += f'<td{ec2}>{s/h:0.2f}</td>'
        rows[5] += f'<td>{v2}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest rank where <em>r<sub>w</sub></em>(<em>i</em>) ≤ <em>C<sub>i</sub></em> is '
               f'{r0}. The weighted <em>h-</em>index is the square-root of the sum of citations up to this '
               f'rank, thus <em>h<sub>w</sub></em> = √{root_sum} = {hw:0.4f}</p>')
    return outstr


def metric_weighted_h_index() -> Metric:
    m = Metric()
    m.name = "weighted h-index"
    m.full_name = "weighted h-index"
    m.html_name = "weighted <em>h-</em>index"
    m.symbol = "<em>h<sub>w</sub></em>"
    m.axis_name = r"$h_w$"
    m.example = write_weighted_h_index_example
    m.metric_type = FLOAT
    rweq = r"$$r_w\left(i\right)=\frac{\sum\limits_{j=1}^{i}{C_j}}{h},$$"
    rwci = r"\(r_w\left(i\right)\leq C_i\)"
    r0 = r"$$r_0=\underset{i}{\max}\left(r_w\left(i\right)\leq C_i\right).$$"
    hweq = r"$$h_w=\sqrt{\sum\limits_{i=1}^{r_0}{C_i}},$$"
    m.description = ('<p>Similar to the __R-index__, the weighted <em>h-</em>index (Egghe and Rousseau 2008) is '
                     'designed to give more weight to publications within the core as they gain citations. The '
                     'primary difference is that for this metric the core is defined differently. Publications are '
                     'still ranked by citation count, but instead of using the raw rank, one uses a weighted rank '
                     f'of</p>{rweq}<p>that is, the weighted rank of the <em>i</em><sup>th</sup> publication is '
                     'the cumulative sum of citations for the top <em>i</em> publications, divided by the standard '
                     '<em>h-</em>index. With these weighted ranks, one finds the last publication in the weighted '
                     f'core, <em>r</em><sub>0</sub>, as the largest value of <em>i</em> where {rwci} '
                     '(the last publication for which the weighted rank of that publication is less than or equal to '
                     f'the number of citations for that publication):</p>{r0}<p>The weighted index is then '
                     f'calculated as{hweq}the square-root of the sum of citations for the weighted core.</p>')
    m.synonyms = ["<em>h<sub>w</sub></em>"]
    m.references = ["Egghe, L., and R. Rousseau (2008) An <em>h-</em>index weighted by citation impact. "
                    "<em>Information Processing and Management</em> 44:770&ndash;780."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_weighted_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# pi-index (Vinkler 2009)
def calculate_pi_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_pi_index(citations)


def write_pi_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    p = metric_set.metrics["total pubs"].value
    ppi = int(math.floor(math.sqrt(p)))
    pi = metric_set.metrics["pi-index"].value
    s = 0
    for i, c in enumerate(citations):
        if i + 1 <= ppi:
            ec = ' class="box"'
            s += c
        else:
            ec = ""
        if i + 1 == ppi:
            v = f'<em>P<sub>π</sub></em>{NBEQ}{ppi}'
        else:
            v = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The <em>π-</em>core is the floor of the square-root of the total number of publications, thus '
               f'<em>P<sub>π</sub></em> = floor(√{p}) = floor({math.sqrt(p):0.2f}) = {ppi}. '
               'The <em>π-</em>index is 1/100<sup>th</sup> of the sum of the citations within the <em>π-</em>core, '
               f'thus <em>π</em> = {s}/100 = {pi:0.2f}.</p>')
    return outstr


def metric_pi_index() -> Metric:
    m = Metric()
    m.name = "pi-index"
    m.full_name = "π-index"
    m.html_name = "<em>π-</em>index"
    m.symbol = "<em>π</em>"
    m.axis_name = r"$\pi$"
    m.metric_type = FLOAT
    m.example = write_pi_index_example
    ppistr = r"$$P_\pi=\text{floor}\left({\sqrt{P}}\right).$$"
    equation = r"$$\pi=\frac{C^\pi}{100}=\frac{\sum\limits_{i=1}^{P_\pi}{C_i}}{100}.$$"
    m.description = ('<p>The <em>π-</em>index (Vinkler 2009) is similar to other measures of the quality of the '
                     '__h-index__ core, except that it uses its own unique definition of the core. For this index, '
                     'the core publication set <em>P<sub>π</sub></em> is defined as the '
                     'square-root of the total number of publications, truncated down to the nearest integer '
                     '(<em>e.g.</em>, for 80 publications, the square-root of 80 is 8.944, so <em>P<sub>π</sub></em> '
                     f'would equal 8):</p>{ppistr}<p>The <em>π-</em>index is 1/100<sup>th</sup> of the total '
                     f'citations within this core:</p>{equation}')
    m.references = ["Vinkler, P. (2009) The <em>p-</em>index: A new indicator for assessing scientific impact. "
                    "<em>Journal of Information Science</em> 35(5):602&ndash;612."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pi_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# pi-rate
def calculate_pi_rate(metric_set: MetricSet) -> float:
    pi_index = metric_set.metrics["pi-index"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_pi_rate(total_pubs, pi_index)


def metric_pi_rate() -> Metric:
    m = Metric()
    m.name = "pi-rate"
    m.full_name = "π-core citation rate"
    m.html_name = "<em>π-</em>core citation rate"
    m.metric_type = FLOAT
    equation = (r"$$\pi\text{-rate}=\frac{C^\pi}{P_\pi}=\frac{\sum\limits_{i=1}^{P_\pi}C_i}{P_\pi}="
                r"\frac{100\pi_\text{index}}{\mathrm{floor}\left(\sqrt{P}\right)}$$")
    m.description = ('<p>The π-core citation rate, or π-rate, is related to the __pi-index__. It is the ratio of '
                     'the π-core citations divided by the number of publications in the π-core. It is simply the '
                     f'average number of citations per core publication.</p>{equation}')
    m.symbol = "<em>π-</em>rate"
    m.axis_name = r"$\pi\text{-rate}$"
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pi_rate
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# q2-index (Cabrerizo et al. 2010)
def calculate_q2_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    m = metric_set.metrics["m-index"].value
    return Impact_Funcs.calculate_q2_index(h, m)


def metric_q2_index() -> Metric:
    m = Metric()
    m.name = "q2-index"
    m.full_name = "q2-index"
    m.html_name = "<em>q</em><sup>2</sup>-index"
    m.symbol = "<em>q</em><sup>2</sup>"
    m.axis_name = r"$q^2$"
    m.metric_type = FLOAT
    equation = r"$$q^2=\sqrt{h\times m}.$$"
    m.description = ('<p>The <em>q</em><sup>2</sup>-index (Cabrerizo <em>et al.</em> 2010) is another metric '
                     'designed to describe the __h-index__ core. It is the geometric mean of both a quantitative '
                     f'(__h-index__) and a qualitative (__m-index__) measure of the core,</p>{equation}')
    m.references = ["Cabrerizo, F.J., S. Alonso, E. Herrera-Viedma, and F. Herrera (2010) "
                    "<em>q</em><sup>2</sup>-index: quantiative and qualitative evaluation based on the number and "
                    "impact of papers in the Hirsch core. <em>Journal of Informetrics</em> 4:23&ndash;28."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_q2_index
    m.properties["Core Property"] = True
    m.properties["Compound Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# e-index (Zhang 2009)
def calculate_e_index(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_e_index(core_cites, h)


# def write_e_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["e-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Tail', 'Center', 'Upper'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(1, maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x < h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         elif x == h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         else:
#             outstr += ", {}, null, null".format(tmp_cites[x - 1])
#         outstr += "],\n"
#         output.append(outstr)
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     isStacked: true,\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "ColumnChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def create_upper_center_tail_citation_graph_data(metric_set: MetricSet) -> list:
    """
    this identical figure is used for multiple metrics
    """
    output = []

    h = metric_set.metrics["h-index"].value

    # basic citation curve
    stack_data = Impact_Graphs.StackData()
    output.append(stack_data)
    n = len(metric_set.citations)
    stack_data.x = [i+1 for i in range(n)]
    cite_data = sorted(metric_set.citations, reverse=True)
    # create tail data
    tail = [0 for _ in range(h)]
    for i in range(h, n):
        tail.append(cite_data[i])
    stack_data.y["tail"] = tail
    # create center data
    center = [h for _ in range(h)]
    for i in range(h, n):
        center.append(0)
    stack_data.y["center (h-square)"] = center
    # create upper data
    upper = [cite_data[i]-h for i in range(h)]
    for i in range(h, n):
        upper.append(0)
    stack_data.y["upper"] = upper
    stack_data.labels = ["tail", "center (h-square)", "upper"]  # keep these as a list to maintain order
    maxc = max(cite_data)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc
    general_data.y_max = general_data.x_max

    return output


def metric_e_index() -> Metric:
    m = Metric()
    m.name = "e-index"
    m.full_name = "e-index"
    m.html_name = "<em>e-</em>index"
    m.symbol = "<em>e</em>"
    m.axis_name = r"$e$"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "e_index_desc"
    graph.data = create_upper_center_tail_citation_graph_data
    equation = r"$$e=\sqrt{C^H-h^2}=\sqrt{\sum\limits_{i=1}^{h}{C_i}-h^2}.$$"
    m.description = ('<p>The <em>e-</em>index (Zhang 2009) is simply a measure of the excess citations in the '
                     '__h-index__ core beyond those necessary to produce the core itself. It is measured as:</p>'
                     f'{equation}<p>Graphically, it is the square-root of the total citations within the upper '
                     'part of the citation curve.</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Zhang, C.-T. (2009) The <em>e-</em>index, complementing the <em>h-</em>index for excess "
                    "citations. <em>PLoS ONE</em> 4(5):e5429."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_e_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# h2-upper index (Bornmann et al. 2010)
def calculate_h2_upper_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_h2_upper_index(total_cites, core_cites, h)


# def write_h2_upper_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h2-upper index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Tail', 'Center', 'Upper'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(1, maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x < h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         elif x == h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         else:
#             outstr += ", {}, null, null".format(tmp_cites[x - 1])
#         outstr += "],\n"
#         output.append(outstr)
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     isStacked: true,\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "ColumnChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def metric_h2_upper_index() -> Metric:
    m = Metric()
    m.name = "h2-upper index"
    m.full_name = "h2-upper index"
    m.html_name = "<em>h</em><sup>2</sup>-upper index"
    m.symbol = r"\(h_\text{upper}^2\)"
    m.axis_name = r"$h_\text{upper}^2$"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h2_upper_index_desc"
    graph.data = create_upper_center_tail_citation_graph_data
    equation = (r"$$h_\text{upper}^2=\frac{C^H - h^2}{C^P}\times 100="
                r"\frac{\sum\limits_{i=1}^{h}{C_i} - h^2}{C^P}\times 100=\frac{e^2}{C^P}\times 100.$$")
    m.description = ('<p>The __h-index__ describes an <em>h</em>×<em>h</em> square under the citation curve '
                     'containing <em>h</em><sup>2</sup> citations. Bornmann <em>et al.</em> (2010) suggest dividing '
                     'the citation curve into three sections based on this square and describing each section as the '
                     'percent of all citations found within the section.</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure><p>The <em>h</em><sup>2</sup>-upper index is '
                     'the percent of excess citations found within the <em>h-</em>core citations, <em>i.e.</em>, '
                     f'the citations found above the <em>h-</em>square. It is related to the __e-index__, and '
                     f'is calculated as:{equation}')
    m.references = ["Bornmann, L., R. Mutz, and H.-D. Daniel (2010) The <em>h</em> index research output "
                    "measurement: Two approaches to enhance its accuracy. <em>Journal of Informetrics</em> "
                    "4:407&ndash;414."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h2_upper_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# h2-center index (Bornmann et al. 2010)
def calculate_h2_center_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_h2_center_index(total_cites, h)


# def write_h2_center_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h2-center index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Tail', 'Center', 'Upper'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(1, maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x < h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         elif x == h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         else:
#             outstr += ", {}, null, null".format(tmp_cites[x - 1])
#         outstr += "],\n"
#         output.append(outstr)
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     isStacked: true,\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "ColumnChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def metric_h2_center_index() -> Metric:
    m = Metric()
    m.name = "h2-center index"
    m.full_name = "h2-center index"
    m.html_name = "<em>h</em><sup>2</sup>-center index"
    m.symbol = r"\(h_\text{center}^2\)"
    m.axis_name = r"$h_\text{center}^2$"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h2_center_index_desc"
    graph.data = create_upper_center_tail_citation_graph_data
    equation = r"$$h_\text{center}^2=\frac{h^2}{C^P}\times 100$$"
    m.description = ('<p>The __h-index__ describes an <em>h</em>×<em>h</em> square under the citation curve '
                     'containing <em>h</em><sup>2</sup> citations. Bornmann <em>et al.</em> (2010) suggest dividing '
                     'the citation curve into three sections based on this square and describing each section as the '
                     'percent of all citations found within the section.</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>The <em>h</em><sup>2</sup>-center index is '
                     f'the percent of citations found within the <em>h-</em>square. It is calculated as:{equation}')
    m.references = ["Bornmann, L., R. Mutz, and H.-D. Daniel (2010) The <em>h</em> index research output "
                    "measurement: Two approaches to enhance its accuracy. <em>Journal of Informetrics</em> "
                    "4:407&ndash;414."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h2_center_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# h2-tail index (Bornmann et al. 2010)
def calculate_h2_tail_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    return Impact_Funcs.calculate_h2_tail_index(total_cites, core_cites)


# def write_h2_tail_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h2-tail index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Tail', 'Center', 'Upper'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(1, maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x < h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         elif x == h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         else:
#             outstr += ", {}, null, null".format(tmp_cites[x - 1])
#         outstr += "],\n"
#         output.append(outstr)
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     isStacked: true,\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "ColumnChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def metric_h2_tail_index() -> Metric:
    m = Metric()
    m.name = "h2-tail index"
    m.full_name = "h2-tail index"
    m.html_name = "<em>h</em><sup>2</sup>-tail index"
    m.symbol = r"\(h_\text{tail}^2\)"
    m.axis_name = r"$h_\text{tail}^2$"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h2_tail_index_desc"
    graph.data = create_upper_center_tail_citation_graph_data
    equation = r"$$h_\text{tail}^2=\frac{C^P - C^H}{C^P}\times 100=\frac{\sum\limits_{i=h+1}^{P}{C_i}}{C^P}\times 100$$"
    m.description = ('<p>The __h-index__ describes an <em>h</em>×<em>h</em> square under the citation curve '
                     'containing <em>h</em><sup>2</sup> citations. Bornmann <em>et al.</em> (2010) suggest dividing '
                     'the citation curve into three sections based on this square and describing each section as the '
                     'percent of all citations found within the section.</p>' 
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>The <em>h</em><sup>2</sup>-tail index is '
                     'the percent of citations found within the tail of the citation curve, <em>i.e.</em>, '
                     f'the citations of publications outside the <em>h-</em>core. It is calculated as:{equation}')
    m.references = ["Bornmann, L., R. Mutz, and H.-D. Daniel (2010) The <em>h</em> index research output "
                    "measurement: Two approaches to enhance its accuracy. <em>Journal of Informetrics</em> "
                    "4:407&ndash;414."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h2_tail_index
    m.properties["Tail Citations"] = True
    m.properties["Tail Publications"] = True
    return m


# k-index (Ye and Rousseau 2010)
def calculate_k_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_k_index(total_cites, core_cites, total_pubs)


def metric_k_index() -> Metric:
    m = Metric()
    m.name = "Ye and Rousseau k-index"
    m.full_name = "k-index (Ye and Rousseau)"
    m.html_name = "<em>k-</em>index (Ye and Rousseau)"
    m.symbol = "<em>k</em>"
    m.axis_name = r"$k$"
    m.metric_type = FLOAT
    equation = r"$$k=\frac{C^PC^h}{P\left(C^P-C^h\right)}.$$"
    m.description = ('<p>The <em>k-</em>index (Ye and Rousseau 2010) is a measure of the relative impact of '
                     'citations within the __h-index__ core to those in the tail. Specifically, it is the ratio of '
                     f'impact over the tail-core ratio and is calculated as</p>{equation}'
                     'This metric is specifically meant to be used in a time-series analysis where <em>k</em> is '
                     'calculated for multiple time points.</p>')
    m.references = ["Ye, F.Y., and R. Rousseau (2010) Probing the <em>h-</em>core: An investigation of the "
                    "tail-core ratio for rank distributions. <em>Scientometrics</em> 84(2):431&ndash;439."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_k_index
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Tail Citations"] = True
    m.properties["Tail Publications"] = True
    m.properties["Core Publications"] = True
    return m


# Prathap p-index (originally called mock hm-index) (Prathap 2010b, 2011)
def calculate_prathap_p_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_prathap_p_index(total_cites, total_pubs)


def metric_prathap_p_index() -> Metric:
    m = Metric()
    m.name = "p-index"
    m.full_name = "p-index (Prathap)"
    m.html_name = "<em>p-</em>index (Prathap)"
    m.symbol = "<em>p</em>"
    m.axis_name = r"$p$"
    m.metric_type = FLOAT
    equation = r"$$p=\sqrt[3]{\frac{\left(C^P\right)^2}{P}}.$$"
    m.description = ('<p>Also called the <span class="metric_name">mock <em>h<sub>m</sub>-</em>index</span> '
                     '(Prathap 2010b), the <em>p-</em>index '
                     '(Prathap 2010a) is derived from mathematical modeling of the relationship of increasing '
                     'numbers of publications and citations. It is a function of the total number of citations and '
                     f'the average citations per paper,</p>{equation}')
    m.synonyms = ["mock <em>h<sub>m</sub>-</em>index"]
    m.references = ["Prathap, G. (2010) The 100 most prolific economists using the <em>p-</em>index. "
                    "<em>Scientometrics</em> 84:167&ndash;172.",
                    "Prathap, G. (2010) Is there a place for a mock <em>h-</em>index? "
                    "<em>Scientometrics</em> 84:153&ndash;165."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_prathap_p_index
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
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
    m.symbol = "<em>ph-</em>ratio"
    m.axis_name = r"$ph\text{-ratio}$"
    m.metric_type = FLOAT
    m.description = ('<p>The __p-index__ can be considered a predictor of the __h-index__.</em> The ratio between '
                     '<em>p</em> and <em>h</em> (the <em>ph-</em>ratio) reflects the sensitivity of the value to the '
                     'proportion of citations in the upper core and the lower tail.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_ph_ratio
    m.properties["Core Property"] = True
    m.properties["Compound Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
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
    m.symbol = "<em>p<sub>f</sub></em>"
    m.axis_name = r"$p_f$"
    m.synonyms = ["<em>p<sub>f</sub></em>"]
    m.metric_type = FLOAT
    eq1 = r"$$C^{\prime}=\sum\limits_{i=1}^{P}{\frac{C_i}{A_i}}$$"
    eq2 = r"$$P^{\prime}=\sum\limits_{i=1}^{P}{\frac{1}{A_i}}$$"
    eq3 = r"$$p_f=\sqrt[3]{\frac{\left.C^{\prime}\right.^2}{P^{\prime}}}$$"
    m.description = ('<p>The fractional <em>p-</em>index (Prathap 2011) is a variant of the __p-index__ '
                     'which attempts to account for multiple-authored publications by adjusting both citation '
                     f'and publication counts by author counts. It is calculated as:</p>{eq1}{eq2}{eq3}')
    m.references = ["Prathap, G. (2011) The fractional and harmonic <em>p-</em>indices for multiple authorship. "
                    "<em>Scientometrics</em> 86:239&ndash;244."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_p_index_frac
    m.properties["Alternative Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# multidimensional h-index (Garcia-Perez 2009)
def calculate_multidimensional_h_index(metric_set: MetricSet) -> list:
    citations = metric_set.citations
    return Impact_Funcs.calculate_multidimensional_h_index(citations)


# def write_multidim_h_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["multidim h-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'h-squares'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     multih = metric_set.metrics["multidim h-index"].value
#     xpos = [multih[0]]
#     for h in multih[1:]:
#         xpos.append(h + xpos[len(xpos)-1])
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 20
#     # citation curve
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#             if v > maxv:
#                 v = "null"
#         outstr += ", {}, null],\n".format(v)
#         output.append(outstr)
#     # h-squares
#     xstart = 0
#     for h in multih:
#         xend = xstart + h
#         output.append("           [{}, null, {}],\n".format(xstart, h))
#         output.append("           [{}, null, {}],\n".format(xend, h))
#         output.append("           [{}, null, {}],\n".format(xend, 0))
#         output.append("           [null, null, null],\n")
#         xstart = xend
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def write_multidim_h_index_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest. Publications determined '
              'to be part of a core are removed for subsequent calcluations.</p>')
    citations = sorted(metric_set.citations, reverse=True)
    multi_h = metric_set.metrics["multidim h-index"].value
    outstr += '<table class="example_table">\n'
    skip = 0
    for j, h in enumerate(multi_h):
        rows = ["" for _ in range(3)]
        rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
        rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i < skip:
                rows[0] += '<td class="light_box"></td>'
                rows[1] += '<td class="light_box"></td>'
                rows[2] += '<td></td>'
            else:
                if i + 1 - skip == h:
                    v = f'<em>h</em><sub>{j+1}</sub>{NBEQ}{h}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                rows[0] += f'<td{ec}>{c}</td>'
                rows[1] += f'<td{ec}>{i+1-skip}</td>'
                rows[2] += f'<td>{v}</td>'
        skip += h
        for row in rows:  # add table row endings
            row += '</tr>\n'
        if j + 1 != len(multi_h):
            rows.append('<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>' + '</tr>\n')
            # row4 = '<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>' + '</tr>\n'
        # else:
        #     row4 = ""
        outstr += "".join(rows)
        # outstr += row1 + row2 + row3 + row4
    outstr += '</table>'
    return outstr


def create_multidim_h_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    multih = metric_set.metrics["multidim h-index"].value

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = []
    point_data.y = []
    h_old = 0
    for h in multih:
        point_data.x.append(h+h_old)
        point_data.y.append(h)
        h_old += h
    point_data.fillcolor = "none"

    # square lines
    square_data = Impact_Graphs.LineData()
    output.append(square_data)
    square_data.x = []
    square_data.y = []
    h_old = 0
    for h in multih:
        square_data.x.extend([h_old, h_old, h+h_old, h+h_old, h_old, None])
        square_data.y.extend([0, h, h, 0, 0, None])
        h_old += h
    square_data.style = ":"
    square_data.label = r"$h\text{-squares}$"

    # # annotation
    h_old = 0
    n = len(multih) + 1
    for i, h in enumerate(multih):
        annotation = Impact_Graphs.AnnotationData()
        output.append(annotation)
        annotation.label = f"$h_{i+1} = {h}$"
        annotation.pos = (h+h_old, h)
        annotation.textpos = (h+h_old+5, h+n)
        h_old += h
        n -= 1

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = 18
    general_data.y_max = general_data.x_max

    return output


def metric_multdim_h_index() -> Metric:
    m = Metric()
    m.name = "multidim h-index"
    m.full_name = "multidimensional h-index"
    m.html_name = "multidimensional <em>h-</em>index"
    m.symbol = "<strong><em>H</em></strong>"
    m.axis_name = r"$h$"
    m.metric_type = LIST
    m.list_formats = INT
    m.example = write_multidim_h_index_example
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "multidim_h_index_desc"
    graph.data = create_multidim_h_index_desc_graph_data
    m.description = ('<p>The multidimensional <em>h-</em>index (García-Pérez 2009) is a simple expansion of the '
                     'original __h-index__ used to separate individuals with identical <em>h-</em>indices. The '
                     'concept is to calculate the <em>h-</em>index from all <em>P</em> publications (this would be '
                     'the first <em>h-</em>index or <em>h</em><sub>1</sub>). One can then calculate a second '
                     '<em>h</em>-index, <em>h</em><sub>2</sub>, from the <em>P</em> – <em>h</em><sub>1</sub> '
                     'remaining publications. Graphically, this is finding the largest square which can fit in the '
                     'tail to the right of the original square represented by <em>h</em><sub>1</sub>. A third, '
                     '<em>h</em><sub>3</sub>, can be calculated from the <em>P</em> – <em>h</em><sub>1</sub> – '
                     '<em>h</em><sub>2</sub> remaining publications, etc., continuing until one reaches '
                     'publications with 0 citations.</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure><p>It should be obvious that <em>h</em><sub>1</sub> ≥ '
                     '<em>h</em><sub>2</sub> ≥ <em>h</em><sub>3</sub>…</p><p>Unlike most of the other indices, this '
                     'index set is primarily focused on the tail of the distribution, ignoring the excess/upper '
                     'part of the citation curve completely. Because it is simply recalculating <em>h</em> for a '
                     'smaller data set, its interpretation is quite straightforward and certainly could serve as '
                     'a solid method of distinguishing individuals with identical <em>h.</em></p>')
    m.references = ["García-Pérez, M.A. (2009) A multidimensional extension to Hirsch\'s <em>h-</em>index. "
                    "<em>Scientometrics</em> 81(3):779&ndash;785."]
    m.draw_graph = Impact_Graphs.draw_graph_multiline_left_chart
    m.calculate = calculate_multidimensional_h_index
    m.properties["Multidimensional Metric"] = True
    m.properties["Core Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# two-sided h-index (Garcia-Perez 2012)
def calculate_two_sided_h_index(metric_set: MetricSet) -> list:
    citations = metric_set.citations
    multidim_h = metric_set.metrics["multidim h-index"].value
    return Impact_Funcs.calculate_two_sided_h(citations, multidim_h)


# def write_two_sided_h_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["two-sided h-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'h-squares'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 40
#     # citation curve
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#             if v > maxv:
#                 v = "null"
#         outstr += ", {}, null],\n".format(v)
#         output.append(outstr)
#     # h-squares
#     twosided_h = metric_set.metrics["two-sided h-index"].value
#     midh = len(twosided_h) // 2
#     xstart = 0
#     for h in twosided_h[midh:]:
#         xend = xstart + h
#         output.append("           [{}, null, {}],\n".format(xstart, h))
#         output.append("           [{}, null, {}],\n".format(xend, h))
#         output.append("           [{}, null, {}],\n".format(xend, 0))
#         output.append("           [null, null, null],\n")
#         xstart = xend
#     h = twosided_h[midh]
#     ystart = h
#     rev_h = twosided_h[::-1]
#     for h in rev_h[midh+1:]:
#         yend = ystart + h
#         output.append("           [{}, null, {}],\n".format(0, yend))
#         output.append("           [{}, null, {}],\n".format(h, yend))
#         output.append("           [{}, null, {}],\n".format(h, ystart))
#         output.append("           [null, null, null],\n")
#         ystart = yend
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output

def create_two_sided_h_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    twosided_h = metric_set.metrics["two-sided h-index"].value
    midh = len(twosided_h) // 2

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"

    # example points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = []
    point_data.y = []
    h_old = 0
    for h in twosided_h[midh:]:
        point_data.x.append(h+h_old)
        point_data.y.append(h)
        h_old += h
    h_old = twosided_h[midh]
    for h in twosided_h[midh-1::-1]:
        point_data.x.append(h)
        point_data.y.append(h+h_old)
        h_old += h
    point_data.fillcolor = "none"

    # square lines
    square_data = Impact_Graphs.LineData()
    output.append(square_data)
    square_data.x = []
    square_data.y = []
    # center and tail h's
    h_old = 0
    for h in twosided_h[midh:]:
        square_data.x.extend([h_old, h_old, h+h_old, h+h_old, h_old, None])
        square_data.y.extend([0, h, h, 0, 0, None])
        h_old += h
    # upper h's
    h_old = twosided_h[midh]
    for h in twosided_h[midh-1::-1]:
        square_data.x.extend([0, 0, h, h, 0, None])
        square_data.y.extend([h_old, h+h_old, h+h_old, h_old, h_old, None])
        h_old += h
    square_data.style = ":"
    square_data.label = r"$h\text{-squares}$"

    # annotation
    h_old = 0
    n = twosided_h[midh] + midh + 1
    for i, h in enumerate(twosided_h[midh:]):
        annotation = Impact_Graphs.AnnotationData()
        output.append(annotation)
        annotation.label = f"$h_{i} = {h}$"
        annotation.pos = (h+h_old, h)
        # annotation.textpos = (h+h_old+8, h+n)
        annotation.textpos = (h+h_old+8, n)
        h_old += h
        n -= 2
    h_old = twosided_h[midh]
    i = -1
    n = midh + 3
    for h in twosided_h[midh-1::-1]:
        annotation = Impact_Graphs.AnnotationData()
        output.append(annotation)
        # annotation.label = f"$h_{i} = {h}$"
        annotation.label = "$h_{" + str(i) + "}" + f" = {h}$"
        annotation.pos = (h, h+h_old)
        annotation.textpos = (h+n, h+h_old+5)
        h_old += h
        i -=1
        n -= 1


    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = 25
    general_data.y_max = general_data.x_max

    return output


def write_two_sided_h_index_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest. Publications within the '
              'original core have <em>h</em> citations removed at each step; publications in the original tail are '
              'ranked independently at each subsequent step.</p>')
    citations = sorted(metric_set.citations, reverse=True)
    two_sided_h = metric_set.metrics["two-sided h-index"].value
    nsteps = len(two_sided_h) // 2
    outstr += '<table class="example_table">\n'
    # first row is standard h
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = two_sided_h[nsteps]
    for i, c in enumerate(citations):
        if i + 1 == h:
            v = f'<em>h</em><sub>0</sub>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows)
    tail_skip = h
    core_skip = h
    oldhm = h
    for j in range(1, nsteps + 1):
        rows = ["" for _ in range(4)]
        hp = two_sided_h[nsteps + j]
        hm = two_sided_h[nsteps - j]
        rows[0] = '<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>'
        rows[1] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
        rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[3] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i < tail_skip:
                if i >= oldhm:
                    rows[1] += '<td class="light_box"></td>'
                    rows[2] += '<td class="light_box"></td>'
                    rows[3] += '<td></td>'
                else:
                    if i + 1 == hm:
                        v = f'<em>h</em><sub>{-j}</sub>{NBEQ}{hm}'
                        ec = ' class="box"'
                    else:
                        v = ""
                        ec = ""
                    rows[1] += f'<td{ec}>{max(0, c-core_skip)}</td>'
                    rows[2] += f'<td{ec}>{i+1}</td>'
                    rows[3] += f'<td>{v}</td>'
            else:
                if (j == 1) and (i == h):
                    ec2 = ' class="left_border"'
                else:
                    ec2 = ""
                if i + 1 - tail_skip == hp:
                    v = f'<em>h</em><sub>{j}</sub>{NBEQ}{hp}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                if (ec2 != "") and (ec != ""):
                    ec = ' class="box left_border"'
                    ec2 = ""
                rows[1] += f'<td{ec}{ec2}>{c}</td>'
                rows[2] += f'<td{ec}{ec2}>{i+1-tail_skip}</td>'
                rows[3] += f'<td>{v}</td>'
        tail_skip += hp
        core_skip += hm
        oldhm = hm

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>'
    return outstr


def metric_two_sided_h_index() -> Metric:
    m = Metric()
    m.name = "two-sided h-index"
    m.full_name = "two-sided h-index"
    m.html_name = "two-sided <em>h-</em>index"
    m.symbol = "<em>h</em>±<em>k</em>"
    m.axis_name = r"$h$"
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "two_sided_h_index_desc"
    graph.data = create_two_sided_h_index_desc_graph_data
    m.example = write_two_sided_h_index_example
    m.metric_type = LIST
    m.list_formats = INT
    m.description = ('<p>The two-sided <em>h-</em>index (García-Pérez 2012) is an extension of the '
                     '__multidim h-index__, which recalcultes <em>h</em> not only for the tail of the distribution '
                     '(as in the multidimensional version) but also for the excess citations from <em>h-</em>core '
                     'publications beyond those necessary to reach <em>h,</em> thus providing a multidimensional '
                     'measure of both the upper and tail parts of the citation distribution.</p><p>The tail half of '
                     'the two-sided <em>h-</em>index is identical to the multidimensional <em>h-</em>index '
                     '(although, notationally, the original <em>h</em> is now designated <em>h</em><sub>0</sub>). To '
                     'calculate the upper part, after the initial <em>h</em> is determined, one calculates '
                     '<em>h</em><sub>-1</sub> (the value immediately in front of <em>h</em>) by first subtracting '
                     '<em>h</em> from the citation count for all of the publications in the core, then determining a '
                     'new <em>h</em> from this reduced citation set.</p>'                     
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure><p>Graphically, this is finding the largest square '
                     'which can fit on top of the original square representing <em>h.</em> This process is repeated '
                     'for the remaining excess citations in the (new) core.</p><p>To ensure symmetry, '
                     'we calculate <em>h</em>±<em>k</em> such that the number of steps above the core is identical to '
                     'the number of steps in the tail.</p>')
    m.references = ["García-Pérez, M.A. (2012) An extension of the <em>h</em> index that covers the tail and the "
                    "top of the citation curve and allows ranking researchers with similar <em>h.</em> <em>Journal of "
                    "Informetrics</em> 6:689&ndash;699."]
    m.draw_graph = Impact_Graphs.draw_graph_multiline_center_chart
    m.calculate = calculate_two_sided_h_index
    m.properties["Core Metric"] = True
    m.properties["Multidimensional Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# iteratively weighted h-index (Todeschini and Baccini 2016)
def calculate_iter_weighted_h_index(metric_set: MetricSet) -> float:
    multidim_h = metric_set.metrics["multidim h-index"].value
    return Impact_Funcs.calculate_iteratively_weighted_h_index(multidim_h)


def metric_iter_weighted_h_index() -> Metric:
    m = Metric()
    m.name = "iter weighted h-index"
    m.full_name = "iteratively weighted h-index"
    m.html_name = "iteratively weighted <em>h-</em>index"
    m.symbol = "<em>iw</em>(<em>h</em>)-index"
    m.axis_name = r"$iw\left(h\right)$"
    m.metric_type = FLOAT
    equation = r"$$iw\left(h\right)=\sum\limits_{j=1}^{n}{\frac{h_j}{j}}.$$"
    m.description = ('<p>The interatively weighted <em>h-</em>index (Todeschini and Baccini 2016) is a method '
                     'for producing a single global index from the vector produced by the __multidim h-index__ '
                     f'(<strong><em>H</em></strong>). This index is calculated as:</p>{equation}'
                     '<p>where <em>h<sub>j</sub></em> and <em>n</em> are the <em>j</em><sup>th</sup> value and total '
                     'length of <strong><em>H</em></strong>, respectively.</p>')
    m.references = ["Todeschini, R., and A. Baccini (2016) <em>Handbook of Bibliometric Indicators: Quantitative "
                    "Tools for Studying and Evaluating Research.</em> Weinheim, Germany: Wiley."]
    m.synonyms = ["<em>iw</em>(<em>h</em>)-index"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_iter_weighted_h_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# EM-index (Bihari and Tripathi 2017)
def calculate_em_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_em_index(citations)


def write_em_index_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'publications. All publications beyond the top <em>E<sub>i</sub></em> are ignored at subsequent '
              'steps.</p>')
    citations = sorted(metric_set.citations, reverse=True)
    # calculate vector
    em_components = Impact_Funcs.calculate_em_components(citations)
    outstr += '<table class="example_table">\n'
    oldh = len(citations)
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>')
        rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i >= oldh:
                rows[0] += '<td class="light_box"></td>'
                rows[1] += '<td class="light_box"></td>'
                rows[2] += '<td></td>'
            else:
                if i + 1 == h:
                    v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                rows[0] += f'<td{ec}>{c}</td>'
                rows[1] += f'<td{ec}>{i+1}</td>'
                rows[2] += f'<td>{v}</td>'
        citations = [max(0, c-h) for c in citations]
        oldh = h
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)

    outstr += '</table>'
    em = metric_set.metrics["EM-index"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. The '
               f'<em>EM-</em>index is the square-root of this sum, thus <em>EM</em>{NBEQ}{em:0.4f}.</p>')
    return outstr


def metric_em_index() -> Metric:
    m = Metric()
    m.name = "EM-index"
    m.full_name = "EM-index"
    m.html_name = "<em>EM-</em>index"
    m.symbol = "<em>EM</em>"
    m.axis_name = r"$EM$"
    m.example = write_em_index_example
    m.metric_type = FLOAT
    equation = r"$$EM=\sqrt{\sum\limits_{i=1}^{n}{E_i}},$$"
    m.description = ('<p>The <em>EM-</em>index (Bihaari and Tripathi 2017) combines elements of the '
                     '__multidim h-index__, the __two-sided h-index__, the __iter weighted h-index__, '
                     'and the __e-index__. The <em>EM-</em>index begins by creating a vector '
                     '(<strong><em>E</em></strong>) which is equivalent to '
                     'the upper/excess half of the two-sided <em>h-</em>index, namely a series of <em>h</em> values '
                     'calculated from the citation curve of just the core publications, stopping when one reaches '
                     'only a single remaining publication, no citations remain, or all remaining publications have '
                     'only a single citation. From this vector, <em>EM</em> can be calculated as:</p>'
                     f'{equation}<p>where <em>E<sub>i</sub></em> and <em>n</em> are the <em>i</em><sup>th</sup> '
                     'element and length of <strong><em>E</em></strong>, respectively.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2017) EM-index: A new measure to evaluate the scientific impact "
                    "of scientists. <em>Scientometrics</em> 112(1):659&ndash;677."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_em_index
    m.properties["Alternative Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# EM'-index (Bihari and Tripathi 2017)
def calculate_emp_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_emp_index(citations)


def write_emp_index_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'publications and all publications are re-ranked by this adjusted citation count for the next step.</p>')
    citations = sorted(metric_set.citations, reverse=True)
    em_components = Impact_Funcs.calculate_emp_components(citations)
    outstr += '<table class="example_table">\n'
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>New Rank (<em>i</em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>')
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i + 1 == h:
                v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[0] += f'<td{ec}>{c}</td>'
            rows[1] += f'<td{ec}>{i+1}</td>'
            rows[2] += f'<td>{v}</td>'
        for i in range(h):
            citations[i] -= h
        citations.sort(reverse=True)
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>'
    emp = metric_set.metrics["EMp-index"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. '
               f'The <em>EM&prime;-</em>index is the square-root of this sum, thus '
               f'<em>EM</em>&prime;{NBEQ}{emp:0.4f}.</p>')
    return outstr


def metric_emp_index() -> Metric:
    m = Metric()
    m.name = "EMp-index"
    m.full_name = "EM\'-index"
    m.html_name = "<em>EM</em>&prime;-index"
    m.symbol = "<em>EM&prime;</em>"
    m.axis_name = r"$EM^{\prime}$"
    m.example = write_emp_index_example
    m.metric_type = FLOAT
    equation = r"$$EM^\prime=\sqrt{\sum\limits_{i=1}^{n}{E_i}},$$"
    m.description = ('<p>The <em>EM</em>&prime;-index (Bihari and Tripathi 2017) is an extension of the '
                     '__EM-index__ which includes all publications, rather than just those from the core. Like '
                     'the <em>EM-</em>index, we begin by creating a vector (<strong><em>E</em></strong>) where the '
                     'first value is <em>E</em><sub>1</sub> = <em>h.</em> Subsequent values of the vector, '
                     '<em>E</em><sub>i+1</sub>, are determined by subtracting <em>E</em><sub>i</sub> from the '
                     'citation count for all publications in the core defined by <em>E</em><sub>i</sub>, and '
                     'recalculating <em>h</em> from these new citation counts, reranking all publications by these '
                     'new citation counts as necessary (<em>i.e.</em>, some of the publications previously in the '
                     'tail of the citation distribution may advance beyond publications in the core as citations '
                     'representing earlier calculations of <em>h</em> are &ldquo;used up&rdquo;). This process '
                     'continues until one runs out of citations, all of the remaining publications have only a '
                     'single remaining citation, or there is only a single publication left to be considered. From '
                     f'this vector, one calculates the index as:</p>{equation}<p>where <em>E<sub>i</sub></em> and '
                     f'<em>n</em> are the <em>i</em><sup>th</sup> element and length of <strong><em>E</em></strong>, '
                     'respectively.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2017) EM-index: A new measure to evaluate the scientific impact "
                    "of scientists. <em>Scientometrics</em> 112(1):659&ndash;677."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_emp_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# iterative weighted EM-index (Bihari et al. 2021)
def calculate_iterative_weighted_em_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_iterative_weighted_em_index(citations)


def write_iterative_weighted_em_index_example(metric_set: MetricSet) -> str:
    def count_cited(tmpc: list) -> int:
        cnt = 0
        for cc in tmpc:
            if cc > 0:
                cnt += 1
        return cnt

    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> publications. '
              'All publications beyond the top <em>E<sub>i</sub></em> are ignored at subsequent steps.</p>')
    citations = sorted(metric_set.citations, reverse=True)
    em_components = Impact_Funcs.calculate_em_components(citations)
    outstr += '<table class="example_table">\n'
    oldh = len(citations)
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>')
        rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i >= oldh:
                rows[0] += '<td class="light_box"></td>'
                rows[1] += '<td class="light_box"></td>'
                rows[2] += '<td></td>'
            else:
                if i + 1 == h:
                    v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                rows[0] += f'<td{ec}>{c}</td>'
                rows[1] += f'<td{ec}>{i+1}</td>'
                rows[2] += f'<td>{v}</td>'
        citations = [max(0, c-h) for c in citations]
        oldh = h
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>'
    em = metric_set.metrics["iterative weighted EM-index"].value
    em_out = ["{}/{}".format(em_components[i], i+1) for i in range(len(em_components))]
    outstr += ('<p><em>iw<sub>EM</sub></em> is the sum of each component of <em>E</em> weighted by it\'s order, '
               'thus <em>iw<sub>EM</sub></em> = ' + " + ".join(em_out) + f' = {em:0.4f}')
    return outstr


def metric_iterative_weighted_em_index() -> Metric:
    m = Metric()
    m.full_name = "iterative weighted EM-index"
    m.name = "iterative weighted EM-index"
    m.html_name = "iterative weighted <em>EM-</em>index"
    m.symbol = "<em>iw<sub>EM</sub></em>"
    m.axis_name = r"$iw_{EM}$"
    m.synonyms = ["<em>iw<sub>EM</sub></em>"]
    m.example = write_iterative_weighted_em_index_example
    m.metric_type = FLOAT
    equation = r"$$iw_{EM}=\sum\limits_{i=1}^{n}\frac{E_i}{i},$$"
    m.description = ('<p>The iterative weighted <em>EM-</em>index (Bihari <em>et al.</em> 2021) is a modification of '
                     'the __EM-index__ which uses a weighted-sum of each successive element in the vector '
                     'rather than the square-root of the sum. The index begins by creating a vector '
                     '(<strong><em>E</em></strong>) which is equivalent to '
                     'the upper/excess half of the __two-sided h-index__, namely a series of __h-index__ values '
                     'calculated from the citation curve of just the core publications, stopping when one reaches '
                     'only a single remaining publication, no citations remain, or all remaining publications have '
                     'only a single citation. From this vector, <em>iw<sub>EM</sub></em> can be calculated as:</p>'
                     f'{equation}<p>where <em>E<sub>i</sub></em> and <em>n</em> are the <em>i</em><sup>th</sup> '
                     'element and length of <strong><em>E</em></strong>, respectively.</p>')
    m.references = ["Bihari, A., S. Tripathi, and A. Deepak (2021) Iterative weighted EM and iterative weighted "
                    "EM′-index for scientific assessment of scholars. <em>Scientometrics</em> 126:5551&ndash;5568."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_iterative_weighted_em_index
    m.properties["Alternative Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# iterative weighted EM'-index (Bihari et al. 2021)
def calculate_iterative_weighted_emp_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_iterative_weighted_emp_index(citations)


def write_iterative_weighted_emp_index_example(metric_set: MetricSet) -> str:
    def count_cited(tmpc: list) -> int:
        cnt = 0
        for cc in tmpc:
            if cc > 0:
                cnt += 1
        return cnt

    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'publications and all publications are re-ranked by this adjusted citation count for the next step.</p>')
    citations = sorted(metric_set.citations, reverse=True)
    em_components = Impact_Funcs.calculate_emp_components(citations)
    outstr += '<table class="example_table">\n'
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>New Rank (<em>i</em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(citations)*'<td></td>')
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i + 1 == h:
                v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[0] += f'<td{ec}>{c}</td>'
            rows[1] += f'<td{ec}>{i+1}</td>'
            rows[2] += f'<td>{v}</td>'
        for i in range(h):
            citations[i] -= h
        citations.sort(reverse=True)
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>'
    emp = metric_set.metrics["iterative weighted EMp-index"].value
    em_out = ["{}/{}".format(em_components[i], i+1) for i in range(len(em_components))]
    outstr += ('<p><em>iw<sub>EM&prime;</sub></em> is the sum of each component of <em>E</em> weighted by it\'s '
               'order, thus <em>iw<sub>EM&prime;</sub></em> = ' + ' + '.join(em_out) + f' = {emp:0.4f}')
    return outstr


def metric_iterative_weighted_emp_index() -> Metric:
    m = Metric()
    m.name = "iterative weighted EMp-index"
    m.full_name = "iterative weighted EM\'-index"
    m.html_name = "iterative weighted <em>EM</em>&prime;-index"
    m.symbol = "<em>iw<sub>EM&prime;</sub></em>"
    m.axis_name = r"$iw_{EM\prime}$"
    m.synonyms = ["<em>iw<sub>EM&prime;</sub></em>"]
    m.example = write_iterative_weighted_emp_index_example
    m.metric_type = FLOAT
    equation = r"$$iw_{EM^\prime}= \sum\limits_{i=1}^{n}\frac{E_i}{i},$$"
    m.description = ('<p>The iterative weighted <em>EM&prime;-</em>index (Bihari <em>et al.</em> 2021) is a '
                     'modification of the __EMp-index__ (Bihari and Tripathi 2017) which uses a '
                     'weighted-sum of each successive element in the vector rather than the square-root of the sum. '
                     'It is an extension of the __iterative weighted EM-index__ '
                     'which includes all publications, rather than just those from the core. '
                     'We begin by creating a vector (<strong><em>E</em></strong>) where the '
                     'first value is <em>E</em><sub>1</sub> = <em>h.</em> Subsequent values of the vector, '
                     '<em>E</em><sub>i+1</sub>, are determined by subtracting <em>E</em><sub>i</sub> from the '
                     'citation count for all publications in the core defined by <em>E</em><sub>i</sub>, and '
                     'recalculating <em>h</em> from these new citation counts, reranking all publications by these '
                     'new citation counts as necessary (<em>i.e.</em>, some of the publications previously in the '
                     'tail of the '
                     'citation distribution may advance beyond publications in the core as citations representing '
                     'earlier calculations of <em>h</em> are &ldquo;used up&rdquo;). This process continues until '
                     'one runs out of citations, all of the remaining publications have only a single remaining '
                     'citation, or there is only a single publication left to be considered. From this vector, '
                     f'one calculates the index as:</p>{equation}<p>where <em>E<sub>i</sub></em> and <em>n</em> '
                     'are the <em>i</em><sup>th</sup> element and length of <strong><em>E</em></strong>, '
                     'respectively.</p>')
    m.references = ["Bihari, A., S. Tripathi, and A. Deepak (2021) Iterative weighted EM and iterative weighted "
                    "EM′-index for scientific assessment of scholars. <em>Scientometrics</em> 126:5551&ndash;5568."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_iterative_weighted_emp_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# total self citations
def calculate_total_self_cites(metric_set: MetricSet) -> int:
    self_citations = metric_set.self_citations
    return Impact_Funcs.calculate_total_self_cites(self_citations)


def metric_total_self_cites() -> Metric:
    m = Metric()
    m.name = "total self cites"
    m.full_name = "total self citations"
    m.symbol = "S"
    m.axis_name = r"$S$"
    m.metric_type = INT
    m.is_self = True
    equation = r"$$S = \sum\limits_{i=1}^{P}{s_i}.$$"
    m.description = ('<p>The total number of self citations is simply the number of citations to all of an '
                     'author\'s publications made by other publications from the same author. If '
                     '<em>s<sub>i</sub></em> is the number of self citations an author has made to their '
                     f'<em>i</em><sup>th</sup> publication then</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_self_cites
    m.properties["Basic Statistic"] = True
    m.properties["Self-Citation"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
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
    m.symbol = "<em>S<sub>r</sub></em>"
    m.axis_name = r"$S_r$"
    m.metric_type = FLOAT
    m.is_self = True
    equation = r"$$S_r=\frac{S}{C^P}=\frac{\sum\limits_{i=1}^{P}{s_i}}{\sum\limits_{i=1}^{P}{C_i}}.$$"
    m.description = ('<p>The total self-citation rate is the ratio bewtween __total self cites__ (the number of '
                     'citations to all of an author\'s publications made by other publications from the same author)'
                     f' versus the total number of citations to all of the author\'s publications or</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_self_cite_rate
    m.properties["Basic Statistic"] = True
    m.properties["Self-Citation"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
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
    m.symbol = r"\(\bar{S_r}\)"
    m.metric_type = FLOAT
    m.is_self = True
    equation = r"$$\bar{S_r}=\frac{1}{P}\sum\limits_{i=1}^{P}{\frac{s_i}{C_i}}$$"
    m.description = ('<p>The mean self-citation rate is the average rate of self-citation for an author across '
                     'all of their publications. It differs from the __total self cite rate__ in that the total '
                     f'is based on the ratio of the sums while the average is based on the sums of the '
                     f'ratios.</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_mean_self_cite_rate
    m.properties["Basic Statistic"] = True
    m.properties["Self-Citation"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# sharpened h-index (Schreiber 2007)
def calculate_sharpened_h_index_self(metric_set: MetricSet) -> float:
    all_citations = metric_set.citations
    self_citations = metric_set.self_citations
    return Impact_Funcs.calculate_sharpened_h_index(self_citations, all_citations)


def metric_sharpened_h_index_self() -> Metric:
    m = Metric()
    m.name = "sharpened h-index (narrow)"
    m.full_name = "sharpened h-index (narrow)"
    m.html_name = "sharpened <em>h-</em>index (narrow)"
    m.symbol = "<em>h</em><sub>sharp.self</sub>"
    m.metric_type = INT
    m.is_self = True
    m.description = ('<p>A simple way of accounting for self-citations with respect to impact is to simply remove '
                     'them from each publication\'s citation counts prior to calculating a metric. For the base '
                     'calculation of the __h-index__ this is known as the sharpened <em>h-</em>index '
                     '(Schreiber 2007).</p>'
                     '<p>One complication is that there may be multiple methods for defining self-citations. In this '
                     'case we use a narrow definition and only remove citations by the focal author to their own '
                     'publications.</p>')
    m.references = ["Schreiber, M. (2007) Self-citation corrections for the Hirsch index. <em>Europhysics "
                    "Letters</em> 78:30002-1&ndash;6."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_sharpened_h_index_self
    m.properties["Core Metric"] = True
    m.properties["Self-Citation"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
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
    m.symbol = "<em>b</em><sub>mean.self</sub>"
    m.metric_type = FLOAT
    m.is_self = True
    equation = r"$$b=hk^{\frac{3}{4}},$$"
    req = r"$$k=1-\bar{S_r}=1-\frac{\sum\limits_{i=1}^{P}{\frac{s_i}{C_i}}}{P}$$"
    m.description = ('<p>The <em>b-</em>index (Brown 2009) is designed to correct the __h-index__ for self-citations, '
                     'without actually having to check the citation records for every publication. It assumes that '
                     'an author\'s self-citation rate is fairly consistent across publications such that, on average, '
                     'a fraction <em>k</em> of the citations are from other authors. Assuming that citations follow '
                     'a Zipfian distribution and that empirically derived estimates of the shape of this distribution '
                     f'are reasonable, one finds the index</p>{equation}<p>where <em>b</em> is an estimate of '
                     'the <em>h-</em>index corrected for self-citations.</p><p>There are multiple ways to estimate '
                     'the non-self-citation rate (<em>k</em>). In this case, we calculate it directly as the mean of '
                     'the proportion of self-citations to total-citations across all publication, subtracted from '
                     f'one, or</p>{req}<p>where <em>s<sub>i</sub></em> is the number of self-citations by the '
                     'target author to the <em>i</em><sup>th</sup> publication.</p>')
    m.references = ["Brown, R.J.C. (2009) A simple method for excluding self-citation from the <em>h-</em>index: "
                    "the <em>b-</em>index. <em>Online Information Review</em> 33(6):1129&ndash;1136."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_b_index_mean_self
    m.properties["Core Metric"] = True
    m.properties["Self-Citation"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


"""
I have commented out all of the coauthor-citation based metrics because the data is too complicated to collect
to be worth keeping up to date
"""

# # total self & coauthor citations
# def calculate_total_coauthor_cites(metric_set: MetricSet) -> int:
#     coauthor_citations = metric_set.self_coauthor_citations()
#     return Impact_Funcs.calculate_total_self_cites(coauthor_citations)
#
#
# def metric_total_coauthor_cites() -> Metric:
#     m = Metric()
#     m.name = "total coauthor cites"
#     m.full_name = "total self & coauthor citations"
#     m.html_name = "total self &amp; coauthor citations"
#     m.symbol = "S"
#     m.metric_type = INT
#     m.is_coauthor = True
#     equation = r"$$S = \sum\limits_{i=1}^{P}{s_i}.$$"
#     m.description = "<p>The total number of self- and coauthor-citations is simply the number of citations to all " \
#                     "of an author\'s publications made by other publications from the same author and coauthors. If "
#                     "<em>s<sub>i</sub></em> is the number of self citations an author and coauthors have made to " \
#                     "their <em>i</em><sup>th</sup> publication then</p>" + equation
#     m.draw_graph = Impact_Graphs.draw_graph_line_chart
#     # m.graph_type = LINE_CHART
#     m.calculate = calculate_total_coauthor_cites
#     return m
#
#
# # total self & coauthor-citation rate
# def calculate_total_coauthor_cite_rate(metric_set: MetricSet) -> float:
#     total_coauthor_cites = metric_set.metrics["total coauthor cites"].value
#     total_cites = metric_set.metrics["total cites"].value
#     return Impact_Funcs.calculate_total_self_cite_rate(total_coauthor_cites, total_cites)
#
#
# def metric_total_coauthor_cite_rate() -> Metric:
#     m = Metric()
#     m.name = "total coauthor cite rate"
#     m.full_name = "total self & coauthor-citation rate"
#     m.html_name = "total self &amp; coauthor-citation rate"
#     m.symbol = "<em>S<sub>r</sub></em>"
#     m.metric_type = FLOAT
#     m.is_coauthor = True
#     equation = r"$$S_r=\frac{S}{C^P}=\frac{\sum\limits_{i=1}^{P}{s_i}}{\sum\limits_{i=1}^{P}{C_i}}.$$"
#     m.description = "<p>The total self- and coauthor-citation rate is the ratio bewtween the number of citations " \
#                     "to all of an author\'s publications made by other publications from the same author and " \
#                     "coauthors versus the total number of citations to all of the author\'s publications or</p>" + \
#                     equation
#     m.draw_graph = Impact_Graphs.draw_graph_line_chart
#     # m.graph_type = LINE_CHART
#     m.calculate = calculate_total_coauthor_cite_rate
#     return m
#
#
# # mean self & coauthor-citation rate
# def calculate_mean_coauthor_cite_rate(metric_set: MetricSet) -> float:
#     all_citations = metric_set.citations
#     coauthor_citations = metric_set.self_coauthor_citations()
#     return Impact_Funcs.calculate_mean_self_cite_rate(coauthor_citations, all_citations)
#
#
# def metric_mean_coauthor_cite_rate() -> Metric:
#     m = Metric()
#     m.name = "mean coauthor cite rate"
#     m.full_name = "mean self &am; coauthor-citation rate"
#     m.html_name = "mean self &amp; coauthor-citation rate"
#     m.symbol = r"\(\bar{S_r}\)"
#     m.metric_type = FLOAT
#     m.is_coauthor = True
#     equation = r"$$\bar{S_r}=\frac{1}{P}\sum\limits_{i=1}^{P}{\frac{s_i}{C_i}}$$"
#     m.description = "<p>The mean self and coauthor-citation rate is the average rate of self and coauthor-citation " \
#                     "for an author across all of their publications. It differs from the total self " \
#                     "and coauthor-citation rate in that the total is based on the ratio of the sums while the " \
#                     "average is based on the sums of the ratios.</p>" + equation
#     m.draw_graph = Impact_Graphs.draw_graph_line_chart
#     # m.graph_type = LINE_CHART
#     m.calculate = calculate_mean_coauthor_cite_rate
#     return m
#
#
# # sharpened h-index (Schreiber 2007)
# def calculate_sharpened_h_index_coauthor(metric_set: MetricSet) -> float:
#     all_citations = metric_set.citations
#     coauthor_citations = metric_set.self_coauthor_citations()
#     return Impact_Funcs.calculate_sharpened_h_index(coauthor_citations, all_citations)
#
#
# def metric_sharpened_h_index_coauthor() -> Metric:
#     m = Metric()
#     m.name = "sharpened h-index (coauthor)"
#     m.full_name = "sharpened h-index (self & coauthor)"
#     m.html_name = "sharpened <em>h-</em>index (self &amp; coauthor)"
#     m.symbol = "<em>h</em><sub>sharp.coauth</sub>"
#     m.metric_type = INT
#     m.is_coauthor = True
#     m.description = "<p>A simple way of accounting for self-citations with respect to impact is to simply remove " \
#                     "them from each publication\'s citation counts prior to calculating a metric. For the base " \
#                     "calculation of the __h-index__ this is known as the sharpened <em>h-</em>index " \
#                     "(Schreiber 2007).</p>" \
#                     "<p>One complication is that there may be multiple methods for defining self-citations. In this "
#                     "case we remove any citations by the target author and any of the coauthors to their own " \
#                     "publications.</p>"
#     m.references = ["Schreiber, M. (2007) Self-citation corrections for the Hirsch index. <em>Europhysics "
#                     "Letters</em> 78:30002-1&ndash;6."]
#     m.draw_graph = Impact_Graphs.draw_graph_line_chart
#     # m.graph_type = LINE_CHART
#     m.calculate = calculate_sharpened_h_index_coauthor
#     m.properties["Core Metric"] = True
#     m.properties["Self-Citation"] = True
#     return m
#
#
# # b-index (Brown 2009)
# def calculate_b_index_mean_coauthor(metric_set: MetricSet) -> float:
#     h = metric_set.metrics["h-index"].value
#     mean_rate = 1 - metric_set.metrics["mean coauthor cite rate"].value
#     return Impact_Funcs.calculate_b_index(h, mean_rate)
#
#
# def metric_b_index_mean_coauthor() -> Metric:
#     m = Metric()
#     m.name = "b-index mean coauthor"
#     m.full_name = "b-index (mean self & coauthor-citation rate)"
#     m.html_name = "<em>b-</em>index (mean self &amp; coauthor-citation rate)"
#     m.symbol = "<em>b</em><sub>mean.coauth</sub>"
#     m.metric_type = FLOAT
#     m.is_coauthor = True
#     equation = r"$$b=hk^{\frac{3}{4}},$$"
#     req = r"$$k=1-\bar{S_r}=1-\frac{\sum\limits_{i=1}^{P}{\frac{s_i}{C_i}}}{P}$$"
#     m.description = "<p>The <em>b-</em>index (Brown 2009) is designed to correct the __h-index__ for self-citations, "
#                     "without actually having to check the citation records for every publication. It assumes that " \
#                     "an author\'s self-citation rate is fairly consistent across publications such that, on average, "
#                     "a fraction <em>k</em> of the citations are from other authors. Assuming that citations follow " \
#                     "a Zipfian distribution and that empirically derived estimates of the shape of this distribution "
#                     "are reasonable, one finds the index</p>" + equation + "<p>where <em>b</em> is an estimate of " \
#                     "the <em>h-</em>index corrected for self-citations.</p><p>There are multiple ways to estimate " \
#                     "the non-self-citation rate (<em>k</em>). In this case, we calculate it directly as the mean of "
#                     "the proportion of self and coauthor-citations to total-citations across all publication, " \
#                     "subtracted from one, or</p>" + req + "<p>where <em>s<sub>i</sub></em> is the number of " \
#                     "self and coauthor-citations to the <em>i</em><sup>th</sup> publication.</p>"
#     m.references = ["Brown, R.J.C. (2009) A simple method for excluding self-citation from the <em>h-</em>index: "
#                     "the <em>b-</em>index. <em>Online Information Review</em> 33(6):1129&ndash;1136."]
#     m.draw_graph = Impact_Graphs.draw_graph_line_chart
#     # m.graph_type = LINE_CHART
#     m.calculate = calculate_b_index_mean_coauthor
#     m.properties["Core Metric"] = True
#     m.properties["Self-Citation"] = True
#     return m


# b-index (Brown 2009)
def calculate_b_index_10_percent(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_b_index(h, 0.9)


def metric_b_index_10_percent() -> Metric:
    m = Metric()
    m.name = "b-index 10%"
    m.full_name = "b-index (10% rate)"
    m.html_name = "<em>b-</em>index (10% rate)"
    m.symbol = "<em>b</em><sub>10%</sub>"
    m.metric_type = FLOAT
    m.is_self = True
    equation = r"$$b=hk^{\frac{3}{4}},$$"
    m.description = ('<p>The <em>b-</em>index (Brown 2009) is designed to correct the __h-index__ for self-citations, '
                     'without actually having to check the citation records for every publication. It assumes that '
                     'an author\'s self-citation rate is fairly consistent across publications such that, on average, '
                     'a fraction <em>k</em> of the citations are from other authors. Assuming that citations follow '
                     'a Zipfian distribution and that empirically derived estimates of the shape of this distribution '
                     f'are reasonable, one finds the index</p>{equation}<p>where <em>b</em> is an estimate of '
                     'the <em>h-</em>index corrected for self-citations.</p><p>There are multiple ways to estimate '
                     'the non-self-citation rate (<em>k</em>). In this case, we simply assume a self-citation rate '
                     'of 10%, meaning the non-self-citation rate is 90%, or <em>k</em> = 0.9.</p>')
    m.references = ["Brown, R.J.C. (2009) A simple method for excluding self-citation from the <em>h-</em>index: "
                    "the <em>b-</em>index. <em>Online Information Review</em> 33(6):1129&ndash;1136."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_b_index_10_percent
    m.properties["Core Metric"] = True
    m.properties["Self-Citation"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# hi-index (Batista et al. 2006)
def calculate_hi_index(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_hi_index(is_core, n_authors, h)


def write_hi_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    tmp_citations = [c for c in metric_set.citations]
    tmp_author_cnts = [a for a in metric_set.author_counts()]
    data = []
    for i in range(len(tmp_citations)):
        data.append([tmp_citations[i], tmp_author_cnts[i]])
    data.sort(reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    hi = metric_set.metrics["hi-index"].value
    s = 0
    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
        else:
            v = ""
        if i + 1 <= h:
            ec = ' class="box"'
            s += a
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td{ec}>{a}</td>'
        rows[2] += f'<td>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h} and the sum of the authors for publications in the core is {s}, thus '
               f'<em>h<sub>i</sub></em>{NBEQ}{hi:0.4f}.</p>')
    return outstr


def metric_hi_index() -> Metric:
    m = Metric()
    m.name = "hi-index"
    m.full_name = "hi-index "
    m.html_name = "<em>h<sub>i</sub>-</em>index"
    m.symbol = "<em>h<sub>i</sub></em>"
    m.axis_name = r"$h_i$"
    m.metric_type = FLOAT
    m.example = write_hi_index_example
    equation = r"$$h_i=\frac{h}{\frac{\sum\limits_{i=1}^{h}{A_i}}{h}}=\frac{h^2}{\sum\limits_{i=1}^{h}{A_i}}.$$"
    m.description = ('<p>The <em>h<sub>i</sub>-</em>index (Batista <em>et al.</em> 2006) is a simple correction of '
                     'the __h-index__ for multi-authored publications. This index is simply the <em>h-</em>index '
                     f'divided by the average number of authors in the core publications, or</p>{equation}'
                     'If every publication in the core is solo-authored then <em>h<sub>i</sub></em> = <em>h.</em> '
                     'This can be an extremely harsh correction. A single core publication with a large number of '
                     'co-authors may skew the average and thus lower an author\'s impact factor tremendously. '
                     'Use of the median rather than the mean might be a fairer approach.</p>')
    m.references = ["Batista, P.D., M.G. Campiteli, O. Kinouchi, and A.S. Martinez (2006) Is it possible to "
                    "compare researchers with different scientific interests? <em>Scientometrics</em> "
                    "68(1):179&ndash;189."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hi_index
    m.properties["Coauthorship"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# fractional pure h-index (Wan et al. 2007)
def calculate_pure_h_index_frac(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_pure_h_index_frac(is_core, n_authors, h)


def write_pure_h_index_frac_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    tmp_citations = [c for c in metric_set.citations]
    tmp_author_cnts = [a for a in metric_set.author_counts()]
    data = []
    for i in range(len(tmp_citations)):
        data.append([tmp_citations[i], tmp_author_cnts[i]])
    data.sort(reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    hp = metric_set.metrics["pure h-index frac"].value
    s = 0
    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
        else:
            v = ""
        if i + 1 <= h:
            ec = ' class="box"'
            s += a
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td{ec}>{a}</td>'
        rows[2] += f'<td>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h} and the sum of the authors for publications in the core is {s}, thus '
               f'<em>h<sub>p</sub></em>{NBEQ}{hp:0.4f}.</p>')
    return outstr


def metric_pure_h_index_frac() -> Metric:
    m = Metric()
    m.name = "pure h-index frac"
    m.full_name = "pure h-index (fractional credit)"
    m.html_name = "pure <em>h-</em>index (fractional credit)"
    m.symbol = "<em>h</em><sub><em>p</em>.frac</sub>"
    m.metric_type = FLOAT
    m.example = write_pure_h_index_frac_example
    equation = r"$$h_{p.\text{frac}}=\frac{h}{\sqrt{\frac{\sum\limits_{i=1}^{h}{A_i}}{h}}}$$"
    m.description = ('<p>The pure <em>h-</em>index (Wan <em>et al.</em> 2007) is similar to the '
                     '__hi-index__ in that it attempts to adjust for multiple authors. The index '
                     'allows for different methods of assigning authorship credit. If one wishes to assign all '
                     'authors equal credit, or if one does not have information about authorship order, one can '
                     'assign fractional credit per author, which essentially means this metric is simply the '
                     '__h-index__ divided by the square-root of the average number of authors in the core, '
                     'thus differing from <em>h<sub>i</sub></em> only by the square-root in the denominator '
                     '(which makes the fractional version of the pure <em>h-</em>index less harsh than '
                     f'<em>h<sub>i</sub></em> by not punishing co-authorship as severely).</p>{equation}')
    m.references = ["Wan, J.-k., P.-h. Hua, and R. Rousseau (2007) The pure <em>h-</em>index: Calculating an "
                    "author\'s <em>h-</em>index by taking co-authors into account. <em>Collnet Journal of "
                    "Scientometrics and Information Management</em> 1(2):1&ndash;5."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pure_h_index_frac
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# proportional pure h-index (Wan et al. 2007)
def calculate_pure_h_index_prop(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_pure_h_index_prop(is_core, n_authors, author_pos, h)


def write_pure_h_index_prop_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    tmp_citations = [c for c in metric_set.citations]
    tmp_author_cnts = [a for a in metric_set.author_counts()]
    tmp_author_pos = [a for a in metric_set.author_position()]
    data = []
    for i in range(len(tmp_citations)):
        data.append([tmp_citations[i], tmp_author_cnts[i], tmp_author_pos[i]])
    data.sort(reverse=True)
    rows = ["" for _ in range(7)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    rows[3] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[5] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[6] = '<tr><th>Weight (<em>w<sub>i</sub></em>)</th>'
    h = metric_set.metrics["h-index"].value
    hp = metric_set.metrics["pure h-index prop"].value
    s = 0
    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        ap = d[2]
        e = Impact_Funcs.author_effort("proportional", a, ap)
        w = 1 / e
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
        else:
            v = ""
        if i + 1 <= h:
            ec = ' class="box"'
            s += w
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
        rows[3] += f'<td>{a}</td>'
        rows[4] += f'<td>{ap}</td>'
        rows[5] += f'<td>{e:0.2f}</td>'
        rows[6] += f'<td{ec}>{w:0.2f}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h} and the sum of the weights for the publications in the core is {s}, '
               f'thus <em>h</em><sub><em>p</em>.prop</sub>{NBEQ}{hp:0.4f}.</p>')
    return outstr


def metric_pure_h_index_prop() -> Metric:
    m = Metric()
    m.name = "pure h-index prop"
    m.full_name = "pure h-index (proportional credit)"
    m.html_name = "pure <em>h-</em>index (proportional credit)"
    m.symbol = "<em>h</em><sub><em>p</em>.prop</sub>"
    m.example = write_pure_h_index_prop_example
    m.metric_type = FLOAT
    effort_eq = r"$$E_i=\frac{2\left(A_i + 1 - a_i\right)}{A_i\left(A_i + 1\right)},$$"
    equation = r"$$h_{p.\text{prop}}=\frac{h}{\sqrt{\frac{\sum\limits_{i=1}^{h}{w_i}}{h}}}.$$"
    m.description = ('<p>The pure <em>h-</em>index (Wan <em>et al.</em> 2007) is similar to the '
                     '__hi-index__ in that it attempts to adjust for multiple authors. The index '
                     'allows for different methods of assigning authorship credit. If one has information on author '
                     'order and assumes the order directly correlates with effort, one can use a proportional '
                     f'(artihmetic) assignment of credit for each publication as:</p>{effort_eq}'
                     '<p>where <em>a<sub>i</sub></em> is the position of the target author within the full author '
                     'list of publication <em>i</em> (<em>i.e.</em>, an integer from 1 to <em>A<sub>i</sub></em>). '
                     'Each publication can then be weighted by the inverse of the author effort, '
                     f'<em>w<sub>i</sub></em>{NBEQ}1/<em>E<sub>i</sub></em>. '
                     f'Given the credited effort for each publication, the metric is calculated as:</p>{equation}')
    m.references = ["Wan, J.-k., P.-h. Hua, and R. Rousseau (2007) The pure <em>h-</em>index: Calculating an "
                    "author\'s <em>h-</em>index by taking co-authors into account. <em>Collnet Journal of "
                    "Scientometrics and Information Management</em> 1(2):1&ndash;5."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pure_h_index_prop
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# geometric pure h-index (Wan et al. 2007)
def calculate_pure_h_index_geom(metric_set: MetricSet) -> float:
    is_core = metric_set.is_core
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_pure_h_index_geom(is_core, n_authors, author_pos, h)


def write_pure_h_index_geom_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    tmp_citations = [c for c in metric_set.citations]
    tmp_author_cnts = [a for a in metric_set.author_counts()]
    tmp_author_pos = [a for a in metric_set.author_position()]
    data = []
    for i in range(len(tmp_citations)):
        data.append([tmp_citations[i], tmp_author_cnts[i], tmp_author_pos[i]])
    data.sort(reverse=True)
    rows = ["" for _ in range(7)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    rows[3] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[5] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[6] = '<tr><th>Weight (<em>w<sub>i</sub></em>)</th>'
    h = metric_set.metrics["h-index"].value
    hp = metric_set.metrics["pure h-index geom"].value
    s = 0
    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        ap = d[2]
        e = Impact_Funcs.author_effort("geometric", a, ap)
        w = 1 / e
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
        else:
            v = ""
        if i + 1 <= h:
            ec = ' class="box"'
            s += w
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
        rows[3] += f'<td>{a}</td>'
        rows[4] += f'<td>{ap}</td>'
        rows[5] += f'<td>{e:0.2f}</td>'
        rows[6] += f'<td{ec}>{w:0.2f}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h} and the sum of the weights for the publications in the core is {s}, '
               f'thus <em>h</em><sub><em>p</em>.geom</sub>{NBEQ}{hp:0.4f}.</p>')
    return outstr


def metric_pure_h_index_geom() -> Metric:
    m = Metric()
    m.name = "pure h-index geom"
    m.full_name = "pure h-index (geometric credit)"
    m.html_name = "pure <em>h-</em>index (geometric credit)"
    m.symbol = "<em>h</em><sub><em>p</em>.geom</sub>"
    m.metric_type = FLOAT
    m.example = write_pure_h_index_geom_example
    effort_eq = r"$$E_i=\frac{2^{A_i - a_i}}{2^{A_i} - 1},$$"
    equation = r"$$h_{p.\text{geom}}=\frac{h}{\sqrt{\frac{\sum\limits_{i=1}^{h}{w_i}}{h}}}.$$"
    m.description = ('<p>The pure <em>h-</em>index (Wan <em>et al.</em> 2007) is similar to the '
                     '__hi-index__ in that it attempts to adjust for multiple authors. The index '
                     'allows for different methods of assigning authorship credit. If one has information on author '
                     'order and assumes the order directly correlates with effort, one can use a geometric '
                     f'assignment of credit for each publication as:</p>{effort_eq}'
                     '<p>where <em>a<sub>i</sub></em> is the position of the target author within the full author '
                     'list of publication <em>i</em> (<em>i.e.</em>, an integer from 1 to <em>A<sub>i</sub></em>). '
                     'Each publication can then be weighted by the inverse of the author effort, '
                     f'<em>w<sub>i</sub></em>{NBEQ}1/<em>E<sub>i</sub></em>. '
                     f'Given the credited effort for each publication, the metric is calculated as:</p>{equation}')
    m.references = ["Wan, J.-k., P.-h. Hua, and R. Rousseau (2007) The pure <em>h-</em>index: Calculating an "
                    "author\'s <em>h-</em>index by taking co-authors into account. <em>Collnet Journal of "
                    "Scientometrics and Information Management</em> 1(2):1&ndash;5."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pure_h_index_geom
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# fractional adapted pure h-index (Chai et al. 2008)
def calculate_adapt_pure_h_index_frac(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_adapt_pure_h_index_frac(citations, n_authors)


def write_adapt_pure_h_index_frac_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c/math.sqrt(a), c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    cstari = r"\(C^*_i\)"
    rows[2] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr><th></th>'
    he = 0
    for i, d in enumerate(data):
        if i + 1 <= d[0]:
            he = i+1
    hp = metric_set.metrics["adapt pure h-index frac"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        if i + 1 == he:
            v = f'<em>h<sub>e</sub></em>{NBEQ}{he}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td{ec}>{cs:1.2f}</td>'
        rows[3] += f'<td{ec}>{i+1}</td>'
        rows[4] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    eq = r"\(i \leq C^*_i\)"
    outstr += (f'<p>The largest rank where {eq} is {he}. Interpolating between this and the next largest rank '
               f'yields <em>h</em><sub><em>ap</em>.frac</sub>{NBEQ}{hp:0.4f}.</p>')
    return outstr


def metric_adapt_pure_h_index_frac() -> Metric:
    m = Metric()
    m.name = "adapt pure h-index frac"
    m.full_name = "adapted pure h-index (fractional credit)"
    m.html_name = "adapted pure <em>h-</em>index (fractional credit)"
    m.metric_type = FLOAT
    m.example = write_adapt_pure_h_index_frac_example
    m.symbol = "<em>h</em><sub><em>ap</em>.frac</sub>"
    cistr = r"$$C^{*}_i = \frac{C_i}{\sqrt{A_i}}.$$"
    hestr = r"$$h_e = \underset{i}{\max}\left(i \leq C^{*}_i\right).$$"
    equation = (r"$$h_{ap.\text{frac}}= "
                r"\frac{\left(h_e+1\right)C^{*}_{h_e}-h_e C^{*}_{h_e +1}}{C^{*}_{h_e}-C^{*}_{h_e+1}+1}.$$")
    m.description = ('<p>The adapted pure <em>h-</em>index (Chai <em>et al.</em> 2008) is very similar to the '
                     '__pure h-index frac__, except that it estimates its own core rather than relying on the '
                     'standard __h-index__ core. For a given publication, if one wishes to assign all authors equal '
                     'credit, or if one does not have information about authorship order, one can calculate an '
                     'effective citation count as the number of citations divided by the square-root of the '
                     f'number of authors,</p>{cistr}<p>Publications are ranked according to these new citation '
                     'counts and the <em>h-</em>equivalent value, <em>h<sub>e</sub>,</em> is found as the largest '
                     f'rank for which the rank is less than the number of equivalent citations, or</p>{hestr}'
                     'The adapted pure <em>h-</em>index is calculated by interpolating between this value and the '
                     f'next largest, as</p>{equation}')
    m.references = ["Chai, J.-c., P.-h. Hua, R. Rousseau, and J.-k. Wan (2008) The adapted pure <em>h-</em>index. "
                    "<em>Fourth International Conference on Webometrics, Informetrics and Scientometrics & Ninth "
                    "COLLNET Meeting,</em> H. Kretschmer and F. Havemann, eds. Humboldt-Universität zu Berlin: "
                    "Institute for Library and Information Science."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_adapt_pure_h_index_frac
    m.properties["Coauthorship"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# proportional adapted pure h-index (Chai et al. 2008)
def calculate_adapt_pure_h_index_prop(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_adapt_pure_h_index_prop(citations, n_authors, author_pos)


def write_adapt_pure_h_index_prop_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        ap = metric_set.author_position()[i]
        e = Impact_Funcs.author_effort("proportional", a, ap)
        data.append([c/math.sqrt(1/e), c, a, ap, e])
    data.sort(reverse=True)
    cstari = r"\(C^*_i\)"
    rows = ["" for _ in range(8)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Weight (<em>w<sub>i</sub></em>)</th>'
    rows[5] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[6] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[7] = '<tr><th></th>'
    he = 0
    for i, d in enumerate(data):
        if i + 1 <= d[0]:
            he = i+1
    hp = metric_set.metrics["adapt pure h-index prop"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        ap = d[3]
        e = d[4]
        w = 1/e
        if i + 1 == he:
            v = f'<em>h<sub>e</sub></em>{NBEQ}{he}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{ap}</td>'
        rows[3] += f'<td>{e:0.2f}</td>'
        rows[4] += f'<td>{w:0.2f}</td>'
        rows[5] += f'<td{ec}>{cs:1.2f}</td>'
        rows[6] += f'<td{ec}>{i+1}</td>'
        rows[7] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    eq = r"\(i \leq C^*_i\)"
    outstr += (f'<p>The largest rank where {eq} is {he}. Interpolating between this and the next largest rank yields '
               f'<em>h</em><sub><em>ap</em>.prop</sub>{NBEQ}{hp:0.4f}.</p>')
    return outstr


def metric_adapt_pure_h_index_prop() -> Metric:
    m = Metric()
    m.name = "adapt pure h-index prop"
    m.full_name = "adapted pure h-index (proportional credit)"
    m.html_name = "adapted pure <em>h-</em>index (proportional credit)"
    m.symbol = "<em>h</em><sub><em>ap</em>.prop</sub>"
    m.metric_type = FLOAT
    m.example = write_adapt_pure_h_index_prop_example
    effort_eq = r"$$E_i=\frac{2\left(A_i + 1 - a_i\right)}{A_i\left(A_i + 1\right)},$$"
    cistr = r"$$C^{*}_i = \frac{C_i}{\sqrt{w_i}}.$$"
    hestr = r"$$h_e = \underset{i}{\max}\left(i \leq C^{*}_i\right).$$"
    equation = (r"$$h_{ap.\text{prop}}= "
                r"\frac{\left(h_e+1\right)C^{*}_{h_e}-h_e C^{*}_{h_e +1}}{C^{*}_{h_e}-C^{*}_{h_e+1}+1}.$$")
    m.description = ('<p>The adapted pure <em>h-</em>index (Chai <em>et al.</em> 2008) is very similar to the '
                     '__pure h-index prop__, except that it estimates its own core rather than relying on the '
                     'standard __h-index__ core. For a given publication, if one has information on author '
                     'order and assumes the order directly correlates with effort, one can use a proportional '
                     f'(artihmetic) assignment of credit for each publication as:</p>{effort_eq}'
                     '<p>where <em>a<sub>i</sub></em> is the position of the target author within the full author '
                     'list of publication <em>i</em> (<em>i.e.</em>, an integer from 1 to <em>A<sub>i</sub></em>). '
                     'Each publication can then be weighted by the inverse of the author effort, '
                     f'<em>w<sub>i</sub></em>{NBEQ}1/<em>E<sub>i</sub></em>. '
                     f'The effective number of citations for each publication is then calculated as</p>{cistr}'
                     '<p>Publications are ranked according to these new citation '
                     'counts and the <em>h-</em>equivalent value, <em>h<sub>e</sub>,</em> is found as the largest '
                     f'rank for which the rank is less than the number of equivalent citations, or</p>{hestr}'
                     'The adapted pure <em>h-</em>index is calculated by interpolating between this value and the '
                     f'next largest, as</p>{equation}')
    m.references = ["Chai, J.-c., P.-h. Hua, R. Rousseau, and J.-k. Wan (2008) The adapted pure <em>h-</em>index. "
                    "<em>Fourth International Conference on Webometrics, Informetrics and Scientometrics & Ninth "
                    "COLLNET Meeting,</em> H. Kretschmer and F. Havemann, eds. Humboldt-Universität zu Berlin: "
                    "Institute for Library and Information Science."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_adapt_pure_h_index_prop
    m.properties["Coauthorship"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# geometric adapted pure h-index (Chai et al. 2008)
def calculate_adapt_pure_h_index_geom(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_adapt_pure_h_index_geom(citations, n_authors, author_pos)


def write_adapt_pure_h_index_geom_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        ap = metric_set.author_position()[i]
        e = Impact_Funcs.author_effort("geometric", a, ap)
        data.append([c/math.sqrt(1/e), c, a, ap, e])
    data.sort(reverse=True)
    cstari = r"\(C^*_i\)"
    rows = ["" for _ in range(8)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Weight (<em>w<sub>i</sub></em>)</th>'
    rows[5] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[6] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[7] = '<tr><th></th>'
    he = 0
    for i, d in enumerate(data):
        if i + 1 <= d[0]:
            he = i+1
    hp = metric_set.metrics["adapt pure h-index geom"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        ap = d[3]
        e = d[4]
        w = 1/e
        if i + 1 == he:
            v = f'<em>h<sub>e</sub></em>{NBEQ}{he}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{ap}</td>'
        rows[3] += f'<td>{e:0.2f}</td>'
        rows[4] += f'<td>{w:0.2f}</td>'
        rows[5] += f'<td{ec}>{cs:1.2f}</td>'
        rows[6] += f'<td{ec}>{i+1}</td>'
        rows[7] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    eq = r"\(i \leq C^*_i\)"
    outstr += (f'<p>The largest rank where {eq} is {he}. Interpolating between this and the next largest rank yields '
               f'<em>h</em><sub><em>ap</em>.geom</sub>{NBEQ}{hp:0.4f}.</p>')
    return outstr


def metric_adapt_pure_h_index_geom() -> Metric:
    m = Metric()
    m.name = "adapt pure h-index geom"
    m.full_name = "adapted pure h-index (geometric credit)"
    m.html_name = "adapted pure <em>h-</em>index (geometric credit)"
    m.symbol = "<em>h</em><sub><em>ap</em>.geom</sub>"
    m.example = write_adapt_pure_h_index_geom_example
    m.metric_type = FLOAT
    effort_eq = r"$$E_i=\frac{2^{A_i - a_i}}{2^{A_i} - 1},$$"
    cistr = r"$$C^{*}_i = \frac{C_i}{\sqrt{w_i}}.$$"
    hestr = r"$$h_e = \underset{i}{\max}\left(i \leq C^{*}_i\right).$$"
    equation = (r"$$h_{ap.\text{geom}}= "
                r"\frac{\left(h_e+1\right)C^{*}_{h_e}-h_e C^{*}_{h_e +1}}{C^{*}_{h_e}-C^{*}_{h_e+1}+1}.$$")
    m.description = ('<p>The adapted pure <em>h-</em>index (Chai <em>et al.</em> 2008) is very similar to the '
                     '__pure h-index geom__, except that it estimates its own core rather than relying on the '
                     'standard __h-index__ core. For a given publication, if one has information on author '
                     'order and assumes the order directly correlates with effort, one can use a geometric '
                     f'assignment of credit for each publication as:</p>{effort_eq}'
                     '<p>where <em>a<sub>i</sub></em> is the position of the target author within the full author '
                     'list of publication <em>i</em> (<em>i.e.</em>, an integer from 1 to <em>A<sub>i</sub></em>). '
                     'Each publication can then be weighted by the inverse of the author effort, '
                     f'<em>w<sub>i</sub></em>{NBEQ}1/<em>E<sub>i</sub></em>. '
                     f'The effective number of citations for each publication is then calculated as</p>{cistr}'
                     '<p>Publications are ranked according to these new citation '
                     'counts and the <em>h-</em>equivalent value, <em>h<sub>e</sub>,</em> is found as the largest '
                     f'rank for which the rank is less than the number of equivalent citations, or</p>{hestr}'
                     'The adapted pure <em>h-</em>index is calculated by interpolating between this value and the '
                     f'next largest, as</p>{equation}')
    m.references = ["Chai, J.-c., P.-h. Hua, R. Rousseau, and J.-k. Wan (2008) The adapted pure <em>h-</em>index. "
                    "<em>Fourth International Conference on Webometrics, Informetrics and Scientometrics & Ninth "
                    "COLLNET Meeting,</em> H. Kretschmer and F. Havemann, eds. Humboldt-Universität zu Berlin: "
                    "Institute for Library and Information Science."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_adapt_pure_h_index_geom
    m.properties["Coauthorship"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
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
    m.symbol = "<em>p<sub>h</sub></em>"
    m.synonyms = ["<em>p<sub>h</sub></em>"]
    m.metric_type = FLOAT
    req = r"$$r_i=\frac{\frac{1}{a_i}}{\sum\limits_{j=1}^{A_i}{\frac{1}{j}}}$$"
    eq1 = r"$$C^{\prime}=\sum\limits_{i=1}^{P}{C_i r_i}$$"
    eq2 = r"$$P^{\prime}=\sum\limits_{i=1}^{P}{r_i}$$"
    eq3 = r"$$p_h=\sqrt[3]{\frac{\left.C^{\prime}\right.^2}{P^{\prime}}}$$"
    m.description = ('<p>The harmonic <em>p-</em>index (Prathap 2011) is a variant of the __p-index__ '
                     'which attempts to account for multiple-authored publications by adjusting both citation '
                     'and publication counts by author counts, using a harmonic weighting credit scheme '
                     'based on the author\'s position within the authorship list for each publication '
                     '(<em>a<sub>i</sub></em>). For each publication, the author receives weighted credit equal to:'
                     f'{req}The harmonic <em>p-</em>index is then calculated as:</p>{eq1}{eq2}{eq3}')
    m.references = ["Prathap, G. (2011) The fractional and harmonic <em>p-</em>indices for multiple authorship. "
                    "<em>Scientometrics</em> 86:239&ndash;244."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_p_index_harm
    m.properties["Coauthorship"] = True
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
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
    m.symbol = "profit <em>p</em>"
    m.metric_type = FLOAT
    weq = r"$$E_i=\frac{1+\left|A_i+1-2a_i\right|}{\frac{1}{2}A_i^2+A_i\left(1-D_i\right)},$$"
    deq = (r"$$D_i=\begin{matrix} 0 & \text{if }A_i\text{ is even} \\ "
           r"\frac{1}{2A_i} & \text{if }A_i\text{ is odd} \end{matrix}.$$")
    equation = r"$$p=1-\frac{\sum\limits_{i=1}^{P}{E_i}}{P}.$$"
    m.description = ('<p>The profit indices (Aziz and Rozing 2013) attempt to measure the effect of collaboration on '
                     'an author\'s impact. They use a harmonic weighting algorithm and information on author '
                     'order (assuming that authors in the middle of an author list had the least impact) to '
                     'estimate effort for each publication. The effort for the <em>i</em><sup>th</sup> '
                     f'publication is</p>{weq}<p>where</p>{deq}<p>The sum of <em>E<sub>i</sub></em> for '
                     'all publications is the number of &ldquo;monograph equivalents&rdquo; (a monograph being '
                     'defined as a single-authored publication). The profit (<em>p</em>)-index is the relative '
                     f'contribution of collaborators to an individual\'s total publication record, or</p>{equation}'
                     '<p>This value ranges from 0 to 1, with 0 indicating no contribution of co-authors (all '
                     'solo-authored papers) and 1 meaning complete contribution from co-authors (a value of exactly '
                     '1 is impossible).</p>')
    m.references = ["Aziz, N.A., and M.P. Rozing (2013) Profit (<em>p</em>)-Index: The degree to which authors "
                    "profit from co-authors. <em>PLoS ONE</em> 8(4):e59814."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_profit_p_index
    m.properties["Alternative Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["All Publications"] = True
    return m


# profit adjusted h-index (Aziz and Rozing 2013)
def calculate_profit_adj_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_profit_adj_h_index(citations, n_authors, author_pos)


def write_profit_adj_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        ap = metric_set.author_position()[i]
        e = Impact_Funcs.author_effort("harmonic", a, ap)
        data.append([c*e, c, a, ap, e])
    data.sort(reverse=True)
    cstari = r"\(C^*_i\)"
    rows = ["" for _ in range(7)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[4] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[5] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[6] = '<tr><th></th>'
    ha = metric_set.metrics["profit adj h-index"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        ap = d[3]
        e = d[4]
        if i + 1 == ha:
            v = f'<em>h<sub>a</sub></em>{NBEQ}{ha}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{ap}</td>'
        rows[3] += f'<td>{e:0.2f}</td>'
        rows[4] += f'<td{ec}>{cs:1.2f}</td>'
        rows[5] += f'<td{ec}>{i+1}</td>'
        rows[6] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    eq = r"\(i \leq C^*_i\)"
    outstr += f'<p>The largest rank where {eq} is {ha}.</p>'
    return outstr


def metric_profit_adj_h_index() -> Metric:
    m = Metric()
    m.name = "profit adj h-index"
    m.full_name = "profit adjusted h-index"
    m.html_name = "profit adjusted <em>h-</em>index"
    m.symbol = "<em>h<sub>a</sub></em>"
    m.axis_name = r"$h_a$"
    m.example = write_profit_adj_h_index_example
    m.metric_type = INT
    weq = r"$$E_i=\frac{1+\left|A_i+1-2a_i\right|}{\frac{1}{2}A_i^2+A_i\left(1-D_i\right)},$$"
    deq = (r"$$D_i=\begin{matrix} 0 & \text{if }A_i\text{ is even} \\ "
           r"\frac{1}{2A_i} & \text{if }A_i\text{ is odd} \end{matrix}.$$")
    ceq = r"$$C^{*}_i=E_i C_i,$$"
    equation = r"$$h_a=\underset{i}{\max}\left(i \leq E_iC_i\right)=\underset{i}{\max}\left(i \leq C^{*}_i\right).$$"
    m.description = ('<p>The profit indices (Aziz and Rozing 2013) attempt to measure the effect of collaboration on '
                     'an author\'s impact. They use a harmonic weighting algorithm and information on author '
                     'order (assuming that authors in the middle of an author list had the least impact) to '
                     'estimate effort for each publication. The effort for the <em>i</em><sup>th</sup> '
                     f'publication is</p>{weq}<p>where</p>{deq}<p>The sum of <em>E<sub>i</sub></em> for '
                     'all publications is the number of &ldquo;monograph equivalents&rdquo; (a monograph being '
                     'defined as a single-authored publication). The profit adjusted <em>h-</em>index is calculated '
                     f'by weighting each publications citation count by this effort,</p>{ceq}'
                     '<p>reranking the publications based upon these weighted counts, and calculating the index '
                     f'as</p>{equation}')
    m.references = ["Aziz, N.A., and M.P. Rozing (2013) Profit (<em>p</em>)-Index: The degree to which authors "
                    "profit from co-authors. <em>PLoS ONE</em> 8(4):e59814."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_profit_adj_h_index
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
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
    m.symbol = "<em>p<sub>h</sub></em>"
    m.metric_type = FLOAT
    equation = r"$$p_h=1-\frac{h_a}{h}$$"
    m.description = ('<p>The profit <em>h-</em>index is the ratio between the __profit adj h-index__ '
                     '(<em>h<sub>a</sub></em>) and the regular __h-index__, subtracted from one, roughly '
                     'indicating the relative contribution of collaborators to an individual\'s '
                     f'<em>h-</em>index.</p>{equation}')
    m.references = ["Aziz, N.A., and M.P. Rozing (2013) Profit (<em>p</em>)-Index: The degree to which authors "
                    "profit from co-authors. <em>PLoS ONE</em> 8(4):e59814."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_profit_h_index
    m.properties["Core Property"] = True
    m.properties["Compound Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# normalized hi-index/hf-index (Wohlin 2009)
def calculate_normal_hi_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_normal_hi_index(citations, n_authors)


def write_normal_hi_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c/a, c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr><th></th>'
    hi = metric_set.metrics["normal hi-index"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        if i + 1 == hi:
            v = f'<em>h</em><sub><em>i-</em>norm</sub>{NBEQ}{hi}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td{ec}>{cs:1.2f}</td>'
        rows[3] += f'<td{ec}>{i+1}</td>'
        rows[4] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em> ≤ <em>C<sub>i</sub></em>/<em>A<sub>i</sub></em> is {hi}.</p>'
    return outstr


def metric_normal_hi_index() -> Metric:
    m = Metric()
    m.name = "normal hi-index"
    m.full_name = "normalized hi-index"
    m.html_name = "normalized <em>h<sub>i</sub>-</em>index"
    m.symbol = "<em>h</em><sub><em>i</em>-norm</sub>"
    m.example = write_normal_hi_index_example
    m.metric_type = INT
    equation = r"$$h_{i\text{-norm}}=\underset{i}{\max}\left(i \leq \frac{C_i}{A_i}\right).$$"
    m.description = ('<p>Similar to the __adapt pure h-index frac__, the normalized <em>h<sub>i</sub>-</em>index '
                     '(Wohlin 2009) is designed to adjust the __h-index__ for multiple authors by adjusting the '
                     'citation count by the number of authors. The primary difference is the new citation value is '
                     'calculated by dividing by the number of authors (<em>C<sub>i</sub></em> / '
                     '<em>A<sub>i</sub></em>) '
                     'rather than the square-root of the number of authors. Publications are again ranked by these '
                     'new citation per author values and the normalized <em>h<sub>i</sub>-</em>index is calculated '
                     'in the same manner as the <em>h-</em>index, that is an author has a normalized '
                     '<em>h<sub>i</sub>-</em>index of <em>h</em><sub><em>i</em>-norm</sub> when '
                     '<em>h</em><sub><em>i</em>-norm</sub> of '
                     'their publications have at least <em>h</em><sub><em>i</em>-norm</sub> citations per author, '
                     f'or</p>{equation}<p>This is identical to what Egghe (2008) called the '
                     '<span class="metric_name">fractional citation <em>h-</em>index '
                     '(<em>h<sub>f</sub></em>)</span> and was again re-invented by Abbas (2011) as the '
                     '<span class="metric_name">equally-weighted <em>h-</em>index (<em>h<sub>e</sub></em>)</span>.</p>')
    m.synonyms = ["fractional citation <em>h-</em>index",
                  "<em>h<sub>f</sub></em>",
                  "equally weighted <em>h-</em>index",
                  "<em>h<sub>e</sub></em>"]
    m.references = ["Wohlin, C. (2009) A new index for the citation curve of researchers. <em>Scientometrics</em> "
                    "81(2):521&ndash;533.",
                    "Egghe, L. (2008) Mathematical theory of the <em>h-</em> and <em>g-</em>index in case of "
                    "fractional counting of authorship. <em>Journal of the American Society for Information Science "
                    "and Technology</em> 59(10):1608&ndash;1616.",
                    "Abbas, A.M. (2011) Weighted indices for evaluating the quality of research with multiple "
                    "authorship. <em>Scientometrics</em> 88:107&ndash;131."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_normal_hi_index
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# gf-index (citation based) (Egghe 2008)
def calculate_gf_cite_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_gf_cite_index(citations, n_authors)


def write_gf_cite_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c/a, c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(7)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Adjusted Citations (<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em>)</th>'
    rows[3] = ('<tr class="top_row"><th>Cumulative Adjusted Citations '
               '(Σ<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em>)</th>')
    rows[4] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[5] = '<tr><th>Rank Squared (<em>i</em><sup>2</sup>)</th>'
    rows[6] = '<tr><th></th>'
    gf = metric_set.metrics["gf-cite"].value
    s = 0
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        s += cs
        if i + 1 == gf:
            v = f'<em>g<sub>f</sub></em>{NBEQ}{gf}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{cs:1.2f}</td>'
        rows[3] += f'<td{ec}>{s:1.2f}</td>'
        rows[4] += f'<td>{i+1}</td>'
        rows[5] += f'<td{ec}>{(i+1)**2}</td>'
        rows[6] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest rank where <em>i</em><sup>2</sup> ≤ '
               f'Σ<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em> is {gf}.</p>')
    return outstr


def metric_gf_cite_index() -> Metric:
    m = Metric()
    m.name = "gf-cite"
    m.full_name = "fractional citation g-index"
    m.html_name = "fractional citation <em>g-</em>index"
    m.example = write_gf_cite_index_example
    m.metric_type = INT
    m.symbol = "<em>g<sub>f</sub></em>"
    equation = r"$$g_f=\underset{i}{\max}\left(i^2 \leq \sum\limits_{j=1}^{i}{\frac{C_j}{A_j}}\right).$$"
    m.description = ('<p>The fractional citation <em>g-</em>index (Egghe 2008) is a variant of the '
                     '__g-index__ normalized by the number of authors and is the <em>g</em> equivalent of the '
                     f'__normal hi-index__. It is calculated as:</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.synonyms = ["<em>g<sub>f</sub></em>"]
    m.references = ["Egghe, L. (2008) Mathematical theory of the <em>h-</em> and <em>g-</em>index in case of "
                    "fractional counting of authorship. <em>Journal of the American Society for Information Science "
                    "and Technology</em> 59(10):1608&ndash;1616."]
    m.calculate = calculate_gf_cite_index
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# hm-index/hF-index (Schreiber 2008)
def calculate_hm_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_hm_index(citations, n_authors)


def write_hm_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = f'<tr><th>Author Effort (<em>E<sub>i</sub></em>{NBEQ}1/<em>A<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = f'<tr><th>Adjusted Rank (<em>r<sub>eff</sub></em>(<em>i</em>){NBEQ}Σ<em>E<sub>i</sub></em>)</th>'
    rows[5] = '<tr><th></th>'
    hm = metric_set.metrics["hm-index"].value
    s = 0
    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        s += 1/a
        if s == hm:
            v = f'<em>h<sub>m</sub></em>{NBEQ}{hm:0.2f}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{1/a:0.2f}</td>'
        rows[3] += f'<td>{i+1}</td>'
        rows[4] += f'<td{ec}>{s:0.2f}</td>'
        rows[5] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest adjusted rank where <em>r<sub>eff</sub></em>(<em>i</em>) ≤ '
               f'<em>C<sub>i</sub></em> is {hm:0.4f}.</p>')
    return outstr


def metric_hm_index() -> Metric:
    m = Metric()
    m.name = "hm-index"
    m.full_name = "hm-index"
    m.html_name = "<em>h<sub>m</sub>-</em>index"
    m.symbol = "<em>h<sub>m</sub></em>"
    m.axis_name = r"$h_m$"
    m.example = write_hm_index_example
    m.metric_type = FLOAT
    rheq = r"$$r_i=\sum\limits_{j=1}^{i}{1}=i.$$"
    reeq = r"$$r_{\text{eff}}\left(i\right)=\sum\limits_{j=1}^{i}{\frac{1}{A_i}}.$$"
    equation = (r"$$h_m=\underset{r_{\text{eff}}\left(i\right)}{\max}\left(r_{\text{eff}}\left(i\right) "
                r"\leq C_i\right).$$")
    m.description = ('<p>While the __normal hi-index__ accounts for the number of authors of '
                     'a publication by normalizing the citation count for that publication, <em>h<sub>m</sub></em> '
                     '(Schreiber 2008), also known as the <span class="metric_name">fractional paper '
                     '<em>h</em></span> and <span class="metric_name"><em>h<sub>F</sub>-</em>index</span> '
                     '(Egghe 2008), accounts for author number by normalizing the '
                     'ranks. For this index, one counts the number of citations and ranks the publications as for '
                     'the __h-index__, but rather than counting the rank of the <em>i</em><sup>th</sup> '
                     'publication as <em>i</em>, it is instead calculated as the cumulative sum of '
                     '1/<em>A<sub>i</sub>.</em> In formal terms, when calculating the <em>h-</em>index the rank of '
                     f'the <em>i</em><sup>th</sup> publication is</p>{rheq}<p>For <em>h<sub>m</sub></em> we '
                     f'instead calculate the effective rank as</p>{reeq}<p><em>h<sub>m</sub></em> is '
                     'determined as the largest value of <em>r</em><sub>eff</sub>(<em>i</em>) for which '
                     f'<em>r</em><sub>eff</sub>(<em>i</em>) ≤ <em>C<sub>i</sub></em> or</p>{equation}')
    m.synonyms = ["fractional paper <em>h</em>",
                  "<em>h<sub>F</sub>-</em>index"]
    m.references = ["Schreiber, M. (2008) To share the fame in a fair way, <em>h<sub>m</sub></em> modifies "
                    "<em>h</em> for multi-authored manuscripts. <em>New Journal of Physics</em> 10:040201.",
                    "Egghe, L. (2008) Mathematical theory of the <em>h-</em> and <em>g-</em>index in case of "
                    "fractional counting of authorship. <em>Journal of the American Society for Information Science "
                    "and Technology</em> 59(10):1608&ndash;1616."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hm_index
    m.properties["Coauthorship"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# gF-index (fractional paper) (Egghe 2008)
def calculate_gf_paper_index(metric_set: MetricSet) -> float:
    cumulative_citations = metric_set.cumulative_citations
    n_authors = metric_set.author_counts()
    rank_order = metric_set.rank_order
    return Impact_Funcs.calculate_gf_paper_index(cumulative_citations, rank_order, n_authors)


def write_gf_paper_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(8)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Cumulative Citations (Σ<em>C<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[3] = f'<tr><th>Author Effort (<em>E<sub>i</sub></em>{NBEQ}1/<em>A<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[5] = f'<tr><th>Adjusted Rank (<em>r<sub>eff</sub></em>(<em>i</em>){NBEQ}Σ<em>E<sub>i</sub></em>)</th>'
    rows[6] = '<tr><th>Adjusted Rank Squared (<em>r<sub>eff</sub></em>(<em>i</em>)<sup>2</sup></th>'
    rows[7] = '<tr><th></th>'
    gf = metric_set.metrics["gf-paper"].value
    s = 0
    sc = 0
    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        s += 1/a
        sc += c
        if s == gf:
            v = f'<em>g<sub>F</sub></em>{NBEQ}{gf:0.2f}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td{ec}>{sc}</td>'
        rows[2] += f'<td>{a}</td>'
        rows[3] += f'<td>{1/a:0.2f}</td>'
        rows[4] += f'<td>{i+1}</td>'
        rows[5] += f'<td>{s:0.2f}</td>'
        rows[6] += f'<td{ec}>{s**2:0.2f}</td>'
        rows[7] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest adjusted rank where <em>r<sub>eff</sub></em>(<em>i</em>)<sup>2</sup> ≤ '
               f'Σ<em>C<sub>i</sub></em> is {gf:0.4f}.</p>')
    return outstr


def metric_gf_paper_index() -> Metric:
    m = Metric()
    m.name = "gf-paper"
    m.full_name = "fractional g-index"
    m.html_name = "fractional <em>g-</em>index"
    m.metric_type = FLOAT
    m.example = write_gf_paper_index_example
    equation = (r"$$g_F=\underset{r_{\text{eff}}\left(i\right)}{\max}\left(r_{\text{eff}}\left(i\right)^2 "
                r"\leq \sum\limits_{j=1}^{i}{C_j}\right).$$")
    m.symbol = "<em>g<sub>F</sub></em>"
    m.axis_name = r"$g_F$"
    m.synonyms = ["<em>g<sub>F</sub></em>"]
    m.description = ('<p>The fractional <em>g-</em>index (Egghe 2008) is a variant of the __g-index__ in which ranks '
                     'are normalized by the number of authors and is the <em>g</em> '
                     'equivalent of the __hm-index__. Effective ranks for each publication are '
                     'calculated identically as for <em>h<sub>m</sub></em>. <em>g<sub>F</sub></em> is calculated '
                     f'as:</p>{equation}')
    m.references = ["Egghe, L. (2008) Mathematical theory of the <em>h-</em> and <em>g-</em>index in case of "
                    "fractional counting of authorship. <em>Journal of the American Society for Information Science "
                    "and Technology</em> 59(10):1608&ndash;1616."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_gf_paper_index
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# position-weighted h-index (Abbas 2011)
def calculate_pos_weight_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_position_weighted_h_index(citations, n_authors, author_pos)


def write_pos_weight_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        ap = metric_set.author_position()[i]
        e = Impact_Funcs.author_effort("proportional", a, ap)
        data.append([c*e, c, a, ap, e])
    data.sort(reverse=True)
    cstari = r"\(C^*_i\)"
    rows = ["" for _ in range(8)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Weight (<em>w<sub>i</sub></em>)</th>'
    rows[5] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[6] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[7] = '<tr><th></th>'
    hp = metric_set.metrics["position-weighted h-index"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        ap = d[3]
        e = d[4]
        w = 1/e
        if i + 1 == hp:
            v = f'<em>h<sub>p</sub></em>{NBEQ}{hp}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{ap}</td>'
        rows[3] += f'<td>{e:0.2f}</td>'
        rows[4] += f'<td>{w:0.2f}</td>'
        rows[5] += f'<td{ec}>{cs:1.2f}</td>'
        rows[6] += f'<td{ec}>{i+1}</td>'
        rows[7] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    eq = r"\(i \leq C^*_i\)"
    outstr += f'<p>The largest rank where {eq} is {hp}.</p>'
    return outstr


def metric_pos_weight_h_index() -> Metric:
    m = Metric()
    m.name = "position-weighted h-index"
    m.full_name = "position-weighted h-index"
    m.html_name = "position-weighted <em>h-</em>index"
    m.symbol = "<em>h<sub>p</sub></em>"
    m.axis_name = r"$h_p$"
    m.synonyms = ["<em>h<sub>p</sub></em>"]
    m.example = write_pos_weight_h_index_example
    m.metric_type = INT
    eistr = r"$$E_i=\frac{2\left(A_i+1-a_i\right)}{A_i\left(A_i+1\right)},$$"
    cistr = r"$$C^{*}_i = \frac{C_i}{w_i} = C_i E_i,$$"
    equation = r"$$h_p=\underset{i}{\max}\left(i \leq C^{*}_i\right).$$"
    m.description = ('<p>The position-weighted <em>h-</em>index (Abbas 2011) is similar to the '
                     '__adapt pure h-index prop__ in that it uses an author\'s position to '
                     'weight citation counts prior to ranking, but differs by dividing the raw citation count '
                     'directly by the inverse of the effort rather than the square-root of the effort. The effort is '
                     f'calculated as</p>{eistr}<p>with weight '
                     f'<em>w<sub>i</sub></em>{NBEQ}1/<em>E<sub>i</sub></em>, and the adjusted citation '
                     f'count as</p>{cistr}'
                     '<p>where <em>a<sub>i</sub></em> is the position of the target author within the full author '
                     'list of publication <em>i</em> (<em>i.e.</em>, an integer from 1 to <em>A<sub>i</sub></em>). '
                     'Publications are ranked by these adjusted citation counts and then the metric is calculated '
                     f'as:</p>{equation}')
    m.references = ["Abbas, A.M. (2011) Weighted indices for evaluating the quality of research with multiple "
                    "authorship. <em>Scientometrics</em> 88:107&ndash;131."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pos_weight_h_index
    m.properties["Core Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
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
    m.symbol = "<em>ψ<sub>p</sub></em>"
    m.axis_name = r"$\psi_p$"
    m.synonyms = ["<em>ψ<sub>p</sub></em>"]
    equation = (r"$$\psi_p=\sum\limits_{i=i}^{P}{\frac{C_i}{\frac{A_i\left(A_i+1\right)}{2\left(A_i+1-a_i\right)}}}"
                r"=\sum\limits_{i=i}^{P}{C_i\frac{2\left(A_i+1-a_i\right)}{A_i\left(A_i+1\right)}}$$")
    m.description = ('<p>The proportional weighted citation aggregate (Abbas 2011) is a weighted count of an '
                     'author\'s citations (an alternative to __total cites__), where the weighting is '
                     'based on the total number of authors of each publication and their position within the author '
                     'list (<em>a<sub>i</sub></em>) under an assumption of proportionally decreasing credit with '
                     f'respect to their position.</p>{equation}')
    m.references = ["Abbas, A.M. (2011) Weighted indices for evaluating the quality of research with multiple "
                    "authorship. <em>Scientometrics</em> 88:107&ndash;131."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_prop_weight_cite_agg
    m.properties["Alternative Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# proportional weighted citation h-cut (Abbas 2011)
def calculate_prop_weight_cite_h_cut(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_prop_weight_cite_h_cut(citations, n_authors, author_pos)


def write_prop_weight_cite_h_cut_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        ap = metric_set.author_position()[i]
        e = Impact_Funcs.author_effort("proportional", a, ap)
        data.append([c*e, c, a, ap, e])
    data.sort(reverse=True)
    cstari = r"\(C^*_i\)"
    rows = ["" for _ in range(8)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Author Effort (<em>E<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Weight (<em>w<sub>i</sub></em>)</th>'
    rows[5] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[6] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[7] = '<tr><th></th>'
    hp = metric_set.metrics["position-weighted h-index"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        ap = d[3]
        e = d[4]
        w = 1/e
        if i + 1 == hp:
            v = f'<em>h<sub>p</sub></em>{NBEQ}{hp}'
        else:
            v = ""
        if i + 1 <= hp:
            ec = ' class="box"'
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{ap}</td>'
        rows[3] += f'<td>{e:0.2f}</td>'
        rows[4] += f'<td>{w:0.2f}</td>'
        rows[5] += f'<td{ec}>{cs:1.2f}</td>'
        rows[6] += f'<td>{i+1}</td>'
        rows[7] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    hc = metric_set.metrics["prop weight cite h-cut"].value
    outstr += f'<p>The sum of the adjusted citations for the top <em>h<sub>p</sub></em> publications is {hc}.</p>'
    return outstr


def metric_prop_weight_cite_h_cut() -> Metric:
    m = Metric()
    m.name = "prop weight cite h-cut"
    m.full_name = "weighted citation H-cut (proportional)"
    m.example = write_prop_weight_cite_h_cut_example
    m.metric_type = FLOAT
    m.symbol = "<em>ξ<sub>p</sub></em>"
    m.axis_name = r"$\xi_p$"
    m.synonyms = ["<em>ξ<sub>p</sub></em>"]
    equation = (r"$$\xi_p=\sum\limits_{i=1}^{h_p}{C^{*}_i}"
                r"=\sum\limits_{i=i}^{h_p}{\frac{C_i}{\frac{A_i\left(A_i+1\right)}{2\left(A_i+1-a_i\right)}}}"
                r"=\sum\limits_{i=i}^{h_p}{C_i\frac{2\left(A_i+1-a_i\right)}{A_i\left(A_i+1\right)}}.$$")
    m.description = ('<p>The proportional weighted citation H-cut is the sum of weighted citations found within '
                     'an author\'s core publications, with the core defined by the __position-weighted h-index__'
                     'and the citation weighting using the scheme from the '
                     f'__prop weight cite agg__:</p>{equation}<p>Note that for this metric '
                     'publication order is by the weighted citation counts rather than the raw citation counts.</p>')
    m.references = ["Abbas, A.M. (2011) Weighted indices for evaluating the quality of research with multiple "
                    "authorship. <em>Scientometrics</em> 88:107&ndash;131."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_prop_weight_cite_h_cut
    m.properties["Core Property"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
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
    m.symbol = "<em>ψ<sub>e</sub></em>"
    m.axis_name = r"$\psi_e$"
    m.synonyms = ["<em>ψ<sub>e</sub></em>"]
    equation = r"$$\psi_e=\sum\limits_{i=i}^{P}{\frac{C_i}{A_i}}$$"
    m.description = ('<p>The fractional weighted citation aggregate (Abbas 2011) is a weighted count of an '
                     'author\'s citations (an alternative to __total cites__), where the weighting is '
                     'based on the total number of authors of each publication, with each author receiving '
                     f'equal credit for the publication.</p>{equation}')
    m.references = ["Abbas, A.M. (2011) Weighted indices for evaluating the quality of research with multiple "
                    "authorship. <em>Scientometrics</em> 88:107&ndash;131."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_frac_weight_cite_agg
    m.properties["Alternative Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# fractional weighted citation h-cut (Abbas 2011)
def calculate_frac_weight_cite_h_cut(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_frac_weight_cite_h_cut(citations, n_authors)


def write_frac_weight_cite_h_cut_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c/a, c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr><th></th>'
    hi = metric_set.metrics["normal hi-index"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        if i + 1 == hi:
            v = f'<em>h</em><sub><em>i-</em>norm</sub>{NBEQ}{hi}'
        else:
            v = ""
        if i + 1 <= hi:
            ec = ' class="box"'
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td{ec}>{cs:1.2f}</td>'
        rows[3] += f'<td>{i+1}</td>'
        rows[4] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    hc = metric_set.metrics["frac weight cite h-cut"].value
    outstr += ('<p>The sum of the adjusted citations for the top <em>h</em><sub><em>i-</em>norm</sub> '
               f'publications is {hc}.</p>')
    return outstr


def metric_frac_weight_cite_h_cut() -> Metric:
    m = Metric()
    m.name = "frac weight cite h-cut"
    m.full_name = "weighted citation H-cut (fractional)"
    m.example = write_frac_weight_cite_h_cut_example
    m.metric_type = FLOAT
    m.symbol = "<em>ξ<sub>e</sub></em>"
    m.axis_name = r"$\xi_e$"
    m.synonyms = ["<em>ξ<sub>e</sub></em>"]
    equation = r"$$\xi_e=\sum\limits_{i=i}^{h_{i\text{-norm}}}{\frac{C_i}{A_i}}.$$"
    m.description = ('<p>The fractional weighted citation H-cut is the sum of weighted citations found within '
                     'an author\'s core publications, with the core defined by the __normal hi-index__ '
                     'and the citation weighting using the scheme from the '
                     f'__frac weight cite agg__:</p>{equation}<p>Note that for this metric '
                     'publication order is by the weighted citation counts rather than the raw citation counts.</p>')
    m.references = ["Abbas, A.M. (2011) Weighted indices for evaluating the quality of research with multiple "
                    "authorship. <em>Scientometrics</em> 88:107&ndash;131."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_frac_weight_cite_h_cut
    m.properties["Core Property"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# h-rate (Hirsch m-quotient)
def calculate_h_rate(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_h_rate(h, age)


# def write_h_rate_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h-rate"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Year', 'h-index', 'slope (m)'],\n")
#     all_sets = metric_set.parent_list
#     last_set = all_sets.index(metric_set)
#     h = []
#     year = []
#     for s in all_sets[:last_set+1]:
#         year.append(s.year())
#         h.append(s.metrics["h-index"].value)
#     max_year = max(year)
#     min_year = min(year) - 1
#     # write h-indices per year
#     for i in range(len(h)):
#         output.append("           [{}, {}, null],\n".format(year[i], h[i]))
#     # write line through final point
#     # m = metric.value
#     output.append("           [{}, null, {}],\n".format(min_year, 0))
#     output.append("           [{}, null, {}],\n".format(max_year, metric_set.metrics["h-index"].value))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'none'},\n")
#     output.append("		     hAxis: { format: \'#\',\n")
#     output.append("		             title: \'Year\',\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     vAxis: {title: \'h-index\'},\n")
#     output.append("		     series: { 0: {pointsVisible: true, pointSize: 8, lineWidth: 0},\n")
#     output.append("		               1: {lineDashStyle: [4, 4]}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#     return output


def create_h_rate_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    # get data
    all_sets = metric_set.parent_list
    last_set = all_sets.index(metric_set)
    h = []
    year = []
    for s in all_sets[:last_set+1]:
        year.append(s.year())
        h.append(s.metrics["h-index"].value)
    max_year = max(year)
    min_year = min(year) - 1

    # data points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = year
    point_data.y = h

    # slope
    slope_data = Impact_Graphs.LineData()
    output.append(slope_data)
    slope_data.x = [min_year, max_year]
    slope_data.y = [0, max(h)]
    slope_data.style = ":"

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Year"
    general_data.y_label = r"$h\text{-index}$"
    general_data.equal_axes = False

    return output


def metric_h_rate() -> Metric:
    m = Metric()
    m.name = "h-rate"
    m.full_name = "h-rate"
    m.html_name = "<em>h-</em>rate"
    m.symbol = "<em>m</em>"
    m.axis_name = r"$m$"
    m.metric_type = FLOAT
    m.synonyms = ["<em>m-</em>quotient",
                  "<em>m-</em>ratio index",
                  "age-normalized <em>h-</em>index",
                  "Carbon <em>h-</em>factor"]
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h_rate_desc"
    graph.data = create_h_rate_desc_graph_data
    m_equation = r"$$m=\frac{h}{Y-Y_{0}+1},$$"
    hstr = r"\(h\)"
    ystr = r"\(Y\)"
    y0str = r"\(Y_{0}\)"
    m.description = ('<p>Originaly defined by Hirsch (2005), this metric is also known as the '
                     '<span class="metric_name"><em>m-</em>quotient,</span> '
                     '<span class="metric_name"><em>m-</em>ratio index,</span> '
                     '<span class="metric_name">age-normalized <em>h-</em>index,</span> and '
                     '<span class="metric_name">Carbon <em>h-</em>factor.</span> It measures the rate at which the '
                     '__h-index__ has increased over the career of a researcher. It is calculated simply as:</p>'
                     f'{m_equation}<p>where {hstr} is the <em>h-</em>index in year {ystr} and {y0str}'
                     ' is the year of the researcher\'s first publication (the denominator of this equation is the '
                     'academic age of the researcher).</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>'
                     '<p>The above estimation is essentially just the slope of the line from the start of a '
                     'researcher\'s career (0 publications, 0 citations) through the most recent estimate of their '
                     '<em>h-</em>index.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h_rate
    m.properties["Core Property"] = True
    m.properties["Time"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# least-squares h-rate
def calculate_ls_h_rate(metric_set: MetricSet) -> float:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    h_list = [m.metrics["h-index"].value for m in metric_list[:metric_pos+1]]
    year_list = [m.year() for m in metric_list[:metric_pos+1]]
    return Impact_Funcs.calculate_least_squares_h_rate(year_list, h_list)


# def write_ls_h_rate_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["ls h-rate"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Year', 'h-index', 'slope (m)'],\n")
#     all_sets = metric_set.parent_list
#     last_set = all_sets.index(metric_set)
#     h = []
#     year = []
#     for s in all_sets[:last_set+1]:
#         year.append(s.year())
#         h.append(s.metrics["h-index"].value)
#     max_year = max(year)
#     min_year = min(year)
#     m = metric.value
#     y = m * (max_year - min_year + 1)
#     # write h-indices per year
#     for i in range(len(h)):
#         output.append("           [{}, {}, null],\n".format(year[i], h[i]))
#     # write line
#     output.append("           [{}, null, {}],\n".format(min_year - 1, 0))
#     output.append("           [{}, null, {}],\n".format(max_year, y))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'none'},\n")
#     output.append("		     hAxis: { format: \'#\',\n")
#     output.append("		             title: \'Year\',\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     vAxis: {title: \'h-index\'},\n")
#     output.append("		     series: { 0: {pointsVisible: true, pointSize: 8, lineWidth: 0},\n")
#     output.append("		               1: {lineDashStyle: [4, 4]}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#     return output

def create_ls_h_rate_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    # get data
    all_sets = metric_set.parent_list
    last_set = all_sets.index(metric_set)
    h = []
    year = []
    for s in all_sets[:last_set+1]:
        year.append(s.year())
        h.append(s.metrics["h-index"].value)
    max_year = max(year)
    min_year = min(year)

    # data points
    point_data = Impact_Graphs.PointData()
    output.append(point_data)
    point_data.x = year
    point_data.y = h

    # slope
    m = metric_set.metrics["ls h-rate"].value
    y1 = m * (max_year - min_year + 1)

    slope_data = Impact_Graphs.LineData()
    output.append(slope_data)
    slope_data.x = [min_year-1, max_year]
    slope_data.y = [0, y1]
    slope_data.style = ":"

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Year"
    general_data.y_label = r"$h\text{-index}$"
    general_data.equal_axes = False

    return output


def metric_ls_h_rate() -> Metric:
    m = Metric()
    m.name = "ls h-rate"
    m.full_name = "least squares h-rate"
    m.html_name = "least squares <em>h-</em>rate"
    m.symbol = "<em>m<sub>ls</sub></em>"
    m.axis_name = r"$m_{ls}$"
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "ls_h_rate_desc"
    graph.data = create_ls_h_rate_desc_graph_data
    m.metric_type = FLOAT
    m.description = ('<p>Hirsch\'s original estimate of the __h-rate__ was based on a single data point, '
                     'the most recently measured value of the __h-index__ and the time since first publication. '
                     'Burrell (2007) suggested that a more accurate measure could be estimated through least-squares '
                     'regression of a series of <em>h-</em>indices measured at different time points of an '
                     'author\'s career, while forcing the intercept through zero at the start of their career (prior '
                     'to first publication).</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Burrell, Q.L. (2007) Hirsch index or Hirsch rate? Some thoughts arising from Liang's data. "
                    "<em>Scientometrics</em> 73(1):19-28."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_ls_h_rate
    m.properties["Core Property"] = True
    m.properties["Time"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# time-scaled h-index (Todeschini and Baccini 2016)
def calculate_time_scaled_h_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_time_scaled_h_index(h, age)


def metric_time_scaled_h_index() -> Metric:
    m = Metric()
    m.name = "time-scaled h-index"
    m.full_name = "time-scaled h-index"
    m.html_name = "time-scaled <em>h-</em>index"
    m.symbol = "<em>h<sup>TS</sup></em>"
    m.axis_name = r"$h^{TS}$"
    m.synonyms = ["<em>h<sup>TS</sup></em>"]
    m.metric_type = FLOAT
    equation = r"$$h^{TS}=\frac{h}{\sqrt{Y-Y_0+1}}.$$"
    m.description = ('<p>The time-scaled <em>h-</em>index (Mannella and Rossi 2013) is a variant of the '
                     '__h-rate__ calculated over the square-root of the academic age of the researcher:</p>' +
                     equation)
    m.references = ["Mannella, R., and P. Rossi (2013) On the time dependence of the <em>h-</em>index. <em>Journal "
                    "of Informetrics</em> 7:176&ndash;182."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_time_scaled_h_index
    m.properties["Core Property"] = True
    m.properties["All Publications"] = True
    m.properties["Time"] = True
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
    m.symbol = "<em>α</em>"
    m.axis_name = r"$\alpha$"
    m.synonyms = ["<em>α-</em>index"]
    m.metric_type = FLOAT
    equation = r"$$\alpha = \frac{h}{Y_D},$$"
    yd = r"$$Y_D = \text{ceiling}\left( \frac{Y-Y_0+1}{10}\right).$$"
    m.description = ('<p>The <em>α-</em>index (Abt 2012; Burrell 2012; Sangwal 2012) is a variant of the '
                     '__h-rate__ where the __h-index__ is divided by number of decades since an author\'s first '
                     f'publication, or</p>{equation}<p>where</p>{yd}')
    m.references = ["Abt, H.A. (2012) A publication index that is independent of age. <em>Scientometrics</em> "
                    "91:863&ndash;868.",
                    "Burrell, Q.L. (2012) Comments on \"A publication index that is independent of age\" by Abt. "
                    "<em>Scientometrics</em> 91:1059&ndash;1060.",
                    "Sangwal, K. (2012) On the age-independent publication index. <em>Scientometrics</em> "
                    "91:1053&ndash;1058."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_alpha_index
    m.properties["Core Property"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    return m


# ar-index (Jin 2007; Jin et al. 2007)
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
    m.symbol = "<em>ar</em>"
    m.axis_name = r"$ar$"
    m.metric_type = FLOAT
    equation = r"$$ar=\sqrt{\sum\limits_{i=1}^{h}{\frac{C_i}{Y-Y_i+1}}},$$"
    m.description = ('<p>The <em>ar-</em>index (Jin 2007; Jin <em>et al.</em> 2007) is an adaptation of the '
                     '__R-index__ which includes time. Rather than being the square-root of the total '
                     'citations within the core, it is the square-root of the citations per year within the '
                     f'core,</p>{equation}<p>where <em>Y</em> is the current year.</p>')
    m.references = ["Jin, B. (2007) The <em>ar-</em>index: Complementing the <em>h-</em>index. "
                    "<em>ISSI</em> Newsletter 3(1):6.",
                    "Jin, B., L. Liang, R. Rousseau, and L. Egghe (2007) The <em>R-</em> and <em>AR-</em>indices: "
                    "Complementing the <em>h-</em>index. <em>Chinese Science Bulletin</em> 52(6):855&ndash;863."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_ar_index
    m.properties["Time"] = True
    m.properties["Core Property"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# dynamic h-type-index
def calculate_dynamic_h_type_index(metric_set: MetricSet) -> Union[str, float]:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    rational_h_list = [m.metrics["rational h-index"].value for m in metric_list[:metric_pos + 1]]
    year_list = [m.year() for m in metric_list[:metric_pos + 1]]
    r = metric_set.metrics["R-index"].value
    return Impact_Funcs.calculate_dynamic_h_type_index(rational_h_list, year_list, r)


def metric_dynamic_h_type_index() -> Metric:
    m = Metric()
    m.name = "dynamic h-type-index"
    m.full_name = "dynamic h-type-index"
    m.html_name = "dynamic <em>h-</em>type-index"
    m.symbol = "<em>h<sub>dyn</sub></em>"
    m.metric_type = FLOAT_NA
    eq1 = r"$$h_{dyn}=R\times v_h,$$"
    m.description = ('<p>The dynamic <em>h-</em>type index (Rousseau and Ye 2008) is a measure of both the size of '
                     f'the core as well as how the core is changing through time. The basic index is</p>{eq1}'
                     'where <em>R</em> is the __R-index__ and <em>v<sub>h</sub></em> is a measure of the rate of '
                     'change of the __h-index__ through time. Rousseau and Ye (2008) suggest a number of ways to '
                     'estimate <em>v<sub>h</sub></em>, including that it be determined over a fixed time '
                     'interval (<em>e.g.</em>, 5 or 10 years) to make it more contemporary. They also suggest one '
                     'use the rational <em>h</em> rather than <em>h</em> because its finer grained resolution will '
                     'allow for better estimates of the rate of change of <em>h.</em></p><p>Here '
                     '<em>v<sub>h</sub></em> for a given year is estimated as the slope of the regression of the '
                     'rational <em>h-</em>index against year for all data points up through that year.</p>')
    m.references = ["Rousseau, R., and F.Y. Ye (2008) A proposal for a dynamic <em>h-</em>type index. "
                    "<em>Journal of the American Society for Information Science and Technology</em> "
                    "59(11):1853&ndash;1855."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_dynamic_h_type_index
    m.properties["Core Property"] = True
    m.properties["Compound Metric"] = True
    m.properties["Time"] = True
    return m


# hpd-index (Kosmulski 2009)
def calculate_hpd_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    return Impact_Funcs.calculate_hpd_index(citations, pub_years, year)


def write_hpd_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    cur_year = metric_set.year()
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        age = cur_year - metric_set.publication_years()[i] + 1
        s = 10*c/age
        data.append([s, c, age])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = f'<tr><th>Age (<em>Y</em>&nbsp;&minus;&nbsp;<em>Y<sub>i</sub></em>{NBPLUS}1)</th>'
    rows[2] = '<tr class="top_row"><th>Adjusted Citations (<em>cpd<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr><th></th>'
    hpd = metric_set.metrics["hpd-index"].value
    for i, d in enumerate(data):
        cpd = d[0]
        c = d[1]
        y = d[2]
        if i + 1 == hpd:
            v = f'<em>hpd</em>{NBEQ}{hpd}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{y}</td>'
        rows[2] += f'<td{ec}>{cpd:1.2f}</td>'
        rows[3] += f'<td{ec}>{i+1}</td>'
        rows[4] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em> ≤ <em>cpd<sub>i</sub></em> is {hpd}.</p>'
    return outstr


def metric_hpd_index() -> Metric:
    m = Metric()
    m.name = "hpd-index"
    m.full_name = "hpd-index"
    m.html_name = "<em>hpd-</em>index"
    m.symbol = "<em>hpd</em>"
    m.axis_name = r"$hpd$"
    m.example = write_hpd_index_example
    m.metric_type = INT
    cpd = r"$$cpd_i=\frac{10C_i}{Y-Y_i+1}$$"
    equation = r"$$hpd=\underset{i}{\max}\left(i \leq cpd_i\right)$$"
    m.description = ('<p>The hpd-index (Kosmulski 2009) is very similar to the __h-index__, except that it '
                     'adjusts for the age of a publication. Rather than adjust per year, the metric is adjusted per '
                     f'decade. Thus if</p>{cpd}<p>is the number of citations an article has per decade (where '
                     '<em>Y</em> is the current year), then '
                     'the <em>hpd-</em>index for an author is the largest rank for which <em>hpd</em> of their '
                     'publications (ranked by <em>cpd<sub>i</sub></em> rather than <em>C<sub>i</sub></em>) have '
                     f'<em>cpd</em> ≥ <em>hpd.</em></p>{equation}')
    m.references = ["Kosmulski, M. (2009) New seniority-independent Hirsch-type index. <em>Journal of "
                    "Informetrics</em> 3:341&ndash;347."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hpd_index
    m.properties["Time"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# contemporary h-index (Sidiropoulos et al. 2007)
def calculate_contemporary_h_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    return Impact_Funcs.calculate_contemporary_h_index(citations, pub_years, year)


def write_contemporary_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    cur_year = metric_set.year()
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        age = cur_year - metric_set.publication_years()[i] + 1
        s = 4*c/age
        data.append([s, c, age])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = f'<tr><th>Age (<em>Y</em>&nbsp;&minus;&nbsp;<em>Y<sub>i</sub></em>{NBPLUS}1)</th>'
    scstr = r"\(S^{C}_i\)"
    rows[2] = f'<tr class="top_row"><th>Adjusted Citations ({scstr})</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr><th></th>'
    hc = metric_set.metrics["contemporary h-index"].value
    for i, d in enumerate(data):
        sc = d[0]
        c = d[1]
        y = d[2]
        if i + 1 == hc:
            v = f'<em>h<sup>C</sup></em>{NBEQ}{hc}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{y}</td>'
        rows[2] += f'<td{ec}>{sc:1.2f}</td>'
        rows[3] += f'<td{ec}>{i+1}</td>'
        rows[4] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    sceq = r"\(i \leq S^{C}_i\)"
    outstr += f'<p>The largest rank where {sceq} is {hc}.</p>'
    return outstr


def metric_contemporary_h_index() -> Metric:
    m = Metric()
    m.name = "contemporary h-index"
    m.full_name = "contemporary h-index"
    m.html_name = "contemporary <em>h-</em>index"
    m.symbol = "<em>h<sup>C</sup></em>"
    m.axis_name = r"$h^C$"
    m.synonyms = ["<em>h<sup>C</sup></em>"]
    m.example = write_contemporary_h_index_example
    m.metric_type = INT
    sceq = r"$$S^C_i=\gamma \left(Y-Y_i+1\right)^{-\delta}C_i.$$"
    hceq = r"$$h^C=\underset{i}{\max}\left(i \leq S^C_i\right)$$"
    m.description = ('<p>The contemporary <em>h-</em>index (Sidiropoulos <em>et al.</em> 2007) is designed to give '
                     'more weight to the citations of recent publications and less weight to the citations of '
                     'older publications. In its most general form, the contemporary score for a specific publication '
                     f'is</p>{sceq}<p>The contemporary <em>h-</em>index for an author, <em>h<sup>C</sup></em>, '
                     'is calculated similarly to the standard <em>h-</em>index, in that an author has a score of '
                     '<em>h<sup>C</sup></em> if <em>h<sup>C</sup></em> of their articles (ranked by '
                     f'<em>S<sup>C</sup></em>) have <em>S<sup>C</sup></em> ≥ <em>h<sup>C</sup></em>.</p>{hceq}'
                     'Sidiropuolos <em>et al.</em> (2007) set <em>γ</em> = 4 and <em>δ</em> = 1. These choices have '
                     'the consequence of making this metric virtually identical to the __hpd-index__, except measured '
                     'on a four year cycle rather than a decade.</p>')
    m.references = ["Sidiropoulos, A., D. Katsaros, and Y. Manolopoulos (2007) Generalized Hirsch <em>h-</em>index "
                    "for disclosing latent facts in citation networks. <em>Scientometrics</em> 72(2):253&ndash;280."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_contemporary_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Time"] = True
    return m


# trend h-index
def calculate_trend_h_index(metric_set: MetricSet) -> int:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    return Impact_Funcs.calculate_trend_h_index(pub_data)


def write_trend_h_index_example(metric_set: MetricSet) -> str:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    year_list = [m.year() for m in metric_list[:metric_pos+1]]
    ny = len(pub_data[0])
    # take total citations for each pub at each year and convert to yearly only totals
    pub_cites = []
    for p in pub_data:
        cites = [p[0]]
        for i in range(1, len(p)):
            if p[i-1] is None:
                cites.append(p[i])
            else:
                cites.append(p[i] - p[i-1])
        pub_cites.append(cites)
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i, p in enumerate(pub_cites):
        s = 0
        for y, c in enumerate(p):
            if c is not None:
                s += c / (ny - y)
        s *= 4
        c = metric_set.citations[i]
        pdata = [s, c]
        for c in p:
            if c is None:
                c = -1
            pdata.append(c)
        data.append(pdata)
    data.sort(reverse=True)
    middle_rows = []
    for y in range(ny):
        if y + 1 == ny:
            ec = ' class="top_row"'
        else:
            ec = ""
        row = f'<tr{ec}><th>&mdash;{year_list[y]}&mdash;</th>'
        for d in data:
            c = d[y+2]
            if c == -1:
                c = '&mdash;'
            row += f'<td>{c}</td>'
        # row += '</tr>\n'
        middle_rows.append(row)

    outer_rows = ["" for _ in range(4)]
    outer_rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    ststr = r"\(S^{t}_i\)"
    outer_rows[1] = f'<tr class="top_row"><th>Adjusted Citations ({ststr})</th>'
    outer_rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    outer_rows[3] = '<tr><th></th>'
    ht = metric_set.metrics["trend h-index"].value
    for i, d in enumerate(data):
        sc = d[0]
        c = d[1]
        if i + 1 == ht:
            v = f'<em>h<sup>C</sup></em>{NBEQ}{ht}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        outer_rows[0] += f'<td>{c}</td>'
        outer_rows[1] += f'<td{ec}>{sc:1.2f}</td>'
        outer_rows[2] += f'<td{ec}>{i+1}</td>'
        outer_rows[3] += f'<td>{v}</td>'
    all_rows = [outer_rows[0]]
    all_rows.extend(middle_rows)
    all_rows.extend(outer_rows[1:])

    for row in all_rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(all_rows) + '</table>\n'
    steq = r"\(i \leq S^{t}_i\)"
    outstr += f'<p>The largest rank where {steq} is {ht}.</p>'
    return outstr


def metric_trend_h_index() -> Metric:
    m = Metric()
    m.name = "trend h-index"
    m.full_name = "trend h-index"
    m.html_name = "trend <em>h-</em>index"
    m.symbol = "<em>h<sup>t</sup></em>"
    m.axis_name = r"$h^t$"
    m.synonyms = ["<em>h<sup>t</sup></em>"]
    m.example = write_trend_h_index_example
    m.metric_type = INT
    steq = r"$$S^t_i = \gamma \sum\limits_{j=1}^{C_i}{\left(Y-Y_{j.i}+1\right)^{-\delta}}$$"
    st2eq = r"$$S^t_i = \gamma \sum\limits_{k=1}^{Y}{C_{i.k}\left(Y-Y_k+1\right)^{-\delta}}.$$"
    hteq = r"$$h^t = \underset{i}{\max}\left(i \leq S^t_i\right)$$"
    m.description = ('<p>The trend <em>h-</em>index (Sidiropoulos <em>et al.</em> 2007) is essentially the '
                     'opposite of the __contemporary h-index__. It is designed to measure how current an '
                     'author\'s impact is by how recently they are being cited. The trend score for a publication '
                     f'is measured as</p>{steq}<p>where <em>γ</em> and <em>δ</em> are parameters '
                     '(often set to 4 and 1, respectively, just as with the contemporary <em>h-</em>index) and '
                     '<em>Y<sub>j.i</sub></em> is the year of the <em>j</em><sup>th</sup> citation for publication '
                     '<em>i.</em> If the number of citations for publication <em>i</em> in year '
                     f'<em>Y<sub>k</sub></em> is <em>C<sub>i.k</sub></em>, this can also be written as {st2eq}'
                     'The trend <em>h-</em>index is the largest value '
                     'for which an author has <em>h<sup>t</sup></em> publications with at least '
                     f'<em>S<sup>t</sup></em> ≥ <em>h<sup>t</sup></em>.</p>{hteq}')
    m.references = ["Sidiropoulos, A., D. Katsaros, and Y. Manolopoulos (2007) Generalized Hirsch <em>h-</em>index "
                    "for disclosing latent facts in citation networks. <em>Scientometrics</em> 72(2):253&ndash;280."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_trend_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Time"] = True
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
    m.symbol = "<em>IV</em>"
    m.metric_type = FLOAT_NA
    equation = (r"$$IV\left(w\right)=\frac{w\left(\frac{\sum\limits_{i=1}^{w}{\frac{c^{Y-w}}{i}}}"
                r"{\sum\limits_{i=1}^{w}{c^{Y-w}}} \right)-1 }{\left(\sum\limits_{i=1}^{w}{\frac{1}{i} } \right)-1}.$$")
    m.description = ('<p>Impact Vitality (Rons and Amez 2008, 2009) is similar in concept to the __trend h-index__, '
                     'but more complicated to measure. If <em>c<sup>x</sup></em> is the total '
                     'number of citations (across all publications) from year <em>x,</em> and <em>w</em> is the '
                     'number of years back from the present (year <em>Y</em>) one wishes to calculate the metric for '
                     '(the citation window), '
                     f'then</p>{equation}<p>The numerator of the numerator is the sum of citation counts divided '
                     'by their age for the window of time in question; the denominator of the numerator is the total '
                     'number of citations for the same window of time. An impact vitality score of 1 indicates '
                     'that the number of citations is approximately constant over time. A value above 1 indicates '
                     'that the number of citations is increasing through time, while a value below 1 indicates '
                     'the number of citations is decreasing through time. Individuals with very different total '
                     'numbers of citations can have identical scores because the metric is focused on '
                     'proportional change and not absolute numbers. However, even beyond the issues of more '
                     'difficult data collection, this metric has odd properties because of its overwhelming '
                     'focus on immediacy. It would produce a higher score for someone with just 1 citation a year '
                     'ago and no citations 2 years ago than another person with 1,000 citations 2 years ago and no '
                     'citations one year ago.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_impact_vitality
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Alternative Metric"] = True
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
    m.symbol = "<em>s</em>"
    m.axis_name = r"$S$"
    m.synonyms = ["<em>s</em>-index (specific impact)"]
    m.metric_type = FLOAT
    equation = (r"$$S=\frac{C^P}{10\sum\limits_{i=1}^{P}{\left(1-e^{0.1\left(Y-Y_i\right)}\right)}}=\frac"
                r"{\sum\limits_{i=1}^{P}{C_i}}{10\sum\limits_{i=1}^{P}{\left(1-e^{0.1\left(Y-Y_i\right)}\right)}},$$")
    m.description = ('<p>The specific-impact <em>s-</em>index (De Visscher 2010) is designed to avoid the '
                     'age-bias of other indices as well as not penalizing fields where citations may lag due to '
                     'the speed of the publication process. It is designed to predict the total number of citations '
                     'a set of publications will have at a time infinitely in the future, assuming exponential '
                     'aging of the citation process. The <em>s-</em>index is a measure of the projected citation '
                     'rate per publication (rather than the actual citation rate per publication). The practical '
                     f'definition is</p>{equation}<p>where <em>s</em> is a measure of the citation rate '
                     'per publication (divided by 10) projected to time infinity. The actual prediction of the '
                     'total number of citations an author would have at time infinity would therefore be '
                     '10<em>sP</em>.</p>')
    m.references = ["De Visscher, A. (2010) An index to measures a scientist's specific impact. <em>Journal of the "
                    "American Society for Information Science and Technology</em> 61(2):319&ndash;328."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_specific_impact_s_index
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
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
    m.symbol = "<em>f</em>"
    m.axis_name = r"$f$"
    m.metric_type = INT
    equation = r"$$f=\max\left(Y_i|C_i>0\right) - \min\left(Y_i|C_i>0\right) + 1,$$"
    m.description = ('<p>Franceschini and Maisano\'s <em>f-</em>index (Franceschini and Maisano 2010) is designed as '
                     'a complement to the __h-index__. It is a measure of the time-width of impact. It is the '
                     f'range of time for publications with at least one citation and is calculated as</p>{equation}'
                     '<p>or the year of the most recent publication with at least one citation minus the year of '
                     'the earliest publication with at least one citation (plus one to consider the time spent '
                     'preparing the earliest publication). For most active researchers, this will likely be simply '
                     'the number of years since they first published since it will most often be the difference '
                     'in age between their first publication (which probably has at least one citation) and their '
                     'most recent publication to get a single citation (probably published within the last year or '
                     'two).</p>')
    m.references = ["Franceschini, F., and D.A. Maisano (2010) Analysis of the Hirsch index's operational "
                    "properties. <em>European Journal of Operational Research</em> 203:494&ndash;504."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_franceschini_f_index
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Time"] = True
    return m


# annual h-index (hIa) (Harzing et al. 2014)
def calculate_annual_h_index(metric_set: MetricSet) -> float:
    norm_h = metric_set.metrics["normal hi-index"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_annual_h_index(norm_h, age)


def metric_annual_h_index() -> Metric:
    m = Metric()
    m.name = "annual h-index"
    m.full_name = "annual h-index"
    m.html_name = "annual <em>h</em>-index"
    m.symbol = "hIa"
    m.synonyms = ["hIa"]
    m.metric_type = FLOAT
    equation = r"$$\text{hIa} = \frac{h_i}{Y-Y_0+1}.$$"
    m.description = ('<p>The annual <em>h</em>-index attempts to normalize by both the number of coauthors of each '
                     'publication as well as the academic age of the researcher and is calculated as the '
                     f'__normal hi-index__ divided by academic age, or:</p>{equation}')
    m.references = ["Harzing, A.-W., S. Alakangas, and D. Adams (2014) hIa: an individual annual <em>h-</em>index "
                    "to accommodate disciplinary and career length differences. <em>Scientometrics</em> "
                    "99:811&ndash;821."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_annual_h_index
    m.properties["Coauthorship"] = True
    m.properties["Time"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# CDS index (Vinkler 2011, 2013)
def calculate_cds_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_cds_index(citations)


def write_cds_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    row1 = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    for c in citations:
        row1 += f'<td>{c}</td>'
    row1 += '</tr>\n'
    outstr += row1 + '</table>\n'

    outstr += ('<p></p><table class="cds_table">'
               '<tr><th>Category<br/>(<em>k</em>)</th><th>Citation<br/>Range</th><th>Count of Pubs<br/>in '
               'Range<br/>(<em>P<sup>k</sup></em>)</th><th><em>kP<sup>k</sub></em></th></tr>')
    max_cites = max(citations)
    nc = 1
    while max_cites > 2**nc:
        nc += 1
    for i in range(nc):
        if i == 0:
            low = 0
            high = 1
        elif i == 1:
            low = 2
            high = 4
        else:
            low = 2**i + 1
            high = 2**(i+1)
        x = 0
        for c in citations:
            if (c >= low) and (c <= high):
                x += 1
        outstr += f'<tr><td>{i+1}</td><td>{low}&ndash;{high}</td><td>{x}</td><td>{(i+1)*x}</td></tr>'
    outstr += '</table>'
    cds = metric_set.metrics["CDS-index"].value
    outstr += f'<p>The index is the sum of <em>kP<sup>k</sub></em>, thus CDS{NBEQ}{cds}.</p>'
    return outstr


def metric_cds_index() -> Metric:
    m = Metric()
    m.name = "CDS-index"
    m.full_name = "citation distribution score index"
    m.symbol = "CDS"
    m.axis_name = r"$CDS$"
    m.synonyms = ["CDS-index"]
    m.example = write_cds_index_example
    m.metric_type = INT
    table = ('<table class="cds_table">'
             '<tr><th>Category</th><th>Range of<br/>Citations</th>'
             '<th>Minimum<br/>Citations</th><th>Maximum<br/>Citations</th></tr>'
             '<tr><td>1</td><td>0&ndash;2<sup>0</sup></td><td>0</td><td>1</td></tr>'
             '<tr><td>2</td><td>(2<sup>0</sup>+1)&ndash;2<sup>2</sup></td><td>2</td><td>4</td></tr>'
             '<tr><td>3</td><td>(2<sup>2</sup>+1)&ndash;2<sup>3</sup></td><td>5</td><td>8</td></tr>'
             '<tr><td>4</td><td>(2<sup>3</sup>+1)&ndash;2<sup>4</sup></td><td>9</td><td>16</td></tr>'
             '<tr><td>5</td><td>(2<sup>4</sup>+1)&ndash;2<sup>5</sup></td><td>17</td><td>32</td></tr>'
             '<tr><td>6</td><td>(2<sup>5</sup>+1)&ndash;2<sup>6</sup></td><td>33</td><td>64</td></tr>'
             '<tr><td>7</td><td>(2<sup>6</sup>+1)&ndash;2<sup>7</sup></td><td>65</td><td>128</td></tr>'
             '<tr><td>8</td><td>(2<sup>7</sup>+1)&ndash;2<sup>8</sup></td><td>129</td><td>256</td></tr>'
             '<tr><td>9</td><td>(2<sup>8</sup>+1)&ndash;2<sup>9</sup></td><td>257</td><td>512</td></tr>'
             '<tr><td>10</td><td>(2<sup>9</sup>+1)&ndash;2<sup>10</sup></td><td>513</td><td>1024</td></tr>'
             '<tr><td>11</td><td>(2<sup>10</sup>+1)&ndash;2<sup>11</sup></td><td>1025</td><td>2048</td></tr>'
             '<tr><td>12</td><td>(2<sup>11</sup>+1)&ndash;2<sup>12</sup></td><td>2049</td><td>4096</td></tr>'
             '<tr><td>13</td><td>(2<sup>12</sup>+1)&ndash;2<sup>13</sup></td><td>4097</td><td>8192</td></tr>'
             '<tr><td>14</td><td>(2<sup>12</sup>+1)&ndash;&#x221e;</td><td>>8192</td><td>&#x221e;</td></tr>'
             '</table>')
    equation = r"$$\text{CDS}=\sum\limits_{k=1}^{14}{k P^k}.$$"
    m.description = ('<p>The citation distribution score index (Vinkler 2011, 2013) is a weighted sum of publication '
                     'counts in a set of pre-defined citation-count-based categories. The 14 categories are '
                     'defined predominantly by their upper limits, with the <em>k</em><sup>th</sup> category usually '
                     'having an upper limits of 2<sup><em>k</em></sup> citations, except for the first category '
                     'which has an upper limit of 2<sup>0</sup> = 1 citation, and the last category, which has no '
                     f'upper limit.</p>{table}<p>The rank of each category is also its weight. If '
                     '<em>P<sup>k</sup></em> is the count of publications '
                     f'within the <em>k</em><sup>th</sup> category, then the index is calculated as</p>{equation}')
    m.references = ["Vinkler, P. (2011) Application of the distribution of citations among publications in "
                    "scientometric evaluations. <em>Journal of the American Society for Information Science "
                    "and Technology</em> 62(10):1963&ndash;1978.",
                    "Vinkler, P. (2013) Would it be possible to increase the Hirsch-index, <em>π-</em>index or "
                    "CDS-index by increasing the number of publications or citations only by unity? <em>Journal of "
                    "Informetrics</em> 7(1):72&ndash;83."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_cds_index
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# CDR index (Vinkler 2011, 2013)
def calculate_cdr_index(metric_set: MetricSet) -> float:
    total_pubs = metric_set.metrics["total pubs"].value
    cds = metric_set.metrics["CDS-index"].value
    return Impact_Funcs.calculate_cdr_index(total_pubs, cds)


def metric_cdr_index() -> Metric:
    m = Metric()
    m.name = "CDR-index"
    m.full_name = "citation distribution rate index"
    m.synonyms = ["CDR-index"]
    m.symbol = "CDR"
    m.axis_name = r"$CDR$"
    m.metric_type = FLOAT
    equation = r"$$\text{CDR}=100\frac{\text{CDS}}{\text{CDS}_\max}=100\frac{\text{CDS}}{14P}.$$"
    m.description = ('<p>The citation distribution rate index (Vinkler 2011, 2013) is a complement to '
                     'the __CDS-index__, calculated as the percent of the maximum possible CDS '
                     f'index actually observed, or</p>{equation}')
    m.references = ["Vinkler, P. (2011) Application of the distribution of citations among publications in "
                    "scientometric evaluations. <em>Journal of the American Society for Information Science "
                    "and Technology</em> 62(10):1963&ndash;1978.",
                    "Vinkler, P. (2013) Would it be possible to increase the Hirsch-index, <em>π-</em>index or "
                    "CDS-index by increasing the number of publications or citations only by unity? <em>Journal of "
                    "Informetrics</em> 7(1):72&ndash;83."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_cdr_index
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# circular citation area radius (Sangwal 2012)
def calculate_circ_cite_area_radius(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_circ_cite_area_radius(total_cites)


def metric_circ_cite_area_radius() -> Metric:
    m = Metric()
    m.name = "circ cite area radius"
    m.full_name = "circular citation area radius"
    m.symbol = "r"
    m.axis_name = r"$r$"
    m.metric_type = FLOAT
    equation = r"$$r=\sqrt{\frac{C^P}{\pi}}=\sqrt{\frac{\sum\limits_{i=1}^{P}{C_i}}{\pi}}$$"
    m.description = ('<p>The circular citation area radius (Sangwal 2012) is an easy to calculate approximation of '
                     f'the __h-index__.</p>{equation}')
    m.references = ["Sangwal, K. (2012) On the relationship between citations of publication output and Hirsch "
                    "index <em>h</em> of authors: Conceptualization of tapered Hirsch index <em>h<sub>T</sub></em>, "
                    "circular citation area radius <em>R</em> and ciation acceleration <em>a.</em> "
                    "<em>Scientometrics</em> 93:987&ndash;1004."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_circ_cite_area_radius
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
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
    m.symbol = "<em>a</em>"
    m.axis_name = r"$a$"
    m.metric_type = FLOAT
    equation = r"$$a = \frac{C^P}{\left(Y-Y_0+1\right)^2}=\frac{\sum\limits_{i=1}^{P}{C_i}}{\left(Y-Y_0+1\right)^2}.$$"
    m.description = ('<p>Citation acceleration (Sangwal 2012) is defined as the total number of citations of an '
                     f'author divided by the square of their academic age,</p>{equation}')
    m.references = ["Sangwal, K. (2012) On the relationship between citations of publication output and Hirsch "
                    "index <em>h</em> of authors: Conceptualization of tapered Hirsch index <em>h<sub>T</sub></em>, "
                    "circular citation area radius <em>R</em> and ciation acceleration <em>a.</em> "
                    "<em>Scientometrics</em> 93:987&ndash;1004."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_citation_acceleration
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    return m


# Render index (Redner 2010)
def calculate_redner_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_redner_index(total_cites)


def metric_redner_index() -> Metric:
    m = Metric()
    m.name = "Redner index"
    m.full_name = "Redner index"
    m.symbol = "<em>R</em>"
    m.axis_name = r"$R$"
    m.metric_type = FLOAT
    equation = r"$$R=\sqrt{C^P}=\sqrt{\sum\limits_{i=1}^{P}{C_i}}$$"
    m.description = ('<p>The Redner index (Redner 2010) is just the square-root of the total citation count for '
                     'all publications, similar to the __Levene j-index__, which is the sum of the square-root '
                     f'of the counts.</p>{equation}')
    m.references = ["Redner, S. (2010) On the meaning of the <em>h-</em>index. <em>Journal of Statistical "
                    "Mechanics: Theory and Experiment</em> 2010(3):L03005."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_redner_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    return m


# Levene j-index (Levene et al. 2012)
def calculate_levene_j_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_levene_j_index(citations)


def metric_levene_j_index() -> Metric:
    m = Metric()
    m.name = "Levene j-index"
    m.full_name = "j-index (Levene)"
    m.html_name = "<em>j-</em>index (Levene)"
    m.symbol = "<em>j</em>"
    m.axis_name = r"$j$"
    m.metric_type = FLOAT
    equation = r"$$j=\sum\limits_{i=1}^{P}{\sqrt{C_i}}$$"
    m.description = ('<p>The Levene <em>j-</em>index (Levene <em>et al.</em> 2012) is the sum of the square-root '
                     'of citation counts for all publications, similar to the __Redner index__ which is the '
                     f'square-root of the sum.</p>{equation}')
    m.references = ["Levene, M., T. Fenner, and J. Bar-Ilan (2012) A bibliometric index based on the complete list "
                    "of cited publications. <em>International Journal of Scientometrics, Informetrics and "
                    "Bibliometrics</em> 16:1."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_levene_j_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
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
    m.symbol = "<em>S</em>"
    m.axis_name = r"$S$"
    m.metric_type = FLOAT
    equation = r"$$S=100\log_{10}\left(h \times C/P\right),$$"
    m.description = ('<p>The <em>S-</em>index (Ye 2010) is an <em>h-</em>mixed synthetic index which '
                     'combines multiple metrics together into a single value. It is calculated as </p>'
                     f'{equation}<p>where C/P is the mean number of citations per publication.</p>')
    m.references = ["Ye, F.Y. (2010) Two H-mixed synthetic indices for the assessment of research performance."
                    "<em>Journal of Library and Information Studies</em> 8:1&ndash;9."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_s_index_h_mixed
    m.properties["Compound Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
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
    m.symbol = "<em>T</em>"
    m.axis_name = r"$T$"
    m.metric_type = FLOAT
    equation = r"$$T=100\log_{10}\left(R\times h \times C/P\right),$$"
    m.description = ('<p>The <em>T-</em>index (Ye 2010) is an <em>h-</em>mixed synthetic index which '
                     'combines multiple metrics together into a single value. It is calculated as </p>'
                     f'{equation}<p>where <em>R</em> is the __R-index__ and C/P is the mean number of '
                     'citations per publication.</p>')
    m.references = ["Ye, F.Y. (2010) Two H-mixed synthetic indices for the assessment of research performance. "
                    "<em>Journal of Library and Information Studies</em> 8:1&ndash;9."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_t_index_h_mixed
    m.properties["Compound Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# s-index / citation entropy p (Silagadze 2009)
def calculate_citation_entropy(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    citations = metric_set.citations
    return Impact_Funcs.calculate_citation_entropy(total_cites, citations)


def metric_citation_entropy() -> Metric:
    m = Metric()
    m.name = "citation entropy"
    m.full_name = "citation entropy"
    m.synonyms = ["<em>s-</em>index (citation entropy)"]
    m.symbol = "<em>s</em>"
    m.axis_name = r"$s$"
    m.metric_type = FLOAT
    equation = r"$$s=\frac{1}{4}\sqrt{C^P}e^{H^*},$$"
    heq = r"$$H^*=-\sum\limits_{i=1}^{P}{\left(\frac{C_i}{C^P}\log_2\frac{C_i}{C^P}\right)}.$$"
    m.description = ('<p>Citation entropy (also known as the <em>s-</em> index) attempts to characterize the quality '
                     'and impact of scientific research'
                     f'using an entropy model. It is calculated as</p>{equation}<p>where <em>H</em><sup>*</sup> '
                     f'is the standardized Shannon entropy or</p>{heq}')
    m.references = ["Silagadze, Z.K. (2009) Citation entropy and research impact estimation. "
                    "<em>ArXiv:physics</em> 0905.1039v2:1-7."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_citation_entropy
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# Corrected Quality ratios (Lindsay 1978)
def calculate_cq_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_cq_index(total_cites, total_pubs)


def metric_cq_index() -> Metric:
    m = Metric()
    m.name = "cq index"
    m.full_name = "corrected quality ratio"
    m.html_name = "corrected quality ratio"
    m.symbol = "<em>CQ</em>"
    m.synonyms = ["<em>CQ</em> index"]
    m.metric_type = FLOAT
    eq_str = r"$$CQ=\frac{C^P}{P}\sqrt{C^P \times P}$$"
    m.description = ('<p>The corrected quality ratio (Lindsey 1978) is a metric derived from the total citations '
                     f'and the total publications. It is calculated as:</p>{eq_str}'
                     'which is the product of the mean number of citations per publication and the geometric mean '
                     'of the numbers of citations and publications. It was designed to overcome problems with the '
                     '__c/p__, particularly with respect to younger researchers.')
    m.references = ["Lindsey, D. (1978) The Corrected Quality Ratio: A composite index of scientific contribution "
                    "to knowledge. <em>Social Studies of Science</em> 8:349&ndash;354."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_cq_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# Corrected Quality ratios / 60:40 (Glanzel 2008)
def calculate_cq04_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_cq04_index(total_cites, total_pubs)


def metric_cq04_index() -> Metric:
    m = Metric()
    m.name = "cq0.4 index"
    m.full_name = "corrected quality ratio (60:40)"
    m.html_name = "corrected quality ratio (60:40)"
    m.symbol = "CQ<sup>0.4</sup>"
    m.metric_type = FLOAT
    equation = r"$$CQ^{0.4}=\left(\frac{C^P}{P}\right)^{0.6}P^{0.4}$$"
    m.description = ('<p>The <em>CQ</em><sup>0.4</sup> index (Glänzel 2008) is a modification of the __cq index__, '
                     f'meant to better match the dimensionality of the __h-index__, calculated as:</p>{equation}')
    m.references = ["Glänzel, W. (2008) On some new bibliometric applications of statistics related to the "
                    "<em>h-</em>index. <em>Scientometrics</em> 77:187&ndash;196."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_cq04_index
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Alternative Metric"] = True
    return m


# characteristic times scale, th (Popov 2005)
def calculate_th_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    years = metric_set.publication_years()
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_th_index(citations, years, total_cites)


def write_th_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by year of publication, from most recent to oldest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    years = metric_set.publication_years()
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        y = years[i]
        data.append([y, c])
    data.sort(reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr><th>Year (<em>Y<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Cumulative Citations (Σ<em>C<sub>i</sub></em>)</th>'
    rows[3] = '<tr><th></th>'
    th = metric_set.metrics["th index"].value
    s = 0
    cp = sum(metric_set.citations)
    ty = -1
    fy = max(years)
    for i, d in enumerate(data):
        y = d[0]
        c = d[1]
        s += c
        if (ty == -1) and (s >= cp/2):
            ty = y
            ec = ' class="box"'
            v = f'½<em>C<sup>P</sup></em>{NBEQ}{cp/2}'
        else:
            ec = ""
            v = ""
        rows[0] += f'<td{ec}>{y}</td>'
        rows[1] += f'<td>{c}</td>'
        rows[2] += f'<td{ec}>{s}</td>'
        rows[3] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The first year where Σ<em>C<sub>i</sub></em> ≥ ½<em>C<sup>P</sup></em> is {ty}, thus the '
               'characteristic time scale of scientific activity is '
               f'{fy}&nbsp;&minus;&nbsp;{ty}{NBPLUS}1{NBEQ}{th}</p>')
    return outstr


def metric_th_index() -> Metric:
    m = Metric()
    m.name = "th index"
    m.full_name = "characteristic time scale of scientific activity"
    m.symbol = "<em>t<sub>h</sub></em>"
    m.synonyms = ["<em>t<sub>h</sub></em>"]
    m.axis_name = r"$t_h$"
    m.example = write_th_index_example
    m.metric_type = INT
    m.description = ('<p>The characteristic time scale of scientific activity of a researcher '
                     '(<em>t<sub>h</sub></em> index) (Popov 2005) is the amount of time from the present to the '
                     'past accounting for publications to which the researcher receives half of their citations. '
                     'Put another way, if one sums a researcher\'s citations in reverse chronological order by '
                     'publication, it is the number of years necessary to reach half of their total citations.</p>')
    m.references = ["Popov, S.B. (2005) A parameter to quantify dynamics of a researcher's scientific activity. "
                    "<em>ArXiv:physics</em>:0508113v1."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_th_index
    m.properties["Time"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Alternative Metric"] = True
    return m


# average activity, at (Popov 2005)
def calculate_mean_at_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    th = metric_set.metrics["th index"].value
    return Impact_Funcs.calculate_mean_at_index(total_cites, th)


def metric_mean_at_index() -> Metric:
    m = Metric()
    m.name = "mean at index"
    m.full_name = "average scientific activity"
    m.symbol = r"\(\bar{a_t}\)"
    m.axis_name = r"$\bar{a_t}$"
    m.synonyms = ["<em>a<sub>t</sub></em>"]
    m.metric_type = FLOAT
    equation = r"$$\bar{a_t}=\frac{C^P}{2t_h},$$"
    m.description = ('<p>The average activity (Popov 2005) of a researcher over the characteristic time scale of '
                     f'their scientific activity is defined as:</p>{equation}<p>where <em>t<sub>h</sub></em> '
                     'is the __th index__.')
    m.references = ["Popov, S.B. (2005) A parameter to quantify dynamics of a researcher's scientific activity. "
                    "<em>ArXiv:physics</em>:0508113v1."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_mean_at_index
    m.properties["Time"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Alternative Metric"] = True
    return m


# Discounted Cumulated Impact (DCI) (Jarvelin and Pearson 2008; Ahlgren and Jarvelin 2010)
def calculate_dci_index2(metric_set: MetricSet) -> list:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_list[:metric_pos+1]]
    return Impact_Funcs.calculate_dci_index(total_cite_list, 2)


def metric_dci_index2() -> Metric:
    m = Metric()
    m.name = "dci index 2"
    m.full_name = "discounted cumulated impact (sharp decay)"
    m.symbol = "DCI (<em>b</em> = 2)"
    m.axis_name = r"$DCI$"
    m.synonyms = ["DCI index (sharp decay)"]
    m.metric_type = LIST
    m.list_formats = FLOAT
    equation = (r"$$\text{DCI}_Y\left(i\right)=\left|\begin{matrix} "
                r"\frac{c^i}{\max\left[1, \log_b\left(Y-1\right)\right]} & "
                r"\text{if }i=1 \\ "
                r"\text{DCI}_Y\left(i-1\right)+\frac{c^i}{\max\left[1, \log_b\left(Y-i\right)\right]} & "
                r"\text{otherwise} \end{matrix} \right. ,$$")
    m.description = ('<p>The discounted cumulated impact index (Järvelin and Pearson 2008; Ahlfren and Järvelin 2010) '
                     'is designed to reduce the role of older citations, but still reward researchers for older '
                     'publications receiving new citations. To begin, let <em>c<sup>x</sup></em> represet the total '
                     'number of citations received by a researcher to all of their publications in year <em>x</em>. '
                     'Over a citation interval of <em>Y</em> years, the cumulated impact vector is simply the sum of '
                     'these values from the first year to be considered (<em>Y</em> years ago) up through the current '
                     'year. If the citation interval is the entire career of a researcher, this would be '
                     'a vector of <em>C<sup>P</sup></em> calculated each year. This raw vector incorporates citation '
                     'counts without decay over time, <em>i.e.</em>, old and new citations are treated equally. '
                     'To incorporate a time decay, one divides the count of new citations each year by the logarithm '
                     'of the number of years elapsed. The discounted cumulative impact vector is thus:</p>'
                     f'{equation}<p>where <em>b</em> is the base of the logarithm used for scaling. Larger values '
                     'of <em>b</em> discount older citations less than smaller values.</p><p>In this version we '
                     'use a sharp decay with <em>b</em> = 2.</p>')
    m.references = ["Järvelin, K., and O. Pearson (2008) The DCI-index: Discounted impact-based research "
                    "evaluation. <em>Journal of the American Society for Information Science and Technology</em> "
                    "59:1433&ndash;1440.",
                    "Ahlgren, P., and K. Järvelin (2010) Measuring impact of 12 information scientists using the "
                    "DCI-index. <em>Journal of the American Society for Information Science and Technology</em> "
                    "67:1424&ndash;1439."]
    m.draw_graph = Impact_Graphs.draw_graph_multiline_left_chart
    m.calculate = calculate_dci_index2
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    m.properties["Multidimensional Metric"] = True
    return m


# Dynamic Discounted Cumulated Impact (dDCI) (Jarvelin and Pearson 2008; Ahlgren and Jarvelin 2010)
def calculate_ddci_index2(metric_set: MetricSet) -> float:
    dci = metric_set.metrics["dci index 2"].value
    return Impact_Funcs.calculate_ddci_index(dci)


def metric_ddci_index2() -> Metric:
    m = Metric()
    m.name = "ddci index 2"
    m.full_name = "dynamic discounted cumulated impact (sharp decay)"
    m.symbol = "dDCI (<em>b</em> = 2)"
    m.axis_name = r"$dDCI$"
    m.synonyms = ["dDCI index (sharp decay)"]
    m.metric_type = FLOAT
    equation = r"$$\text{dDCI}_Y\left[j\right]=DCI_j\left[j\right] ,$$"
    m.description = ('<p>The dynamic discounted cumulated impact index (Järvelin and Pearson 2008; '
                     'Ahlfren and Järvelin 2010) is an addendum to the __dci index 2__ which '
                     'cumulates across different time intervals, rather than a single fixed interval. Formally, '
                     f'it is a vector defined as:</p>{equation}<p>where DCI<em><sub>j</sub></em>[<em>j</em>] '
                     'is essentially the last item in the DCI vector for time interval <em>j.</em> When calculated '
                     'for a career, where each subsequent interval is the length of the career up to that point, '
                     'the values calculated for earlier career points are identical those same intervals for later '
                     'career points, thus we just report the final value for each year, with all values up to that '
                     'year actually representing the full dDCI vector.</p><p>Because DCI can be calculated with '
                     'varying degrees of citation decay, dDCI is also dependent on this same decay. This version is '
                     'calculated from the DCI index with a sharp decay of <em>b</em> = 2.</p>')
    m.references = ["Järvelin, K., and O. Pearson (2008) The DCI-index: Discounted impact-based research "
                    "evaluation. <em>Journal of the American Society for Information Science and Technology</em> "
                    "59:1433&ndash;1440.",
                    "Ahlgren, P., and K. Järvelin (2010) Measuring impact of 12 information scientists using the "
                    "DCI-index. <em>Journal of the American Society for Information Science and Technology</em> "
                    "67:1424&ndash;1439."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_ddci_index2
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    m.properties["Multidimensional Metric"] = True
    return m


# Discounted Cumulated Impact (DCI) (Jarvelin and Pearson 2008; Ahlgren and Jarvelin 2010)
def calculate_dci_index10(metric_set: MetricSet) -> list:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_list[:metric_pos+1]]
    return Impact_Funcs.calculate_dci_index(total_cite_list, 10)


def metric_dci_index10() -> Metric:
    m = Metric()
    m.name = "dci index 10"
    m.full_name = "discounted cumulated impact (mild decay)"
    m.symbol = "DCI (<em>b</em> = 10)"
    m.axis_name = r"$DCI$"
    m.synonyms = ["DCI index (mild decay)"]
    m.metric_type = LIST
    m.list_formats = FLOAT
    equation = (r"$$\text{DCI}_Y\left(i\right)=\left|\begin{matrix} "
                r"\frac{c^i}{\max\left[1, \log_b\left(Y-1\right)\right]} & "
                r"\text{if }i=1 \\ "
                r"\text{DCI}_Y\left(i-1\right)+\frac{c^i}{\max\left[1, \log_b\left(Y-i\right)\right]} & "
                r"\text{otherwise} \end{matrix} \right. ,$$")
    m.description = ('<p>The discounted cumulated impact index (Järvelin and Pearson 2008; Ahlfren and Järvelin 2010) '
                     'is designed to reduce the role of older citations, but still reward researchers for older '
                     'publications receiving new citations. To begin, let <em>c<sup>x</sup></em> represet the total '
                     'number of citations received by a researcher to all of their publications in year <em>x</em>. '
                     'Over a citation interval of <em>Y</em> years, the cumulated impact vector is simply the sum of '
                     'these values from the first year to be considered (<em>Y</em> years ago) up through the current '
                     'year. If the citation interval is the entire career of a researcher, this would be '
                     'a vector of <em>C<sup>P</sup></em> calculated each year. This raw vector incorporates citation '
                     'counts without decay over time, <em>i.e.</em>, old and new citations are treated equally. '
                     'To incorporate a time decay, one divides the count of new citations each year by the logarithm '
                     'of the number of years elapsed. The discounted cumulative impact vector is thus:</p>'
                     f'{equation}<p>where <em>b</em> is the base of the logarithm used for scaling. Larger values '
                     'of <em>b</em> discount older citations less than smaller values.</p><p>In this version we '
                     'use a mild decay with <em>b</em> = 10.</p>')
    m.references = ["Järvelin, K., and O. Pearson (2008) The DCI-index: Discounted impact-based research "
                    "evaluation. <em>Journal of the American Society for Information Science and Technology</em> "
                    "59:1433&ndash;1440.",
                    "Ahlgren, P., and K. Järvelin (2010) Measuring impact of 12 information scientists using the "
                    "DCI-index. <em>Journal of the American Society for Information Science and Technology</em> "
                    "67:1424&ndash;1439."]
    m.draw_graph = Impact_Graphs.draw_graph_multiline_left_chart
    m.calculate = calculate_dci_index10
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    m.properties["Multidimensional Metric"] = True
    return m


# Dynamic Discounted Cumulated Impact (dDCI) (Jarvelin and Pearson 2008; Ahlgren and Jarvelin 2010)
def calculate_ddci_index10(metric_set: MetricSet) -> float:
    dci = metric_set.metrics["dci index 10"].value
    return Impact_Funcs.calculate_ddci_index(dci)


def metric_ddci_index10() -> Metric:
    m = Metric()
    m.name = "ddci index 10"
    m.full_name = "dynamic discounted cumulated impact (mild decay)"
    m.symbol = "dDCI (<em>b</em> = 10)"
    m.axis_name = r"$dDCI$"
    m.synonyms = ["dDCI index (mild decay)"]
    m.metric_type = FLOAT
    equation = r"$$\text{dDCI}_Y\left[j\right]=DCI_j\left[j\right] ,$$"
    m.description = ('<p>The dynamic discounted cumulated impact index (Järvelin and Pearson 2008; '
                     'Ahlfren and Järvelin 2010) is an addendum to the __dci index 10__ which '
                     'cumulates across different time intervals, rather than a single fixed interval. Formally, '
                     f'it is a vector defined as:</p>{equation}<p>where DCI<em><sub>j</sub></em>[<em>j</em>] '
                     'is essentially the last item in the DCI vector for time interval <em>j.</em> When calculated '
                     'for a career, where each subsequent interval is the length of the career up to that point, '
                     'the values calculated for earlier career points are identical those same intervals for later '
                     'career points, thus we just report the final value for each year, with all values up to that '
                     'year actually representing the full dDCI vector.</p><p>Because DCI can be calculated with '
                     'varying degrees of citation decay, dDCI is also dependent on this same decay. This version is '
                     'calculated from the DCI index with a mild decay of <em>b</em> = 10.</p>')
    m.references = ["Järvelin, K., and O. Pearson (2008) The DCI-index: Discounted impact-based research "
                    "evaluation. <em>Journal of the American Society for Information Science and Technology</em> "
                    "59:1433&ndash;1440.",
                    "Ahlgren, P., and K. Järvelin (2010) Measuring impact of 12 information scientists using the "
                    "DCI-index. <em>Journal of the American Society for Information Science and Technology</em> "
                    "67:1424&ndash;1439."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_ddci_index10
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    m.properties["Multidimensional Metric"] = True
    return m


## start here


# history h-index (Randic 2009)
def calculate_history_h_index(metric_set: MetricSet) -> int:
    h = metric_set.metrics["h-index"].value
    citations = metric_set.citations
    return Impact_Funcs.calculate_history_h_index(citations, h)


# def write_history_h_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["history h-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'threshold lines', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     maxc = max(tmp_cites)
#     maxk = 0
#     while maxc > 2**maxk:
#         maxk += 1
#     maxk -= 1
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     # write citation count for ranked publication x
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#         outstr += ", {}, null, null],\n".format(v)
#         output.append(outstr)
#     # write slopes
#     for k in range(maxk+1):
#         x = maxv / 2**k
#         output.append("           [{}, null, {}, null],\n".format(0, 0))
#         output.append("           [{}, null, {}, null],\n".format(x, maxv))
#         output.append("           [null, null, null, null],\n")
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4]}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def create_history_h_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # # example points
    # point_data = Impact_Graphs.PointData()
    # output.append(point_data)
    # point_data.x = [h, h+1]
    # point_data.y = [h, h+1]
    # point_data.fillcolor = "none"

    # threshold lines
    maxk = 0
    while maxc > 2**maxk:
        maxk += 1
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = []
    threshold_data.y = []
    for k in range(maxk):
        endx = maxc / 2**k
        threshold_data.x.extend([0, endx, None])
        threshold_data.y.extend([0, maxc, None])
    threshold_data.style = "--"
    threshold_data.label = "threshold lines"

    # # annotation
    # annotation = Impact_Graphs.AnnotationData()
    # output.append(annotation)
    # annotation.label = f"$h = {h}$"
    # annotation.pos = (h, h)
    # annotation.textpos = (h+20, h)
    #
    # annotation = Impact_Graphs.AnnotationData()
    # output.append(annotation)
    # annotation.label = f"$h+1 = {h+1}$"
    # annotation.pos = (h+1, h+1)
    # annotation.textpos = (h+20, h+15)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True

    return output



def write_history_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    maxc = max(citations)
    maxk = 0
    while maxc > 2**maxk:
        maxk += 1
    maxk -= 1
    hklist = []
    for k in range(maxk+1):
        hk = 0
        for i, c in enumerate(citations):
            if c >= (i+1) * 2**k:
                hk = i+1
        hklist.append(hk)
    row1 = '<tr class="top_row"><th></th><th>Citations (<em>C<sub>i</sub></em>)</th><th>Rank (<em>i</em>)</th>'
    for k in range(maxk+2):
        row1 += f'<th>2<sup>{k}</sup></th>'
    row1 += '</tr>\n'
    rows = []
    for i, c in enumerate(citations):
        vlist = []
        for k, hk in enumerate(hklist):
            if hk == i+1:
                vlist.append(f'<em>H</em><sup>{k}</sup>{NBEQ}{i+1}')
        if len(vlist) > 0:
            v = ',&nbsp;'.join(vlist)
        else:
            v = ""
        row = f'<tr><td>{v}</td><td>{c}</td><td>{i+1}</td>'
        for k in range(maxk+2):
            if k <= maxk:
                if i+1 == hklist[k]:
                    ec = ' class="box"'
                else:
                    ec = ""
            else:
                ec = ""
            row += f'<td{ec}>{(i+1)*2**k}</td>'
        row += '</tr>\n'
        rows.append(row)
    outstr += row1
    for row in rows:
        outstr += row
    outstr += '</table>'
    h = metric_set.metrics["history h-index"].value
    outstr += f'<p>The sum of all of the <em>H<sup>k</sup></em> values is {h}.</p>'
    return outstr


def metric_history_h_index() -> Metric:
    m = Metric()
    m.name = "history h-index"
    m.full_name = "history h-index"
    m.html_name = "history <em>h-</em>index"
    m.symbol = "<em>H</em>"
    m.axis_name = r"$H$"
    m.synonyms = ["<em>H</em>"]
    m.example = write_history_h_index_example
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "history_h_index_desc"
    graph.data = create_history_h_index_desc_graph_data
    m.metric_type = INT
    hkeq = r"$$H^k=\underset{i}{\max}\left(C_i \geq i \times 2^k\right).$$"
    equation = r"$$H=\sum\limits_{k=0}^{K}{H^k},$$"
    m.description = ('<p>The history <em>h-</em>index (Randić 2009) is another metric designed to help distinguish '
                     'among researchers with identical __h-index__. It is based on the idea of exploring a '
                     'power expansion of the citation counts for publications in the core. This index starts by '
                     'creating a vector representing larger power expansions of citation counts. '
                     'The <em>k</em><sup>th</sup> '
                     'element of the vector is the largest rank (<em>i</em>), for which the number of citations '
                     'for that publication is equal or larger than the rank times 2<sup><em>k</em></sup>, or</p>'
                     f'{hkeq}<p>By definition, the first (zeroth) entry is <em>h</em> '
                     f'(since 2<sup>0</sup>{NBEQ}1). Graphically, this is looking at the intersection '
                     '(rounding the rank down to the nearest integer) of the citation curve with a series of lines '
                     'with ever increasing slopes of 2<sup><em>k</em></sup>: '
                     '1 (=<em>h</em>), 2, 4, 8, etc., with the largest <em>k</em> equal to the line with the largest '
                     'slope that actually intersects the citation curve.</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure><p>The history <em>h-</em>index is simply the sum of the '
                     f'values in this vector, or</p>{equation}<p>where <em>K</em> is the largest power of 2 '
                     'for which <em>C</em><sub>max</sub> >= 2<sup><em>K</em></sup>.')
    m.references = ["Randić, M. (2009) Citations versus limitations of citations: Beyond Hirsch index. "
                    "<em>Scientometrics</em> 80(3):809&ndash;818."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_history_h_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# quality quotient (Randic 2009)
def calculate_quality_quotient(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    history_h = metric_set.metrics["history h-index"].value
    return Impact_Funcs.calculate_quality_quotient(h, history_h)


def metric_quality_quotient() -> Metric:
    m = Metric()
    m.name = "quality quotient"
    m.full_name = "quality quotient"
    m.symbol = "<em>Q</em>"
    m.axis_name = r"$Q$"
    m.synonyms = ["<em>Q</em>"]
    m.metric_type = FLOAT
    equation = r"$$Q=\frac{H}{h}.$$"
    m.description = ('<p>The quality quotient (Randić 2009) is the ratio between the __history h-index__ and the '
                     f'__h-index__,</p>{equation}<p>This metric can only really be used to compare '
                     'individuals with identical <em>h-</em>indices, as the minimum possible value varies with '
                     '<em>h</em> in a non-monotonic manner, <em>e.g.,</em> '
                     f'when <em>h</em>{NBEQ}1, min(<em>Q</em>){NBEQ}1; '
                     f'when <em>h</em>{NBEQ}2, min(<em>Q</em>){NBEQ}1.5; '
                     f'when <em>h</em>{NBEQ}3, min(<em>Q</em>){NBEQ}1.33; '
                     f'when <em>h</em>{NBEQ}4, min(<em>Q</em>){NBEQ}1.75, etc.</p>')
    m.references = ["Randić, M. (2009) Citations versus limitations of citations: Beyond Hirsch index. "
                    "<em>Scientometrics</em> 80(3):809&ndash;818."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_quality_quotient
    m.properties["Core Property"] = True
    m.properties["Compound Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# scientist's level (Mitropoulos 2009)
def calculate_scientist_level(metric_set: MetricSet) -> list:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_scientist_level(total_cites, total_pubs)


def metric_scientist_level() -> Metric:
    m = Metric()
    m.name = "scientist level"
    m.full_name = "scientist\'s level"
    m.symbol = "<em>L<sup>v</sup></em> = [<em>v</em>, <em>L</em>]"
    m.synonyms = ["<em>L<sup>v</sup></em>"]
    m.metric_type = LIST
    m.list_formats = INT
    eq1 = r"$$v=\text{floor}\left[\log\left(C^P + P\right)\right]$$"
    eq2 = r"$$L^v=\text{floor}\left(\frac{C^P + P}{10^v}\right)$$"
    eq3 = r"$$\text{level}=v.L=v + \frac{L}{10}.$$"
    m.description = ('<p>The scientist\'s level (Mitropoulos 2009) is an attempt to quantitatively break '
                     'scientist\'s into broad categories of advancement based on a combination of their total '
                     'citations and publications. It is expressed as <em>L<sup>v</sup>,</em> where <em>v</em> '
                     'represent the overall level and <em>L</em> the progress within <em>v</em>. Functionally, '
                     'these values are logarithmic decompositions of the sum of citations and publications, such '
                     'that <em>v</em> represents the integer value of the (base 10) logarithm of the sum '
                     f'(<em>i.e.,</em> <em>v</em>{NBEQ}0 when the sum is less than 10, <em>v</em>{NBEQ}1 '
                     f'when the sum is between 10 and 99, <em>v</em>{NBEQ}2 when the sum is between 100 and '
                     '999, etc.), and <em>L</em> is the integer value of the sum divided by '
                     f'10<sup><em>v</em></sup> (<em>i.e.,</em> if <em>v</em>{NBEQ}2, <em>L</em>{NBEQ}1 '
                     f'if the sum is between 100 and 199, <em>L</em>{NBEQ}2 if the sum is between 200 and 299, '
                     f'etc.).</p>{eq1}{eq2}'
                     '<p><em>L</em> can be any integer from 1 to 9, while <em>v</em> will generally be an integer '
                     'between 0 and 5 (a <em>v</em> of 6 would require > 1 million combined citations and '
                     'publications).</p>'
                     '<p>Because of this structure and the limited possible values of these measures, one could '
                     f'readily combine these into a single value as,</p>{eq3}')
    m.references = ["Mitropoulos, A.C. (2009) Is it more difficult to write or to cite a paper? <em>Journal of "
                    "Engineering Science and Technology Review</em> 2(1):68&ndash;70."]
    m.draw_graph = Impact_Graphs.draw_graph_line_combined_chart
    m.calculate = calculate_scientist_level
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Multidimensional Metric"] = True
    return m


# non-integer scientist's level (Todeschini and Baccini 2016)
def calculate_scientist_level_nonint(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_scientist_level_nonint(total_cites, total_pubs)


def metric_scientist_level_nonint() -> Metric:
    m = Metric()
    m.name = "nonint scientist level"
    m.full_name = "scientist\'s level (non-integer)"
    m.symbol = "<em>τ</em>"
    m.axis_name = r"$\tau$"
    m.synonyms = ["<em>τ</em>"]
    m.metric_type = FLOAT
    equation = r"$$\tau=\ln{\left(\sqrt{C^P}+P\right)}.$$"
    m.description = ('<p>The non-integer scientist\'s level (Todeschini and Baccini 2016) is a logarithmic '
                     'approach to scaling the total number of citations and publications of an author into a single '
                     'measure without the degeneracy of the integer versioned __scientist level__. It is calculated '
                     f'as</p>{equation}')
    m.references = ["Todeschini, R., and A. Baccini (2016) <em>Handbook of Bibliometric Indicators: Quantitative "
                    "Tools for Studying and Evaluating Research.</em> Weinheim, Germany: Wiley."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_scientist_level_nonint
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# q-index (Bartneck and Kokkelmans 2011)
def calculate_q_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    cites = metric_set.citations
    self_cites = metric_set.self_citations
    return Impact_Funcs.calculate_q_index(cites, self_cites, h)


def write_q_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    h = metric_set.metrics["h-index"].value
    q_index = metric_set.metrics["q-index"].value
    tmp_cites = metric_set.citations
    tmp_self = metric_set.self_citations
    data = []
    for i in range(len(tmp_cites)):
        data.append([tmp_cites[i], tmp_self[i], 0, 0])
    data.sort(reverse=True)
    prev_a = 0
    for i, d in enumerate(data):
        c = d[0]
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
                q = (i+1) + 1 - a - h
            prev_a = a
        else:
            a = 0
            q = 0
        d[2] = a
        d[3] = q
    rows = ["" for _ in range(7)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Self Citations (<em>c<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    rows[4] = '<tr><th><em>a<sub>i</sub></em></th>'
    rows[5] = '<tr><th><em>q<sub>i</sub></em></th>'
    rows[6] = '<tr><th><em>c<sub>i</sub>q<sub>i</sub></em></th>'
    sq = 0
    for i, d in enumerate(data):
        c = d[0]
        s = d[1]
        a = d[2]
        q = d[3]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td>{s}</td>'
        rows[2] += f'<td{ec}>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'
        rows[4] += f'<td>{a}</td>'
        if q == 0:
            rows[5] += '<td>0</td>'
            tsq = 0
        else:
            rows[5] += f'<td>1/{q}</td>'
            tsq = s/q
        rows[6] += f'<td>{tsq:0.3f}</td>'
        sq += tsq

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The sum of <em>c<sub>i</sub>q<sub>i</sub></em> is {sq:1.4f}, thus Q is {q_index:1.4f}.</p>'
    return outstr


def metric_q_index() -> Metric:
    m = Metric()
    m.name = "q-index"
    m.full_name = "q-index"
    m.html_name = "<em>q-</em>index"
    m.symbol = "<em>Q</em>"
    m.axis_name = r"$Q$"
    m.synonyms = ["<em>Q</em>"]
    m.is_self = True
    m.example = write_q_index_example
    m.metric_type = FLOAT
    qieq = (r"$$q_i=\left|\begin{matrix} 0 & \text{if }C_i > h \text{ or } i < h \\ \frac{1}{i+1-a_i-h} & "
            r"\text{if }C_i \leq h \text{ and } i \geq h \end{matrix}\right.,$$")
    aieq = (r"$$a_i=\left|\begin{matrix} 0 & \text{if }i \leq h \\ a_{i-1} & \text{if }i>h \text{ and } C_i "
            r"\neq C_{i-1}\\ 1+a_{i-1} & \text{if }i>h \text{ and } C_i = C_{i-1} \end{matrix}\right. .$$")
    equation = r"$$Q=\frac{1}{P}\sum\limits_{i=1}^{P}{c_i q_i}.$$"
    m.description = ('<p>The <em>q-</em>index (Bartneck and Kokkelmans 2011) is an attempt to measure whether an '
                     'author is manipulating their own __h-index__ through self-citation. It calculates a '
                     'potential cost of a self-citation for each publication whose citation count is equal or less '
                     'than the <em>h,</em> sums these costs for all self-citations, then normalizes by the total '
                     'number of publications. Essentially, publications with a citation count equal to <em>h</em> '
                     'generate a cost of 1 per self-citation, with each subsequent publication in rank order '
                     'generating costs of 1/2, 1/3, 1/4, etc., with ties generating equal values. The potential costs '
                     f'are calculated as:</p>{qieq}<p>where</p>{aieq}<p>The total self-citations for any '
                     'publication where <em>C<sub>i</sub></em>&nbsp;≤&nbsp;<em>h</em> are multiplied by the '
                     f'associated cost and these values are summed and averaged for all publications.</p>{equation}'
                     '<p>where <em>c<sub>i</sub></em> is the number of self-citations to the <em>i</em><sup>th</sup> '
                     'publication.</p><p>Simulations indicate that selective citing to boost <em>h</em> may lead to a '
                     '<em>q</em>-index, greater than one, while lower values are found when self-citation is random '
                     'or fair.</p>')
    m.references = ["Bartneck, C., and S. Kokkelmans (2011) Detecting <em>h-</em>index manipulation through "
                    "self-citation analysis. <em>Scientometrics</em> 87(1):85&ndash;98."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_q_index
    m.properties["Self-Citation"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Alternative Metric"] = True
    return m


# career years h-index by publications (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_pub(metric_set: MetricSet) -> int:
    pub_years = metric_set.publication_years()
    return Impact_Funcs.calculate_career_years_h_index_pub(pub_years)


def write_career_years_h_index_pub_example(metric_set: MetricSet) -> str:
    outstr = '<p>Years are ordered by number of publications, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    h = metric_set.metrics["career years h-index by pub"].value
    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: pub_years.count(y) for y in range(miny, maxy + 1)}
    data = []
    for y in year_cnts:
        data.append([year_cnts[y], y])
    data.sort(reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Publications (<em>P<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    for i, d in enumerate(data):
        c = d[0]
        y = d[1]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{y}</td>'
        rows[1] += f'<td{ec}>{c}</td>'
        rows[2] += f'<td{ec}>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em>&nbsp;≤&nbsp;<em>P<sub>i</sub></em> is {h}.</p>'
    return outstr


def metric_career_years_h_index_pub() -> Metric:
    m = Metric()
    m.name = "career years h-index by pub"
    m.full_name = "career years h-index by publications"
    m.html_name = "career years <em>h-</em>index by publications"
    m.symbol = "career years <em>h</em> by pubs"
    m.example = write_career_years_h_index_pub_example
    m.metric_type = INT
    equation = r"$$\text{career years }h\text{ by publications}=\underset{i}{\max}\left(i\leq P_i\right).$$"
    m.description = ('<p>The career years <em>h-</em>index by publications (Mahbuba and Rousseau 2013) is a measure '
                     'of publication intensity or distribution, rather than citation intensity as captured by '
                     'most __h-index__ type indices. Rather than create a list of publications ranked by citation '
                     'count, one creates a list of years ranked by publication count. This list is then processed '
                     'in the same manner as a typical <em>h-</em>type index, namely the career years <em>h-</em>index '
                     'by publications is the largest value <em>h</em> for which at least <em>h</em> years have '
                     f'<em>h</em> publications.</p>{equation}<p>This metric helps indicate whether the '
                     'publication output of a researcher is confined to a limited number of years (smaller value) or '
                     'is spread more evenly across their career (larger values); it is most useful for comparing '
                     'among established/older researchers with similar publication counts and career lengths; '
                     'this metric is limiting for young researchers with short careers because the maximum value is '
                     'the length of the career.</p>')
    m.references = ["Mahbuba, D., and R. Rousseau (2013) Year-based <em>h-</em>type indicators. "
                    "<em>Scientometrics</em> 96(3):785&ndash;797."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart

    m.calculate = calculate_career_years_h_index_pub
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    return m


# career years h-index by citations (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_cite(metric_set: MetricSet) -> int:
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    return Impact_Funcs.calculate_career_years_h_index_cite(pub_years, cites)


def write_career_years_h_index_cite_example(metric_set: MetricSet) -> str:
    outstr = '<p>Years are ordered by number of citations for publications from that year, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    h = metric_set.metrics["career years h-index by cite"].value
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    miny = min(pub_years)
    maxy = max(pub_years)
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = []
    for y in year_cnts:
        data.append([year_cnts[y], y])
    data.sort(reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    for i, d in enumerate(data):
        c = d[0]
        y = d[1]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{y}</td>'
        rows[1] += f'<td{ec}>{c}</td>'
        rows[2] += f'<td{ec}>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em>&nbsp;≤&nbsp;<em>C<sub>i</sub></em> is {h}.</p>'
    return outstr


def metric_career_years_h_index_cite() -> Metric:
    m = Metric()
    m.name = "career years h-index by cite"
    m.full_name = "career years h-index by citations"
    m.html_name = "career years <em>h-</em>index by citations"
    m.symbol = "career years <em>h</em> by cites"
    m.example = write_career_years_h_index_cite_example
    m.metric_type = INT
    equation = r"$$\text{career years }h\text{ by citations}=\underset{i}{\max}\left(i\leq P_i\right).$$"
    m.description = ('<p>The career years <em>h-</em>index by citations (Mahbuba and Rousseau 2013) is a measure '
                     'of citation intensity or distribution by publication year, rather than by publication as '
                     'captured by most __h-index__ type indices. Rather than create a list of publications ranked by '
                     'citation count, one creates a list of years ranked by citation count for all publications from '
                     'that year. This list is then processed in the same manner as a typical <em>h-</em>type index, '
                     'namely the career years <em>h-</em>index by citations is the largest value <em>h</em> for '
                     f'which at least <em>h</em> years have publications with <em>h</em> total citations.</p>{equation}'
                     '<p>This metric helps indicate whether the citation impact of a researcher is confined to a '
                     'limited number of years (smaller value) or is spread more evenly across their career '
                     '(larger values); it is most useful for comparing among established/older researchers with '
                     'similar career lengths and citation counts/<em>h-</em>indices; this metric is limiting for '
                     'young researchers with short careers because the maximum value is the length of the career.</p>')
    m.references = ["Mahbuba, D., and R. Rousseau (2013) Year-based <em>h-</em>type indicators. "
                    "<em>Scientometrics</em> 96(3):785&ndash;797."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_career_years_h_index_cite
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# career years h-index by avg citations/year (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_avgcite(metric_set: MetricSet) -> float:
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    return Impact_Funcs.calculate_career_years_h_index_avgcite(pub_years, cites)


def write_career_years_h_index_avgcite_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by average number of citations per publication from that year, from highest to '
              'lowest.</p>')
    outstr += '<table class="example_table">\n'
    hint = metric_set.metrics["career years h-index by avg cite"].value
    h = math.trunc(hint)
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    miny = min(pub_years)
    maxy = max(pub_years)
    pub_cnts = {y: pub_years.count(y) for y in range(miny, maxy + 1)}
    cite_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        cite_cnts[pub_years[i]] += c
    data = []
    for y in pub_cnts:
        data.append([cite_cnts[y]/pub_cnts[y], y, pub_cnts[y], cite_cnts[y]])
    data.sort(reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Publications (<em>P<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[3] = ('<tr class="top_row"><th>Average Citations per '
              'Publication(<em>C<sub>i</sub></em>/<em>P<sub>i</sub></em>)</th>')
    rows[4] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[5] = '<tr><th></th>'
    for i, d in enumerate(data):
        a = d[0]
        y = d[1]
        p = d[2]
        c = d[3]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{y}</td>'
        rows[1] += f'<td>{p}</td>'
        rows[2] += f'<td>{c}</td>'
        rows[3] += f'<td{ec}>{a:0.2f}</td>'
        rows[4] += f'<td{ec}>{i+1}</td>'
        rows[5] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest rank where <em>i</em>&nbsp;≤&nbsp;<em>C<sub>i</sub></em>/<em>P<sub>i</sub></em> is '
               f'{h}. The interpolated rank betweeen this and the next largest value is {hint:0.2f}.</p>')
    return outstr


def metric_career_years_h_index_avgcite() -> Metric:
    m = Metric()
    m.name = "career years h-index by avg cite"
    m.full_name = "career years h-index by average citations per year"
    m.html_name = "career years <em>h-</em>index by average citations per year"
    m.symbol = "Career years <em>h<sub>int</sub></em> by avg cites"
    m.example = write_career_years_h_index_avgcite_example
    m.metric_type = FLOAT
    equation = (r"$$\text{career years }h\text{ by average citations per year}="
                r"\underset{i}{\max}\left(i\leq \frac{C_i}{P_i}\right).$$")
    equation2 = (r"$$h_{int}=\frac{\left(h+1\right)\frac{C_h}{P_h}-h\frac{C_{h+1}}{P_{h+1}}}"
                 r"{1-\frac{C_{h+1}}{P_{h+1}}+\frac{C_h}{P_h}}.$$")
    m.description = ('<p>The career years <em>h-</em>index by average citations per year (Mahbuba and Rousseau 2013) '
                     'is similar to the __career years h-index by cite__ and __career years h-index by pub__, '
                     'but is based on the average '
                     'number of citations generated per publication per year, rather than on the total publications '
                     'or total citations for each year. One creates a list of years ranked by average citation count '
                     'per publication for all publications from that year. This list is then processed in the same '
                     'manner as a typical <em>h-</em>type index, namely the career years <em>h-</em>index by '
                     'average citations per year is the largest value <em>h</em> for '
                     'which at least <em>h</em> years have publications with an average of <em>h</em> citations.</p>'
                     f'{equation}<p>Because the average number of citations will often not be an integer, the '
                     'authors recommend interpolating between this and the next largest value, as with the real '
                     f'<em>h-</em>index, in order to more accurately estimate the metric.</p>{equation2}')
    m.references = ["Mahbuba, D., and R. Rousseau (2013) Year-based <em>h-</em>type indicators. "
                    "<em>Scientometrics</em> 96(3):785&ndash;797."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_career_years_h_index_avgcite
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# career years h-index by diffusion speed (Mahbuba and Rousseau 2013)
def calculate_career_years_h_index_diffspeed(metric_set: MetricSet) -> float:
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    cur_year = metric_set.year()
    return Impact_Funcs.calculate_career_years_h_index_diffspeed(pub_years, cites, cur_year)


def write_career_years_h_index_diffspeed_example(metric_set: MetricSet) -> str:
    outstr = '<p>Years are ordered by diffusion speed per year, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    hint = metric_set.metrics["career years h-index by diff speed"].value
    h = math.trunc(hint)
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    cur_year = metric_set.year()
    miny = min(pub_years)
    maxy = max(pub_years)
    cite_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        cite_cnts[pub_years[i]] += c
    data = []
    for y in cite_cnts:
        data.append([cite_cnts[y]/(cur_year - y + 1), y, cur_year - y + 1, cite_cnts[y]])
    data.sort(reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Age (<em>A<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[3] = '<tr class="top_row"><th>Diffusion Speed (<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[5] = '<tr><th></th>'
    for i, d in enumerate(data):
        ds = d[0]
        y = d[1]
        a = d[2]
        c = d[3]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{y}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td>{c}</td>'
        rows[3] += f'<td{ec}>{ds:0.2f}</td>'
        rows[4] += f'<td{ec}>{i+1}</td>'
        rows[5] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += ('<p>The largest rank where <em>i</em>&nbsp;≤&nbsp;<em>C<sub>i</sub></em>/<em>A<sub>i</sub></em> is '
               f'{h}. The interpolated rank betweeen this and the next largest value is {hint:0.2f}.</p>')
    return outstr


def metric_career_years_h_index_diffspeed() -> Metric:
    m = Metric()
    m.name = "career years h-index by diff speed"
    m.full_name = "career years h-index by diffusion speed"
    m.html_name = "career years <em>h-</em>index by diffusion speed"
    m.symbol = "Career years <em>h<sub>int</sub></em> by diffusion speed"
    m.example = write_career_years_h_index_diffspeed_example
    m.metric_type = FLOAT
    equation = (r"$$\text{career years }h\text{ by diffusion speed}="
                r"\underset{i}{\max}\left(i\leq \frac{C_i}{A_i}\right).$$")
    equation2 = (r"$$h_{int}=\frac{\left(h+1\right)\frac{C_h}{A_h}-h\frac{C_{h+1}}{A_{h+1}}}"
                 r"{1-\frac{C_{h+1}}{A_{h+1}}+\frac{C_h}{A_h}}.$$")
    m.description = ('<p>The career years <em>h-</em>index by diffusion speed (Mahbuba and Rousseau 2013) '
                     'is similar to the __career years h-index by avg cite__, but rescales the citation '
                     'counts per year for the time ellapsed since the year of publication. One could also calculate '
                     'it for a fixed time window, but here we are using career length at the time of calcuation. '
                     'One creates a list of years ranked by diffusion speed estimated for all citations for all '
                     'publications from that year. This list is then processed in the same '
                     'manner as a typical <em>h-</em>type index, namely the career years <em>h-</em>index by '
                     'diffusion speed is the largest value <em>h</em> for '
                     'which at least <em>h</em> years have a diffusion speed of <em>h</em>.</p>'
                     f'{equation}<p>Because the diffusion speed will often not be an integer, the '
                     'authors recommend interpolating between this and the next largest value, as with the real '
                     f'<em>h-</em>index, in order to more accurately estimate the metric.</p>{equation2}')
    m.references = ["Mahbuba, D., and R. Rousseau (2013) Year-based <em>h-</em>type indicators. "
                    "<em>Scientometrics</em> 96(3):785&ndash;797."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_career_years_h_index_diffspeed
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# collaborative index (Lawani 1980)
def calculate_collaborative_index(metric_set: MetricSet) -> float:
    author_cnts = metric_set.author_counts()
    return Impact_Funcs.calculate_collaborative_index(author_cnts)


def write_collaborative_index_example(metric_set: MetricSet) -> str:
    outstr = '<table class="example_table">'
    author_cnts = metric_set.author_counts()
    max_a = max(author_cnts)
    cnts = {a: author_cnts.count(a) for a in range(1, max_a+1)}
    ci = metric_set.metrics["collaborative index"].value
    rows = ["" for _ in range(3)]
    rows[0] = '<tr><th># of Authors (<em>a</em>)</th>'
    rows[1] = '<tr class="top_row"><th># of Publications (<em>f<sub>a</sub></em>)</th>'
    rows[2] = '<tr><th>Product (<em>a&times;f<sub>a</sub></em>)</th>'
    s = 0
    for a in range(1, max_a+1):
        rows[0] += f'<td>{a}</td>'
        rows[1] += f'<td>{cnts[a]}</td>'
        rows[2] += f'<td>{a*cnts[a]}</td>'
        s += a*cnts[a]

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The sum of the products is {s}, which yields a collaborative index of {ci:0.2} when divided by the '
               f'total number of publications ({len(author_cnts)}).</p>')
    return outstr


def metric_collaborative_index() -> Metric:
    m = Metric()
    m.name = "collaborative index"
    m.full_name = "collaborative index"
    m.symbol = "CI"
    m.synonyms = ["CI"]
    m.example = write_collaborative_index_example
    m.metric_type = FLOAT
    equation = r"$$\text{CI}=\frac{\sum\limits_{a=1}^{a_\max}{af_a}}{P},$$"
    m.description = ('<p>The Collaborative Index (Lawani 1980) is a basic measurement of the degree of collaboration '
                     f'within a set of publications. It is calculated as:</p>{equation}<p>where '
                     '<em>f<sub>a</sub></em> is the number of publications having <em>a</em> authors and '
                     '<em>a</em><sub>max</sub> is the largest number of authors for any publication.</p>')
    m.references = ["Lawani, S.M. (1980) <em>Quality, Collaboration and Citations in Cancer Research: "
                    "A Bibliometric Study</em> (doctoral dissertation). Florida State University: Tallahassee, "
                    "Florida."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_collaborative_index
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# degree of collaboration (Subramanyam 1983)
def calculate_degree_of_collaboration(metric_set: MetricSet) -> float:
    author_cnts = metric_set.author_counts()
    return Impact_Funcs.calculate_degree_of_collaboration(author_cnts)


def metric_degree_of_collaboration() -> Metric:
    m = Metric()
    m.name = "degree of collaboration"
    m.full_name = "degree of collaboration"
    m.symbol = "DC"
    m.synonyms = ["DC"]
    m.metric_type = FLOAT
    equation = r"$$\text{DC}=1-\frac{f_1}{P},$$"
    m.description = ('<p>The Degree of Collaboration index (Subramanyam 1983) is simply the proportion of '
                     f'a researcher\'s publications which are coauthored,</p>{equation}<p>where '
                     '<em>f</em><sub>1</sub> is the number of single-authored publications.')
    m.references = ["Subramanyam, K. (1983) Bibliometric studies of research collaboration: A review. "
                    "<em>Journal of Information Science</em> 6(1):33&ndash;38."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_degree_of_collaboration
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# collaborative coefficient (Ajiferuke et al. 1988)
def calculate_collaborative_coefficient(metric_set: MetricSet) -> float:
    author_cnts = metric_set.author_counts()
    return Impact_Funcs.calculate_collaborative_coefficient(author_cnts)


def write_collaborative_coefficient_example(metric_set: MetricSet) -> str:
    outstr = '<table class="example_table">'
    author_cnts = metric_set.author_counts()
    max_a = max(author_cnts)
    cnts = {a: author_cnts.count(a) for a in range(1, max_a+1)}
    cc = metric_set.metrics["collaborative coefficient"].value
    rows = ["" for _ in range(3)]
    rows[0] = '<tr><th># of Authors (<em>a</em>)</th>'
    rows[1] = '<tr class="top_row"><th># of Publications (<em>f<sub>a</sub></em>)</th>'
    rows[2] = '<tr><th>Quotient (<em>f<sub>a</sub></em>/<em>a</em>)</th>'
    s = 0
    for a in range(1, max_a+1):
        rows[0] += f'<td>{a}</td>'
        rows[1] += f'<td>{cnts[a]}</td>'
        rows[2] += f'<td>{cnts[a]/a:0.2f}</td>'
        s += cnts[a]/a

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The sum of the quotients is {s:0.2f}, which yields a collaborative index of {cc:0.4f}.</p>'
    return outstr


def metric_collaborative_coefficient() -> Metric:
    m = Metric()
    m.name = "collaborative coefficient"
    m.full_name = "collaborative coefficient"
    m.symbol = "CC"
    m.synonyms = ["CC"]
    m.example = write_collaborative_coefficient_example
    m.metric_type = FLOAT
    equation = r"$$\text{CC}=1-\frac{\sum\limits_{a=1}^{a_\max}{\frac{f_a}{a}}}{P},$$"
    m.description = ('<p>The Collaborative Coefficient (Ajiferuke <em>et al.</em> 1988) is another measure of the '
                     f'degree of collaboration within a set of publications. It is calculated as:</p>{equation}'
                     '<p>where <em>f<sub>a</sub></em> is the number of publications having <em>a</em> authors and '
                     '<em>a</em><sub>max</sub> is the largest number of authors for any publication.</p>')
    m.references = ["Ajiferuke, I., Q.L. Burrell, and J. Tague (1988) Collaborative coefficient: A single measure "
                    "of the degree of collaboration in research. <em>Scientometrics</em> 14(5&ndash;6):421&ndash;433."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_collaborative_coefficient
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# i10 index (Google Scholar)
def calculate_i10_index(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_i10_index(metric_set.citations)


def metric_i10_index() -> Metric:
    m = Metric()
    m.name = "i10"
    m.full_name = "i10 index"
    m.html_name = "<em>i10</em> index"
    m.axis_name = r"$\text{i10}$"
    m.symbol = "i10"
    m.metric_type = INT
    m.description = ('<p>The <em>i10</em> index (Google Scholar) is simply the number of publications which '
                     'have received at least 10 citations.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_i10_index
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# i100 index (Teixeira da Silva, 2021)
def calculate_i100_index(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_i100_index(metric_set.citations)


def metric_i100_index() -> Metric:
    m = Metric()
    m.name = "i100"
    m.full_name = "i100 index"
    m.html_name = "<em>i100</em> index"
    m.symbol = "i100"
    m.axis_name = r"$\text{i100}$"
    m.metric_type = INT
    m.description = ('<p>The <em>i100</em> index (Teixeira da Silva 2021) is an exapansion of Google Scholar\'s '
                     '__i10__ and is simply the number of publications which have received at least 100 citations.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_i100_index
    m.references = ["Teixeira da Silva, J.A. (2021) The i100-index, i1000-index and i10,000-index: expansion and "
                    "fortification of the Google Scholar h-index for finer-scale citation descriptions and researcher "
                    "classification. <em>Scientometrics</em> 126:3667-3672."]
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# i1000 index (Teixeira da Silva, 2021)
def calculate_i1000_index(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_i1000_index(metric_set.citations)


def metric_i1000_index() -> Metric:
    m = Metric()
    m.name = "i1000"
    m.full_name = "i1000 index"
    m.html_name = "<em>i1000</em> index"
    m.symbol = "i1000"
    m.axis_name = r"$\text{i1000}$"
    m.metric_type = INT
    m.description = ('<p>The <em>i1000</em> index (Teixeira da Silva 2021) is an exapansion of Google Scholar\'s '
                     '__i10__ and is simply the number of publications which have received at least 1000 '
                     'citations.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_i1000_index
    m.references = ["Teixeira da Silva, J.A. (2021) The i100-index, i1000-index and i10,000-index: expansion and "
                    "fortification of the Google Scholar h-index for finer-scale citation descriptions and researcher "
                    "classification. <em>Scientometrics</em> 126:3667-3672."]
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# p1 index (van Eck and Waltman 2008)
def calculate_p1_index(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_p1_index(metric_set.citations)


def metric_p1_index() -> Metric:
    m = Metric()
    m.name = "P1"
    m.full_name = "p-index (P1)"
    m.html_name = "<em>p-</em>index (<em>P</em><sub>1</sub>)"
    m.symbol = "P1"
    m.axis_name = r"$P_1$"
    m.synonyms = ["<em>p-</em>index (<em>P</em><sub>1</sub>)", "<em>P</em><sub>1</sub>"]
    m.metric_type = INT
    m.description = ('<p><em>P</em><sub>1</sub> (van Eck and Waltman 2008), also known as the <em>p-</em>index, is '
                     'simply the number of publications which have received at least one citation.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_p1_index
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Uncited Publications"] = True
    return m


# PC%
def calculate_cited_paper_percent(metric_set: MetricSet) -> float:
    return Impact_Funcs.calculate_cited_paper_percent(metric_set.citations)


def metric_cited_paper_percent() -> Metric:
    m = Metric()
    m.name = "cited paper percent"
    m.full_name = "cited paper percent"
    m.synonyms = ["<em>P</em><sub>C</sub>%"]
    m.symbol = "Pc%"
    m.metric_type = FLOAT
    m.description = ('<p>The cited paper percent is simply the percent of publications which have received at least '
                     'one citation.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_cited_paper_percent
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Uncited Publications"] = True
    return m


# uncitedness factor
def calculate_uncitedness_factor(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_uncitedness_factor(metric_set.citations)


def metric_uncitedness_factor() -> Metric:
    m = Metric()
    m.name = "uncitedness factor"
    m.full_name = "uncitedness factor"
    m.symbol = "Pu"
    m.synonyms = ["<em>UF</em>", "<em>P<sub>U</sub></em>"]
    m.metric_type = INT
    equation = r"$$P_U = P - P_1,$$"
    m.description = (f'<p>The uncitedness factor is simply the number of uncited publications, or</p>{equation}'
                     '<p>where <em>P</em><sub>1</sub> is the number of publications with at least one citation.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_uncitedness_factor
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Uncited Publications"] = True
    return m


# UF%
def calculate_uncited_paper_percent(metric_set: MetricSet) -> float:
    return Impact_Funcs.calculate_uncited_paper_percent(metric_set.citations)


def metric_uncited_paper_percent() -> Metric:
    m = Metric()
    m.name = "uncited paper percent"
    m.full_name = "uncited paper percent"
    m.synonyms = ["<em>P</em><sub>U</sub>%"]
    m.symbol = "Pu%"
    m.metric_type = FLOAT
    equation = r"$$P_U\% = 100 - P_C\%,$$"
    m.description = ('<p>The uncited paper percent is simply the percent of publications which have not received any '
                     f'citations, or</p>{equation}<p>where <em>P</em><sub>C</sub>% is the percent of '
                     'publications with at least one citation.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_uncited_paper_percent
    m.properties["Basic Statistic"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Uncited Publications"] = True
    return m


# # beauty coefficient (Ke et al. 2015)
# def calculate_beauty_coefficient(metric_set: MetricSet) -> list:
#     metric_list = metric_set.parent_list
#     metric_pos = metric_list.index(metric_set)
#     pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
#     return Impact_Funcs.calculate_beauty_coefficient(pub_data)
#
#
# def metric_beauty_coefficient() -> Metric:
#     m = Metric()
#     m.name = "beauty coefficient"
#     m.full_name = "beauty coefficient"
#     m.html_name = "beauty coefficient"
#     m.symbol = "B"
#     # m.metric_type = FLOATLIST
#     m.metric_type = LIST
#     m.list_formats = FLOAT
#     line_equation = r"$$x_t = \frac{c_{\max}-c_0}{t_{\max}}t+c_{0}.$$"
#     b_equation = r"$$B=\sum^{t_\max}_{t=0}{\frac{\frac{c_\max-c_0}{t_\max}t+c_0-c_t}{\max{\left(1, c_t\right)}}}.$$"
#     m.description = "<p>The Beauty Coefficient attempts to measure the citation trajectory of individual " \
#                     "publications to better understand when they reach peak impact. It is related to the concept of "
#                     "awakening time, which means to measure when a previously unnoticed publication suddenly begins "
#                     "to accumulate citations. Let <em>c<sub>t</sub></em> be " \
#                     "the number of citations received by the publication in it's <em>t</em><sup>th</sup> year since "
#                     "publication. The year with the maximum number of citations (<em>c</em><sub>max</sub>) is "
#                     "<em>t</em><sub>max</sub>. In a plot of citations by year, one could add a straight line "
#                     "(<em>x</em>) connecting the number of citations in the first year (0, " \
#                     "<em>c</em><sub>0</sub>) to the maximum number of citations (<em>t</em><sub>max</sub>, " \
#                     "<em>c</em><sub>max</sub>). This line is described by the equation</p>" + line_equation + \
#                     "<p>The Beauty coefficient is the sum of the ratios between " \
#                     "<em>x<sub>t</sub></em>&minus;<em>c<sub>t</sub></em> and max(1, <em>c<sub>t</sub></em>) for all "
#                     "<em>t</em> up through <em>t</em><sub>max</sub>.</p>" + b_equation + \
#                     "<p>Publications whose citation rate grows linearly with time will have a <em>B</em> equal to " \
#                     "zero (there is no difference between the observed citation curve and <em>x</em>). A value of " \
#                     "zero is also found when a publication is cited very quickly and then forgotten. Large " \
#                     "positive values indicate publications whose citation recognition was delayed after publication, "
#                     "while negative values indicate concave publication trajectories.</p>"
#     m.references = ["Ke, Q., E. Ferrara, F. Radicchi, and A. Flammini (2015) Defining and identifying Sleeping "
#                     "Beauties in science. <em>Proceedings of the National Academy of Sciences USA</em> "
#                     "112(24):7426&ndash;7431."]
#     # m.graph_type = MULTILINE_CHART_LEFT
#     m.draw_graph = Impact_Graphs.draw_graph_multiline_left_chart
#     m.calculate = calculate_beauty_coefficient
#     return m


# # awakening time (Ke et al. 2015)
# def calculate_awakening_time(metric_set: MetricSet) -> list:
#     metric_list = metric_set.parent_list
#     metric_pos = metric_list.index(metric_set)
#     pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
#     return Impact_Funcs.calculate_awakening_time(pub_data)
#
#
# def metric_awakening_time() -> Metric:
#     m = Metric()
#     m.name = "awakening time"
#     m.full_name = "awakening time"
#     m.html_name = "awakening time"
#     m.symbol = "ta"
#     # m.metric_type = INTLIST
#     m.metric_type = LIST
#     m.list_formats = INT
#     # m.description = "The uncited paper percent is simply the percent of publications which have not received any " \
#     #                 "citations, or</p>" + equation + "<p>where <em>P</em><sub>C</sub>% is the percent of " \
#     #                 "publications with at least one citation.</p>"
#     m.references = ["Ke, Q., E. Ferrara, F. Radicchi, and A. Flammini (2015) Defining and identifying Sleeping "
#                     "Beauties in science. <em>Proceedings of the National Academy of Sciences USA</em> "
#                     "112(24):7426&ndash;7431."]
#     # m.graph_type = MULTILINE_CHART_LEFT
#     m.draw_graph = Impact_Graphs.draw_graph_multiline_left_chart
#     m.calculate = calculate_awakening_time
#     return m


# # h-index for principal investigators (Steinbruchel 2019)
# def calculate_principal_h(metric_set: MetricSet) -> list:
#     # metric_list = metric_set.parent_list
#     # metric_pos = metric_list.index(metric_set)
#     # pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
#     # return Impact_Funcs.calculate_awakening_time(pub_data)
#     pass
#
#
# def metric_principal_h() -> Metric:
#     m = Metric()
#     # m.name = "awakening time"
#     # m.full_name = "awakening time"
#     # m.html_name = "awakening time"
#     # m.symbol = "ta"
#     # m.metric_type = INTLIST
#     # m.description = "The uncited paper percent is simply the percent of publications which have not received any " \
#     #                 "citations, or</p>" + equation + "<p>where <em>P</em><sub>C</sub>% is the percent of " \
#     #                 "publications with at least one citation.</p>"
#     m.references = ["Steinbrüchel, C. (2019) A citation index for principal investigators. <em>Scientometrics</em> "
#                     "118(1):305-320."]
#     # m.graph_type = MULTILINE_CHART_LEFT
#     # m.calculate = calculate_awakening_time
#     return m


# apparent h-index (Mohammed et al. 2020)
def calculate_apparent_h_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    citations = metric_set.citations
    return Impact_Funcs.calculate_apparent_h_index(citations, h)


def write_apparent_h_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    ha = metric_set.metrics["apparent h-index"].value
    non_zero_cnt = 0
    for i, c in enumerate(citations):
        if c > 0:
            non_zero_cnt += 1
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h}. Of the {len(citations)} publications, {non_zero_cnt} have at least '
               f'one citation. The apparent <em>h-</em>index is therefore {h}&times;{non_zero_cnt}/{len(citations)} = '
               f'{ha:0.2f}</p>')
    return outstr


def metric_apparent_h_index() -> Metric:
    m = Metric()
    m.name = "apparent h-index"
    m.full_name = "apparent h-index"
    m.html_name = "apparent <em>h-</em>index"
    m.symbol = "<em>h<sub>A</sub></em>"
    m.synonyms = ["<em>h<sub>A</sub></em>"]
    m.axis_name = r"$h_A$"
    m.metric_type = FLOAT
    m.example = write_apparent_h_index_example
    equation = r"$$h_A=h \frac{P_{\textrm{non-zero cites}}}{P}.$$"
    m.description = ('<p>The apparent <em>h-</em>index (Mohammed <em>et al.</em> 2020) is simply the __h-index__ '
                     'times the proportion of publications that have at least one citation; it is similar to the '
                     f'__normalized h-index__.</p>{equation}')
    m.references = ["Mohammed, S., A. Morgan, and E. Nyantakyi (2020) On the influence of uncited publications on a "
                    "researcher's <em>h</em>‑index. <em>Scientometrics</em>."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_apparent_h_index
    m.properties["Uncited Publications"] = True
    m.properties["All Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Metric"] = True
    return m


# rec index (Levene et al. 2019)
def calculate_rec_index(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_rec_index(metric_set.citations)


# def write_rec_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["rec-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'rec-square'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     # citation curve
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#             if v > maxv:
#                 v = "null"
#         outstr += ", {}, null],\n".format(v)
#         output.append(outstr)
#     # chi-square
#     chisq = 0
#     chir = -1
#     for i, c in enumerate(tmp_cites):
#         p = (i + 1)*c
#         if p > chisq:
#             chisq = p
#             chir = i
#     # write chi-square
#     output.append("           [{}, null, {}],\n".format(0, tmp_cites[chir]))
#     output.append("           [{}, null, {}],\n".format(chir+1, tmp_cites[chir]))
#     output.append("           [{}, null, {}],\n".format(chir+1, 0))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#     return output


def create_rec_index_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    # h = metric_set.metrics["h-index"].value

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(len(metric_set.citations))]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # square lines
    rect_data = Impact_Graphs.LineData()
    output.append(rect_data)
    rec_area = 0
    rec_x = -1
    for i, c in enumerate(cite_data.y):
        p = (i + 1)*c
        if p > rec_area:
            rec_area = p
            rec_x = i
    rec_y = cite_data.y[rec_x]

    rect_data.x = [0, 0, rec_x, rec_x, 0]
    rect_data.y = [0, rec_y, rec_y, 0, 0]
    rect_data.style = ":"
    rect_data.label = "rec-square"

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc
    general_data.y_max = general_data.x_max

    return output


def write_rec_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th><em>i</em>&times;<em>C<sub>i</sub></em></th>'
    rec = metric_set.metrics["rec-index"].value
    chisq = 0
    for i, c in enumerate(citations):
        p = (i + 1)*c
        if p > chisq:
            chisq = p
        if p == rec:
            ec = ' class="box"'
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td{ec}>{p}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rectangle which can fit under the citation curve has an area of {rec}.</p>'
    return outstr


def metric_rec_index() -> Metric:
    m = Metric()
    m.name = "rec-index"
    m.full_name = "rec-index"
    m.html_name = "<em>rec-</em>index"
    m.symbol = "<em>rec</em>"
    m.axis_name = r"$rec$"
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "rec_index_desc"
    graph.data = create_rec_index_desc_graph_data
    m.example = write_rec_index_example
    m.synonyms = ["<em>rec-</em>index", "maxprod-index"]
    m.metric_type = INT
    m.description = ('<p>The <em>rec-</em>index (Levene <em>et al.</em> 2019) is the area of the largest rectangle ' 
                     'which can fit under the citation curve; similar to how <em>h</em><sup>2</sup> is the area of ' 
                     'the largest square. This index is identical to the '
                     '<span class="metric_name">maxprod-index</span> previously suggested by Kosmulski (2007)</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Levene, M., T. Fenner, and J. Bar-Ilan (2019) Characterisation of the <em>χ</em>-index and the "
                    "<em>rec-index</em>. <em>Scientometrics</em> 120:885-896.",
                    "Kosmulski, M. (2007) MAXPROD - A new index for assessment of the scientific output of an "
                    "individual, and a comparison with the <em>h-</em>index. <em>International Journal of "
                    "Scientometrics, Informetrics and Bibliometrics</em> 11(1):5."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_rec_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# chi index (Fenner et al. 2018)
def calculate_chi_index(metric_set: MetricSet) -> float:
    rec = metric_set.metrics["rec-index"].value
    return Impact_Funcs.calculate_chi_index(rec)


# def write_chi_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["chi-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'chi-square'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     # citation curve
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#             if v > maxv:
#                 v = "null"
#         outstr += ", {}, null],\n".format(v)
#         output.append(outstr)
#     # chi-square
#     chisq = 0
#     chir = -1
#     for i, c in enumerate(tmp_cites):
#         p = (i + 1)*c
#         if p > chisq:
#             chisq = p
#             chir = i
#     # write chi-square
#     output.append("           [{}, null, {}],\n".format(0, tmp_cites[chir]))
#     output.append("           [{}, null, {}],\n".format(chir+1, tmp_cites[chir]))
#     output.append("           [{}, null, {}],\n".format(chir+1, 0))
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [2, 2],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#     return output


def write_chi_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th><em>i</em>&times;<em>C<sub>i</sub></em></th>'
    chi = metric_set.metrics["chi-index"].value
    chisq = 0
    for i, c in enumerate(citations):
        p = (i + 1)*c
        if p > chisq:
            chisq = p
        if math.sqrt(p) == chi:
            ec = ' class="box"'
        else:
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td{ec}>{p}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The largest rectangle which can fit under the citation curve has an area of {chisq}, the '
               f'square-root of which is <em>χ</em> = {chi:0.3f}.</p>')
    return outstr


def metric_chi_index() -> Metric:
    m = Metric()
    m.name = "chi-index"
    m.full_name = "χ-index"
    m.html_name = "<em>χ-</em>index"
    m.symbol = "<em>χ</em>"
    m.axis_name = r"$\chi$"
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "chi_index_desc"
    graph.data = create_rec_index_desc_graph_data  # identical figure as rec_index
    m.example = write_chi_index_example
    m.synonyms = ["<em>χ-</em>index"]
    m.metric_type = FLOAT
    m.description = ('<p>The <em>χ-</em>index (Fenner <em>et al.</em> 2018) is the square-root of the size of the '
                     'largest rectangle which can fit under the citation curve; similar to how the __h-index__ is the '
                     'size of the largest square. It is the square-root of the __rec-index__.</p>'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Fenner, T., M. Harris, M. Levene, and J. Bar-Ilan (2018) A novel bibliometric index with a "
                    "simple geometric interpretation. <em>PLoS ONE</em> 13(7):e0200098."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_chi_index
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# rec index (Levene et al. 2020)
def calculate_reci_recp(metric_set: MetricSet) -> list:
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_reci_recp(metric_set.citations, h)


def write_reci_recp_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(8)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr class="top_row"><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    rows[3] = '<tr><th><em>i</em>&times;<em>C<sub>i</sub></em></th>'
    rows[4] = '<tr class="top_row"><th></th>'
    rows[5] = '<tr><th>min(<em>h</em>, <em>C<sub>i</sub></em>)</th>'
    rows[6] = '<tr><th>min(<em>h</em>, <em>C<sub>i</sub></em>)&times;<em>i</em></th>'
    rows[7] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    recip = metric_set.metrics["reci-recp"].value
    reci = recip[0]
    recp = recip[1]
    for i, c in enumerate(citations):
        iarea = (i + 1)*c
        iv = ""
        iec = ""
        if i + 1 <= h:
            if iarea == reci:
                iec = ' class="box"'
                iv = '<em>rec<sub>I</sub></em>'

        pec = ""
        pv = ""
        parea = min(h, c) * (i + 1)
        if i + 1 >= h:
            if parea == recp:
                pec = ' class="box"'
                pv = ' <em>rec<sub>P</sub></em>'
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        if i + 1 == h:
            rows[2] += f'<td><em>h</em>{NBEQ}{h}</td>'
        else:
            rows[2] += '<td></td>'
        if i+1 <= h:
            rows[3] += f'<td{iec}>{iarea}</td>'
        else:
            rows[3] += '<td></td>'
        rows[4] += f'<td>{iv}</td>'
        if i+1 >= h:
            rows[5] += f'<td>{min(h, c)}</td>'
            rows[6] += f'<td{pec}>{parea}</td>'
        else:
            rows[5] += '<td></td>'
            rows[6] += '<td></td>'
        rows[7] += f'<td>{pv}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    return outstr


def metric_reci_recp() -> Metric:
    m = Metric()
    m.name = "reci-recp"
    m.full_name = "recI, recP"
    m.html_name = "<em>rec<sub>I</sub></em>, <em>rec<sub>P</sub></em>"
    m.symbol = "[<em>rec<sub>I</sub></em>, <em>rec<sub>P</sub></em>]"
    m.axis_name = r"$rec_I, rec_P$"
    m.example = write_reci_recp_example
    m.synonyms = ["<em>rec<sub>I</sub></em>, <em>rec<sub>P</sub></em>"]
    m.metric_type = LIST
    m.list_formats = INT
    m.description = ('<p>The [<em>rec<sub>I</sub></em>, <em>rec<sub>P</sub></em>] metrics (Levene <em>et al.</em> '
                     '2020) are a two-dimensional expansion of the __rec-index__, where <em>rec<sub>I</sub></em> '
                     'is the largest vertical (influential) rectangle that can fit under the citation '
                     'curve and <em>rec<sub>P</sub></em> is the largest horizontal (prolific) rectangle '
                     'that can fit under the citation curve. The minimum size of both is the area of the '
                     '<em>h-</em>square; the larger of the two is equal to the <em>rec</em>-index.</p>')
    m.references = ["Levene, M., M. Harris, and T. Fenner (2020) A two‑dimensional bibliometric index reflecting both "
                    "quality and quantity. <em>Scientometrics</em>."]
    m.draw_graph = Impact_Graphs.draw_graph_two_line_chart
    m.calculate = calculate_reci_recp
    m.properties["Alternative Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Multidimensional Metric"] = True
    return m


# academic trace (Ye and Leydesdorff 2014)
def calculate_academic_trace(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    core_cites = metric_set.metrics["h-core cites"].value
    citations = metric_set.citations
    return Impact_Funcs.calculate_academic_trace(citations, core_cites, h)


def write_academic_trace_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(3)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    h = metric_set.metrics["h-index"].value
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    t = metric_set.metrics["academic trace"].value
    pz = 0
    for i, c in enumerate(citations):
        if c == 0:
            pz += 1
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h</em>-index is {h}; the total number of citations (<em>C<sup>P</sup></em>) is '
               f'{total_cites}; the number of citations in the top <em>h</em> publications (<em>C<sup>h</sup></em>) '
               f'is {core_cites}; the total number of publications (P) is {len(citations)}; and the number of '
               f'publications with zero citations (<em>P<sub>z</sub></em>) is {pz}. Entered in the above formula, '
               f'the academic trace is {t:0.4f}.</p>')
    return outstr


def metric_academic_trace() -> Metric:
    m = Metric()
    m.name = "academic trace"
    m.full_name = "academic trace"
    m.html_name = "academic trace"
    m.symbol = "<em>tr</em>(V)"
    m.example = write_academic_trace_example
    m.synonyms = ["tr(V)", "academic trace"]
    equation = (r"$$tr\left(V\right)=\frac{h^2}{P}+\frac{\left(C^P-C^h\right)^2}{C^P}+\frac{\left(C^h - "
                r"h^2\right)^2}{C^P} -\frac{P_z^2}{P}.$$")
    m.metric_type = FLOAT
    m.description = ('<p>The Academic Trace (Ye and Leydesdorff 2014; Ye <em>et al.</em> 2017) starts by taking '
                     'the concept of the citation curve and describing it as three vectors of information. The '
                     'first vector (<strong>X</strong>) separates publications into those in the core '
                     '(X<sub>1</sub>), those in the tail with at least one citation (X<sub>2</sub>), and those with '
                     'zero citations (X<sub>3</sub>). These three values are each calculated as the square of the '
                     'count of publications in each category, divided by the total number of publications. The second '
                     'vector (<strong>Y</strong>) separates citations into those in the core block (Y<sub>1</sub>), '
                     'those in the tail (Y<sub>2</sub>), and the excess citations in the core above the core block '
                     '(Y<sub>3</sub>). These values are calculated as the square of the count of citations within '
                     'each category, divided by the total citation. The third vector (<strong>Z</strong>) '
                     'contrasts particularly highly cited '
                     'publications and those with zero citations, and is simply the difference of the corresponding '
                     'values of the first two vectors, X<sub>1</sub> - Y<sub>1</sub>, X<sub>2</sub> - Y<sub>2</sub>, '
                     'and X<sub>3</sub> - Y<sub>3</sub>. These vectors form a 3D matrix, the trace of which '
                     'is a measure of academic performance. The trace can be determined as X<sub>1</sub> + '
                     'Y<sub>2</sub> + Z<sub>3</sub>; a "shortcut" formula (Ding '
                     f'<em>et al.</em> 2020) is as follows:</p><p>{equation}</p><p>where <em>P<sub>z</sub></em> '
                     'is the number of publications with zero citations and the rest of the values have been '
                     'defined earlier.</p>')
    m.references = ["Ye, F.Y., and L. Leydesdorff (2014) The “Academic Trace” of the Performance Matrix: A "
                    "Mathematical Synthesis of the "
                    "<em>h</em>-Index and the Integrated Impact Indicator (I3). <em>Journal of the Association for "
                    "Information Science and Technology</em> 65(4):742&ndash;750.",
                    "Ye, F.Y., L. Bornmann, and L. Leydesdorff (2017) <em>h</em>-based I3-type multivariate vectors: "
                    "Multidimensional indicators of publication and citation scores. <em>Collnet Journal of "
                    "Scientometrics and Information Management</em> 11(1):153&ndash;171.",
                    "Ding, J., C. Liu, and G.A. Kandonga (2020) Exploring the limitations of the <em>h‑</em>index and "
                    "<em>h</em>‑type indexes in measuring the research performance of authors. "
                    "<em>Scientometrics.</em>"]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_academic_trace
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Alternative Metric"] = True
    m.properties["Tail Citations"] = True
    m.properties["Tail Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    m.properties["Uncited Publications"] = True
    return m


# scientific quality index (Pluskiewicz1 et al. 2019)
def calculate_scientific_quality_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    self_citations = metric_set.self_citations
    return Impact_Funcs.calculate_scientific_quality_index(citations, self_citations)


def write_scientific_quality_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of non-self citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    all_citations = metric_set.citations
    self_citations = metric_set.self_citations
    citations = [all_citations[i] - self_citations[i] for i in range(len(self_citations))]
    citations = sorted(citations, reverse=True)
    rows = ["" for _ in range(2)]
    rows[0] = '<tr class="top_row"><th>Non-self Citations</th>'
    rows[1] = '<tr><th>Rank</th>'
    cnt = 0
    sum_cites = 0
    for i, c in enumerate(citations):
        sum_cites += c
        if c >= 10:
            ec = ' class="box"'
            cnt += 1
        else:
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    n = len(citations)
    outstr += (f'<p>Of the {n} publications, {cnt} have 10 or more non-self citations, {cnt}/{n} = {cnt/n:0.1%}. '
               f'The total non-self citations is {sum_cites}, thus the mean non-self citations per publication is '
               f'{sum_cites/n:0.1f}. The SQI is the sum of these values, or {(100*cnt/n) + (sum_cites/n):0.1f}.</p>')
    return outstr


def metric_scientific_quality_index() -> Metric:
    m = Metric()
    m.name = "scientific quality index"
    m.full_name = "scientific quality index"
    m.html_name = "scientific quality index"
    m.symbol = "SQI"
    m.example = write_scientific_quality_index_example
    m.metric_type = FLOAT
    m.description = ('<p>The Scientific Quality Index (Pluskiewicz <em>et al.</em> 2019) is a slightly odd metric '
                     'which is simply the sum of the mean '
                     'citations per publication and the percent of publications with 10 or more citations (both '
                     'adjusted for self- and co-author citations, in a perfect world). The authors considered it to '
                     'be a slightly better judge of quality than metrics such as the __h-index__.</p>')
    m.references = ["Pluskiewicz, W., B. Drozdzowska, P. Adamczyk, and K. Noga (2019) Scientific Quality Index: A "
                    "composite size‑independent metric compared with <em>h</em>‑index for 480 medical researchers. "
                    "<em>Scientometrics</em> 119:1009&ndash;1016."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_scientific_quality_index
    m.properties["Alternative Metric"] = True
    m.properties["Self-Citation"] = True
    m.properties["Compound Metric"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# first author h-index (Butson and Yu 2010)
def calculate_first_author_h_index(metric_set: MetricSet) -> int:
    h = metric_set.metrics["h-index"].value
    author_pos = metric_set.author_position()
    is_core = metric_set.is_core
    return Impact_Funcs.calculate_first_author_h_index(h, author_pos, is_core)


def metric_first_author_h_index() -> Metric:
    m = Metric()
    m.name = "first-author h-index"
    m.full_name = "first-author h-index"
    m.html_name = "first-author <em>h-</em>index"
    m.metric_type = INT
    equation = r"$$h_{fa}=h \frac{P_h + P_{fa}}{P_h}=h + P_{fa}.$$"
    m.description = ('<p>The first-author <em>h-</em>index (Butson and Yu 2010) was designed to rescale output ' 
                     'between large and small collaborative research teams under an assumption that larger teams ' 
                     'could produce more output per year just by the nature of being larger. It attempts to rescale ' 
                     'the __h-index__ based on the number of publications in the <em>h-</em>core that were ' 
                     f'first-authored (<em>P<sub>fa</sub></em>).</p>{equation}<p>The authors did not seem to ' 
                     'realize that the number of papers in the core <em>P<sub>h</sub></em> is, by definition, equal ' 
                     'to <em>h</em> and thus some of the terms cancel, leaving the metric just the sum of ' 
                     '<em>h</em> and the number of first-authored papers that make up h. This index ranges from equal ' 
                     'to the <em>h-</em>index if the investigator is never a first author of publications in the ' 
                     '<em>h-</em>core to double the <em>h-</em>index if they are the first author of every ' 
                     'publication in the core.</p><p>This is conceptually similar to some other metrics such as the '
                     '__stratified h-index__ and the __hmaj-index__.</p>')
    m.symbol = "<em>h<sub>fa</sub></em>"
    m.synonyms = ["<em>h<sub>fa</sub></em>"]
    m.axis_name = r"$h_{fa}$"
    m.references = ["Butson, M.J., and P.K.N. Yu (2010) The first author h-index (h(fa)-index): levelling the field "
                    "for small and large institute medical and science scholars. <em>Australasian Physical and "
                    "Engineering Sciences in Medicine</em> 33:299&ndash;300."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_first_author_h_index
    m.properties["Core Property"] = True
    m.properties["Coauthorship"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# o-index (Dorogovtsev and Mendes 2015)
def calculate_o_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    max_cites = metric_set.metrics["max cites"].value
    return Impact_Funcs.calculate_o_index(h, max_cites)


def metric_o_index() -> Metric:
    m = Metric()
    m.name = "o-index"
    m.full_name = "o-index"
    m.html_name = "<em>o-</em>index"
    m.axis_name = r"$o$"
    m.metric_type = FLOAT
    equation = r"$$o=\sqrt{hC_{max}}.$$"
    m.description = ('<p>The <em>o-</em>index (Dorogovtsev and Mendses 2015) was designed to balance a researcher\'s '
                     'most-cited work with their diligence in regular publication, and is simply the geometric mean '
                     'of their __h-index__ and the count of citations to their most cited work. It is calculated '
                     f'as:</p>{equation}')
    m.symbol = "<em>o</em>"
    m.synonyms = ["<em>o</em>"]
    m.references = ["Dorogovtsev, S.N., and J.F. Mendes (2015) Ranking scientists. <em>Nature Physics</em> "
                    "11(11):882&ndash;883."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_o_index
    m.properties["Compound Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# discounted h-index (Ferrara and Romero 2013)
def calculate_discounted_h_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    total_self = metric_set.metrics["total self cites"].value
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_discounted_h_index(h, total_cites, total_self)


def metric_discounted_h_index() -> Metric:
    m = Metric()
    m.name = "discounted h-index"
    m.full_name = "discounted h-index"
    m.html_name = "discounted <em>h-</em>index"
    m.is_self = True
    m.metric_type = FLOAT
    equation = r"$$dh=h \sqrt{\frac{C^P-S^P}{C^P}},$$"
    m.description = ('<p>The discounted <em>h-</em>index (Ferrara and Romero 2013) was designed to adjust the '
                     '__h-index__ for self-citations by multiplying it by square-root of the percentage of total '
                     'citations that were not self-citations. It is readily calculated '
                     f'as:</p>{equation}<p>where <em>S<sup>P</sup></em> is the sum of self-citations for all '
                     'publications.')
    m.symbol = "<em>dh</em>"
    m.axis_name = r"$dh$"
    m.synonyms = ["<em>dh</em>"]
    m.references = ["Ferrara, E., and A.E. Romero (2013) Scientific impact evaluation and the effect of "
                    "self-citations: Mitigating the bias by discounting the h-index. <em>Journal of the American "
                    "Society for Information Science and Technology</em> 64(11):2332&ndash;2339."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_discounted_h_index
    m.properties["Core Metric"] = True
    m.properties["Self-Citation"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    return m


# j-index (Mikhailov 2014)
def calculate_mikhailov_j_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_mikhailov_j_index(citations)


# def write_mikhailov_j_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["Mikhailov j-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Citations', 'y=floor(x^3/2)', {'type': 'string', 'role': 'annotation'}],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     j = metric_set.metrics["Mikhailov j-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         # write citation count for ranked publication x
#         if x == 0:
#             v = "null"
#         else:
#             v = tmp_cites[x - 1]
#         outstr += ", {}".format(v)
#         # write y for y=x^2
#         v = math.floor(x**(3/2))
#         if v > maxv:
#             v = "null"
#         if x == j:
#             a = "\'j\'"
#         else:
#             a = "null"
#         outstr += ", {}, {}".format(v, a)
#         outstr += "],\n"
#         output.append(outstr)
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     # output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("		     series: { 0: {},\n")
#     output.append("		               1: {lineDashStyle: [4, 4],\n")
#     output.append("		                   annotations:{textStyle:{color: \'black\', italic: true,
#     bold: true}}}}\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "LineChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def create_mikhailov_j_desc_graph_data(metric_set: MetricSet) -> list:
    output = []

    # h = metric_set.metrics["h-index"].value
    n = len(metric_set.citations)

    # basic citation curve
    cite_data = Impact_Graphs.LineData()
    output.append(cite_data)
    cite_data.x = [i+1 for i in range(n)]
    cite_data.y = [c for c in metric_set.citations]
    cite_data.y.sort(reverse=True)
    cite_data.label = "Citations"
    maxc = max(cite_data.y)

    # # example points
    # point_data = Impact_Graphs.PointData()
    # output.append(point_data)
    # point_data.x = [h, h+1]
    # point_data.y = [h, h+1]
    # point_data.fillcolor = "none"

    # threshold line
    threshold_data = Impact_Graphs.LineData()
    output.append(threshold_data)
    threshold_data.x = [i+1 for i in range(n)]
    threshold_data.y = [i**(3/2) for i in range(n)]
    threshold_data.style = "--"
    threshold_data.label = r"$y = x^{3/2}$"

    # # annotation
    # annotation = Impact_Graphs.AnnotationData()
    # output.append(annotation)
    # annotation.label = f"$h = {h}$"
    # annotation.pos = (h, h)
    # annotation.textpos = (h+20, h)
    #
    # annotation = Impact_Graphs.AnnotationData()
    # output.append(annotation)
    # annotation.label = f"$h+1 = {h+1}$"
    # annotation.pos = (h+1, h+1)
    # annotation.textpos = (h+20, h+15)

    general_data = Impact_Graphs.GeneralData()
    output.append(general_data)
    general_data.x_label = "Rank"
    general_data.y_label = "Citation Count"
    general_data.inc_legend = True
    general_data.x_max = maxc
    general_data.y_max = general_data.x_max

    return output


def write_mikhailov_j_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(4)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th>floor(<em>i</em><sup>3/2</sup>)</th>'
    rows[3] = '<tr><th></th>'
    j = metric_set.metrics["Mikhailov j-index"].value
    for i, c in enumerate(citations):
        if i + 1 == j:
            v = f'<em>j</em>{NBEQ}{j}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td>{i+1}</td>'
        rows[2] += f'<td{ec}>{math.trunc((i+1)**(3/2))}</td>'
        rows[3] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>i</em>&nbsp;≤&nbsp;<em>C<sub>i</sub></em> is {j}.</p>'
    return outstr


def metric_mikhailov_j_index() -> Metric:
    m = Metric()
    m.name = "Mikhailov j-index"
    m.full_name = "j-index (Mikhailov)"
    m.html_name = "<em>j-</em>index (Mikhailov)"
    m.symbol = "<em>j</em>"
    m.axis_name = r"$j$"
    m.metric_type = INT
    m.example = write_mikhailov_j_index_example
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "mikhailov_j_index_desc"
    graph.data = create_mikhailov_j_desc_graph_data
    equation = r"$$j=\underset{i}{\max}\left(\text{floor}\left(i^{3/2}\right) \leq C_i\right).$$"
    m.description = ('<p>Mikhailov\'s <em>j</em>-index (Mikhailov 2014) falls between the __h-index__ and the '
                     '__h(2)-index__. Rather than requiring each publication in the core to have <em>h</em> or '
                     '<em>h</em><sup>2</sup> publications, respectively, it requires them to have '
                     f'<em>j</em><sup>3/2</sup>:</p>{equation}'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Mikhailov, O.V.e. (2014) A new version of the Hirsh index: The <em>j-</em>index. <em>Herald of "
                    "the Russian Academy of Sciences</em> 84(3):217&ndash;220."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_mikhailov_j_index
    m.properties["Core Metric"] = True
    m.properties["Core Citations"] = True
    m.properties["Core Publications"] = True
    return m


# year-based EM-index by publications (Bihari and Tripathi 2018)
def calculate_year_based_em_pub(metric_set: MetricSet) -> float:
    pub_years = metric_set.publication_years()
    return Impact_Funcs.calculate_year_based_em_pub(pub_years)


def write_year_based_em_pub_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by number of publications, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the publications of the top <em>E<sub>i</sub></em> '
              'years. All years beyond the top <em>E<sub>i</sub></em> are ignored at subsequent steps.</p>')

    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    data = [pub_years.count(y) for y in range(miny, maxy + 1)]
    data.sort(reverse=True)

    ydata = [[pub_years.count(y), y] for y in range(miny, maxy + 1)]
    ydata.sort(reverse=True)

    # calculate vector
    em_components = Impact_Funcs.calculate_em_components(data)
    outstr += '<table class="example_table">\n'

    outstr += '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    for x in ydata:
        outstr += f'<td>{x[1]}</td>'
    outstr += '</tr>\n'

    oldh = len(data)
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Publications per Year (<em>P<sub>i</sub></em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Publications (<em>P<sub>i</sub></em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(data)*'<td></td>')
        rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(data):
            if i >= oldh:
                rows[0] += '<td class="light_box"></td>'
                rows[1] += '<td class="light_box"></td>'
                rows[2] += '<td></td>'
            else:
                if i + 1 == h:
                    v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                rows[0] += f'<td{ec}>{c}</td>'
                rows[1] += f'<td{ec}>{i+1}</td>'
                rows[2] += f'<td>{v}</td>'
        data = [max(0, c-h) for c in data]
        oldh = h

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)

    outstr += '</table>'
    yp_em = metric_set.metrics["Year-based EM-index by publications"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. The Year-based '
               f'<em>EM</em>-index by publications is the square-root of this sum, thus '
               f'<em>Yp_EM</em>{NBEQ}{yp_em:0.4f}.</p>')
    return outstr


def metric_year_based_em_pub() -> Metric:
    m = Metric()
    m.name = "Year-based EM-index by publications"
    m.full_name = "Year-based EM-index by publications"
    m.html_name = "Year-based <em>EM</em>-index by publications"
    m.symbol = "<em>Yp_EM</em>"
    m.axis_name = r"$Yp\_EM$"
    m.synonyms = ["<em>Yp_EM</em>"]
    m.example = write_year_based_em_pub_example
    m.metric_type = FLOAT
    m.description = ('<p>The Year-based <em>EM</em>-index by publications (Bihari and S. Tripathi 2018) is an '
                     'adapation of the '
                     '__EM-index__ applied to the __career years h-index by pub__. This metric is a measure '
                     'of publication intensity or distribution, rather than citation intensity as captured by '
                     'most __h-index__ type indices. Rather than create a list of publications ranked by citation '
                     'count, one creates a list of years ranked by publication count. '
                     'This list is then processed in the same multivariate manner as the EM-index.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2018) Year based EM-index: A new approach to evaluate the "
                    "scientific impact of scholars. <em>Scientometrics</em> 114:1175&ndash;1205."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_year_based_em_pub
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Time"] = True
    return m


# year-based EM-index by publication year citations (Bihari and Tripathi 2018)
def calculate_year_based_em_pycites(metric_set: MetricSet) -> float:
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    return Impact_Funcs.calculate_year_based_em_pycites(pub_years, cites)


def write_year_based_em_pycites_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by number of citations, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'years. All years beyond the top <em>E<sub>i</sub></em> are ignored at subsequent steps.</p>')

    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    cites = metric_set.citations
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)

    ydata = [[year_cnts[y], y] for y in range(miny, maxy + 1)]
    ydata.sort(reverse=True)

    # # calculate vector
    em_components = Impact_Funcs.calculate_em_components(data)

    outstr += '<table class="example_table">\n'
    outstr += '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    for x in ydata:
        outstr += f'<td>{x[1]}</td>'
    outstr += '</tr>\n'

    oldh = len(data)
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(4)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations from Publication Year (<em>C<sub>i</sub></em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(data)*'<td></td>')
        rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(data):
            if i >= oldh:
                rows[0] += '<td class="light_box"></td>'
                rows[1] += '<td class="light_box"></td>'
                rows[2] += '<td></td>'
            else:
                if i + 1 == h:
                    v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                rows[0] += f'<td{ec}>{c}</td>'
                rows[1] += f'<td{ec}>{i+1}</td>'
                rows[2] += f'<td>{v}</td>'
        data = [max(0, c-h) for c in data]
        oldh = h

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)

    outstr += '</table>'
    yp_em = metric_set.metrics["Year-based EM-index by publication year citations"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. Year-based '
               f'<em>EM</em>-index by publication year citations is the square-root of this sum, thus '
               f'<em>Ypc_EM</em>{NBEQ}{yp_em:0.4f}.</p>')
    return outstr


def metric_year_based_em_pycites() -> Metric:
    m = Metric()
    m.name = "Year-based EM-index by publication year citations"
    m.full_name = "Year-based EM-index by publication year citations"
    m.html_name = "Year-based <em>EM</em>-index by publication year citations"
    m.symbol = "<em>Ypc_EM</em>"
    m.axis_name = r"$Ypc\_EM$"
    m.synonyms = ["<em>Ypc_EM</em>"]
    m.example = write_year_based_em_pycites_example
    m.metric_type = FLOAT
    m.description = ('<p>The Year-based <em>EM</em>-index by publication year citations (Bihari and S. Tripathi 2018) '
                     'is an adapation of the __EM-index__ applied to the __career years h-index by cite__. This '
                     'metric is a measure of citation intensity or distribution by publication year, rather than by '
                     'publication. Rather than create a list of publications ranked by citation count, one creates a '
                     'list of years ranked by citation count for all publications from that year. '
                     'This list is then processed in the same multivariate manner as the <em>EM-</em>index.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2018) Year based EM-index: A new approach to evaluate the "
                    "scientific impact of scholars. <em>Scientometrics</em> 114:1175&ndash;1205."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_year_based_em_pycites
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    return m


# year-based EM-index by citations (Bihari and Tripathi 2018)
def calculate_year_based_em_cites(metric_set: MetricSet) -> float:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_list[:metric_pos + 1]]
    return Impact_Funcs.calculate_year_based_em_cites(total_cite_list)


def write_year_based_em_cites_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by number of citations received that year, from highest to lowest. After each '
              'step, <em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'years. All years beyond the top <em>E<sub>i</sub></em> are ignored at subsequent steps.</p>')

    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    metric_pos = metric_set.parent_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_set.parent_list[:metric_pos + 1]]
    total_cites_per_year = Impact_Funcs.total_citations_each_year(total_cite_list)
    data = [d for d in total_cites_per_year]
    data.sort(reverse=True)

    tmpy = [y for y in range(miny, maxy + 1)]
    ydata = [[total_cites_per_year[y], tmpy[y]] for y in range(len(tmpy))]
    ydata.sort(reverse=True)

    # calculate vector
    em_components = Impact_Funcs.calculate_em_components(data)
    outstr += '<table class="example_table">\n'
    outstr += '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    for x in ydata:
        outstr += '<td>{}</td>'.format(x[1])
    outstr += '</tr>\n'

    oldh = len(data)
    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations received in year (<em>C<sub>i</sub></em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(data)*'<td></td>')
        rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(data):
            if i >= oldh:
                rows[0] += '<td class="light_box"></td>'
                rows[1] += '<td class="light_box"></td>'
                rows[2] += '<td></td>'
            else:
                if i + 1 == h:
                    v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                    ec = ' class="box"'
                else:
                    v = ""
                    ec = ""
                rows[0] += f'<td{ec}>{c}</td>'
                rows[1] += f'<td{ec}>{i+1}</td>'
                rows[2] += f'<td>{v}</td>'
        data = [max(0, c - h) for c in data]
        oldh = h

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)

    outstr += '</table>'
    yp_em = metric_set.metrics["Year-based EM-index by citations"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. The Year-based '
               f'<em>EM-</em>index by citations is the square-root of this sum, thus '
               f'<em>Yc_EM</em>{NBEQ}{yp_em:0.4f}.</p>')
    return outstr


def metric_year_based_em_cites() -> Metric:
    m = Metric()
    m.name = "Year-based EM-index by citations"
    m.full_name = "Year-based EM-index by citations"
    m.html_name = "Year-based <em>EM</em>-index by citations"
    m.symbol = "<em>Yc_EM</em>"
    m.axis_name = r"$Yc\_EM$"
    m.synonyms = ["<em>Yc_EM</em>"]
    m.example = write_year_based_em_cites_example
    m.metric_type = FLOAT
    m.description = ('<p>The Year-based <em>EM</em>-index by citations (Bihari and S. Tripathi 2018) is an '
                     'adapation of the __EM-index__ applied to the citation counts received in a year (to all '
                     'publications), rather than citations clustered by year of publication. '
                     'One creates a list of years ranked by citations received that year for all publications. '
                     'This list is then processed in the same multivariate manner as the <em>EM-</em>index.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2018) Year based EM-index: A new approach to evaluate the "
                    "scientific impact of scholars. <em>Scientometrics</em> 114:1175&ndash;1205."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_year_based_em_cites
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    return m


# year-based EM'-index by publications (Bihari and Tripathi 2018)
def calculate_year_based_emp_pub(metric_set: MetricSet) -> float:
    pub_years = metric_set.publication_years()
    return Impact_Funcs.calculate_year_based_emp_pub(pub_years)


def write_year_based_emp_pub_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by number of publications, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the publications of the top <em>E<sub>i</sub></em> '
              'years. The yearly data is then resorted from high to low for each subsequent step.</p>')

    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    data = [pub_years.count(y) for y in range(miny, maxy + 1)]
    data.sort(reverse=True)

    ydata = [[pub_years.count(y), y] for y in range(miny, maxy + 1)]
    ydata.sort(reverse=True)

    # calculate vector
    em_components = Impact_Funcs.calculate_emp_components(data)
    outstr += '<table class="example_table">\n'

    outstr += '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    for x in ydata:
        outstr += f'<td>{x[1]}</td>'
    outstr += '</tr>\n'

    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Publications per Year (<em>P<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Publications (<em>P<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>New Rank (<em>i</em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(data)*'<td></td>')
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(data):
            if i + 1 == h:
                v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[0] += f'<td{ec}>{c}</td>'
            rows[1] += f'<td{ec}>{i+1}</td>'
            rows[2] += f'<td>{v}</td>'
        for i in range(h):
            data[i] = max(0, data[i]-h)
        data.sort(reverse=True)

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows) + '</table>\n'
    outstr += '</table>'
    yp_emp = metric_set.metrics["Year-based EMp-index by publications"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. The Year-based '
               f'<em>EM</em>&prime;-index by publications is the square-root of this sum, thus '
               f'<em>Yp_EM</em>&prime;{NBEQ}{yp_emp:0.4f}.</p>')
    return outstr


def metric_year_based_emp_pub() -> Metric:
    m = Metric()
    m.name = "Year-based EMp-index by publications"
    m.full_name = "Year-based EM\'-index by publications"
    m.html_name = "Year-based <em>EM</em>&prime;-index by publications"
    m.symbol = "<em>Yp_EM</em>&prime;"
    m.axis_name = r"$Yp\_EM^\prime$"
    m.synonyms = ["<em>Yp_EM</em>&prime;"]
    m.example = write_year_based_emp_pub_example
    m.metric_type = FLOAT
    m.description = ('<p>The Year-based <em>EM</em>&prime;-index by publications (Bihari and S. Tripathi 2018) is an '
                     'adapation of the __Year-based EM-index by publications__ which includes all years '
                     'rather than just those in the initial core. It is calculated just like the Year-based '
                     '<em>EM</em>&prime;-index by publications, except with a __EMp-index__ style modification.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2018) Year based EM-index: A new approach to evaluate the "
                    "scientific impact of scholars. <em>Scientometrics</em> 114:1175&ndash;1205."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_year_based_emp_pub
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Time"] = True
    return m


# year-based EM'-index by publication year citations (Bihari and Tripathi 2018)
def calculate_year_based_emp_pycites(metric_set: MetricSet) -> float:
    pub_years = metric_set.publication_years()
    cites = metric_set.citations
    return Impact_Funcs.calculate_year_based_emp_pycites(pub_years, cites)


def write_year_based_emp_pycites_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by number of citations, from highest to lowest. After each step, '
              '<em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'years. The yearly data is then resorted from high to low for each subsequent step.</p>')
    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    cites = metric_set.citations
    year_cnts = {y: 0 for y in range(miny, maxy+1)}
    for i, c in enumerate(cites):
        year_cnts[pub_years[i]] += c
    data = [year_cnts[y] for y in year_cnts]
    data.sort(reverse=True)

    ydata = [[year_cnts[y], y] for y in range(miny, maxy + 1)]
    ydata.sort(reverse=True)

    # calculate vector
    em_components = Impact_Funcs.calculate_emp_components(data)

    outstr += '<table class="example_table">\n'
    outstr += '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    for x in ydata:
        outstr += f'<td>{x[1]}</td>'
    outstr += '</tr>\n'

    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations from Publication Year (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>New Rank (<em>i</em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(data)*'<td></td>')
        rows[2] = "<tr><th></th>"
        for i, c in enumerate(data):
            if i + 1 == h:
                v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[0] += f'<td{ec}>{c}</td>'
            rows[1] += f'<td{ec}>{i+1}</td>'
            rows[2] += f'<td>{v}</td>'

        for i in range(h):
            data[i] = max(0, data[i]-h)
        data.sort(reverse=True)

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)

    outstr += '</table>'
    yp_em = metric_set.metrics["Year-based EMp-index by publication year citations"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. The year-based '
               f'<em>EM</em>&prime;-index by publication year citations is the square-root of this sum, thus '
               f'<em>Ypc_EM</em>&prime;{NBEQ}{yp_em:0.4f}.</p>')
    return outstr


def metric_year_based_emp_pycites() -> Metric:
    m = Metric()
    m.name = "Year-based EMp-index by publication year citations"
    m.full_name = "Year-based EM\'-index by publication year citations"
    m.symbol = "<em>Ypc_EM</em>&prime;"
    m.axis_name = r"$Ypc\_EM^\prime$"
    m.synonyms = ["<em>Ypc_EM</em>&prime;"]
    m.example = write_year_based_emp_pycites_example
    m.metric_type = FLOAT
    m.description = ('<p>The Year-based <em>EM</em>&prime;-index by publication year citations '
                     '(Bihari and S. Tripathi 2018) is an adapation of the __Year-based EM-index by '
                     'publication year citations__ which includes all years '
                     'rather than just those in the initial core. It is calculated just like the Year-based '
                     '<em>EM</em>&prime;-index by publication year citations, except with a __EMp-index__ '
                     'style modification.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2018) Year based EM-index: A new approach to evaluate the "
                    "scientific impact of scholars. <em>Scientometrics</em> 114:1175&ndash;1205."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_year_based_emp_pycites
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    return m


# year-based EM'-index by citations (Bihari and Tripathi 2018)
def calculate_year_based_emp_cites(metric_set: MetricSet) -> float:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_list[:metric_pos + 1]]
    return Impact_Funcs.calculate_year_based_emp_cites(total_cite_list)


def write_year_based_emp_cites_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Years are ordered by number of citations received that year, from highest to lowest. After each '
              'step, <em>E<sub>i</sub></em> is subtracted from the citations of the top <em>E<sub>i</sub></em> '
              'years. The yearly data is then resorted from high to low for each subsequent step.</p>')

    pub_years = metric_set.publication_years()
    miny = min(pub_years)
    maxy = max(pub_years)
    metric_pos = metric_set.parent_list.index(metric_set)
    total_cite_list = [m.metrics["total cites"].value for m in metric_set.parent_list[:metric_pos + 1]]
    total_cites_per_year = Impact_Funcs.total_citations_each_year(total_cite_list)
    data = [d for d in total_cites_per_year]
    data.sort(reverse=True)

    tmpy = [y for y in range(miny, maxy + 1)]
    ydata = [[total_cites_per_year[y], tmpy[y]] for y in range(len(tmpy))]
    ydata.sort(reverse=True)

    # calculate vector
    em_components = Impact_Funcs.calculate_emp_components(data)

    outstr += '<table class="example_table">\n'
    outstr += '<tr><th>Year (<em>y<sub>i</sub></em>)</th>'
    for x in ydata:
        outstr += f'<td>{x[1]}</td>'
    outstr += '</tr>\n'

    for j, h in enumerate(em_components):
        rows = ["" for _ in range(3)]
        if j == 0:
            rows[0] = '<tr class="top_row"><th>Citations received in year (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
        else:
            rows[0] = '<tr class="top_row"><th>Adjusted Citations (<em>C<sub>i</sub></em>)</th>'
            rows[1] = '<tr><th>New Rank (<em>i</em>)</th>'
        if j + 1 != len(em_components):
            rows.append('<tr class="spacer_row"><th></th>' + len(data)*'<td></td>')
        rows[2] = '<tr><th></th>'
        for i, c in enumerate(data):
            if i + 1 == h:
                v = f'<em>E</em><sub>{j+1}</sub>{NBEQ}{h}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[0] += f'<td{ec}>{c}</td>'
            rows[1] += f'<td{ec}>{i+1}</td>'
            rows[2] += f'<td>{v}</td>'
        for i in range(h):
            data[i] = max(0, data[i] - h)
        data.sort(reverse=True)

        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)

    outstr += '</table>'
    yp_em = metric_set.metrics["Year-based EMp-index by citations"].value
    outstr += (f'<p>The sum of the {len(em_components)} <em>E</em> values is {sum(em_components)}. The Year-based '
               f'<em>EM</em>&prime;-index by citations is the square-root of this sum, thus '
               f'<em>Yc_EM</em>&prime;{NBEQ}{yp_em:0.4f}.</p>')
    return outstr


def metric_year_based_emp_cites() -> Metric:
    m = Metric()
    m.name = "Year-based EMp-index by citations"
    m.full_name = "Year-based EM\'-index by citations"
    m.html_name = "Year-based <em>EM</em>&prime;-index by citations"
    m.symbol = "<em>Yc_EM</em>&prime;"
    m.axis_name = r"$Yc\_EM^\prime$"
    m.synonyms = ["<em>Yc_EM</em>&prime;"]
    m.example = write_year_based_emp_cites_example
    m.metric_type = FLOAT
    m.description = ('<p>The Year-based <em>EM</em>&prime;-index by citations (Bihari and S. Tripathi 2018) is an '
                     'adapation of the __Year-based EM-index by citations__ which includes all years '
                     'rather than just those in the initial core. It is calculated just like the Year-based '
                     '<em>EM</em>&prime;-index by citations, except with a __EMp-index__ '
                     'style modification.</p>')
    m.references = ["Bihari, A., and S. Tripathi (2018) Year based EM-index: A new approach to evaluate the "
                    "scientific impact of scholars. <em>Scientometrics</em> 114:1175&ndash;1205."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_year_based_emp_cites
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    return m


# h'-index (Zhang 2013)
def calculate_h_prime_index(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    core_cites = metric_set.metrics["h-core cites"].value
    h = metric_set.metrics["h-index"].value
    e = metric_set.metrics["e-index"].value
    return Impact_Funcs.calculate_h_prime(h, e, total_cites, core_cites)


# def write_h_prime_index_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["h_prime-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Tail', 'Center', 'Upper'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(1, maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x < h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         elif x == h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         else:
#             outstr += ", {}, null, null".format(tmp_cites[x - 1])
#         outstr += "],\n"
#         output.append(outstr)
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     isStacked: true,\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "ColumnChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def metric_h_prime_index() -> Metric:
    m = Metric()
    m.name = "h_prime-index"
    m.full_name = "h&prime;-index"
    m.html_name = "<em>h&prime;-</em>index"
    m.symbol = "<em>h&prime;</em>"
    m.axis_name = r"$h^\prime$"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "h_prime_index_desc"
    graph.data = create_upper_center_tail_citation_graph_data
    equation = r"$$h^\prime=\frac{eh}{t}.$$"
    m.description = ('<p>The <em>h&prime;-</em>index (Zhang 2013) is a variant of the __h-index__, where '
                     '<em>h</em> is scaled by the ratio of excess and tail citations relative to the core. '
                     f'It is measured as:</p>{equation}<p>where <em>e</em> '
                     'is the __e-index__ (the square root of the count of citations in the '
                     'core above and beyond what is necessary to produce <em>h</em>) and <em>t</em> is the '
                     'square root of all citations for publications in the tail (<em>i.e.</em>, not in the core). '
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Zhang, C.-T. (2013) The <em>h’</em> Index, effectively improving the <em>h</em>-Index based on "
                    "the citation distribution. <em>PLoS ONE</em> 8(4):e59912."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h_prime_index
    m.properties["Core Property"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Core Citations"] = True
    m.properties["Tail Citations"] = True
    return m


# hc (Khuarana and Sharma 2022)
def calculate_hc(metric_set: MetricSet) -> int:
    h = metric_set.metrics["h-index"].value
    m = metric_set.metrics["max cites"].value
    return Impact_Funcs.calculate_hc(h, m)


def metric_hc() -> Metric:
    m = Metric()
    m.name = "hc"
    m.full_name = "hc"
    m.html_name = "<em>h<sub>c</sub></em>"
    m.symbol = "<em>h<sub>c</sub></em>"
    m.axis_name = r"$h_c$"
    m.metric_type = INT
    equation = r"$$k = \left[\log_h\left(C_{\max}-1 \right)\right],$$"
    equation2 = r"$$h_c = h+k.$$"
    m.description = ('<p><em>h<sub>c</sub></em> (Kharana and Sharma 2022) is a modification of the __h-index__ '
                     'which includes an additional weighting '
                     'factor for the most cited publication of the author\'s record. This extra factor is the maximum '
                     'power one can raise <em>h</em> to which is less than the __max cites__, which is then added to '
                     f'<em>h</em>, thus:</p>{equation2}<p>The original authors describe the calculation of <em>k</em> '
                     'through an algorithm, but as long as <em>h</em> &gt; 1 it can directly be determined '
                     f'as:</p>{equation}<p>which is the logarithm in base <em>h</em> of one '
                     'less than the largest number of citations to a single paper, truncated to an integer. If '
                     '<em>h</em> &le; 1, then <em>h<sub>c</sub></em> = 2 if the maximum citations is '
                     'greater than one, otherwise <em>h<sub>c</sub></em> = <em>h</em>.')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hc
    m.properties["Core Property"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.references = ["Khurana, P., and K. Sharma (2022) Impact of <em>h‑</em>index on author’s rankings: An "
                    "improvement to the <em>h‑</em>index for lower‑ranked authors. <em>Scientometrics</em> "
                    "127:4483&ndash;4498."]
    return m


# k-index (Anania and Caruso 2013)
def calculate_k_index_anania_caruso(metric_set: MetricSet) -> float:
    core_cites = metric_set.metrics["h-core cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_k_index_anania_caruso(h, core_cites)


# def write_k_index_anania_caruso_desc_data(metric_set: MetricSet) -> list:
#     metric = metric_set.metrics["Anania and Caruso k-index"]
#     graph = metric.description_graphs[0]
#     output = list()
#     output.append("        var data_{} = google.visualization.arrayToDataTable([\n".format(graph.name))
#     output.append("           ['Rank', 'Tail', 'Center', 'Upper'],\n")
#     tmp_cites = [c for c in metric_set.citations]
#     tmp_cites.sort(reverse=True)
#     h = metric_set.metrics["h-index"].value
#     maxx = metric_set.metrics["total pubs"].value
#     maxv = 50
#     for x in range(1, maxx + 1):
#         outstr = "           [{}".format(x)  # write rank
#         if x < h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         elif x == h:
#             outstr += ", null, {}, {}".format(h, tmp_cites[x - 1] - h)
#         else:
#             outstr += ", {}, null, null".format(tmp_cites[x - 1])
#         outstr += "],\n"
#         output.append(outstr)
#
#     output.append("		]);\n")
#     output.append("\n")
#     output.append("        var options_{} = {{\n".format(graph.name))
#     output.append("		     legend: {position: 'top'},\n")
#     output.append("		     isStacked: true,\n")
#     output.append("		     interpolateNulls: true,\n")
#     output.append("		     hAxis: {slantedText: true,\n")
#     output.append("		             title: \'Rank\',\n")
#     output.append("		             gridlines: {color: \'transparent\'},\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             viewWindow: {max:" + str(maxv) + "}},\n")
#     output.append("		     vAxis: {viewWindow: {max:" + str(maxv) + "},\n")
#     output.append("		             title: \'Citation Count\',\n")
#     output.append("		             ticks: [0, 10, 20, 30, 40, 50],\n")
#     output.append("		             gridlines: {color: \'transparent\'}},\n")
#     output.append("        };\n")
#     output.append("\n")
#     output.append("        var chart_{} = new google.visualization."
#                   "ColumnChart(document.getElementById('chart_{}_div'));\n".format(graph.name, graph.name))
#     output.append("        chart_{}.draw(data_{}, options_{});\n".format(graph.name, graph.name, graph.name))
#     output.append("\n")
#
#     return output


def metric_k_index_anania_caruso() -> Metric:
    m = Metric()
    m.name = "Anania and Caruso k-index"
    m.full_name = "k-index (Anania and Caruso)"
    m.html_name = "<em>k-</em>index (Anania and Caruso)"
    m.symbol = "<em>k</em>"
    m.axis_name = r"$k$"
    m.metric_type = FLOAT
    graph = DescriptionGraph()
    m.description_graphs.append(graph)
    graph.name = "k_index_anania_caruso_desc"
    graph.data = create_upper_center_tail_citation_graph_data
    equation = r"$$k=h+\left(1-\frac{h^2}{C^H}\right)=h+\frac{e^2}{C^H}=h+\frac{e^2}{h^2 + e^2}.$$"
    m.description = ('<p>The <em>k-</em>index (Anania and Caruso 2013) is a variant of the __h-index__, where '
                     '<em>h</em> includes a fractional component representing the proportion of the __h-core cites__ '
                     '(<em>C<sup>H</sup></em>) which are above and beyond those necessary to achieve <em>h</em>, '
                     'making <em>k</em> essentially a function of <em>h</em> and the __e-index__. '
                     f'It can be calculated as:</p>{equation}<p><em>k</em> will always be between <em>h</em> and '
                     '<em>h</em>+1. The authors also described a very similar metric known as the '
                     '__Anania and Caruso w-index__; <em>w</em> will always be equal to or greater than <em>k</em>.'
                     f'<figure class="desc_fig"><img class="impact_fig" src="impact_figs/img_{graph.name}.svg" '
                     f'/></figure>')
    m.references = ["Anania, G., and A. Caruso (2013) Two simple new bibliometric indexes to better evaluate "
                    "research in disciplines where publications typically receive less citations. "
                    "<em>Scientometrics</em> 96:617&ndash;631."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_k_index_anania_caruso
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# w-index (Anania and Caruso 2013)
def calculate_w_index_anania_caruso(metric_set: MetricSet) -> float:
    total_cites = metric_set.metrics["total cites"].value
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_w_index_anania_caruso(h, total_cites)


def metric_w_index_anania_caruso() -> Metric:
    m = Metric()
    m.name = "Anania and Caruso w-index"
    m.full_name = "w-index (Anania and Caruso)"
    m.html_name = "<em>w-</em>index (Anania and Caruso)"
    m.symbol = "<em>w</em>"
    m.axis_name = r"$w$"
    m.metric_type = FLOAT
    equation = r"$$w=h+\left(1-\frac{h^2}{C_T}\right).$$"
    m.description = ('<p>The <em>w-</em>index (Anania and Caruso 2013) is a variant of the __h-index__, where '
                     '<em>h</em> includes a fractional component representing the proportion of the __total cites__ '
                     '(<em>C<sub>T</sub></em>) which are above and beyond those necessary to achieve <em>h</em>. '
                     f'It can be calculated as:</p>{equation}<p><em>w</em> will always be between <em>h</em> and '
                     '<em>h</em>+1. The authors also described a very similar metric known as the '
                     '__Anania and Caruso k-index__; <em>w</em> will always be equal to or greater than <em>k</em>.')
    m.references = ["Anania, G., and A. Caruso (2013) Two simple new bibliometric indexes to better evaluate "
                    "research in disciplines where publications typically receive less citations. "
                    "<em>Scientometrics</em> 96:617&ndash;631."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_w_index_anania_caruso
    m.properties["Core Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["All Citations"] = True
    return m


# h-norm index (Anania and Caruso 2013)
def calculate_h_norm(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_h_norm(citations, n_authors)


def write_h_norm_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by adjusted number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    data = []
    for i in range(len(metric_set.citations)):
        c = metric_set.citations[i]
        a = metric_set.author_counts()[i]
        data.append([c/a, c, a])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    cstari = r"\(C^*_i\)"
    rows[2] = f'<tr class="top_row"><th>Adjusted Citations ({cstari})</th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr><th></th>'
    hn = metric_set.metrics["h-norm"].value
    for i, d in enumerate(data):
        cs = d[0]
        c = d[1]
        a = d[2]
        if i + 1 == hn:
            v = f'<em>h-norm</em>{NBEQ}{hn}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{a}</td>'
        rows[2] += f'<td{ec}>{cs:1.2f}</td>'
        rows[3] += f'<td{ec}>{i+1}</td>'
        rows[4] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    eq = r"\(i \leq C^*_i\)"
    outstr += f'<p>The largest rank where {eq} is {hn}.</p>'
    return outstr


def metric_h_norm() -> Metric:
    m = Metric()
    m.name = "h-norm"
    m.full_name = "h-norm"
    m.html_name = "<em>h-norm</em> index"
    m.symbol = "<em>h-norm</em>"
    m.axis_name = r"$h\text{-norm}$"
    m.example = write_h_norm_example
    m.metric_type = INT
    ceq = r"$$C^{*}_i = \frac{C_i}{A_i}.$$"
    hnormeq = r"$$h{-}norm = \underset{i}{\max}\left(i \leq C^{*}_i\right).$$"
    m.description = ('<p>The <em>h-norm</em> index (Anania and Caruso 2013) is described more or less incidentally '
                     'when building up to normalized versions of other metrics in the paper. It is a version of the '
                     '__h-index__ normalized by the number of coauthors for each publication. It is very similar to '
                     'the calculation of <em>h<sub>e</sub></em> when determining the __adapt pure h-index frac__, '
                     'but citation counts are divided by the number of coauthors rather than the square root. '
                     f'Citation counts are adjusted for coauthor counts as:</p>{ceq}<p>and <em>h-norm</em> is '
                     f'determined using these adjusted counts:</p>{hnormeq}')
    m.references = ["Anania, G., and A. Caruso (2013) Two simple new bibliometric indexes to better evaluate "
                    "research in disciplines where publications typically receive less citations. "
                    "<em>Scientometrics</em> 96:617&ndash;631."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_h_norm
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Coauthorship"] = True
    return m


# k-norm index (Anania and Caruso 2013)
def calculate_k_norm_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_k_norm_index(citations, n_authors)


def metric_k_norm_index() -> Metric:
    m = Metric()
    m.name = "k-norm index"
    m.full_name = "k-norm index"
    m.html_name = "<em>k-norm</em> index"
    m.symbol = "<em>k-norm</em>"
    m.axis_name = r"$k\text{-norm}$"
    m.metric_type = FLOAT
    ceq = r"$$C^{*}_i = \frac{C_i}{A_i}.$$"
    equation = r"$$k{-}norm=h{-}norm+\left(1-\frac{{h{-}norm}^2}{\sum\limits_{i=1}^{h{-}norm} C^{*}_i}\right).$$"
    m.description = ('<p>The <em>k-norm</em> index (Anania and Caruso 2013) is a variant of the '
                     '__Anania and Caruso k-index__, where citation counts are first normalized by dividing by the '
                     f'number of coauthors for each publication:</p>{ceq}<p>These are used to calculate a normalized '
                     f'version of <em>h</em> (__h-norm__), and then <em>k-norm</em> is determined as:{equation}')
    m.references = ["Anania, G., and A. Caruso (2013) Two simple new bibliometric indexes to better evaluate "
                    "research in disciplines where publications typically receive less citations. "
                    "<em>Scientometrics</em> 96:617&ndash;631."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_k_norm_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Coauthorship"] = True
    return m


# w-norm index (Anania and Caruso 2013)
def calculate_w_norm_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    n_authors = metric_set.author_counts()
    return Impact_Funcs.calculate_w_norm_index(citations, n_authors)


def metric_w_norm_index() -> Metric:
    m = Metric()
    m.name = "w-norm index"
    m.full_name = "w-norm index"
    m.html_name = "<em>w-norm</em> index"
    m.symbol = "<em>w-norm</em>"
    m.axis_name = r"$w\text{-norm}$"
    m.metric_type = FLOAT
    ceq = r"$$C^{*}_i = \frac{C_i}{A_i}.$$"
    equation = r"$$w{-}norm=h{-}norm+\left(1-\frac{{h{-}norm}^2}{\sum\limits_{i=1}^{P} C^{*}_i}\right).$$"
    m.description = ('<p>The <em>w-norm</em> index (Anania and Caruso 2013) is a variant of the '
                     '__Anania and Caruso w-index__, where citation counts are first normalized by dividing by the '
                     f'number of coauthors for each publication:</p>{ceq}<p>These are used to calculate a normalized '
                     f'version of <em>h</em> (__h-norm__), and then <em>w-norm</em> is determined as:{equation}')
    m.references = ["Anania, G., and A. Caruso (2013) Two simple new bibliometric indexes to better evaluate "
                    "research in disciplines where publications typically receive less citations. "
                    "<em>Scientometrics</em> 96:617&ndash;631."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_w_norm_index
    m.properties["Core Metric"] = True
    m.properties["All Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["All Citations"] = True
    m.properties["Coauthorship"] = True
    return m


# yearly h-index (Singh 2022)
def calculate_yearly_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    return Impact_Funcs.calculate_yearly_h_index(citations, pub_years)


def write_yearly_h_index_example(metric_set: MetricSet) -> str:
    outstr = ('<p>Publications are ordered by number of citations, from highest to lowest, for each year '
              'independently.</p>')
    outstr += '<table class="example_table">\n'

    pub_years = metric_set.publication_years()
    min_year = min(pub_years)
    max_year = max(pub_years)
    nyears = max_year - min_year + 1
    for y in range(min_year, max_year + 1):
        # create citation list for pubs in one year only
        citations = []
        for i, c in enumerate(metric_set.citations):
            if pub_years[i] == y:
                citations.append(c)
        citations.sort(reverse=True)
        tmp_h = Impact_Funcs.get_rank_value(citations)

        rows = ["" for _ in range(4)]
        rows[0] = f'<tr class="top_row"><th>{y}</th>'
        rows[1] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
        rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[3] = '<tr><th></th>'
        for i, c in enumerate(citations):
            if i + 1 == tmp_h:
                v = f'<em>h</em><sub>{y}</sub>{NBEQ}{tmp_h}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[1] += f'<td{ec}>{c}</td>'
            rows[2] += f'<td{ec}>{i+1}</td>'
            rows[3] += f'<td>{v}</td>'
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>\n'
    yh = metric_set.metrics["yearly h-index"].value
    outstr += (f'<p>The yearly <em>h-</em>index is the average of the {nyears} <em>h-</em>indices calculated '
               f'independently for publications released each year, or {yh:0.4f}.</p>')
    return outstr


def metric_yearly_h_index() -> Metric:
    m = Metric()
    m.name = "yearly h-index"
    m.full_name = "yearly h-index"
    m.html_name = "yearly <em>h-</em>index"
    m.symbol = r"\(\bar{h}_y\)"
    m.axis_name = r"$\bar{h}_y$"
    m.metric_type = FLOAT
    equation = r"$$\bar{h}_y = \frac{\sum\limits_{i=Y_0}^{Y}h_i}{\text{academic age}},$$"
    m.description = ('<p>The yearly <em>h-</em>index (Singh 2022) is described more or less incidentally '
                     'when building up to another metric in the paper. It is simply the average __h-index__ '
                     'for a researcher based on calculations of <em>h</em> from sets of papers published from each '
                     'individual year of their career, rather than a single <em>h</em> determined for the entire '
                     f'career. It is calculated as:</p>{equation}<p>where <em>h<sub>i</sub></em> is simply an '
                     '<em>h-</em>index calculated only for papers from year <em>i</em>. Regardless of citation '
                     'counts, the yearly <em>h-</em>index will always be limited by the total number of papers '
                     'published per year, thus highly cited papers and poorly cited papers will frequently '
                     'contribute about equal weight in any given year. It serves more as a general measure of '
                     'consistency and&mdash;assuming most papers get at least a few citations&mdash;is little '
                     'different than the average number of papers published per year, at least for most '
                     'individuals.')
    m.references = ["Singh, P.K. (2022) <em>t-</em>index: Entropy based random document and citation analysis "
                    "using average <em>h-index</em>. <em>Scientometrics</em> 127:637&ndash;660."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_yearly_h_index
    m.example = write_yearly_h_index_example
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Time"] = True
    return m


# t-index (Singh 2022)
def calculate_t_index_singh(metric_set: MetricSet) -> float:
    year_h = metric_set.metrics["yearly h-index"].value
    age = metric_set.academic_age()
    citations = metric_set.citations
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_t_index_singh(citations, year_h, age, total_cites)


def metric_t_index_singh() -> Metric:
    m = Metric()
    m.name = "Singh t-index"
    m.full_name = "t-index (Singh)"
    m.html_name = "<em>t-</em>index (Singh)"
    m.symbol = "<em>t</em>"
    m.axis_name = r"$t$"
    m.metric_type = FLOAT
    equation = r"$$t=4e^{T/T^\prime}\bar{h}_y,$$"
    teq1 = r"$$T = \sum\limits_{i=1}^{P}\frac{c_i}{C^P}\ln\frac{c_i}{C^P}$$"
    teq2 = r"$$T^\prime=\ln \left(10 \times  \text{academic age} \right).$$"
    m.description = ('<p>The <em>t-</em>index (Singh 2022) is an alternative metric for impact based on the '
                     'information entropy of individual publications, with scaling factors based on academic age '
                     f'and the __yearly h-index__. It is calculated as:</p>{equation}<p>where</p>{teq1}<p>and</p>'
                     f'{teq2}<p>It is a bit difficult to interpret and is not guaranteed to monotonically '
                     'increase.')
    m.references = ["Singh, P.K. (2022) <em>t-</em>index: Entropy based random document and citation analysis "
                    "using average <em>h-index</em>. <em>Scientometrics</em> 127:637&ndash;660."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_t_index_singh
    m.properties["Alternative Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    m.properties["Time"] = True
    return m


# fairness
def calculate_fairness(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_fairness(total_cites, total_pubs, citations)


def metric_fairness() -> Metric:
    m = Metric()
    m.name = "fairness"
    m.full_name = "fairness"
    m.symbol = "<em>η</em>"
    m.metric_type = FLOAT
    m.synonyms = ["<em>η</em>"]

    equation = r"$$\eta = \frac{\left(C^P\right)^2}{P\sum\limits_{i=1}^{P} C_i^2}.$$"

    m.description = ('<p>Fairness (Prathap 2014; Gagolewski <em> et al.</em> 2022) is a measure of the '
                     'distribution of citations across all of an author\'s publications. A value of 1 would indicate '
                     'that all publications have the same number of citations, while lower values indicate a skewed '
                     'distribution with some publications having more citations than other. It is calculated as:'
                     f'</p>{equation}<p>It is not generally considered as an impact measure in-and-of itself, but '
                     'serves as a complement to other metrics.')

    m.references = ["Prathap, G. (2014) The Zynergy-Index and the formula for the h-Index. <em>Journal of the "
                    "Association for Information Science and Technology</em> 65(2):426&ndash;427.",
                    "Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Fairness in the three‑dimensional"
                    " model for citation impact. <em>Scientometrics</em> 127:6055&ndash;6059."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_fairness
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# Zynergy (Prathap 2014)
def calculate_zynergy(metric_set: MetricSet) -> float:
    f = metric_set.metrics["fairness"].value
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_zynergy(total_cites, total_pubs, f)


def metric_zynergy() -> Metric:
    m = Metric()
    m.name = "zynergy index"
    m.full_name = "Zynergy-Index"
    m.symbol = "<em>z</em>"
    m.axis_name = r"$z$"
    m.metric_type = FLOAT
    m.synonyms = ["<em>z</em>"]
    equation = r"$$z = \sqrt[3]{\frac{\eta \left(C^P\right)^2}{P}}$$"
    m.description = ('<p>The Zynergy-Index (Prathap 2014) is a heuristic alternative to the __h-index__ based on '
                     'a thermodynamical model. It is a function of the total number of citations and publications '
                     'of an author, along with the distribution of the citations across the publications as measured '
                     f'by __fairness__ (<em>η</em>).</p>{equation}.')

    m.references = ["Prathap, G. (2014) The Zynergy-Index and the formula for the h-Index. <em>Journal of the "
                    "Association for Information Science and Technology</em> 65(2):426&ndash;427."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_zynergy
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# p20 (Gagolewski et al. 2022)
def calculate_p20(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_p20(citations, total_cites, total_pubs)


def metric_p20() -> Metric:
    m = Metric()
    m.name = "p20"
    m.full_name = "p20"
    m.html_name = "<em>p</em><sub>20</sub>"
    m.symbol = "<em>p</em><sub>20</sub>"
    m.axis_name = r"$p_{20}$"
    m.metric_type = FLOAT
    m.description = ('<p>Gagolewski <em>et al.</em> (2022) suggested a variety of metrics that might be used to '
                     'approximate the distribution of an author\'s citation vector, some of which were novel in '
                     'a bibliometric context. <em>p</em><sub>20</sub> (which stems from economics) is the proportion '
                     'of the total citations that occur in the top 20% of an author\'s publications. One could view '
                     'it as the proportion of citations within the core, if the core were fixed as the top 20% '
                     'of publications rather than defined in a manner more similar to the __h-index__.')

    m.references = ["Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Ockham's index of citation "
                    "impact. <em>Scientometrics</em> 127:2829&ndash;2845."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_p20
    m.properties["Alternative Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# rmp (Gagolewski et al. 2022)
def calculate_rmp(metric_set: MetricSet) -> float:
    mp = metric_set.metrics["rec-index"].value  # rec-index is equal to maxprod
    return Impact_Funcs.calculate_rmp(mp)


def metric_rmp() -> Metric:
    m = Metric()
    m.name = "rmp-index"
    m.full_name = "rmp-index"
    m.html_name = "<em>rmp</em>-index"
    m.symbol = "<em>rmp</em>"
    m.axis_name = r"$rmp$"
    m.metric_type = FLOAT
    m.description = ('<p>Gagolewski <em>et al.</em> (2022) suggested a variety of metrics that might be used to '
                     'approximate the distribution of an author\'s citation vector, some of which were novel in '
                     'a bibliometric context. The <em>rmp</em>-index is simply the square-root of the maxprod-index, '
                     'a.k.a., the __rec-index__.')

    m.references = ["Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Ockham's index of citation "
                    "impact. <em>Scientometrics</em> 127:2829&ndash;2845."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_rmp
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# css (Gagolewski et al. 2022)
def calculate_css(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_css(citations)


def metric_css() -> Metric:
    m = Metric()
    m.name = "css"
    m.full_name = "css"
    m.html_name = "<em>css</em>"
    m.symbol = "<em>css</em>"
    m.axis_name = r"$css$"
    m.metric_type = FLOAT
    equation = r"$$css = \sqrt[3]{\sum\limits_{i=1}^P C_i^2}$$"
    m.description = ('<p>Gagolewski <em>et al.</em> (2022) suggested a variety of metrics that might be used to '
                     'approximate the distribution of an author\'s citation vector, some of which were novel in '
                     'a bibliometric context. <em>css</em> is the cube-root of the sum of squared citation '
                     f'counts.</p>{equation}')

    m.references = ["Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Ockham's index of citation "
                    "impact. <em>Scientometrics</em> 127:2829&ndash;2845."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_css
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# csr (Gagolewski et al. 2022)
def calculate_csr(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_csr(citations)


def metric_csr() -> Metric:
    m = Metric()
    m.name = "csr"
    m.full_name = "csr"
    m.html_name = "<em>csr</em>"
    m.symbol = "<em>csr</em>"
    m.axis_name = r"$csr$"
    m.metric_type = FLOAT
    equation = r"$$csr = \sqrt[3]{2\sum\limits_{i=1}^P \left(i-0.5\right)C_i}$$"
    m.description = ('<p>Gagolewski <em>et al.</em> (2022) suggested a variety of metrics that might be used to '
                     'approximate the distribution of an author\'s citation vector, some of which were novel in '
                     'a bibliometric context. <em>csr</em> is the cube-root of the sum of ranks, a function of '
                     f'the average rank of the counts in the citation vector.</p>{equation}')

    m.references = ["Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Ockham's index of citation "
                    "impact. <em>Scientometrics</em> 127:2829&ndash;2845."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_csr
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# slg (Gagolewski et al. 2022)
def calculate_slg(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    return Impact_Funcs.calculate_slg(citations)


def metric_slg() -> Metric:
    m = Metric()
    m.name = "slg"
    m.full_name = "slg"
    m.html_name = "<em>slg</em>"
    m.symbol = "<em>slg</em>"
    m.axis_name = r"$slg$"
    m.metric_type = FLOAT
    equation = r"$$slg= \sum\limits_{i=1}^P \log\left(C_i + 1\right)$$"
    m.description = ('<p>Gagolewski <em>et al.</em> (2022) suggested a variety of metrics that might be used to '
                     'approximate the distribution of an author\'s citation vector, some of which were novel in '
                     'a bibliometric context. <em>slg</em> is the sum of the logarithms of the citation counts '
                     f'(plus one), which is an estimator often used for Pareto distributions.</p>{equation}')

    m.references = ["Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Ockham's index of citation "
                    "impact. <em>Scientometrics</em> 127:2829&ndash;2845."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_slg
    m.properties["Alternative Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# 3DSI (pr) (Siudem et al. 2020, Gagolewsi et al. 2022)
def calculate_3dsi_pr(metric_set: MetricSet) -> list:
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    csr = metric_set.metrics["csr"].value
    return Impact_Funcs.calculate_3dsi_pr(total_pubs, total_cites, csr)


def metric_3dsi_pr() -> Metric:
    m = Metric()
    m.name = "3DSI (pr)"
    m.full_name = "3DSI (pr)"
    m.html_name = "3DSI (ρ<sub>R</sub>)"
    m.metric_type = LIST
    m.list_formats = [INT, INT, FLOAT]
    m.symbol = "[<em>P</em>, <em>C<sup>P</sup></em>, ρ<sub>R</sub>]"

    equation = r"$$\rho_R = \frac{P-\frac{2csr^3}{C^P}+1}{P-\frac{csr^3}{C^P}},$$"
    m.description = ('<p>Siudem <em>et al.</em> (2020) describe a three-dimensional model to measure scientific '
                     'impact of an author, generally called 3DSI. The first dimension is simply the total number '
                     'of publications, and the second is the total number of citations. The third dimension is '
                     'for a parameter <em>ρ</em> which generally describes the distribution of citations within the '
                     'publications based on a preferential attachment rule (strictly speaking <em>ρ</em> is the ratio '
                     'of preferential citations to total citations). Roughly speaking, positive values of '
                     '<em>ρ</em> (approximately one or greater) indicate that most citations are preferentially '
                     'going to a limited number of publications, values around zero indicate '
                     'approximately a random citation distribution according to their model, and negative values '
                     'indicate citations are more evenly spread among publications.</p>'
                     '<p>While the first two dimensions are simple to '
                     'calculate, there are many methods for estimating <em>ρ<sub>R</sub></em> from empirical data.</p>'
                     '<p>In this version, we use a rank-size domain estimator, <em>ρ<sub>R</sub></em> '
                     f'(Gagolewski <em>et al.</em> 2022), determined as:</p>{equation}<p>where __csr__ is the '
                     'cube-root of the sum of ranks.')

    m.references = ["Siudem, G., B. Żogała‑Siudem, A. Cena, and M. Gagolewski (2020) Three dimensions of "
                    "scientific impact. <em>Proceedings of the National Academy of Sciences of the United States of"
                    " America</em> 117(25):13896&ndash;13900.",
                    "Gagolewski, M., B. Żogała‑Siudem, G. Siudem, and A. Cena (2022) Ockham's index of citation "
                    "impact. <em>Scientometrics</em> 127:2829&ndash;2845."]
    m.calculate = calculate_3dsi_pr
    m.draw_graph = Impact_Graphs.draw_graph_3d_scatter_chart
    m.properties["Alternative Metric"] = True
    m.properties["Multidimensional Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# total collaborators
def calculate_total_collaborators(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_total_collaborators(metric_set.coauthors())


def metric_total_collaborators() -> Metric:
    m = Metric()
    m.name = "total collaborators"
    m.full_name = "total collaborators"
    m.symbol = "collaborators"
    m.metric_type = INT
    m.description = ('<p>This is simply the total number of unique collaborators of an author. It is not an impact '
                     'factor in the traditional sense.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_collaborators
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# partnership ability index (Schubert 2012)
def calculate_partnership_ability(metric_set: MetricSet) -> int:
    return Impact_Funcs.calculate_partnership_ability(metric_set.coauthors())


def write_partnership_example(metric_set: MetricSet) -> str:
    coauthor_list = metric_set.coauthors()
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
    data = [[coauthor_cnts[c], c] for c in coauthor_cnts]
    data.sort(reverse=True)

    outstr = '<p>Coauthors are ordered by number of coauthored publications, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    rows = ["" for _ in range(4)]
    rows[0] = '<tr class="top_row"><th>Coauthor</th>'
    rows[1] = '<tr class="top_row"><th>Coauthored Publications</th>'
    rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[3] = '<tr><th></th>'
    phi = metric_set.metrics["partnership ability"].value
    for i, d in enumerate(data):
        if i + 1 == phi:
            v = f'<em>φ</em>{NBEQ}{phi}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>Coauthor&nbsp;{i+1}</td>'
        rows[1] += f'<td{ec}>{d[0]}</td>'
        rows[2] += f'<td{ec}>{i+1}</td>'
        rows[3] += f'<td>{v}</td>'
    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The largest rank which is greater than or equal to the corresponding number of coauthored '
               f'publications is {phi}.</p>')
    return outstr


def metric_partnership_ability() -> Metric:
    m = Metric()
    m.name = "partnership ability"
    m.full_name = "partnership ability"
    m.symbol = "<em>φ</em>"
    m.axis_name = r"$\phi$"
    m.synonyms = ["<em>φ</em>"]
    m.metric_type = INT
    m.example = write_partnership_example
    m.description = ('<p>The partnership ability index (Schubert 2012) is the collaborator equivalent of '
                     'the __h-index__. It is the '
                     'largest value for which <em>φ</em> coauthors of the target author have produced at least '
                     '<em>φ</em> publications with the target author.</p><p>A <em>φ</em> of zero would indicate the '
                     'target author has only produced solo-author publications. A <em>φ</em> of one indicates '
                     'at least one coauthor on one publication, but also at most one coauthor with whom they have '
                     'published more than once.</p><p><em>φ</em> is essentially a simple form of a collaboration '
                     'network metric.')
    m.references = ["Schubert, A. (2012) A Hirsch-type index of co-author partnership ability. "
                    "<em>Scientometrics</em> 91:303&ndash;308."]

    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_partnership_ability
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# stratified h-index (Wurtz and Schmidt 2016)
def calculate_stratified_h(metric_set: MetricSet) -> list:
    h = metric_set.metrics["h-index"].value
    author_pos = metric_set.author_position()
    author_cnts = metric_set.author_counts()
    citations = metric_set.citations
    return Impact_Funcs.calculate_stratified_h(h, author_pos, author_cnts, citations)


def metric_stratified_h() -> Metric:
    m = Metric()
    m.name = "stratified h-index"
    m.full_name = "stratified h-index"
    m.html_name = "stratified <em>h-</em>index"
    m.axis_name = r"$h$"
    m.symbol = ("[<em>h</em>, <em>h</em><sub>1</sub>, <em>h</em><sub>2</sub>, <em>h</em><sub>3</sub>, "
                "<em>h</em><sub>last</sub>]")
    m.metric_type = LIST
    m.list_formats = INT
    m.description = ('<p>The stratified <em>h-</em>index (Würtz and Schmidt 2016) attempts to deal with coauthorship '
                     'by producing a set of '
                     '<em>h-</em>indices based on differing authorship position wihin the publications. Essentially, '
                     'in addition to the general __h-index__, one calculates independent indices for publications '
                     'in which one is the first author, second author, third author, or last author, with these '
                     'four positions being deemed the highest contributing to a publication, in various degrees '
                     'of importance. In theory, by viewing this set of indices, rather than a single value, one can '
                     'determine how much of an author\'s impact is based on &ldquo;primary&rdquo; contributions to '
                     'publications versus secondary.</p><p>This concept is very similar to a few other proposals, '
                     'including the __hmaj-index__ and the __first-author h-index__.</p>')
    m.references = ["Würtz, M., and M. Schmidt (2016) The stratified H-index. <em>Annals of Epidemiology</em> "
                    "26(4):299&ndash;300."]

    m.calculate = calculate_stratified_h
    m.draw_graph = Impact_Graphs.draw_graph_five_line_chart
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Multidimensional Metric"] = True
    m.properties["Coauthorship"] = True
    return m


# platinum h-index (Smith 2015)
def calculate_platinum_h(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    total_cites = metric_set.metrics["total cites"].value
    total_pubs = metric_set.metrics["total pubs"].value
    age = metric_set.academic_age()
    return Impact_Funcs.calculate_platinum_h(h, total_cites, total_pubs, age)


def metric_platinum_h() -> Metric:
    m = Metric()
    m.name = "platinum h-index"
    m.full_name = "platinum h-index"
    m.html_name = "platinum <em>h-</em>index"
    m.symbol = "<em>h</em><sub>plat</sub>"
    m.metric_type = FLOAT
    equation = r"$$h_{plat}=\frac{hC^P}{\left(\text{academic age}\right)P}=\frac{hC^P}{\left({Y-Y_{0}+1}\right)P}.$$"
    m.description = ('<p>The platinum <em>h-</em>index (Smith 2015) is a compound metric that rescales the '
                     '__h-index__ based on the academic age of the researcher and the average number of '
                     f'citations per publication. It is simply calculated as:</p>{equation}')
    m.references = ["Smith, D.R. (2015) “Platinum H”: Refining the h-Index to more realistically assess career "
                    "trajectory and scientific publications. <em>Archives of Environmental & Occupational Health</em> "
                    "70(2):67&ndash;69."]

    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_platinum_h
    m.properties["Compound Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["All Citations"] = True
    m.properties["All Publications"] = True
    m.properties["Time"] = True
    return m


# stochastic h-index (Nair and Turlach 2012)
def calculate_stochastic_h(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    return Impact_Funcs.calculate_stochastic_h(h, citations, year, pub_years)


def metric_stochastic_h() -> Metric:
    m = Metric()
    m.name = "stochastic h-index"
    m.full_name = "stochastic h-index"
    m.html_name = "stochastic <em>h-</em>index"
    m.symbol = "<em>h<sub>s</sub></em>"
    m.axis_name = r"$h_s$"
    m.synonyms = ["<em>h<sub>s</sub></em>"]
    m.metric_type = FLOAT

    eq1 = r"$$\lambda_i=-ln\left(\frac{\text{age}_i+1}{\text{age}_i+2}\right).$$"
    eq2 = r"$$h_s=h + 1 - \sum\limits_{i=1}^k Q_i,$$"
    eq3 = (r"$$Q_0=\prod\limits_{i=1}^{n}q_i \\Q_1=\sum\limits_{i=1}^{n}\left(p_i\prod\limits_{j=1, "
           r"j\ne i}^{n}q_j\right) \\Q_2=\sum\limits_{i=1}^{n}\sum\limits_{j=i+1}^{n}\left(p_ip_j\prod\limits_{k=1, "
           r"k\ne i, k\ne j}^{n}q_k\right)\\\text{etc.}$$")

    m.description = (f"<p>The stochastic <em>h-</em>index (Naid and Turlach 2012) is a variant of the __h-index__ "
                     f"where h is modified to include a fractional component equal to the probability that it will "
                     f"increase by at least one by the next year. It is somewhat similar to the __rational h-index__ "
                     f"and the __real h-index__ in that its value ranges between <em>h</em> and <em>h</em>+1 and "
                     f"that the fractional component indicates something about progress toward the higher value.</p>"
                     f"<p>Although the logic behind this metric is not particularly difficult, the calculation "
                     f"is a bit complicated to explain. Publications can be "
                     f"divided into two sets: those already with <em>h</em>+1 or more citations (thus not needing any "
                     f"additional citations for the researcher to reach the next value of <em>h</em>) and those "
                     f"with <em>h</em> or fewer citations. The number of publications in each of these sets are "
                     f"labeled as <em>L</em><sub>0</sub> and <em>n</em>, respectively. "
                     f"The number of publications within the second set that will need to gain "
                     f"citations to reach <em>h</em>+1 is <em>k</em> = <em>h</em>&minus;<em>L</em><sub>0</sub></p>"
                     f"<p>The probability that one of the publications in the second set will get to <em>h</em>+1 "
                     f"citations is determined from a Poisson distribution with a mean equal to the average annual "
                     f"citation rate of that publication (<em>λ<sub>i</sub></em>) and the number of citations it "
                     f"needs to gain to reach "
                     f"<em>h</em>+1. The probability it will reach at least <em>h</em>+1 citations is labeled "
                     f"<em>p<sub>i</sub></em>, and the "
                     f"probability it will not reach at least <em>h</em>+1 citations is labeled "
                     f"<em>q<sub>i</sub></em> = "
                     f"1&minus;<em>p<sub>i</sub></em>.</p><p>If a publication has zero citations, its presumed rate "
                     f"of future citation is based on the age of the publication, determined as:</p>{eq1}"
                     f"<p>Give the probabilities of the individual publications reaching at least <em>h</em>+1 "
                     f"citations in the next year, the stochastic <em>h-</em>index is then calculated as</p>{eq2}"
                     f"<p>where </p>{eq3}<p>These products and sums represent the combined probabilities of all of "
                     f"the ways that the publication set can fail to reach the citation count necessary to achieve an "
                     f"<em>h-</em>index of <em>h</em>+1.</p><p>One of the interesting factors of this index is it "
                     f"can, within certain limits, decrease from one year to the next. If more poorly cited "
                     f"publications fail to be cited with enough frequency in a given year, the reduced average "
                     f"rate of citation for those publications can decreases the probability of achieving "
                     f"<em>h</em>+1 the following year.")
    m.references = ["Nair, G.M., and B.A. Turlach (2012) The stochastic <em>h-</em>index. <em>Journal of "
                    "Informetrics</em> 6(1):80&ndash;87."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_stochastic_h
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# multiple h-index (Yaminfirooz and Gholinia 2015)
def calculate_multiple_h_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    year = metric_set.year()
    pub_years = metric_set.publication_years()
    return Impact_Funcs.calculate_multiple_h_index(citations, year, pub_years)


def metric_multiple_h_index() -> Metric:
    m = Metric()
    m.name = "multiple h-index"
    m.full_name = "multiple h-index"
    m.html_name = "multiple <em>h-</em>index"
    m.symbol = "<em>Mh</em>"
    m.axis_name = r"$Mh$"
    m.synonyms = ["<em>Mh</em>"]
    m.metric_type = FLOAT
    # m.example = write_multiple_h_index_example
    equation = (r"$$Mh = \sqrt{\sum\limits_{i=1}^P\frac{h_iC_i^2}{\text{age}_i}} = "
                r"\sqrt{\sum\limits_{i=1}^P\frac{h_iC_i^2}{Y_i-Y_0+1}},$$")

    m.description = ('<p>The multiple <em>h-</em>index (Yaminfirooz and Gholinia 2015) is essentially a function '
                     'of the __multidim h-index__ where the series of <em>h-</em>indices are used to combine the '
                     'citation counts of individual publications into a single value, including a scaling for the '
                     'age of each publication.</p><p>The first step is to calculate the multidimensional '
                     '<em>h-</em>index, keeping track of which value of <em>h</em> in the multidimensional vector '
                     'each publication falls into. From these, one can calculate the multiple <em>h-</em>index as'
                     f'</p>{equation}<p>where <em>h<sub>i</sub></em> is the value of the multidimensional '
                     '<em>h-</em>index associated with the <em>i</em><sup>th</sup> publication.</p>')

    m.references = ["Yaminfirooz, M., and H. Gholinia (2015) Multiple h-index: A new scientometric indicator. "
                    "<em>Electronic Library</em> 33(3):547&ndash;556."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_multiple_h_index
    m.properties["Core Metric"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# hmaj-index (Hu et al. 2010; Bucur et al. 2015)
def calculate_hmaj_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    primary = metric_set.primary_authorship()
    return Impact_Funcs.calculate_hmaj_index(citations, primary)


def metric_hmaj_index() -> Metric:
    m = Metric()
    m.name = "hmaj-index"
    m.full_name = "hmajor-index"
    m.html_name = "<em>h<sub>major</sub>-</em>index"
    m.symbol = "<em>h<sub>maj</sub></em>"
    m.axis_name = r"$h_{maj}$"
    m.synonyms = ["<em>h</em>(<em>p</em>,<em>t</em>)"]
    m.metric_type = INT
    m.description = ('<p>This metric proposed by Hu <em>et al.</em> (2010) suggests reporting an <em>h-</em>index '
                     'based only on those publications in which the author is a major contributor '
                     '(lead author or corresponding author).</p><p><em>h<sub>maj</sub></em> is essentially '
                     'identical to the primary author part of the <em>h</em>(<em>p</em>,<em>t</em>) index pair '
                     'suggested by Bucur <em>et al.</em> (2015), with the only potential difference being subtleties '
                     'in how one defines a major or primary author. This concept is very similar to a few other '
                     'proposals, including the __stratified h-index__ and the __first-author h-index__.</p>')
    m.references = ["Hu, X., R. Rousseau, and J. Chen (2010) In those fields where multiple authorship is the rule, "
                    "the h-index should be supllmeneted by role-based h-indices. <em>Journal of Information "
                    "Science</em> 36(1):73&ndash;85.",
                    "Bucur, O., A. Almasan, R. Zubarev, M. Friedman, G.L. Nicolson, P. Sumazin, M. Leabu, "
                    "B.S. Nikolajczyk, D. Avram, T. Kunej, G.A. Calin, A.K. Godwin, H.-O. Adami, P.G. Zaphiropoulos, "
                    "D.R. Richardson, G. Schmitt-Ulms, H. Westerblad, M. Keniry, G.E.R. Grau, S. Carbonetto, "
                    "R.V. Stan, A. Popa-Wagner, K. Takhar, B.W. Baron, P.J. Galardy, F. Yang, D. Data, O. Fadare, "
                    "K.T.J. Yeo, G.R. Gabreanu, S. Andrei, G.R. Soare, M.A. Nelson, and E.A. Liehn (2015) An "
                    "updated h-index measures both the primary and total scientific output of a researcher. "
                    "<em>Discoveries</em> 3(3):e50."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hmaj_index
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Coauthorship"] = True
    return m


# fractional publication count
def calculate_total_pubs_fractional(metric_set: MetricSet) -> float:
    return Impact_Funcs.calculate_total_pubs_coauthor_adj("fractional", metric_set.author_counts(),
                                                          metric_set.author_position())


def metric_total_pubs_fractional() -> Metric:
    m = Metric()
    m.name = "total pubs frac"
    m.full_name = "total publications (fractional counting)"
    m.symbol = "<em>P<sub>frac</sub></em>"
    m.axis_name = r"$P_\text{frac}$"
    m.synonyms = ["<em>P<sub>frac</sub></em>"]
    m.metric_type = FLOAT
    equation = r"$$P_{frac} = \sum\limits_{i=1}^P\frac{1}{A_i}.$$"
    m.description = ('<p>In just the same way one can account for coauthorship when calculating various '
                     'citation-based metrics, one could use the same approach for counting the total number of '
                     'publications of an author.</p><p>This version uses the fractional approach for assigning '
                     'authorship credit, with each author of a publication getting an equal amount of credit. If '
                     '<em>A<sub>i</sub></em>is the number of authors of the <em>i</em><sup>th</sup> publication, '
                     f'the total publications of an author with fractional authorship counting is</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_pubs_fractional
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# proportional publication count
def calculate_total_pubs_proportional(metric_set: MetricSet) -> float:
    return Impact_Funcs.calculate_total_pubs_coauthor_adj("proportional", metric_set.author_counts(),
                                                          metric_set.author_position())


def metric_total_pubs_proportional() -> Metric:
    m = Metric()
    m.name = "total pubs prop"
    m.full_name = "total publications (proportional counting)"
    m.symbol = "<em>P<sub>prop</sub></em>"
    m.axis_name = r"$P_\text{prop}$"
    m.synonyms = ["<em>P<sub>prop</sub></em>"]
    m.metric_type = FLOAT
    equation = r"$$P_{prop}=\sum\limits_{i=1}^P2\frac{A_i + 1 - a_i}{A_i\left(A_i + 1\right)}.$$"
    m.description = ('<p>In just the same way one can account for coauthorship when calculating various '
                     'citation-based metrics, one could use the same approach for counting the total number of '
                     'publications of an author.</p><p>This version uses the proportional approach for assigning '
                     'authorship credit, with each author\'s contribution declining with their subsequent position '
                     'within the author list. If <em>A<sub>i</sub></em> is the number of authors of the '
                     '<em>i</em><sup>th</sup> publication and <em>a<sub>i</sub></em> is the position of the target '
                     'author within that publication\'s author list, the total publications of an author with '
                     f'proportional authorship counting is</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_pubs_proportional
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# geometric publication count
def calculate_total_pubs_geometric(metric_set: MetricSet) -> float:
    return Impact_Funcs.calculate_total_pubs_coauthor_adj("geometric", metric_set.author_counts(),
                                                          metric_set.author_position())


def metric_total_pubs_geometric() -> Metric:
    m = Metric()
    m.name = "total pubs geom"
    m.full_name = "total publications (geometric counting)"
    m.symbol = "<em>P<sub>geom</sub></em>"
    m.axis_name = r"$P_\text{geom}$"
    m.synonyms = ["<em>P<sub>geom</sub></em>"]
    m.metric_type = FLOAT
    equation = r"$$P_{geom}=\sum\limits_{i=1}^P\frac{2^{A_i - a_i}}{2^{A_i}-1}.$$"
    m.description = ('<p>In just the same way one can account for coauthorship when calculating various '
                     'citation-based metrics, one could use the same approach for counting the total number of '
                     'publications of an author.</p><p>This version uses the geometric approach for assigning '
                     'authorship credit, with each author\'s contribution declining with their subsequent position '
                     'within the author list. If <em>A<sub>i</sub></em> is the number of authors of the '
                     '<em>i</em><sup>th</sup> publication and <em>a<sub>i</sub></em> is the position of the target '
                     'author within that publication\'s author list, the total publications of an author with '
                     f'geometric authorship counting is</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_pubs_geometric
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# harmonic publication count
def calculate_total_pubs_harmonic(metric_set: MetricSet) -> float:
    return Impact_Funcs.calculate_total_pubs_coauthor_adj("harmonic", metric_set.author_counts(),
                                                          metric_set.author_position())


def metric_total_pubs_harmonic() -> Metric:
    m = Metric()
    m.name = "total pubs harm"
    m.full_name = "total publications (harmonic counting)"
    m.symbol = "<em>P<sub>harm</sub></em>"
    m.axis_name = r"$P_\text{harm}$"
    m.synonyms = ["<em>P<sub>harm</sub></em>"]
    m.metric_type = FLOAT
    equation = r"$$P_{harm}=\sum\limits_{i=1}^P\frac{\frac{1}{a_i}}{\sum\limits_{j=1}^{A_i}\frac{1}{j}}.$$"
    m.description = ('<p>In just the same way one can account for coauthorship when calculating various '
                     'citation-based metrics, one could use the same approach for counting the total number of '
                     'publications of an author.</p><p>This version uses the harmonic approach for assigning '
                     'authorship credit, with each author\'s contribution declining with their subsequent position '
                     'within the author list. If <em>A<sub>i</sub></em> is the number of authors of the '
                     '<em>i</em><sup>th</sup> publication and <em>a<sub>i</sub></em> is the position of the target '
                     'author within that publication\'s author list, the total publications of an author with '
                     f'harmonic authorship counting is</p>{equation}')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_total_pubs_harmonic
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# l sequence (liu and yang 2014)
def calculate_l_sequence(metric_set: MetricSet) -> int:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    return Impact_Funcs.calculate_l_sequence(pub_data)


def write_l_sequence_example(metric_set: MetricSet) -> str:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    pub_cites = Impact_Funcs.citations_per_pub_per_year(pub_data)
    year_list = [m.year() for m in metric_list[:metric_pos+1]]
    npubs = [metric_list[i].metrics["total pubs"].value for i in range(metric_pos+1)]

    outstr = ('<p>Publications are ordered within each year by number of citations obtained within that year, '
              'from highest to lowest.</p>')
    outstr += '<table class="example_table">\n'
    lvalues = []
    for j, y in enumerate(year_list):
        cur_year_cites = [x[j] for x in pub_cites]
        sorted_citations = sorted(cur_year_cites, reverse=True)
        sorted_citations = sorted_citations[:npubs[j]]     # remove zero counts for pubs not yet published that year
        lv = Impact_Funcs.get_rank_value(sorted_citations)
        lvalues.append(lv)

        rows = ["" for _ in range(4)]
        rows[0] = f'<tr><th>{y}</th>'
        rows[1] = f'<tr class="top_row"><th>Citations</th>'
        rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[3] = '<tr><th></th>'

        for i, c in enumerate(sorted_citations):
            if i + 1 == lv:
                v = f'<em>L</em><sub>{y}</sub>{NBEQ}{lv}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[1] += f'<td{ec}>{c}</td>'
            rows[2] += f'<td{ec}>{i+1}</td>'
            rows[3] += f'<td>{v}</td>'
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>\n'

    lvalues = [str(lv) for lv in lvalues]
    outstr += (f'<p>The index is calculated following the standard <em>h-</em>index approach but based only on '
               f'citations obtained within a particular year. The <em>L-</em>Sequence is the full series of '
               f'values for all years, thus {", ".join(lvalues)}.</p>')
    return outstr


def metric_l_sequence() -> Metric:
    m = Metric()
    m.name = "l seq"
    m.full_name = "L-Sequence"
    m.html_name = "<em>L-</em>Sequence"
    m.symbol = "<em>L<sub>y</sub></em>"
    m.axis_name = r"$L_y$"
    m.metric_type = INT
    m.description = ('<p>The <em>L-</em>Sequence is a multi-dimensional measure where impact is measured as a '
                     'series of <em>h-</em>indices with each one based on the citations for a single year. In '
                     'practice, this means that from one year to the next, the only change in the sequences is the '
                     'value for the latest year.</p><p>In practice the value of <em>L</em> for a particular year may '
                     'be higher or lower than the previous year, depending on what the citation pattern for that '
                     'particular year ended up being.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_l_sequence
    m.example = write_l_sequence_example
    m.properties["Multidimensional Metric"] = True
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Time"] = True
    m.properties["Core Citations"] = True
    m.references = ["Liu, Y., and Y. Yang (2014) Empirical study of <em>L-</em>Sequence: The basic <em>h-</em>index "
                    "sequence for cumulative publications with consideration of the yearly citation performance. "
                    "<em>Journal of Informetrics</em> 8(3):478&ndash;485."]
    return m


# l∝ (liu and yang 2014)
def calculate_l_prop(metric_set: MetricSet) -> int:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    return Impact_Funcs.calculate_l_prop(pub_data)


def write_l_prop_example(metric_set: MetricSet) -> str:
    metric_list = metric_set.parent_list
    metric_pos = metric_list.index(metric_set)
    pub_data = [p.citations[:metric_pos+1] for p in metric_set.publications]
    pub_cites = Impact_Funcs.citations_per_pub_per_year(pub_data)
    year_list = [m.year() for m in metric_list[:metric_pos+1]]
    npubs = [metric_list[i].metrics["total pubs"].value for i in range(metric_pos+1)]

    outstr = ('<p>Publications are ordered within each year by number of citations obtained within that year, '
              'from highest to lowest.</p>')
    outstr += '<table class="example_table">\n'
    lvalues = []
    for j, y in enumerate(year_list):
        cur_year_cites = [x[j] for x in pub_cites]
        sorted_citations = sorted(cur_year_cites, reverse=True)
        sorted_citations = sorted_citations[:npubs[j]]     # remove zero counts for pubs not yet published that year
        lv = Impact_Funcs.get_rank_value(sorted_citations)
        lvalues.append(lv)

        rows = ["" for _ in range(4)]
        rows[0] = f'<tr><th>{y}</th>'
        rows[1] = f'<tr class="top_row"><th>Citations</th>'
        rows[2] = '<tr><th>Rank (<em>i</em>)</th>'
        rows[3] = '<tr><th></th>'

        for i, c in enumerate(sorted_citations):
            if i + 1 == lv:
                v = f'<em>L</em><sub>{y}</sub>{NBEQ}{lv}'
                ec = ' class="box"'
            else:
                v = ""
                ec = ""
            rows[1] += f'<td{ec}>{c}</td>'
            rows[2] += f'<td{ec}>{i+1}</td>'
            rows[3] += f'<td>{v}</td>'
        for row in rows:  # add table row endings
            row += '</tr>\n'
        outstr += "".join(rows)
    outstr += '</table>\n'

    lvalues = [str(lv) for lv in lvalues]
    lp = metric_set.metrics["l prop"].value
    outstr += (f'<p>The index is the sum of the values in the <em>L-</em>Sequence, thus '
               f'<em>L<sub>∝</sub></em>{NBEQ}{NBPLUS.join(lvalues)}{NBEQ}{lp}.</p>')
    return outstr


def metric_l_prop() -> Metric:
    m = Metric()
    m.name = "l prop"
    m.full_name = "L∝"
    m.html_name = "<em>L<sub>∝</sub></em>"
    m.axis_name = r"$L_\propto$"
    m.metric_type = INT
    m.example = write_l_prop_example
    m.description = ('<p><em>L<sub>∝</sub></em> is simply the sum of the values in the __l seq__, '
                     'meant to be viewed as an alternative to the __h-index__.</p>')
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_l_prop
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Time"] = True
    m.properties["Core Citations"] = True
    m.references = ["Liu, Y., and Y. Yang (2014) Empirical study of <em>L-</em>Sequence: The basic <em>h-</em>index "
                    "sequence for cumulative publications with consideration of the yearly citation performance. "
                    "<em>Journal of Informetrics</em> 8(3):478&ndash;485."]
    return m


# k-index (Kaptay 2020)
def calculate_k_index_kaptay(metric_set: MetricSet) -> float:
    fwca = metric_set.metrics["frac weight cite agg"].value
    return Impact_Funcs.calculate_k_index_kaptay(fwca)


def metric_k_index_kaptay() -> Metric:
    m = Metric()
    m.name = "Kaptay k-index"
    m.full_name = "k-index (Kaptay)"
    m.html_name = "<em>k-</em>index (Kaptay)"
    m.symbol = "<em>k</em>"
    m.axis_name = r"$k$"
    m.metric_type = FLOAT
    equation = r"$$k=\sqrt{\sum\limits_{i=1}^{P}{\frac{C_i}{A_i}}}.$$"
    m.description = ('<p>The <em>k-</em>index (Kapatay 2010) is a measure of impact that account for all citations '
                     'as well as the number of authors of each publication. It is the square-root of the author-credit-'
                     'adjusted citation count for each publication. Without additional information on author credit, '
                     f'credit is assigned strictly based on the fractional number of authors.</p>{equation}<p>This '
                     'metric is simply the square-root of the __frac weight cite agg__, but is supposed to '
                     'approximate the value of the __h-index__.</p>')
    m.references = ["Kaptay, G. (2020) The <em>k-</em>index is introduced to replace the <em>h-</em>index to "
                    "evaluate better the scientific excellence of individuals. <em>Heliyon</em> 6(7):e04415."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_k_index_kaptay
    m.properties["Alternative Metric"] = True
    m.properties["Coauthorship"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# kz-index (Sharma and Uddin 2026)
def calculate_kz_index(metric_set: MetricSet) -> float:
    citations = metric_set.citations
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    h = metric_set.metrics["h-index"].value
    return Impact_Funcs.calculate_kz_index(citations, pub_years, year, h)


def metric_kz_index() -> Metric:
    m = Metric()
    m.name = "Kz index"
    m.full_name = "Kz index"
    m.html_name = "<em>K<sub>z</sub></em> index"
    m.symbol = "<em>K<sub>z</sub></em>"
    m.axis_name = r"$K_z$"
    m.metric_type = FLOAT
    equation1 = r"$$k_i=\frac{\ln{C_i}}{\ln \left(h+1\right)}.$$"
    equation2 = r"$$K_z=\sum\limits_{i=1}^P \frac{k_i}{Y - Y_i + 1},$$"
    m.description = ('<p>The <em>K<sub>z</sub></em> index (Sharma and Uddin 2026) expands upon the two-dimensional '
                     'interpretation of the __h-index__ by introducing the age of publications and a measure of the '
                     'impact of each publication to <em>h</em> into a three-dimensional framework which includes '
                     'all publications, rather than just the core. The impact parameter for each publication is '
                     f'calculated as</p>{equation1}<p> The metric <em>K<sub>z</sub></em> is then determined as</p>'
                     f'{equation2}<p>where <em>Y</em> is the current year (the denominator is the age of the '
                     '<em>i</em><sup>th</sup> publication). This metric is essentially the area under a '
                     'three-dimensional surface defined by the '
                     'rank of each publication along one axis, it\'s age on a second axis, and the ratio of it\'s '
                     'age-normalized impact on the third axis.</p>')
    m.references = ["Sharma, K., and Z. Uddin (2026) Beyond the <em>h‑</em>index: Evaluating continuous research "
                    "impact using the <em>K<sub>z</sub></em> index. <em>Scientometrics</em> 131:3193&ndash;3217."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_kz_index
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# λ-index (Lathabai 2026)
def calculate_lambda_index(metric_set: MetricSet) -> int:
    citations = metric_set.citations
    return Impact_Funcs.calculate_lambda_index(citations)


def write_lambda_index_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Cumulative Citations (<em>C<sup>i</sup></em> =Σ<em>C<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th><em>C<sup>i</sup>/C<sup>P</sup></em></th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr class="top_row"><th>1 - <em>i/P</em></th>'
    rows[5] = '<tr><th></th>'
    lam = metric_set.metrics["λ-index"].value
    s = 0
    total_c = sum(citations)
    p = len(citations)
    for i, c in enumerate(citations):
        s += c
        if i + 1 == lam:
            v = f'<em></em>λ{NBEQ}{lam}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{s}</td>'
        rows[2] += f'<td{ec}>{s/total_c:0.4f}</td>'
        rows[3] += f'<td>{i+1}</td>'
        rows[4] += f'<td{ec}>{1 - (i+1)/p:0.4f}</td>'
        rows[5] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += f'<p>The largest rank where <em>C<sup>i</sup>/C<sup>P</sup></em> ≤ 1 - <em>i/P</em> is {lam}.</p>'
    return outstr


def metric_lambda_index() -> Metric:
    m = Metric()
    m.name = "λ-index"
    m.full_name = "λ-index"
    m.symbol = "λ"
    m.axis_name = r"$\lambda$"
    m.metric_type = INT
    equation = r"$$\lambda=\underset{i}{\max} \left( \frac{C^i}{C^P} \leq 1-\frac{i}{P}\right).$$"
    m.description = ('<p>The λ-index (Lathabai 2026) is based on the Pareto principle, which essentially observes '
                     'that 80% of outputs are produced by 20% of inputs (the 80:20 rule). In the case of academic '
                     'output, the inputs are publications and the outputs are citations. The λ-index is a measure of '
                     'the largest value which produces a 1-λ/<em>P</em>:λ/<em>P</em> proportion of outputs to '
                     'inputs.</p><p>It is calcaulted by comparing the proportion of total citations found in the '
                     'top <em>i</em> publications to the proportion '
                     f'of publications represented by the top <em>i</em> publications, or</p>{equation}<p></p>')
    m.references = ["Lathabai, H.H. (2026) λ-index: A new indicator based on generalized law in Information "
                    "Production Processes. <em>Journal of Informetrics</em> 20(1):101769."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_lambda_index
    m.example = write_lambda_index_example
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# Pareto rule (Lathabai 2026)
def calculate_pareto_rule(metric_set: MetricSet) -> float:
    lamb = metric_set.metrics["λ-index"].value
    n = metric_set.metrics["total pubs"].value
    return Impact_Funcs.calculate_pareto_rule(lamb, n)


def write_pareto_rule_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    citations = sorted(metric_set.citations, reverse=True)
    rows = ["" for _ in range(6)]
    rows[0] = '<tr><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Cumulative Citations (<em>C<sup>i</sup></em> =Σ<em>C<sub>i</sub></em>)</th>'
    rows[2] = '<tr><th><em>C<sup>i</sup>/C<sup>P</sup></em></th>'
    rows[3] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[4] = '<tr class="top_row"><th>1 - <em>i/P</em></th>'
    rows[5] = '<tr><th></th>'
    lam = metric_set.metrics["λ-index"].value
    s = 0
    total_c = sum(citations)
    p = len(citations)
    for i, c in enumerate(citations):
        s += c
        if i + 1 == lam:
            v = f'<em></em>λ{NBEQ}{lam}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        rows[0] += f'<td>{c}</td>'
        rows[1] += f'<td>{s}</td>'
        rows[2] += f'<td{ec}>{s/total_c:0.4f}</td>'
        rows[3] += f'<td>{i+1}</td>'
        rows[4] += f'<td{ec}>{1 - (i+1)/p:0.4f}</td>'
        rows[5] += f'<td>{v}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    pv = metric_set.metrics["Pareto value"].value
    outstr += (f'<p>The largest rank where <em>C<sup>i</sup>/C<sup>P</sup></em> ≤ 1 - <em>i/P</em> is {lam}. With {p} '
               f'total publications, that makes the '
               f'λ/P&nbsp;%{NBEQ}100&times;{lam}/{p}{NBEQ}{round(pv)}%, representing a '
               f'{100-round(pv)}:{round(pv)} rule.</p>')
    return outstr


def metric_pareto_rule() -> Metric:
    m = Metric()
    m.name = "Pareto value"
    m.full_name = "Pareto value"
    m.symbol = "λ/P %"
    m.axis_name = r"$\lambda/P\text{ %}$"
    m.metric_type = FLOAT
    m.description = ('<p>The λ-index (Lathabai 2026) determines the number of publications for which the proportion '
                     'of total publications represented by λ produces 1-proportion of total citations, based on the '
                     'concept of the Pareto rule, which observed that 80% of outputs were produced by 20% of inputs. '
                     'The Pareto value is the percentage of publications represented by λ, or 100&times;λ/P.</p>'
                     '<p>The proportion of outputs is 100 - the Pareto value, thus a Pareto value of 22 would indicate '
                     'a 78:22 Pareto rule, or 78% of outputs (citations) are produced by 22% of inputs '
                     '(publications).</p>')
    m.references = ["Lathabai, H.H. (2026) λ-index: A new indicator based on generalized law in Information "
                    "Production Processes. <em>Journal of Informetrics</em> 20(1):101769."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_pareto_rule
    m.example = write_pareto_rule_example
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    return m


# h*-index (Rusinek et al. 2026)
def calculate_hstar_index(metric_set: MetricSet) -> float:
    h = metric_set.metrics["h-index"].value
    pub_years = metric_set.publication_years()
    year = metric_set.year()
    year0 = metric_set.first_pub_year
    academic_age = metric_set.academic_age()
    total_cites = metric_set.metrics["total cites"].value
    return Impact_Funcs.calculate_hstar_index(h, pub_years, year, year0, academic_age, total_cites)


def metric_hstar_index() -> Metric:
    m = Metric()
    m.name = "hstar-index"
    m.full_name = "h*-index"
    m.html_name = "<em>h<sup>*</sup></em>-index"
    m.axis_name = r"$h^*$"
    m.symbol = "<em>h<sup>*</sup></em>"
    m.metric_type = FLOAT
    equation = (r"$$h^* = h \times \left(\frac{R_{cnt}}{R_{total}}\right)^{\alpha} \times "
                r"\left(\frac{C^P}{\text{academic age}}\right)^{\beta} \times \frac{1}{\sqrt{\text{academic age}}},$$")
    m.description = ('<p>The <em>h<sup>*</sup></em>-index (Rusinek <em>et al.</em> 2026) is a slightly complicated '
                     'modification of the __h-index__ designed to reflect not only cumulative achievement, but '
                     'also recent productivity and impact. In addition to <em>h</em>, it includes a measure of '
                     'publication regularity (the proportion of two-year intervals of the investigator\'s career that '
                     'they published at least one item), citation intensity (average citations per year of career), '
                     'and an adjustment for career length which introduces a mild penalty for long careers with little '
                     f'recent output.</p><p>The entire formula for the index is:</p>{equation}<p>where '
                     '<em>R<sub>total</sub></em> is the number of two year intervals in the academic career (the '
                     'floor of academic age/2) and <em>R<sub>cnt</sub></em> is the count of those intervals in '
                     'which the researcher published at least one paper. &alpha; and &beta; are tuning parameters '
                     'that have been set to 1.</p><p>Overall, these are multiplicative adjustments to <em>h</em>. '
                     'Two of these terms (the first and third) can never be greater than 1 and would thus serve to '
                     'reduce the value of <em>h<sup>*</sup></em> relative to <em>h</em>, while the second term will '
                     'generally be much greater than 1 and thus increase the value of <em>h<sup>*</sup></em> relative '
                     'to <em>h</em>, potentially dramatically for those who are well cited.</p>')
    m.references = ["Rusinek, A., T. Jankowiak, and A. Besnard (2026) A novel indicator h* to measure research "
                    "efficiency and identify researchers facing challenges: Application to engineering sciences. "
                    "<em>Journal of Informetrics</em> 20(3):101818."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_hstar_index
    m.properties["Alternative Metric"] = True
    m.properties["Time"] = True
    m.properties["All Publications"] = True
    m.properties["All Citations"] = True
    return m


# APR (Rull 2026)
def calculate_apr(metric_set: MetricSet) -> list:
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    return Impact_Funcs.calculate_apr(n_authors, author_pos)


def metric_apr() -> Metric:
    m = Metric()
    m.name = "APR"
    m.full_name = "Author Position Ratio"
    m.symbol = "[Author%, Collaborator%, Manager%, APR]"
    m.metric_type = LIST
    m.list_formats = [FLOAT, FLOAT, FLOAT, STR]
    m.description = ('<p>The Author Position Ratio (Rull 2026) is a statistic focused on coauthorship patterns, rather '
                     'than publications or citations. Like some other metrics, it divides authorship of a publication '
                     'into one of three categories: Author-focused works (those where the researcher is the '
                     'first author), Manager-focused works (those where the researcher is the last author), and '
                     'Collaborator-focused works (those where the researchers is neither first nor last author). '
                     'Like other such metrics, this breakdown makes assumptions about the relationship of '
                     'author position and contribution which may not be true in any given field or any '
                     'given work.</p><p>The metric itself starts by simply calculating the percent of publications '
                     'which fall into each of these three categories. The one with the highest percentage would be '
                     'considered the dominant focus of the researcher. If two categories are similar in level, the '
                     'researcher might earn a mixed-label combining those two categories; if all three are similar, '
                     'they could be viewed to have an equal focus. For reporting purposes, the APR is '
                     'reported as the letter(s) representing the dominant categor(ies) and its percentage (average '
                     'percentage for combined labeling).<p><p>The original paper does not suggest a threshold for '
                     'combining categories, so in these calculations I combined '
                     'categories if the top two were within 5% of each other (or all three if all three were within '
                     '5%).</p><p>Because the three categories must add up to 100%, an obvous way to graph them is '
                     'a ternary plot where positions within a triangle indicate the tripartite combination of '
                     'the three values.</p>')
    m.references = ["Rull, V. (2026) Author position ratio (APR): A simple complementary bibliometric descriptor of "
                    "authorship patterns. <em>Journal of Informetrics</em> 20(1):101776."]
    m.draw_graph = Impact_Graphs.draw_graph_ternary_chart
    m.calculate = calculate_apr
    m.properties["Basic Statistic"] = True
    m.properties["All Publications"] = True
    m.properties["Coauthorship"] = True
    return m


# revised h (Romanovsky 2012)
def calculate_revised_h(metric_set: MetricSet) -> float:
    n_authors = metric_set.author_counts()
    author_pos = metric_set.author_position()
    h = metric_set.metrics["h-index"].value
    is_core = metric_set.is_core
    return Impact_Funcs.calculate_revised_h(h, is_core, n_authors, author_pos)


def write_revised_h_example(metric_set: MetricSet) -> str:
    outstr = '<p>Publications are ordered by number of citations, from highest to lowest.</p>'
    outstr += '<table class="example_table">\n'
    tmp_citations = [c for c in metric_set.citations]
    tmp_author_cnts = [a for a in metric_set.author_counts()]
    tmp_author_pos = [a for a in metric_set.author_position()]
    data = []
    for i in range(len(tmp_citations)):
        data.append([tmp_citations[i], tmp_author_cnts[i], tmp_author_pos[i]])
    data.sort(reverse=True)
    rows = ["" for _ in range(5)]
    rows[0] = '<tr class="top_row"><th>Citations (<em>C<sub>i</sub></em>)</th>'
    rows[1] = '<tr><th>Rank (<em>i</em>)</th>'
    rows[2] = '<tr><th></th>'
    rows[3] = '<tr><th>Authors (<em>A<sub>i</sub></em>)</th>'
    rows[4] = '<tr><th>Author Position (<em>a<sub>i</sub></em>)</th>'
    h = metric_set.metrics["h-index"].value
    r = metric_set.metrics["revised h"].value
    # count 1st/last author papers in core
    acnt = 0
    for i in range(h):
        if (data[i][2] == 1) or (data[i][2] == data[i][1]):
            acnt += 1

    for i, d in enumerate(data):
        c = d[0]
        a = d[1]
        ap = d[2]
        if i + 1 == h:
            v = f'<em>h</em>{NBEQ}{h}'
            ec = ' class="box"'
        else:
            v = ""
            ec = ""
        ec2 = ""
        if i + 1 <= h:
            if (ap == 1) or (a == ap):
                ec2 = ' class="dark_box"'
        rows[0] += f'<td{ec}>{c}</td>'
        rows[1] += f'<td{ec}>{i+1}</td>'
        rows[2] += f'<td>{v}</td>'
        rows[3] += f'<td{ec2}>{a}</td>'
        rows[4] += f'<td{ec2}>{ap}</td>'

    for row in rows:  # add table row endings
        row += '</tr>\n'
    outstr += "".join(rows) + '</table>\n'
    outstr += (f'<p>The <em>h-</em>index is {h}. Of the {h} publications in the core, {acnt} represent first or last '
               f'author publications, so '
               f'<em>r</em>&nbsp;=1.2&times;{acnt}{NBPLUS}0.4&times;{h}{NBEQ}{r:0.4}.</p>')
    return outstr


def metric_revised_h() -> Metric:
    m = Metric()
    m.name = "revised h"
    m.full_name = "revised h-index"
    m.html_name = "revised <em>h-</em>index"
    m.symbol = "<em>r</em>"
    m.axis_name = r"$r$"
    m.metric_type = FLOAT
    equation = r"$$r=1.6a + 0.4\left(h-a\right)=1.2a + 0.4h,$$"
    m.description = ('<p>The revised <em>h-</em>index (Romanovsky 2012) is a modification of the __h-index__ meant '
                     'to account for coauthorship, explicitly giving more weight to publications with first and '
                     'last authorship. It is a simple modification '
                     f'of the <em>h-</em>index:</p>{equation}<p>where <em>a</em> is the count of publications with '
                     f'first or last authorship in the Hirsch core. It gives these papers 60% more weight and those '
                     f'with middle authorship 60% less weight.')
    m.references = ["Romanovsky, A.A. (2012) Revised <em>h</em> index for biomedical research. <em>Cell Cycle</em> "
                    "11(22):4118&ndash;4121."]
    m.draw_graph = Impact_Graphs.draw_graph_line_chart
    m.calculate = calculate_revised_h
    m.example = write_revised_h_example
    m.properties["Core Metric"] = True
    m.properties["Core Publications"] = True
    m.properties["Core Citations"] = True
    m.properties["Coauthorship"] = True
    return m









# Ab-index (Biswal 2013)
# def calculate_ab_index(metric_set: MetricSet) -> float:
    # citations = metric_set.citations
    # # h = metric_set.metrics["h-index"].value
    # primary = metric_set.primary_authorship()
    # return Impact_Funcs.calculate_hmaj_index(citations, primary)


# def metric_ab_index() -> Metric:
#     m = Metric()
#     m.name = "Ab-index"
#     m.full_name = "absolute index"
#     m.html_name = "absolute index"
#     # m.html_name = "<em>h</em>(<em>p</em>,<em>t</em>)-index"
#     m.symbol = "<em>Ab</em>"
#     m.synonyms = ["<em>Ab</em>"]
#     m.metric_type = FLOAT
#
#     m.description = (f"<p>The Absolute index (Biswal 2013) it not a citation-based measure, rather it is a
#     substitute "
#                      f"for __total pubs__ which uses a fractional counting scheme to account for coauthorship."
#                      f"suggests reporting an <em>h-</em>index "
#                      f"based only on those publications in which the author is a major contributor "
#                      f"(lead author or corresponding author).</p><p><em>h<sub>maj</sub></em> is essentially "
#                      f"identical to the primary author part of the <em>h</em>(<em>p</em>,<em>t</em>) index pair "
#                      f"suggested by Bucur <em>et al.</em> (2015), with the only potential difference being
#                      subtleties "
#                      f"in how one defines a major or primary author. This concept is very similar to a few other "
#                      f"proposals, including the __stratified h-index__.</p>")
#
#     m.references = ["Biswal, A.K. (2013) An Absolute Index (Ab-index) to measure a researcher's useful contributions "
#                     "and productivity. <em>PLoS ONE</em> 8(12):e84334."]
#     m.graph_type = LINE_CHART
#     m.calculate = calculate_ab_index
#     m.properties["Basic Statistic"] = True
#     m.properties["All Publications"] = True
#     m.properties["Coauthorship"] = True
#     return m




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
                   metric_normalized_h_index(),
                   metric_v_index(),
                   metric_m_index(),
                   metric_rm_index(),
                   metric_weighted_h_index(),
                   metric_pi_index(),
                   metric_pi_rate(),
                   metric_q2_index(),
                   metric_e_index(),
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
                   # metric_total_coauthor_cites(),
                   # metric_total_coauthor_cite_rate(),
                   # metric_mean_coauthor_cite_rate(),
                   # metric_sharpened_h_index_coauthor(),
                   # metric_b_index_mean_coauthor(),
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
                   metric_indifference(),
                   metric_th_index(),
                   metric_mean_at_index(),
                   metric_dci_index2(),
                   metric_ddci_index2(),
                   metric_dci_index10(),
                   metric_ddci_index10(),
                   metric_history_h_index(),
                   metric_quality_quotient(),
                   metric_scientist_level(),
                   metric_scientist_level_nonint(),
                   metric_q_index(),
                   metric_career_years_h_index_pub(),
                   metric_career_years_h_index_cite(),
                   metric_career_years_h_index_avgcite(),
                   metric_career_years_h_index_diffspeed(),
                   metric_collaborative_index(),
                   metric_degree_of_collaboration(),
                   metric_collaborative_coefficient(),
                   metric_i10_index(),
                   metric_p1_index(),
                   metric_cited_paper_percent(),
                   metric_uncitedness_factor(),
                   metric_uncited_paper_percent(),
                   metric_apparent_h_index(),
                   metric_rec_index(),
                   metric_chi_index(),
                   metric_reci_recp(),
                   metric_academic_trace(),
                   metric_scientific_quality_index(),
                   metric_i100_index(),
                   metric_i1000_index(),
                   metric_first_author_h_index(),
                   metric_iterative_weighted_em_index(),
                   metric_iterative_weighted_emp_index(),
                   metric_o_index(),
                   metric_discounted_h_index(),
                   metric_mikhailov_j_index(),
                   metric_year_based_em_pub(),
                   metric_year_based_em_pycites(),
                   metric_year_based_em_cites(),
                   metric_year_based_emp_pub(),
                   metric_year_based_emp_pycites(),
                   metric_year_based_emp_cites(),
                   metric_h_prime_index(),
                   metric_hc(),
                   metric_k_index_anania_caruso(),
                   metric_w_index_anania_caruso(),
                   metric_h_norm(),
                   metric_k_norm_index(),
                   metric_w_norm_index(),
                   metric_yearly_h_index(),
                   metric_t_index_singh(),
                   metric_fairness(),
                   metric_zynergy(),
                   metric_p20(),
                   metric_rmp(),
                   metric_css(),
                   metric_csr(),
                   metric_slg(),
                   metric_3dsi_pr(),
                   metric_total_collaborators(),
                   metric_partnership_ability(),
                   metric_stratified_h(),
                   metric_platinum_h(),
                   metric_stochastic_h(),
                   metric_multiple_h_index(),
                   metric_hmaj_index(),
                   metric_total_pubs_fractional(),
                   metric_total_pubs_proportional(),
                   metric_total_pubs_geometric(),
                   metric_total_pubs_harmonic(),
                   metric_l_sequence(),
                   metric_l_prop(),
                   metric_k_index_kaptay(),
                   metric_kz_index(),
                   metric_lambda_index(),
                   metric_pareto_rule(),
                   metric_hstar_index(),
                   metric_apr(),
                   metric_revised_h()
                   # metric_ab_index()
                   # metric_beauty_coefficient(),
                   # metric_awakening_time()
                   ]
    return metric_list
