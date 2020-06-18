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
from CommsCommon import DataFormat, CycleFormat, ReadbackFormat, AlarmFormat, TargetFormat, BatteryFormat, PersonalFormat
from datetime import datetime
import logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

import io
import csv
import sys
import argparse
import sqlite3
from datetime import datetime
import threading

#SQLITE_FILE = 'database/HEV_monitoringDB.sqlite'  # name of the sqlite database file
#SQLITE_FILE = 'hev::memory:?cache=shared'
#SQLITE_FILE = 'file:hev?mode=memory&cache=shared'
SQLITE_FILE = '/dev/shm/HEV_monitoringDB.sqlite'  # use the linux shared memory pool as a file system
MASTER_TABLE_NAME = 'hev_monitor' # this table keeps track of the data we get through keys to other tables
DATA_TABLE_NAME = 'hev_monitor_data'  # name of the table to be created for payload type data
CYCLE_TABLE_NAME = 'hev_monitor_cycle'  # name of the table to be created for payload type cycle
TARGET_TABLE_NAME = 'hev_monitor_target'  # name of the table to be created for payload type target
READBACK_TABLE_NAME = 'hev_monitor_readback'  # name of the table to be created for payload type readback
ALARM_TABLE_NAME = 'hev_monitor_alarm'  # name of the table to be created for payload type readback
PERSONAL_TABLE_NAME = 'hev_personal_target'  # name of the table to be created for payload type personal


def getList(dict):
    return [*dict]


payload_types = {
    'DATA' : {'table_name' : DATA_TABLE_NAME, 'format' : DataFormat().getDict(), 'id' : 'DataID'},
    'CYCLE' : {'table_name' : CYCLE_TABLE_NAME, 'format' : CycleFormat().getDict(), 'id': 'CycleID'},
    'READBACK' : { 'table_name' : READBACK_TABLE_NAME, 'format' : ReadbackFormat().getDict(), 'id' : 'ReadBackID'},
    'ALARM'    : { 'table_name' : ALARM_TABLE_NAME, 'format' : AlarmFormat().getDict(), 'id' : 'AlarmID' },
    #'TARGET' : { 'table_name' : 'hevmonitor_target', 'format' : TargetFormat().getDict(), 'id' : 'TargetID' },
    'TARGET' : { 'table_name' : TARGET_TABLE_NAME, 'format' : TargetFormat().getDict(), 'id' : 'TargetID' },
    'BATTERY' : { 'table_name' : 'hevmonitor_battery', 'format' : BatteryFormat().getDict(), 'id' : 'BatteryID' },
    'PERSONAL' : { 'table_name' : PERSONAL_TABLE_NAME, 'format' : PersonalFormat().getDict(), 'id' : 'PersonalID' },
}


