#!/usr/bin/env python

from __future__ import print_function

import web, mca66, sys, json, time, logging

logfile = '/var/log/mca66_server/server.log'
serial_port = '/dev/ttyUSB0'

# set up logger
logging.basicConfig(filename=logfile,level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


# get the MCA66 object
audio = mca66.MCA66(serial_port)

# open the audio device - wait until we can reach it.  Most common reason - power is off on the Amp
logging.info("Opening MCA66 at %s",serial_port)
while audio.open() is False:
    logging.warning("Could not open MCA-66 comm - is it on? Retrying in 15s...")
    time.sleep(15)

# define list of commands we handle
commands = ['allon','alloff','pwr','volup','voldwn','setvol','setinput','togglemute','status','getzonelabels']
            
# urls for the web app
urls = (
    '/', 'index',
    '/mca66', 'controller'
)

# respond to /
class index:
    def GET(self):
        return "MCA-66 Home Audio System Controller"

# respond to /mca66
class controller:

    def GET(self):
        print("Received GET")
        # we're going to return JSON
        web.header('Content-Type', 'application/json')
        # Grab the arguements from the URL
        user_data = web.input()
        logging.debug("user_data:",user_data)
        
        # do some input validation
        if 'command' in user_data:
            command = user_data.command.lower()
            if command in commands: 
                logging.info("Processing...",command)
                zone = int(user_data.zone) if 'zone' in user_data else None
                value = int(user_data.value) if 'value' in user_data else None

                # Process the commnads
                if command == "status":
                    if zone:
                        audio.queryZone(zone)
                    else:
                        logging.error("Error - no zone specified.")
                elif command == "allon":
                    audio.setPower(0, 1)
                elif command == "alloff":
                    audio.setPower(0, 0)
                elif command == "pwr":
                    if zone and value is not None:
                        audio.setPower(zone, value)
                    else:
                        loggin.error("Zone or Value not specified: Zone: %s, Value: %s",zone,value)
                elif command == "volup":
                    if zone:
                        audio.volUp(zone)
                    else:
                        logging.error("Error - no zone specified.")
                elif command == "voldwn":
                    if zone:
                        audio.volDwn(zone)
                    else:
                        logging.error("Error - no zone specified.")
                elif command == "setvol":
                    if zone and value is not None:
                        audio.setVol(zone, value)
                    else:
                        loggin.error("Zone or Value not specified: Zone: %s, Value: %s",zone,value)
                elif command == "setinput":
                    if zone and value:
                        audio.setInput(zone, value)
                    else:
                        loggin.error("Zone or Value not specified: Zone: %s, Value: %s",zone,value)
                elif command == "togglemute":
                    if zone:
                        audio.toggleMute(zone)
                    else:
                        logging.error("Error - no zone specified.")
                elif command == "getzonelabels":
                    return json.dumps(audio.getZoneNames())
            else:
                loggin.warning("Invalid command specified:", command)
        else:
            logging.warning("No command specified")

        # give the Amp time to reply 
        time.sleep(0.5)
        
        return json.dumps(audio.status())
    

if __name__ == "__main__":

    app = web.application(urls, globals())
    app.run()
