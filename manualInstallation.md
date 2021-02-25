# Instructions to setup HEV software manually

## Contents

* [Ansible Setup](#ansible-setup)

### Ansible Setup

A complete copy of these instructions can be found [here](ansible/README.md).

After the initial setup of the Raspberry Pi, create an empty file called `ssh`:

```bash
sudo touch /boot/ssh
```

If you wish to login without entering a password each time, on your local PC generate a ssh keypair and copy it over to the pi:

```bash
ssh keygen
ssh-copy-id pi@RPI-IP-ADDRESS
```

Complete the following instructions on your local PC.

```bash
source ansible/hev-ansible.sh
```

Add the Raspberry Pi IP address to `ansible/playbooks/host` under `[hevpi]` and `[allpi]`. Example:

```bash
[hevpi]
192.168.1.23
```

Run the ansible playbooks.

```bash
ansible-playbook firstboot.yml
ansible-playbook install_software.yml
```

Finally reboot the pi

```bash
ssh pi@MY-RPI-IPADDRESS "sudo reboot"
```

### Installation

At the time of writing, not all dependencies could be installed using the `requirements.txt` and a number of system-wide installs were requited using apt-get. Note for PySide2, the libs need to be copied into your virtual env (if you are using virtualenv).

```bash
git clone https://ohwr.org/project/hev
cd hev
sudo apt-get update
sudo pip3 install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt
sudo apt-get install socat
sudo apt-get install libatlas-base-dev
sudo apt-get install python3-pyside2.qt3dcore python3-pyside2.qt3dinput python3-pyside2.qt3dlogic python3-pyside2.qt3drender python3-pyside2.qtcharts python3-pyside2.qtconcurrent python3-pyside2.qtcore python3-pyside2.qtgui python3-pyside2.qthelp python3-pyside2.qtlocation python3-pyside2.qtmultimedia python3-pyside2.qtmultimediawidgets python3-pyside2.qtnetwork python3-pyside2.qtopengl python3-pyside2.qtpositioning python3-pyside2.qtprintsupport python3-pyside2.qtqml python3-pyside2.qtquick python3-pyside2.qtquickwidgets python3-pyside2.qtscript python3-pyside2.qtscripttools python3-pyside2.qtsensors python3-pyside2.qtsql python3-pyside2.qtsvg python3-pyside2.qttest python3-pyside2.qttexttospeech python3-pyside2.qtuitools python3-pyside2.qtwebchannel python3-pyside2.qtwebsockets python3-pyside2.qtwidgets python3-pyside2.qtx11extras python3-pyside2.qtxml python3-pyside2.qtxmlpatterns python3-pyside2uic
cp -r /usr/lib/python3/dist-packages/PySide2  env/lib/python3.7/site-packages/
```

## Installation - VM

The following has been tested using Python 3.7.3 with a Raspian Desktop VM (Buster) which can be run in [VirtualBox](https://www.virtualbox.org/) or [VMWare Fusion Player](https://www.vmware.com/products/fusion.html).

See [Raspberry Pi Installation](#installation---rpi).

```bash
pip install git+https://github.com/hex-in/libscrc.git
```