class WebClient(HEVClient):
    def __init__(self):
        super().__init__(polling=True)

    def start_client(self):
        """runs in other thread - works as long as super goes last and nothing
        else is blocking. If something more than a one-shot process is needed
        then use async"""
        self.database_setup()
        # call for all the targets and personal details
        # when starting the web app so we always have some in the db
        self.send_cmd("GET_TARGETS","PC_AC")
        self.send_cmd("GET_TARGETS","PC_AC_PRVC")
        self.send_cmd("GET_TARGETS","PC_PSV")
        self.send_cmd("GET_TARGETS","TEST")
        self.send_cmd("GENERAL", "GET_PERSONAL")
        super().start_client()


    def get_updates(self, payload):
        """callback from the polling function, payload is data from socket"""
        self.monitoring(payload)

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
        for payload_type in payload_types :
            payload = payload_types[payload_type]
            logging.debug('Creating ' + payload['table_name'] + ' table..' )
            # Create the table if it does not exist
            try:
                # Connecting to the database file
                conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)

                exec_string = "created_at  INTEGER  NOT NULL"
                for var in payload['format']:
                   exec_string += ", " + var + "  FLOAT  NOT NULL"
                #exec_string += "alarms  STRING  NOT NULL "

                conn.execute('''CREATE TABLE IF NOT EXISTS {tn} ({ex_str});'''
                .format(tn=payload['table_name'], ex_str=exec_string))
                conn.commit()
            except sqlite3.Error as err:
                conn.close()
                raise Exception("sqlite3 Error. Create failed: {}".format(str(err)))
            finally:
                conn.close()
                logging.info('Table ' + payload['table_name'] + ' created successfully!')
        #now make master table
        # Create the table if it does not exist
        try:
            # Connecting to the database file
            conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)

            #exec_string = "created_at  INTEGER  NOT NULL, "
            exec_string=""
            for p in payload_types:
                exec_string += "{pid} INTEGER, ".format(pid=payload_types[p]['id'])
            for p in payload_types:
                exec_string += "FOREIGN KEY({pid}) REFERENCES {tn}(ROWID) ,".format(pid = payload_types[p]['id'], tn = DATA_TABLE_NAME)
            exec_string = exec_string[:-1]
            # Setting the maximum size of the DB to 100 MB
            conn.execute("PRAGMA max_page_count = 204800")
            conn.execute("PRAGMA page_size = 512")
            conn.execute('''CREATE TABLE IF NOT EXISTS {tn} ({ex_str});'''
                .format(tn=MASTER_TABLE_NAME, ex_str=exec_string))
            conn.commit()
        except sqlite3.Error as err:
            conn.close()
            raise Exception("sqlite3 Error. Create failed: {}".format(str(err)))
        finally:
            conn.close()
            logging.info('Table ' + MASTER_TABLE_NAME + ' created successfully!')

    def monitoring(self, payload):
        '''
        Store arduino data in the sqlite3 table.
        '''
        epoch = datetime(1970, 1, 1)

        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
        current_time = datetime.now()

        # Computing the time in seconds since the epoch because easier to manipulate.
        timestamp = (current_time -epoch).total_seconds() * 1000

        if payload != None and payload['type'] in payload_types:
            payload_type = payload['type']
            data_packet = { el : payload[payload_type][el] for el in payload_types[payload_type]['format']}
            data_packet.update({"DB_time" : timestamp})
            logging.debug("Writing to data database ...")
            try:
                exec_string = "( :DB_time"
                for el in payload_types[payload_type]['format']:
                    exec_string += ", :" + el
                exec_string += ") "

                cursor.execute(
                        'INSERT INTO {tn} VALUES {ex_str} '
                        .format(tn=payload_types[payload_type]['table_name'], ex_str=exec_string), data_packet
                )
                conn.commit()
                payload_id = cursor.lastrowid
                columns = conn.execute("PRAGMA table_info({tn})".format(tn=MASTER_TABLE_NAME))
                cursor.execute(
                    'INSERT INTO {tn} ({pid}) VALUES ( {pl} )'.format(pid = payload_types[payload_type]['id'], tn = MASTER_TABLE_NAME, pl = payload_id )
                )
                conn.commit()
            except sqlite3.Error as err:
                conn.close()
                raise Exception("sqlite3 error. Insert into database failed: {}".format(str(err)))
            finally:
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
client = WebClient()

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

@WEBAPP.route('/downloadCSV', methods=['get'])
def downloadCSV():
    sqlSelect =  "SELECT * FROM hev_monitor_data; "
    timestr = time.strftime("%Y%m%d-%H%M%S")
    fileName= 'export_'+timestr+'.csv'
    try:
       conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
       cursor = conn.cursor()
       si = io.StringIO()
       cw = csv.writer(si, dialect='excel',  delimiter=',')      
       for row in cursor.execute(sqlSelect):
         cw.writerow(row)
       #results = cursor.fetchall()        
       # Extract the table headers.
       #headers = [i[0] for i in cursor.description]
       #cw.writerows(headers)       
       #csv.writer.writerow   (results)
       output = make_response(si.getvalue())
       print("benzinaaaa\n\n")          
       output.headers["Content-Disposition"] = "attachment; filename="+fileName
       output.headers["Content-type"] = "text/csv"
       output.headers["charset"]='utf-8-sig'
       print("Data export successful.")      
    except sqlite3.Error as err:
      conn.close()
      raise Exception("sqlite3 error. CSV export failed: {}".format(str(err)))      
    finally:
      conn.close()   
      return output



@WEBAPP.route('/send_cmd', methods=['POST'])
def send_cmd():
    """
    Send command to the data server
    """
    web_form = request.form
    success = True
    if 'cmd' in web_form.keys() and web_form.get('cmd') in [ 'START', 'STOP', 'STANDBY']:
        success=client.send_cmd("GENERAL", web_form.get('cmd'))
    elif 'export' in web_form.keys():
        downloadCSV()

    response = make_response(json.dumps(success))
    response.content_type = 'application/json'
    return (response)


@WEBAPP.route('/set_alarm_threshold', methods=['POST'])
def set_alarm_threshold():
    """
    Send alarm command to the data server
    """
    data = request.form
    #print(data.get('name'))
    #print(data.get('min'))
    #print(data.get('max'))

    print(client.send_cmd("SET_THRESHOLD_MIN", data.get('name'), int(data.get('min'))))
    print(client.send_cmd("SET_THRESHOLD_MAX", data.get('name'), int(data.get('max'))))

    return ('', 204)




