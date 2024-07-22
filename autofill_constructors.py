import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QComboBox, QFormLayout, QLabel


class group_general_table(QComboBox):
    def __init__(self, name, window):
        super().__init__()
        self.name = name
        name_label = QLabel(text=name)
        self.parent = window
        self.parent.forms.addRow(name_label, self)
class autofill_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.forms = QFormLayout()
        point1 = group_general_table('njxrf', self)

        central_widget = QWidget()
        central_widget.setLayout(self.forms)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    main_window = autofill_window()
    main_window.show()
    sys.exit(app.exec_())

