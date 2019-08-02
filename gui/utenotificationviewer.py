from PySide2 import QtCore, QtGui, QtWidgets
import datetime
import json
from driver.utenotificationclient import UteNotificationClient 
from gui.notificationTargetConfig import NotificationConfigDialog

class HistoryRequestDialog(QtWidgets.QDialog):
   
   
    historyDoRequest=QtCore.Signal(dict)
    
    def __init__(self):
        super(HistoryRequestDialog, self).__init__()

        self.createView()
        
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

       # buttonBox.accepted.connect(self.accept)
        buttonBox.accepted.connect(self.doRequest)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QGridLayout()
      #  mainLayout.setMenuBar(self.menuBar)
        mainLayout.addWidget(self.udpAlertBox)
        mainLayout.addWidget(buttonBox)
  
        self.setLayout(mainLayout)
        self.setWindowTitle("Configurar notificaciones")
         
    def doRequest(self):
        
        config=self.getRequestFromDialog()
        print (config)
        self.historyDoRequest.emit(config)
       # self.accept()
        
    
    
    def createView(self):
        
        self.udpAlertBox = QtWidgets.QGroupBox("Fuente de notificaciones")
        self.udpalertip = QtWidgets.QLineEdit(self)
        
        
        self.dateEditInicio = QtWidgets.QDateEdit(datetime.datetime.now())
        self.dateEditInicio.setCalendarPopup(True)
        self.dateEditInicio.calendarWidget().installEventFilter(self)
        
        self.dateEditFin = QtWidgets.QDateEdit(datetime.datetime.now())
        self.dateEditFin.setCalendarPopup(True)
        self.dateEditFin.calendarWidget().installEventFilter(self)
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("ip:"),self.udpalertip)
        layout.addRow(QtWidgets.QLabel("desde:"),self.dateEditInicio)
        layout.addRow(QtWidgets.QLabel("hasta:"),self.dateEditFin)

      
        self.udpAlertBox.setLayout(layout)
    
    def getRequestFromDialog(self):
        
        config ={}
    
        textIp=self.udpalertip.text().strip(" ")
        textInicio=self.dateEditInicio.dateTime().toPython()
        textFin=self.dateEditFin.dateTime().toPython()
        
        if len(textIp)>0:     
            config['target']=textIp    
            config['inicio']=textInicio
            config['fin']=textFin
              
        if len(config.keys())==3:
            return config     
        
        return None
  
  
    


