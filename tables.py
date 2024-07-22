from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QMessageBox, QLabel, QLineEdit, QPushButton, QMainWindow

from json_controllers import JsonControl
from legal_units import ContainerLegalUnits
from dialog_window_tools import confirm_saving, ItemsListWindow, ConfigItemsWindow, open_line_edit_window
from ui.ui_settings_table_window import UiSettingsTableWindow

class GeneralTableModel(QStandardItemModel):
    def __init__(self, table, path):
        super().__init__()
        self.table = table
        self.json_controller = JsonControl(path)
        self.data_table = self.json_controller.get_file()
        self.update()

    def update(self):
        self.removeRows(0, self.rowCount())
        self.setRowCount(0)
        self.setColumnCount(0)
        # self.table.verticalHeader.clicked.connect(self.active_item)
        data = [i for i in self.data_table.values()]
        print(data)
        for column in range(len(data)):
            columns = []
            for row in range(len(data[column])):
                print(data[column][row], column, row)
                item = QStandardItem(data[column][row])
                item.emitDataChanged()
                columns.append(item)

            self.appendColumn(columns)
        self.setHorizontalHeaderLabels(list(self.data_table.keys()))

        self.table.setModel(self)
        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.table.doubleClicked.connect(self.change_value)

    def add_value(self):
        def set_name_group(names):
            name = names[0]
            self.temp = open_line_edit_window('введите значение', 'Добавление значения', set_value, name)

        def set_value(value, name_group):
            self.data_table[name_group].append(value)
            self.update()

        self.temp = ConfigItemsWindow(None, list(self.data_table.keys()), set_name_group, is_one=True)
        self.temp.show()

    def add_group(self):
        def check(name):
            return name not in self.data_table.keys()

        def set_name_group(name):
            self.data_table[name] = []
            self.update()

        self.temp = open_line_edit_window('введите имя группы', 'Добавление группы', set_name_group,
                                          check=check)
    def remove_group(self):
        def set_name_group(names):
            name = names[0]
            self.data_table.pop(name)
            self.update()

        self.temp = ConfigItemsWindow(None, list(self.data_table.keys()), set_name_group, is_one=True)
        self.temp.show()

    def remove_value(self):
        def set_value(values, name_group):
            value = values[0]
            self.data_table[name_group].remove(value)
            self.update()

        def set_name_group(names):
            name = names[0]
            self.temp = ConfigItemsWindow(None, list(self.data_table.keys()), set_value, name, is_one=True)
            self.temp.show()

        self.temp = ConfigItemsWindow(None, list(self.data_table.keys()), set_name_group, is_one=True)
        self.temp.show()

    def change_value(self, index):
        data = [i for i in self.data_table.values()]
        def set_value(value):
            data[index.column()][index.row()] = value
            self.update()
        self.temp = open_line_edit_window('введите новое значение', 'Изменение значения', set_value,
                                          default_value=data[index.column()][index.row()])

    def save(self):
        self.json_controller.set_file(self.data_table)

