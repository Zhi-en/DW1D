#!/bin/bash
#reference this file in /etc/rc.local

sudo apt-get update -y
cd /home/pi/Documents/DW1D
git checkout master
git pull
python GUI.py