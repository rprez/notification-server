from PySide2 import QtCore, QtGui, QtWidgets
#import application_rc
import time
import datetime
import json
import threading
import queue

from driver.uteTelnetDriver import UteTelnetDriver

class TargetConfig(QtWidgets.QDialog):
   
   
    targetConnect=QtCore.Signal(dict)
    def __init__(self):
        super(TargetConfig, self).__init__()

        self.createTargetBox()
        
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

       # buttonBox.accepted.connect(self.accept)
        buttonBox.accepted.connect(self.conectarTarget)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QGridLayout()
      #  mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.targetBox)
        mainLayout.addWidget(buttonBox)
  
        self.setLayout(mainLayout)
        self.setWindowTitle("Conectar")
     
     
         
    def conectarTarget(self):
        
        config={}
        config['ip']=self.targetip.text().strip()
        config['pass']=self.targetPass.text()
        
        #print (config)
        
        self.targetConnect.emit(config)
        self.accept()
    
    def createTargetBox(self):
        
        self.targetBox = QtWidgets.QGroupBox("Conectar con dispositivo")
        self.targetip = QtWidgets.QLineEdit(self)
        self.targetPass = QtWidgets.QLineEdit(self)
        self.targetPass.setEchoMode(QtWidgets.QLineEdit.Password)
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("ip:"),self.targetip)
        layout.addRow(QtWidgets.QLabel("password:"), self.targetPass)      
      
        self.targetBox.setLayout(layout)


