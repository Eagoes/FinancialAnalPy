import matplotlib.pyplot as plt
from io import BytesIO


def img_draw(title: str, category: list,  plot_params: list):
    """
    the image creation function
    :param title: string, to be the title of the image
    :param category: list, the data of the x axis
    :param plot_params: list, the items are smaller list, each list contains the data of each plot,
    the label of each plot and the type, there will be two types: 1 refers to plot, 2 refers to bar
    :return: the byte stream of the image
    """
    imgdata = BytesIO()
    fig, axe = plt.subplots()
    for info in plot_params:
        if info[2] == 1:  # use the plot method
            axe.plot(category, info[0], label=info[1])
        elif info[2] == 2:  # use the bar method
            axe.bar(category, info[0], label=info[1])

    box = axe.get_position()
    axe.set_position([box.x0, box.y0 + box.height * 0.1,
                      box.width, box.height * 0.9])
    axe.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fontsize=9, frameon=False)
    axe.set_title(title, fontsize=11)

    fig.savefig(imgdata, format='png')
    imgdata.seek(0)
    return imgdata

def bar_and_plot(categoty: list, bar_param: list, plot_param:list):
    """
    the function that draws an image contains a bar axis and a plot axis
    :param categoty: data of the x axis
    :param bar_param: data of the bar axis, bar title
    :param plot_param: data of the plot axis, plot title
    :return: the byte stream of the image
    """
    imgdata = BytesIO()
    fig, left_axe = plt.subplots()
    right_axe = left_axe.twinx()
    left_axe.bar(categoty, bar_param[0], label=bar_param[1])
    right_axe.plot(categoty, plot_param[0], label=plot_param[1])

    box = left_axe.get_position()
    left_axe.set_position([box.x0, box.y0 + box.height * 0.1,
                      box.width, box.height * 0.9])
    left_axe.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), fontsize=9, frameon=False)
    left_axe.ylabel(bar_param[1])
    right_axe.ylabel(plot_param[1])
