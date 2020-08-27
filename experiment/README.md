* Requirements: Installation of `docker` and `gnuradio (maint-3.8)`   

## Installation of gr-ieee802-11
In order to install the additional gnuradio block developed for this lap, the branch must be changed to `meta_data_analyzing` (`git checkout meta_data_analyzing`). Afterwards the installation can take place as described in `gr-ieee802-11\README.md`. The gnuradio-companion should now contain a block named `WiFi Parse Meta Mac`.

## Installation of MySQL Database
The mysql Database, in which the meta data of each MAC-frame will be stored, is deployed via docker. To get the mysql docker container up and running the following commands need to be executed as root.
```
docker pull mysql:latest   
docker run --name meta_analyzer_db -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123  mysql:latest
```

### Load Database 
Some recorded tables are provided in `analysis/mac_frames.zip`.  
Note: the file is unzipped a size of 189 MB.  
   
The unzipped database can be loaded into the docker container with the following commands:   
```
echo "CREATE DATABASE IF NOT EXISTS MAC_Frames;" | docker exec -i meta_analyzer_db /usr/bin/mysql -uroot -p123

cat mac_frames.sql | docker exec -i meta_analyzer_db /usr/bin/mysql -u root --password=123 MAC_Frames
```

## UDP Receiver
* Requirements: `pip3 install mysql-connector-python`   
    
With `gr-ieee802-11/experiment/udp_receiver.py` a python script is provided which receives the udp-packages published by the gnuradio flow graph. (either wifi_loopback or wifi_rx) The received data is pared and saved in the database running in the docker container. By default the UDP Server is bind to 127.0.0.1:52002 but a different interface IP and Port number can be provided as arguments. For example, to receive data from another interface than the loopback.

## Query Visualizer
* Requirements: `pip3 install matplotlib numpy sqlalchemy pymysql pandas sklearn`
     
Within the directory `gr-ieee802-11/experiment/analysis/`, there are three python scripts for different visualizations:  
* general_information.py
* clustering.py
* auto_corr.py  

The database table to use can be specified with `--table`. The in the report used tables are 4_hours and 7_days