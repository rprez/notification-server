import os
import sys

import hashlib


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

#print(sys.argv)


if(len(sys.argv)==3):
   
    homeDir=sys.argv[1]
    remoteDir=sys.argv[2]
    
    if len(homeDir)>0:
        if not homeDir.endswith("/"):
            homeDir+="/"
    
    if len(remoteDir)>0:
        if not remoteDir.endswith("/"):
            remoteDir+="/"
    print("comparing home dir: "+homeDir+ " with remote: "+remoteDir)
    checksum_home = getMd5OfFilesInDir(homeDir)
    checksum_remote = getMd5OfFilesInDir(remoteDir)
    
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
    
    
    
  #  print(fmd5)
    
        
    
