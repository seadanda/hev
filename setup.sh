#!/bin/bash

# This shell script uses ansible, apt-get, and pip to install all the requirements to run the HEV UI.

set -e

# Define colours
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Move to top level of repo
cd "$(git rev-parse --show-toplevel)"

# Get the pi / vm ip address from user
echo "What is the IP address for your Raspberry Pi / VM you wish to setup?"
read -r ipaddr

# Create a hosts file from default
hostsfile="ansible/playbooks/hosts"
rm -f $hostsfile
cp -rp ansible/playbooks/hosts.default $hostsfile


# Add the IP address into hosts file
if [[ $ipaddr != "" ]]; then 
sed -i '' "s/IPADDRESS/$ipaddr/" $hostsfile 
else
echo -e "${RED}ERROR:${NC} user input for IP Address was blank. Please rerun and enter IP Address."
exit 1
fi
echo "User inputtted IP Address added to $hostsfile."

# Create local variables for ansible installation
echo "Using ansible to setup Raspberry Pi / VM."
cd ansible
source hev-ansible.sh
cd playbooks
ansible-playbook firstboot.yml
ansible-playbook install_software.yml

# Clean up
cd "$(git rev-parse --show-toplevel)"

# Request to reboot raspberry pi / VM
echo
echo "SETUP FINISHED"
echo -e "${YELLOW}Rasperberry Pi / VM must be rebooted for changes to take effect.${NC}"
echo "Please run 'ssh pi@$ipaddr \"sudo reboot\"'."