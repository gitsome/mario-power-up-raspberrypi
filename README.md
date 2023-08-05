# mario-power-up-raspberrypi

![mario design](mario-design.png)

Code for 3D printed power up box. Manages LEDs, sound effects, weight scale, and servo motor.

## Raspberry Pi Setup

### Startup Script

Ensure your Pi is setup to launch the main script on restart:

```
sudo nano
```

The contents of this file should look something like this:

```txt
#!/bin/sh -e
#/etc/rc.local
# rc.local
#
# This script is executed at the end of each multiuser runlevel.
# Make sure that the script will "exit 0" on success or any other
# value on error.
#
# In order to enable or disable this script just change the execution
# bits.
#
# By default this script does nothing.

# Print the IP address
_IP=$(hostname -I) || true
if [ "$_IP" ]; then
  printf "My IP address is %s\n" "$_IP"
fi

sudo bash -c 'sudo python3 /home/johnmartin/Documents/src/main.py > /home/johnmartin/Documents/mario.log 2>&1' &

exit 0
```

## Developing

The scripts requires `sshpass` a linux library. On Mac install using:

```bash
brew install hudochenkov/sshpass/sshpass
```

## Scripts

From the root directory, you can run the following:

### Copy Files and Restart Python

```bash
sh scripts/changes_made.sh
```

### Reboot Raspberry Pi

```bash
sh scripts/reboot.sh
```
