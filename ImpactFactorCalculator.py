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

import Impact_Defs
import datetime
# import urllib.request
from typing import Tuple

tb = '\t'
# LINE_CHART = 1

# these aren't really proper classes, but rather just simple
# multivariate data objects


class Article:
    def __init__(self):
        self.year = 0
        self.authors = 0
        self.author_rank = 0
        self.rank = 0
        self.title = ''
        self.citations = []
        self.self_cites = []
        self.coauthor_cites = []
        # # for GoogleScholar
        # self.authorList = []
        # self.googleScholarURL = ''
        # self.citationURL = ''
        # self.citeList = []


def string_to_date(s: str) -> datetime.date:
    m, d, y = s.split('/')
    return datetime.date(int(y), int(m), int(d))


def date_to_string(d: datetime.date) -> str:
    return str(d.month) + '/' + str(d.day) + '/'+str(d.year)


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

                new_article.author_rank = int(tstr)
                tstr = line[:line.find(tb)]
                line = line[line.find(tb)+1:]

                new_article.title = tstr
                cite_list = line.split(tb)
                for n in cite_list:
                    if n == 'n/a':
                        n = None
                    else:
                        n = int(n)
                    new_article.citations.append(n)
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
    def read_self_citation_file(filename: str, is_coauthor: bool) -> None:
        with open(filename, "r") as infile:
            a = -1
            for line in infile:
                line = line.strip()
                a += 1
                # skip header
                if (a != 0) and (line != ''):
                    article = article_list[a - 1]
                    # skip year
                    line = line[line.find(tb) + 1:]
                    # skip authors
                    line = line[line.find(tb) + 1:]
                    # skip author rank
                    line = line[line.find(tb) + 1:]
                    # skip title
                    line = line[line.find(tb) + 1:]
                    cite_list = line.split(tb)
                    for n in cite_list:
                        if n == 'n/a':
                            n = None
                        else:
                            n = int(n)
                        if is_coauthor:
                            article.coauthor_cites.append(n)
                        else:
                            article.self_cites.append(n)

    read_self_citation_file(sname, False)
    read_self_citation_file(cname, True)


# -----------------------------------------------------
# Main Calculation Loop
# -----------------------------------------------------

def calculate_metrics(y: int, date_list: list, article_list: list, inc_self: bool) -> Impact_Defs.MetricSet:
    """
    function to calculate impact factor metrics for data for a given date 
    """

    metrics = Impact_Defs.MetricSet()
    metrics.date = date_list[y]

    # determine active articles and raw data summaries
    metrics.first_pub_year = 3000  # arbitrarily large year
    for article in article_list:
        if article.citations[y] is not None:
            metrics.publications.append(article)
            metrics.first_pub_year = min(article.year, metrics.first_pub_year)

    # construct sub-lists for active articles only
    n = len(metrics.publications)
    metrics.citations = [0 for _ in range(n)]
    if inc_self:
        metrics.self_citations = [0 for _ in range(n)]
        metrics.coauthor_citations = [0 for _ in range(n)]

    i = -1
    for article in metrics.publications:
        i += 1
        metrics.citations[i] = article.citations[y]
        if inc_self:
            metrics.self_citations[i] = article.self_cites[y]
            metrics.coauthor_citations[i] = article.coauthor_cites[y]

    metrics.calculate_ranks()
    return metrics


# -----------------------------------------------------
# output a table of all results
# -----------------------------------------------------
def write_output(fname: str, date_list: list, yearly_metrics_list: list, inc_self: bool) -> None:
    # fstr = "1.4f"  # constant formatting string
    with open(fname, "w", encoding="utf-8") as outfile:
        # write header of dates
        outfile.write("Date")
        for date in date_list:
            outfile.write(tb + date_to_string(date))
        outfile.write("\n")

        # write a row for each metric type, with columns representing years
        base_metric_list = yearly_metrics_list[0]
        for m in base_metric_list.metric_names:
            tmp_metric = base_metric_list.metrics[m]
            if tmp_metric.is_self and not inc_self:
                pass  # skip self-citation metrics
            else:
                outfile.write(tmp_metric.full_name)  # name of metric
                for metric_list in yearly_metrics_list:
                    outfile.write(tb + str(metric_list.metrics[m]))
                outfile.write("\n")


