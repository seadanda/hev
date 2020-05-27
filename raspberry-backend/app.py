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
from CommsCommon import DataFormat, CycleFormat
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

import sys
import argparse
import sqlite3
from datetime import datetime
import threading


readBattery = True

pin_bat     = 5
pin_ok      = 6
pin_alarm   = 12
pin_rdy2buf = 13
pin_bat85   = 19


try:
    import RPi.GPIO as gpio
    gpio.setmode(gpio.BCM)
    gpio.setup(pin_bat     , gpio.IN)
    gpio.setup(pin_ok      , gpio.IN)
    gpio.setup(pin_alarm   , gpio.IN)
    gpio.setup(pin_rdy2buf , gpio.IN)
    gpio.setup(pin_bat85   , gpio.IN)
except ImportError:
    print("No Raspberry Pi GPIO Module, battery information won't be reliable")
    readBattery = False



#SQLITE_FILE = 'database/HEV_monitoringDB.sqlite'  # name of the sqlite database file
#SQLITE_FILE = 'hev::memory:?cache=shared'
#SQLITE_FILE = 'file:hev?mode=memory&cache=shared'
SQLITE_FILE = '/dev/shm/HEV_monitoringDB.sqlite'  # use the linux shared memory pool as a file system
DATA_TABLE_NAME = 'hev_monitor_data'  # name of the table to be created
CYCLE_TABLE_NAME = 'hev_monitor_cycle'  # name of the table to be created


def getList(dict):
    return [*dict]

# List of data variables in the data packet from the Arduino
data_format = DataFormat().getDict()
cycle_format = CycleFormat().getDict()

class ArduinoClient(HEVClient):
    def __init__(self):
        super().__init__(polling=True)
        self.last_row_accessed = 0

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
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        c = conn.cursor()
        #get the count of tables with the name
        c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{tn}' '''.format(tn=tableName))
        existence = False

        #if the count is 1, then table exists
        if c.fetchone()[0]==1 :
            existence = True
        else :
        	logging.warning('Table does not exist.')

        #commit the changes to db
        conn.close()
        return existence

    def database_setup(self):
        '''
        This function creates the sqlite3 table with the timestamp column
        and the columns for the arduino packet data
        '''
        for TABLE_NAME in [ DATA_TABLE_NAME, CYCLE_TABLE_NAME ]:
            logging.debug('Creating ' + TABLE_NAME + ' table..' )
            # Create the table if it does not exist
            try:
                # Connecting to the database file
                conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)

                exec_string = "created_at  INTEGER  NOT NULL, "
                for var in data_format:
                   exec_string += var + "  FLOAT  NOT NULL, "
                exec_string += "alarms  STRING  NOT NULL "

                # Setting the maximum size of the DB to 100 MB
                conn.execute("PRAGMA max_page_count = 204800")
                conn.execute("PRAGMA page_size = 512")

                conn.execute('''CREATE TABLE IF NOT EXISTS {tn} ({ex_str});'''
                .format(tn=TABLE_NAME, ex_str=exec_string))
                conn.commit()
            except sqlite3.Error as err:
                conn.close()
                raise Exception("sqlite3 Error. Create failed: {}".format(str(err)))
            finally:
                conn.close()
                logging.info('Table ' + TABLE_NAME + ' created successfully!')

    def monitoring(self):
        '''
        Store arduino data in the sqlite3 table.
        '''
        epoch = datetime(1970, 1, 1)

        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
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

            if data_receiver['payload_type'] == "DATA" :
                data_packet = { el : data_receiver[el] for el in data_format}
                data_packet.update({"DB_time" : timestamp})
                data_packet.update({"alarms" : data_alarms})

                logging.debug("Writing to data database ...")
                try:
                    exec_string = "( :DB_time, "
                    for el in data_format:
                        exec_string += ":" + el + ", "
                    exec_string += ":alarms) "

                    cursor.execute(
                            'INSERT INTO {tn} VALUES {ex_str} '
                            .format(tn=DATA_TABLE_NAME, ex_str=exec_string), data_packet
                    )
                    conn.commit()
                except sqlite3.Error as err:
                    conn.close()
                    raise Exception("sqlite3 error. Insert into database failed: {}".format(str(err)))
                finally:
                    conn.close()
                    sys.stdout.flush()
            elif data_receiver['payload_type'] == "CYCLE" :
                data_packet = { el : data_receiver[el] for el in cycle_format }
                data_packet.update({"DB_time" : timestamp})
                data_packet.update({"alarms" : data_alarms})

                logging.debug("Writing to cycle table ...")
                try:
                    exec_string = "( :DB_time, "
                    for el in data_format:
                        exec_string += ":" + el + ", "
                    exec_string += ":alarms) "

                    cursor.execute(
                            'INSERT INTO {tn} VALUES {ex_str} '
                            .format(tn=CYCLE_TABLE_NAME, ex_str=exec_string), data_packet
                    )
                    conn.commit()
                except sqlite3.Error as err:
                    conn.close()
                    raise Exception("sqlite3 error. Insert into database failed: {}".format(str(err)))
                finally:
                    conn.close()
                    sys.stdout.flush()



    def db_backup(self,backup_time):
        threading.Timer(backup_time, self.db_backup, [backup_time]).start()
        logging.debug("Executing DB backup")
        try:
            # Backup DB
            conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
            backupCon = sqlite3.connect("database/HEC_monitoringDB_backup.sqlite")
            with backupCon:
                conn.backup(backupCon, pages=5, progress=progress)
                logging.debug("Backup successful")
        except sqlite3.Error as err:
            conn.close()
            backupCon.close()
            raise Exception("sqlite3 error. Error during backup: {}".format(str(err)))
        finally:
            conn.close()
            if(backupCon):
                backupCon.close()

    def number_rows(self, table_name):
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        c = conn.cursor()
        #get the count of tables with the name
        c.execute(''' SELECT count(*) FROM {tn} '''.format(tn=table_name))

        values = c.fetchone()
        logging.debug(f"{values[0]}") # TODO give a more meaningful log message

        #commit the changes to db
        #self.conn.commit()
        conn.close()
        return values[0]