class ModoMonitorWindows(QtWidgets.QMainWindow):
    
   
    def __init__(self):
        super(ModoMonitorWindows, self).__init__()

       # self.curFile = ''

        
        mainLayout = QtWidgets.QVBoxLayout()
        
        self.createViews() 
        
       # mainLayout.addWidget(self.horizontalGroupBox)
       # self.setLayout(self.listLayout)
        self.setWindowTitle("Modo monitor")
        self.setWindowIcon(QtGui.QIcon('./gui/imagenes/lupa.png'))

        wit=QtWidgets.QWidget()
        wit.setLayout(self.mainLayout)
        self.setCentralWidget(wit)
                #self.setLayout(mainLayout)

        self.createActions()
      #  self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.targetConfig=TargetConfig()
        self.targetConfig.targetConnect.connect(self.conectarNuevoTarget)

        self.showDate=True

        self.rxStr=""
        self.txStr=""
        self.listRx=[]
        self.listTx=[]
        
    def conectarNuevoTarget(self,config):
        ip=config['ip']
        passwd=config['pass']
        
        self.listRx=[]
        self.listTx=[]
        self.rxStr=""
        self.txStr=""
        self.updateAllViewsFromSource()
        print("Conectando nuevo con dispositivo")
        self.updateStatusBar("Conectando con dispositivo")
        self.mmControl=queue.Queue()
        self.mmHandler=MonitorModeHandler(ip,passwd,self.mmControl)
        
        self.mmHandler.ss.sendNotification.connect(self.updateStatusBar)
        self.mmHandler.ss.appendSerial.connect(self.appendSerial)
        self.mmHandler.ss.appendTcp.connect(self.appendTcp)
        
        self.mmHandler.ss.conectionStatus.connect(self.setConectionIndication)
        
        self.mmHandler.start()
        
    def createActions(self):
        
        self.tconfig = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/plugged.png'), "&Configurar Target",
                self,statusTip="Configurar target", triggered=self.showTargetConfig)
        
        self.code_hex = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/code_hex.png'), "&Convertir a hex",
                self,statusTip="Convertir a hex", triggered=self.setHex)
       # self.code_hex.setDisabled(True)
        
        self.code_txt = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/code_txt.png'), "&Convertir a txt",
                self,statusTip="Convertir a txt", triggered=self.setTxt)
        
        self.unlink = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/unplugged.png'), "&Desconectar Target",
                self,statusTip="Desconectar Target", triggered=self.desconectarTarget)
        
        self.unlink.setDisabled(True)
        
           
        self.toggleTime = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/watchon.png'), "&Mostrar/No mostrar hora",
                self,statusTip="Mostrar/No mostrar hora", triggered=self.toggleTimeInText)
     
     
        
        self.code=0
        self.code_txt.setDisabled(True)

    def toggleTimeInText(self):
        
        if self.showDate:
            self.toggleTime.setIcon(QtGui.QIcon('./gui/imagenes/watchoff.png'))
            self.showDate=False
        else:
            self.showDate=True
            self.toggleTime.setIcon(QtGui.QIcon('./gui/imagenes/watchon.png'))

        self.updateAllViewsFromSource()
        
    def desconectarTarget(self):
        
        self.mmControl.put("end")
        self.mmHandler.modemDriver.abort=True
        
    def convertirAHex(self):
        print("to Hex") 
        self.code=1
   
        self.updateAllViewsFromSource()
    def convertirATxt(self):
        print("to Txt") 
        self.code=0
        
        self.updateAllViewsFromSource()
        
    def setHex(self):
        
        self.code_txt.setEnabled(True)
        self.code_hex.setDisabled(True)
        self.convertirAHex()
    
    def setTxt(self):
        
        self.code_hex.setEnabled(True)
        self.code_txt.setDisabled(True)
        self.convertirATxt()
        
    def showTargetConfig(self):
        print("target config")  
        self.targetConfig.show()
  
    def updateStatusBar(self,msg):
        self.statusBar().showMessage(msg)
        
    def createViews(self):
        
         #self.horizontalGroupBox = QtWidgets.QGroupBox("Horizontal layout")
        self.mainLayout = QtWidgets.QHBoxLayout()
        
        self.infoTcp= QtWidgets.QTextEdit()
        self.infoTcp.setPlainText("")
        self.infoTcp.setReadOnly(True)
        self.infoTcp.setFontPointSize(10)
        
           
        
        self.infoTcp.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.infoTcp.customContextMenuRequested.connect(self.handleTcpPopMenu)
     
     
        self.infoTcpBox = QtWidgets.QGroupBox("Serial Rx")
        layIt = QtWidgets.QHBoxLayout()
        layIt.addWidget(self.infoTcp)
        self.infoTcpBox.setLayout(layIt)
        
        self.infoSerial= QtWidgets.QTextEdit()
        self.infoSerial.setPlainText("")
        self.infoSerial.setReadOnly(True)
        self.infoSerial.setFontPointSize(10)
         
        
        self.infoSerial.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.infoSerial.customContextMenuRequested.connect(self.handleSerialPopMenu)
        
        self.infoSerialBox = QtWidgets.QGroupBox("Serial Tx")
        layIs = QtWidgets.QHBoxLayout()
        layIs.addWidget(self.infoSerial)
        self.infoSerialBox.setLayout(layIs)

        self.mainLayout.addWidget(self.infoTcpBox)        
        self.mainLayout.addWidget(self.infoSerialBox)        
     
    def guardarLogSerial(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar como", QtCore.QDir.currentPath(),"text file (*.txt)")  
        if len(filePath[0])>0:
            dataString = self.infoSerial.toPlainText()       
            archivo = open(filePath[0],"w+")        
            archivo.write(dataString)                       
            archivo.close()   
    def handleSerialPopMenu(self,pos):

        menu = QtWidgets.QMenu() 
        action = QtWidgets.QAction("guardar como", self)       
        action.triggered.connect(lambda : self.guardarLogSerial())
        menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())
        
    def guardarLogTcp(self):
        filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar como", QtCore.QDir.currentPath(),"text file (*.txt)")  
        if len(filePath[0])>0:
            dataString = self.infoTcp.toPlainText()       
            archivo = open(filePath[0],"w+")        
            archivo.write(dataString)                       
            archivo.close()   
            
    def handleTcpPopMenu(self,pos):
        menu = QtWidgets.QMenu() 
        action = QtWidgets.QAction("Guardar como", self)       
        action.triggered.connect(lambda : self.guardarLogTcp())
        menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())
        
    def closeEvent(self, event):
        event.accept()
    
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
    
    def createToolBars(self):
        self.fileToolBar = self.addToolBar("Configuration")
        self.fileToolBar.addAction(self.tconfig)
        self.fileToolBar.addAction(self.unlink)
        self.fileToolBar.addAction(self.code_txt)
        self.fileToolBar.addAction(self.code_hex)
        self.fileToolBar.addAction(self.toggleTime)

    def setConectionIndication(self,state):
        print("conection state" + str(state))
        if state:
            self.hookIndication.setIcon(QtGui.QIcon('./gui/imagenes/plugged.png'))
            self.unlink.setDisabled(False)
        else:
            self.hookIndication.setIcon(QtGui.QIcon('./gui/imagenes/unplugged.png'))
            self.unlink.setDisabled(True)

    def createStatusBar(self):
        
        self.hookIndication=QtWidgets.QPushButton(icon=QtGui.QIcon('./gui/imagenes/unplugged.png'))
        self.hookIndication.setFlat(True)
        self.statusBar().addPermanentWidget(self.hookIndication)
    
    def appendTcp(self,newData):
        print("Apending Tcp")   
                
        print(newData)
        
        for x in newData:
            self.listTx.append(x)
            self.appendTcpDataWithTime(x, self.showDate, self.code)
            
        self.updateTcpView()
        
        
    def updateAllViewsFromSource(self):
        
        self.rxStr=""
        for x in self.listRx:
            self.appendSerialDataWithTime(x, self.showDate, self.code)
         
        self.updateSerialView()
   
        self.txStr=""
        for x in self.listTx:
            self.appendTcpDataWithTime(x, self.showDate, self.code)
          
        self.updateTcpView()   
        
    def appendSerial(self,newData): 
        print("Apending Serial")   
        
        print(newData)
        
        for x in newData:
            self.listRx.append(x)
            self.appendSerialDataWithTime(x, self.showDate, self.code)
            
        self.updateSerialView()
    
    def updateTcpView(self):
       
        if self.showDate:
            self.infoTcp.setText("<html>"+self.txStr+"</html>")
        else:
            self.infoTcp.setText(self.txStr)
            
        self.infoTcp.verticalScrollBar().setSliderPosition(self.infoTcp.verticalScrollBar().maximum())

    def appendTcpDataWithTime(self,x,withDate,modeCode):
        
        newString=""
        if modeCode==0:
            if withDate:
                newString+="<br><b>" +x['fecha']+" :</b>"
                newString+=x['data'].replace("\n","<br>")
            else:
                newString+=x['data']
        else:
            text=" ".join("{:02x}".format(ord(c)) for c in  x['data'])

            if withDate:
                newString+="<br><b>" +x['fecha']+" :</b>"
                newString+=text
            else:
                newString+=text
               
            
        self.txStr+=newString
    
          
    def appendSerialDataWithTime(self,x,withDate,modeCode):
        
        newString=""
        if modeCode==0:
           
            if withDate:
                newString+="<br><b>" +x['fecha']+" :</b>"
                newString+=x['data'].replace("\n","<br>")
            else:
                newString+=x['data']
        else:
            text=" ".join("{:02x}".format(ord(c)) for c in  x['data'])

            if withDate:
                newString+="<br><b>" +x['fecha']+" :</b>"
                newString+=text
            else:
                newString+=text
        self.rxStr+=newString
    
    def updateSerialView(self):
        
        if self.showDate:
            self.infoSerial.setText("<html>"+self.rxStr+"</html>")
        else:
            self.infoSerial.setText(self.rxStr)

      #  if self.code==0:
      #      self.infoSerial.setText("".join(self.listRx))
     #   else:
    #        text=" ".join(hex(ord(n)) for n in self.listRx)
       #     self.infoSerial.setText(text)
        
        self.infoSerial.verticalScrollBar().setSliderPosition(self.infoSerial.verticalScrollBar().maximum())
   
      
  
