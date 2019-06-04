from PySide2 import QtCore, QtGui, QtWidgets
import socket
import re
import json

class ConfigurationDialog(QtWidgets.QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self):
        super(ConfigurationDialog, self).__init__()

        self.createMenu()    
        self.createSerialPortBox()
        self.createSureLinkBox()
        self.createApnBox()
        self.createAutoResetBox()
        self.createNetModeBox()
        self.createLastgaspBox()
        self.createUdpAlertBox()
        self.createPingPeriodicoBox()
        self.createBandsBox()
        self.createWhiteListIpBox()      
        

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.apnbox,0,0)
        mainLayout.addWidget(self.autoresetbox,0,1)
        mainLayout.addWidget(self.serialPortBox,1,0)
        mainLayout.addWidget(self.surelinkBox,1,1)
      
        mainLayout.addWidget(self.netModeBox)
        mainLayout.addWidget(self.lastgaspbox)
        mainLayout.addWidget(self.bandsbox)
       
        mainLayout.addWidget(self.utepingbox)
        mainLayout.addWidget(self.udpAlertBox)
        mainLayout.addWidget(self.ipfilterBox)
  
        self.setLayout(mainLayout)
        self.setWindowTitle("Configuración de dispositivos")
         
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

   
    def createSerialPortBox(self):
        self.serialPortBox = QtWidgets.QGroupBox("Serial port")

        self.baudRateCombo=QtWidgets.QComboBox()
        self.baudRateCombo.addItems(["110","300","600","1200","2400","4800","9600","14400","19200","38400","57600","115200"])
        self.baudRateCombo.setCurrentIndex(6)
        
        self.databitsCombo=QtWidgets.QComboBox() 
        self.databitsCombo.addItems(["5","6","7","8"])
        self.databitsCombo.setCurrentIndex(3)
        
        self.stopCombo=QtWidgets.QComboBox() 
        self.stopCombo.addItems(["1","2"])
        self.stopCombo.setCurrentIndex(0)
        
        self.parityCombo=QtWidgets.QComboBox() 
        self.parityCombo.addItems(["none","even","odd","force0","force1"])
        self.parityCombo.setCurrentIndex(0)
        
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Baud rate:"),self.baudRateCombo)
        layout.addRow(QtWidgets.QLabel("Data bits"), self.databitsCombo)
        layout.addRow(QtWidgets.QLabel("Parity"), self.parityCombo)
        layout.addRow(QtWidgets.QLabel("Stop bits"), self.stopCombo)
      
        self.serialPortBox.setLayout(layout)
        self.serialPortBox.setCheckable(True)
        self.serialPortBox.setChecked(False)
     
    def getSureLinkData(self): 
        
      
        try:
            data={}
            data['surelink default ip']=self.suredefIp.text()
            data['surelink backup ip']=self.surebackIp.text()
            data['surelink interval']=int(self.sureinter.text())
            data['surelink retries']=int(self.sureret.text())
            return data
        except Exception as e:
            return None
 
    def createSureLinkBox(self):
        self.surelinkBox = QtWidgets.QGroupBox("Surelink")
        self.surelinkBox.setCheckable(True)
        self.surelinkBox.setChecked(False)
        
        ipRange = "([1-9][0-9]|[0-9]|2[0-4][0-9]|25[0-5]|1[0-9][0-9])";
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$");
        rx = QtCore.QRegExp(ipRegex)
        validator =  QtGui.QRegExpValidator(rx)
        
        self.suredefIp = QtWidgets.QLineEdit(self)
        self.suredefIp.setValidator(validator)
        self.suredefIp.setText("0.0.0.0")

        self.surebackIp = QtWidgets.QLineEdit(self)
        self.surebackIp.setValidator(validator)
        self.surebackIp.setText("0.0.0.0")

        self.sureintervalValidator=QtGui.QIntValidator()
        self.sureintervalValidator.setBottom(3)
        self.sureintervalValidator.setTop(600)
        self.sureinter = QtWidgets.QLineEdit(self)
        self.sureinter.setValidator(self.sureintervalValidator)
        self.sureinter.setText("10")
        
           
        self.sureretValidator=QtGui.QIntValidator()
        self.sureretValidator.setBottom(1)
        self.sureretValidator.setTop(10)
        self.sureret = QtWidgets.QLineEdit(self)
        self.sureret.setValidator(self.sureintervalValidator)
        self.sureret.setText("3")
        
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("default ip:"),self.suredefIp)
        layout.addRow(QtWidgets.QLabel("backup ip"), self.surebackIp)
        layout.addRow(QtWidgets.QLabel("intervalo (minutos)"), self.sureinter)
        layout.addRow(QtWidgets.QLabel("reintentos"), self.sureret)
      
        self.surelinkBox.setLayout(layout)
     
    def createUdpAlertBox(self):
        self.udpAlertBox = QtWidgets.QGroupBox("Alertas Udp")
        self.udpAlertBox.setCheckable(True)
        self.udpAlertBox.setChecked(False)
        
        ipRange = "([1-9][0-9]|[0-9]|2[0-4][0-9]|25[0-5]|1[0-9][0-9])";
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$");
        rx = QtCore.QRegExp(ipRegex)
        validator =  QtGui.QRegExpValidator(rx)
        
        self.udpalertip = QtWidgets.QLineEdit(self)
        self.udpalertip.setValidator(validator)
        self.udpalertip.setText("0.0.0.0")
     
        udpPortValidator=QtGui.QIntValidator()
        udpPortValidator.setBottom(1)
        udpPortValidator.setTop(65355)
        self.udpPort = QtWidgets.QLineEdit(self)
        self.udpPort.setValidator(udpPortValidator)
        self.udpPort.setText("12345")
   
        udpIntervalVali=QtGui.QIntValidator()
        udpIntervalVali.setBottom(1)
        udpIntervalVali.setTop(10)
        self.udpInterval = QtWidgets.QLineEdit(self)
        self.udpInterval.setValidator(udpIntervalVali)
        self.udpInterval.setText("3")

        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("ip:"),self.udpalertip)
        layout.addRow(QtWidgets.QLabel("puerto"), self.udpPort)      
        layout.addRow(QtWidgets.QLabel("intervalo (minutos)"), self.udpInterval)
      
        self.udpAlertBox.setLayout(layout)
    
    def createPingPeriodicoBox(self):
        self.utepingbox = QtWidgets.QGroupBox("Ping periodico")
        self.utepingbox.setCheckable(True)
        self.utepingbox.setChecked(False)
        
        ipRange = "([1-9][0-9]|[0-9]|2[0-4][0-9]|25[0-5]|1[0-9][0-9])";
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$");
        rx = QtCore.QRegExp(ipRegex)
        validator =  QtGui.QRegExpValidator(rx)
        
        self.utepingip = QtWidgets.QLineEdit(self)
        self.utepingip.setValidator(validator)
        self.utepingip.setText("0.0.0.0")
     
        utepingvali=QtGui.QIntValidator()
        utepingvali.setBottom(1)
        utepingvali.setTop(600)
        self.utepinginter = QtWidgets.QLineEdit(self)
        self.utepinginter.setValidator(utepingvali)
        self.utepinginter.setText("3")

        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("ip:"),self.utepingip)
        layout.addRow(QtWidgets.QLabel("intervalo (minutos)"), self.utepinginter)
      
        self.utepingbox.setLayout(layout)
      
   
    def createApnBox(self):
        self.apnbox = QtWidgets.QGroupBox("Apn")
        self.apnbox.setCheckable(True)
        self.apnbox.setChecked(False)
        
        self.apn = QtWidgets.QLineEdit(self)
        self.apn.setText("comstc01.vpnantel")

        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("apn"),self.apn)
      
        self.apnbox.setLayout(layout)

    def createAutoResetBox(self):
        self.autoresetbox = QtWidgets.QGroupBox("AutoReset")
        self.autoresetbox.setCheckable(True)
        self.autoresetbox.setChecked(False)
        
        self.autoreset = QtWidgets.QLineEdit(self)
        self.autoreset.setText("720")
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("autoreset (minutos)"),self.autoreset)
      
        self.autoresetbox.setLayout(layout)
        
    def createLastgaspBox(self):
        self.lastgaspbox = QtWidgets.QGroupBox("Last gasp")
        self.lastgaspbox.setCheckable(True)
        self.lastgaspbox.setChecked(False)
        
        self.lastgasp = QtWidgets.QLineEdit(self)
        self.lastgasp.setText("1990")
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("lastgasp numero sms"),self.lastgasp)
      
        self.lastgaspbox.setLayout(layout)
    
    def createBandsBox(self):
        self.bandsbox = QtWidgets.QGroupBox("Bandas")
        self.bandsbox.setCheckable(True)
        self.bandsbox.setChecked(False)
        
        self.band850=QtWidgets.QCheckBox(self)
        self.band850.setChecked(True)
        self.band900=QtWidgets.QCheckBox(self)
        self.band900.setChecked(True)
        self.band1800=QtWidgets.QCheckBox(self)
        self.band1800.setChecked(True)        
        self.band2100=QtWidgets.QCheckBox(self)
        self.band2100.setChecked(True)
        
        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel("850:"),0,0)
        layout.addWidget(self.band850,0,1)
       
        
        layout.addWidget(QtWidgets.QLabel("900:"),0,2)
        layout.addWidget(self.band900,0,3)
        
        layout.addWidget(QtWidgets.QLabel("1800:"),1,0) 
        layout.addWidget(self.band1800  ,1,1) 
        
        layout.addWidget(QtWidgets.QLabel("2100:"),1,2) 
        layout.addWidget(self.band2100  ,1,3) 
       
        self.bandsbox.setLayout(layout)
            
    def createNetModeBox(self):
        self.netModeBox = QtWidgets.QGroupBox("Red")
        self.netModeBox.setCheckable(True)
        self.netModeBox.setChecked(False)
        
        self.netmode=QtWidgets.QComboBox()
        self.netmode.addItems(["dualmode(umts)","umts","gsm","dualmode(gsm)"])
        self.netmode.setCurrentIndex(0)
       
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Modo de red"),self.netmode)
      
        self.netModeBox.setLayout(layout)


    def createWhiteListIpBox(self):
            
        self.ipfilterBox = QtWidgets.QGroupBox("Filtro Ip (telnet)")
        self.ipfilterBox.setCheckable(True)
        self.ipfilterBox.setChecked(False)
        
        ipRange = "([1-9][0-9]|[0-9]|2[0-4][0-9]|25[0-5]|1[0-9][0-9]|x|xx|xxx|n|nn|nnn)";
        ipRegex = QtCore.QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$");
        rx = QtCore.QRegExp(ipRegex)
        validator =  QtGui.QRegExpValidator(rx)
        
        self.wl1 = QtWidgets.QLineEdit(self)
        self.wl1.setValidator(validator)
        self.wl1.setText("x.x.x.x")
        
        self.wl2 = QtWidgets.QLineEdit(self)
        self.wl2.setValidator(validator)
        self.wl2.setText("x.x.x.x")
        
        self.wl3 = QtWidgets.QLineEdit(self)
        self.wl3.setValidator(validator)
        self.wl3.setText("x.x.x.x")
     

        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("whitelist 1:"),self.wl1)
        layout.addRow(QtWidgets.QLabel("whitelist 2:"),self.wl2)
        layout.addRow(QtWidgets.QLabel("whitelist 3:"),self.wl3)
      
        self.ipfilterBox.setLayout(layout)
      
      
      
    def createFormGroupBox(self):
        self.formGroupBox = QtWidgets.QGroupBox("Form layout")
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Line 1:"), QtWidgets.QLineEdit())
        layout.addRow(QtWidgets.QLabel("Line 2, long text:"), QtWidgets.QComboBox())
        layout.addRow(QtWidgets.QLabel("Line 3:"), QtWidgets.QSpinBox())
        self.formGroupBox.setLayout(layout)

    
    def getConfigFromDialog(self):
        
        config ={}
        if self.apnbox.isChecked():
            apntext=self.apn.text().strip()
            if len(apntext)>0:
                config['apn']=apntext
        
        if self.serialPortBox.isChecked():            
            config['serialport baudrate']=int( self.baudRateCombo.currentText()  )
            config['serialport databits']=int( self.databitsCombo.currentText()  )
            config['serialport parity']= self.parityCombo.currentText()  
            config['serialport stop']=int( self.stopCombo.currentText()  )
        
        if self.netModeBox.isChecked():
            config['netmode']=self.netmode.currentText()
        
        if self.bandsbox.isChecked():
            
            bands=None
            if self.band900.isChecked():
                if bands==None:
                    bands="900"
                else:
                    bands+=",900"
            
            if self.band850.isChecked():
                if bands==None:
                    bands="850"
                else:
                    bands+=",850"
            
            if self.band1800.isChecked():
                if bands==None:
                    bands="1800"
                else:
                    bands+=",1800"
           
            if self.band2100.isChecked():
                if bands==None:
                    bands="2100"
                else:
                    bands+=",2100"
            
            if bands!=None:
                config['bandas']=bands
            
        if self.udpAlertBox.isChecked():
            
            textIp=self.udpalertip.text()
            textPuerto=self.udpPort.text()
            textInt=self.udpInterval.text()
            
            if len(textInt)>0:
                inter=int(textInt)
                if inter>0:
                    config['keep alive interval']=inter
                else:
                    print("Error parsing intevalo")
            
            if len(textPuerto)>0:
                p=int(textPuerto)
                if p>0:
                    config['keep alive port']=p
                else:
                    print("Error parsing Alertas udp port")
                
            if len(textIp)>0:        
                try:
                    socket.inet_aton(textIp)                    
                    config['keep alive ip']=textIp                  
                    # legal
                except socket.error:
                    print("Error parsing Alertas udp ip")
            
        if self.autoresetbox.isChecked():
            text = self.autoreset.text()
            if len(text)>0:
                if int(text)>15:
                    config['programed reset minutes']=int(text)
            else:
                print("Error parsing AutoReset")
                
        if self.surelinkBox.isChecked():
            
            ip=self.suredefIp.text()
            backip=self.surebackIp.text()
            inte=self.sureinter.text()
            ret=self.sureret.text()
            
            if len(ip)>0:
                try:
                    socket.inet_aton(ip)                    
                    config['surelink default ip']=ip                  
                except socket.error:
                    print("Error parsing Surelink default ip")
            
            if len(backip)>0:
                try:
                    socket.inet_aton(backip)                    
                    config['surelink backup ip']=ip                  
                except socket.error:
                    print("Error parsing Surelink backup ip")
            
            if len(inte)>0:
                if int(inte)>0:
                    config['surelink period']=int(inte) 
            else:
                print("Error parsing surelink intervalo")
            
            if len(ret)>0:
                if int(ret)>0:
                    config['surelink retries']=int(inte) 
            else:
                print("Error parsing surelink reintentos")
                
        if self.lastgaspbox.isChecked():
            text=self.lastgasp.text()
            if len(text)>0:
                config['lastgasp number']=text  
            else:
                print("Error parsing lastgasp")
                
        if self.utepingbox.isChecked():
            ip=self.utepingip.text()
            inter=self.utepinginter.text()
            
            if len(ip)>0:
                try:
                    socket.inet_aton(ip)                    
                    config['uteping ip']=ip                  
                except socket.error:
                    print("Error parsing Ping Periodico ip")
            
            if len(inter)>0:
                if int(inter)>0:
                    config['uteping interval minutes']=int(inter) 
            else:
                print("Error parsing Ping Periodico intervalo")
            
        if self.ipfilterBox.isChecked():
            
            ipRange = "([1-9][0-9]|[0-9]|2[0-4][0-9]|25[0-5]|1[0-9][0-9]|x|xx|xxx|n|nn|nnn)";
            ipRegex = "^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$"
       
            pattern = re.compile(ipRegex)

            wl1=self.wl1.text()
            wl2=self.wl2.text()
            wl3=self.wl3.text()
            
            if pattern.match(wl1):
                config['whitelist 1']=wl1
            else:
                print("Error parsing Filtro ip 1")
            
            if pattern.match(wl2):
                config['whitelist 2']=wl2
            else:
                print("Error parsing Filtro ip 2")
            
            if pattern.match(wl3):
                config['whitelist 3']=wl3
            else:
                print("Error parsing Filtro ip 3")
   
        if len(config.keys())==0:
            return None     
        return config
  
    def guardarConfig(self):
      
        config=self.getConfigFromDialog()
       
        if config!=None:
            filePath = QtWidgets.QFileDialog.getSaveFileName(self, "Guardar como",
                    QtCore.QDir.currentPath(),"Config file (*.json)")
            
            if len(filePath[0])>0:
                configString = json.dumps(config,indent=2, sort_keys=True)
                        
                archivo = open(filePath[0],"w+")        
                archivo.write(configString)                       
                archivo.close()   
        else:
          
            QtWidgets.QMessageBox.information(self,"Error", "Configuracion vacia")
           
           
    
    def cargarConfig(self):
        
        filePath = QtWidgets.QFileDialog.getOpenFileName(self, "Cargar",
                QtCore.QDir.currentPath(),"Config file (*.json)")

        if len(filePath[0])>0:
            
            try:
                loadedConfig=json.load(open(filePath[0]))
                print (loadedConfig)            
                self.actualizarDialogFromConfig(loadedConfig)            
            except Exception as e:
                print("No se pudo parsear configuracion")            
                print(e)
            
    
    def actualizarDialogFromConfig(self,jsonConfig): 
        
        self.apnbox.setChecked(False)
        self.bandsbox.setChecked(False)
        self.ipfilterBox.setChecked(False)
        self.lastgaspbox.setChecked(False)
        self.netModeBox.setChecked(False)
        self.surelinkBox.setChecked(False)
        self.udpAlertBox.setChecked(False)
        self.utepingbox.setChecked(False)  
        self.serialPortBox.setChecked(False)
        self.autoresetbox.setChecked(False)

        #TODO carga de configuracion
        if "apn" in jsonConfig:
            self.apnbox.setChecked(True)
            self.apn.setText(jsonConfig['apn'])  
         
   
        if "serialport baudrate" in jsonConfig:
            self.serialPortBox.setChecked(True)
            index=self.baudRateCombo.findText(str(jsonConfig['serialport baudrate']))
            if index!=-1:
                self.baudRateCombo.setCurrentIndex(index)
            else:
                print("Error parsing SerialPort baudrate")
        
        if "serialport databits" in jsonConfig:
            self.serialPortBox.setChecked(True)
            index=self.databitsCombo.findText(str(jsonConfig['serialport databits']))
            if index!=-1:
                self.databitsCombo.setCurrentIndex(index)
            else:
                print("Error parsing SerialPort databits")
        
        if "serialport parity" in jsonConfig:
            self.serialPortBox.setChecked(True)
            index=self.parityCombo.findText(jsonConfig['serialport parity'])
            if index!=-1:
                self.parityCombo.setCurrentIndex(index)
            else:
                print("Error parsing SerialPort parity")
        
        if "serialport stop" in jsonConfig:
            self.serialPortBox.setChecked(True)
            index=self.stopCombo.findText(str(jsonConfig['serialport stop']))
            if index!=-1:
                self.stopCombo.setCurrentIndex(index)
            else:
                print("Error parsing SerialPort stop")
        
        
        if "netmode" in jsonConfig:
            
            index=self.netmode.findText(jsonConfig["netmode"])
            if index>=0:
                self.netmode.setCurrentIndex(index)
                self.netModeBox.setChecked(True)
        
        
        if "bandas" in jsonConfig:
            
            bandas=jsonConfig["bandas"].split(",")  
            self.band900.setChecked(False)
            self.band850.setChecked(False)
            self.band1800.setChecked(False)
            self.band2100.setChecked(False)
            
            for x in bandas:
                if x =="900":
                    self.band900.setChecked(True)
                    self.bandsbox.setChecked(True)
                elif x =="850":
                    self.band850.setChecked(True)
                    self.bandsbox.setChecked(True)
                elif x =="1800":
                    self.band1800.setChecked(True)
                    self.bandsbox.setChecked(True)
                elif x =="2100":
                    self.band2100.setChecked(True)
                    self.bandsbox.setChecked(True)
                    
        if ('keep alive interval' in jsonConfig) and ('keep alive ip' in jsonConfig) and ('keep alive port' in jsonConfig):
             
            self.udpAlertBox.setChecked(True)
            self.udpalertip.setText(jsonConfig['keep alive ip'])
            self.udpPort.setText(str(jsonConfig['keep alive port']))
            self.udpInterval.setText(str(jsonConfig['keep alive interval']))
            
        if 'programed reset minutes' in jsonConfig:
            self.autoresetbox.setChecked(True)
            self.autoreset.setText(str(jsonConfig['programed reset minutes']))
         
         
        if ('surelink default ip' in jsonConfig) and ( 'surelink backup ip' in jsonConfig ) and ('surelink period' in jsonConfig) and ('surelink retries' in jsonConfig ):    
            self.surelinkBox.setChecked(True)            
            self.suredefIp.setText(jsonConfig['surelink default ip'])
            self.surebackIp.setText(jsonConfig['surelink backup ip'])
            self.sureinter.setText(str(jsonConfig['surelink period']))
            self.sureret.setText(str(jsonConfig['surelink retries']))
        
        if 'lastgasp number' in jsonConfig:
                 
            self.lastgaspbox.setChecked(True)
            self.lastgasp.setText(jsonConfig['lastgasp number'])
         
        if ('uteping ip' in jsonConfig) and( 'uteping interval minutes' in jsonConfig) :
            
            self.utepingbox.setChecked(True)
            self.utepingip.setText(jsonConfig['uteping ip'])
            self.utepinginter.setText(str(jsonConfig['uteping interval minutes']))
         
        if ('whitelist 1' in jsonConfig) and ('whitelist 2' in jsonConfig) and ('whitelist 3' in jsonConfig):   
            
            self.ipfilterBox.setChecked(True)
            self.wl1.setText(jsonConfig['whitelist 1'])
            self.wl2.setText(jsonConfig['whitelist 2'])
            self.wl3.setText(jsonConfig['whitelist 3'])
            
    
#if __name__ == '__main__':

#    import sys

#    app = QtWidgets.QApplication(sys.argv)
#    dialog = Dialog()
#    sys.exit(dialog.exec_())
