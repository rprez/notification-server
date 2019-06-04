from PySide2 import QtCore, QtGui, QtWidgets
#import application_rc
import time
from gui.configer import ConfigurationDialog
from gui.coperation import OperationDialog
from operation.operationmgr import OperationMgr
from operation.operation import Operation
import datetime
import os
import threading
from gui.copemngr import OMngrDialog
from gui.utemodomonitor import ModoMonitorWindows
import logging 

class MainWindow(QtWidgets.QMainWindow):
    
    HideID=True
   
    def __init__(self,loggerH):
        super(MainWindow, self).__init__()

        self.logger=loggerH
        self.configer=None
       # self.curFile = ''

        mainLayout = QtWidgets.QVBoxLayout()
        
        self.createOperationBoxes() 
        
       # mainLayout.addWidget(self.horizontalGroupBox)
       # self.setLayout(self.listLayout)
        self.setWindowTitle("Operaciones")
        self.setWindowIcon(QtGui.QIcon('./gui/imagenes/operaciones2.png'))
     
        wit=QtWidgets.QWidget()
        wit.setLayout(self.mainLayout)
        self.setCentralWidget(wit)
                #self.setLayout(mainLayout)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

      #  self.readSettings()

        #self.textEdit.document().contentsChanged.connect(self.documentWasModified)

     #   self.setCurrentFile('')
        self.setUnifiedTitleAndToolBarOnMac(True) 

        self.crearOperationManager()
    
        self.comngr=OMngrDialog(self.operMngr)
        
        self.modomonitorwindows=ModoMonitorWindows()

    def __logDebug(self,text):
        if self.logger!=None:
            self.logger.debug(text)
        
    def crearOperationManager(self):
        
        self.operMngr=OperationMgr()
      
        self.operMngr.ss.appendPending.connect(self.appendPending)
        self.operMngr.ss.deletePending.connect(self.deletePending)
        
        self.operMngr.ss.appendWorking.connect(self.appendWorking)
        self.operMngr.ss.changeStatusWorking.connect(self.changeStatusWorking)
        self.operMngr.ss.deleteWorking.connect(self.deleteWorking)
        
        self.operMngr.ss.appendEnded.connect(self.appendEnded)
        self.operMngr.ss.deleteEnded.connect(self.deleteEnded)

        
        self.operMngr.ss.updateInfo.connect(self.updateInformationBox)
        
    @QtCore.Slot(dict)    
    def printD(self,data):
        print(data)
     
    def handleEndingPopMenu(self,pos):

        rowIndex=self.listEnded.indexAt(pos)
        
        if rowIndex.row()!=-1:
            menu = QtWidgets.QMenu() 
        
            operId=self.endModel.itemFromIndex(self.endModel.index(rowIndex.row(), 4)).text()
        
            action = QtWidgets.QAction("Repetir", self)       
            action.triggered.connect(lambda : self.repetirOperacion(operId))
            menu.addAction(action)
            
          #  action = QtWidgets.QAction("Delete", self)       
          #  action.triggered.connect(lambda : self.cancelarPendingRow(rowIndex.row()))
          #  menu.addAction(action)
            
          #  action = QtWidgets.QAction("Delete", self)       
         #   action.triggered.connect(lambda : self.cancelarPendingRow(rowIndex.row()))
         #   menu.addAction(action)
            
            menu.exec_(QtGui.QCursor.pos())
      
      
    def repetirOperacion(self,operId): 
        
        self.operMngr.repetirOperacion(operId)
        
    def handlePendingPopMenuWorking(self,pos):    
        
        self.comngr.show()
      #  action = QtWidgets.QAction("Delete", self)       
      #  action.triggered.connect(lambda : self.cancelarPendingRow(rowIndex.row()))
      #  menu.addAction(action)
      #  menu.exec_(QtGui.QCursor.pos()) 
               
    def handlePendingPopMenu(self,pos):

        rowIndex=self.listPending.indexAt(pos)
        
        if rowIndex.row()!=-1:
            menu = QtWidgets.QMenu() 
            action = QtWidgets.QAction("Delete", self)       
            action.triggered.connect(lambda : self.cancelarPendingRow(rowIndex.row()))
            menu.addAction(action)
            menu.exec_(QtGui.QCursor.pos())        
            
    def cancelarPendingRow(self,index):
        
        id=self.pendingModel.itemFromIndex(self.pendingModel.index(index, 4))
        self.__logDebug("deleting pending row %d, operation ID=%d"%(index,int(id.text())))
        
        self.operMngr.cancelarPendingOperacion(id.text())
        #self.pendingModel.removeRow(index)
    
    def createOperationBoxes(self):
        
         #self.horizontalGroupBox = QtWidgets.QGroupBox("Horizontal layout")
        self.mainLayout = QtWidgets.QVBoxLayout()

        self.listLayout = QtWidgets.QHBoxLayout()
        
        self.listPending = QtWidgets.QTreeView()
        self.listPending.setRootIsDecorated(False)
        self.listPending.setAlternatingRowColors(True)          
        self.pendingBox = QtWidgets.QGroupBox("Pendientes")
        layp = QtWidgets.QHBoxLayout()
        layp.addWidget(self.listPending)
        self.pendingBox.setLayout(layp)
        
        ####
        self.pendingModel = QtGui.QStandardItemModel(0, 5, self)
        self.pendingModel.setHeaderData(0, QtCore.Qt.Horizontal, "IP")
        self.pendingModel.setHeaderData(1, QtCore.Qt.Horizontal, "Fecha")
        self.pendingModel.setHeaderData(2, QtCore.Qt.Horizontal, "Operación")
        self.pendingModel.setHeaderData(3, QtCore.Qt.Horizontal, "Parametro")
        self.pendingModel.setHeaderData(4, QtCore.Qt.Horizontal, "ID")
        self.listPending.setModel(self.pendingModel)        
        self.listPending.setColumnHidden(4,self.HideID)
        
        
        self.listPending.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listPending.customContextMenuRequested.connect(self.handlePendingPopMenu)
        
        self.listPending.selectionModel().selectionChanged.connect(self.selectChangedPending)
         #####
        
        
        ####
        self.listWorking = QtWidgets.QTreeView()
        self.listWorking.setRootIsDecorated(False)
        self.listWorking.setAlternatingRowColors(True) 
        self.workingBox = QtWidgets.QGroupBox("En proceso")
        layw = QtWidgets.QHBoxLayout()
        layw.addWidget(self.listWorking)
        self.workingBox.setLayout(layw)
        
        self.workingModel = QtGui.QStandardItemModel(0, 4, self)
        self.workingModel.setHeaderData(0, QtCore.Qt.Horizontal, "IP")
        self.workingModel.setHeaderData(1, QtCore.Qt.Horizontal, "Operación")
        self.workingModel.setHeaderData(2, QtCore.Qt.Horizontal, "Estado")
        self.workingModel.setHeaderData(3, QtCore.Qt.Horizontal, "ID")
        self.listWorking.setModel(self.workingModel)     
        self.listWorking.setColumnHidden(3,self.HideID)
        
        self.listWorking.selectionModel().selectionChanged.connect(self.selectChangedWorking)

        self.listWorking.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWorking.customContextMenuRequested.connect(self.handlePendingPopMenuWorking)
       
        #####
        
        self.listEnded = QtWidgets.QTreeView()
        self.listEnded.setRootIsDecorated(False)
        self.listEnded.setAlternatingRowColors(True) 
        
       # self.listEnded.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        
        self.endedBox = QtWidgets.QGroupBox("Finalizados")
        laye = QtWidgets.QHBoxLayout()
        laye.addWidget(self.listEnded)
        self.endedBox.setLayout(laye)
       
        
        self.endModel = QtGui.QStandardItemModel(0, 5, self)
        self.endModel.setHeaderData(0, QtCore.Qt.Horizontal, "IP")
        self.endModel.setHeaderData(1, QtCore.Qt.Horizontal, "Operación")
        self.endModel.setHeaderData(2, QtCore.Qt.Horizontal, "Resultado")
        self.endModel.setHeaderData(3, QtCore.Qt.Horizontal, "Fecha Fin")
        self.endModel.setHeaderData(4, QtCore.Qt.Horizontal, "ID")