def progress(status, remaining, total):
    logging.debug(f'Copied {total-remaining} of {total} pages...')


WEBAPP = Flask(__name__)

# Instantiating the client
client = ArduinoClient()

N = 300 # number of entries to request for alarms and data (300 = 60 s of data divided by 0.2 s interval)


@WEBAPP.route('/', methods=['GET', 'POST'])
def hello_world():
   return render_template('index.html')

@WEBAPP.route('/testing', methods=['GET', 'POST'])
def prototype():
   return render_template('index_prototype.html')

@WEBAPP.route('/settings')
def settings():
    return render_template('settings.html')

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
    Set timeout threshold data to the Arduino
    """
    #data = request.get_json(force=True)
    data = request.form
    for d,v in data.items():
        print(d,v)
    #print(client.send_cmd("SET_DURATION", data['name'].upper(), int(data['value'])))
    # make this false if things don't go well
    response = make_response(json.dumps(True))
    response.content_type = 'application/json'
    return (response)

def modeSwitchter(modeName):
    switcher = {
        0: "UNKNOWN",
        "PC-PSV": "HEV_MODE_PS",
        "CPAP": "HEV_MODE_CPAP",
        "PC-A/C-PRVC": "HEV_MODE_PRVC",
        "PC-A/C": "HEV_MODE_TEST",
        7: "LAB_MODE_BREATHE",
        8: "LAB_MODE_PURGE",
        10: "LAB_MODE_FLUSH"
    }
    return switcher.get(modeName, "Invalid ventilation mode")


@WEBAPP.route('/mode_handler', methods=['POST'])
def mode_handler():
    """
    Set mode for the ventilator
    """
    data = request.form
    data = request.get_json(force=True)

    print(client.send_cmd("SET_MODE", modeSwitchter(data['name'])))
    print(data)
    return ('', 204)

@WEBAPP.route('/send_ack', methods=['POST'])
def send_ack():
    """
    Send acknowledgement 
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



@WEBAPP.route('/live-data', methods=['GET'])
def live_data():
    """
    Get live data from the hevserver
    Output in json format
    """
    response = make_response(json.dumps(client.get_values()).encode('utf-8') )
    response.content_type = 'application/json'
    return response