@WEBAPP.route('/current_target_handler', methods=['POST'])
def current_target_handler():
    """
    Update Current Targets

    INSPIRATORY_PRESSURE = 1
    RESPIRATORY_RATE     = 2 
    IE_RATIO             = 3
    VOLUME               = 4
    PEEP                 = 5
    FIO2                 = 6
    INHALE_TIME          = 7


    """
    data = request.form
    success = True
    for d,v in data.items():
        print("SET_TARGET_CURRENT", d, v,type(d),type(v))
        success = client.send_cmd("SET_TARGET_CURRENT", d, float(v))
    
    response = make_response(json.dumps(success))
    response.content_type = 'application/json'
    return (response)
    
@WEBAPP.route('/target_handler', methods=['POST'])
def target_handler():
    """
    Update Current Targets

    INSPIRATORY_PRESSURE = 1
    RESPIRATORY_RATE     = 2 
    IE_RATIO             = 3
    VOLUME               = 4
    PEEP                 = 5
    FIO2                 = 6
    INHALE_TIME          = 7


    """
    data = request.form
    success = True
    print("**************************set target test")

    #simulated payload in case we need for testing
    payload = { key : 1.1 for key in payload_types['TARGET']['format']}
    payload['payload_type'] = 'TARGET'
    for d,v in data.items():
        if 'pcac_setting_' in d:
            payload['mode'] = 'PC_AC'
            success = client.send_cmd("SET_TARGET_PC_AC", d.replace('pcac_setting_','').upper(), float(v))
            payload[d.replace('pcac_setting_','')] = float(v)
        elif 'prvc_setting_' in d:
            payload['mode'] = 'PC_AC_PRVC'
            success = client.send_cmd("SET_TARGET_PC_AC_PRVC", d.replace('prvc_setting_','').upper(), float(v))
            payload[d.replace('prvc_setting_','')] = float(v)
        elif 'psv_setting_' in d:
            payload['mode'] = 'PC_PSV'
            success = client.send_cmd("SET_TARGET_PC_PSV", d.replace('psv_setting_','').upper(), float(v))
            payload[d.replace('psv_setting_','')] = float(v)

        elif 'test_setting_' in d:
            payload['mode'] = 'TEST'
            success = client.send_cmd("SET_TARGET_TEST", d.replace('test_setting_','').upper(), float(v))
            payload[d.replace('test_setting_','')] = float(v)
    # sent the simulated payload to the db
    #client.monitoring({'type' : 'TARGET', 'TARGET' : payload})
    
    response = make_response(json.dumps(success))
    response.content_type = 'application/json'
    return (response)


import random

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
    response = make_response(json.dumps(random.choice([True,False])))
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
    for d,v in data.items():
        print(d,v)

    #success = client.send_cmd("SET_MODE", modeSwitchter(data['name'].upper()))
    success = client.send_cmd("SET_MODE", data['name'])
    response = make_response(json.dumps(success))
    response.content_type = 'application/json'
    return (response)

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
    elif web_form.get('standby') == "STANDBY":
        print(client.send_cmd("GENERAL", "STANDBY"))
    elif web_form.get('reset') == "RESET":
        print(client.send_cmd("GENERAL", "RESET"))
    #return render_template('index.html', result=live_data())
    return ('', 204)

@WEBAPP.route('/personal_data_handler', methods=['POST'])
def personal_data_handler():
    """
    Send personal data to the Arduino
    """
    #data = request.get_json(force=True)
    data = request.form
    personal = {}

    for d,v in data.items():
        print(d,v)
        personal[d.replace('personal_', '')] = v

    success = client.send_personal(personal=personal )
    '''
    #for testing
    for p in payload_types['PERSONAL']['format']:
        if p not in personal:
            personal[p]=''
    client.monitoring({'type' : 'PERSONAL', 'PERSONAL' : personal})
    '''
    response = make_response(json.dumps(success))
    response.content_type = 'application/json'
    return (response)

@WEBAPP.route('/live-data', methods=['GET'])
def live_data():
    """
    Get live data from the hevserver
    Output in json format
    """
    response = make_response(json.dumps(client.get_values()).encode('utf-8') )
    response.content_type = 'application/json'
    return response