class UserTableModel(QStandardItemModel):
    def __init__(self, legal_units: ContainerLegalUnits, table, window, path):
        super().__init__()
        self.legal_units = legal_units
        self.table = table
        self.window = window
        self._categories = None
        self._columns = None
        self.sort = ('фио', lambda x: x)
        self.categories = 'all'
        self.legal_units.table = self
        self.id_legal_units = None
        self.path = path
        self.old_text_select_item = None
        self.old_select_item = None

        self.mode_editing = not False
        self.switching_mode()
        self.settings_window = None
        self.open_settings()
        self.settings_window.update_columns()
        self.settings_window.close()

        self.table.clicked.connect(self.select_item)
        self.table.doubleClicked.connect(self.active_item)
        self.table.setSelectionBehavior(self.table.SelectRows)

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, categories):
        if categories == 'all':
            categories = self.legal_units.categories
        self._categories = categories

    # get value columns
    @property
    def columns(self):
        return self._columns

    # set value and name columns
    @columns.setter
    def columns(self, name_and_columns):
        columns = [i[1] for i in name_and_columns]
        name = [i[0] for i in name_and_columns]
        self._columns = columns
        self._name_columns = name
        self.update()

    def update(self):
        self.removeRows(0, self.rowCount())
        self.id_legal_units = self.legal_units.get_id_legal_unit(self.categories, self.sort)
        self.setRowCount(0)
        self.setColumnCount(0)
        self.setHorizontalHeaderLabels(self._name_columns)
        # self.table.verticalHeader.clicked.connect(self.active_item)

        for id in self.id_legal_units:
            row = []
            for column in self.columns:
                item = QStandardItem(self.legal_units.get_property(id, column).value)
                item.emitDataChanged()
                row.append(item)
            self.appendRow(row)
        self.table.setModel(self)
        self.table.resizeColumnsToContents()
        self.old_select_item = None

    def switching_mode(self, button=None):
        self.mode_editing = not self.mode_editing
        if self.mode_editing:
            self.table.setEditTriggers(self.table.DoubleClicked)
        else:
            self.table.setEditTriggers(self.table.NoEditTriggers)

        if button:
            button.setText(('Реж Н', 'Реж Р')[self.mode_editing])

    def select_item(self, index):
        if not self.old_text_select_item or not self.old_select_item:
            return

        item = self.item(index.row(), index.column())

        if self.old_text_select_item != self.old_select_item.text():
            def new_active_item():
                self.old_select_item = item
                self.old_text_select_item = item.text()

            def save():
                id = self.id_legal_units[self.old_select_item.row()]
                name = self.columns[self.old_select_item.column()]
                self.legal_units.get_property(id, name).value = self.old_select_item.text().strip()
                self.legal_units.save()
                new_active_item()

            def cancel():
                self.old_select_item.setText(self.old_text_select_item)
                new_active_item()

            confirm_saving(self.window, 'Сохронить изменение ячейки?', save, cancel)

    def active_item(self, index):
        if not self.mode_editing or index.column() == 0:
            self.legal_units.open_window_legal_unit(self.id_legal_units[index.row()])
        self.old_select_item = self.item(index.row(), index.column())
        self.old_text_select_item = self.old_select_item.text()

    def is_table_change(self):
        for row in range(0, len(self.id_legal_units)):
            for column in range(0, len(self.columns)):
                id = self.id_legal_units[row]
                name = self.columns[column]
                if self.item(row, column).text() != self.legal_units.get_property(id, name).value:
                    return True
        return False

    def save_change(self):
        for row in range(0, len(self.id_legal_units)):
            for column in range(0, len(self.columns)):
                id = self.id_legal_units[row]
                name = self.columns[column]
                if self.item(row, column).text() != self.legal_units.get_property(id, name).value:
                    self.legal_units.get_property(id, name).value = self.old_select_item.text().strip()
        self.legal_units.save()

    def open_settings(self):
        if self.settings_window:
            self.settings_window.close()
        self.settings_window = SettingsTableWindow(self.legal_units, self, self.path)
        self.settings_window.show()


