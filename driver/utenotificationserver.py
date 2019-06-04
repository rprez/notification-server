import json
import socket
import threading
from datetime import datetime
import queue
import time
import os
import shutil
from driver.NotificationDBStorage import NotificationDatabase
import sys

def parseDate(dir):
    
    pedazos=dir.split("-")
    if len(pedazos)==3:
        try:
            y=int(pedazos[0])
            m=int(pedazos[1])
            d=int(pedazos[2])
                        
            return datetime(year=y,month=m,day=d)
        except Exception as e:
            return None
    
    return None

def borrarHistorialViejo(diasConservados):
    
    fechaHoy=datetime.now()
    dirs=os.listdir("./history")
    for d in dirs:
        fechaDir=parseDate(d)
        if fechaDir!=None:
            if (fechaHoy - fechaDir).days > diasConservados:
                print("es necesario borrar directorio %s"%(d))
                try:
                    shutil.rmtree("./history/"+d)
                    print("directorio %s borrado"%(d))
                except Exception as e:
                    print (e)
                    print("directorio %s no se puedo borrar"%(d))

def getFolder(msg):
    
    return msg['fecha'].split(" ")[0]


def saveNoticationToDiskTest(msg):
    subFolderDay = getFolder(msg)                      
    if not os.path.exists("history/" + subFolderDay):
        os.makedirs("history/" + subFolderDay)
         
    if "ip" in msg:
        
        msgString = json.dumps(msg, indent=0, sort_keys=False)
        iptext = msg["ip"]
        iptext = iptext.replace(".", "_")
        fname = "history/" + subFolderDay + "/" + iptext + datetime.now().strftime('_%Y-%m-%d-%H-%M-%S-%f') + ".json"
                       
        saveStringToFile(fname, msgString)


def saveNoticationToDisk(msg):
    subFolderDay = datetime.now().strftime('%Y-%m-%d')                            
    if not os.path.exists("history/" + subFolderDay):
        os.makedirs("history/" + subFolderDay)
         
    if "ip" in msg:
        
        msgString = json.dumps(msg, indent=0, sort_keys=False)
        iptext = msg["ip"]
        iptext = iptext.replace(".", "_")
        fname = "history/" + subFolderDay + "/" + iptext + datetime.now().strftime('_%Y-%m-%d-%H-%M-%S-%f') + ".json"
                       
        saveStringToFile(fname, msgString)


def saveStringToFile(fname, msgEnString):
    
    archivo = open(fname, "w+")        
    archivo.write(msgEnString)                       
    archivo.close()   

class HistoryCleaner (threading.Thread):
    
    def __init__(self,diasConservados):
                threading.Thread.__init__(self)
                
                self.diasConservados = diasConservados         
    
    def run(self):     
    
        while True:            
            borrarHistorialViejo(self.diasConservados)
            time.sleep(60)

        
class StorageDbHandler (threading.Thread):
    
    def __init__(self,dbConfig,sq,sqlock):
                threading.Thread.__init__(self)
                
                self.dbConfig=dbConfig
                self.sq=sq
                self.sqlock=sqlock
                self.tableName="notifications"
                #self.diasConservados = diasConservados         
    
    def run(self):     
    
        self.db=NotificationDatabase(self.dbConfig['dbName'], self.dbConfig['dbUser'], self.dbConfig['dbPass'],self.dbConfig['host'])
        
        try:
            self.db.connect()
            self.db.doBasicSetup(self.tableName)
        except Exception as e:
            print(e)
            exit(0)
            
        while True:            
            toSave=[]
            self.sqlock.acquire()
            while not self.sq.empty():
                toSave.append(self.sq.get())
            self.sqlock.release()
            
            
            if len(toSave)>0:
                self.db.storeNotification(self.tableName,toSave)
            time.sleep(1)

        
        
        
