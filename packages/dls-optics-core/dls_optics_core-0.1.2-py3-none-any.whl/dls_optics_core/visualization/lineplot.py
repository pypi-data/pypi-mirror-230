import matplotlib.pyplot as plt
import numpy as np

def plot_lines(datasets, legend=False, showplot=True, xlabel='', ylabel='', title=''):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    for data in datasets:
        ax.plot(data[:, 0], data[:, 1])

    plt.grid(True, which='both')

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if legend:
        # print(legend)
        handles, labels = ax.get_legend_handles_labels()
        # print(handles)
        plt.legend(handles, legend)

    if showplot:
        plt.show()

    return fig, ax

def plot_lines_2up(datasets1, datasets2, legend=False, showplot=True):
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    
    for data in datasets1:
        ax1.plot(data[:, 0], data[:, 1])

    for data in datasets2:
        ax1.plot(data[:, 0], data[:, 1])

    plt.grid(True, which='both')

    if legend:
        plt.legend()

    if showplot:
        plt.show()

    return fig, ax1, ax2