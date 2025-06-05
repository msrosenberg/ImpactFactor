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
import re

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
                    line = line[line.find("\t")+1:]
                tmp_list = line.split("\t")
                for d in tmp_list:
                    date_list.append(string_to_date(d))
            # read data
            elif line != '':
                new_article = Article()
                article_list.append(new_article)
                tstr = line[:line.find("\t")]
                line = line[line.find("\t")+1:]
                new_article.year = int(tstr)
                tstr = line[:line.find("\t")]
                line = line[line.find("\t")+1:]
                new_article.authors = int(tstr)
                tstr = line[:line.find("\t")]
                line = line[line.find("\t")+1:]

                new_article.author_rank = int(tstr)
                tstr = line[:line.find("\t")]
                line = line[line.find("\t")+1:]

                new_article.title = tstr
                cite_list = line.split("\t")
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
                    line = line[line.find("\t") + 1:]
                    # skip authors
                    line = line[line.find("\t") + 1:]
                    # skip author rank
                    line = line[line.find("\t") + 1:]
                    # skip title
                    line = line[line.find("\t") + 1:]
                    cite_list = line.split("\t")
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
    if cname != "":
        read_self_citation_file(cname, True)


# -----------------------------------------------------
# Main Calculation Loop
# -----------------------------------------------------
def calculate_metrics(y: int, date_list: list, article_list: list, inc_self: bool,
                      inc_coauth: bool) -> Impact_Defs.MetricSet:
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
    metrics.self_citations = [0 for _ in range(n)]
    metrics.coauthor_citations = [0 for _ in range(n)]

    i = -1
    for article in metrics.publications:
        i += 1
        metrics.citations[i] = article.citations[y]
        if inc_self:
            metrics.self_citations[i] = article.self_cites[y]
        if inc_coauth:
            metrics.coauthor_citations[i] = article.coauthor_cites[y]

    metrics.calculate_ranks()
    return metrics


# -----------------------------------------------------
# output a table of all results
# -----------------------------------------------------
def write_output(fname: str, date_list: list, yearly_metrics_list: list, inc_self: bool, inc_coauth: bool) -> None:
    with open(fname, "w", encoding="utf-8") as outfile:
        # write header of dates
        outfile.write("Date")
        for date in date_list:
            outfile.write("\t" + date_to_string(date))
        outfile.write("\n")

        # write a row for each metric type, with columns representing years
        base_metric_list = yearly_metrics_list[0]
        for m in base_metric_list.metric_names:
            tmp_metric = base_metric_list.metrics[m]
            if tmp_metric.is_self and not inc_self:
                pass  # skip self-citation metrics
            elif tmp_metric.is_coauthor and not inc_coauth:
                pass  # skip coauthor-citation metrics
            else:
                outfile.write(tmp_metric.full_name)  # name of metric
                for metric_list in yearly_metrics_list:
                    outfile.write("\t" + str(metric_list.metrics[m]))
                outfile.write("\n")


# -----------------------------------------------------
# Output results as set of webpages
# -----------------------------------------------------
def encode_name(name: str) -> str:
    name = name.replace(" ", "_")
    name = name.replace("-", "_")
    name = name.replace("/", "_")
    name = name.replace("(", "")
    name = name.replace(")", "")
    name = name.replace(".", "_")
    name = name.replace("%", "")
    return name


def strip_html(html_str: str) -> str:
    """
    remove any stray html tags from string
    """
    regex = r"<.+?>"
    return re.sub(regex, "", html_str)


