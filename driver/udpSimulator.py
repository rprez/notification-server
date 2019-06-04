import json
import socket
import threading
import datetime
import time
import random
import sys

class UteUdpSimulator(threading.Thread):
    
    def __init__(self,host,port,count,interval):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.host=host
        self.port=port
        self.interval=interval
        
        self.count=count
        self.logSize=0
        self.temp=25
        self.uptime=0
    
        
    def gen_timestamp(self):
        # gera um datetime no formato yyyy-mm-dd hh:mm:ss.000000
        year = 2018
        month = random.randint(11, 12)
        day = random.randint(1, 28)
        hour = random.randint(1, 23)
        minute = random.randint(1, 59)
        second = random.randint(1, 59)
        microsecond = random.randint(1, 999999)
        date = datetime.datetime(
            year, month, day, hour, minute, second, microsecond)
        return date
    
    
    
    
    def randomImei(self):
        
       
        imei=""
        for i in range(0,15):
            imei+=str(random.randint(0,9))
            
        return imei
        
        
    def createRandomAlert(self):
        
        """
        { "imei":359486064904103 ,"ip":"192.168.210.18","fecha": "19-5-17 8:56:8","alert":"lastgasp sent"}
       
           { "imei":359486064904103 ,"ip":"192.168.210.18","fecha": "19-5-17 8:56:8","alert":"lastgasp sent"}
      
          { "imei":359486064903246 ,"ip":"192.168.210.16","fecha": "19-5-17 10:30:29","alert":"lastgasp sent"}
        """
        
        packet={}
        
        packet['imei']=359486064904103
        packet['ip']="192.168.210.18"
        packet['fecha']="19-5-17 10:30:29"
        packet['alert']="lastgasp sent"
        
        return packet
    def createNewRandomPacket(self):
       
        dbm=random.randint(1,100)
        self.logSize+= random.randint(1,100)
        self.uptime+=self.interval
        packet={}
        
        packet['imei']=self.randomImei()
        packet['rssi']=" -88 dmb"
        packet['ip']=str(random.randint(1,255))+"."+str(random.randint(1,255))+"."+str(random.randint(1,255))+"."+str(random.randint(1,255))
        packet['fecha']=self.gen_timestamp().strftime("%y-%m-%d %H:%M:%S")            
    
        packet['rssi']="-%d dbm"%(dbm)
        packet['EC/NO']=32
        packet['cellid']=str(random.randint(100,20000))
        packet['logSize']=self.logSize
        packet['temp']=self.temp + random.randint(1,50)/10
        packet['uptime']=self.uptime
        
        return packet
        
    def run(self):    
        
        
        while self.count>0:
            self.count-=1
            newMsg=self.createNewRandomPacket()
            txt=json.dumps(newMsg,indent=0, sort_keys=True)

            self.sock.sendto(txt.encode(), (self.host, self.port))
            time.sleep(self.interval)
           
           
print(sys.argv)
if len(sys.argv)==5:
     
    simu=UteUdpSimulator(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]))
    simu.start()
else:
    print("usage: <ip> <port> <count> <interval>")
       