class SocketHandler_NotificationDistributor (threading.Thread):
    
    def __init__(self, socketQueue, socketLock, udpQueue, udpLock,sq,sqlock,storageMode):
                threading.Thread.__init__(self)
                
                self.socketQueue = socketQueue       
                self.socketLock = socketLock
                
                self.udpQueue = udpQueue
                self.udpLock = udpLock    
                
                self.socketList = []   
                
                self.sq=sq
                self.sqlock=sqlock 
                self.storageMode=storageMode
    
    def sendMsg(self, sockDict, jsonMsg):
        
        try:
            msgString = json.dumps(jsonMsg, indent=0, sort_keys=False)
            sockDict['lock'].acquire()
            sockDict['socket'].send(msgString.encode())
            sockDict['lock'].release()

            return True
        except Exception as e:
            print(e)
                    
        sockDict['lock'].release()
        return False   
    
    def run(self):     
    
        while True:            

            # check if new sockets to append            
            if not self.socketQueue.empty():
                self.socketLock.acquire()
                while not self.socketQueue.empty():
                    newSocketDict=self.socketQueue.get()                    
                    self.socketList.append(newSocketDict)
                self.socketLock.release()
                
            # distribute new Messages            
            if not self.udpQueue.empty():
                msgs = []
                self.udpLock.acquire()
                while not self.udpQueue.empty():
                    msgs.append(self.udpQueue.get())
                self.udpLock.release()
                
                socketsToBeRemoved = []
                for m in msgs:
                    for s in self.socketList:                   
                        if not self.sendMsg(s, m):
                            socketsToBeRemoved.append(s)
                            break
                    
                    if storageMode=="db":
                        self.sqlock.acquire()
                        self.sq.put(m)
                        self.sqlock.release()
                    elif storageMode=="file":
                        saveNoticationToDiskTest(m)
                    
                if len(self.socketList) == 0:
                    print("Discarting %d notificacion" % (len(msgs)))
                    
                for s in socketsToBeRemoved:
                    self.socketList.remove(s) 
                    
            else:
                time.sleep(1)


class SocketHandler_NotificationHistory (threading.Thread):
    
    def __init__(self,socketList):
                threading.Thread.__init__(self)
                
                self.socketList = socketList 
    
    def __findJson(self,text):
        
        inicio=text.find("{")
        fin=text.find("}")
        newJson=""
        if inicio!=-1 and fin!=-1:            
            newJson = text[inicio:fin+1]
                        
            try:
                jsonLoaded=json.loads(newJson)
                return [jsonLoaded,fin]
            except Exception as e:
                print("cant parse:")
                print(newJson)
    
        return [None,0]   
               
    def checkIfRequestPending(self,sockDict):
        
        if not ("stream" in sockDict):
            sockDict['stream']=""
      
       
        [pendingJsonRequest,pendingFin]=self.__findJson(sockDict['stream'])
        if pendingJsonRequest!=None:
            sockDict['stream']=sockDict['stream'][pendingFin+1::]
            return pendingJsonRequest
        
        try:  
            sockDict['lock'].acquire()
            sockDict['socket'].setblocking(False)
            data=sockDict['socket'].recv(1024)
            sockDict['socket'].setblocking(True)
            sockDict['lock'].release()
           
            if len(data)==0:
                return None
              
            data=data.decode('utf-8',errors="ignore")
            sockDict['stream']+=data
            
            
            [jsonResult,fin]=self.__findJson(sockDict['stream'])
            if jsonResult!=None:
               
                sockDict['stream']=sockDict['stream'][fin+1::]
                return jsonResult
            
        except Exception as e:
            sockDict['socket'].setblocking(True)
            sockDict['lock'].release()
        #    print(e)
            
            
        return None
    
    def sendMsg(self, sockDict, jsonMsg):
        try:
            msgString = json.dumps(jsonMsg, indent=0, sort_keys=False)
            sockDict['lock'].acquire()
            sockDict['socket'].send(msgString.encode())
            sockDict['lock'].release()

            return True
        except Exception as e:
            pass# print(e)
                    
        sockDict['lock'].release()
        return False   
    
    
    def checkTargetStr(self,targetFilter,targetName):
        if targetFilter =="*":
            return True
        else:
            return False
        return False
    
    def isTarget(self,targetFilter,targetName):
        
        if isinstance(targetFilter,str):
            return self.checkTargetStr(targetFilter,targetName)
        elif isinstance(targetFilter,list):
            for x in targetFilter:
                if self.checkTargetStr(x,targetName):
                    return True
                
        return False        
    
    def getNotificationFromFiles(self,inicio,fin,target):
     
        lista =[]

        dirs=os.listdir("./history")
 
        for d in dirs:
            fechaDir=parseDate(d)
            if fechaDir!=None:
                if  fechaDir>=inicio and fechaDir <=fin:
                    
                    fileNames = os.listdir("./history/"+d)
                   
                    for fileName in fileNames:
                        if self.isTarget(target, fileName):
                            oldNoti=json.load(open("./history/"+d+"/"+fileName))
                            lista.append(oldNoti)
                            
        return lista
    
    def getNotification(self,inicio,fin,target):
        
        lista=[]
        
        lista=self.getNotificationFromFiles(inicio, fin, target)
        
        
        return lista
        
    
    def proccessHistoryRequest(self,request):
        
        result=[]
        if "inicio" in request and "fin" in request:
            
            inicio = datetime.strptime(request['inicio'],"%Y-%m-%d %H:%M:%S")
            fin = datetime.strptime(request['fin'],"%Y-%m-%d %H:%M:%S")
            
            requestTarget=""
            if "target" in request:
                requestTarget=request['target']
            
            result=self.getNotification(inicio, fin, requestTarget)
            
        return result
                
    
    def run(self):     
    
        while True:            
        
            for sd in self.socketList:
                requestJson=self.checkIfRequestPending(sd)
                
                if requestJson!=None:
                  #  print("New history Request")
                  #  print(requestJson)
                    
                    
                    requestResult=self.proccessHistoryRequest(requestJson)
                    for x in requestResult:
                     #   print(x)
                        self.sendMsg(sd, x)
                    #handle request.....!!!
                    
            
            time.sleep(0.5)   
       
        
