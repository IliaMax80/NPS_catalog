from abc import ABC, abstractmethod
from datetime import datetime, date


class InformationField(ABC):
    @abstractmethod
    def __init__(self, name, format_fields, legal_unit):
        self.name = name
        self.format = format_fields
        self.legal_unit = legal_unit

    @property
    def edit_value(self):
        return self.value

    @edit_value.setter
    def edit_value(self, value):
        self.value = value

    @property
    @abstractmethod
    def value(self):
        pass

    @value.setter
    @abstractmethod
    def value(self, value):
        pass

    @staticmethod
    def create_information_field(name, format_field, legal_unit):
        information_field = None
        arg = name, legal_unit
        if format_field == 'text':
            information_field = TextInformationField(*arg)
        if format_field == 'date':
            information_field = DateInformationField(*arg)
        if format_field == 'combo':
            information_field = ComboInformationField(*arg)
        return information_field


class TextInformationField(InformationField):
    def __init__(self, name, legal_unit):
        self._value: str = ""
        super().__init__(name, 'text', legal_unit)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class DateInformationField(InformationField):
    def __init__(self, name, legal_unit):
        self._value: date = date.today()
        super().__init__(name, 'date', legal_unit)

    @property
    def value(self):
        return self._value.strftime('%d.%m.%Y')

    @value.setter
    def value(self, value):
        dt = datetime.strptime(value, '%d.%m.%Y')
        self._value = date(dt.year, dt.month, dt.day)


class ComboInformationField(InformationField):
    def __init__(self, name, legal_unit):
        self.format_text = None
        self._value = None
        super().__init__(name, 'combo', legal_unit)

    # get value
    @property
    def value(self):
        if not self.format_text:
            self.format_text = ComboInformationField.text_formatting(self._value)
        return ComboInformationField.build_value(self.format_text, self.legal_unit)

    # set value - impossible operation
    @value.setter
    def value(self, value):
        print(f'impossible {self.name}.value = {value}')
        pass

    # get format value for change in information window
    @property
    def edit_value(self):
        return self._value

    # set format value
    @edit_value.setter
    def edit_value(self, value):
        print(value)
        self._value = value
        self.format_text = ComboInformationField.text_formatting(self._value)

    @staticmethod
    def build_value(format_text, legal_unit):
        text = ''
        for fragment, is_property in format_text:
            if is_property:
                text += legal_unit.get_property(fragment).value
            else:
                text += fragment
        return text

    @staticmethod
    def text_formatting(text):
        if not text:
            return [('', False)]
        format_text = []
        for fragment in text.split('>'):
            if '<' in fragment:
                word, name = fragment.split('<')
                format_text.append((word, False))
                format_text.append((name, True))
            else:
                format_text.append((fragment, False))
        return format_text


class TemporaryInformationField:
    def __init__(self, text):
        self._value = text

    @property
    def value(self):
        return self._value


class Documents:
    def __init__(self, name, short_name, validity_period, path_folder):
        self.name = name
        self.short_name = short_name
        self.validity_period = validity_period
        self.path_folder = path_folder
        self.path = ''
        self.validity = None
        self.date_of_issue = None

    def set_options(self, data_of_issue, validity, path):
        self.date_of_issue = data_of_issue
        self.validity = validity
        self.path = path

    @property
    def dict_properties(self):
        properties = {'data_of_issue': self.date_of_issue, 'validity': self.validity, 'path': self.path}
        return properties

    @dict_properties.setter
    def dict_properties(self, properties):
        self.date_of_issue = properties['data_of_issue']
        self.validity = properties['validity']
        self.path = properties['path']
