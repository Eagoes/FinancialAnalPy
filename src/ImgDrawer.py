import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.ticker import MultipleLocator
from io import BytesIO


def align_yaxis(ax1, v1, ax2, v2):
    """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
    _, y1 = ax1.transData.transform((0, v1))
    _, y2 = ax2.transData.transform((0, v2))
    adjust_yaxis(ax2,(y1-y2)/2,v2)
    adjust_yaxis(ax1,(y2-y1)/2,v1)

def adjust_yaxis(ax,ydif,v):
    """shift axis ax by ydiff, maintaining point v at the same location"""
    inv = ax.transData.inverted()
    _, dy = inv.transform((0, 0)) - inv.transform((0, ydif))
    miny, maxy = ax.get_ylim()
    miny, maxy = miny - v, maxy - v
    if -miny>maxy or (-miny==maxy and dy > 0):
        nminy = miny
        nmaxy = miny*(maxy+dy)/(miny+dy)
    else:
        nmaxy = maxy
        nminy = maxy*(miny+dy)/(maxy+dy)
    ax.set_ylim(nminy+v, nmaxy+v)

def img_draw(category: list,  plot_params: list, use_percent=True):
    """
    the image creation function
    :param category: list, the data of the x axis
    :param plot_params: list, the items are smaller list, each list contains the data of each plot,
    the label of each plot and the type, there will be two types: 1 refers to plot, 2 refers to bar
    :param use_percent: set the y axis using percent format
    :return: the byte stream of the image
    """
    imgdata = BytesIO()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    xLocator = MultipleLocator(1)
    fig, axe = plt.subplots(figsize=(7,4))
    for info in plot_params:
        if info[2] == 1:  # use the plot method
            axe.plot(category, info[0], label=info[1])
        elif info[2] == 2:  # use the bar method
            axe.bar(category, info[0], label=info[1])
    axe.xaxis.set_major_locator(xLocator)

    if use_percent:
        yticks = mtick.PercentFormatter(xmax=1, decimals=0)
        axe.yaxis.set_major_formatter(yticks)

    # box = axe.get_position()
    # axe.set_position([box.x0 - box.width * 0.03, box.y0 + box.height * 0.1,
    #                        box.width, box.height * 0.9])
    # axe.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(plot_params),
    #            fontsize=9, frameon=False)
    axe.legend(loc='best', fontsize=9, frameon=False)

    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    plt.clf()
    plt.cla()
    plt.close()
    return imgdata


def bar_and_plot(category: list, bar_param: list, plot_param:list, use_percent=True):
    """
    the function that draws an image contains a bar axis and a plot axis
    :param category: data of the x axis
    :param bar_param: data of the bar axis, bar title
    :param plot_param: data of the plot axis, plot title
    :return: the byte stream of the image
    """
    imgdata = BytesIO()
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    xLocator = MultipleLocator(1)
    fig, left_axe = plt.subplots(figsize=(7, 4))
    right_axe = left_axe.twinx()
    left_axe.bar(category, bar_param[0], label=bar_param[1], width=0.4)
    right_axe.plot(category, plot_param[0], label=plot_param[1], color='red', linewidth=2)

    # get the plot and the labels to merge them in one legend
    bars, labels = left_axe.get_legend_handles_labels()
    lines, labels2 = right_axe.get_legend_handles_labels()

    # set the tick spacing
    left_axe.xaxis.set_major_locator(xLocator)
    if use_percent:
        yticks = mtick.PercentFormatter(xmax=1, decimals=0)
        right_axe.yaxis.set_major_formatter(yticks)

    # place the legend and the labels
    # box = left_axe.get_position()
    # left_axe.set_position([box.x0 - box.width * 0.03, box.y0 + box.height * 0.1,
    #                   box.width, box.height * 0.9])
    # left_axe.legend(bars + lines, labels + labels2, loc='upper center',
    #                 bbox_to_anchor=(0.5, -0.05), ncol=2, fontsize=9, frameon=False)
    left_axe.legend(bars + lines, labels + labels2, loc='best', fontsize=9, frameon=False)
    left_axe.set_ylabel(bar_param[1])
    right_axe.set_ylabel(plot_param[1])

    # set the horizon line of y=0 and align the y axis
    plt.axhline(0, color='black')
    align_yaxis(left_axe, 0, right_axe, 0)

    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    plt.clf()
    plt.cla()
    plt.close()
    return imgdata

