#!/bin/bash
source config.local.ini

sshpass -p ${SSH_PASSWORD} ssh ${SSH_USER}@raspberrypi.local 'sudo pkill python && sudo python3 ~/Documents/src/main.py' &
