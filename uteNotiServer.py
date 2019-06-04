import queue
import threading
import os
import sys
import json
import socket

from driver.utenotificationserver import StorageDbHandler 
from driver.utenotificationserver import SocketHandler_NotificationDistributor
from driver.utenotificationserver import SocketHandler_NotificationHistory
from driver.utenotificationserver import HistoryCleaner

from driver.uteUdpNotificationReceiver import UteUdpReceiver


   
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
       
    