from PySide2 import QtCore, QtGui, QtWidgets
import re
import json
import csv
import os
from operation.operation import Operation
# from operation.operationmgr import OperationMgr

class OMngrDialog(QtWidgets.QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, operMngr):
        super(OMngrDialog, self).__init__()

        self.operMngr = operMngr
        self.createOperationBox()
        

        mainLayout = QtWidgets.QGridLayout()
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.aplicarCambios)
        buttonBox.rejected.connect(self.reject)

        
   #     mainLayout.setMenuBar(self.menuBar)
   
        mainLayout.addWidget(self.operationBox)
        mainLayout.addWidget(buttonBox)
    
        self.setLayout(mainLayout)        
        self.setWindowTitle("Maximo operaciones simultaneas")
        
       
    def aplicarCambios(self):
        
        
        countText=self.maxCount.text()
        
        try:
            count=int(countText)
            self.operMngr.setMaxRunningOperations(count)
            self.accept()
        except Exception as e:
            print(e)
        
        
    

    def createOperationBox(self):
        self.operationBox = QtWidgets.QGroupBox("Configuracion")
              
        self.maxCount = QtWidgets.QLineEdit("100")        
       
        layout = QtWidgets.QFormLayout()
        layout.addRow(QtWidgets.QLabel("Maximo operaciones simultaneas:"), self.maxCount)
       
        self.operationBox.setLayout(layout)

            
    
        
if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    dialog = OMngrDialog()
    sys.exit(dialog.exec_())