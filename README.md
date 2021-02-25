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

The following has been tested using Python 3.7.3 on a Raspberry Pi 4 4GB model B and Raspian Desktop VM (Buster).

### Prerequisites

Raspbian Version: Raspbian GNU/Linux 10 (buster)

Python Version: 3.7

On your local PC, install [ansible](https://docs.ansible.com/ansible/latest/installation_guide/index.html)

### Installation

Run and follow the prompts:

```bash
./setup.sh
```

For manual installation instructions please refer to [manualInstallation.md](manualInstallation.md).

## Usage

### Running the HEV UI

Running the HEV UI requires three separate python process running in the same virtualenv.

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