if __name__ == "__main__":
    HOST, PORT = "", 15353   
    udpPort = 12345
   
    if not os.path.exists("history"):
        os.makedirs("history")
  
    storageMode="db"
    if len(sys.argv)==2:
        if sys.argv[1]=="-filedb":
            storageMode="file"
        
    
    storageQueue=queue.Queue()
    storageQueueLock=threading.Lock()
    config={}
    dbHandler=None
    
    if storageMode=="db":
        try:
            config=json.load(open("udpserverconfig.json"))
          
        except Exception as e:
            print("Error al cargar configuracion")
            print(e)  
            exit(0)
        
        try:  
            dbHandler=StorageDbHandler(config, storageQueue, storageQueueLock)
            dbHandler.setDaemon(True)
            dbHandler.start()    
        except Exception as e:
            print("Error al conectar con base de datos")
            print(e)  
            exit(0)
        
            
      
   # udpSimulator=UteUdpSimulator("localhost",12345,0.1)
  #  udpSimulator.setDaemon(True)
  #  udpSimulator.start()
   
   # #notification receiver
    udpQueue = queue.Queue()
    udpLock = threading.Lock()
    udpReceiver = UteUdpReceiver(udpPort, udpQueue, udpLock)
    udpReceiver.setDaemon(True)
    udpReceiver.start()
    
    

    
   # #notification distributor
    newSocketQueue = queue.Queue()
    newSocketLock = threading.Lock()
    
    
    resender = SocketHandler_NotificationDistributor(newSocketQueue, newSocketLock, udpQueue, udpLock, storageQueue,storageQueueLock,storageMode)
    resender.setDaemon(True)
    resender.start()
    
    # conection receiver
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(20)
    
    
    
    historyHandler=SocketHandler_NotificationHistory(resender.socketList)
    historyHandler.setDaemon(True)
    historyHandler.start()
    
    historyCleaner=HistoryCleaner(30)
    historyCleaner.setDaemon(True)
    historyCleaner.start()
    
    
    while True:

        print("Waiting connection")
        print("Active Thread Count Before enviarFile: %d" % (threading.activeCount()))
        client, fromaddr = server_socket.accept()                
         
        newSocketLock.acquire()
        newLock=threading.Lock()
        newDict={}
        newDict['socket']=client
        newDict['lock']=newLock
        newSocketQueue.put(newDict)
        newSocketLock.release()
        print("Connection accepted from ")
        print(fromaddr)
        ip = fromaddr[0]
       
    
