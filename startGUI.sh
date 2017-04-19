#!/bin/bash
# reference this file in /etc/rc.local

# sudo apt-get update -y
# cd /home/pi/Documents/DW1D

sudo git checkout master && sudo git pull && sudo python GUI.py
