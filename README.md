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

Ansible: Version 2.8 or later

### Setup

There are 2 methods of installation, [using SSH](#ssh-installation) or installing [locally](#local-installation). Both methods can be used with both a Raspberry Pi and a VM depending on your setup and personal preference.

The advantage of SSH is that the Raspberry Pi does not need dedicated peripherals and you can make use of your local development environment. However, there is no control over the default installation location (`/home/pi/hev`). Whereas, the local installation method installs all the requirements in the location you clone this repo to.

#### SSH Installation

On your local PC, install [ansible](https://docs.ansible.com/ansible/latest/installation_guide/index.html) at least version 2.8. The easiest way to do this via `pip`:

```bash
pip3 install ansible
```

> Make sure that SSH is enabled. To check this to go:
>
> With GUI: `Preferences > Raspberry Pi Configuration > Interfaces`
>
> Without GUI: `sudo touch /boot/ssh`
>
> ***WARNING:** There may be extra steps if you are using a VM on your local machine.*

For ansible to work, you need to create an ssh keypair with your Raspberry Pi / VM. On your local PC generate a ssh keypair and copy it over to the pi:

```bash
ssh-keygen
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

#### Local Installation

Change default Python to Python3.7:

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2
```

Install ansible with the following:

```bash
pip3 install ansible
sudo reboot
```

Clone this repo and checkout the `release/ui` branch:

```bash
git clone https://ohwr.org/project/hev.git
cd hev
git checkout ui_dev
```

Run `setup.sh` and enter `localhost` when asked for an IP address.

```bash
./setup.sh
```

Ansible logs are saved in `ansible/playbooks/logs`.

## Usage

### Running the HEV UI

Running the HEV UI requires three separate python process running in the same virtualenv from the `hev` directory. This varies depending on your installation method as follows:

* Remote Installation:

    ```bash
    cd /home/pi/hev
    ```

* Local Installation:

    ```bash
    cd /path/to/hev
    ```

1) Run ArduinoEmulator

    Note that a selection of dump files are provided in the `raspberry-dataserver/share` dir.

    ```bash
    source .hev_env/bin/activate
    ./raspberry-dataserver/ArduinoEmulator.py -f raspberry-dataserver/share/B6-20201207.dump
    ```

2) Run hevserver in another shell

    ```bash
    source .hev_env/bin/activate
    cd raspberry-dataserver
    ./hevserver.py --use-dump-data
    ```

3) Run NativeUI in another shell

    ```bash
    source .hev_env/bin/activate
    ./NativeUI/NativeUI.py
    ```

### Command-Line Arguments
NativeUI.py accepts the following command line arguments:

| Command | Pattern(s) | Effect | Example |
|---------|------------|--------|---------|
| Windowed | -w, --windowed | Create the user interface in windowed mode | ```./NativeUI/NativeUI.py -w``` |
| Debug | -d, --debug | Set the logging output level. By default only log messages of ERROR or higher priority will be displayed. The debug flag changes this to messages of INFO or higher if provided once, or DEBUG or higher if provided twice. | ```./NativeUI/NativeUI.py -dd```|
| Resolution | -r , --resolution | Takes the following string as specifying the desired size of the UI in pixels. Resolutions should be two integers separated by a non-numerical character. | ```./NativeUI/NativeUI.py -r 1600x900```

## Testing

For full testing documentation please refer to the [testing README](NativeUI/tests/README.md).

## Unit Tests

To run the unit tests on a Raspberry Pi or VM, run the following:

```bash
source .hev_env/bin/activate
pytest NativeUI
```

### Coverage

To get pytest coverage run from the root of the repo:

```bash
pip install pytest-cov
pytest --cov=NativeUI NativeUI
```

## License

See [LICENSE](LICENCE.txt) file.

## Acknowledgments

* LIST OF PEOPLE / INSTITUTES
* CERN
* STFC
