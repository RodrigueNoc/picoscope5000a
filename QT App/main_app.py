from PySide2 import QtWidgets

from app import Ui_MainWindow

class MainWindow():
    def  __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow
        self.ui.setupUi(self)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()