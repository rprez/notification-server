import threading
import json
import time
import socket
import os
import hashlib
import traceback
from datetime import datetime
from _datetime import timedelta
from importlib.resources import path
from test.ann_module import Meta
import base64
import queue

class UpdateClient():
    
    def __init__(self,host,port,installPath,tempFolder):
               
                
        self.ip = host
        self.port = port 
        self.stream=""
        self.installPath=installPath
        self.tempFolder=tempFolder
        self.timeout=15
        self.socketConnected=False
        self.stateQueue=queue.Queue()

    def __logInfo(self,txt,appendToQueue=False):
        print(txt)
        if appendToQueue:
            self.stateQueue.put(txt)
    def __logError(self,txt):
        print(txt)
    def connectToServer(self):
    
        try:          
            try:
                self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
                self.__logInfo('Starting connection',True)
                self.socket.connect((self.ip,self.port))
                self.socketConnected=True
                self.__logInfo('Connection success',True)
                 
            except socket.error as e:
                self.socketConnected=False
                self.__logInfo('Connection fail',True)
                self.__logError(str(e))                 
                self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      
        except Exception:
            self.__logError(traceback.format_exc())  # log exception info at FATAL log level    
            self.socketConnected=False
            
        
        return self.socketConnected   
    
    def __findMatchedBracketEnd(self,text):
        
        pass
     
     
    def __findJson(self,text):
        
        bracketBalanced=False
        fin=0
        inicio=0
        while (not bracketBalanced)  and fin!=-1 and len(text)>=fin:
            inicio=text.find("{")
            
            fin=text.find("}",fin+1)
            newJson=""
            
            if inicio!=-1 and fin!=-1:            
                newJson = text[inicio:fin+1]
                  
                if newJson.count("{")==newJson.count("}"):
                    bracketBalanced=True
                       
            else:
                return [None,0]
           
        if inicio!=-1 and fin!=-1 and bracketBalanced:               
            try:
                jsonLoaded=json.loads(newJson)
                return [jsonLoaded,fin]
            except Exception as e:
                print("cant parse:")
                print(newJson)
    
        return [None,0]   
               
    def checkIfRequestPending(self,waitingTime=30):
    
        timeoutTime=timedelta(seconds=waitingTime) + datetime.now()
        
        
        while timeoutTime > datetime.now():    
            
            [pendingJsonRequest,pendingFin]=self.__findJson(self.stream)
            if pendingJsonRequest!=None:
                self.stream=self.stream[pendingFin+1::]
                return pendingJsonRequest
            
            try:  
                data=self.socket.recv(102400)
               
                if len(data)==0:
                    return None
                  
                data=data.decode('utf-8',errors="ignore")
                self.stream+=data
                
                
                [jsonResult,fin]=self.__findJson(self.stream)
                if jsonResult!=None:
                   
                    self.stream=self.stream[fin+1::]
                    return jsonResult
                
            except Exception as e:
                time.sleep(0.5) 
                pass
             
           # time.sleep(0.5)   
        return None
    
    def sendMsg(self, jsonMsg):
        try:
            msgString = json.dumps(jsonMsg, indent=0, sort_keys=False)
            self.socket.send(msgString.encode())

            return True
        except Exception as e:
            pass# print(e)
                    
        return False
   
    def getMD5FromServer(self):
        
        request={}
        request['type']="GETMD5"
        self.sendMsg(request)
        response=self.checkIfRequestPending()
        
        if response!=None:
            if "data" in response:
                return response['data']
    
        return None
    
    def proccessGETMD5(self):
        
        result=self.getMD5Response()
        self.sendMsg(result)         
                    
       
    def getFileFromServer(self,path): 
        
        request={}
        request['type']="GETFILE"
        request['path']=path
        
        self.__logInfo("Downloading file:"+path,True)
        self.sendMsg(request)
        
        metaData=self.checkIfRequestPending()
        
        fileData=None
        if metaData!=None:
            if "type" in metaData and "size" in metaData and "pieces" in metaData:
                self.__logInfo("File size:"+str(metaData['size'])+" bytes",True)
                
              #  print("File divided in "+str(metaData['pieces'])+" pieces")
                fileDataArray=[]
                for x in range(0,metaData['pieces']):
                    piece=self.checkIfRequestPending()
                    percentage= (x+1)   / metaData['pieces']  * 100
                    self.__logInfo("Download status:"+str(round(percentage,2))+"%",True)
                 
                    if "type" in piece:
                        if piece['type']=="FILEDATA":
                            decodedData=base64.b64decode(piece['data'])
                            fileDataArray.append(decodedData)
                          #  if piece['pieceOrder']==1:
                         #       fileData=decodedData
                         #   else:
                          #      fileData+=decodedData
                    else:
                        self.__logInfo("Download Error:"+str(round(percentage,2))+"%",True)
                        break
                 
                fileData=b''.join(fileDataArray)   
                if fileData!=None and len(fileData)==metaData['size']:
                    return fileData
                else:
                    return None
                
            if "type" in metaData and "detail" in metaData:
                self.__logInfo("Error getting file :"+metaData['detail'],True)

        return None   
            
   
    def compareToRemoteMd5(self,homeMd5,remoteMd5):
        
        checksum_home = homeMd5
        checksum_remote = remoteMd5
    
        needUpdate_home=[]
        needDelete_home=[]
        needCreate_home=[]
    
        for x in checksum_home:
            if x in checksum_remote:
                if checksum_home[x]!=checksum_remote[x]:
                    needUpdate_home.append(x)
                #else:
                #   print("Match for "+x)
            
                del checksum_remote[x]
            else:
                needDelete_home.append(x)         
                
        for x in checksum_remote:
            needCreate_home.append(x)
             
             
        return needUpdate_home,needDelete_home,needCreate_home
    
    def connect(self):
        
        if client.connectToServer():
            return True
        return False
    
    def checkVersionWithRemote(self):

        remoteMd5=client.getMD5FromServer()
        if remoteMd5!=None:
            print("MD5 GET Success")
        else:
            print("MD5 GET Fail")
            return False,None,None,None
                 

        homeMd5=getMd5OfFilesInDir(self.installPath)
        
        needUpdate_home,needDelete_home,needCreate_home = self.compareToRemoteMd5(homeMd5, remoteMd5)
        
        if len(needUpdate_home)>0 or len(needCreate_home)>0:
            return True,needUpdate_home,needDelete_home,needCreate_home

        return False,None,None,None
    
    
    def cleanTemporaryDownloadFolder(self):
        
        
        pass
    
    
    def getSplitedPath(self,path):
        
        normPath = os.path.normpath(path)
        splited=normPath.split(os.sep)
        
        if len(splited)>0:
            if len(splited[0])==0:
                splited.pop(0)
                
        
        
        return splited
    
    def createSubdirectoryPath(self,splitedPath):
        
        if len(splitedPath)>0:
            acumPath=""
            for x in range(0,len(splitedPath)):
                acumPath+=splitedPath[x] +os.sep
                if not os.path.exists(acumPath):
                    os.makedirs(acumPath)
                      
    def saveToFile(self,path,data):
    
        rootFolderWithBar=self.tempFolder
        if not rootFolderWithBar.endswith(os.sep):
            rootFolderWithBar+=os.sep
            
        try:
            splitPath=self.getSplitedPath(rootFolderWithBar+path)
            if len(splitPath)>0:
                self.createSubdirectoryPath(splitPath[:-1])
                archivo = open(rootFolderWithBar+path,"wb")        
                archivo.write(data)                       
                archivo.close() 
                return True  
        except:
            traceback.print_exc()
            return False
    
    def downloadFilesToTempFolder(self,nu,nc):
        
        self.cleanTemporaryDownloadFolder()
        
        for x in nu:
            fileData=self.getFileFromServer(x)
            if fileData!=None:
                self.saveToFile(x,fileData)
            else:
                print("Error getting file:"+x)
                return False
            
        for x in nc:
            fileData=self.getFileFromServer(x)
            if fileData!=None:
                self.saveToFile(x,fileData)
            else:
                print("Error getting file:"+x)
                return False
            
        return True
    
