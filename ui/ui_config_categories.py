# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'set_categories.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class UiConfingCategories(object):
    def setupUi(self, UiConfingCategories):
        UiConfingCategories.setObjectName("UiConfingCategories")
        UiConfingCategories.resize(365, 430)
        self.centralwidget = QtWidgets.QWidget(UiConfingCategories)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.scroll_area = QtWidgets.QScrollArea(self.centralwidget)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_layout = QtWidgets.QWidget()
        self.scroll_layout.setGeometry(QtCore.QRect(0, 0, 341, 336))
        self.scroll_layout.setObjectName("scroll_layout")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scroll_layout)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.categories_layout = QtWidgets.QVBoxLayout()
        self.categories_layout.setContentsMargins(7, 7, 7, 7)
        self.categories_layout.setObjectName("categories_layout")
        self.verticalLayout.addLayout(self.categories_layout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.scroll_area.setWidget(self.scroll_layout)
        self.verticalLayout_2.addWidget(self.scroll_area)
        self.apply_button = QtWidgets.QPushButton(self.centralwidget)
        self.apply_button.setObjectName("apply_button")
        self.verticalLayout_2.addWidget(self.apply_button)
        UiConfingCategories.setCentralWidget(self.centralwidget)

        self.retranslateUi(UiConfingCategories)
        QtCore.QMetaObject.connectSlotsByName(UiConfingCategories)

    def retranslateUi(self, UiConfingCategories):
        _translate = QtCore.QCoreApplication.translate
        UiConfingCategories.setWindowTitle(_translate("UiConfingCategories", "Выбор категории"))
        self.apply_button.setText(_translate("UiConfingCategories", "Потвердить"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    UiConfingCategories = QtWidgets.QMainWindow()
    ui = Ui_UiConfingCategories()
    ui.setupUi(UiConfingCategories)
    UiConfingCategories.show()
    sys.exit(app.exec_())
