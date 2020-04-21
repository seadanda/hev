# Installing the Raspberry Pi 

- First assumption - we're using latest Raspbian 
- Install Raspbian with the Raspberry Pi imager https://www.raspberrypi.org/downloads/
- In the boot partition of the SD card create and empty file called `ssh`
- Boot as default and set your preferred options for country, password, etc.

> From command line on your local PC (not the pi):
- copy your ssh keys if you don't want a password every time
    - ssh-copy-id pi@MY-RPI-IPADDRESS
- then setup ansible:
    - install ansible on your local PC with your package manager
    - download the hev-sw repo:

```
git clone https://github.com/hev-sw/hev-sw
cd hev-sw/ansible
source hev-ansible.sh
cd playbooks
```
- add the address of your Raspberry Pi to the `hosts` file under the section `[hevpi]`
    - example : 
```
[hevpi]
192.168.1.23
```
- run the ansible playbooks
```
ansible-playbook firstboot.yml
ansible-playbook install_software.yml
```
- finally reboot the pi
```
ssh pi@MY-RPI-IPADDRESS "sudo /sbin/reboot"
```

