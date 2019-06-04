import socket
import logging
import os
from datetime import datetime
from time import strftime
from _datetime import timedelta
import json
import binascii
import re
from cgi import closelog
#aplicar config en json, opcion de reset luego
#descargar config a json
#update de firmware
#reset
#descargar logs, con opcion de borrar
##modo monitor.
class UteTelnetDriver():
   
    
    def __init__(self,ip,outputQueue,port=53300,loggingLevel=logging.DEBUG,name=None):
         
         
        #for testing
        self.user ="admin" 
        self.password = "admin123"

        self.outputQueue=outputQueue
        self.timeout=60
        self.loggingEnabled=True; 
        self.logger=None
        self.softV=None
        
        
        rip,rport=self.ipHasPort(ip)
        self.ip=rip
        self.port=port
        if rport!=None:
            self.port=rport
            
        if name==None:
            self.name = datetime.now().strftime("%Y-%m-%dT%H_%M_%S") + "_"+ip
        else:
            self.name=name
        self.stream=""
        if self.loggingEnabled:
            self.__configLogFileName(self.name,loggingLevel)
    
        self.keymap = json.load(open("driver\jsonkeymap.json"))
    
        self.abortable=True
        self.abort=False
        
        self.mmLastSource=0
    def ipHasPort(self,ip):
        
        rip=ip
        rpuerto=None
        if ":" in ip:
            pedazos=ip.split(":")
            if len(pedazos)==2:
                rip=pedazos[0]
                try:
                    puerto=int(pedazos[1])
                    if (puerto>0 and puerto<65535):
                        rpuerto=puerto    
                except:
                    pass
        
        return rip,rpuerto
        
    def setPassword(self,passwd):
        self.password=passwd
        
    def closeSocket(self):
        
        try:
            self.socket.shutdown(socket.SHUT_RD|socket.SHUT_WR)
        except Exception as e:
            pass
       
        try:
            self.socket.close()
        except Exception as e:
            pass
        
        self.closeLogs()
        
    def tryAbort(self):
        
        if self.abortable==True:
            self.abort=True
            self.outputQueue.put("Cancelado por usuario")
            return True       
        
        return False
    #
        #self.logger.info("New driver created")
 
    def __logInfo(self,text):
        if self.logger!=None:
            self.logger.info(text)
    def __logError(self,text):
        if self.logger!=None:
            self.logger.error(text)
    def __logDebug(self,text):
        if self.logger!=None:
            self.logger.debug(text)
     
    def __sendStr(self,text): 
        
        if self.abort:
            self.__logDebug("Aborted by user")
            self.outputQueue.put("Abortado por usuario")   
            return False
            
        self.__logDebug("SocketSend:")
        self.__logDebug(text.encode('utf-8'))
        self.socket.send(text.encode('utf-8'))
     
    def __isLoggedIn(self):
            
        try: 
            self.stream=""
            self.__sendStr("dummyMsg\r\n")
            if self.__waitFor("Unknown command", self.timeout):
                self.stream=""
                return True
        except Exception as e:
            return False
    
   
        
    def _login(self,forceNewSocket=False):
        self.__logInfo("Login started")
        
        #self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.abortable=True

        if forceNewSocket:
            self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
        else:
            if not self.__isLoggedIn():
                self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
            else:
                self.__logDebug("Already Logged on")
                return True
        
        try:          
            try:
                self.outputQueue.put("Conectando...")
                self.__logInfo('Starting connection') 
                self.socket.connect((self.ip,self.port))
                self.socketConnected=True
                self.__logInfo('Connection success')
                self.outputQueue.put("Conectado")
               
               
            except socket.error as e:
                self.socketConnected=False
                self.__logInfo('Connection fail')
                self.outputQueue.put("Connection fail")   
                self.__logError(str(e))                 
                self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      
            if self.socketConnected:
                #do login
                self.outputQueue.put("Iniciando sesion")
                if self.__waitFor("user:", self.timeout):
                    self.__sendStr(self.user+"\r\n")
                    if self.__waitFor("pass:", self.timeout):
                        self.__sendStr(self.password+"\r\n")
                        
                        #esperar > en caso afirmativo de login o Bad user and password en caso contrario y abortar
                        
                        ok, softVersionText=self.__waitForBinary("Bad user and password",">",self.timeout)

                        if "Bad user and password" in softVersionText:
                            self.socketConnected=False
                            self.outputQueue.put("Error en login: contraseña o usuario incorrecto")   
                            return False
                        
                       # ok,softVersionText=self.__waitFor(">", self.timeout)
                        
                        svpat="Software Version :"
                        start=softVersionText.find(svpat)
                        end=softVersionText.find("\n>")
                        
                        if start!=-1 and end!=-1:
                            self.softV=softVersionText[start+len(svpat):end]
                            self.outputQueue.put("Version de firmware:%s"%(self.softV))
                        
                        if ok:
                            self.__logInfo("Login success")
                            self.outputQueue.put("Inicio de sesion completado")
                            return True
                
                self.outputQueue.put("Error en login")             
             
        except Exception as e:
                self.__logError(str(e))  # log exception info at FATAL log level    
                self.socketConnected=False
                self.outputQueue.put("Error en login")     
                  
        self.__logInfo("Login fail") 
        
        
        return False
           
    def ___cleanStreamByteCount(self,byteCount):
        ind=byteCount
        resultado=self.stream[0:ind]
        self.stream=self.stream[ind::]
        return resultado       
    
    def ___cleanStream(self,text):
        
        if text in self.stream:
            ind=self.stream.find(text)
            resultado=self.stream[0:ind+len(text)]
            self.stream=self.stream[ind+len(text)::]
            return resultado
            
    def __waitFor(self,text,timeout):    
        timeoutTime=timedelta(seconds=timeout) + datetime.now()
        
        
        while timeoutTime > datetime.now():            
            try:
                
                if self.abort:
                    self.__logDebug("Aborted by user")   
            
                    return False
                
                if text in self.stream:
                    textLeido=self.___cleanStream(text)
                    return True, textLeido
                
                data=self.socket.recv(1024)
                if len(data)==0:
                    self.socketConnected=False
                    return False
                
                data=data.decode('utf-8',errors="ignore")
                self.stream+=data
                self.__logDebug("socket read %d bytes:"%(len(data)) +" "+data)   
            
            except socket.timeout as e:
                
                pass
              
            except Exception as e:
                self.__logError(str(e))
                break
                
        return False
    
    def __waitForByteCount(self,byteCount,timeout):    
        timeoutTime=timedelta(minutes=timeout) + datetime.now()
        while timeoutTime > datetime.now():            
            try:
                
                if self.abort:
                    self.__logDebug("Aborted by user")   
            
                if byteCount <= len(self.stream):
                    textLeido=self.___cleanStreamByteCount(byteCount)
                    return True, textLeido
                
                data=self.socket.recv(1024)
                if len(data)==0:
                    self.socketConnected=False
                    return False
                
                data=data.decode('utf-8',errors="ignore")
                self.stream+=data
                self.__logDebug("socket read %d bytes:"%(len(data)) +" "+data)   
            
              
                
            except Exception as e:
                self.__logError(str(e))
                break
                
        return False
    
    def __waitForBinary(self,text1,text2,timeout):    
        timeoutTime=timedelta(minutes=timeout) + datetime.now()
        while timeoutTime > datetime.now():            
            try:
                
                if self.abort:
                    self.__logDebug("Aborted by user")   
            
                data=self.socket.recv(1024)
                if len(data)==0:
                    self.socketConnected=False
                    return False
                
                data=data.decode('utf-8',errors="ignore")
                self.stream+=data
                self.__logDebug("socket read %d bytes:"%(len(data)) +" "+data)   
            
                if text1 in self.stream:
                    textLeido=self.___cleanStream(text1)
                    return True, textLeido
                elif  text2 in self.stream:
                    textLeido=self.___cleanStream(text2)
                    return True, textLeido
                
            except Exception as e:
                self.__logError(str(e))
                break
                
        return False,None
    
    def __getNextByteMM(self):
        
        self.stream=self.stream.lstrip()
        result={}
        
        if self.stream.startswith("1 >"):
            result['dir']=1
            self.stream=self.stream[3:]
        elif self.stream.startswith("2 >"):
            result['dir']=2
            self.stream=self.stream[3:]
        elif len(self.stream)>=2:
            try:
                data=int(self.stream[:2],16)
                result['data']=data
                self.stream=self.stream[2:]
            except Exception as e:
                print(e)    
        return result
    
    def __parseMonitorModeStream(self):
        tcp=[]
        ser=[]
        err=False
        
        while len(self.stream)>=2:
            result=self.__getNextByteMM()
                        
            if "data" in result:
                data=result['data']
                if self.mmLastSource==1:
                    tcp.append(data)
                elif self.mmLastSource==2:
                    ser.append(data)
                    
            if "dir" in result:
                dir=result["dir"]    
                self.mmLastSource=dir
                      
        print("stream:" +self.stream)
        
        if err:
            return False,tcp,ser
        return True,tcp,ser  
                     
    def __readSocket(self,timeout):    
        timeoutt=self.socket.gettimeout()
        timeoutTime=timedelta(minutes=timeout) + datetime.now()
        self.socket.settimeout(0.5)
        while timeoutTime > datetime.now():            
            try:
                if self.abort:
                    self.__logDebug("Aborted by user") 
                    self.socket.settimeout(timeoutt)
                    return False
            
                data=self.socket.recv(1024)
                if len(data)==0:
                    self.socketConnected=False
                    self.socket.settimeout(timeoutt)
                    return False
                
                data=data.decode('utf-8',errors="ignore")
                self.stream+=data
                self.__logDebug("socket read %d bytes:"%(len(data)) +" "+data)
                self.socket.settimeout(timeoutt)
                return True
               
            except socket.timeout as e:
                
                continue
            except Exception as e:
                self.__logError(str(e))
                break
         
        self.socket.settimeout(timeoutt)       
        return False
    
    def reset(self):
        if self._login():
            self.abortable=False
            self._resetDevice()
            return True
        return False
        
    def _resetDevice(self):

        self.outputQueue.put("Reseteando..")
             
        self.__logInfo("Reset device start")
        self.__sendStr("resetnow\r\n")
        if self.__waitFor("OK", 15):
            self.__logInfo("Reset Success")
            self.outputQueue.put("Reset completado")
             
            return True
        else:
            self.__logError("Reset Error")
            self.outputQueue.put("Error en reset")
             
            return False

    def sendJsonConfigFromPath(self,path,resetOnsuccess):
        
        try:
            config= json.load(open(path))
            
            return self.sendJsonConfig(config, resetOnsuccess)
    
        except Exception as e:
            self.__logError("Cant load json =%s"%(path))
            return False
        
        
        
       
    def sendJsonConfig(self,config,resetOnSuccess):
        
        success=False
        if config!=None:
            convertedConfig=self.convertJsonToMachineReadable(config)
            if self._login():
                
                self.abortable=False
                self.__logInfo("Send Json config start")
                self.outputQueue.put("Enviando configuracion")
                
                self.__sendStr("__write_json_config\r\n")
                if self.__waitFor("OK\r\n", 15):
                              
                    jsonConfigText = json.dumps(convertedConfig,indent=None,separators=(',', ':'), sort_keys=True)
                    self.__sendStr(jsonConfigText +"\n")
               
                    respuesta, resultado = self.__waitForBinary("OK","ERROR", 15)
                    
                    if respuesta:    
                        print(resultado)
                        
                        if "OK" in resultado:
                            
                            self.outputQueue.put("Configuracion enviada")
             
                            if resetOnSuccess:
                                if self._resetDevice():
                                    return True
                                else:
                                    return False
                        
                             
                             
                            return True  
                        elif "ERROR" in resultado:
                            
                            respuesta , error = self.__waitFor("}\n", 30)
                            
                            self.__logError("Device could not parse since "+ error)
                            self.outputQueue.put("Error al enviar configuracion")
             
                          
                            
                            
                            return False
                #send jsonConfigCommand
                #waitForOK
                #send jsonConfig
                #waitForResponse
                    #if OK
               
        else:
            self.__logError("Null config")            
                    #else errorEnJson
                
                
        return False

        
    def modoMonitor(self,queueControl,queueTcp,queueSerial,tcpLock,serialLock):
        self.abortable=True
        if self._login():
        
            self.__logInfo("MonitorMode start")
            self.outputQueue.put("Modo monitor iniciado")
            
            self.modoMonitorEnabled=True
            self.__sendStr("monitormode\r\n")
            
            while True:
                
                if not queueControl.empty():#se termina
                    self.__sendStr("\n")
                    return True
                    break
                
                if self.__readSocket(5):
                    result,tcp,ser=self.__parseMonitorModeStream()
                    
                    if result:
                        if len(tcp)>0:
                            newTcp=""
                            for x in tcp:
                                newTcp+=chr(x)
                            tcpLock.acquire()
                            queueTcp.put({"data":newTcp,"fecha": datetime.now().strftime("%H:%M:%S,%f")})
                            tcpLock.release()
                            
                        if len(ser)>0:
                            newSer=""
                            for x in ser:
                                newSer+=chr(x)
                            serialLock.acquire()
                            queueSerial.put({"data":newSer,"fecha": datetime.now().strftime("%H:%M:%S,%f")})
                            serialLock.release()
                else:
                    print("Modo monitor timeout")
                    return False
           
           # self.__sendStr("\r\n")
        return False
    
    
    def convertJsonToHumanReadable(self,oldJson):
        
        newJson={}
        for x in oldJson:
            if x in self.keymap:
                xvalue=oldJson[x]
                newJson[self.keymap[x]]=xvalue
            else:
                self.__logError("Key in json conversionToHuman discarted, not in jsonKeyMap.json file "+x)              
        
        return newJson
    
    def convertJsonToMachineReadable(self,oldJson):
        inv_map = {v: k for k, v in self.keymap.items()}
        newJson={}
        for x in oldJson:
            if x in inv_map:
                xvalue=oldJson[x]
                newJson[inv_map[x]]=xvalue                
            elif x in self.keymap:
                xvalue=oldJson[x]
                newJson[x]=xvalue   
            else:
                self.__logError("Key in json conversionToMachine discarted, not in jsonKeyMap.json file "+x)              
            
        return newJson
    
    def __findJson(self,text):
        
        inicio=text.find("{")
        fin=text.find("}")
        
        if inicio!=-1 and fin!=-1:            
            newJson = text[inicio:fin+1]
                        
            try:
                jsonLoaded=json.loads(newJson)
                return jsonLoaded
            except Exception as e:
                self.__logError( "Error parsing json" )
                self.__logError(str(e))
               
        return None
    
    def getJsonConfig(self):
        if self._login():
            self.abortable=False
            self.outputQueue.put("Solicitando configuracion")
             
            self.__logInfo("Get Json config start")
            self.__sendStr("__read_json_config\r\n")
            if self.__waitFor("OK\r\n", 10):
                llegoFinJson, rawJson = self.__waitFor("}", 10)
                
                if llegoFinJson:
                    self.__logDebug("Raw Json candidate:" + rawJson)
                    jsonConfig=self.__findJson(rawJson)
                    if jsonConfig!=None:
                        jsonConfigText = json.dumps(jsonConfig,indent=2, sort_keys=True)
                        self.__logInfo("Device Config : \r\n"+jsonConfigText)
                        self.outputQueue.put("Configuracion recibida")
                        
                        humanJson=self.convertJsonToHumanReadable(jsonConfig)
                        
             
                        return humanJson
                    else:
                        self.__logError("Text is not json")
                        self.outputQueue.put("Error al parsear configuracion")
             
        return None
        
    def __eraseTopMem(self):
        
        self.outputQueue.put("Borrando memoria")
             
        self.__logInfo("Erase Half Top Memory Started")
        self.__sendStr("eRaSeToP\r\n")
        
        responseArrived, result = self.__waitForBinary("OK\r\n","ERASE ERROR", 10)
       
        if responseArrived:
            if "OK" in result:  
                self.__logInfo("Erase Half Top Memory OK")
                self.outputQueue.put("Borrado completado")
             
                return True
            else:
                self.__logInfo("Erase Half Top Memory ERROR")
                self.outputQueue.put("Error al borrar memoria")
             
                return False
            
        self.__logInfo("Erase Half Top Memory ERROR")                    
        return False
    
    def __enterFastWriteMode(self,offset,len):
        
        self.__logInfo("EnterFastWriteMode Started")
        self.__sendStr("__fast_write %d %d\n"%(offset,len))
        
        responseArrived, result = self.__waitForBinary("OK\r\n","Wrong", 10)
       
        if responseArrived:
            if "OK" in result:  
                self.__logDebug("EnterFastWriteMode OK")
                   
                return True
            else:
                self.__logDebug("EnterFastWriteMode ERROR")
            
                return False
            
        self.__logInfo("EnterFastWriteMode ERROR")                    
        return False
        
    def __sendRawData(self,data,responseNumber):
        
        self.socket.send(data)
        if self.__waitFor("OK %d"%(responseNumber), 30):
            return True
        return False        
     
     
    def __crc32(self,binaryData):
        
        crcValueSigned=binascii.crc32(binaryData)
        crcValueUnsigned=crcValueSigned % (1<<32)
        
        return crcValueUnsigned
        
    def __doMemorySwap(self, binaryData):  
        
        
        self.abortable=False
        crcValue=self.__crc32(binaryData)        
        self.__sendStr("uPgRaDe %X %d\n"%(crcValue,len(binaryData)))
        
        responseArrived, result = self.__waitForBinary("OK","CRC MISMATCH", 10)
       
        if responseArrived:
            if "OK" in result:  
                self.__logDebug("Crc accepted for memory swap OK")
                   
                return True
            else:
                self.__logError("Crc error at memory swap")
            
                return False
        
        self.__logError("Response timeout at crc send")            
        return False       
            
    def __firmwareUpdate(self,binaryData):
        blockSize=10240
        if self._login():
              
            self.__logInfo("Firmware update start")
            
            if self.__eraseTopMem():
                dataSent=0
                fileLen=len(binaryData)
                if self.__enterFastWriteMode(0, fileLen):
                    
                    while dataSent < fileLen:
                        blockSize=10240
                        
                        if fileLen - dataSent < blockSize:
                            blockSize=fileLen-dataSent
                        
                        self.__logDebug("Data block size = %d"%(blockSize))
                        
                        dataChunk = binaryData[dataSent:dataSent+blockSize]
                        
                        self.outputQueue.put("Enviando %d/%d"%(dataSent,fileLen))

                        if self.__sendRawData(dataChunk, dataSent+blockSize):
                            dataSent +=blockSize
                            self.__logDebug("%d byte sended"%(blockSize))
             
                        else:
                            self.__logError("Error at sending data, offset= %d, blockSize=%d"%(dataSent,blockSize))
                            self.outputQueue.put("Error en envio")
             
                            return False
                        
                    self.__logInfo("%d byte Sended - File sended"%(dataSent))
                    
                    if dataSent==fileLen:
                        self.outputQueue.put("Envio de firmware completado")
             
                        self.outputQueue.put("Instalando nuevo firmware")             
                        if self.__doMemorySwap(binaryData):
                            self.__logInfo("Firmware Upgrade Success")
                            self.outputQueue.put("Instalacion completada")             
                            return True
                        else:
                            self.__logError("Firmware Upgrade Error")
                            self.outputQueue.put("Error en instalacion")
             
                        
        return False
     
     
    def hasValidFirmwareChecksum(self,binaryData):
        
        suma=0
        for x in range(0,7):
            numberToSum= binaryData[4*x ] | binaryData[4*x +1]<<8 | binaryData[4*x+2]<<16 |binaryData[4*x+3]<<24
            
            suma+=numberToSum
        
        checkAdress=7
        checkValue=  binaryData[checkAdress*4 ] | binaryData[checkAdress*4 +1]<<8 | binaryData[checkAdress*4+2]<<16 |binaryData[checkAdress*4+3]<<24
        
        if checkValue-0x1000 == 0xFFFFF000 -suma:
            return True
        
        return False
        
        
        
    def firmwareUpdateFromPath(self,path):  
        binaryData=None
        with open(path, 'rb') as f:
            binaryData = f.read() 
            
        if binaryData!=None:
            
            #fileCHECKSUM
            hasCheckSum=self.hasValidFirmwareChecksum(binaryData)
            
            if hasCheckSum:
                self.__logInfo("Firmware file has checksum")
                
                self.outputQueue.put("Firmware presenta crc valido")             
                return self.__firmwareUpdate(binaryData)
            else:
                self.outputQueue.put("El archivo de firmware no presenta checksum valido")             
                self.__logError("Firmware file not has checksum, Error")
                return False
       
       
    def __logFileSize(self):  
        
        self.__sendStr("logs size\n")
        
        responseArrived, result = self.__waitFor("bytes", 10)
       
        if responseArrived:
            if "=" in result:
                pedazos=result.split("=")
                if " " in pedazos[1]:
                    otroPedazo=pedazos[1].split(" ")
                    return int(otroPedazo[0])
  
        return -1
              
    def downloadLog(self):
        if self._login():
            self.abortable=False
            
            self.__logInfo("Download log start")
            self.outputQueue.put("Consultando tamaño de log")
            self.__sendStr("logs\n")
       
            responseArrived, result = self.__waitFor("bytes", 10)
            charToRead=0
            if responseArrived:
                if "=" in result:
                    pedazos=result.split("=")
                    if " " in pedazos[1]:
                        otroPedazo=pedazos[1].split(" ")
                        charToRead= int(otroPedazo[0])
                        self.outputQueue.put("%d bytes para leer"%(charToRead))
                                
                        result, text=self.__waitForByteCount(charToRead, 360)
                        
                        if result:
                            self.__logInfo("Log File Download Complete")
                            self.outputQueue.put("Descarga de log completada")
                            print(text)
                            return text
                        else:
                            self.__logError("Log File Download Error")
                            self.outputQueue.put("Error en descarga de log")

            
                
                      
        
        return None
    
    def deleteLog(self):
        if self._login():
            
            self.abortable=False
            self.outputQueue.put("Borrando archivo de log")             
            self.__logInfo("Delete log start")            
            self.__sendStr("logs delete\n")       
            responseArrived = self.__waitFor("logs file deleted", 30)
            
            if responseArrived:
                self.__logInfo("Log File Delete Complete")  
                self.outputQueue.put("Borrado completado")             
                return True
            else:
                self.__logError("Log File Delete Error")
                self.outputQueue.put("Error en borrado")
             
        
        else:
            return False
       
    def closeLogs(self):
        
        self.__logInfo("Operación terminada\n**********************************************************************\n")     
        try:
            self.handler.close()
            self.logger.removeHandler(self.handler)
        except Exception as e:
            pass
        try:
            self.consoleHandler.close()
            self.logger.removeHandler(self.consoleHandler)

        except Exception as e:
            pass
        
      
       
    def __configLogFileName(self,name,level):
            
            global logger
            self.logger = logging.getLogger(name)
            self.logger.setLevel(level)
        
            if not os.path.exists("./logs"):
                os.makedirs("./logs")
                ## create a file handler
        
            #global logger,consoleHandler
            self.handler = logging.FileHandler('./logs/'+name+'.log')  #agregar hora antes del nombre
            self.handler.setLevel(logging.INFO)
            
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