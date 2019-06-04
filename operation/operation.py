from driver.uteTelnetDriver import UteTelnetDriver

import threading
import queue
import datetime
import os
import traceback

def saveCrashReport(exceptionText):
        
    fecha=datetime.datetime.now().strftime('_%Y-%m-%d-%H-%M-%S-%f')
    try:
        if not os.path.exists("./logs/crash"):
            os.makedirs("./logs/crash")
            
        archivo = open("./logs/crash/crash_"+fecha, "w+")        
        archivo.write(exceptionText)                       
        archivo.close()   
    except:
        pass
       
       
class Operation(threading.Thread):
    
    operationId=None
    fechaComienzo=None
    logStream=""
    resultString=""

    def __init__(self,params,passwd,driverName=None):
        threading.Thread.__init__(self)
        #dict con tipo de funcion y paramatros de la funcion
        self.params=params
        self.outputQueue=queue.Queue()        
        self.dataOutputQueue=queue.Queue()
        self.outputLock=threading.Lock()
        self.driver=None
        self.driverName=driverName
        self.fechaComienzo=datetime.datetime.now()
        self.intentosRestantes=params['reintentos'][0]
        self.intervalReintentos=params['reintentos'][1]
        self.passwd=passwd
        
    def getDriverName(self):
        if self.driver!=None:
            return self.driver.name
        else:
            return None
        
    def abort(self):
        
        if self.driver!=None:
            if self.driver.tryAbort():
                return True
            return False
        return True              
    
        
    def run(self):

        try :
            oper=self.params['oper']
            para=self.params['params']
            target=self.params['target']        
            driver = UteTelnetDriver(target,self.outputQueue,name=self.driverName)
            self.driver=driver
            self.driver.setPassword(self.passwd)
            
            resetAfter=False
            if 'resetAfter' in self.params:
                if self.params['resetAfter']:
                    resetAfter=True
            
            if oper=="WRITECONFIG":
                result=driver.sendJsonConfigFromPath(para, False)
                self.fechaFin=datetime.datetime.now()
                
                
                if resetAfter:
                    result=driver.reset()
                    
                self.outputLock.acquire()
                if result!=None:
                    if result:                
                        self.dataOutputQueue.put(True)
                    else:
                        self.dataOutputQueue.put(False)
                else:  
                    self.dataOutputQueue.put(False)
                self.outputLock.release()
            
            elif oper=="READCONFIG":
                result = driver.getJsonConfig()
                self.fechaFin=datetime.datetime.now()
                self.outputLock.acquire()            
                if result!=None:  
                    if driver.softV!=None:
                        softV=driver.softV
                        result['firmware version']=softV.replace("\r","")
                    if result:              
                        self.dataOutputQueue.put( True)
                        self.dataOutputQueue.put(result)
                    else:
                        self.dataOutputQueue.put(False)
                else:  
                    self.dataOutputQueue.put(False)
                self.outputLock.release()
            
            elif oper=="UPGRADE":
                result = driver.firmwareUpdateFromPath(para)
                self.fechaFin=datetime.datetime.now()
                self.outputLock.acquire()
                if result!=None:
                    if result:                
                        self.dataOutputQueue.put(True)
                    else:
                        self.dataOutputQueue.put(False)
                else:  
                    self.dataOutputQueue.put(False)
                self.outputLock.release()
                    
            elif oper=="DOWNLOADLOG":
                #TODO
                result = driver.downloadLog()
                self.fechaFin=datetime.datetime.now()
                self.outputLock.acquire()            
                if result!=None:  
                    if result:              
                        self.dataOutputQueue.put( True)
                        self.dataOutputQueue.put(result)
                    else:
                        self.dataOutputQueue.put(False)
                else:  
                    self.dataOutputQueue.put(False)
                self.outputLock.release()
            
            
            if oper=='BORRARLOG' :
                result=driver.deleteLog()
                self.fechaFin=datetime.datetime.now()
                self.outputLock.acquire()            
                if result==True:   
                    self.dataOutputQueue.put(True)
                else:  
                    self.dataOutputQueue.put(False)
                self.outputLock.release()
                    
            
            if oper=='RESET' :
                result=driver.reset()
                self.fechaFin=datetime.datetime.now()
                self.outputLock.acquire()            
                if result==True:   
                    self.dataOutputQueue.put(True)
                else:  
                    self.dataOutputQueue.put(False)
                self.outputLock.release()
            
            
            driver.closeSocket()
        
        except Exception as e:
            text=traceback.format_exc()
            saveCrashReport(text)
            traceback.print_exc()
            