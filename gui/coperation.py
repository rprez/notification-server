from PySide2 import QtCore, QtGui, QtWidgets
import socket
import re
import json
import csv
import os
from operation.operation import Operation
# from operation.operationmgr import OperationMgr

class OperationDialog(QtWidgets.QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, operMngr):
        super(OperationDialog, self).__init__()

        self.operMngr = operMngr
        self.parteVariable = None
        self.createOperationBox()
        
        
        self.createLoadConfigFile()
        self.createLoadFirmwareFile()
        self.createSaveConfigFileDir()
     #   self.createMenu()    

        mainLayout = QtWidgets.QGridLayout()
        
        
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

       # buttonBox.accepted.connect(self.accept)
        buttonBox.accepted.connect(self.crearOperacion)
        buttonBox.rejected.connect(self.reject)

        
   #     mainLayout.setMenuBar(self.menuBar)
   
        mainLayout.addWidget(self.operationBox)
        mainLayout.addWidget(self.filePathBox)
        mainLayout.addWidget(self.firmwareFilePathBox)
        mainLayout.addWidget(self.dirFilePathBox)
        mainLayout.addWidget(buttonBox)
     #   mainLayout.addWidget(self.apnbox,0,0)
     #   mainLayout.addWidget(self.autoresetbox,0,1)
      #  mainLayout.addWidget(self.serialPortBox,1,0)
      #  mainLayout.addWidget(self.surelinkBox,1,1)
      
      #  mainLayout.addWidget(self.netModeBox)
      #  mainLayout.addWidget(self.lastgaspbox)
      #  mainLayout.addWidget(self.bandsbox)
       
      #  mainLayout.addWidget(self.utepingbox)
      #  mainLayout.addWidget(self.udpAlertBox)
      #  mainLayout.addWidget(self.ipfilterBox)
  
        self.setLayout(mainLayout)        
        self.setWindowTitle("Crear nueva operacion")
        
         
        ipRange = "([1-9][0-9]|[0-9]|2[0-4][0-9]|25[0-5]|1[0-9][0-9])";
        ipRegex = "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$"
       
        self.pattern = re.compile(ipRegex)
       
    def crearOperacion(self):
        
        print("creado") 
        
        [ok, targets] = self.getTargets()
        reintentos = self.cantidadReintentos.currentIndex()
        intervalReintentos=self.intervaloReintentos.currentIndex()
        passwd=self.passwd.text()
        acceptClick=False
        if ok:
            value = self.operationCombo.currentText()
            if value == "Enviar configuracion":
                path = self.configFilePath.text()
                if len(path) > 0:
                    if os.path.exists(path):
                        for x in targets:
                            params = {}
                            params['reintentos'] = [reintentos,intervalReintentos]
                            params['oper'] = "WRITECONFIG"
                            params['params'] = path
                            params['target'] = x
                            params['resetAfter']=self.resetAfterSuccess.isChecked()
                            self.operMngr.encolarOperacion(Operation(params,passwd))  
                            acceptClick=True   
               
            elif value == "Leer configuracion":
                if self.notSaveResult.isChecked():
                    for x in targets:
                        params = {}
                        params['reintentos'] = [reintentos,intervalReintentos]

                        params['oper'] = "READCONFIG"
                        params['params'] = None
                        params['target'] = x
                         
                        self.operMngr.encolarOperacion(Operation(params,passwd))
                        acceptClick=True   
                    
                else:
                    path = self.dirFilePath.text()
                    if len(path) > 0:
                        if os.path.isdir(path):
                            for x in targets:
                                params = {}
                                params['reintentos'] = [reintentos,intervalReintentos]


                                params['oper'] = "READCONFIG"
                                params['params'] = path
                                params['target'] = x
                                 
                                self.operMngr.encolarOperacion(Operation(params,passwd)) 
                            acceptClick=True   
                        
            elif value == "Upgrade de firmware":
                path = self.firmwareFilePath.text()
                if len(path) > 0:
                    if os.path.exists(path):
                        for x in targets:
                            params = {}
                            params['reintentos'] = [reintentos,intervalReintentos]


                            params['oper'] = "UPGRADE"
                            params['params'] = path
                            params['target'] = x
                             
                            self.operMngr.encolarOperacion(Operation(params,passwd))   
                        acceptClick=True     
                        
            elif value == "Descargar log":
                if self.notSaveResult.isChecked():
                    for x in targets:
                        params = {}
                        params['reintentos'] = [reintentos,intervalReintentos]

                        params['oper'] = "DOWNLOADLOG"
                        params['params'] = None
                        params['target'] = x
                         
                        self.operMngr.encolarOperacion(Operation(params,passwd)) 
                    acceptClick=True     
                else:
                    path = self.dirFilePath.text()
                    if len(path) > 0:
                        if os.path.isdir(path):
                            for x in targets:
                                params = {}
                                params['reintentos'] = [reintentos,intervalReintentos]
                                
                                params['oper'] = "DOWNLOADLOG"
                                params['params'] = path
                                params['target'] = x
                                 
                                self.operMngr.encolarOperacion(Operation(params,passwd)) 
                            acceptClick=True       
                     
                   
            elif value == "Borrar log":
                
                for x in targets:
                    params = {}
                    params['reintentos'] = [reintentos,intervalReintentos]

                    params['oper'] = "BORRARLOG"
                    params['params'] = None
                    params['target'] = x
                     
                    self.operMngr.encolarOperacion(Operation(params,passwd))
                    acceptClick=True    
                
                
                
            elif value == "Reset":
                
                for x in targets:
                    params = {}
                    params['reintentos'] = [reintentos,intervalReintentos]

                    params['oper'] = "RESET"
                    params['params'] = None
                    params['target'] = x
                     
                    self.operMngr.encolarOperacion(Operation(params,passwd))
                    acceptClick=True    
                
                pass
            
            if acceptClick:
                self.accept() 
        else:
            QtWidgets.QMessageBox.information(self, "Error", "Error al parsear Targets : %s" % (targets))
           
          
    
    def __validIP(self, text):
       
        mtext=text
        if ":" in mtext:
            pedazos=mtext.split(":")
            if len(pedazos)==2:
                mtext=pedazos[0]
                try:
                    puerto=int(pedazos[1])
                    if not (puerto>0 and puerto<65535):
                        return False
                except:
                    return False
                
        if self.pattern.match(mtext):
            return True
        
        return False
    
    def getTargets(self):
        
        linea = self.targetLine.text()
        
        pedazos = linea.split(",")
        targets = []
        for x in pedazos:
            t = x.strip()
            if self.__validIP(t):
                targets.append(t)
            else:
                return [False , t]
        
        return [True, targets]
        
    def createMenu(self):
        self.menuBar = QtWidgets.QMenuBar()

        self.fileMenu = QtWidgets.QMenu("&File", self)
        self.guardar = self.fileMenu.addAction("G&uardar como")
        self.cargar = self.fileMenu.addAction("C&argar")        
        self.exitAction = self.fileMenu.addAction("E&xit")
        self.menuBar.addMenu(self.fileMenu)

        self.exitAction.triggered.connect(self.accept)
        self.guardar.triggered.connect(self.guardarConfig)
        self.cargar.triggered.connect(self.cargarConfig)

    def operationTypeChange(self, value):
        
        if value == "Enviar configuracion":
            self.parteVariable.hide()
            self.filePathBox.show()
            self.parteVariable = self.filePathBox
        elif value == "Leer configuracion":
            self.parteVariable.hide()
            self.dirFilePathBox.show()
            self.parteVariable = self.dirFilePathBox  
        elif value == "Upgrade de firmware":
            self.parteVariable.hide()
            self.firmwareFilePathBox.show()
            self.parteVariable = self.firmwareFilePathBox
            pass
        elif value == "Descargar log":
            self.parteVariable.hide()
            self.dirFilePathBox.show()
            self.parteVariable = self.dirFilePathBox
        elif value == "Borrar log" or value == "Reset":
            self.parteVariable.hide()
        

    def createOperationBox(self):
        self.operationBox = QtWidgets.QGroupBox("Operacion")
        
        self.operationCombo = QtWidgets.QComboBox()
        self.operationCombo.addItems(["Enviar configuracion", "Leer configuracion", "Upgrade de firmware", "Descargar log", "Borrar log", "Reset"])
        self.operationCombo.setCurrentIndex(0)
        
        self.operationCombo.currentTextChanged.connect(self.operationTypeChange)        
        self.targetLine = QtWidgets.QLineEdit("127.0.0.1")        
        self.targetLoadCsvButton = QtWidgets.QPushButton("csv")
        self.targetLoadCsvButton.clicked.connect(self.cargarTargetIps)
        
        self.cantidadReintentos = QtWidgets.QComboBox()
        self.cantidadReintentos.addItems(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])
        self.cantidadReintentos.setCurrentIndex(0)
        
        
        self.intervaloReintentos = QtWidgets.QComboBox()
        intervals=[]
        for x in range(0,61):
            intervals.append(str(x))
        self.intervaloReintentos.addItems(intervals)
        self.intervaloReintentos.setCurrentIndex(5)
        
        
        self.passwd = QtWidgets.QLineEdit("")   
        self.passwd.setEchoMode(QtWidgets.QLineEdit.Password)
     
      
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Operacion:"), self.operationCombo)
        layout.addRow(QtWidgets.QLabel("Target ip:"), self.targetLine)
        layout.addRow(QtWidgets.QLabel("Cargar ip desde archivo:"), self.targetLoadCsvButton)
        layout.addRow(QtWidgets.QLabel("Contraseña:"), self.passwd)

        layout.addRow(QtWidgets.QLabel("Cantidad de reintentos:"), self.cantidadReintentos)
        layout.addRow(QtWidgets.QLabel("Minutos entre reintentos:"), self.intervaloReintentos)
      
       
        self.operationBox.setLayout(layout)
    
    
    def createLoadConfigFile(self):
        
        self.filePathBox = QtWidgets.QGroupBox("Archivo de configuracion")        
        self.parteVariable = self.filePathBox        
        self.configFilePath = QtWidgets.QLineEdit()        
        self.findFileButton = QtWidgets.QPushButton("Cargar")
        
        self.resetAfterSuccess = QtWidgets.QCheckBox()
        self.resetAfterSuccess.setChecked(False)
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Path:"), self.configFilePath)
        layout.addRow(QtWidgets.QLabel(""), self.findFileButton)
        layout.addRow(QtWidgets.QLabel("Reset al final:"), self.resetAfterSuccess)
        
        self.findFileButton.clicked.connect(self.cargarConfigFile)
        self.filePathBox.setLayout(layout)
    
    def createLoadFirmwareFile(self):
        
        self.firmwareFilePathBox = QtWidgets.QGroupBox("Archivo de firmware")
        self.firmwareFilePath = QtWidgets.QLineEdit()
        self.firmwareFindFileButton = QtWidgets.QPushButton("Cargar")
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Path:"), self.firmwareFilePath)
        layout.addRow(QtWidgets.QLabel(""), self.firmwareFindFileButton)
        
        self.firmwareFindFileButton.clicked.connect(self.cargarFirmwareFile)
        self.firmwareFilePathBox.setLayout(layout)
        self.firmwareFilePathBox.hide()
    
    def createSaveConfigFileDir(self):
        
        self.dirFilePathBox = QtWidgets.QGroupBox("Directorio destino")
        self.dirFilePath = QtWidgets.QLineEdit()
        self.dirFindFileButton = QtWidgets.QPushButton("Cargar")
        
        
        self.notSaveResult = QtWidgets.QCheckBox()
        self.notSaveResult.setChecked(False)
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Dir:"), self.dirFilePath)
        layout.addRow(QtWidgets.QLabel(""), self.dirFindFileButton)
        layout.addRow(QtWidgets.QLabel("No guardar:"), self.notSaveResult)
        
        
        self.notSaveResult.stateChanged.connect(self.checkBoxNoGuardarChange)
        self.dirFindFileButton.clicked.connect(self.selectDir)
        self.dirFilePathBox.setLayout(layout)
        self.dirFilePathBox.hide()
    
    def checkBoxNoGuardarChange(self, event):  
        if event == 2:
            self.dirFindFileButton.setEnabled(False)
            self.dirFilePath.setEnabled(False)
        else:
            self.dirFindFileButton.setEnabled(True)
            self.dirFilePath.setEnabled(True)
        
    def guardarConfig(self):
      
        config = self.getConfigFromDialog()
       
        if config != None:
            filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar como",
                    QtCore.QDir.currentPath(), "Config file (*.json)")
            
            if len(filePath[0]) > 0:
                configString = json.dumps(config, indent=2, sort_keys=True)
                        
                archivo = open(filePath[0], "w+")        
                archivo.write(configString)                       
                archivo.close()   
        else:
          
            QtWidgets.QMessageBox.information(self, "Error", "Configuracion vacia")
           
           
    
    def cargarTargetIps(self):
        
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Cargar",
                QtCore.QDir.currentPath(), "Csv file (*.csv)")

        if len(filePath[0]) > 0: 
            try:          
                newTargets = ""
                with open(filePath[0], 'r') as csvfile:
                    csvFile = csv.reader(csvfile, delimiter=',', quotechar='|')
                    for row in csvFile:
                        newTargets += ', '.join(row)
                
                oldTargets = self.targetLine.text()
                if len(oldTargets.strip()) > 0:              
                    self.targetLine.setText(oldTargets + "," + newTargets)
                else:
                    self.targetLine.setText(newTargets)
                    
                
             
            except Exception as e:
                print("No se pudo parsear configuracion")            
                print(e)
            
    
    def cargarConfigFile(self):
        
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Cargar",
                QtCore.QDir.currentPath(), "Config file (*.json)")

        if len(filePath[0]) > 0: 
            
            self.configFilePath.setText(filePath[0])
     
    def selectDir(self):
        
        dirPath = QtWidgets.QFileDialog.getExistingDirectory()
        
        if len(dirPath) > 0: 
            
            self.dirFilePath.setText(dirPath)
            
    def cargarFirmwareFile(self):
        
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Cargar",
                QtCore.QDir.currentPath(), "Firmware binary file (*.bin)")

        if len(filePath[0]) > 0: 
            
            self.firmwareFilePath.setText(filePath[0])
                  
    
        
if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = OperationDialog()
    sys.exit(dialog.exec_())
