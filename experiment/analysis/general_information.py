import dataset_helper as dsh
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse
import numpy as np

def plot_data_points(mac_groups):
    """ Scatter frequency offset against time
        The color indicates the affiliation to a sender mac
    """
    fig, ax = plt.subplots()
    for name, group in mac_groups:
        ax.scatter(group['record_time'], group["freq_offset"], label=name)
    ax.legend(loc=1 )
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Frequency offset")
    fig.tight_layout()
    
    #Export plot as pdf 
    with PdfPages(r'figures/scatter_plot.pdf') as export_pdf:
        export_pdf.savefig()

def plot_deviation(mac_groups):
    """ Plot histogram of frequency offset deviation 
        Each bin in the histogram indicates how many frames are in the given range of frequency offsets
        Normalized by the bins area
    """
    colors = [(1., 0., 0, 0.5), (0., 1., 0., 0.5), (0., 0., 1., 0.5), (1., 1., 0., 0.5)]
    _, ax = plt.subplots()
    index = 0
    for name, group in mac_groups:
        old_count = group["freq_offset"].count()
        #Remove outliers to avoid waist of bins
        group = group[np.abs(group["freq_offset"]-df["freq_offset"].mean()) <= (10*df["freq_offset"].std())]
        print(name, " Deleted: ", old_count - group["freq_offset"].count())
        plt.hist(group["freq_offset"], bins=16, density=1, label=name, color=colors[index])
        index += 1
    ax.legend(loc=1)

    #Export plot as pdf 
    with PdfPages(r'figures/histogram.pdf') as export_pdf:
        export_pdf.savefig()

parser = argparse.ArgumentParser(description="Plot basic information about Dataset")
parser.add_argument('--table', type=str, help="Name of the database Table")
parser.add_argument('--remove_ten_min', action='store_true', help="The first 10 minutes of each day are removed from the recording")

args = parser.parse_args()

if __name__ == '__main__':
    if args.table == None:
        df = dsh.load_data()
    else:
        df = dsh.load_data(table = args.table)
    if args.remove_ten_min:
        df = dsh.remove_ten_min(df)
    mac_groups = dsh.group_by_mac(df)
    plot_data_points(mac_groups)
    plot_deviation(mac_groups)
    print(mac_groups['freq_offset'].describe())

    plt.show()

    

    