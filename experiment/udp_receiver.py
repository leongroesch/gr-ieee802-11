#!/usr/bin/env python
import socket
import mysql.connector
import sys
import traceback

def str_to_float(s):
  s = s.strip().replace(',', '.')
  return float(s)

def convert_data(data):
  fields = str(data,'utf-8').split(';')
  fields[0] = str_to_float(fields[0])
  fields[2] = str_to_float(fields[2])
  fields[3] = str_to_float(fields[3])
  fields[4] = str_to_float(fields[4])
  return fields

# Makes sure the required database and the required table is there 
def init_db(db_cursor):
  db_cursor.execute("CREATE DATABASE IF NOT EXISTS MAC_Frames;")
  db_cursor.execute("use MAC_Frames;")
  db_cursor.execute("""CREATE TABLE IF NOT EXISTS frames (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        record_time INT,
                        sender_mac VARCHAR(20),
                        snr FLOAT,
                        norm_freq DOUBLE,
                        freq_offset DOUBLE
                    );""")

def main():
  ip = "127.0.0.1"
  port = 52002
  sql_insert = "INSERT INTO frames (record_time, sender_mac, snr, norm_freq, freq_offset) VALUES (%s, %s, %s, %s, %s)"

  if( len(sys.argv) >= 3):  
    ip = sys.argv[1] #"127.0.0.1"
    port = int(sys.argv[2]) # 52002
  

  mydb = mysql.connector.connect(
      host="127.0.0.1",
      port=3306 ,
      user="root",
      password="123",
      auth_plugin='mysql_native_password'
     # database="MAC_Frames"
  )

  db_cursor = mydb.cursor()

  init_db(db_cursor)

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind((ip,port))
  print("Listening on: %s:%d" % (ip, port))

  while True:
    data, addr = sock.recvfrom(1024)
    try:
      data_array = convert_data(data)
      db_cursor.execute(sql_insert, data_array)
      print("Received Data: ", data_array)
      mydb.commit()
    except:
      print(traceback.format_exc())

main()