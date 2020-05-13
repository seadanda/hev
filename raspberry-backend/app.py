#!/usr/bin/env python3

# Python monitoring code
# USAGE:  python3 app.py
#
# Last update: May 5, 2020

import time
from flask import Flask, render_template, make_response, jsonify, Response, request
import sqlite3
import argparse
from flask import json
import chardet
from hevclient import HEVClient
from CommsCommon import DataFormat
from datetime import datetime

import sys
import argparse
import sqlite3
from datetime import datetime
import threading

#SQLITE_FILE = 'database/HEV_monitoringDB.sqlite'  # name of the sqlite database file
#SQLITE_FILE = 'hev::memory:?cache=shared'
SQLITE_FILE = 'file:hev?mode=memory&cache=shared'
TABLE_NAME = 'hev_monitor'  # name of the table to be created

def getList(dict): 
    return [*dict] 

# List of data variables in the data packet from the Arduino
data_format = getList(DataFormat().getDict())    

class ArduinoClient(HEVClient):
    def __init__(self):
        super().__init__(polling=True)
        self.conn = None

    def start_client(self):
        """runs in other thread - works as long as super goes last and nothing
        else is blocking. If something more than a one-shot process is needed
        then use async"""
        self.database_setup()
        super().start_client()

    def get_updates(self, payload):
        """callback from the polling function, payload is data from socket"""
        self.monitoring()

    def check_table(self,tableName):
        c = self.conn.cursor()    			
        #get the count of tables with the name
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tn}' '''.format(tn=tableName))  
        existence = False

        #if the count is 1, then table exists
        if c.fetchone()[0]==1 : 
            existence = True
            print('Table exists.')
        else :
        	print('Table does not exist.')
    			
        #commit the changes to db			
        #self.conn.commit()
        return existence
    def database_setup(self):
        '''
        This function creates the sqlite3 table with the timestamp column 
        and the columns for the arduino packet data  
        '''
        print('Creating ' + TABLE_NAME + ' table..' )

        # Create the table if it does not exist
        try:
            # Connecting to the database file
            self.conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
   
            exec_string = "created_at  INTEGER  NOT NULL, "
            for var in data_format:
               exec_string += var + "  FLOAT  NOT NULL, "
            exec_string += "alarms  STRING  NOT NULL "

            # Setting the maximum size of the DB to 100 MB
            self.conn.execute("PRAGMA max_page_count = 204800")
            self.conn.execute("PRAGMA page_size = 512")

            self.conn.execute('''CREATE TABLE IF NOT EXISTS {tn} ({ex_str});'''
            .format(tn=TABLE_NAME, ex_str=exec_string))
            self.conn.commit()
        except sqlite3.Error as err:
            raise Exception("sqlite3 Error. Create failed: {}".format(str(err)))
        finally:
            print('Table ' + TABLE_NAME + ' created successfully!')

    def monitoring(self):
        '''
        Store arduino data in the sqlite3 table. 
        '''
        epoch = datetime(1970, 1, 1)

        cursor = self.conn.cursor()
        current_time = datetime.now()

        # Computing the time in seconds since the epoch because easier to manipulate. 
        timestamp = (current_time -epoch).total_seconds() * 1000
           
        data_receiver = self._fastdata
        data_alarms = self._alarms
        if data_receiver != None and len(data_receiver) > 0:

            # data alarms can have length of 6, joining all the strings
            if data_alarms != None:
                data_alarms = ','.join(data_alarms)
            else:
                data_alarms = "none"
            data_packet = { el : data_receiver[el] for el in data_format}
            data_packet.update({"DB_time" : timestamp})
            data_packet.update({"alarms" : data_alarms})

            print("Writing to database ...")
            try:
                exec_string = "( :DB_time, "
                for el in data_format: 
                    exec_string += ":" + el + ", "
                exec_string += ":alarms) "

                cursor.execute(
                        'INSERT INTO {tn} VALUES {ex_str} '
                        .format(tn=TABLE_NAME, ex_str=exec_string), data_packet
                )
                self.conn.commit()
            except sqlite3.Error as err:
                raise Exception("sqlite3 error. Insert into database failed: {}".format(str(err)))
            finally:                  
                sys.stdout.flush()

    def db_backup(self,backup_time):
        threading.Timer(backup_time, self.db_backup, [backup_time]).start()
        print("Executing DB backup")
        try:
            # Backup DB
            backupCon = sqlite3.connect("database/HEC_monitoringDB_backup.sqlite")    
            with backupCon:
                self.conn.backup(backupCon, pages=5, progress=progress)
                print("Backup successful")
        except sqlite3.Error as err:
            raise Exception("sqlite3 error. Error during backup: {}".format(str(err)))
        finally: 
            if(backupCon):
                backupCon.close()

    def number_rows(self, table_name):
        c = self.conn.cursor()    			
        #get the count of tables with the name
        c.execute(''' SELECT count(*) FROM {tn} '''.format(tn=table_name))  

        values = c.fetchone()
        print(values[0])

        #commit the changes to db			
        #self.conn.commit()
        return values[0]

