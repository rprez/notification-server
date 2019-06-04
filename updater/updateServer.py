import threading
import json
import time
import socket
import os
import hashlib
import base64
import traceback
import math

class DownloadableJsonFileBase64():
    
    def __init__(self,path,sizePiece):
        self.path=path
        
        self.pieceCounter=0
        self.pieceTotal=0
        self.sizePiece=sizePiece
        self.largoFile=0
        self.file=None
       
       
    def getNextChunk(self):
        while True:
            data = self.file.read(self.sizePiece)
            if not data:
                break
            yield data

    def prepareDownload(self):
        
        try:
            self.file=open(self.path, mode='rb')
            self.largoFile=os.path.getsize(self.path)
            return True
        except:
            return False 
           
    def getMetadata(self):
        
        if self.file!=None:
            self.pieceTotal= math.ceil(self.largoFile/self.sizePiece)
            
            metaData={}
            metaData['type']="FILERESPONSE"
            metaData['size']=self.largoFile
            metaData['pieces']=self.pieceTotal
            
            return metaData
        
        return None
          
    def getNextPiece(self):
        
        while True:
            data = self.file.read(self.sizePiece)
            if not data:
                break

            encodedDataUTF= base64.b64encode(data).decode('utf-8',errors="ignore")
            self.pieceCounter+=1
            newPiece={}
            newPiece['type']="FILEDATA"
            newPiece['pieceOrder']=self.pieceCounter
            newPiece['data']=encodedDataUTF
            yield newPiece
        
        return None
       
    def getNextPiece_old(self):
        
        if self.pieceCounter<=self.pieceTotal:
            indiceInf=self.pieceCounter*self.sizePiece
            indiceSup=indiceInf+self.sizePiece
            if indiceSup>self.largoFile:
                indiceSup=self.largoFile
            pice = self.fileContent[indiceInf:indiceSup]
            encodedDataUTF= base64.b64encode(pice).decode('utf-8',errors="ignore")
            self.pieceCounter+=1
            newPiece={}
            newPiece['type']="FILEDATA"
            newPiece['pieceOrder']=self.pieceCounter
            newPiece['data']=encodedDataUTF
            return newPiece
        
        return None

           
class SocketHandler_Updater (threading.Thread):
    
    def __init__(self,client,md5Table,installPath):
                threading.Thread.__init__(self)
                
                self.socketClient = client 
                self.stream=""
                self.md5Table=md5Table
                self.installPath=installPath
    
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
               
    def checkIfRequestPending(self):
    
        [pendingJsonRequest,pendingFin]=self.__findJson(self.stream)
        if pendingJsonRequest!=None:
            self.stream=self.stream[pendingFin+1::]
            return pendingJsonRequest
        
        try:  
            data=self.socketClient.recv(1024)
           
            if len(data)==0:
                return None
              
            data=data.decode('utf-8',errors="ignore")
            self.stream+=data
            
            
            [jsonResult,fin]=self.__findJson(self.stream)
            if jsonResult!=None:
               
                self.stream=self.stream[fin+1::]
                return jsonResult
            
        except Exception as e:
            pass
            
        return None
    
    def sendMsg(self, jsonMsg):
      
        msgString = json.dumps(jsonMsg, indent=0, sort_keys=False)
        self.socketClient.send(msgString.encode())

        return True
 
    def getMD5Response(self):
        
        response={}
        response['type']="GETMD5_RESPONSE"
        response['data']=self.md5Table
        return response
        
    def proccessGETMD5(self):
        
        result=self.getMD5Response()
        self.sendMsg(result)         
        
        
    def loadFile(self,path):
        
        fileContent=None
        with open(self.installPath+path, mode='rb') as file: # b is important -> binary
            fileContent = file.read()     
        return fileContent
       
    def splitFileEncoded64(self,dataFile,size):
        
        data=dataFile
        largo=len(dataFile)
           
        arrs = []
        count=1
        while len(data) > size:
            pice = data[:size]
            data   = data[size:]
            
            encodedDataUTF= base64.b64encode(pice).decode('utf-8',errors="ignore")
            arrs.append([count,encodedDataUTF])
            count+=1
            
        if len(data)>0:
            
            encodedDataUTF= base64.b64encode(data).decode('utf-8',errors="ignore")
            arrs.append([count,encodedDataUTF])
            
        return arrs 

    def getFileResponse(self,request):
        
        if "path" in request:
            if request['path'] in self.md5Table:
                
                downloadableFile=DownloadableJsonFileBase64(self.installPath+request['path'], 50000)
                metaData={}
                metaData['type']="DOWNLOADABLE_FILE"
                if downloadableFile.prepareDownload():
                    metaData['file']=downloadableFile
                    return metaData
                 
        print("requested file not found!!, returning json with error")              
        metaData={}
        metaData['type']="FILERESPONSE_ERROR"
        metaData['detail']="File requested not found"
        return metaData

    def proccessGETFILE(self,request): 
        response = self.getFileResponse(request)
        try:
            if response:
                if "type" in response:
                    if response['type']=="FILERESPONSE_ERROR":
                        self.sendMsg(response)
                    else:
                        meta= response['file'].getMetadata()
                        self.sendMsg(meta)
                        
                        for x in response['file'].getNextPiece():
                            self.sendMsg(x)
            else:
                print("responses gETFILE NOne")
        except :
            traceback.print_exc()
    
    def processRequest(self,request):
        if "type" in request:
            if request['type']=="GETMD5":
                self.proccessGETMD5()
            elif request['type']=="GETFILE":
                if "path" in request:
                    self.proccessGETFILE(request)
                    
    
    def run(self):     
    
        while True:            
        
            requestJson=self.checkIfRequestPending()
            
            if requestJson!=None:                  
                self.processRequest(requestJson)
            else:
                print("Error receiving Request")   
                break
          #  time.sleep(0.5)   
       

        try:
            self.socketClient.close()
            self.socketClient.shutdown()
        except Exception as e:
            pass
        print("Handler Ended")



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





if __name__ == "__main__":
    HOST, PORT = "", 31111   
   
    
    datastore=None
    with open("updateConfig.json", 'r') as f:
        datastore = json.load(f)
    
    
    md5Table=getMd5OfFilesInDir(datastore['path'])
    
    
    # conection receiver
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(20)
    
    
    while True:

        print("Waiting connection")
        print("Active Thread Count Before enviarFile: %d" % (threading.activeCount()))
        client, fromaddr = server_socket.accept()                
         
        handler=SocketHandler_Updater(client,md5Table,datastore['path'])
        handler.setDaemon(True)
        handler.start()
        print("Connection accepted from ")
        print(fromaddr)
        ip = fromaddr[0]
       