#  self.endModel.setHeaderData(4, QtCore.Qt.Horizontal, "Resultado")
        self.listEnded.setModel(self.endModel)     
        self.listEnded.setColumnHidden(4,self.HideID)
      
        self.listEnded.selectionModel().selectionChanged.connect(self.selectChangedEnded)

        self.listEnded.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listEnded.customContextMenuRequested.connect(self.handleEndingPopMenu)
        
       #########
        self.listLayout.addWidget(self.pendingBox)
        self.listLayout.addWidget(self.workingBox)
        self.listLayout.addWidget(self.endedBox)
        
        listsW=QtWidgets.QWidget()
        listsW.setLayout(self.listLayout)
        self.mainLayout.addWidget(listsW)
        
        self.informationLabel= QtWidgets.QTextEdit()
        self.informationLabel.setPlainText("")
        self.informationLabel.setReadOnly(True)
        self.informationLabel.setFontPointSize(10)
        
        
        self.resultaData= QtWidgets.QTextEdit()
        self.resultaData.setPlainText("")
        self.resultaData.setReadOnly(True)
        self.resultaData.setFontPointSize(10)
        
        
        self.informationBox = QtWidgets.QGroupBox("Información")
        layI = QtWidgets.QHBoxLayout()
        layI.addWidget(self.informationLabel)
        layI.addWidget(self.resultaData)
        self.informationBox.setLayout(layI)
        
        layI.setStretchFactor(self.listLayout,0.2)
    
    
        self.mainLayout.addWidget(self.informationBox)
     
    def selectChangedPending(self, selected,deselected):
        
        self.__logDebug("selectionChangedPending")
        if selected!=None:
            indexes=selected.indexes()
            if len(indexes):
                index=indexes[0].row()
                selectedOperationId=self.pendingModel.item(index,4).text()   
                self.operMngr.selectedOperationId=selectedOperationId     
                self.__logDebug("selected ID=%s"%(selectedOperationId))    
    
    def selectChangedWorking(self, selected,deselected):
        
        self.__logDebug("selectionChangedWorking")
        if selected!=None:
            indexes=selected.indexes()
            if len(indexes):
                index=indexes[0].row()
                selectedOperationId=self.workingModel.item(index, 3).text()   
                self.operMngr.selectedOperationId=selectedOperationId     
                self.__logDebug("selected ID=%s"%(selectedOperationId))    
    
    def selectChangedEnded(self, selected,deselected):
       
        self.__logDebug("selectionChangedEnded")
        if selected!=None:
            indexes=selected.indexes()
            if len(indexes):
                index=indexes[0].row()
                selectedOperationId=self.endModel.item(index, 4).text() 
                self.operMngr.selectedOperationId=selectedOperationId
                self.__logDebug("selected ID=%s"%(selectedOperationId))    

    def updateInformationBox(self,msg,resultText):
        
        self.informationLabel.setText(msg) 
        self.informationLabel.verticalScrollBar().setSliderPosition(self.informationLabel.verticalScrollBar().maximum())
        self.resultaData.setText(resultText)
     
    def closeEvent(self, event):
        
        if self.workingModel.rowCount()>0:
            quit_msg = "Al salir se interrumpen las operaciones, desea continuar?"
            reply = QtWidgets.QMessageBox.question(self, 'Salir?', 
                     quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
    
            if reply == QtWidgets.QMessageBox.Yes:
                event.accept()
                os._exit(1)
            else:
                event.ignore() 
        else:
            event.accept()
            os._exit(1)
            
    def newFile(self):
        if self.maybeSave():
            self.textEdit.clear()
            self.setCurrentFile('')

    def open(self):
        if self.maybeSave():
            fileName, filtr = QtWidgets.QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)

        return self.saveAs()

    def saveAs(self):
        fileName, filtr = QtWidgets.QFileDialog.getSaveFileName(self)
        if fileName:
            return self.saveFile(fileName)

        return False

    def about(self):
        QtWidgets.QMessageBox.about(self, "Sobre la aplicación",
                "<b>Operaciones</b> facilita la gestión de los modems RS485-3G "
                "desarrollados conjuntamente entre Antel y Ute, "
                "por bugs o sugerencias, escribir a pfrodriguez@antel.com.uy")


    def createActions(self):

        self.cconfig = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/config-480.png'), "&Crear Configuración",
                self,shortcut="Ctrl+K",
                statusTip="Crear configuración", triggered=self.showConfiger)

        self.coperation = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/operationicon.png'),
                "&Crear Operación", self, shortcut="Ctrl+O",
                statusTip="Encolar nueva operación", triggered=self.createOperation)

        self.operationPlay = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/playicon.png'),
                "&Play operaciones", self,shortcut="Ctrl+P",
                statusTip="Parar o continuar operaciones", triggered=self.operationPlayAction)
        
        self.operationPause = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/pauseicon.png'),
                "&Pausar operaciones", self,shortcut="Ctrl+U",
                statusTip="Pausar operaciones", triggered=self.operationPauseAction)
        
        self.operationPause.setDisabled(True)
        
        self.operationCancel = QtWidgets.QAction(QtGui.QIcon('./gui/imagenes/stopicon.png'),
                "&Cancelar operaciones", self,shortcut="Ctrl+I",
                statusTip="Cancelar operaciones", triggered=self.operationCancelAction)


        self.saveAsAct = QtWidgets.QAction("Save &As...", self,
                shortcut=QtGui.QKeySequence.SaveAs,
                statusTip="Save the document under a new name",
                triggered=self.saveAs)

        self.exitAct = QtWidgets.QAction("E&xit", self, shortcut="Ctrl+Q",
                statusTip="Exit the application", triggered=self.close)

        self.modoMonitor = QtWidgets.QAction("M&odo monitor", self, shortcut="Ctrl+M",
                statusTip="Modo monitor", triggered=self.showMonitorMode)

