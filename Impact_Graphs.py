"""
create graphs for output, rather than relying on Google Charts
"""

import matplotlib.pyplot as plt
import mpltern
import numpy
from Impact_Common import encode_name

FIGSIZE = [6, 4]  # default figure size
WIDESIZE = [8, 4]  # for multiline with legends


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
    faxes.set_ylabel(base_metric.axes_name)
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
    faxes.set_ylabel(base_metric.axes_name)
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
    faxes.set_ylabel(base_metric.axes_name)
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
    faxes.set_ylabel(base_metric.axes_name)
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
    faxes.set_ylabel(base_metric.axes_name)
    plt.tight_layout()
    save_figure(plt, name)
    plt.close("all")


def draw_graph_ternary_chart(name: str, metric_list: list):
    base_metric = metric_list[0].metrics[name]
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
