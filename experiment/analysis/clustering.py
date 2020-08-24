import dataset_helper as dsh
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth
from sklearn.metrics import silhouette_score
import numpy as np

def silhouette_method(df, n_samples = 1000):
    """ Estimate number of clusters
        The Function calculates the K-Means algorithm for differnet numbers of clusters
        and returns the best k in tearms of the silhouette_score. The function works on
        a subset with n_samples samples due to computational effort.
    """
    df_subset = df.sample(n=n_samples) if df.shape[0]>n_samples else df
    x = np.array(df_subset['freq_offset']).reshape(-1, 1)
    silhou_score = []
    max_clusters = 20
    for k in range(2, max_clusters+1):
        y_km = (KMeans(n_clusters=k, init='random', n_init=5, max_iter=300, tol=1e-4, random_state=0).fit(x))
        silhou_score.append(silhouette_score(x, y_km.labels_, metric = 'euclidean' )) 
    return 2 + silhou_score.index(max(silhou_score))

def k_means(df, num_clusters):
    """ Cluster DataFrame into num_clusters cluster
        Use K-Means to cluster the data points appropriate to the frequency offset
    """
    y = np.array(df['freq_offset'])

    km = KMeans(n_clusters=num_clusters, init='random', n_init=10, max_iter=300, tol=1e-4, random_state=0)
    y_km = km.fit_predict(y.reshape(-1, 1))
    return y_km

def mean_shift(df):
    """ Clusters DataFrame into clusters
        Since K-Means is well suited for uneven sized clusters
    """
    Y = np.array(df['freq_offset']).reshape(-1, 1)
    bandwidth = estimate_bandwidth(Y, quantile=0.2, n_samples=500)

    ms = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    ms.fit(Y)
    y_km = ms.labels_
    num_clusters = len(np.unique(y_km))
    return y_km, num_clusters

def plot_clustering(df, y_km, label):
    """ Plot the data points 
        The color represents the affiliation to a cluster
    """
    y = np.array(df['freq_offset'])
    x = np.array(df['record_time'])
    _, ax = plt.subplots()
    for i in range(num_clusters): 
        ax.scatter(x[y_km==i], y[y_km==i])
        ax.set_title(label=label)
    
    #Export plot as pdf
    with PdfPages(r'figures/%s.pdf' % label) as export_pdf:
        export_pdf.savefig()
    

def print_error_rate(df, y_km, num_clusters):
    """ Print error rate
        Each cluster is assigned to the device which has send the most frames in the cluster
        Based on the frames in the cluster which are not send by the assigned device a error rate is calculated
    """
    ground_truth = np.array(df['sender_mac'])
    for i in range(num_clusters):
        cluster = ground_truth[y_km==i]
        # Counts occurence of a specific value in cluster 
        unique, counts = np.unique(cluster, return_counts=True)
        occ_counter = dict(zip(unique, counts))
        
        #Note: One device could be associated with multiple clusters
        sum_cluster_frames = len(cluster)
        #The device which is sender of the most frames in the cluster 
        cluster_sender = max(occ_counter, key = occ_counter.get)
        error_rate = (sum_cluster_frames - occ_counter[cluster_sender]) / sum_cluster_frames
        print(occ_counter)
        print("Size of cluster: ", sum_cluster_frames)
        print("Estimated device:", cluster_sender)
        print("Error rate:", error_rate)

def normalize(df, mac_groups, samples_per_device):
    """ Reduce DataFrame
        The DataFrame is reduced, in order to contain only samples_per_device frames per device.
        Can be performed to avoid the impact of the huge difference in the amount of frames per device
    """

    #Check if each device has enough frames
    for _, group in mac_groups:
        if group.shape[0] < samples_per_device:
            print("\nSome dataset to small to get normalized")
            print("Skip normalization")
            return df 

    for _, group in mac_groups:
        to_drop = group.shape[0]-samples_per_device
        df = df.drop(group.sample(n=to_drop).index)
    return df


parser = argparse.ArgumentParser(description="Plot basic information about Dataset")
parser.add_argument('--table', type=str, help="Name of the database Table")
parser.add_argument('--num_cluster', type=int, help="Manually specify number of clusters")
parser.add_argument('--normalize', type=int, help="Use the same amount of samples for each device")
parser.add_argument('--remove_ten_min', action='store_true', help="The first 10 minutes of each day are removed from the recording")


args = parser.parse_args()

if __name__ == '__main__':
    if args.table == None:
        df = dsh.load_data()
    else:
        df = dsh.load_data(table = args.table)
    if args.remove_ten_min:
        df = dsh.remove_ten_min(df)

    if args.normalize != None:
        df = normalize(df, dsh.group_by_mac(df), args.normalize)

    if args.num_cluster == None:
        num_clusters = silhouette_method(df)
    else:
        num_clusters = args.num_cluster
    y_km = k_means(df, num_clusters)
    plot_clustering(df, y_km, "K-Means")
    print_error_rate(df, y_km, num_clusters)

    y_km, num_clusters = mean_shift(df)
    plot_clustering(df, y_km, "Mean-Shift")
    print_error_rate(df, y_km, num_clusters)

    plt.show()