def progress(status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')


WEBAPP = Flask(__name__)

# Instantiating the client
client = ArduinoClient()

N = 300 # number of entries to request for alarms and data (300 = 60 s of data divided by 0.2 s interval)


@WEBAPP.route('/', methods=['GET', 'POST'])
def hello_world():
   return render_template('index.html', result=last_data())

@WEBAPP.route('/testing', methods=['GET', 'POST'])
def prototype():
   return render_template('index_prototype.html', result=last_data())

@WEBAPP.route('/settings')
def settings():
    return render_template('settings.html', result=last_data())

@WEBAPP.route('/charts')
def charts():
    return render_template('charts.html', result=last_N_data())

@WEBAPP.route('/charts2')
def charts2():
    return render_template('charts2.html')

@WEBAPP.route('/chartsLoop')
def chartsLoop():
    return render_template('chartsLoop.html')

@WEBAPP.route('/logs')
def logs():
    return render_template('logs.html', result=last_N_alarms())    

@WEBAPP.route('/fan')
def fan():
    return render_template('fan.html', result=live_data())


def multiple_appends(listname, *element):
    listname.extend(element)

@WEBAPP.route('/send_cmd', methods=['POST'])
def send_cmd():
    """
    Send command to the data server
    """ 
    web_form = request.form
    if web_form.get('start') == "START":
        print(client.send_cmd("GENERAL", "START"))
    elif web_form.get('stop') == "STOP":
        print(client.send_cmd("GENERAL", "STOP"))
    elif web_form.get('reset') == "RESET":
        print(client.send_cmd("GENERAL", "RESET"))
    #return render_template('index.html', result=live_data())
    return ('', 204)
    

@WEBAPP.route('/data_handler', methods=['POST'])
def data_handler():
    """
    Send configuration data to the Arduino
    """
    output = []
    var_1 = request.form['pressure_air_supply']
    var_2 = request.form['variable2']
    var_3 = request.form['variable3']
    var_4 = request.form['variable4']
    var_5 = request.form['variable5']
    var_6 = request.form['variable6']
  
    patient_name = request.form['patient_name']

 
    multiple_appends(output, var_1, var_2, var_3, var_4, var_5, var_6)
    
    converted_output = [float(i) for i in output] 

    print(converted_output)
    print("The thresholds are set with a command, not with a set threshold function")
    #hevclient.set_thresholds(converted_output)

    return render_template('index.html', result=live_data(), patient=patient_name)






@WEBAPP.route('/live-data', methods=['GET'])
def live_data():
    """
    Get live data from the hevserver
    Output in json format
    """
    response = make_response(json.dumps(client.get_values()).encode('utf-8') )
    response.content_type = 'application/json'
    return response

@WEBAPP.route('/last-data', methods=['GET'])
def last_data():
    """
    Query the sqlite3 table for variables
    Output in json format
    """

    list_variables = []
    list_variables.append("created_at")
    list_variables.append("alarms")
    list_variables.extend(getList(DataFormat().getDict()))

    united_var = ','.join(list_variables)

    fetched_all = []
    
    if client.check_table(TABLE_NAME) and client.number_rows(TABLE_NAME) > 0:
        cursor = client.conn.cursor()
        cursor.execute(" SELECT {var} "
        " FROM {tn} ORDER BY ROWID DESC LIMIT {size} ".format(tn=TABLE_NAME, var=united_var, size=1))
            
        fetched = cursor.fetchall()
        for el in fetched:
            data = {key: None for key in list_variables}
    
        for index, item in enumerate(list_variables):
            data[item] = el[index]

        fetched_all.append(data)
    else:
        for _ in range(1):
            data = {key: None for key in list_variables}
            for index, item in enumerate(list_variables):
                data[item] = ""

            fetched_all.append(data)

    response = make_response(json.dumps(fetched_all[0]).encode('utf-8') )
    response.content_type = 'application/json'

    return response

@WEBAPP.route('/last_N_data', methods=['GET'])
def last_N_data():
    """
    Query the sqlite3 table for variables
    Output in json format
    """

    list_variables = []
    list_variables.append("created_at")
    list_variables.extend(getList(DataFormat().getDict()))

    united_var = ','.join(list_variables)

    fetched_all = []
    
    if client.check_table(TABLE_NAME) and client.number_rows(TABLE_NAME) > N:
        cursor = client.conn.cursor()
        cursor.execute(" SELECT {var} "
        " FROM {tn} ORDER BY ROWID DESC LIMIT {size} ".format(tn=TABLE_NAME, var=united_var, size=N))
            
        fetched = cursor.fetchall()
        for el in fetched:
            data = {key: None for key in list_variables}
    
            for index, item in enumerate(list_variables):
                data[item] = el[index]

            fetched_all.append(data)
    else:
        for _ in range(N):
            data = {key: None for key in list_variables}
            for index, item in enumerate(list_variables):
                data[item] = ""

            fetched_all.append(data)

    response = make_response(json.dumps(fetched_all).encode('utf-8') )
    response.content_type = 'application/json'

    return response


@WEBAPP.route('/live-alarms', methods=['GET'])
def live_alarms():
    """
    Get live alarms from the hevserver
    Output in json format
    """
    data = {'timestamp' : None, 'alarms' : None}
    data_alarms = client.get_alarms()
    data_receiver = client.get_values()


    if data_alarms != None:
        data_alarms = ','.join(data_alarms)
    else:
        data_alarms = "none"

    data["alarms"] = data_alarms

    if data_receiver is not None:
        data["timestamp"] = data_receiver['timestamp']/1000
    else:
        data["timestamp"] = "none"

    response = make_response(json.dumps(data).encode('utf-8') )


@WEBAPP.route('/last_N_alarms', methods=['GET'])
def last_N_alarms():
    """
    Query the sqlite3 table for the last N alarms
    Output in json format
    """
    data = {'timestamp' : None, 'alarms' : None}

    if client.check_table(TABLE_NAME):
        cursor = client.conn.cursor()
        cursor.execute("SELECT timestamp, alarms "
        "FROM {tn} ORDER BY ROWID DESC LIMIT {size}".format(tn=TABLE_NAME, size=N))
        fetched = cursor.fetchall()
    else:
        fetched = []
        for _ in range(N):
              data['timestamp'] = "none"
              data['alarms'] = "none"
              fetched.append(data)


    response = make_response(json.dumps(fetched).encode('utf-8') )
    response.content_type = 'application/json'
    return response


def parse_args():
    parser = argparse.ArgumentParser(description='HEV webserver')
    parser.add_argument('--host', default='127.0.0.1')    
    parser.add_argument('--interval', type=float, default=0.02)
    parser.add_argument('--backup_time', type=int, default=600)
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = parse_args()
    #db_backup(ARGS.backup_time)
    WEBAPP.run(debug=True, host=ARGS.host, port=5000)