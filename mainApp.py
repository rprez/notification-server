from gui.mainwindows import MainWindow
from PySide2 import QtCore, QtGui, QtWidgets
import sys
import traceback
import logging
import os
import datetime
from logging.handlers import RotatingFileHandler

if __name__ == '__main__':

    loggerHandler = logging.getLogger("Operations")
    loggerHandler.setLevel(logging.DEBUG)

    if not os.path.exists("./logs"):
        os.makedirs("./logs")
        ## create a file handler

    if not os.path.exists("./logs/operaciones"):
        os.makedirs("./logs/operaciones")
        
    #global logger,consoleHandler
    loggerH = RotatingFileHandler('./logs/operaciones/'+"operaciones"+'.log', maxBytes=10000000, backupCount=4)
   # loggerH = logging.FileHandler('./logs/operaciones/'+"operaciones"+'.log')  #agregar hora antes del nombre
    loggerH.setLevel(logging.DEBUG)
    
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    loggerH.setFormatter(formatter)
    
    # create console logging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    
    # add the handlers to the logger
    loggerHandler.addHandler(loggerH)
    loggerHandler.addHandler(consoleHandler)  
    
    loggerHandler.debug("\n\nIniciando Operaciones\n\n")
    
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
    
    
    def exceptHook( exceptionType, exceptionValue, exceptionTraceback):   
        
        global loggerHandler
        tb=traceback.format_exception(exceptionType, exceptionValue, exceptionTraceback)
        #traceback.print_tb(exceptionTraceback)
        loggerHandler.fatal("".join(tb))
        saveCrashReport("".join(tb))
    
    
    sys.excepthook = exceptHook
    app = QtWidgets.QApplication(sys.argv)
    mainWin = MainWindow(loggerHandler)
    mainWin.show()
    mainWin.operMngr.start()
    sys.exit(app.exec_())
    
    print("exit")
#
#    print("exception trapped " +traceback.format_exc())