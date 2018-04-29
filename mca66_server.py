#!/usr/bin/env python

from __future__ import print_function

import web, mca66, sys, json
# Open the serial port to communicate with the MCA-66
# Exit if it fails.

# Defults
logfile = open('/var/log/mca66_server/server.log','w',0)
sys.stdout = logfile
sys.stderr = logfile

audio = mca66.MCA66('/dev/ttyUSB0')
if audio.open() is False:
    print("False!!")
    sys.exit()

# define list of commands we handle
post_commands = ['allon','alloff','pwr','volup','voldwn','setvol','setinput','togglemute']
get_commands = ['status','getzonelabels']
            

urls = (
    '/', 'index',
    '/mca66', 'controller'
)

class index:
    def GET(self):
        return "MCA-66 Home Audio System Controller"

class controller:

    def GET(self):
        print("Received GET")
        # we're going to return JSON
        web.header('Content-Type', 'application/json')
        # Grab the arguements from the URL
        user_data = web.input()
        print("user_data:",user_data)
        #print user_data, commands
        # do some input validation
        if 'command' in user_data:
            command = user_data.command.lower()
            if command in get_commands: 
                print("Processing...",command)
                zone = int(user_data.zone) if 'zone' in user_data else None
                
                # Process the commnads
                if command == "status":
                    if zone:
                        audio.queryZone(zone)
                    else:
                        print("Error.")
                elif command == "getzonelabels":
                    return json.dumps(audio.getZoneNames())
            else:
                print("Invalid command specified:", command)
        else:
            print("No command specified")
             
        return json.dumps(audio.status())
    
    def POST(self):
        # Grab the arguements from the URL
        user_data = web.input()
        # we're going to return JSON
        web.header('Content-Type', 'application/json')
        
        print("Received POST")
        print("user_data:",user_data)
        print("data:", web.data())
        if 'command' in user_data:
            command = user_data.command.lower()
            if command in post_commands: 
                print("Processing...",command)
                zone = int(user_data.zone) if 'zone' in user_data else None
                value = int(user_data.value) if 'value' in user_data else None
            
                # Process the commnads
                if command == "allon":
                    audio.setPower(0, 1)
                elif command == "alloff":
                    #print "AllOff!!!!"
                    audio.setPower(0, 0)
                elif command == "pwr":
                    if zone and value is not None:
                        audio.setPower(zone, value)
                    else:
                        print("Error.")
                elif command == "volup":
                    if zone:
                        audio.volUp(zone)
                    else:
                        print("Error.")
                elif command == "voldwn":
                    if zone:
                        audio.volDwn(zone)
                    else:
                        print("Error.")
                elif command == "setvol":
                    if zone and value is not None:
                        audio.setVol(zone, value)
                    else:
                        print("Error.")
                elif command == "setinput":
                    if zone and value:
                        audio.setInput(zone, value)
                    else:
                        print("Error.")
                elif command == "togglemute":
                    if zone:
                        audio.toggleMute(zone)
                    else:
                        print("Error.")
            else:
                print("Invalid command specified:", command)
        else:
            print("No command specified")
             
        return json.dumps(audio.status())

if __name__ == "__main__":

    app = web.application(urls, globals())
    app.run()
