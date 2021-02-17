# High Energy Ventilator

> Note: this README is a WIP.

Rapidly-producible ventilator developed with CERN and collaborating institutes for the COVID-19 pandemic.

## Contents

* [Raspberry Pi Installation](#installation---rpi)
* [Virtual Machine Installation](#installation---VM)
* [Usage](#usage)
* [Testing](#testing)
* [License](#license)
* [Acknowledgments](#acknowledgments)

## Installation - RPi

The following has been tested using Python 3.7.3 on a Raspberry Pi 4 4GB model B.

### Prerequisites

```bash
$ python3 --version
$ Python 3.7.3

$ cat /etc/os-release 
$ PRETTY_NAME="Raspbian GNU/Linux 10 (buster)"
$ NAME="Raspbian GNU/Linux"
$ VERSION_ID="10"
$ VERSION="10 (buster)"
$ VERSION_CODENAME=buster
$ ID=raspbian
$ ID_LIKE=debian
$ HOME_URL="http://www.raspbian.org/"
$ SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
$ BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"
```

### Installation

At the time of writing, not all dependencies could be installed using the `requirements.txt` and a number of system-wide installs were requited using apt-get. Note for PySide2, the libs need to be copied into your virtual env (if you are using virtualenv).

```bash
$ git clone https://ohwr.org/project/hev
$ cd hev
$ sudo apt-get update
$ sudo pip3 install virtualenv
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ sudo apt-get install socat
$ sudo apt-get install libatlas-base-dev
$ sudo apt-get install python3-pyside2.qt3dcore python3-pyside2.qt3dinput python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml python3-pyside2.qtxmlpatterns python3-pyside2uic
$ cp -r /usr/lib/python3/dist-packages/PySide2  env/lib/python3.7/site-packages/
```

## Installation - VM

The following has been tested using Python 3.7.3 with a Raspian Desktop VM (Buster) which can be run in [VirtualBox](https://www.virtualbox.org/) or [VMWare Fusion Player](https://www.vmware.com/products/fusion.html).

See [Raspberry Pi Installation](#installation---rpi).

### Prerequisites

bar

### Installation

For VM, you may also need:

```bash
pip install git+https://github.com/hex-in/libscrc.git
```

## Usage

### Running the HEV UI

Running the HEV UI requires three separate python process running in the same virtualenv.

#### 1) Run ArduinoEmulator

Note that a selection of dump files are provided in the `raspberry-dataserver/share` dir.

```bash
$ raspberry-dataserver/ArduinoEmulator.py -f raspberry-dataserver/share/B6-20201207.dump
```

#### 2) Run hevserver in another shell

```bash
$ source env/bin/activate
$ cd raspberry-dataserver
$ ./hevserver.py --use-dump-data
```

#### 3) Run NativeUI in another shell

```bash
$ source env/bin/activate
$ ./NativeUI/NativeUI.py
```

## Testing

## License

See [LICENSE](LICENCE.txt) file.

## Acknowledgments

* LIST OF PEOPLE / INSTITUTES
* CERN
* STFC
