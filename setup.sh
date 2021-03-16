#!/bin/bash

# This shell script uses ansible, apt-get, and pip to install all the requirements to run the HEV UI.

set -e

# Define colours
RED='\033[0;31m'
YELLOW='\033[1;33m'
ITALIC='\033[3m'
NC='\033[0m' # No Color or Syntax

# CHeck if in repo and move to top level of repo
if [[ -d $(git rev-parse --git-dir 2> /dev/null) ]]; then
    cd "$(git rev-parse --show-toplevel)"
    repo_location=$(pwd)
else
    echo "ERROR: Not a git directory. Please run setup.sh from the HEV repository."
    exit 1
fi

# Create a hosts file from default
hostsfile="ansible/playbooks/hosts"

# create and write hosts file function
function create_hostsfile {
    # Replace current hostfile with the default
    rm -f $hostsfile
    # Get users raspberry pi / VM IP address
    echo "What is the IP address for your Raspberry Pi / VM you wish to setup?"
    echo -e "${ITALIC}NOTE: If you use a non-standard SSH port (22), add the port to your IP address as such: ${YELLOW}IPADDRESS:PORT${NC}"
    echo -e "${ITALIC}NOTE: If you wish to run the ansible installation locally, please input: ${YELLOW}localhost${NC}"
    read -r ipaddr
    # Add the IP address into hosts file
    if [[ $ipaddr == "" ]]; then
        echo -e "${RED}ERROR:${NC} user input for IP Address was blank. Please rerun and enter IP Address."
        exit 1
    elif [[ $ipaddr == "localhost" ]]; then
        cp -rp ansible/playbooks/hosts.local $hostsfile
        local=True
        echo "Installing locally at $repo_location."
    else
        cp -rp ansible/playbooks/hosts.default $hostsfile
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/IPADDRESS/$ipaddr/g" $hostsfile
        else
            sed -i "s/IPADDRESS/$ipaddr/g" $hostsfile
        fi
        echo "User inputtted IP Address added to $hostsfile."
    fi
}

# Check if local flag has been used
cli_flag1=$1

if [[ $cli_flag1 == 'local' ]]; then
    cp -rp ansible/playbooks/hosts.local $hostsfile
    local=True
    echo "Installing locally at $repo_location."
elif [[ $cli_flag1 == '' ]]; then
    # Get the pi / vm ip address from user
    if [[ -f $hostsfile ]]; then
        # Check if hosts file already exists
        echo -e "${YELLOW}$hostsfile${NC} already exists, override and create a new hosts file? [y/n]"
        read -r yn
        case $yn in
            [Yy]* )
                    create_hostsfile;;
            [Nn]* ) if [[ $(sed -n 2p ansible/playbooks/hosts) == *"localhost"* ]]; then
                        local=True
                    else
                        ipaddr=$(sed -n 2p ansible/playbooks/hosts) # copy IP address in hosts file to variable ipaddr
                    fi;;
            * ) echo "Please answer yes or no."; exit 1;;
        esac
    else
        create_hostsfile
    fi
else
    echo "ERROR: Only CLI input accepted is 'local' for local installation."
    exit 1
fi

# Run ansible playbooks for both local and remote
if [[ $local == True ]]; then # Local run
    # Create local variables for ansible installation
    echo "Using ansible to setup local HEV install."
    cd ansible
    source hev-ansible.sh
    # Run ansible playbooks
    cd playbooks
    # Create local repo variable
    ansible-playbook firstboot.yml
    ansible-playbook install_software_local.yml
    # Clean up
    cd "$(git rev-parse --show-toplevel)"
    echo
    echo "SETUP FINISHED"
    echo -e "${YELLOW}Rasperberry Pi / VM must be rebooted for changes to take effect.${NC}"
    echo "Please run 'sudo reboot'."
    echo
else # Remote run
    # Create local variables for ansible installation
    echo "Using ansible to setup remote Raspberry Pi / VM."
    cd ansible
    source hev-ansible.sh
    # Run ansible playbooks
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
    echo
fi