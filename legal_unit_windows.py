from typing import Dict, Any

from ui.ui_information_field_window import UiInformationFieldWindow

from ui.ui_legal_unit_window import UiUnitLegalWindow
from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from dialog_window_tools import confirm_saving, open_line_edit_window, open_confing_categories_window, ItemsListWindow


class LegalUnitWindow(QMainWindow, UiUnitLegalWindow):
    def __init__(self, legal_unit, category, legal_units, fields):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(f'{legal_unit.title}, категория - {category}')
        self.example_button.deleteLater()
        self.example_field.deleteLater()
        self.example_label.deleteLater()
        self.example_date.deleteLater()

        self.information_fields_widgets = {}
        self.category = category
        self.legal_unit = legal_unit
        self.legal_units = legal_units
        self.setup_ui_legal_unit_frame(fields)
        self.see_all_field_button.setChecked(True)
        self.update_information_fields()
        self.save_button.clicked.connect(self.save)

        self.config_information_windows = None
        self.config_documents_windows = None

        self.config_information_field_button.clicked.connect(self.open_config_information_windows)
        self.config_document_button.clicked.connect(self.open_config_documents_windows)
        self.remove_legal_unit_button.clicked.connect(self.remove_legal_unit)
        self.reset_categories_button.clicked.connect(self.reset_categories)
        self.see_all_field_button.clicked.connect(self.update_information_fields)
        self.see_edit_field_button.clicked.connect(self.update_information_fields)
        self.see_combo_field_button.clicked.connect(self.update_information_fields)

    def update_information_fields(self):
        if self.information_fields_widgets:
            for widgets in self.information_fields_widgets.values():
                label, line_edit = widgets
                label.deleteLater()
                line_edit.deleteLater()
        self.information_fields_widgets = {}
        # bulding dicts name fields: value
        filter_table = self.get_filter_information_fields()

        value_information_fields = []
        if filter_table == 'all' or filter_table == 'edit':
            value_information_fields = list(self.legal_unit.value_information_fields.items())
        if filter_table == 'all' or filter_table == 'combo':
            value_information_fields += list(self.legal_unit.value_combo_information_fields.items())

        for name, value in value_information_fields:
            label = QPushButton(text=name)
            label.clicked.connect(lambda *reat, name=name: self.open_information_field_window(name))
            line_edit = QLineEdit()
            line_edit.setText(value)
            self.field_layout.addRow(label, line_edit)
            self.information_fields_widgets[name] = (label, line_edit)

    def get_filter_information_fields(self):
        if self.see_all_field_button.isChecked():
            return 'all'
        if self.see_combo_field_button.isChecked():
            return 'combo'
        if self.see_edit_field_button.isChecked():
            return 'edit'

    def setup_ui_legal_unit_frame(self, fields):
        for name, key in fields.items():
            fields[name] = self.legal_unit.get_property(key).value

        # title = f'{str(worker.post).capitalize()} - {worker.surname} {worker.name[0]}. {worker.patronymic[0]}.'nNN
        # self.setWindowTitle(title)

        for name, value in fields.items():
            label = QLabel(text=name)
            line_edit = QLineEdit()
            line_edit.setText(value)
            self.subclass_form.addRow(label, line_edit)

    def change_information_fields(self):
        change_combo_field = False
        for name, value in self.legal_unit.value_combo_information_fields.items():
            if self.information_fields_widgets.get(name):
                if self.information_fields_widgets[name][1].text() != value:
                    change_combo_field = True
                    break

        if change_combo_field:
            dialog = QMessageBox(self)
            dialog.setWindowTitle('Внимание!')
            text = 'Были зафиксированы изменения в комбирнированом информационном поле, которые не сохраняться.'
            dialog.setText(text)
            text = 'Комбинированые поля используют информацию из других информационных полей, поэтому их '
            text += 'можно редактировать только через формулу, которая доступна в окне информационого поля.'
            text += 'Не стоит менять их значения, если не знаете как это работает'
            dialog.setDetailedText(text)
            dialog.exec()
        for name, value in self.legal_unit.value_information_fields.items():
            if self.information_fields_widgets.get(name):
                if self.information_fields_widgets[name][1].text() != value:
                    return True
        return False

    def open_information_field_window(self, name):
        information_field = self.legal_unit.get_property(name)
        self.information_field_window = InformationFieldWindow(self.legal_units, self.category, self.legal_unit,
                                                               information_field)
        self.information_field_window.show()

    def save(self):
        self.save_information_fields()
        self.legal_units.table.update()
        self.legal_units.save()

    def save_information_fields(self):
        value_information_fields = {}
        for name, widget in self.information_fields_widgets.items():
            label, line_edit = widget
            value_information_fields[name] = line_edit.text()
        self.legal_unit.value_information_fields = value_information_fields

    def remove_legal_unit(self):
        dialog = QMessageBox(self)
        text = 'Удаление еденицы сотрет без возможности востановления всю ее информацию. '
        text += 'Потвердить действия?'
        dialog.setText(text)
        dialog.setWindowTitle('Удаления юридической еденицы')
        dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
        dialog.setDefaultButton(QMessageBox.StandardButton.No)
        if dialog.exec() != QMessageBox.StandardButton.Yes:
            return
        self.legal_units.categories_legal_units[self.category].pop(self.legal_unit.id)
        self.legal_units.table.update()
        self.legal_units.save()
        self.legal_units.legal_unit_window = None
        self.close()

    def reset_categories(self):
        def check_category(categories):
            if len(categories) == 1:
                return categories[0] != self.category
            return False

        def set_category(categories):
            category = categories[0]
            old_information_fields = set(self.legal_units.sample_information_fields[self.category].keys())
            new_information_fields = set(self.legal_units.sample_information_fields[category].keys())
            unsaved_information_fields = list(old_information_fields.difference(new_information_fields))
            count_unsaved = len(unsaved_information_fields)
            text = f'Было найдено {count_unsaved} пункт(-ов) несоотвествия. Эту информацю будет невозможно востановить'
            text += '\nДалее список имя - значение:'
            for i in range(count_unsaved):
                value = self.legal_unit.get_property(unsaved_information_fields[i]).value
                text += f'\n\t{i + 1}) {unsaved_information_fields[i]} - {value}'
            text += '\n\nРекомендуемые решения, отмените изменения категории и предварительно добавте в '
            text += 'новую категорию информационные поля, которые хотели бы сохранить.'
            dialog = QMessageBox(self)
            dialog.setDetailedText(text)
            text = 'После изменения категории, все информационые поля, которых не существует в новой категории'
            text += f' удаляться без возможности востановалние. \n\nБудет удалено {count_unsaved} пункт(-ов)'
            text += '\nСм. детали, для подробной информации'
            dialog.setText(text)
            dialog.setInformativeText('Потвердить действия?')
            dialog.setWindowTitle('Изменения категории')
            dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
            dialog.setDefaultButton(QMessageBox.StandardButton.No)
            if dialog.exec() != QMessageBox.StandardButton.Yes:
                return

            value_information_fields = self.legal_unit.value_information_fields
            self.legal_units.categories_legal_units[self.category].pop(self.legal_unit.id)
            self.legal_units.categories_legal_units[category][self.legal_unit.id] = self.legal_unit
            self.legal_units.changes_sample(category, self.legal_unit.id)
            self.legal_unit.value_information_fields = value_information_fields
            self.legal_units.table.update()
            self.legal_units.save()
            self.close()

        self.temp = open_confing_categories_window(self.category, self.legal_units, set_category, check=check_category,
                                                   is_one=True)

    def closeEvent(self, event):
        change_information_fields = self.change_information_fields()
        if change_information_fields:
            def save():
                self.save()
                event.accept()

            confirm_saving(window=self,
                           text='Сохранить изменения?',
                           save=save,
                           dont_save=lambda: event.accept(),
                           cancel=event.ignore())
        else:
            event.accept()

    def open_config_information_windows(self):
        if self.config_information_windows:
            self.config_information_windows.close()
        self.config_information_windows = InformationFieldsCategoryWindow(legal_unit=self.legal_unit,
                                                                          category=self.category,
                                                                          legal_units=self.legal_units)
        self.config_information_windows.show()

    def open_config_documents_windows(self):
        if self.config_documents_windows:
            self.config_documents_windows.close()
        self.config_documents_windows = DocumentsCategoryWindow(legal_unit=self.legal_unit,
                                                                category=self.category,
                                                                legal_units=self.legal_units)
        self.config_documents_windows.show()