@WEBAPP.route('/last-data/<rowid>', methods=['GET'])
def last_data(rowid):
    """
    Query the sqlite3 table for variables
    Output in json format
    """


    fetched_all = []
    if client.check_table(MASTER_TABLE_NAME) and client.number_rows(MASTER_TABLE_NAME) > 0:
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        payload_names = ','.join([ payload_types[p]['id'] for p in payload_types ])
        cursor = conn.cursor()
        cursor.execute(" SELECT ROWID,{ids} FROM {tn} WHERE ROWID > {rowid} ORDER BY ROWID DESC LIMIT {size}".format(tn=MASTER_TABLE_NAME, size=100,rowid=rowid,ids=payload_names))

        fetched = cursor.fetchall()
        for el in fetched:
            rowid = el[0]
            for i,p in enumerate(payload_types):
                united_vars = ','.join(list(payload_types[p]['format']) + ['ROWID', 'created_at'])
                payloadid = el[i+1]
                if payloadid != None :
                    data = {}
                    cursor.execute(" SELECT {var} "
                    " FROM {tn} WHERE ROWID == {rowid}".format(tn=payload_types[p]['table_name'], var=united_vars,rowid=payloadid))
                    payload_el = cursor.fetchone()
                    for index, item in enumerate(payload_types[p]['format']):
                        data[item] = payload_el[index]
                    # switch so rowid refers to master, and payload id is table rowid
                    data["PAYLOADID"] = payloadid
                    data["ROWID"] = rowid
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

@WEBAPP.route('/last-targets', methods=['GET'])
def last_targets():
    """
    Query the sqlite3 table for the last targets for each mode
    Output in json format
    """

    list_variables = []
    list_variables.append('ROWID')
    list_variables.append("created_at")
    list_variables.extend(getList(TargetFormat().getDict()))
    united_var = ','.join(list_variables)

    fetched_all = []

    if client.check_table(DATA_TABLE_NAME) and client.number_rows(TARGET_TABLE_NAME) > 1:
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()

        for mode in ( "CPAP", "TEST", "PC_AC", "PC_PSV", "PC_AC_PRVC" ):
        #for mode in ( "PCAP", "TEST" ):
            cursor.execute(" SELECT {var} "
            " FROM {tn} WHERE mode == '{md}' ORDER BY ROWID DESC LIMIT 1 ".format(tn=TARGET_TABLE_NAME, var=united_var, md = mode))
            fetched = cursor.fetchone()
            if fetched:
                fetched_all.append({item : fetched[index] for index,item in enumerate(list_variables)})
        conn.close()

    response = make_response(json.dumps(fetched_all).encode('utf-8') )
    response.content_type = 'application/json'

    return response

@WEBAPP.route('/last-personal', methods=['GET'])
def last_personal():
    """
    Query the sqlite3 table for the last targets for each mode
    Output in json format
    """

    list_variables = []
    list_variables.append("created_at")
    list_variables.append("ROWID")

    list_variables.extend(getList(PersonalFormat().getDict()))

    united_var = ','.join(list_variables)

    fetched_all = []

    if client.check_table(PERSONAL_TABLE_NAME) and client.number_rows(PERSONAL_TABLE_NAME) > 0:
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()

        cursor.execute(" SELECT {var} FROM {tn} ORDER BY ROWID DESC LIMIT 1 ".format(tn=PERSONAL_TABLE_NAME, var=united_var))
        fetched = cursor.fetchone()
        if fetched:
            fetched_all.append({item : fetched[index] for index,item in enumerate(list_variables)})
        conn.close()
    fetched_last = {}
    if (len(fetched_all) > 0): fetched_last = fetched_all[0]
    response = make_response(json.dumps(fetched_last).encode('utf-8') )
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
    #if (len(data_alarms) > 0 ):
        #print(f"Alarms: {data_alarms[0]['alarm_code']}")

    #    # acknowledge the oldest alarm
        #try:
        #    hevclient.ack_alarm(alarms[0]) # blindly assume we have one after 40s
        #except:
            #logging.info("No alarms received")
    if len(data_alarms) > 0 and data_alarms[0]['alarm_type'] == "PRIORITY_HIGH":
        response = make_response(json.dumps(data_alarms[0]).encode('utf-8') )
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

    alarm_variables = []
    alarm_variables.append("ROWID")
    alarm_variables.append("created_at")
    alarm_variables.extend(getList(AlarmFormat().getDict()))

    alarm_united_var = ','.join(alarm_variables)
    fetched = []
    if client.check_table(ALARM_TABLE_NAME):
        conn = sqlite3.connect(SQLITE_FILE, check_same_thread = False, uri = True)
        cursor = conn.cursor()
        cursor.execute("SELECT {var} "
        "FROM {tn} ORDER BY ROWID DESC LIMIT {size}".format(tn=ALARM_TABLE_NAME, size=N, var =alarm_united_var))
        fetched = cursor.fetchall()
        conn.close()


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
