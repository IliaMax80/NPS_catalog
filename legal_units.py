from PyQt5.QtWidgets import QMessageBox

from legal_unit_properties import InformationField, ComboInformationField, TemporaryInformationField, Documents
from json_controllers import LegalUnitsJson
from dialog_window_tools import open_confing_categories_window, open_line_edit_window


class LegalUnit():
    def __init__(self, id):
        self.id = id
        self._information_fields = {}
        self._combo_information_fields = {}
        self._documents = {}

    @property
    def title(self):
        return self.id

    @property
    def name_user_id(self):
        return

    def availability_check(self, names):
        for name in names:
            if not self.get_property(name):
                return False
        return True

    def request(self, names, key=lambda x: x):
        return dict([(name, key(self.get_property(name))) for name in names])

    def get_property(self, name):
        if '<' in name:
            format_text = ComboInformationField.text_formatting(name)
            text = ComboInformationField.build_value(format_text, self)
            information_field = TemporaryInformationField(text)
            return information_field
        if name in self._information_fields.keys():
            return self._information_fields[name]
        if name in self._combo_information_fields.keys():
            return self._combo_information_fields[name]
        if name in self._documents.keys():
            return self._documents[name]
        return TemporaryInformationField('Отсуствует')

    @property
    def sample_documents(self):
        def get_property(documents):
            return {'name': documents.name,
                    'short_name': documents.short_name,
                    'validity_period': documents.validity_period,
                    'path_folder': documents.path_folder}
        return dict([(name, get_property(documents)) for name, documents in self._documents.items()])

    @sample_documents.setter
    def sample_documents(self, sample):
        self._documents = dict([(name, Documents(*list(properties))) for name, properties in sample.items()])

    @property
    def sample_information_fields(self):
        items = [(name, field.format) for name, field in self._information_fields.items()]
        items += [(name, field.format) for name, field in self._combo_information_fields.items()]
        sample_information_fields = {}
        for name, format in items:
            sample_information_fields[name] = format
        return sample_information_fields

    def update_property(self):
        return

    @sample_information_fields.setter
    def sample_information_fields(self, sample):
        information_fields = {}
        for name, format in sample.items():
            information_fields[name] = InformationField.create_information_field(name, format, self)
        self._information_fields = dict(
            [(name, field) for name, field in information_fields.items() if field.format != 'combo'])
        self._combo_information_fields = dict(
            [(name, field) for name, field in information_fields.items() if field.format == 'combo'])

    @property
    def value_information_fields(self, include_combo_fields=False):
        return dict([(name, field.value) for name, field in self._information_fields.items()])

    @property
    def value_documents(self):
        return dict([(name, document.dict_properties) for name, document in self._documents.items()])

    @value_documents.setter
    def value_documents(self, information_fields):
        for name, value in information_fields.items():
            if self._information_fields.get(name):
                self._information_fields[name].dict_properties = value

    @value_information_fields.setter
    def value_information_fields(self, information_fields):
        for name, value in information_fields.items():
            if self._information_fields.get(name):
                self._information_fields[name].value = value
        self.update_property()

    # get value combo fields
    @property
    def value_combo_information_fields(self):
        return dict([(name, field.value) for name, field in self._combo_information_fields.items()])

    # set format combo information fields
    @value_combo_information_fields.setter
    def value_combo_information_fields(self, combo_information_fields):
        for name, format_text in combo_information_fields.items():
            if self._combo_information_fields.get(name):
                self._combo_information_fields[name].edit_value = format_text

    def update_sample_information_fields(self, sample, name=None, new_name=None):
        information_fields = self.value_information_fields
        if name and new_name:
            information_fields[new_name] = information_fields[name]
        self.sample_information_fields = sample
        self.value_information_fields = information_fields

    def update_sample_documents(self, sample):
        documents = self.value_documents
        self.sample_documents = sample
        self.value_documents = documents

    @property
    def dict(self):
        legal_unit = {'information_fields': self.value_information_fields, 'documents': self.value_documents}
        return legal_unit

    @dict.setter
    def dict(self, legal_unit):
        self.value_information_fields = legal_unit['information_fields']
        self.value_documents = legal_unit['documents']


class Car(LegalUnit):
    def __init__(self, number):
        self.number = None
        super().__init__(number)
        if self.get_property('гос номер').value != 'Отсуствует':
            self.get_property('гос номер').value = number

    def update_property(self):
        self.number = self.get_property('гос номер').value

    @property
    def name_user_id(self):
        return 'гос номер'

    def title(self):
        return f'{self.number}'


