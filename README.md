# High Energy Ventilator

> Note: this README is a WIP.

Rapidly-producible ventilator developed with CERN and collaborating institutes for the COVID-19 pandemic.

## Contents

* [Installation](#installation)
* [Usage](#usage)
* [Testing](#testing)
* [License](#license)
* [Acknowledgments](#acknowledgments)

## Installation

The following has been tested using Python 3.7 on a Raspberry Pi 4 4GB model B and Raspbian Desktop VM (Buster).

You can install a VM using either [VirtualBox](https://www.virtualbox.org/) or [VMWare Fusion Player](https://www.vmware.com/products/fusion.html), and download the Raspbian OS from [here](https://www.raspberrypi.org/software/raspberry-pi-desktop/).

### Prerequisites

Raspbian Version: Raspbian GNU/Linux 10 (buster)

Python Version: 3.7

On your local PC, install [ansible](https://docs.ansible.com/ansible/latest/installation_guide/index.html).

### Setup

#### Using SSH

> Make sure that SSH is enabled. To check this to go:
>
> With GUI: `Preferences > Raspberry Pi Configuration > Interfaces`
>
> Without GUI: `sudo touch /boot/ssh`
>
> ***WARNING:** There may be extra steps if you are using a VM on your local machine.*

For ansible to work, you need to create an ssh keypair with your Raspberry Pi / VM. On your local PC generate a ssh keypair and copy it over to the pi:

```bash
ssh keygen
ssh-copy-id pi@IP-ADDRESS
```

To obtain the IP Address of your Raspberry Pi / VM, on your Raspberry Pi / VM run:

```bash
hostname -I
```

Run and follow the prompts:

```bash
./setup.sh
```

Ansible logs are saved in `ansible/playbooks/logs`.

#### Locally

Install ansible with the following:

```bash
pip3 install ansible
```

Clone this repo and checkout the `ui_dev` branch:

```bash
git clone https://ohwr.org/project/hev.git
git checkout ui_dev
```

Run `setup.sh` and enter `localhost` when asked for an IP address.

```bash
./setup.sh
```

Ansible logs are saved in `ansible/playbooks/logs`.

## Usage

### Running the HEV UI

Running the HEV UI requires three separate python process running in the same virtualenv from the `hev` directory.

```bash
cd /home/pi/hev
```

#### 1) Run ArduinoEmulator

Note that a selection of dump files are provided in the `raspberry-dataserver/share` dir.

```bash
source .hev_env/bin/activate
./raspberry-dataserver/ArduinoEmulator.py -f raspberry-dataserver/share/B6-20201207.dump
```

#### 2) Run hevserver in another shell

```bash
source .hev_env/bin/activate
cd raspberry-dataserver
./hevserver.py --use-dump-data
```

#### 3) Run NativeUI in another shell

```bash
source .hev_env/bin/activate
./NativeUI/NativeUI.py
```

## Testing

## License

See [LICENSE](LICENCE.txt) file.

## Acknowledgments

* LIST OF PEOPLE / INSTITUTES
* CERN
* STFC