class SignalMM(QtCore.QObject):
    
    appendTcp=QtCore.Signal(list)
    appendSerial=QtCore.Signal(list)
    sendNotification=QtCore.Signal(str)
    conectionStatus=QtCore.Signal(bool)
    
   
class MonitorModeHandler(threading.Thread):
    
    def __init__(self,host,passwd,q_control):
        threading.Thread.__init__(self)
        
        self.q_tcp=queue.Queue()
        self.q_serial=queue.Queue()
        self.l_tcp=threading.Lock()
        self.l_serial=threading.Lock()
        self.q_control=q_control
        
        self.outputQueue=queue.Queue()
        self.modemDriver=UteTelnetDriver(host, self.outputQueue, 53300 )
        
        self.ss=SignalMM()
    
    
    def startModoMonitor(self):
        self.modemDriver.modoMonitor(self.q_control, self.q_tcp, self.q_serial, self.l_tcp, self.l_serial)
        self.modemDriver.closeSocket()
        
    def run(self):
        
        workingT=threading.Thread(target=self.startModoMonitor)
        workingT.setDaemon(True)
        workingT.start()
        while True:
            
            
            tcpList=[]
            if not self.q_tcp.empty():
                self.l_tcp.acquire()
                
                while not self.q_tcp.empty():
                    tcpList.append(self.q_tcp.get())
                self.l_tcp.release()
                
                self.ss.appendTcp.emit(tcpList)
               
            serialList=[] 
            if not self.q_serial.empty():
                self.l_serial.acquire()
                
                while not self.q_serial.empty():
                    serialList.append(self.q_serial.get())
                self.l_serial.release()
                
                self.ss.appendSerial.emit(serialList)
 
            if not self.outputQueue.empty():
                while not  self.outputQueue.empty():
                    newMsg=self.outputQueue.get()
                    self.ss.sendNotification.emit(newMsg)
                    if newMsg=="Modo monitor iniciado":
                        self.ss.conectionStatus.emit(True)
                 
            if not workingT.is_alive():
                print("modo monitor thread end")
                if not self.outputQueue.empty():
                    while not  self.outputQueue.empty():
                        newMsg=self.outputQueue.get()
                        self.ss.sendNotification.emit(newMsg)
                
                self.ss.conectionStatus.emit(False)      
                break
                
            time.sleep(0.1)    
            
            
        
        

          
#if __name__ == '__main__':

 #   import sys

 #   app = QtWidgets.QApplication(sys.argv)
 #   mainWin = ModoMonitorWindows()
 #   mainWin.show() 
#    mainWin.mmClient.start()

#sys.exit(app.exec_())