class Worker(LegalUnit):
    def __init__(self, id):
        self.full_name = None
        self.post = None
        super().__init__(id)

    @property
    def name_user_id(self):
        return 'фио'

    def update_property(self):
        self.full_name = self.get_property('фио').value
        self.post = self.get_property('должность').value

    @property
    def title(self):
        return f'{self.full_name}'


class ContainerLegalUnits():
    def __init__(self, legal_unit_class, path, window_class):
        self.json_controller = LegalUnitsJson(self, path)
        self.window_class = window_class
        self.legal_unit_class = legal_unit_class
        self.categories_legal_units = {}
        self.sample_information_fields = {}
        self.sample_documents = {}
        self.combo_information_fields = {}
        self.json_controller.import_data()
        self.table = None
        self.window = None

    @property
    def categories(self):
        return list(self.categories_legal_units.keys())

    # export sample categories in json
    def get_categories_sample(self):
        return self.categories, self.sample_information_fields, self.sample_documents, self.combo_information_fields

    # sample categories import
    def set_categories_sample(self, category, sample_information_fields, sample_documents, combo_information_fields):
        self.sample_information_fields = sample_information_fields
        self.sample_documents = sample_documents
        self.combo_information_fields = combo_information_fields
        self.categories_legal_units = dict((i, {}) for i in category)

    def changes_format_sample_information_fields(self, category, name, new_format):
        self.sample_information_fields[category][name] = new_format
        self.changes_sample(category)

    def changes_name_sample_information_fields(self, category, name, new_name):
        sample = {}
        for key, value in self.sample_information_fields[category].items():
            sample[key if key != name else new_name] = value
        self.sample_information_fields[category] = sample
        for legal_unit in self.categories_legal_units[category].values():
            value = legal_unit.value_information_fields
            value[new_name] = value[name]
            legal_unit.update_sample_information_fields(sample)
            legal_unit.value_information_fields = value
        if self.table:
            self.table.update()
        if self.window:
            self.window.update_information_fields()

    def set_sample_information_fields(self, category, sample):
        self.sample_information_fields[category] = sample
        self.changes_sample(category=category)

    def set_sample_documents(self, category, sample):
        self.sample_documents[category] = sample
        self.changes_sample(category=category)

    def get_dict_legal_units(self, category):
        return dict([(id, legal_unit.dict) for id, legal_unit in self.categories_legal_units[category].items()])

    def set_dict_legal_units(self, category, dict_legal_units):
        legal_units = {}
        for id, dict_legal_unit in dict_legal_units.items():
            legal_units[id] = self.legal_unit_class(id)
            # set sample field, document, combo_field(in sample_information_fielsds)
            legal_units[id].sample_documents = self.sample_documents[category]
            legal_units[id].sample_information_fields = self.sample_information_fields[category]
            # set values combo, field
            legal_units[id].value_combo_information_fields = self.combo_information_fields[category]
            # set values document, field in dict_legal_unit
            legal_units[id].dict = dict_legal_unit

        self.categories_legal_units[category] = legal_units

    def get_property(self, id_legal_unit, name_property):
        return self.get_legal_unit(id_legal_unit=id_legal_unit).get_property(name_property)

    def is_category(self, category):
        return category in self.categories_legal_units.keys()

    def add_category(self, category):
        if not self.is_category(category):
            self.sample_information_fields[category] = {}
            self.sample_documents[category] = {}
            self.categories_legal_units[category] = {}

    def add_sample_information_field_in_category(self, category, name, format):
        pass

    def add_sample_information_fields_category(self, category, sample_information_fields, update=True):
        for name, format in sample_information_fields.items():
            self.sample_information_fields[category][name] = format
        if update:
            self.changes_sample(category)

    # soft_set
    def append_data_legal_unit(self, category, id_legal_unit, dict_information_fields, dict_document):
        if not self.is_legal_unit(category, id_legal_unit):
            self.add_legal_unit(category, id_legal_unit)
        legal_unit = self.get_legal_unit(category, id_legal_unit)
        value_information_fields = legal_unit.value_information_fields
        for name, value in dict_information_fields.items():
            value_information_fields[name] = value
        legal_unit.value_information_fields = value_information_fields
        # value_documents = legal_unit.value_documents
        # for name, value in dict_document.items():
        #   value_document[name] = value
        # legal_unit.value_documents = value_documents

        self.window = None

    def add_legal_unit(self, category, id_legal_unit):
        self.categories_legal_units[category][id_legal_unit] = self.legal_unit_class(id_legal_unit)
        self.changes_sample(category, id_legal_unit)
        # documents

    def is_legal_unit(self, category=None, id_legal_unit=None):
        if category:
            return id_legal_unit in self.categories_legal_units[category].keys()
        else:
            return id_legal_unit in self.all_legal_units.keys()

    def get_id_legal_unit(self, categories=None, sort=None):
        if sort:
            name = sort[0]
            foo = sort[1]
            legal_units = self.get_all_legal_units(categories).values()
            return [i.id for i in sorted(legal_units, key=lambda x: foo(x.get_property(name).value))]
        return [i.id for i in self.get_all_legal_units(categories)]

    @property
    def all_legal_units(self):
        return self.get_all_legal_units()

    def get_all_legal_units(self, categories=None):
        list_legal_units = []
        for category, category_legal_units in self.categories_legal_units.items():
            if (not categories) or (category in categories):
                list_legal_units += list(category_legal_units.items())
        return dict(list_legal_units)

    def get_category(self, id_legal_unit):
        for category, legal_units in self.categories_legal_units.items():
            if id_legal_unit in legal_units.keys():
                return category
        return None

    def get_legal_unit(self, category=None, id_legal_unit=None) -> LegalUnit:
        category = category or self.get_category(id_legal_unit)
        return self.categories_legal_units[category][id_legal_unit]

    def changes_sample(self, category=None, id_legal_unit=None):
        if id_legal_unit:
            category = category or self.get_category(id_legal_unit)
            sample_fields = self.sample_information_fields[category]
            sample_documents = self.sample_documents[category]
            combo_fields = self.combo_information_fields[category]
            self.categories_legal_units[category][id_legal_unit].update_sample_information_fields(sample_fields)
            self.categories_legal_units[category][id_legal_unit].update_sample_documents(sample_documents)
            self.categories_legal_units[category][id_legal_unit].value_combo_information_fields = combo_fields
            return
        if category:
            sample_fields = self.sample_information_fields[category]
            combo_fields = self.combo_information_fields[category]
            sample_documents = self.sample_documents[category]
            for legal_unit in self.categories_legal_units[category].values():
                legal_unit.update_sample_information_fields(sample_fields)
                legal_unit.update_sample_documents(sample_documents)
                legal_unit.value_combo_information_fields = combo_fields
        else:
            for category, sample_fields in self.sample_information_fields.items():
                combo_fields = self.combo_information_fields[category]
                sample_documents = self.sample_documents[category]
                for legal_unit in self.categories_legal_units[category].values():
                    legal_unit.update_sample_information_fields(sample_fields)
                    legal_unit.update_sample_documents(sample_documents)
                    legal_unit.value_combo_information_fields = combo_fields

        if self.table:
            self.table.update()
        if self.window:
            self.window.update_information_fields()

    def open_window_legal_unit(self, id_legal_unit):
        self.window = self.window_class(legal_unit=self.get_legal_unit(id_legal_unit=id_legal_unit),
                                        category=self.get_category(id_legal_unit),
                                        legal_units=self)
        self.window.show()

    def open_window_add_categories(self):
        def check_name(name):
            if name:
                if name.lower() not in [i.lower() for i in self.categories]:
                    return True
            return False

        def set_name(name):
            self.temp = open_confing_categories_window(None, self, set_catigories, name,
                                                       check=lambda x: True)

        def set_catigories(catigories, new_category):
            self.add_category(new_category)
            for category in catigories:
                for name, format in self.sample_information_fields[category].items():
                    self.sample_information_fields[new_category][name] = format
            self.save()

        self.temp = open_line_edit_window('Введите названия новой категории', 'Создания новой категории',
                                          set_name, check=check_name)

    def open_window_remove_categories(self, window):
        def check_categories(categories):
            return len(categories) == 1

        def set_categories(categories):
            category = categories[0]
            dialog = QMessageBox(window)
            text = 'Удаление категории, сотрет без возможности востановления все'
            text += ' едениици принадлежащих данной категории.'
            dialog.setInformativeText('Потвердить действия?')
            dialog.setText(text)
            dialog.setWindowTitle('Удаления категории')
            dialog.setStandardButtons(QMessageBox.StandardButton.No | QMessageBox.StandardButton.Yes)
            dialog.setDefaultButton(QMessageBox.StandardButton.No)
            if dialog.exec() != QMessageBox.StandardButton.Yes:
                return
            self.sample_information_fields.pop(category)
            self.sample_documents.pop(category)
            self.categories_legal_units.pop(category)
            self.save()

        self.temp = open_confing_categories_window(None, self, set_categories,
                                                   check=check_categories, is_one=True)

    def save(self):
        self.json_controller.export_data()