def getAllFiles(dir):
    allFiles=[]
    for root, dirs, files in os.walk(dir, topdown=False):
        reducedRoot=str(root)
        if reducedRoot.startswith(dir):
            reducedRoot=reducedRoot[len(dir):]
            
        if reducedRoot.startswith("logs"):
            continue
        
        for name in files:
            if name=='base_library.zip':
                continue
            allFiles.append(os.path.join(reducedRoot, name))
        
        for name in dirs:
            allFiles.append(os.path.join(reducedRoot, name))
     
    return allFiles 



def md5OfData(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def getMd5OfFilesInDir(dir):
    
    result={}
    
    allFiles=getAllFiles(dir)
    for f in allFiles:
        if not os.path.isdir(dir+f):
            result[f]=md5(dir+f)
    
    return result


if True:
    
    HOST, PORT = "ceydvpn", 31111   
       
    datastore=None
    with open("updateConfigClient.json", 'r') as f:
        datastore = json.load(f)
    
    
    client=UpdateClient(datastore['host'], 31111,datastore['path'],datastore['tempFolder'])

    if client.connect():
        client.downloadFilesToTempFolder(['gui\\imagenes\\postgresql-11.3-1-windows-x64.exe'],[])


if False:
     
    if __name__ == "__main__":
        HOST, PORT = "ceydvpn", 31111   
       
        datastore=None
        with open("updateConfigClient.json", 'r') as f:
            datastore = json.load(f)
        
        
        client=UpdateClient(datastore['host'], 31111,datastore['path'],datastore['tempFolder'])
        result,needUpdate_home,needDelete_home,needCreate_home= client.checkVersionWithRemote()
    
        if result:
            print("Check with remote OK")
            if len(needUpdate_home)>0 or len(needDelete_home)>0 or len(needCreate_home)>0:  
                
                if len(needUpdate_home)>0:
                    print("needUpdate @home")
                    print(needUpdate_home)
                
             #   if len(needDelete_home)>0:
             #       print("needDelete @home")
             #       print(needDelete_home)
                
                if len(needCreate_home)>0:
                    print("needCreate @home")
                    print(needCreate_home)
            else:
                print("Directory are identicals, ( not checking logs dir)")
            
            client.downloadFilesToTempFolder(needUpdate_home,needCreate_home)

if False:
    
    if __name__ == "__main__":
        HOST, PORT = "", 31111   
       
        datastore=None
        with open("updateConfigClient.json", 'r') as f:
            datastore = json.load(f)
        
        client=UpdateClient("localhost", 31111,datastore['path'])
        
        if client.connectToServer():
            md5RemoteTable=client.getMD5FromServer()
            if md5RemoteTable!=None:
                print("MD5 GET Success")
                #print(md5RemoteTable)
            else:
                print("MD5 GET Fail")
              
            time.sleep(1)
            
            path="Operaciones.exe"
            dFile=client.getFileFromServer(path)
            fileMd5=md5OfData(dFile)
            
            if fileMd5==md5RemoteTable[path]:
                print("MD5 Match")
            else:
                print("MD5 Error")
                
       