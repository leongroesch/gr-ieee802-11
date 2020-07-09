#!/usr/bin/env python
import mysql.connector
import matplotlib.pyplot as plt
from operator import itemgetter

def cluster_mac(data):
  clusters = {}
  for x in data:
    if x[0] not in clusters:
      clusters[x[0]] = []
    clusters[x[0]].append((x[1], x[2]))
  return clusters

def plot_clusters(clusters, subplot):
  i = 0
  #colors = ["red", "green", "blue"]
  
  for g in clusters:
    x, y = zip(*clusters[g])
    subplot.scatter(x, y, label=g)
    i+=1
  
def nulling_timestamp(data):
  time = min(data, key=itemgetter(1))[1]
  for x in data:
    x[1] = x[1] - time
  
  




def main():
  db = mysql.connector.connect(
      host="127.0.0.1",
      port=3306 ,
      user="root",
      password="123",
      auth_plugin='mysql_native_password',
      database="MAC_Frames"
  )
  #Query data
  db_cursor = db.cursor()
  db_cursor.execute("select sender_mac, record_time, freq_offset from frames;")
  data = db_cursor.fetchall()

  data = [list(x) for x in data]

  #Nulling of timestamp
  nulling_timestamp(data)

  clusters = cluster_mac(data)
  #Cluster data after macs

  #Plot clusters
  fig = plt.figure()
  cluster_fig = fig.add_subplot(1, 1, 1)

  plot_clusters(clusters, cluster_fig)

  cluster_fig.set_ylabel("Frequenzy offset")
  cluster_fig.set_xlabel("Timestamp") 
  plt.legend(loc=2)
  plt.show()
main()