class WorkerWindow(LegalUnitWindow):
    def __init__(self, legal_unit, category, legal_units):
        fields = {'ФИО': 'фио',
                  'Паспорт серия, номер': '<серия> <номер>',
                  'Паспорт выдан': '<паспорт дата выдачи>, <паспорт выдан>',
                  'Родился': '<дата рождения>, <место рождения>',
                  'Адрес регестрация': 'адрес регестрации',
                  'Код подразделения': 'код подразделения'}

        super().__init__(legal_unit, category, legal_units, fields)


class CarWindow(LegalUnitWindow):
    def __init__(self, legal_unit, category, legal_units):
        fields = {'гос номер': 'гос номер',
                  'марка': 'марка',
                  'Тип ТС': 'Тип ТС',
                  'год выпуска': 'год выпуска',
                  'тип в/ш/л': 'тип в/ш/л'}

        super().__init__(legal_unit, category, legal_units, fields)


class DocumentsCategoryWindow(ItemsListWindow):
    def __init__(self, legal_unit, category, legal_units):
        title = f'Категория - {category}'
        items = list(legal_units.sample_documents[category].keys())
        super().__init__(title, items)
        self.legal_unit = legal_unit
        self.legal_units = legal_units
        self.category = category
        self.update_item_widget()

    def remove_items(self):
        text = 'Удаление документа, сотрет без возможности востановления всю информацию'
        text += ' у всех еденииц принадлежащих данной категории.'
        text += '\nФайлы принадлежащие документов сохраняться'
        title = 'Удаления информационого поля'
        self.dialog_remove_items(text, title)

    def add_item(self):
        def set_categories(categories, name):
            for category in categories:

                self.legal_units.sample_documents[category][name] = {'name': name, 'short_name': name,
                                                                     'validity_period': 30, 'path_folder': ''}
                self.legal_units.changes_sample(category)

        def set_name(name):
            self.temp = open_confing_categories_window(self.category, self.legal_units, set_categories, name)

        documents = [self.legal_units.sample_documents[self.category].keys()]

        def check(name):
            if name:
                if name not in documents:
                    return True
            return False

        self.temp = open_line_edit_window('Ввод имя документа', 'Создания информационого поля',
                                          set_name, check=check)


