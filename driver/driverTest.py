from uteTelnetDriver import UteTelnetDriver 
import logging
import json
import time


testIP="localhost"
testIP="osma-dman.ddns.net"
testPort=5555
driver = UteTelnetDriver(testIP,testPort,logging.DEBUG)

TESTREADCONFIG=True
TESTWRITECONFIG=False

TESTRESET=False

TESTDOWNLOG=False
TESTDELLOG=False
TESTUPGRADE=True

if TESTWRITECONFIG: 
    start=time.time()    
    configTest = json.load(open("configTest3.json"))
    print("Send json Test")
    print("Config To send:")
    print (configTest)
    
    jsonConfigText = json.dumps(configTest,indent=None, sort_keys=True)
    print(jsonConfigText)       
    result=driver.sendJsonConfig(configTest, False)
    
    if result:
        print("Exito")
    else:
        print("Fail")
        
    print("Time elapsed = %d secs"%(time.time()-start))  
 
        
time.sleep(3)

if TESTREADCONFIG:
    start=time.time()
    print("Get json Test")
    deviceConfig=driver.getJsonConfig()
    
    if deviceConfig:
        print(driver.convertJsonToHumanReadable(deviceConfig))
  
    print("Time elapsed = %d secs"%(time.time()-start))  
 
 
 
if TESTDOWNLOG:
    start=time.time()
    print("Log Download test")
    result, file= driver.downloadLog()
    
    if result:
        print("Log download Succes")
    else:
        print("Log download Fail")
    print("Time elapsed = %d secs"%(time.time()-start)) 
     
if TESTDELLOG:
    start=time.time()
    print("Log Delete test")
    result= driver.deleteLog()
    
    if result:
        print("Log delete Success")
    else:
        print("Log delete Fail")
    print("Time elapsed = %d secs"%(time.time()-start))  
 
  
if TESTUPGRADE:
    start=time.time()
    print("Firmware Upgrade test")
    if driver.firmwareUpdateFromPath("C:/Repositorios/modemute_2018_git/rtos_basic.bin"):
        print("Firmware Upgrade  Test Success")
    else:
        print("Firmware Upgrade Test Fail")
        
    print("Time elapsed = %d secs"%(time.time()-start))  
 
if TESTRESET:
    print("Reset test")
    if driver.reset():
        print("Reset Test Success")
    else:
        print("Reset Test Fail")
    print("Time elapsed = %d secs"%(time.time()-start))  
 
 
    
    