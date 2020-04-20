#!/bin/bash
wget -qO - https://hev-sw.gitlab.io/public.key | sudo apt-key add - && echo deb https://hev-sw.gitlab.io/wip/deb/raspbian/ buster main | sudo tee /etc/apt/sources.list.d/hev-sw.list