def new_items(self, categories):
    new_categories = {}
    for name in self.items:
        new_categories[name] = categories[name]
    return new_categories


def save_items(self):
    categories = self.legal_units.sample_documents[self.category]
    self.legal_units.set_sample_information_fields(self.category, self.new_items(categories))


class InformationFieldsCategoryWindow(ItemsListWindow):
    def __init__(self, legal_unit, category, legal_units):
        title = f'Категория - {category}'
        items = list(legal_units.sample_information_fields[category].keys())
        super().__init__(title, items)
        self.legal_unit = legal_unit
        self.legal_units = legal_units
        self.category = category
        self.update_item_widget()

    def remove_items(self):
        text = 'Удаление информационого поля, сотрет без возможности востановления всю информацию'
        text += ' у всех еденииц принадлежащих данной категории.'
        title = 'Удаления информационого поля'
        self.dialog_remove_items(text, title)

    def save_items(self):
        categories = self.legal_units.sample_information_fields[self.category]
        self.legal_units.set_sample_information_fields(self.category, self.new_items(categories))

    def new_items(self, categories):
        new_categories = {}
        for name in self.items:
            new_categories[name] = categories[name]
        return new_categories

    def add_item(self):
        def set_categories(categories, name):
            for category in categories:
                self.legal_units.sample_information_fields[category][name] = 'text'
                self.legal_units.changes_sample(category)

        def set_name(name):
            self.temp = open_confing_categories_window(self.category, self.legal_units, set_categories, name)

        information_fields = [self.legal_units.sample_information_fields[self.category].keys()]

        def check(name):
            if name:
                if name not in information_fields:
                    return True
            return False

        self.temp = open_line_edit_window('Ввод имя информационого поля', 'Создания информационого поля',
                                          set_name, check=check)


class InformationFieldWindow(QMainWindow, UiInformationFieldWindow):
    def __init__(self, legal_units, category, legal_unit, information_field):
        super().__init__()
        self.setupUi(self)
        self.information_field = information_field
        self.belonging_label.setText(legal_unit.get_property(legal_unit.name_user_id).value)
        self.legal_unit = legal_unit
        self.legal_units = legal_units
        self.category = category
        self.name_field.setText(information_field.name)
        self.value_field.setText(information_field.edit_value)
        self.apply_button.clicked.connect(self.apply)
        self.clear_button.clicked.connect(self.close)
        if self.information_field.format == 'text':
            self.set_text_format.setChecked(True)
        elif self.information_field.format == 'date':
            self.set_date_format.setChecked(True)
        elif self.information_field.format == 'combo':
            self.set_combo_format.setChecked(True)

    def remove(self):
        self.legal_unit.remove_field_all(self.information_field.name)
        self.legal_unit_area.remove_field(self.information_field.name)

    def apply(self):
        is_change_value = self.information_field.edit_value != self.value_field.text()
        is_change_name = self.information_field.name != self.name_field.text()
        is_change_format = self.information_field.format != self.check_format()
        if is_change_format:
            self.change_format(self.check_format())
        if is_change_value:
            self.change_value(self.value_field.text())
        if is_change_name:
            self.change_name(self.information_field.name, self.name_field.text())
        if is_change_name or is_change_value or is_change_format:
            self.legal_units.save()
            self.legal_units.window.update_information_fields()
        self.legal_units.window.information_fields_window = None

    def check_format(self):
        if self.set_text_format.isChecked():
            return 'text'
        if self.set_date_format.isChecked():
            return 'date'
        if self.set_combo_format.isChecked():
            return 'combo'

    def change_format(self, format):
        name = self.information_field.name
        category = self.category
        self.legal_units.changes_format_sample_information_fields(category, name, format)

    def change_value(self, new_value):
        if self.information_field.format == 'combo':
            self.legal_units.combo_information_fields[self.category][self.information_field.name] = new_value
            self.legal_units.changes_sample(self.category)
            return
        self.information_field.edit_value = new_value

    def change_name(self, old_name, new_name):
        old_name = old_name.lower().strip()
        new_name = new_name.lower().strip()
        category = self.category
        self.legal_units.changes_name_sample_information_fields(category, old_name, new_name)