# -----------------------------------------------------
# Output results as set of webpages
# -----------------------------------------------------
# def webheader(outfile, page_title: str, data: list) -> None:
#     outfile.write("<!DOCTYPE HTML>\n")
#     outfile.write("<html lang=\"en\">\n")
#     outfile.write("  <head>\n")
#     outfile.write("    <meta charset=\"utf-8\" />\n")
#     outfile.write("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />\n")
#     outfile.write("    <title>" + page_title + "</title>\n")
#     outfile.write("    <meta name=\"description\" content=\"xxx\" />\n")
#     outfile.write("    <link rel=\"author\" href=\"mailto:msr@asu.edu\" />\n")
#     outfile.write("    <script src=\"https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?"
#                   "config=TeX-MML-AM_CHTML\"></script>\n")
#     # graph data
#     outfile.write("    <script type=\"text/javascript\" src=\"https://www.google.com/jsapi\"></script>\n")
#     outfile.write("    <script type=\"text/javascript\">\n")
#     outfile.write("      google.load(\"visualization\", \"1\", {packages:[\"corechart\"]});\n")
#     # outfile.write("      google.charts.load('current', {'packages':['line']});")
#     outfile.write("      google.setOnLoadCallback(drawChart);\n")
#     outfile.write("      function drawChart() {\n")
#     for i, dataset in enumerate(data):
#         header = dataset[0]
#         data_values = dataset[1]
#         chart_type = dataset[2]
#         vaxis_title = dataset[3]
#         chart_options = dataset[4]
#         outfile.write("        var data{} = google.visualization.arrayToDataTable([\n".format(i))
#         outfile.write("           [" + ",".join(header) + "],\n")
#         for d in data_values:
#             outfile.write("           [" + ",".join(d) + "],\n")
#         outfile.write("		]);\n")
#         outfile.write("\n")
#         outfile.write("        var options" + str(i) + " = {\n")
#         # outfile.write("          title: \"" + chart_title + "\",\n")
#         outfile.write("		  legend: {position: 'right'},\n")
#         outfile.write("		  vAxis: {title: '" + vaxis_title + "'},\n")
#         outfile.write("		  hAxis: {slantedText: true},\n")
#         if chart_options is not None:
#             for opt in chart_options:
#                 outfile.write(opt)
#         outfile.write("        };\n")
#         outfile.write("\n")
#         # outfile.write("        var chart{} = new google.charts."
#         #               "Line(document.getElementById('impact_chart{}_div'));\n".format(i, i))
#         outfile.write("        var chart{} = new google.visualization."
#                       "LineChart(document.getElementById('impact_chart{}_div'));\n".format(i, i))
#         # if chart_type == LINE_CHART:
#         #     outfile.write("        var chart{} = new google.visualization."
#         #                   "LineChart(document.getElementById('impact_chart{}_div'));\n".format(i, i))
#         # elif chart_type == POINT_CHART:
#         #     outfile.write("        var chart{} = new google.visualization."
#         #                   "ScatterChart(document.getElementById('impact_chart{}_div'));\n".format(i, i))
#         outfile.write("        chart{}.draw(data{}, options{});\n".format(i, i, i))
#         # outfile.write("        chart{}.draw(data{}, google.chart.Line.convertOptions(options{}));\n".format(i, i, i))
#         outfile.write("\n")
#     outfile.write("		}\n")
#     outfile.write("    </script>\n")
#     outfile.write("  </head>\n")
#
#
# def write_paragraph(outfile, p: str) -> None:
#     outfile.write("    <p>" + p + "</p>\n")
#
#
# def webout_h_rate(date_list: list, metric_list: list) -> None:
#     """
#     Output a webpage with the h-rate and least squares h-rates
#     """
#     graphs = []
#     data1 = []
#     data2 = []
#     data3 = []
#     for i, d in enumerate(date_list):
#         year = d.year
#         m = metric_list[i]
#         data1.append(["\'" + str(year) + "\'", str(m.values["h-rate"]), str(m.values["ls h-rate"])])
#         if i == 0:
#             v = "0,0"
#         elif i == len(date_list) - 1:
#             v = str(m.values["h-index"]) + "," + str(m.values["ls h-rate"]*(len(date_list)-1))
#         else:
#             v = "null,null"
#         data2.append(["\'" + str(year) + "\'", str(m.values["h-index"]), v])
#         data3.append(["\'" + str(year) + "\'", str(m.values["time-scaled h-index"])])
#     header1 = ["\'Year\'", "\'h-rate\'", "\'ls h-rate\'"]
#     header2 = ["\'Year\'", "\'h-index\'", "\'h-rate\'", "\'ls h-rate\'"]
#     header3 = ["\'Year\'", "\'time-scaled h-index\'"]
#     graphs.append([header1, data1, LINE_CHART, "h per year", None])
#     options = ["       interpolateNulls: true,\n",
#                "       series: {\n",
#                "       0: {\n",
#                "           pointsVisible: true,\n",
#                "           lineWidth: 0,\n",
#                "           pointSize: 10\n",
#                "          }\n",
#                "         }\n"]
#     graphs.append([header2, data2, LINE_CHART, "h-index", options])
#     graphs.append([header3, data3, LINE_CHART, "h per sqrt(year)", None])
#
#     with open("webout/h_rate.html", "w", encoding="utf-8") as outfile:
#         webheader(outfile, "h-rate", graphs)
#
#         # define equations and symbols
#         m_equation = r"$$m=\frac{h}{Y-Y_{0}+1}$$"
#         hstr = r"\(h\)"
#         ystr = r"\(Y\)"
#         y0str = r"\(Y_{0}\)"
#         hts_equation = r"$$h^{TS}=\frac{h}{\sqrt{Y-Y_{0}+1}}$$"
#         p1 = "Originaly defined by Hirsch (2005), this metric is also known as the " \
#              "<strong><em>m-</em>quotient,</strong> " \
#              "<strong><em>m-</em>ratio index,</strong> <strong>age-normalized <em>h-</em>index,</strong> and " \
#              "<strong>Carbon <em>h-</em>factor.</strong> It measures the rate at which the <em>h-</em>index has " \
#              "increased over the career of a researcher. It is calculated simply as:"
#         p2 = "where " + hstr + " is the <em>h-</em>index in year " + ystr + " and " + y0str + \
#              " is the year of the researcher's first publication (the denominator of this equation is the academic " \
#              "age of the researcher)."
#         p3 = "The above estimation is essentially just the slope of the line from the start of a researcher's " + \
#              "career through the most recent estimate of the <em>h-</em>index. If one has access to yearly " \
#              "estimates of " + hstr + ", an alternative would be to perform a linear regression of " + hstr + \
#              " versus year of academic career (through the origin) and use the slope of that line for a more accurate" \
#              " measure. This is known as the <strong>least squares <em>h-</em>rate</strong> (Burrell, 2007)."
#         p4 = "Another similar measure, the <strong>time-scaled <em>h-</em>index</strong> (Mannella and Rossi 2013) " \
#              "scales " + hstr + " by the square-root of the academic age."
#         outfile.write("  <body>\n")
#         outfile.write("    <h1><em>h-</em>rate</h1>\n")
#         outfile.write("    <h2>Description</h2>\n")
#         write_paragraph(outfile, p1)
#         write_paragraph(outfile, m_equation)
#         write_paragraph(outfile, p2)
#         write_paragraph(outfile, p3)
#         outfile.write("   <div id=\"impact_chart1_div\"></div>\n")
#         outfile.write("   <p class=\"caption\" style=\"font-style: italic; font-size: 0.75em; text-align: center\">"
#                       "The points represent the <em>h-</em>index at the end of each year. "
#                       "The simple <em>h-</em>rate is the slope of the line passing from the origin through the final "
#                       "point. The least-squares estimate is based on the linear regression of all points, "
#                       "with the intercept forced through the origin.</p>\n")
#
#         write_paragraph(outfile, p4)
#         write_paragraph(outfile, hts_equation)
#         outfile.write("    <h2>History</h2>\n")
#         outfile.write("   <div id=\"impact_chart0_div\"></div>\n")
#         outfile.write("   <div id=\"impact_chart2_div\"></div>\n")
#         outfile.write("  </body>\n")
#         outfile.write("</html>\n")
#
#
# def webout_basic_data(date_list: list, metric_list: list) -> None:
#     """
#     Output a webpage with the base data and simple stats
#     """
#     graphs = []
#     data1 = []
#     data2 = []
#     data3 = []
#     data4 = []
#     data5 = []
#     for i, d in enumerate(date_list):
#         year = d.year
#         m = metric_list[i]
#         data1.append(["\'" + str(year) + "\'", str(m.values["total pubs"])])
#         data2.append(["\'" + str(year) + "\'", str(m.values["total cites"]), str(m.values["max cites"])])
#         data3.append(["\'" + str(year) + "\'", str(m.values["avg cites per pub"]),
#                       str(m.values["median cites per pub"])])
#         data4.append(["\'" + str(year) + "\'", str(m.values["time-scaled num papers"])])
#         data5.append(["\'" + str(year) + "\'", str(m.values["time-scaled num citations"])])
#     header1 = ["\'Year\'", "\'total\'"]
#     header2 = ["\'Year\'", "\'total\'", "\'maximum\'"]
#     header3 = ["\'Year\'", "\'mean\'", "\'median\'"]
#     header4 = ["\'Year\'", "\'time-scaled number of papers\'"]
#     header5 = ["\'Year\'", "\'time-scaled citation index\'"]
#     graphs.append([header1, data1, LINE_CHART, "Publications", None])
#     graphs.append([header2, data2, LINE_CHART, "Citations", None])
#     graphs.append([header3, data3, LINE_CHART, "Citations per Publication", None])
#     graphs.append([header4, data4, LINE_CHART, "Publications per Year", None])
#     graphs.append([header5, data5, LINE_CHART, "Citations per Year", None])
#
#     with open("webout/basic_data.html", "w", encoding="utf-8") as outfile:
#         webheader(outfile, "basic data", graphs)
#
#         # # define equations and symbols
#         # m_equation = r"$$m=\frac{h}{Y-Y_{0}+1}$$"
#         # hstr = r"\(h\)"
#         # ystr = r"\(Y\)"
#         # y0str = r"\(Y_{0}\)"
#         # hts_equation = r"$$h^{TS}=\frac{h}{\sqrt{Y-Y_{0}+1}}$$"
#         p1 = "The raw data of impact are publications and citations to the publications. Beyond simply counting how " \
#              "many of these there are each year, some simple obvious summaries one can make include identifying the " \
#              "publication with the maximum number of citations, as well as considering the average number of " \
#              "citations per publication (as both mean and median)."
#         p2 = "If one wants to consider simple rates of impact, then other obvious measures would be the mean number " \
#              "of publications per year and the mean number of citations per year. These have been referred to as the " \
#              "<strong>time-scaled number of papers (<em>P<sup>TS</sup></em>)</strong> and <strong>time-scaled " \
#              "citation index (<em>C<sup>TS</sup></em>)</strong> in the literature."
#         # p2 = "where " + hstr + " is the <em>h-</em>index in year " + ystr + " and " + y0str + \
#         #      " is the year of the researcher's first publication (the denominator of this equation is the academic " \
#         #      "age of the researcher)."
#         # p3 = "The above estimation is essentially just the slope of the line from the start of a researcher's " + \
#         #      "career through the most recent estimate of the <em>h-</em>index. If one has access to yearly " \
#         #      "estimates of " + hstr + ", an alternative would be to perform a linear regression of " + hstr + \
#         #      " versus year of academic career (through the origin) and use the slope of that line for a more accurate" \
#         #      " measure. This is known as the <strong>least squares <em>h-</em>rate</strong> (Burrell, 2007)."
#         # p4 = "Another similar measure, the <strong>time-scaled <em>h-</em>index</strong> (Mannella and Rossi 2013) " \
#         #      "scales " + hstr + " by the square-root of the academic age."
#         outfile.write("  <body>\n")
#         outfile.write("    <h1>Basic Data</h1>\n")
#         outfile.write("    <h2>Description</h2>\n")
#         write_paragraph(outfile, p1)
#         # write_paragraph(outfile, m_equation)
#         write_paragraph(outfile, p2)
#         # write_paragraph(outfile, p3)
#         # outfile.write("   <p class=\"caption\" style=\"font-style: italic; font-size: 0.75em; text-align: center\">"
#         #               "The points represent the <em>h-</em>index at the end of each year. "
#         #               "The simple <em>h-</em>rate is the slope of the line passing from the origin through the final "
#         #               "point. The least-squares estimate is based on the linear regression of all points, "
#         #               "with the intercept forced through the origin.</p>\n")
#         #
#         # write_paragraph(outfile, p4)
#         # write_paragraph(outfile, hts_equation)
#         outfile.write("    <h2>History</h2>\n")
#         outfile.write("   <div id=\"impact_chart0_div\"></div>\n")
#         outfile.write("   <div id=\"impact_chart1_div\"></div>\n")
#         outfile.write("   <div id=\"impact_chart2_div\"></div>\n")
#         outfile.write("   <div id=\"impact_chart3_div\"></div>\n")
#         outfile.write("   <div id=\"impact_chart4_div\"></div>\n")
#         outfile.write("  </body>\n")
#         outfile.write("</html>\n")
#
#
# def write_webpages(date_list: list, metric_list: list, inc_self: bool) -> None:
#     webout_basic_data(date_list, metric_list)
#     webout_h_rate(date_list, metric_list)


