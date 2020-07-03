* Requirements: Installation of `docker` and `gnuradio (maint-3.8)`   

## Installation of gr-ieee802-11
In order to install the additional gnuradio block developed for this lap the branch must be changed to `meta_data_analyzing`. Afterwards the installation can take place as described in `gr-ieee802-11\README.md`. The gnuradio-companion should now contain a block named `WiFi Parse Meta Mac`.

## Installation of MySQL Database
The mysql Database, in which the meta data of each MAC-frame will be stored, is deployed via docker. To get the mysql docker container up an running the following commands need to be executed as root.
```
docker pull mysql:latest   
docker run --name meta_analyzer_db -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=123  mysql:latest
```

## UDP Receiver

With `gr-ieee802-11/experiment/udp_receiver.py` a python script is provided which receives the udp-packages published by the gnuradio flow graph. The received data is pared and saved in the database running in the docker container. By default the UDP Server is bind to 127.0.0.1:52002 but a different interface IP and Port number can be provided as arguments.


