from PySide2 import QtCore, QtGui, QtWidgets
from gui.utenotificationviewer import NotificationMainWindow

if __name__ == '__main__':

    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWin = NotificationMainWindow()
    mainWin.show()
    mainWin.notiClient.start()
    sys.exit(app.exec_())