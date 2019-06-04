import json
import socket
import threading
import time
from PySide2 import QtCore
import queue
import threading

class NotificationSignalEmiter(QtCore.QObject):
    
    notifyRx=QtCore.Signal(list)
    updateSB=QtCore.Signal(str)
    updateSBIcon=QtCore.Signal(bool)
    
    
class UteNotificationClient(threading.Thread):
    
    ss=NotificationSignalEmiter()
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.port=22222
        self.host="targetHost"
        self.sock=None
        
        self.dataStream=""
        self.socket=None
        self.updateHost=False
        
        self.requestList=[]
        self.queue=queue.Queue()
        self.qlock=threading.Lock()
        
        self.notificationInterval=1.0
        
    def findJson(self):

        largo=len(self.dataStream)
        inicio=self.dataStream.find("{")
        fin=self.dataStream.find("}")
        
        if inicio!=-1 and fin!=-1:
            
            newJson = self.dataStream[inicio:fin+1]
            self.dataStream=self.dataStream[fin+1::]
            
            try:
                jsonLoaded=json.loads(newJson)
                return jsonLoaded
            except Exception as e:
                pass
               
        return None
       
       
    def updateTarget(self,host,port):      
        self.host=host
        self.port=port
        
        self.updateHost=True    
     
    def rxUdp(self):   
        self.sock.settimeout(5)
        while True:
            if self.updateHost:
                return ""
            try:
                data=self.sock.recv(1024)
                return data
            except socket.timeout as e:
                pass
            
    def rxUdpNotBlocking(self):   
        self.sock.settimeout(1.0)
        if self.updateHost:
            return ""
        try:
            data=self.sock.recv(1024)
            return data
        except socket.timeout as e:
            pass
        
        return None
        
    def sendRequest(self,req):
        
        msgString = json.dumps(req)
        try:
            self.sock.send(msgString.encode())
        except Exception as e:
            print(e)
       
    def readJsons(self):
        
        if self.sock==None: 
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(120.0) 
                self.sock.connect((self.host, self.port))   
                self.updateHost=False 
                self.ss.updateSB.emit("Conectado con fuente de notificaciones")
                self.ss.updateSBIcon.emit(True)
            except Exception as e:
                self.sock=None
                print(e)
        
        if self.sock!=None:
            try:
                msgList=[]
                data=self.rxUdp()
                if len(data)==0:
                    self.sock=None
                else:
                    data=data.decode('utf-8',errors="ignore")
                    self.dataStream+=data
                    
                    newJson=self.findJson()
                    while newJson!=None:
                        msgList.append(newJson)        
                        newJson=self.findJson()   
                         
                return msgList
            except Exception as e:
                print(e)
        
        return None
    
    def readJsonsNotBlocking(self):
        
        if self.sock==None: 
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(120.0) 
                self.sock.connect((self.host, self.port))   
                self.updateHost=False 
                self.ss.updateSB.emit("Conectado con fuente de notificaciones")
                self.ss.updateSBIcon.emit(True)
            except Exception as e:
                self.sock=None
                print(e)
        
        if self.sock!=None:
            try:
                msgList=[]
                data=self.rxUdpNotBlocking()
                
                if data!=None:
                    if len(data)==0:
                        self.sock=None
                    else:
                        data=data.decode('utf-8',errors="ignore")
                        self.dataStream+=data
                        
                        newJson=self.findJson()
                        while newJson!=None:
                            msgList.append(newJson)        
                            newJson=self.findJson()   
                             
                return msgList
            except Exception as e:
                print(e)
        
        return None
    
    def appendRequest(self,jsonRequest):
    
        self.requestList.append(jsonRequest)
    
    
    def groupedNotification(self):
        while True:
            lista=[]
            self.qlock.acquire()
            while not self.queue.empty():
                lista.append(self.queue.get())
            self.qlock.release()
            
            if len(lista)>0:
                self.ss.notifyRx.emit(lista)
            
            time.sleep(self.notificationInterval)
                
    def run(self):    

        threading.Thread(target=self.groupedNotification).start()

        while True:
            
            newJsons=self.readJsonsNotBlocking()
           
            if newJsons!=None:
                self.qlock.acquire()
                for x in newJsons:
                    self.queue.put(x)                    
                   # self.ss.notifyRx.emit(x)
                self.qlock.release()
                
            else:
                print("No se pudo conectar con el servidor de notificaciones, reintentando en 5 segundos")
                time.sleep(5)
                self.ss.updateSB.emit("No se pudo conectar con fuente, reintentando ...")
                self.ss.updateSBIcon.emit(False)
           
            if len(self.requestList)>0:
                req=self.requestList.pop()
                self.sendRequest(req)
           
           
            if self.updateHost:
                self.sock=None