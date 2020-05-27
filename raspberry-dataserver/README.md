# Data server specification for the HEV

First implementation of dataserver for the raspberry pi with broadcast and query capabilities.

TCP server implemented using the asyncio python library to serve data on two unix sockets and listen for requests on a third. Requests and broadcasts are dealt with on separate threads.

## Sockets

| Address           | Socket use                | 
| ----------------- | ------------------------- |
| `127.0.0.1:54320` | WebUI broadcast socket    |
| `127.0.0.1:54321` | Joint query socket        |
| `127.0.0.1:54322` | NativeUI broadcast socket |


Clients connect once to their broadcast socket and keep the connection open while polling constantly for the next packet.
Clients connect to the joint query socket, send one query, await the reply, then disconnect to free up the socket.

### Broadcast sockets
A broadcast is sent out to all connections every n seconds where n is configurable

Alarms are included in the broadcast packet but can also come through as a dedicated alarm packet if they come through alone, depending on the LLI implementation (TBC)

The packet is a json frame with format:
```python
{
    "sensors": {
        "version": int,
        "fsm_state": int,
        "pressure_air_supply": float,
        "pressure_air_regulated": float,
        "pressure_o2_supply": float,
        "pressure_o2_regulated": float,
        "pressure_buffer": float,
        "pressure_inhale": float,
        "pressure_patient": float,
        "temperature_buffer": float,
        "pressure_diff_patient": float,
        "readback_valve_air_in": float,
        "readback_valve_o2_in": float,
        "readback_valve_inhale": float,
        "readback_valve_exhale": float,
        "readback_valve_purge": float,
        "readback_mode": int
    },
    "alarms": List[str]
}
```

- “sensors” refers to a dict containing all values in the `dataFormat` class
- “alarms” refers to a list of strings taken from the `alarm_codes` enum in `commsConstants.py`

Example broadcast packet:
```json
{
    "sensors": {
        "version": 160,
        "fsm_state": 0,
        "pressure_air_supply": 0,
        "pressure_air_regulated": 0,
        "pressure_o2_supply": 0,
        "pressure_o2_regulated": 0,
        "pressure_buffer": 36864,
        "pressure_inhale": 36864,
        "pressure_patient": 0,
        "temperature_buffer": 0,
        "pressure_diff_patient": 0,
        "readback_valve_air_in": 0,
        "readback_valve_o2_in": 0,
        "readback_valve_inhale": 0,
        "readback_valve_exhale": 0,
        "readback_valve_purge": 1,
        "readback_mode": 0
    },
    "alarms": [
        "APNEA"
    ]
}
```

Example alarm packet:
```json
{
    “type”: “alarm”,
    “alarms”: ["APNEA"]
}
```

### Request socket
The HEVServer class has a method to set a different mode of operation, this is done through the shared socket to avoid multiple threads writing to the same variables.

Sending data to the arduino is acheived by opening a connection to the shared request socket, sending a payload and waiting for an acknowledge before closing the connection. This is now acheived by using command packets with a cmd which is taken from the `command_codes` enum in `commsConstants.py`. These are the only commands currently supported.

#### Uplink packets
Query packet format:
```python
{
    "type": str,
    "cmdtype": str,
    "cmd”: str,
    “param”: int
}
```

Example command packet:
```json
{
    "type": "cmd",
    "cmdtype": "GENERAL",
    "cmd": "START",
    "param": null
}
```
where the value of the cmd key is a key in the `command_codes` enum from `commsConstants.py`

#### Downlink packets
Reply format:
```python
{
    “type”: str,
}
```
where type can be either `"ack"` in response to a valid command or `"nack"` in response to an invalid command


## Example `hevclient.py` Usage

```python
# just import hevclient and do something like the following
hevclient = HEVClient()


time.sleep(2)
print(hevclient.send_cmd("GENERAL", "START"))
# Play with sensor values and alarms
for i in range(20):
    values = hevclient.get_values() # returns a dict or None
    alarms = hevclient.get_alarms() # returns a list of alarms currently ongoing
    if values is None:
        i = i+1 if i > 0 else 0
    else:
        print(f"Values: {json.dumps(values, indent=4)}")
        print(f"Alarms: {alarms}")
    time.sleep(1)

# acknowledge the oldest alarm
try:
    hevclient.ack_alarm(alarms[0]) # blindly assume we have one after 40s
except:
    logging.info("No alarms received")

time.sleep(1)
print(f"Alarms: {hevclient.get_alarms()}")

# send commands:
time.sleep(1)
print("This one will fail since foo is not in the command_codes enum:")
print(hevclient.send_cmd("general", "foo"))

# print some more values
for i in range(10):
    print(f"Values: {json.dumps(hevclient.get_values(), indent=4)}")
    print(f"Alarms: {hevclient.get_alarms()}")
    time.sleep(1)

print(hevclient.send_cmd("GENERAL", "STOP"))
```

## Arduino emulator

`ArduinoEmulator.py` is a front end emulator which creates a serial port and
serves data from a dumpfile which can then be read by the hevserver as if it
were an Arduino.


To run this kill any hevserver instances which are running and run
```bash
./ArduinoEmulator.py -f <filename>
```
Dumps exist containing real data and alarms from the `hevpi1` prototype at CERN
then in another terminal, run a hevserver with the argument `--use-dump-data`:
```bash
./hevserver.py --use-dump-file
```

Note that the version of the dumpfile must match the protocol version used by
the hevserver.