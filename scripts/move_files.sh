#!/bin/bash

source config.local.ini

sshpass -p "$SSH_PASSWORD" scp -r src/ $SSH_USER@raspberrypi.local:~/Documents/