def html_output_introduction(outfile, inc_self: bool = True, inc_coauth: bool = True):
    outfile.write("   <h2>Publication and Citation-based Impact</h2>")
    outfile.write("   <p>I have been collecting data on citations of my own work for a number of years and once "
                  "wrote a <a href=\"https://peerj.com/preprints/477/\">guide to the concepts for "
                  "biologists</a> (rather than for those better versed in bibliometrics and scientometrics) "
                  "(put on <em>PeerJ Preprint Server,</em> 2014-08-26). I have expanded the collection of metrics "
                  "beyond those described in the paper and have now created a separate webpage "
                  "for every metric, including a basic explanation, a worked example (in many cases), and a "
                  "year-by-year history of that metric based on my own publication record.</p>\n")
    outfile.write("   <p>The code for calculating all of these metrics can be found on "
                  "<a href=\"https://github.com/msrosenberg/ImpactFactor\"><span class=\"fab fa-github\">"
                  "</span> Github</a>.</p>\n")
    now = datetime.datetime.now()
    outfile.write(f"   <p>Citation data used for calculating all examples extracted from Google Scholar "
                  f"on {now.strftime("%Y-%m-%d")}.</p>\n")

    if not inc_self:
        outfile.write("  <p style=\"font-style: italic\">Note: metrics which account for "
                      "self- and coauthor-citation are not currently included in the descriptions below because the "
                      "current data source makes it difficult to track these accurately.</p>")
    # elif not inc_coauth:
    #     outfile.write("  <p style=\"font-style: italic\">Note: metrics which account for "
    #                   "coauthor-citation are not currently included in the descriptions below because the "
    #                   "current data source makes it difficult to track these accurately.</p>")

    outfile.write("      <h3>Common Symbols and Definitions</h3>\n")
    outfile.write("        <ul>\n")
    outfile.write("          <li><em>P</em> &mdash; The total number of publications of an author. Unless "
                  "otherwise specified, publications are in rank order from 1&hellip;<em>P,</em> with 1 having "
                  "the most citations and <em>P</em> the fewest.</li>\n")
    outfile.write("          <li><em>C<sub>i</sub></em> &mdash; The number of citations for the "
                  "<em>i</em><sup>th</sup> publication.</li>\n")
    outfile.write("          <li><em>C<sup>x</sup></em> &mdash; The sum of citations for the top <em>x</em> "
                  "publications, " + r"\(C^x=\sum\limits_{i=1}^{x}{C_i}\)" + ".</li>\n")
    outfile.write("          <li><em>A<sub>i</sub></em> &mdash; The number of authors of the "
                  "<em>i</em><sup>th</sup> publication.</li>\n")
    outfile.write("          <li><em>a<sub>i</sub></em> &mdash; The ordered position of the focal author among "
                  "the full author list of the <em>i</em><sup>th</sup> publication, it\'s value can range from "
                  "1 to <em>A<sub>i</sub>.</em></li>\n")
    outfile.write("          <li><em>Y<sub>i</sub></em> &mdash; The year of the "
                  "<em>i</em><sup>th</sup> publication.</li>\n")
    outfile.write("          <li><em>Y</em><sub>0</sub></em> &mdash; The year of the "
                  "author\'s first publication, " + r"\(Y_0=\min\left(Y_i\right)\)" + ".</li>\n")
    outfile.write('          <li>academic age &mdash; The number of years since an author\'s first publication. '
                  'If <em>Y</em> is the current year (or year of interest), the academic age of the author is '
                  r"\(Y-Y_0+1\)" + '.</li>\n')
    outfile.write("        </ul>\n")


def create_name_links(metric_names, metric_base_data, inc_self, inc_coauth):
    name_links = {}
    for name in metric_names:
        metric = metric_base_data.metrics[name]
        if metric.is_self and not inc_self:
            pass  # skip self-citation metrics
        elif metric.is_coauthor and not inc_coauth:
            pass  # skip self-citation metrics
        else:
            name_links[metric.full_name] = [metric.html_name, encode_name(name)]
            for n in metric.synonyms:
                name_links[strip_html(n)] = [n, encode_name(name)]
    return name_links


def format_description(instr: str, metric_data: Impact_Defs.MetricSet, single_page: bool = False) -> str:
    search_str = r"__(?P<xref>.+?)__"
    # for every xref tagged in the string
    for match in re.finditer(search_str, instr):
        name = match.group("xref")
        metric = metric_data.metrics[name]
        if single_page:
            prefix = "#"
            suffix = ""
        else:
            prefix = "impact_"
            suffix = ".html"
        replace_str = f'<a href="{prefix}{encode_name(name)}{suffix}">{metric.html_name}</a>'
        # replace_str = "<a href=\"" + prefix + encode_name(name) + suffix + "\">" + metric.html_name + "</a>"
        instr = re.sub(search_str, replace_str, instr, count=1)
    return instr


