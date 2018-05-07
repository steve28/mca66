from __future__ import absolute_import, division, print_function
import serial, time, logging

class MCA66:
    
    def __init__(self, device, to=1):
        logging.debug("Init...")
        lines = filter(None, (line.strip() for line in open("zones_list.txt")))
        self.zone_names = {int(a): b for a,b in [line.split(':') for line in lines]}
        self.input_names = filter(None, (line.strip() for line in open("sources_list.txt")))
        self.device = device
        self.to = 1
        self.zonelist = {k+1:{'power':None,'input':None,'vol':None,'mute':None,'input_name':None} for k in range(6)}
    def __enter__(self):
        logging.debug("Enter...")
        self.open()
        return self
        
    def __exit__(self ,type, value, traceback):
        logging.debug("Exit...")
        self.ser.close()
        
    def getZoneNames(self):
        return self.zone_names

    def open(self):
        self.ser = serial.Serial(port=self.device, baudrate = 38400, timeout=self.to)
        self.ser.flushInput()
        if self.commCheck():
            return True
        else:
            return False
        
    def commCheck(self):
        cmd=bytearray([0x02,0x00,0x01,0x08,0x00])
        cmd.append(self.checksum(cmd))
        self.ser.write(cmd)
        x=self.ser.read(13).decode("utf-8")
        if len(x)==13 and x=='Wangine_MCA66':
            logging.debug('MCA-66 detected. Received: %s', str(x))
            return True
        else:
            logging.warning("Could not communicate with MCA-66.")
            return False

    def checksum(self, message):
        cs = 0
        for b in message:
            cs=cs+b
        csb=cs&0xff
        return csb
    
    def printzone(self, zone):
        logging.debug("Zone: %s", zone)
        logging.debug("Power: %s", self.zonelist[zone]['power'])
        logging.debug("Input: %s", self.zonelist[zone]['input'])
        logging.debug("Input Name: %s", self.zonelist[zone]['input_name'])
        logging.debug("Volume: %s",self.zonelist[zone]['vol'])
        logging.debug("Mute: %s", self.zonelist[zone]['mute'])

    def parse_reply(self, message):
        zone = message[2]
        self.zonelist[zone]['power'] = "on" if (message[4] & 1<<7)>>7 else "off"
        self.zonelist[zone]['input'] = message[8]+1
        self.zonelist[zone]['input_name'] = self.input_names[message[8]]
        self.zonelist[zone]['vol'] = message[9]-195 if message[9] else 0
        self.zonelist[zone]['mute'] = "on" if (message[4] & 1<<6)>>6 else "off"
    
    def get_reply(self):
        msg_count = 0
        done=False
        time.sleep(0.05)
        while self.ser.inWaiting()>0:
            reply=bytearray(self.ser.read(14))    
            if len(reply)==0:
                break
                
            #else:
            #    print("Other message:",hex(reply[3]))
            #    continue
            if reply[3]!=0x05:
                #print("*** Zone Status:", reply[2])
                logging.debug("Other message:",hex(reply[3]))
                continue
            #print("*** Zone Status:", reply[2])

            if len(reply) != 14:
                logging.debug("Full messasge not received.")
                continue
 
            if ord(reply[-1:]) != self.checksum(reply[:-1]):
                logging.debug("Message Failed checksum!")
                continue

            msg_count=msg_count+1
            #print("reply",[hex(reply[i]) for i in range(14)] )
            #self.printzone(reply)
            self.parse_reply(reply)

        return msg_count

   
    def setInput(self, zone, input):
        if zone not in range(1,7):
            logging.warning("Invalid Zone")
            return    
        if input not in range(1,7):
            logging.warning("invalid input number")
            return   
        cmd = bytearray([0x02,0x00,zone,0x04,input+2])
        self.send_command(cmd)
    
    def volUp(self, zone):
        if zone not in range(1,7):
            logging.warning("Invalid Zone")
            return    
        cmd = bytearray([0x02,0x00,zone,0x04,0x09])
        self.send_command(cmd)

    def volDwn(self, zone):
        if zone not in range(1,7):
            logging.warning("Invalid Zone")
            return    
        cmd = bytearray([0x02,0x00,zone,0x04,0x0A])
        self.send_command(cmd)

    def setVol(self, zone, vol):
        #print(self.zonelist)
        if vol not in range(0,62):
            logging.warning("Invald Volume")
            return
        #print("Requested:",vol)
        #print("Current:", self.zonelist[zone]['vol'])
        #print("Zone:",self.zonelist[zone])
        volDiff = vol-self.zonelist[zone]['vol']
        start_time = time.time()
        if volDiff < 0:
            for k in range(abs(volDiff)):
                self.volDwn(zone)
        elif volDiff > 0:
            for k in range(volDiff):
                self.volUp(zone)
        else:
            pass
        #print("Vol Change took",time.time()-start_time,"seconds to do",volDiff,"steps")
        return
        
    def toggleMute(self, zone):
        if zone not in range(1,7):
            logging.warning("Invalid Zone")
            return    
        cmd = bytearray([0x02,0x00,zone,0x04,0x22])
        self.send_command(cmd)    

    def queryZone(self, zone):
        if zone not in range(1,7):
            logging.warning("Invalid Zone")
            return
        cmd = bytearray([0x02,0x00,zone,0x06,0x00])    
        self.send_command(cmd)

    def setPower(self, zone, pwr):
        if zone not in range(0,7):
            logging.warning("Invalid Zone")
            return    
        if pwr not in [0,1]:
            logging.warning("invalid power command")
            return
        if zone==0:
            cmd = bytearray([0x02,0x00,zone,0x04,0x38 if pwr else 0x39])
        else:
            cmd = bytearray([0x02,0x00,zone,0x04,0x20 if pwr else 0x21])
        
        self.send_command(cmd)

    def send_command(self, cmd):
        cmd.append(self.checksum(cmd))
        self.ser.write(cmd)
        self.get_reply() 

    def status(self):
        return self.zonelist