#        self.cutAct = QtWidgets.QAction(QtGui.QIcon(':/images/cut.png'), "Cu&t",self, shortcut=QtGui.QKeySequence.Cut,statusTip="Cut the current selection's contents to the clipboard",                triggered=self.textEdit.cut)

        #self.copyAct = QtWidgets.QAction(QtGui.QIcon(':/images/copy.png'),   "&Copy", self, shortcut=QtGui.QKeySequence.Copy,                statusTip="Copy the current selection's contents to the clipboard",                triggered=self.textEdit.copy)

        #self.pasteAct = QtWidgets.QAction(QtGui.QIcon(':/images/paste.png'),                "&Paste", self, shortcut=QtGui.QKeySequence.Paste,                statusTip="Paste the clipboard's contents into the current selection",                triggered=self.textEdit.paste)

        self.aboutAct = QtWidgets.QAction("&About", self,
                statusTip="Show the application's About box",
                triggered=self.about)

       # self.cutAct.setEnabled(False)
      #  self.copyAct.setEnabled(False)
      #  self.textEdit.copyAvailable.connect(self.cutAct.setEnabled)
      #  self.textEdit.copyAvailable.connect(self.copyAct.setEnabled)

    def operationPlayAction(self):
        
        self.operationPause.setEnabled(True)
        self.operationPlay.setEnabled(False)
        
        self.operMngr.paused=False
        pass
    
    def operationPauseAction(self):
        
        self.operationPause.setEnabled(False)
        self.operationPlay.setEnabled(True)
        
        self.operMngr.paused=True
    
    
    def operationCancelAction(self):
        
        self.operMngr.abortAll()
    
    
    
    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu("&Archivo")
        self.fileMenu.addAction(self.cconfig)
        self.fileMenu.addAction(self.coperation)
       
       # self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = self.menuBar().addMenu("&Otros")
      
        self.editMenu.addAction(self.modoMonitor)
      #  self.editMenu.addAction(self.copyAct)
      #  self.editMenu.addAction(self.pasteAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&About")
        self.helpMenu.addAction(self.aboutAct)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("Configuration")
        self.fileToolBar.addAction(self.cconfig)
        self.fileToolBar.addAction(self.coperation)
      
        self.editToolBar = self.addToolBar("Operative")
        self.editToolBar.addAction(self.operationPlay)
        self.editToolBar.addAction(self.operationPause)
        self.editToolBar.addAction(self.operationCancel)
      #  self.editToolBar.addAction(self.cutAct)
      #  self.editToolBar.addAction(self.copyAct)
       # self.editToolBar.addAction(self.pasteAct)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    def createOperation(self):
        
        self.coper= OperationDialog(self.operMngr)
        self.coper.show()

    def showConfiger(self):
        
        self.configer= ConfigurationDialog()
        self.configer.show()
    
    def showMonitorMode(self):
        
        self.__logDebug("showing modo monitor")   
        if self.modomonitorwindows.isHidden():
            self.modomonitorwindows.show()
        
    @QtCore.Slot(Operation)
    def appendPending(self,oper):
        
        ip=oper.params['target']
        #fecha=oper.fechaCreacion.strftime("%Y-%m-%d %H:%M:%S")
        fecha=oper.fechaComienzo.strftime("%Y-%m-%d %H:%M:%S")
        count=self.pendingModel.rowCount()
        self.pendingModel.insertRow(count)
            
        self.pendingModel.setData(self.pendingModel.index(count, 0), ip)
        self.pendingModel.setData(self.pendingModel.index(count, 1), fecha)
        self.pendingModel.setData(self.pendingModel.index(count, 2),  oper.params['oper'])
        self.pendingModel.setData(self.pendingModel.index(count, 3), oper.params['params'])
        self.pendingModel.setData(self.pendingModel.index(count, 4), str(oper.operationId))
        
        self.pendingModel.itemFromIndex(self.pendingModel.index(count, 0)).setEditable(False)
        self.pendingModel.itemFromIndex(self.pendingModel.index(count, 1)).setEditable(False)
        self.pendingModel.itemFromIndex(self.pendingModel.index(count, 2)).setEditable(False)
        self.pendingModel.itemFromIndex(self.pendingModel.index(count, 3)).setEditable(False)
        self.pendingModel.itemFromIndex(self.pendingModel.index(count, 4)).setEditable(False)
       
    @QtCore.Slot(str)
    def deletePending(self,id):
        
       # print("Delete Pending operation ID=%d"%(int(id)))      
        itemFound=self.pendingModel.findItems(id,column=4)
        if len(itemFound)>0:
            indexToDelete=self.pendingModel.indexFromItem(itemFound[0])
            self.pendingModel.removeRow(indexToDelete.row())
          
    
    def deleteEnded(self,idoper):
        
      #  print("Delete Ended operation ID=%d"%(int(idoper)))      
        itemFound=self.endModel.findItems(idoper,column=4)
        if len(itemFound)>0:
            indexToDelete=self.endModel.indexFromItem(itemFound[0])
            self.endModel.removeRow(indexToDelete.row())
             
    @QtCore.Slot(str)
    def deleteWorking(self,idoper):
        
        self.__logDebug("Delete Working operation ID=%d"%(int(idoper)))      
        itemFound=self.workingModel.findItems(idoper,column=3)
        
        if len(itemFound)>0:
            indexToDelete=self.workingModel.indexFromItem(itemFound[0])
            self.workingModel.removeRow(indexToDelete.row())
                
    @QtCore.Slot(Operation)
    def appendWorking(self,oper):
        
       # print("Apending Working")        
       # print(oper)
        ip=oper.params['target']
      #  fecha=oper.fechaInicio.strftime("%Y-%m-%d %H:%M:%S")
        
        count=self.workingModel.rowCount()
        
        self.workingModel.insertRow(count)
            
        self.workingModel.setData(self.workingModel.index(count, 0), ip)
        self.workingModel.setData(self.workingModel.index(count, 1),  oper.params['oper'])
        self.workingModel.setData(self.workingModel.index(count, 2), "Iniciando")
        self.workingModel.setData(self.workingModel.index(count, 3), str(oper.operationId))
       
        self.workingModel.itemFromIndex(self.workingModel.index(count, 0)).setEditable(False)
        self.workingModel.itemFromIndex(self.workingModel.index(count, 1)).setEditable(False)
        self.workingModel.itemFromIndex(self.workingModel.index(count, 2)).setEditable(False)
        self.workingModel.itemFromIndex(self.workingModel.index(count, 3)).setEditable(False)
       
       
    @QtCore.Slot(dict)
    def changeStatusWorking(self,msgRx): 
        
        idnumber=msgRx['id']
        msg=msgRx['msg']
        
        itemFound=self.workingModel.findItems(idnumber,column=3)
        if len(itemFound)>0:
            index=self.pendingModel.indexFromItem(itemFound[0]).row()
            self.workingModel.setData(self.workingModel.index(index, 2), msg)
          
      
    @QtCore.Slot(Operation)
    def appendEnded(self,oper):

      #  print("Apending Ended")        
      #  print(oper)
        ip=oper.params['target']
        fechaFin=oper.fechaFin.strftime("%Y-%m-%d %H:%M:%S")
        
        self.endModel.insertRow(0)
            
        self.endModel.setData(self.endModel.index(0, 0), ip)
        self.endModel.setData(self.endModel.index(0, 1),  oper.params['oper'])
        if oper.result:
            self.endModel.setData(self.endModel.index(0, 2), "Ok")
        else:
            self.endModel.setData(self.endModel.index(0, 2), "Fail")
       
        self.endModel.setData(self.endModel.index(0, 3),fechaFin)      
        self.endModel.setData(self.endModel.index(0, 4), str(oper.operationId))
       
        self.endModel.itemFromIndex(self.endModel.index(0, 0)).setEditable(False)
        self.endModel.itemFromIndex(self.endModel.index(0, 1)).setEditable(False)
        self.endModel.itemFromIndex(self.endModel.index(0, 2)).setEditable(False)
        self.endModel.itemFromIndex(self.endModel.index(0, 3)).setEditable(False)
        self.endModel.itemFromIndex(self.endModel.index(0, 4)).setEditable(False)
        
class testWorker(QtCore.QThread):
 
    printD = QtCore.Signal(dict)
    
    def run(self):
        count = 0
        while count < 50:
            time.sleep(2)
            print("A Increasing")
            count += 1
            hola={}
            hola['msg']="asdfasdf"
            self.printD.emit( hola)

           
  