def create_metric_table(outfile, metric_base_data, metric_names, inc_coauth: bool, inc_self: bool,
                        is_single: bool = True):
    # new and temp
    outfile.write("    <hr/>\n")
    outfile.write("    <div>\n")
    outfile.write('      <table class="property_table">\n')
    outfile.write("       <thead>\n")
    outfile.write("        <tr>\n")
    outfile.write('          <th class="blank toph"></th>\n')
    for m_type in Impact_Defs.PROPERTY_TYPES:
        nc = len(Impact_Defs.PROPERTY_DICT[m_type])
        outfile.write(f'          <th class="toph" colspan="{nc}" style="width: {nc*40}px">{m_type}</th>\n')
    outfile.write("        </tr>\n")
    outfile.write("        <tr>\n")
    outfile.write("          <th>Metric Name</th>\n")
    for m_type in Impact_Defs.PROPERTY_TYPES:
        for p in Impact_Defs.PROPERTY_DICT[m_type]:
            outfile.write(f'        <th><div class="rot_1"><div class="rot_2">{p}</div></div></th>\n')
    outfile.write("        </tr>\n")
    outfile.write("       </thead>\n")
    outfile.write("       <tbody>\n")
    tmp_names = [[metric_base_data.metrics[x].full_name.lower(), x] for x in metric_names]
    if is_single:
        prefix = "#"
        suffix = ""
    else:
        prefix = "impact_"
        suffix = ".html"
    for full_name, name in sorted(tmp_names):
        metric = metric_base_data.metrics[name]
        if metric.is_coauthor and not inc_coauth:
            pass
        elif metric.is_self and not inc_self:
            pass
        else:
            outfile.write("        <tr>\n")
            outfile.write(f'          <td class="first_col"><a href="{prefix}{encode_name(metric.name)}{suffix}">'
                          f'{metric.html_name}</a></td>\n')
            for m_type in Impact_Defs.PROPERTY_TYPES:
                for p in Impact_Defs.PROPERTY_DICT[m_type]:
                    if metric.properties[p]:
                        v = "⚫"
                    else:
                        v = ""
                    outfile.write(f"        <td>{v}</td>\n")
            outfile.write("        </tr>\n")
    outfile.write("       </tbody>\n")
    outfile.write("      </table>\n")
    outfile.write("    </div>\n")


