# mca66
This is the serial controller that implements a REST API for the Home Theater Direct MCA-66 Home Audio distribution amplifier. 

# Files
* zone_list.txt: This file is a text file containing the list of zone names
* sources_list.txt: This file is a text file containing the list of source names
* mca66.py: this is the class I wrote for the MCA-66 controller
* mca66_server.py: this is the main python script you run - assumes the above files are in the same directory as this script
* mca66_server.sh: I run this on a raspberry pi, so I use this in /etc/init.d/ so it will run at startup.  It assumes everything is installed in /usr/local/bin/mca66_server/

