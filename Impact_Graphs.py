"""
create graphs for output, rather than relying on Google Charts
"""

import matplotlib.pyplot as plt
import mpltern
import numpy
from Impact_Common import encode_name

FIGSIZE = [6, 4]  # default figure size
WIDESIZE = [8, 4]  # for multiline with legends


class LineData:
    def __init__(self):
        self.x = []
        self.y = []
        self.style = "-"
        self.label = ""


class GeneralData:
    def __init__(self):
        self.x_label = ""
        self.y_label = ""
        self.inc_legend = False
        self.x_max = None
        self.y_max = None


class AnnotationData:
    def __init__(self):
        self.label = ""
        self.pos = None
        self.textpos = None


class PointData:
    def __init__(self):
        self.x = []
        self.y = []
        self.label = ""
        self.edgecolor = "black"
        self.fillcolor = "black"
        self.marker = "o"



# ---- history plotting functions ----

def save_figure(plt, name):
    plt.savefig(f'webout/impact_figs/img_{encode_name(name)}.svg', format="svg", dpi=600)


def draw_graph_line_chart(name: str, metric_list: list):
    base_metric = metric_list[0].metrics[name]
    # get data for line plot
    x = []
    y = []
    for metric_set in metric_list:
        if metric_set.metrics[name].value == "n/a":
            v = numpy.nan
        else:
            v = metric_set.metrics[name].value
        x.append(metric_set.year())
        y.append(v)

    # create plot
    fig, faxes = plt.subplots(figsize=FIGSIZE)
    faxes.plot(x, y)
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.set_xlabel("Year")
    faxes.set_ylabel(base_metric.axis_name)
    plt.tight_layout()
    save_figure(plt, name)
    plt.close("all")


def draw_graph_multiline_left_chart(name: str, metric_list: list):
    base_metric = metric_list[0].metrics[name]
    # figure out how many values will be on the x-axis
    maxx = 0
    for metric_set in metric_list:
        maxx = max(maxx, len(metric_set.metrics[name].value))

    fig, faxes = plt.subplots(figsize=WIDESIZE, layout="constrained")

    # get data
    for metric_set in metric_list:
        y = metric_set.metrics[name].value
        x = [i+1 for i in range(len(y))]
        faxes.plot(x, y, label=f"{metric_set.year()}")

    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.set_ylabel(base_metric.axis_name)
    fig.legend(loc="outside right center", prop={"size": "x-small"}, ncols=2)
    save_figure(plt, name)
    plt.close("all")


def draw_graph_multiline_center_chart(name: str, metric_list: list):
    base_metric = metric_list[0].metrics[name]
    # figure out how many values will be on the x-axis
    maxx = 0
    for metric_set in metric_list:
        maxx = max(maxx, len(metric_set.metrics[name].value))

    fig, faxes = plt.subplots(figsize=WIDESIZE, layout="constrained")

    # get data
    for metric_set in metric_list:
        y = metric_set.metrics[name].value
        n = len(y)
        shift = (n - 1) // 2
        x = [i - shift for i in range(n)]
        faxes.plot(x, y, label=f"{metric_set.year()}")

    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.set_ylabel(base_metric.axis_name)
    fig.legend(loc="outside right center", prop={"size": "x-small"}, ncols=2)
    save_figure(plt, name)
    plt.close("all")


def draw_graph_two_line_chart(name: str, metric_list: list):
    base_metric = metric_list[0].metrics[name]
    # get data for line plot
    x = []
    y1 = []
    y2 = []
    for metric_set in metric_list:
        v = metric_set.metrics[name].value
        x.append(metric_set.year())
        y1.append(v[0])
        y2.append(v[1])

    # create plot
    fig, faxes = plt.subplots(figsize=FIGSIZE)
    faxes.plot(x, y1, label=r"$rec_I$")
    faxes.plot(x, y2, label=r"$rec_P$")
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.set_xlabel("Year")
    faxes.set_ylabel(base_metric.axis_name)
    faxes.legend()
    plt.tight_layout()
    save_figure(plt, name)
    plt.close("all")


def draw_graph_line_combined_chart(name: str, metric_list: list):
    base_metric = metric_list[0].metrics[name]
    # get data for line plot
    x = []
    y = []
    for metric_set in metric_list:
        v = metric_set.metrics[name].value
        x.append(metric_set.year())
        y.append(v[0] + v[1]/10)

    # create plot
    fig, faxes = plt.subplots(figsize=FIGSIZE)
    faxes.plot(x, y)
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    faxes.set_xlabel("Year")
    faxes.set_ylabel(base_metric.axis_name)
    plt.tight_layout()
    save_figure(plt, name)
    plt.close("all")


def draw_graph_ternary_chart(name: str, metric_list: list):
    # base_metric = metric_list[0].metrics[name]
    fig = plt.figure(figsize=FIGSIZE)
    faxes = fig.add_subplot(projection="ternary")
    faxes.grid()
    faxes.set_axisbelow(True)
    # get data
    a, c, m, y = [], [], [], []
    for metric_set in metric_list:
        d = metric_set.metrics[name].value
        a.append(d[0])
        c.append(d[1])
        m.append(d[2])
        y.append(metric_set.year())
    sc = faxes.scatter(a, c, m, c=y)
    faxes.set_tlabel("Author")
    faxes.set_llabel("Collaborator")
    faxes.set_rlabel("Manager")

    cax = faxes.inset_axes([1.05, 0.1, 0.05, 0.9], transform=faxes.transAxes)
    fig.colorbar(sc, cax=cax)

    plt.tight_layout()
    save_figure(plt, name)
    plt.close("all")


# ---- example drawing function ----

def draw_example_figure(graph, metric_base_data):
    fig, faxes = plt.subplots(figsize=FIGSIZE)
    graph_data = graph.data(metric_base_data)
    for data in graph_data:
        if isinstance(data, LineData):
            faxes.plot(data.x, data.y, linestyle=data.style, label=data.label)
        elif isinstance(data, PointData):
            faxes.scatter(data.x, data.y, label=data.label, edgecolors=data.edgecolor, c=data.fillcolor)
        elif isinstance(data, AnnotationData):
            faxes.annotate(data.label, xy=data.pos, xytext=data.textpos, va="center",
                           arrowprops=dict(facecolor="black", shrink=0.1))
        elif isinstance(data, GeneralData):
            faxes.set_xlabel(data.x_label)
            faxes.set_ylabel(data.y_label)
            if data.inc_legend:
                faxes.legend()
            if data.x_max is not None:
                faxes.set_xlim(0, data.x_max)
            if data.y_max is not None:
                faxes.set_ylim(0, data.y_max)

    faxes.set_aspect("equal", adjustable="box")
    faxes.spines["right"].set_visible(False)
    faxes.spines["top"].set_visible(False)
    plt.tight_layout()
    save_figure(plt, graph.name)
    plt.close("all")