# -----------------------------------------------------
# Google Scholar import functions
# -----------------------------------------------------
# def get_webpage(url: str, encoding: str) -> str:
#     """
#     function to fetch the webpage specifed by url and
#     return a single string containing the contents of the page
#     """
#     webpage = urllib.request.urlopen(url)
#     page = webpage.read()
#     page = page.decode(encoding, "ignore")
#     return page
#
#
# def trim_header(page: str) -> str:
#     """
#     This function removes the header (including CSS and scripts) from
#     the webpage, possibly increasing search efficiency a little
#     """
#     return page[page.find("<body>"):]
#
#
# def find_scholar_name(page: str) -> str:
#     """
#     Find the name of the scholar from the Google Scholar profile
#     """
#     name_tag = "<div id=\"gsc_prf_in\">"
#     x = page.find(name_tag)
#     name = page[x+len(name_tag):]
#     name = name[:name.find("<")]
#     return name
#
#
# def update_author_list(paper: Article) -> str:
#     """
#     This function tries to update the author list when it is abbreviated on
#     the primary profile page
#     """
#     author_tag = "<div class=\"gsc_field\">Authors</div><div class=\"gsc_value\">"
#     site = "https://scholar.google.com" + paper.googleScholarURL
#     page = get_webpage(site, "utf-8")
#     page = trim_header(page)
#     x = page.find(author_tag)
#     tstr = page[x+len(author_tag):]
#     return tstr[:tstr.find("</div>")]
#
#
# def standardize_author(instr: str) -> str:
#     """
#     Standardize the name format to all uppecase, with just a single
#     initial (no periods, middle names) and last name, e.g., M ROSENBERG
#     """
#     names = instr.strip().split(" ")
#     standard = names[0][0]
#     # standard = ''
#     # for n in names[:len(names)-1]:
#     #    standard += n.strip()[0]
#     standard += " " + names[len(names)-1]
#     return standard.upper()
#
#
# def clean_authors(article: Article, author_str: str) -> None:
#     if author_str.find("...") > -1:
#         author_str = update_author_list(article)
#     if "," in author_str:
#         tmp_list = author_str.split(",")
#     else:
#         tmp_list = [author_str]
#     article.authors = len(tmp_list)
#     for a in tmp_list:
#         article.authorList.append(standardize_author(a))
#
#
# def detect_author_order(article: Article, name: str) -> None:
#     x = article.authorList.index(name)
#     if x == -1:
#         x = 0
#     article.author_rank = x + 1
#
#
# def find_gs_articles(page: str) -> list:
#     article_tag = "<td class=\"gsc_a_t\">"
#     a_list = []
#     x = page.find(article_tag)
#     while x > -1:
#         page = page[x+len(article_tag):]
#         y = page.find("</tr>")
#         pstr = page[:y]
#         page = page[y:]
#         new_article = Article()
#
#         # Link to Scholar paper page
#         y = pstr.find("href")
#         tstr = pstr[y+6:]
#         tstr = tstr[:tstr.find("\"")]
#         new_article.googleScholarURL = tstr.replace("&amp;", "&")
#
#         # Title
#         tstr = pstr[pstr.find("gsc_a_at")+10:]
#         tstr = tstr[:tstr.find("</a>")]
#         new_article.title = tstr
#
#         # Authors
#         tstr = pstr[pstr.find("gs_gray")+9:]
#         tstr = tstr[:tstr.find("</div>")]
#         clean_authors(new_article, tstr)
#
#         # Year
#         y = pstr.find("gs_oph")
#         if y == -1:
#             tstr = pstr[pstr.find("gsc_a_h")+9:]
#         else:
#             tstr = pstr[y+10:]
#         tstr = tstr[:tstr.find("</span>")]
#         new_article.year = int(tstr)
#
#         # Citations
#         tstr = pstr[pstr.find("href", pstr.find("href")+1)+6:]
#         new_article.citationURL = tstr[:tstr.find("\"")].replace("&amp;", "&")
#         tstr = tstr[tstr.find("gsc_a_ac")+10:]
#         tmpcnt = tstr[:tstr.find("</a>")]
#         if tmpcnt == "&nbsp;":
#             tmpcnt = "0"
#         new_article.citations = [int(tmpcnt)]
#
#         a_list.append(new_article)
#         x = page.find(article_tag)
#     return a_list
#
#
# def get_citing_article_info(article: Article) -> None:
#     site = article.citationURL
#     print(site)
#     site = "http://scholar.google.com/scholar?cites=12480068626253116047,8651933093376463528"
#     page = get_webpage(site, "utf-8")
#     page = trim_header(page)
#     article_tag = "<h3 class=\"gs_rt\">"
#     # alist = []
#     x = page.find(article_tag)
#     while x > -1:
#         # new_cite = CitingArticle()
#         y = page.find("<h3", page.find("<h3")+1)
#         pstr = page[:y]
#         page = page[y:]
#         tstr = pstr[pstr.find("<div class=\"gs_a\">")+18:]
#         tstr = tstr[:tstr.find(" - ")]
#         print(tstr)
#         x = page.find(article_tag)

            
# -----------------------------------------------------
# fetch data from Google Scholar
# -----------------------------------------------------
# def get_data_from_google_scholar() -> Tuple[list, list]:
#     # user input
#     default_value = "exyen9EAAAAJ"
#     in_code = input("Google Scholar ID number (example: " + default_value + "): ")
#     if in_code == "":
#         in_code = default_value
#     max_papers = "1000"  # assume no one has published more than 1000 papers
#     site = "https://scholar.google.com/citations?hl=en&pagesize=" + max_papers + "&user=" + in_code
#     page = get_webpage(site, "utf-8")
#     page = trim_header(page)
#     scholar_name = find_scholar_name(page)
#     standard_name = standardize_author(scholar_name)
#     print("Impact factors for " + scholar_name)
#     article_list = find_gs_articles(page)
#     for a in article_list:
#         detect_author_order(a, standard_name)
#     date_list = [datetime.datetime.now()]
#     print("Found", len(article_list), "publications")
#     # checking citing articles
#     # for a in article_list:
#     #    getCitingArticleInfo(a)
#     return date_list, article_list


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
    # print("Personal Impact Factor Calculator")
    # print()
    # print("Source of data:")
    # print(" (1) Pre-determined data files")
    # print(" (2) Retrieve data from Google Scholar")
    # valid_choice = ("1", "2", "")
    # data_choice = "x"
    # while data_choice not in valid_choice:
    #     data_choice = input("Enter 1 or 2 (default = 1): ")
    # print()
    #
    # if data_choice != "2":  # temp
    #     self_str = input("Include self-citation measures? (y/n) (default = y) ")
    #     if (self_str.strip() == "") or (self_str.strip().lower() == "y"):
    #         inc_self = True
    #     else:
    #         inc_self = False
    #     print()
    # else:
    #     inc_self = False
    #
    # date_list, article_list = get_data_from_files(inc_self)
    # if data_choice == "1" or data_choice == "":
    #     date_list, article_list = get_data_from_files(inc_self)
    # else:
    #     date_list, article_list = get_data_from_google_scholar()
    #
    # out_name = input("Name of output file (default = \"impactfactors.txt\"): ")
    # if out_name.strip() == "":
    #     out_name = "impactfactors.txt"
    # print()
    #
    # webstr = input("Create webpages? (y/n) (deafult = n) ")
    # # webstr = input("Create webpages? (y/n) (deafult = y) ")
    # # if (webstr.strip() == "") or (webstr.strip().lower() == "y"):
    # if webstr.strip().lower() == "y":
    #     do_web = True
    # else:
    #     do_web = False

    print("Personal Impact Factor Calculator")
    print()

    self_str = input("Include self-citation measures? (y/n) (default = y) ")
    if (self_str.strip() == "") or (self_str.strip().lower() == "y"):
        inc_self = True
    else:
        inc_self = False
    print()

    date_list, article_list = get_data_from_files(inc_self)

    out_name = input("Name of output file (default = \"impactfactors.txt\"): ")
    if out_name.strip() == "":
        out_name = "impactfactors.txt"
    print()

    # calculate metrics for every year
    yearly_metrics_list = []
    for y in range(len(date_list)):
        m = calculate_metrics(y, date_list, article_list, inc_self)
        yearly_metrics_list.append(m)
        m.parent_list = yearly_metrics_list

    # output
    write_output(out_name, date_list, yearly_metrics_list, inc_self)
    print("Finished")


if __name__ == "__main__":
    main()