def create_single_html_output(yearly_metrics_list: list, inc_self: bool, inc_coauth: bool) -> None:
    with open("webout/impact_factors.html", "w", encoding="utf-8") as outfile:
        outfile.write("<!DOCTYPE HTML>\n")
        outfile.write('<html lang="en">\n')
        outfile.write("  <head>\n")
        outfile.write('    <meta charset="utf-8" />\n')
        outfile.write('    <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n')
        outfile.write("    <title>Impact Factors</title>\n")
        outfile.write('    <meta name="description" content="Impact factor calculations and descriptions" />\n')
        outfile.write('    <link rel="author" href="mailto:msr@asu.edu" />\n')
        outfile.write('    <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.0/MathJax.js?'
                      'config=TeX-MML-AM_CHTML"></script>\n')
        outfile.write('    <link rel="stylesheet" href="impact.css" />\n')

        # graph data
        outfile.write('    <script type="text/javascript" src="https://www.google.com/jsapi"></script>\n')
        outfile.write('    <script type="text/javascript">\n')
        outfile.write('      google.load("visualization", "1", {packages:["corechart"]});\n')
        outfile.write("      google.setOnLoadCallback(drawChart);\n")
        outfile.write("      function drawChart() {\n")
        metric_base_data = yearly_metrics_list[4]  # use data from the 5th year for examples
        metric_names = metric_base_data.metric_names
        for name in metric_names:
            metric = metric_base_data.metrics[name]
            if metric.is_self and not inc_self:
                pass  # skip self-citation metrics
            elif metric.is_coauthor and not inc_coauth:
                pass  # skip self-citation metrics
            elif metric.graph_type is not None:
                enc_name = encode_name(name)
                outfile.write(f"        var data_{enc_name} = google.visualization.arrayToDataTable([\n")
                if metric.graph_type == Impact_Defs.LINE_CHART:
                    outfile.write(f"           ['Year', '{metric.symbol}'],\n")
                    for metric_set in yearly_metrics_list:
                        if metric_set.metrics[name].value == "n/a":
                            v = "null"
                        else:
                            v = metric_set.metrics[name].value
                        outfile.write(f"           ['{metric_set.year()}', {v}],\n")
                    outfile.write("		]);\n")
                    outfile.write("\n")
                    outfile.write(f"        var options_{enc_name} = {{\n")
                    outfile.write("		     legend: {position: 'none'},\n")
                    outfile.write("		     hAxis: {slantedText: true},\n")
                    outfile.write("        };\n")
                if metric.graph_type == Impact_Defs.TWO_LINE_CHART:
                    s1 = "recI"
                    s2 = "recP"
                    outfile.write(f"           ['Year', '{s1}', '{s2}'],\n")
                    for metric_set in yearly_metrics_list:
                        if metric_set.metrics[name].value == "n/a":
                            v = "null"
                        else:
                            v = metric_set.metrics[name].value
                            v1 = v[0]
                            v2 = v[1]
                        outfile.write(f"           ['{metric_set.year()}', {v1}, {v2}],\n")
                    outfile.write("		]);\n")
                    outfile.write("\n")
                    outfile.write(f"        var options_{enc_name} = {{\n")
                    outfile.write("		     hAxis: {slantedText: true},\n")
                    outfile.write("        };\n")
                elif metric.graph_type == Impact_Defs.MULTILINE_CHART_LEFT:
                    # figure out how many values will be on the x-axis
                    maxx = 0
                    for metric_set in yearly_metrics_list:
                        maxx = max(maxx, len(metric_set.metrics[name].value))
                    # write header
                    outstr = "           [\'i\'"
                    for metric_set in yearly_metrics_list:
                        outstr += f", '{metric_set.year()}'"
                    outstr += "],\n"
                    outfile.write(outstr)
                    for x in range(maxx):
                        outstr = f"           ['{x+1}'"
                        for metric_set in yearly_metrics_list:
                            vlist = metric_set.metrics[name].value
                            if x >= len(vlist):
                                v = "null"
                            else:
                                v = vlist[x]
                            outstr += f", {v}"
                        outstr += "],\n"
                        outfile.write(outstr)
                    outfile.write("		]);\n")
                    outfile.write("\n")
                    outfile.write(f"        var options_{enc_name} = {{\n")
                    outfile.write("		     hAxis: {slantedText: true},\n")
                    outfile.write("        };\n")
                elif metric.graph_type == Impact_Defs.MULTILINE_CHART_CENTER:
                    # figure out how many values will be on the x-axis
                    maxx = 0
                    for metric_set in yearly_metrics_list:
                        maxx = max(maxx, len(metric_set.metrics[name].value))
                    # write header
                    outstr = "           [\'i\'"
                    for metric_set in yearly_metrics_list:
                        outstr += f", '{metric_set.year()}'"
                    outstr += "],\n"
                    outfile.write(outstr)
                    d = maxx // 2
                    for x in range(-d, d+1):
                        outstr = f"           ['{x}'"
                        for metric_set in yearly_metrics_list:
                            vlist = metric_set.metrics[name].value
                            vl = len(vlist)
                            if (x + vl // 2 < 0) or (x + vl // 2 >= vl):
                                v = "null"
                            else:
                                v = vlist[x + vl // 2]
                            outstr += f", {v}"
                        outstr += "],\n"
                        outfile.write(outstr)
                    outfile.write("		]);\n")
                    outfile.write("\n")
                    outfile.write(f"        var options_{enc_name} = {{\n")
                    outfile.write("		     hAxis: {slantedText: true},\n")
                    outfile.write("        };\n")
                elif metric.graph_type == Impact_Defs.LINE_CHART_COMBINE:
                    outfile.write(f"           ['Year', '{metric.symbol}'],\n")
                    for metric_set in yearly_metrics_list:
                        t = metric_set.metrics[name].value
                        v = t[0] + t[1]/10
                        outfile.write(f"           ['{metric_set.year()}', {v}],\n")
                    outfile.write("		]);\n")
                    outfile.write("\n")
                    outfile.write(f"        var options_{enc_name} = {{\n")
                    outfile.write("		     legend: {position: 'none'},\n")
                    outfile.write("		     hAxis: {slantedText: true},\n")
                    outfile.write("        };\n")
                outfile.write("\n")
                outfile.write(f"        var chart_{enc_name} = new google.visualization."
                              f"LineChart(document.getElementById('chart_{enc_name}_div'));\n")
                outfile.write(f"        chart_{enc_name}.draw(data_{enc_name}, options_{enc_name});\n")
                outfile.write("\n")
            # plots for descriptions
            for graph in metric.description_graphs:
                for outline in graph.data(metric_base_data):
                    outfile.write(outline)
        outfile.write("		}\n")
        outfile.write("    </script>\n")

        outfile.write("  </head>\n")
        outfile.write("  <body>\n")
        metric_names = metric_base_data.metric_names
        outfile.write("    <div>\n")
        html_output_introduction(outfile, inc_self, inc_coauth)

        # output index of names
        name_links = create_name_links(metric_names, metric_base_data, inc_self, inc_coauth)
        outfile.write("      <h2>Index</h2>\n")
        outfile.write("      <ul class=\"index_list\">\n")
        # need to sort by lowercase, but need to maintain uppercase to allow distinction of some metric names
        index_list = [[i.lower(), i] for i in list(name_links.keys())]
        index_list.sort()
        for i in index_list:
            name = name_links[i[1]]
            outfile.write(f'        <li><a href="#{name[1]}">{name[0]}</a></li>\n')
        outfile.write("      </ul>\n")
        outfile.write("    </div>\n")

        create_metric_table(outfile, metric_base_data, metric_names, inc_coauth, inc_self)

        # output a section for every metric
        for name in metric_names:
            metric = metric_base_data.metrics[name]
            if metric.is_self and not inc_self:
                pass  # skip self-citation metrics
            elif metric.is_coauthor and not inc_coauth:
                pass  # skip self-citation metrics
            else:
                outfile.write(f'    <div id="{encode_name(name)}" class="metric_container">\n')
                outfile.write(f'      <h2>{metric.html_name}</h2>\n')
                # outfile.write("    <div id=\"" + encode_name(name) + "\" class=\"metric_container\">\n")
                # outfile.write("      <h2>" + metric.html_name + "</h2>\n")
                outfile.write("      <h3>Properties</h3>\n")
                outfile.write("        <ul>\n")
                for m_type in Impact_Defs.PROPERTY_TYPES:
                    outlist = []
                    for p in Impact_Defs.PROPERTY_DICT[m_type]:
                        if metric.properties[p]:
                            outlist.append(p)
                    if len(outlist) > 0:
                        outfile.write("          <li><strong>{}:</strong> {}</li>\n".format(m_type, ", ".join(outlist)))
                outfile.write("        </ul>\n")
                outfile.write("      <h3>Description</h3>\n")
                outfile.write("      " + format_description(metric.description, metric_base_data, True) + "\n")
                if metric.example is not None:
                    outfile.write("      <h3>Example</h3>\n")
                    outfile.write("      " + metric.example(metric_base_data) + "\n")
                outfile.write("      <h3>History</h3>\n")
                if metric.metric_type == Impact_Defs.INTLIST:
                    outfile.write(f'    <div id="{encode_name(name)}" class="metric_data_container_wide">\n')
                    # outfile.write("    <div id=\"" + encode_name(name) + "\" class=\"metric_data_container_wide\">\n")
                else:
                    outfile.write('      <div class="metric_data_container">\n')
                outfile.write('        <div class="table_container">\n')
                outfile.write('          <table class="impact_table">\n')
                outfile.write("            <tr>")
                outfile.write("<th>Year</th>")
                outfile.write(f"<th>{metric.symbol}</th>")
                outfile.write("</tr>\n")
                for metric_set in yearly_metrics_list:
                    outfile.write("            <tr>")
                    outfile.write(f'<td class="cell_year">{metric_set.year():4d}</td>')
                    outfile.write(f'<td class="cell_value">{str(metric_set.metrics[name])}</td>')
                    outfile.write("</tr>\n")
                outfile.write("          </table>\n")
                outfile.write("        </div>\n")
                if metric.graph_type is not None:
                    outfile.write('        <div class="graph_container">\n')
                    outfile.write(f'          <div id="chart_{encode_name(name)}_div" class="impact_chart"></div>\n')
                outfile.write("        </div>\n")
                outfile.write("      </div>\n")
                outfile.write("    </div>\n")
        # references
        outfile.write('    <div id="references">\n')
        outfile.write("      <h2>References</h2>\n")
        outfile.write("      <ul>\n")
        reflist = metric_base_data.references()
        for r in reflist:
            outfile.write(f"        <li>{r}</li>\n")
        outfile.write("      </ul>\n")
        outfile.write("    </div>\n")

        outfile.write("  </body>\n")
        outfile.write("</html>\n")


def create_set_html_output(yearly_metrics_list: list, inc_self: bool, inc_coauth: bool) -> None:
    with open("webout/impact_pages_html.txt", "w", encoding="utf-8") as outfile:
        # introduction and index
        html_output_introduction(outfile, inc_self, inc_coauth)
        metric_base_data = yearly_metrics_list[4]  # use data from the 5th year for examples
        metric_names = metric_base_data.metric_names
        name_links = create_name_links(metric_names, metric_base_data, inc_self, inc_coauth)
        # need to sort by lowercase, but need to maintain uppercase to allow distinction of some metric names
        outfile.write("      <h3>Index</h3>\n")
        outfile.write('      <ul class="index_list">\n')
        index_list = [[i.lower(), i] for i in list(name_links.keys())]
        index_list.sort()
        for i in index_list:
            name = name_links[i[1]]
            outfile.write(f'        <li><a href="impact_{name[1]}.html">{name[0]}</a></li>\n')
        outfile.write("      </ul>\n")
        # output a page for every metric
        for name in metric_names:
            metric = metric_base_data.metrics[name]

            if metric.is_self and not inc_self:
                pass  # skip self-citation metrics
            elif metric.is_coauthor and not inc_coauth:
                pass  # skip self-citation metrics
            else:
                outfile.write("@@@@\n")
                link = name_links[metric.full_name]
                outfile.write(f"impact_{link[1]}.html\n")

                # output header info for graphs and plots
                if metric.graph_type is not None:
                    enc_name = encode_name(name)
                    outfile.write(f'        var data_{enc_name} = google.visualization.arrayToDataTable([\n')
                    if metric.graph_type == Impact_Defs.LINE_CHART:
                        outfile.write(f"           ['Year', '{metric.symbol}'],\n")
                        for metric_set in yearly_metrics_list:
                            if metric_set.metrics[name].value == "n/a":
                                v = "null"
                            else:
                                v = metric_set.metrics[name].value
                            outfile.write(f"           ['{metric_set.year()}', {v}],\n")
                        outfile.write("		]);\n")
                        outfile.write("\n")
                        outfile.write(f"        var options_{enc_name} = {{\n")
                        outfile.write("		     legend: {position: 'none'},\n")
                        outfile.write("		     hAxis: {slantedText: true},\n")
                        outfile.write("        };\n")
                    elif metric.graph_type == Impact_Defs.MULTILINE_CHART_LEFT:
                        # figure out how many values will be on the x-axis
                        maxx = 0
                        for metric_set in yearly_metrics_list:
                            maxx = max(maxx, len(metric_set.metrics[name].value))
                        # write header
                        outstr = "           ['i'"
                        for metric_set in yearly_metrics_list:
                            outstr += f", '{metric_set.year()}'"
                        outstr += "],\n"
                        outfile.write(outstr)
                        for x in range(maxx):
                            outstr = f"           ['{x + 1}'"
                            for metric_set in yearly_metrics_list:
                                vlist = metric_set.metrics[name].value
                                if x >= len(vlist):
                                    v = "null"
                                else:
                                    v = vlist[x]
                                outstr += f", {v}"
                            outstr += "],\n"
                            outfile.write(outstr)
                        outfile.write("		]);\n")
                        outfile.write("\n")
                        outfile.write(f"        var options_{enc_name} = {{\n")
                        outfile.write("		     hAxis: {slantedText: true},\n")
                        outfile.write("        };\n")
                    elif metric.graph_type == Impact_Defs.MULTILINE_CHART_CENTER:
                        # figure out how many values will be on the x-axis
                        maxx = 0
                        for metric_set in yearly_metrics_list:
                            maxx = max(maxx, len(metric_set.metrics[name].value))
                        # write header
                        outstr = "           ['i'"
                        for metric_set in yearly_metrics_list:
                            outstr += f", '{metric_set.year()}'"
                        outstr += "],\n"
                        outfile.write(outstr)
                        d = maxx // 2
                        for x in range(-d, d + 1):
                            outstr = "           [\'{}\'".format(x)
                            for metric_set in yearly_metrics_list:
                                vlist = metric_set.metrics[name].value
                                vl = len(vlist)
                                if (x + vl // 2 < 0) or (x + vl // 2 >= vl):
                                    v = "null"
                                else:
                                    v = vlist[x + vl // 2]
                                outstr += ", {}".format(v)
                            outstr += "],\n"
                            outfile.write(outstr)
                        outfile.write("		]);\n")
                        outfile.write("\n")
                        outfile.write(f"        var options_{enc_name} = {{\n")
                        outfile.write("		     hAxis: {slantedText: true},\n")
                        outfile.write("        };\n")
                    elif metric.graph_type == Impact_Defs.LINE_CHART_COMBINE:
                        outfile.write(f"           ['Year', '{metric.symbol}'],\n")
                        for metric_set in yearly_metrics_list:
                            t = metric_set.metrics[name].value
                            v = t[0] + t[1] / 10
                            outfile.write(f"           ['{metric_set.year()}', {v}],\n")
                        outfile.write("		]);\n")
                        outfile.write("\n")
                        outfile.write(f"        var options_{enc_name} = {{\n")
                        outfile.write("		     legend: {position: 'none'},\n")
                        outfile.write("		     hAxis: {slantedText: true},\n")
                        outfile.write("        };\n")
                    outfile.write("\n")
                    outfile.write(f"        var chart_{enc_name} = new google.visualization."
                                  f"LineChart(document.getElementById('chart_{enc_name}_div'));\n")
                    outfile.write(f"        chart_{enc_name}.draw(data_{enc_name}, options_{enc_name});\n")
                    outfile.write("\n")
                # plots for descriptions
                for graph in metric.description_graphs:
                    for outline in graph.data(metric_base_data):
                        outfile.write(outline)
                outfile.write("@@\n")
                # output page info
                outfile.write(f'    <div id="{encode_name(name)}" class="metric_container">\n')
                outfile.write(f'      <h2>{metric.html_name}</h2>\n')
                outfile.write("      " + format_description(metric.description, metric_base_data) + "\n")
                if metric.example is not None:
                    outfile.write("      <h3>Example</h3>\n")
                    outfile.write("      " + metric.example(metric_base_data) + "\n")
                outfile.write("      <h3>History</h3>\n")
                if metric.metric_type == Impact_Defs.INTLIST:
                    outfile.write(f'    <div id="{encode_name(name)}" class="metric_data_container_wide">\n')
                else:
                    outfile.write('      <div class="metric_data_container">\n')
                outfile.write('        <div class="table_container">\n')
                outfile.write('          <table class="impact_table">\n')
                outfile.write("            <tr>")
                outfile.write("<th>Year</th>")
                outfile.write("<th>" + metric.symbol + "</th>")
                outfile.write("</tr>\n")
                for metric_set in yearly_metrics_list:
                    outfile.write("            <tr>")
                    outfile.write(f'<td class="cell_year">{metric_set.year():4d}</td>')
                    outfile.write(f'<td class="cell_value">{str(metric_set.metrics[name])}</td>')
                    outfile.write("</tr>\n")
                outfile.write("          </table>\n")
                outfile.write("        </div>\n")
                if metric.graph_type is not None:
                    outfile.write('        <div class="graph_container">\n')
                    outfile.write(f'          <div id="chart_{encode_name(name)}_div" class="impact_chart"></div>\n')
                outfile.write("        </div>\n")
                outfile.write("      </div>\n")
                outfile.write("    </div>\n")

                # references
                reflist = sorted(metric.references)
                if len(reflist) > 0:
                    outfile.write('    <div id="references">\n')
                    outfile.write("      <h2>References</h2>\n")
                    outfile.write("      <ul>\n")
                    for r in reflist:
                        outfile.write(f"        <li>{r}</li>\n")
                    outfile.write("      </ul>\n")
                    outfile.write("    </div>\n")


# -----------------------------------------------------
# pre-determined data files
# -----------------------------------------------------
def prompt_file_name(prompt: str, default: str) -> str:
    file_name = input("Name of " + prompt + " (default: \"" + default + "\"): ")
    if file_name.strip() == "":
        file_name = default
    return file_name
    

def get_data_from_files(inc_self: bool, inc_coauth: bool) -> Tuple[list, list]:
    # user input
    in_name = prompt_file_name("citation file", "Citations.txt")
    date_list, article_list = read_data_file(in_name)
    if inc_self:
        self_name = prompt_file_name("self-citation file", "Citations-Self.txt")
        if inc_coauth:
            coauth_name = prompt_file_name("coauthor-citation file", "Citations-Coauthor.txt")
        else:
            coauth_name = ""
        read_self_citation_files(article_list, self_name, coauth_name)
    return date_list, article_list


# -----------------------------------------------------
# main loop
# -----------------------------------------------------
def main():
    print("Personal Impact Factor Calculator")
    print()

    self_str = input("Include self-citation measures? (y/n) (default = y) ")
    if (self_str.strip() == "") or (self_str.strip().lower() == "y"):
        inc_self = True
        # self_str = input("Include coauthor-citation measures? (y/n) (default = y) ")
        # if (self_str.strip() == "") or (self_str.strip().lower() == "y"):
        self_str = input("Include coauthor-citation measures? (y/n) (default = n) ")
        if self_str.strip().lower() == "y":
            inc_coauth = True
        else:
            inc_coauth = False
        print()
    else:
        inc_self = False
        inc_coauth = False
    print()

    date_list, article_list = get_data_from_files(inc_self, inc_coauth)

    out_name = input("Name of output file (default = \"impactfactors.txt\"): ")
    if out_name.strip() == "":
        out_name = "impactfactors.txt"
    print()

    webstr = input("Create html output? (y/n) (deafult = y) ")
    if (webstr.strip() == "") or (webstr.strip().lower() == "y"):
        do_web = True
    else:
        do_web = False

    # calculate metrics for every year
    yearly_metrics_list = []
    for y in range(len(date_list)):
        m = calculate_metrics(y, date_list, article_list, inc_self, inc_coauth)
        yearly_metrics_list.append(m)
        m.parent_list = yearly_metrics_list

    # output
    write_output(out_name, date_list, yearly_metrics_list, inc_self, inc_coauth)
    if do_web:
        create_single_html_output(yearly_metrics_list, inc_self, inc_coauth)
        create_set_html_output(yearly_metrics_list, inc_self, inc_coauth)

    print("Finished")


if __name__ == "__main__":
    main()
