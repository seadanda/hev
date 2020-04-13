## High Energy Ventilator (HEV)

### Raspberry Pi backend and monitoring frontend for the High Energy Ventilators project 

- Author: Adam Abed Abud <
- Mail: adam.abed.abud@cern.ch
- Last update: April 2, 2020


**Backend:** Python3, Flask, sqlite3 
**Frontend:** Javascript, HTML, ChartsJS


# Usage
Before starting the web application you will need the following packages to be installed on the RP:

```sh
sudo pip3 install flask
sudo apt-get install sqlite3
```

Start the HEV server

```sh
cd raspberry-dataserver
python3 hevserver.py

# In case you want to test with random generated numbers
python3 hevserver.py --inputFile share/byteArray.dump
```


```sh
cd raspberry-backend
python3 arduino_recorder.py
```
This will start the server and it will simulate data coming from two different sensors



Start the web application. 

```sh
cd raspberry-backend
python3 app.py
```

Start firefox with the following address:

```sh
firefox 127.0.0.1:5000
```


License
----

For the benefit of everyone.