class SettingsTableWindow(QMainWindow, UiSettingsTableWindow):
    def __init__(self, legal_units, table_model, path):
        super().__init__()
        self.setupUi(self)
        self.legal_units = legal_units
        self.table_model = table_model
        self.json_controller = JsonControl(path)
        data = self.json_controller.get_file()
        self.sample = data.get('sample', {})
        self.current = data.get('current', 'полная таблица')
        self.is_temporary = data.get('is_temporary', False)
        self.sample_widgets = {}
        self.columns_widgets = {}
        self.setup_sample_widget()
        self.setup_columns_widget()

        self.columns_window = None

        self.save_sample_buttons.clicked.connect(self.save_sample)
        self.change_columns.clicked.connect(self.set_columns)
        self.remove_sample_buttons.clicked.connect(self.remove_sample)
        self.set_order_sample_buttons.clicked.connect(self.open_window_set_order)

    def open_window_set_order(self):
        self.sample_window = SampleItemsWindow(self.sample, self)
        self.sample_window.show()

    def set_order_sample(self, order):
        order = ['полная таблица', 'пустая таблица'] + order
        if self.is_temporary:
            order = [self.current] + order
        self.sample = dict([(i, self.sample.get(i, [])) for i in order])
        self.update_columns()
    def active_sample(self, name):
        if name == self.current:
            return
        if self.is_temporary:
            dialog = QMessageBox(self)
            text = 'Изменения в текущем шаблоне таблицы не будут сохранены'
            dialog.setInformativeText('Потвердить действия?')
            dialog.setText(text)
            dialog.setWindowTitle('Изменить шаблон')
            dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
            dialog.setDefaultButton(QMessageBox.StandardButton.No)
            if dialog.exec() != QMessageBox.StandardButton.Yes:
                return
            self.sample.pop(self.current)
            self.is_temporary = False
            self.current = name
        else:
            self.current = name
        self.update_columns()

    def save_sample(self):
        if not self.is_temporary:
            return

        def set_name(name):
            if name == 'полная таблица' or self.current == 'пустая таблица':
                dialog = QMessageBox(self)
                dialog.setText('Имена \'полная таблица\' и \'пустая таблица\' зарезервиравано')
                dialog.setWindowTitle('Сохранение шаблона')
                dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
                dialog.exec()
                return
            if self.sample.get(name, False):
                dialog = QMessageBox(self)
                text = 'Шаблон с таким именем уже существует'
                dialog.setInformativeText('Перезаписать его?')
                dialog.setText(text)
                dialog.setWindowTitle('Сохранение шаблона')
                dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
                dialog.setDefaultButton(QMessageBox.StandardButton.No)
                if dialog.exec() != QMessageBox.StandardButton.Yes:
                    return
            self.sample[name] = self.sample[self.current].copy()
            self.sample.pop(self.current)
            self.current = name
            self.is_temporary = False
            self.update_columns()

        text = 'Имя шаблона'
        title = 'Сохранения шаблона'
        self.temp = open_line_edit_window(text, title, set_name, default_value=self.current.strip('*'))

    def get_all_columns(self):
        columns = []
        for category in self.legal_units.categories:
            columns += list(self.legal_units.sample_information_fields[category].keys())
        columns = [(i, i) for i in dict([(i, None) for i in columns]).keys()]
        return columns

    def update_columns(self):
        print(self.current, self.sample)
        self.setup_sample_widget()
        self.setup_columns_widget()
        self.table_model.columns = self.sample[self.current]

    def remove_sample(self):
        if self.current == 'полная таблица' or self.current == 'пустая таблица':
            dialog = QMessageBox(self)
            dialog.setText('полная и пустая таблица  не подлежит удалению')
            dialog.setWindowTitle('Удаление шаблона')
            dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            dialog.exec()
            return
        dialog = QMessageBox(self)
        text = 'После удаление шаблон будет невозможно востановить'
        dialog.setInformativeText('Потвердить действие?')
        dialog.setText(text)
        dialog.setWindowTitle('Удаление шаблона')
        dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        if dialog.exec() != QMessageBox.StandardButton.Yes:
            return
        self.sample.pop(self.current)
        self.is_temporary = False
        self.current = list(self.sample.keys())[0]
        self.update_columns()

    def setup_sample_widget(self):
        for widget in self.sample_widgets.values():
            widget.deleteLater()
        self.sample_widgets = {}
        self.sample['полная таблица'] = self.get_all_columns()
        category = False
        if self.table_model.legal_units.categories_legal_units.values():
            if len(self.table_model.legal_units.categories_legal_units.values()) > 0:
                category = list(self.table_model.legal_units.categories_legal_units.values())[0]
        user_id = False
        if category and category.values() and len(category.values()) > 0:
            user_id = list(category.values())[0].name_user_id
        if user_id:
            self.sample['пустая таблица'] = [(user_id, user_id)]
        for name in self.sample.keys():
            button = QPushButton(text=name)
            if name == self.current:
                button.setStyleSheet('background-color: white')
            button.clicked.connect(lambda *reat, name=name: self.active_sample(name))
            self.sample_widgets[name] = button
            self.samples_layout.addWidget(button)

    def set_columns(self):
        if self.is_temporary:
            self.columns_window = ColumnsItemsWindow(self.sample[self.current], self)
            self.columns_window.show()
        else:
            self.sample = dict([(f'*{self.current}', self.sample[self.current])] + list(self.sample.items()))
            self.current = f'*{self.current}'
            self.is_temporary = True
            self.setup_sample_widget()
            self.setup_columns_widget()
            self.set_columns()

    def setup_columns_widget(self):
        self.sample['полная таблица'] = self.get_all_columns()
        category = False
        if self.table_model.legal_units.categories_legal_units.values():
            if len(self.table_model.legal_units.categories_legal_units.values()) > 0:
                category = list(self.table_model.legal_units.categories_legal_units.values())[0]
        user_id = False
        if category and category.values() and len(category.values()) > 0:
            user_id = list(category.values())[0].name_user_id
        if user_id:
            self.sample['пустая таблица'] = [(user_id, user_id)]
        columns = [i[0] for i in self.sample[self.current]]
        for widget in self.columns_widgets.values():
            widget.deleteLater()
        self.columns_widgets = {}
        for name in columns:
            label = QLabel(text=name)
            self.sample_widgets[name] = label
            self.columns_layout.addWidget(label)

    def closeEvent(self, event):
        data = {'sample': self.sample,
                'current': self.current,
                'is_temporary': self.is_temporary}
        self.json_controller.set_file(data)
        self.table_model.settings_window = None
        event.accept()