@WEBAPP.route('/battery', methods=['GET'])
def live_battery():
    """
    Get battery info
    Output in json format
    """
    battery = {'bat' : 0, 'ok' : 0, 'alarm' : 0, 'rdy2buf' : 0, 'bat85' : 0}
    if readBattery:
        battery = {
        'bat'     : gpio.input(pin_bat    ) ,
        'ok'      : gpio.input(pin_ok     ) ,
        'alarm'   : gpio.input(pin_alarm  ) ,
        'rdy2buf' : gpio.input(pin_rdy2buf) ,
        'bat85'   : gpio.input(pin_bat85  )
        }
    response = make_response(json.dumps(battery).encode('utf-8') )
    response.content_type = 'application/json'
    return response

@WEBAPP.route('/last-data/<rowid>', methods=['GET'])
def last_data(rowid):
    """
    Query the sqlite3 table for variables
    Output in json format
    """

    list_variables = []
    list_variables.append("ROWID")
    list_variables.append("created_at")
    list_variables.append("alarms")
    list_variables.extend(getList(DataFormat().getDict()))

    united_var = ','.join(list_variables)

    fetched_all = []

    if client.check_table(DATA_TABLE_NAME) and client.number_rows(DATA_TABLE_NAME) > 0:
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
        cursor.execute(" SELECT {var} "
        " FROM {tn} WHERE ROWID > {rowid} ORDER BY ROWID DESC LIMIT {size} ".format(tn=DATA_TABLE_NAME, var=united_var, size=1000,rowid=rowid))

        fetched = cursor.fetchall()
        conn.close()
        for ir,el in enumerate(fetched):
            data = {key: None for key in list_variables}

            for index, item in enumerate(list_variables):
                data[item] = el[index]
                if ir == 0 and item == "ROWID" : client.last_row_accessed = el[index]

            fetched_all.append(data)

    else:
        for _ in range(1):
            data = {key: None for key in list_variables}
            for index, item in enumerate(list_variables):
                data[item] = ""

            fetched_all.append(data)

    response = make_response(json.dumps(fetched_all).encode('utf-8') )
    response.content_type = 'application/json'
    return response


@WEBAPP.route('/last-data', methods=['GET'])
def last_datum():
    """
    Query the sqlite3 table for variables
    Output in json format
    """

    list_variables = []
    list_variables.append("created_at")
    list_variables.extend(getList(DataFormat().getDict()))

    united_var = ','.join(list_variables)

    fetched_all = []

    if client.check_table(DATA_TABLE_NAME) and client.number_rows(DATA_TABLE_NAME) > 1:
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
        cursor.execute(" SELECT {var} "
        " FROM {tn} ORDER BY ROWID DESC LIMIT {size} ".format(tn=DATA_TABLE_NAME, var=united_var, size=1))

        fetched = cursor.fetchall()
        conn.close()
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

    if client.check_table(DATA_TABLE_NAME) and client.number_rows(DATA_TABLE_NAME) > N:
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
        cursor.execute(" SELECT {var} "
        " FROM {tn} ORDER BY ROWID DESC LIMIT {size} ".format(tn=DATA_TABLE_NAME, var=united_var, size=N))

        fetched = cursor.fetchall()
        conn.close()
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
    data = {'version': None, 'timestamp': None, 'payload_type': None, 'alarm_type': None, 'alarm_code': None, 'param': None}

    data_alarms = client.get_alarms()
    print(f"Alarms: {data_alarms[0]['alarm_code']}")

#    # acknowledge the oldest alarm
    #try:
    #    hevclient.ack_alarm(alarms[0]) # blindly assume we have one after 40s
    #except:
        #logging.info("No alarms received")

    if data_alarms[0]['alarm_type'] == "PRIORITY_HIGH":
       response = make_response(json.dumps(data_alarms).encode('utf-8') )
    else:
       response = make_response(json.dumps(data).encode('utf-8') )
    response.content_type = 'application/json'
    return response

@WEBAPP.route('/last_N_alarms', methods=['GET'])
def last_N_alarms():
    """
    Query the sqlite3 table for the last N alarms
    Output in json format
    """
    data = {'version': None, 'timestamp': None, 'payload_type': None, 'alarm_type': None, 'alarm_code': None, 'param': None}

    if client.check_table(DATA_TABLE_NAME):
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp, alarms "
        "FROM {tn} ORDER BY ROWID DESC LIMIT {size}".format(tn=DATA_TABLE_NAME, size=N))
        fetched = cursor.fetchall()
        conn.close()
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
