import sys
from PyQt5.QtWidgets import QApplication
from views.functional.app import App

app = QApplication(sys.argv)
mainWindow = App()
mainWindow.master.show()
sys.exit(app.exec_())