from PyQt5.QtWidgets import QMessageBox, QMainWindow, QCheckBox, QDialog, QSpinBox, QPushButton, QRadioButton

from ui.ui_config_categories import UiConfingCategories
from ui.ui_dialog_line_edit_window import UiLineEdit
from ui.ui_information_fields_window import UiInformationFields


def confirm_saving(window, text, save, dont_save, title='Потвердить изменения', cancel=None):
    dialog = QMessageBox(window)
    dialog.setWindowTitle(title)
    buttons = QMessageBox.Save | QMessageBox.No | QMessageBox.Cancel
    dialog.setStandardButtons(buttons)
    dialog.setText(text)
    dialog.setIcon(QMessageBox.Question)
    answer = dialog.exec()
    if answer == QMessageBox.No:
        dont_save()
    elif answer == QMessageBox.Save:
        save()
    else:
        if cancel:
            cancel()


def open_confing_categories_window(category, legal_units, function, *args, check=lambda x: x, is_one=False):
    confing_categories_window = ConfingCategoriesWindow(category, legal_units, function, *args,
                                                        check=check, is_one=is_one)
    confing_categories_window.show()
    return confing_categories_window


class ConfigItemsWindow(QMainWindow, UiConfingCategories):
    def __init__(self, default_item, items, function, *args, check=lambda x: x, is_one=False):
        super().__init__()
        self.setupUi(self)
        self.show()
        self.default_item = default_item
        self.items = items
        self.function = function
        self.args = args
        self.check = check
        self.items_widgets = {}
        self.is_one = is_one
        self.set_items_widgets()
        self.apply_button.clicked.connect(self.apply)

    def select_items(self):
        items = []
        for name, widget in self.items_widgets.items():
            if widget.isChecked():
                items.append(name)
        return items

    def apply(self):
        items = self.select_items()
        if self.check(items):
            self.function(items, *self.args)
            self.close()

    def set_items_widgets(self):
        self.items_widgets = {}
        if self.default_item:
            if self.is_one:
                check_box = QRadioButton(parent=self, text=self.default_item)
            else:
                check_box = QCheckBox(parent=self, text=self.default_item)
            check_box.setChecked(True)
            self.items_widgets[self.default_item] = check_box
            self.categories_layout.addWidget(check_box)
        for item in self.items:
            if not self.items_widgets.get(item):
                if self.is_one:
                    check_box = QRadioButton(parent=self, text=item)
                else:
                    check_box = QCheckBox(parent=self, text=item)
                check_box.setChecked(False)
                self.categories_layout.addWidget(check_box)
                self.items_widgets[item] = check_box

        if self.default_item:
            self.items_widgets[self.default_item].setChecked(True)


class ConfingCategoriesWindow(ConfigItemsWindow):
    def __init__(self, default_category, legal_units, function, *args, check, is_one=False):
        default_item = default_category
        items = legal_units.categories
        self.legal_units = legal_units
        super().__init__(default_item, items, function, *args, check=check, is_one=is_one)


def open_line_edit_window(text, title, function, *args, check=lambda x: x, default_value=''):
    line_edit_window = LineEditWindow(text, title, function, *args, check=check, default_value=default_value)
    line_edit_window.show()
    return line_edit_window


class MySpinBox(QSpinBox):
    def __init__(self, name, function, *args, **kwargs):
        self.old_value = None
        self.function = function
        super().__init__(*args, **kwargs)
        self.valueChanged.connect(self.spin)

    def setValue(self, *args):
        super().setValue(*args)
        self.old_value = self.value()

    def wheelEvent(self, event):
        event.ignore()

    def spin(self):
        if self.old_value:
            if self.old_value < self.value():
                self.up()
            else:
                self.down()
        self.old_value = self.value()

    def set_count(self, count):
        self.count = count

    def set_function(self, function):
        self.function = function

    def up(self):
        if self.old_value - 2 < 0:
            self.setValue(self.old_value)
            return
        self.function(self.old_value - 1, self.old_value - 2)

    def down(self):
        if self.old_value >= self.count:
            self.setValue(self.old_value)
            return
        self.function(self.old_value - 1, self.old_value)


class LineEditWindow(QMainWindow, UiLineEdit):
    def __init__(self, text, title, function, *args, check=lambda x: x, default_value=''):
        super().__init__()
        self.setupUi(self)
        self.info_text.setText(text)
        self.line_edit.setText(default_value)
        self.setWindowTitle(title)
        self.apply_button.clicked.connect(self.apply)
        self.function = function
        self.args = args
        self.check = check

    def apply(self):
        text = self.line_edit.text().strip()
        if self.check(text):
            self.function(text, *self.args)
            self.close()


class ItemsListWindow(QMainWindow, UiInformationFields):
    def __init__(self, title, items, double_clicked=None):
        super().__init__()
        self.double_clicked = double_clicked
        self.items = items
        self.setupUi(self)
        self.setWindowTitle(title)
        self.items_widget = {}
        self.active_item = None
        self.update_item_widget()
        self.remove_button.clicked.connect(self._remove_items)
        self.add_button.clicked.connect(self._add_item)
        self.save_button.deleteLater()

    def order_changes(self, old_index, new_index):
        temp = self.items[new_index], self.items[old_index]
        self.items[old_index], self.items[new_index] = temp
        self.update_item_widget()
        self.save_items()

    def remove_item_widget(self):
        if self.items_widget:
            for widgets in self.items_widget.values():
                button, spin_box = widgets
                button.deleteLater()
                spin_box.deleteLater()

    def update_item_widget(self):
        self.remove_item_widget()
        self.items_widget = {}
        for i in range(len(self.items)):
            button = QPushButton(parent=self, text=self.items[i])
            button.clicked.connect(lambda *x, name=self.items[i]: self.select_items(name))
            spin_box = MySpinBox(parent=self, name=self.items[i], function=self.order_changes)
            spin_box.set_function(self.order_changes)
            spin_box.setValue(i + 1)
            spin_box.set_count(len(self.items))
            self.information_fields_form.addRow(button, spin_box)
            self.items_widget[self.items[i]] = (button, spin_box)

    def select_items(self, active_name):
        if self.double_clicked and active_name == self.active_item:
            self.double_clicked(active_name)
            return
        self.active_item = active_name
        for name, widget in self.items_widget.items():
            button, spin_box = widget
            if name == active_name:
                button.setStyleSheet("background-color : yellow")
            else:
                button.setStyleSheet('background-color: white')

    def _remove_items(self):
        self.remove_items()
        self.update_item_widget()
        self.save_items()

    def _add_item(self):
        self.add_item()
        self.update_item_widget()
        self.save_items()


    def remove_items(self):
        return

    def add_item(self):
        return

    def dialog_remove_items(self, text, title):
        if not self.active_item:
            return
        dialog = QMessageBox(self)
        dialog.setText(text)
        dialog.setInformativeText('Потвердить действия?')
        dialog.setWindowTitle(title)
        dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        if dialog.exec() != QMessageBox.StandardButton.Yes:
            return
        if self.active_item:
            name_list = []
            for name in self.items:
                if name != self.active_item:
                    name_list.append(name)
            self.items = name_list



    def save_items(self):
        return


if __name__ == '__main__':
    import sys
    from PyQt5 import QtWidgets
    from main_window import MainWindow

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    print(open_line_edit_window('sf', 'sfd', main_window))