class NotificationMainWindow(QtWidgets.QMainWindow):
    

    def __init__(self):
        super(NotificationMainWindow, self).__init__()

        mainLayout = QtWidgets.QVBoxLayout()
        
        self.createNotificationBox() 
        
       # mainLayout.addWidget(self.horizontalGroupBox)
       # self.setLayout(self.listLayout)
        self.setWindowTitle("Notificaciones")
        self.setWindowIcon(QtGui.QIcon('./gui/imagenes/notifications.png'))

        wit=QtWidgets.QWidget()
        wit.setLayout(self.mainLayout)
        self.setCentralWidget(wit)
                #self.setLayout(mainLayout)

        self.createActions()
        #por ahora no hay nada en el menu
       # self.createMenus()
        self.createToolBars()
        self.createStatusBar()

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.createNotificationClient()
        self.noti=NotificationConfigDialog()
        config=self.noti.tryLoadConfig()
        self.notiClient.updateTarget(config['target'], config['port'])
        
        
        self.noti.notiTargetUpdate.connect(self.updateSource)
        
        self.count=0


    def updateSource(self,source):
        
        self.notiClient.updateTarget(source['target'], source['port'])
        
        
    def createActions(self):
        
        self.nconfig = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/connection.png'), "&Actualizar fuente",
                self,statusTip="Actualizar fuente", triggered=self.showNotificationConfig)
        
        self.nfilter = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/filter.png'), "&Filtrar notificaciones",
                self,statusTip="Filtrar notificaciones", triggered=self.showFilter)
        
        self.nCleanList = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/clean.png'), "&Limpiar lista",
                self,statusTip="Limpiar lista", triggered=self.cleanList)
        
        self.nHistory = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/history.png'), "&Consultar historial",
                self,statusTip="Consultar historial", triggered=self.showHistory)
       
    def showHistory(self):
        
        print("showing history request config")
        if self.requestBox.isVisible():
            self.requestBox.hide()
        else:
            self.requestBox.show()
        
    def createNotificationClient(self):
        
        self.notiClient=UteNotificationClient()
        self.notiClient.ss.notifyRx.connect(self.appendNotification)
        self.notiClient.ss.updateSB.connect(self.updateStatusBar)
        self.notiClient.ss.updateSBIcon.connect(self.setHookIndication)

    


    def updateStatusBar(self,msg):
        self.statusBar().showMessage(msg)
        

    def showNotificationConfig(self):
        
        self.noti.show()
      
    def cleanList(self):
        
        self.pendingModel.removeRows(0,self.pendingModel.rowCount())
        self.informationLabel.setText("")

        self.count=0
        self.notificationCountLabel.setText("Cantidad :"+str(self.count))

            
    def showFilter(self):
        
        if self.filterBox.isHidden():
            self.filterBox.show()
            
            self.nfilter.setIcon(QtGui.QIcon('./gui/imagenes/filter.png'))
            self.filterRegExpChanged()
        else:
            self.filterBox.hide()
            self.nfilter.setIcon(QtGui.QIcon('./gui/imagenes/filter.png'))
            #desactivar filtrado
            syntax = QtCore.QRegExp.PatternSyntax(0)
            regExp = QtCore.QRegExp("", QtCore.Qt.CaseInsensitive, syntax)
            self.pendingModelFiltered.setFilterRegExp(regExp)

    def handlePendingPopMenu(self,pos):

        rowIndex=self.listPending.indexAt(pos)
        
        menu = QtWidgets.QMenu() 
        action = QtWidgets.QAction("Delete", self)       
        action.triggered.connect(lambda : self.cancelarPendingRow(rowIndex.row()))
        menu.addAction(action)
        menu.exec_(QtGui.QCursor.pos())
        
    
    def createNotificationBox(self):
        
         #self.horizontalGroupBox = QtWidgets.QGroupBox("Horizontal layout")
        self.mainLayout = QtWidgets.QHBoxLayout()
        
        self.listPending = QtWidgets.QTreeView()
        self.listPending.setRootIsDecorated(False)
        self.listPending.setAlternatingRowColors(True)          
        self.listPending.setSortingEnabled(True)
        
        self.pendingBox = QtWidgets.QGroupBox("Notificaciones")
        layp = QtWidgets.QVBoxLayout()
        layp.addWidget(self.listPending)
        
        
        self.notificationCountLabel=QtWidgets.QLabel("Cantidad: 0")
        layp.addWidget(self.notificationCountLabel)
        self.pendingBox.setLayout(layp)
        
        ####
        self.pendingModel = QtGui.QStandardItemModel(0, 4, self)
        self.pendingModel.setHeaderData(0, QtCore.Qt.Horizontal, "IP")
        self.pendingModel.setHeaderData(1, QtCore.Qt.Horizontal, "Fecha")
        self.pendingModel.setHeaderData(2, QtCore.Qt.Horizontal, "Tipo")
        self.pendingModel.setHeaderData(3, QtCore.Qt.Horizontal, "Texto")
        
        self.pendingModelFiltered = QtCore.QSortFilterProxyModel()
        self.pendingModelFiltered.setDynamicSortFilter(True)
        self.pendingModelFiltered.setSourceModel(self.pendingModel)
        self.listPending.setModel(self.pendingModelFiltered)        
        
       # self.listPending.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        #self.listPending.customContextMenuRequested.connect(self.handlePendingPopMenu)
         
        self.listPending.selectionModel().selectionChanged.connect(self.selectChanged)
        #####
        self.listPending.setColumnHidden(3,True)

        self.informationLabel= QtWidgets.QTextEdit()
        self.informationLabel.setPlainText("")
        self.informationLabel.setReadOnly(True)
        self.informationLabel.setFontPointSize(10)
        
        self.informationBox = QtWidgets.QGroupBox("Información")
        layI = QtWidgets.QVBoxLayout()
        layI.addWidget(self.informationLabel)
        self.informationBox.setLayout(layI)
        
        
        
        self.filterBox = QtWidgets.QGroupBox("filtro")
        self.filterPatternLineEdit = QtWidgets.QLineEdit()
        self.filterColumnComboBox = QtWidgets.QComboBox()
        self.filterColumnComboBox.addItem("IP")
        self.filterColumnComboBox.addItem("Fecha")
        self.filterColumnComboBox.addItem("Tipo")

        self.filterPatternLineEdit.textChanged.connect(self.filterRegExpChanged)
        self.filterColumnComboBox.currentIndexChanged.connect(self.filterColumnChanged)

        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("patron:"),self.filterPatternLineEdit)
        layout.addRow(QtWidgets.QLabel("columna"), self.filterColumnComboBox)   
        
        self.filterBox.setLayout(layout)
        
       
        
        
        self.requestBox = QtWidgets.QGroupBox("Historial")
        
        self.requestIp = QtWidgets.QLineEdit(self)
        
        self.dateEditInicio = QtWidgets.QDateEdit(datetime.datetime.now())
        self.dateEditInicio.setCalendarPopup(True)
        self.dateEditInicio.calendarWidget().installEventFilter(self)
        
        self.dateEditFin = QtWidgets.QDateEdit(datetime.datetime.now())
        self.dateEditFin.setCalendarPopup(True)
        self.dateEditFin.calendarWidget().installEventFilter(self)
        
        self.doRequestButton = QtWidgets.QPushButton("Consultar")
        
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("ip:"),self.requestIp)
        layout.addRow(QtWidgets.QLabel("desde:"),self.dateEditInicio)
        layout.addRow(QtWidgets.QLabel("hasta:"),self.dateEditFin)
        layout.addRow(self.doRequestButton)

        self.requestBox.setLayout(layout)
        
        layI.addWidget(self.requestBox)
        layI.addWidget(self.filterBox)
        
        self.mainLayout.addWidget(self.pendingBox)
        self.mainLayout.addWidget(self.informationBox)
        
        self.filterBox.hide()
        self.requestBox.hide()
      
        self.doRequestButton.released.connect(self.handleRequest)
     
    def getRequestFromDialog(self):
        
        config ={}
    
        textIp=self.requestIp.text().strip(" ")
        textInicio=self.dateEditInicio.dateTime().toPython().strftime("%Y-%m-%d %H:%M:%S")
        textFin=self.dateEditFin.dateTime().toPython().strftime("%Y-%m-%d %H:%M:%S")

        if len(textIp)>0:     
            config['target']=textIp    
            config['inicio']=textInicio
            config['fin']=textFin
              
        if len(config.keys())==3:
            return config     
        
        return None
   
    def handleRequest(self):
        
        request=self.getRequestFromDialog()
        
        if request==None:
            self.statusBar().showMessage("Consulta incorrecta, ingrese ip o *")
        else:
            self.notiClient.appendRequest(request)
        print(request)
        
    def filterRegExpChanged(self): 
        
        syntax = QtCore.QRegExp.PatternSyntax(0)
        regExp = QtCore.QRegExp(self.filterPatternLineEdit.text(), QtCore.Qt.CaseInsensitive, syntax)
        self.pendingModelFiltered.setFilterRegExp(regExp)
        
    def filterColumnChanged(self):
        
        self.pendingModelFiltered.setFilterKeyColumn(self.filterColumnComboBox.currentIndex())

    
    def pretifyJson(self,jsonStr):
        
        pretyJson=""
        try:
            parsedJson=json.loads(jsonStr)
        
            pretyJson+="<html>"
            for x in parsedJson:
                pretyJson+="<b>"+x +" : </b>"
                pretyJson+=str(parsedJson[x])+"<br>" 
                
            pretyJson+="</html>"
        except Exception as e:
            pretyJson=jsonStr
        
        return pretyJson
    
    def selectChanged(self, selected,deselected):
        
        indexes=selected.indexes()
        if len(indexes)>0:
            index=indexes[0].row()
            sourceIndex=self.pendingModelFiltered.mapToSource(indexes[0])
            sourceIndex=sourceIndex.row()
            msg=self.pendingModel.item(sourceIndex, 3).text()        
            self.informationLabel.setText(self.pretifyJson(msg))
            
    def closeEvent(self, event):
        
        event.accept()

    
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
       # self.fileMenu.addAction(self.cconfig)
      #  self.fileMenu.addAction(self.coperation)
       
       # self.fileMenu.addAction(self.saveAsAct)
      #  self.fileMenu.addSeparator()
       # self.fileMenu.addAction(self.exitAct)

      #  self.editMenu = self.menuBar().addMenu("&Otros")
      
      #  self.editMenu.addAction(self.cutAct)
      #  self.editMenu.addAction(self.copyAct)
      #  self.editMenu.addAction(self.pasteAct)

      #  self.menuBar().addSeparator()

      #  self.helpMenu = self.menuBar().addMenu("&Help")
       # self.helpMenu.addAction(self.aboutAct)
       # self.helpMenu.addAction(self.aboutQtAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("Configuration")
        self.fileToolBar.addAction(self.nconfig)
        self.fileToolBar.addAction(self.nfilter)
        self.fileToolBar.addAction(self.nCleanList)
        self.fileToolBar.addAction(self.nHistory)
        
       # self.editToolBar = self.addToolBar("Operative")
      #  self.editToolBar.addAction(self.operationPlay)
      #  self.editToolBar.addAction(self.operationPause)
      #  self.editToolBar.addAction(self.operationCancel)
      #  self.editToolBar.addAction(self.cutAct)
      #  self.editToolBar.addAction(self.copyAct)
       # self.editToolBar.addAction(self.pasteAct)

    def setHookIndication(self,state):
        if state:
            self.hookIndication.setIcon(QtGui.QIcon('./gui/imagenes/plugged.png'))
        else:
            self.hookIndication.setIcon(QtGui.QIcon('./gui/imagenes/unplugged.png'))

    def createStatusBar(self):
        
        self.statusBar().showMessage("Conectando con fuente de notificaciones")
        
        self.hookIndication=QtWidgets.QPushButton(icon=QtGui.QIcon('./gui/imagenes/unplugged.png'))
       # self.hookIndication.setEnabled(False)
        self.hookIndication.setFlat(True)
        self.statusBar().addPermanentWidget(self.hookIndication)
        
    def fixFechaFormat(self,toFix):
        if toFix!=None:
            pedazos=toFix.split(" ")
            pf=pedazos[0].split("-")
            ph=pedazos[1].split(":")
            
            newStringDate="%s-%02d-%02d %02d:%02d:%02d"%(pf[0],int(pf[1]),int(pf[2]),int(ph[0]),int(ph[1]),int(ph[2]))
            
            return newStringDate
           
        return toFix
    
    @QtCore.Slot(dict)
    def appendNotification(self,notiGroup):
        
   #     print("Apending Notification")   
   #     print(noti)
       
        print("appending "+str(len(notiGroup))+ " notifications")
        for noti in notiGroup:
            ip=noti['ip']
            fecha=noti['fecha']
            fecha=self.fixFechaFormat(fecha)
            
            tipo="notificación"
            if "alert" in noti:
                tipo="alerta"
            text = json.dumps(noti,indent=2, sort_keys=True)
            
           
            
            
            self.pendingModel.appendRow([QtGui.QStandardItem(ip),QtGui.QStandardItem(fecha),QtGui.QStandardItem(tipo),QtGui.QStandardItem(text)])
            
            
            
            
            self.count+=1
            
            
        self.notificationCountLabel.setText("Cantidad :"+str(self.count))