class ColumnsItemsWindow(ItemsListWindow):
    def __init__(self, columns, settings_table_window):
        self.settings_table_window = settings_table_window
        self.value_columns = [i[1] for i in columns] # value
        items = [i[0] for i in columns] # name
        super().__init__('Настройка столбцов', items, double_clicked=self.reset_item)

    def order_changes(self, old_index, new_index):
        temp = self.value_columns[new_index], self.value_columns[old_index]
        self.value_columns[old_index], self.value_columns[new_index] = temp
        super().order_changes(old_index, new_index)

    def add_item(self):
        def update_column(columns):
            self.items += columns
            self.value_columns += columns
            self.update_item_widget()
            self.save_items()

        def check_name(name):
            return name not in self.items

        def set_name(name):
            text = 'Введите формулу столбца'
            title = 'Создания столбца'
            self.window = open_line_edit_window(text, title, set_format_text, name, check=check_name)

        def set_format_text(format_text, name):
            self.items.append(name)
            self.value_columns.append(format_text)
            self.update_item_widget()
            self.save_items()

        dialog = QMessageBox(self)
        dialog.setText('Добовление столбцов')
        dialog.setText('Хотите добавить свой столбец?\nYes - Добавить свой\nNo - Выбрать из сушествуеющих')
        dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        answer = dialog.exec()
        if answer == QMessageBox.StandardButton.No:
            all_columns = [i[0] for i in self.settings_table_window.get_all_columns()]
            items = [i for i in set(all_columns).difference(set(self.items))]
            self.window = ConfigItemsWindow(None, items, update_column, is_one=False)
            self.window.show()
        if answer == QMessageBox.StandardButton.Yes:
            text = 'Введите имя столбца'
            title = 'Создания столбца'
            self.window = open_line_edit_window(text, title, set_name, check=check_name)


    def remove_items(self):
        if self.active_item:
            self.value_columns.pop(self.items.index(self.active_item))
            self.items.remove(self.active_item)
            self.active_item = None
            self.update_item_widget()

    def save_items(self):
        columns = list(zip(self.items, self.value_columns))
        self.settings_table_window.sample[self.settings_table_window.current] = columns
        self.settings_table_window.update_columns()

    def reset_item(self, old_name):
        def check_name(name):
            return name not in self.items or name == old_name

        def reset_name(name):

            text = 'Введите формулу столбца'
            title = 'Создания столбца'
            index = self.items.index(old_name)
            self.items[index] = name
            self.window = open_line_edit_window(text, title, reset_format_text, index, check=check_name,
                                                default_value=self.value_columns[index])

        def reset_format_text(format_text, index):
            self.value_columns[index] = format_text
            self.update_item_widget()
            self.save_items()

        text = 'Введите новое имя столбца или оставьте старое'
        title = 'Изменение столбца'
        self.window = open_line_edit_window(text, title, reset_name, check=check_name, default_value=old_name)

class SampleItemsWindow(ItemsListWindow):
    def __init__(self, sample, settings_table_window):
        self.settings_table_window = settings_table_window
        items = list(sample.keys()) # name
        if self.settings_table_window.is_temporary:
            items.pop(0)
        items.remove('полная таблица')
        items.remove('пустая таблица')
        super().__init__('Настройка столбцов', items)
        self.add_button.deleteLater()
        self.remove_button.deleteLater()

    def select_items(self, *args):
        pass

    def save_items(self):
        self.settings_table_window.set_order_sample(self.items)