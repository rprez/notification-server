import json
import socket
import threading
 
class UteUdpReceiver(threading.Thread):
    
    def __init__(self,port,udpQueue,queueLock):
        threading.Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.port=port
        self.udpQueue=udpQueue
        self.queueLock=queueLock
    
    
    def parseDataToJson(self,data):
        try:
            parsedJson=json.loads(data)
            
            return parsedJson           
        except Exception as e:
            #correccion de bug en firmware 1.63
            if "\"rssi\" : \" \"" in data:
                data=data.replace("\"rssi\" : \" \"","\"rssi\" : \"")
                try:
                    parsedJson=json.loads(data)            
                    return parsedJson 
                except Exception as e:
                    pass
        return None   
                
    
    def run(self):    
        
        self.sock.bind(("",self.port))
    
        while True:
            data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
            strData=data.decode('ascii')
            print ("received message from :"+ strData)
            
            parsedJson=self.parseDataToJson(strData)
          #  print(parsedJson)
            if parsedJson:
                self.queueLock.acquire()
                self.udpQueue.put(parsedJson)
                self.queueLock.release()
            else:
                print("Error parsing json: " + strData)
            
           