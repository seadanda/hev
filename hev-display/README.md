# HEV display software

## Impoving performance

The interface should be responsive regardless of the incoming data rate provided.
If this isn't the case, one of the following actions should fix the issue:

* Enable OpenGL by starting with `hev-display --opengl`
* Ensure the screen resolution is appropriate, 1080p or 720p should both be fine
* Increase the fraction of memory allocated to th GPU in `sudo raspi-config` > `Advanced Options` > `Memory Split`

## Building directly on a Rasberry pi

These instructions have been tested on the Rasberry Pi 3B+ and Rasberry Pi 4.

### Install dependencies (these might not all be needed as Qt is already built)

```bash
sudo apt-get install cmake libglvnd-dev build-essential libfontconfig1-dev libdbus-1-dev libfreetype6-dev libicu-dev libinput-dev libxkbcommon-dev libsqlite3-dev libssl-dev libpng-dev libjpeg-dev libglib2.0-dev libraspberrypi-dev
```

# Download prebuilt Qt 5.12 binaries

```bash
curl -L https://chrisburr.me/hev/opt-Qt5.12.tar.gz > ~/Downloads/opt-Qt5.12.tar.gz
sudo mkdir -p /opt/Qt5.12
cd /opt/Qt5.12
sudo tar xvf ~/Downloads/opt-Qt5.12.tar.gz
```

# Clone the sources

```bash
mkdir -p ~/
cd ~/
git clone git@gitlab.com:hev-sw/hev-display.git
cd hev-display
```

# Build the sources with CMake

```bash
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=../install -DCMAKE_PREFIX_PATH=/opt/Qt5.12/lib/cmake ..
make VERBOSE=1 install -j4
```

# Run the display

```bash
LD_LIBRARY_PATH=/opt/Qt5.12/lib QML2_IMPORT_PATH=/opt/Qt5.12/qml QML_IMPORT_PATH=/opt/Qt5.12/qml /home/pi/Development/hev-display/install/bin/hev-display --opengl
```
