from PySide2 import QtCore, QtGui, QtWidgets
import json

class NotificationConfigDialog(QtWidgets.QDialog):
   
   
    notiTargetUpdate=QtCore.Signal(dict)
    def __init__(self):
        super(NotificationConfigDialog, self).__init__()

        self.createUdpAlertBox()
        
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

       # buttonBox.accepted.connect(self.accept)
        buttonBox.accepted.connect(self.actualizarTarget)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QGridLayout()
      #  mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.udpAlertBox)
        mainLayout.addWidget(buttonBox)
  
        self.setLayout(mainLayout)
        self.setWindowTitle("Configurar notificaciones")
         
    def actualizarTarget(self):
        
        config=self.getConfigFromDialog()
        self.guardarConfig()
        
        print (config)
        
        self.notiTargetUpdate.emit(config)
        self.accept()
        
         
    def tryLoadConfig(self):
        
        config={}
        try:
            configLoaded=json.load(open("notificationTarget.json"))
            
            if "target" in configLoaded and "port" in configLoaded:
                config['target']=configLoaded['target'].strip()
                config['port']=configLoaded['port']
            
                return config
                
        except Exception as e:
            pass
        config['target']="localhost"
        config['port']=23344
        return config
            

    
    def createUdpAlertBox(self):
        
        config = self.tryLoadConfig()
        self.udpAlertBox = QtWidgets.QGroupBox("Fuente de notificaciones")
    
        self.udpalertip = QtWidgets.QLineEdit(self)
        self.udpalertip.setText(config['target'])
     
        udpPortValidator=QtGui.QIntValidator()
        udpPortValidator.setBottom(1)
        udpPortValidator.setTop(65355)
        self.udpPort = QtWidgets.QLineEdit(self)
        self.udpPort.setValidator(udpPortValidator)
        self.udpPort.setText(str(config['port']))

        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("ip:"),self.udpalertip)
        layout.addRow(QtWidgets.QLabel("puerto"), self.udpPort)      
      
        self.udpAlertBox.setLayout(layout)
    
    def getConfigFromDialog(self):
        
        config ={}
    
        textIp=self.udpalertip.text().strip(" ")
        textPuerto=self.udpPort.text()
           
        if len(textPuerto)>0:
            p=int(textPuerto)
            if p>0:
                config['port']=p
            else:
                print("Error parsing port")
            
        if len(textIp)>0:     
            config['target']=textIp             
              
        if len(config.keys())==0:
            return None     
        return config
  
    def guardarConfig(self):
      
        config=self.getConfigFromDialog()
       
        if config!=None:
            filePath = "notificationTarget.json"
            
            if len(filePath[0])>0:
                configString = json.dumps(config,indent=2, sort_keys=True)
                        
                archivo = open(filePath,"w+")        
                archivo.write(configString)                       
                archivo.close()      
           
    
        
#if __name__ == '__main__':

    #import sys

    #app = QtWidgets.QApplication(sys.argv)
    #dialog = NotificationConfigDialog()
    #sys.exit(dialog.exec_())
