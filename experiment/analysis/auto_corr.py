import dataset_helper as dsh
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse

def plot_autocorrelation(resampled_devices):
    ''' Plot autocorrelation
        The autocorrelation is calculated for a lag from zero to 20
        For each device a differnet subplot is used 
    '''
    fig, ax = plt.subplots(len(resampled_devices), figsize=(10, 20))
    for i, name in enumerate(resampled_devices):
        one_device = resampled_devices[name]
        autocorr = [one_device["freq_offset"].autocorr(x) for x in range(21)] 
        x = range(len(autocorr))
        ax[i].scatter(x, autocorr, label=name)
        ax[i].legend()
        ax[i].set_ylim([-1.0, 1.0])
        ax[i].set_xlabel('lag')
        ax[i].set_ylabel('autocorrelation')
        
    
    #Export plot as pdf
    with PdfPages(r'figures/autocorr_plot.pdf') as export_pdf:
        export_pdf.savefig()

def plot_connected(resampled_devices):
    ''' Plot resampled data point as connected lines
    '''
    fig, ax = plt.subplots()
    for name in resampled_devices:
        resampled_devices[name]["freq_offset"].plot(label=name, ax=ax)
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Frequency offset')
        ax.legend()
    fig.tight_layout()
    
    #Export plot as pdf
    with PdfPages(r'figures/line_plot.pdf') as export_pdf:
        export_pdf.savefig()


def parse_time_period(argument):
    ''' Parse command line argument
    '''
    time_period = 'D'
    if argument == "hour":
        time_period = 'H'
    elif argument == "min":
        time_period = 'T'
    elif argument == 'sec':
        time_period = 'S'
    else:
        print("Unknown time period: Use [sec|min|day]")

    return time_period

        

parser = argparse.ArgumentParser(description="Plot basic information about Dataset")
parser.add_argument('--table', type=str, help="Name of the database Table")
parser.add_argument('--time_period', type=str, help="Time period for which the data should be resampled [sec | min | hour | day]")
parser.add_argument('--remove_ten_min', action='store_true', help="The first 10 minutes of each day are removed from the recording")
args = parser.parse_args()

if __name__ == '__main__':
    time_period = parse_time_period(args.time_period)
    if args.table == None:
        df = dsh.load_data()
    else:
        df = dsh.load_data(table = args.table)
    if args.remove_ten_min:
        df = dsh.remove_ten_min(df)
    mac_groups = dsh.group_by_mac(df)
    
    resampled_devices = dsh.resample(mac_groups, time_period)
    plot_autocorrelation(resampled_devices)
    plot_connected(resampled_devices)
    plt.show()