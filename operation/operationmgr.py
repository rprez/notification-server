import queue
from PySide2 import QtCore
import threading
from operation import operation
import time
import datetime
import json
from PyQt5.Qt import QTextObject
import logging
import os
from logging.handlers import RotatingFileHandler
import traceback
#import pydevd

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
       
class SignalSender(QtCore.QObject):
    
    appendPending=QtCore.Signal(dict)
    deletePending=QtCore.Signal(str)
    
    appendWorking=QtCore.Signal(dict)
    deleteWorking=QtCore.Signal(str)
    
    changeStatusWorking=QtCore.Signal(dict)
    
    appendEnded=QtCore.Signal(dict)
    deleteEnded=QtCore.Signal(str)
    
    updateInfo=QtCore.Signal(str,str)
    
def saveStringToFile(fname,msgEnString):
    
    archivo = open(fname,"w+")        
    archivo.write(msgEnString)                       
    archivo.close()  
    
class OperationMgr(threading.Thread):
    
    appendPending=QtCore.Signal(dict)
    deletePending=QtCore.Signal(str)
    
    appendWorking=QtCore.Signal(dict)
    deleteWorking=QtCore.Signal(int)
    
    changeStatusWorking=QtCore.Signal(dict)
    
    appendEnd=QtCore.Signal(dict)
    
    
    prevTexto=""
    prevResultaData=""
    def __init__(self,parent=None):
        threading.Thread.__init__(self)
        self.queueLock=threading.Lock()
        self.queue=queue.Queue()
        
        self.pending={}
        self.working={}
        self.ended={}
        
        self.operationCounter=0
        
        self.maxSimultaneosOperation=100
        self.paused=True
        
        self.ss=SignalSender()
        
        self.selectedOperationId=None
        
        self.__configLogFileName("operationManager",logging.DEBUG)
    
    def __logDebug(self,text):
        if self.logger!=None:
            self.logger.debug(text)
            
    def __configLogFileName(self,name,level):
            
        global logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
    
        if not os.path.exists("./logs"):
            os.makedirs("./logs")
        ## create a file handler

        if not os.path.exists("./logs/operaciones"):
            os.makedirs("./logs/operaciones")
    
        #global logger,consoleHandler
        self.handler =  RotatingFileHandler('./logs/operaciones/'+name+'.log', maxBytes=10000000, backupCount=4)

       # self.handler = logging.FileHandler('./logs/operaciones/'+name+'.log')  #agregar hora antes del nombre
        self.handler.setLevel(logging.DEBUG)
        
        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        
        # create console logging
        self.consoleHandler = logging.StreamHandler()
        self.consoleHandler.setFormatter(formatter)
        
        # add the handlers to the logger
        self.logger.addHandler(self.handler)
        self.logger.addHandler(self.consoleHandler)
        
        #########################

    
    def setMaxRunningOperations(self,maxCount):
        self.maxSimultaneosOperation=maxCount
        
    #encolar operaciones.
    def encolarOperacion(self,operacion,operId=None):
    
       # print("encolando operacion")
        if operId==None:
            operacion.operationId=self.operationCounter 
        else:
            operacion.operationId=operId
        operacion.fechaCreacion=datetime.datetime.now()
           
        self.queueLock.acquire()        
        self.pending[str(operacion.operationId)]=operacion
        self.queueLock.release()
        
        self.ss.appendPending.emit(operacion)       
       
        if operId==None:
            self.operationCounter=self.operationCounter+1
        
    
   
    def repetirOperacion(self,operId):
        
        
        if operId in self.ended:
         #   print("Repetir operacion ID=%s"%(operId))
        
            oper=self.ended[operId]
            #self.ss.deleteEnded.emit(operId)
            
            newParams=oper.params.copy()
            self.encolarOperacion(operation.Operation(newParams,oper.passwd))

        else:   
            self.__logDebug("Fallo repeticion de operacion, no se encontro ID=%s en las operaciones terminadas"%(operId))
        
    
    
    def abortAll(self):
        
        for w in self.working:
            self.working[w].abort()
       
       
        keys=list(self.pending.keys())       
        for p in keys:            
            self.cancelarPendingOperacion(p)
        
    def pausarOperaciones(self):
        self.paused=True

        
    def cancelarPendingOperacion(self,id):
        
        if id in self.pending:
            oper=self.pending.pop(id)
            self.ss.deletePending.emit(id)
            oper.logStream+="Cancelado por Usuario\n"
            oper.fechaFin = datetime.datetime.now()
            oper.result=False
            self.ended[id]=oper
            self.ss.appendEnded.emit(oper)
            
        pass
    
    def unPauseOperaciones(self):
        self.paused=False
        
    def __targetBusy(self,operacion):
        
        target=operacion.params['target']        
        for x in self.working:
            
            if target == self.working[x].params['target']:
                return True
        
        return False        
    
    def __tryStartingAPendingOperation(self):
        
        for x in self.pending:
            operacion=self.pending[x]
            if not self.__targetBusy(operacion) :
                if  operacion.fechaComienzo < datetime.datetime.now():
                    operacionAtrabajar=self.pending.pop(x)
                    
                    self.__logDebug("iniciando operacion")
                    self.__logDebug(operacionAtrabajar)
                    
                    self.working[x]=operacionAtrabajar
                    operacionAtrabajar.setDaemon(True)
                    operacionAtrabajar.start()
                    
                    self.ss.deletePending.emit(str(operacionAtrabajar.operationId))
                    self.ss.appendWorking.emit(operacionAtrabajar)               
                    
                    return True
      
        return False
    
    
    def updateInformationBox(self):
        
        if self.selectedOperationId != None:
            
            texto=""
            resultText=""
            if self.selectedOperationId in self.pending:
                texto= self.pending[self.selectedOperationId].logStream 
                resultText=self.pending[self.selectedOperationId].resultString
            elif self.selectedOperationId in self.working:
                texto= self.working[self.selectedOperationId].logStream 
                resultText=self.working[self.selectedOperationId].resultString
            elif self.selectedOperationId in self.ended:
                texto= self.ended[self.selectedOperationId].logStream
                resultText=self.ended[self.selectedOperationId].resultString

            if texto!=self.prevTexto or resultText!=self.prevResultaData:
                self.prevTexto=texto
                self.prevResultaData=resultText
                self.ss.updateInfo.emit(texto,resultText)
                
    
    
    def checkIfMsgInQueuesAndProcess(self):
        
        operToBePoped=[]
        for id in self.working:
            oper=self.working[id]
            
            while not oper.outputQueue.empty():
                msg = oper.outputQueue.get()
                
                msgToSend={}
                msgToSend['id']=str(id)
                msgToSend['msg']=msg
                
                oper.logStream+=msg +"\n"
                
                self.ss.changeStatusWorking.emit(msgToSend)

            if not oper.dataOutputQueue.empty():
                oper.outputLock.acquire()##para estar seguros que esta todo ingresado en la cola, en el caso que s retornam as de un valor
                result=oper.dataOutputQueue.get()
                data=None
                if not oper.dataOutputQueue.empty():
                    data = oper.dataOutputQueue.get()
                oper.outputLock.release()
                
                if data!=None:
                    
                    #guardar resultado
                    path=oper.fechaCreacion.strftime("%Y-%m-%dT%H-%M-%S_")
                    path+=oper.params['target']+"_"+oper.params['oper']
                    pathDir=oper.params['params']
                    
                    if oper.params['oper']=="READCONFIG":
                        texto=json.dumps(data,indent=2,sort_keys=True)
                        oper.resultString=texto
                        
                    elif oper.params['oper']=="DOWNLOADLOG":
                        oper.resultString=data
                        
                    if pathDir!=None:
                        saveStringToFile(pathDir+"/"+path, oper.resultString)
                    
                ## pasar op a ended
                
                oper.result=result 
                operToBePoped.append(id)               
                self.ended[id]=oper
                self.ss.deleteWorking.emit(id)
                
                # revisar si tiene que repetir en caso de fail y si tiene repeticiones
                #TODO
                if not oper.result:
                    if oper.intentosRestantes>0:
                        self.__logDebug("Operacion fallo intentando reintento")
                          
                        newParams=oper.params.copy()
                        dName=oper.getDriverName()
                        newOper=operation.Operation(newParams,oper.passwd,driverName=dName)
                        newOper.logStream+=oper.logStream
                        newOper.intentosRestantes=oper.intentosRestantes-1
                        newFecha=datetime.datetime.now()+datetime.timedelta(minutes=newOper.intervalReintentos)
                        newOper.fechaComienzo=newFecha
                        newOper.logStream+= "\n-----------------------------\nReintentos pendientes :%d\n"%(oper.intentosRestantes)
                        newOper.logStream+="@ "+ newOper.fechaComienzo.strftime("%Y-%m-%d %H:%M:%S")+"\n\n"
                     
                        self.encolarOperacion(newOper,id)
                    else:
                        self.ss.appendEnded.emit(oper)
                else:
                    self.ss.appendEnded.emit(oper)

        for x in operToBePoped:
            self.working.pop(x)        
                    
    def run(self):

      #  pydevd.settrace(suspend=False, trace_only_current_thread=True)
        try:
            while True:
    
                if not self.paused:            
                    stopTrying=False
                    while len(self.working)<self.maxSimultaneosOperation and len(self.pending)>0 and not stopTrying:
                     
                        if self.__tryStartingAPendingOperation():
                            pass
                        else:
                            stopTrying=True
                               
                self.checkIfMsgInQueuesAndProcess()       
                self.updateInformationBox()
                  
                time.sleep(0.25)             
             
        except Exception as e:
            text=traceback.format_exc()
            saveCrashReport(text)
            traceback.print_exc()   
            
            
            
            
            
            
            
            
            
            
        