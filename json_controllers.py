import json
import os


class JsonControl:
    def __init__(self, path):
        self.path = path

    def get_file(self):
        if not os.path.isfile(self.path):
            return {}
        with open(self.path, "r") as read_file:
            data = json.load(read_file)
        return data

    def set_file(self, data):
        with open(self.path, "w") as write_file:
            json.dump(data, write_file)


class LegalUnitsJson(JsonControl):
    def __init__(self, legal_units, path):
        super().__init__(path)
        self.legal_units = legal_units

    def export_data(self):
        data = {}
        temp = self.legal_units.get_categories_sample()
        categories, sample_information_fields, sample_documents, combo_information_fields = temp
        for category in categories:
            data[category] = {}
            data[category]['sample_information_fields'] = sample_information_fields[category]
            data[category]['combo_information_fields'] = combo_information_fields[category]
            data[category]['sample_documents'] = sample_documents[category]
            data[category]['legal_units'] = self.legal_units.get_dict_legal_units(category)
        print(data)
        self.set_file(data)

    def import_data(self):
        data = self.get_file()
        sample_information_fields = {}
        sample_documents = {}
        combo_information_fields = {}
        categories_dict_legal_units = {}
        categories = []
        for category, category_data in data.items():
            categories.append(category)
            sample_information_fields[category] = category_data['sample_information_fields']
            sample_documents[category] = category_data.get('sample_documents', {})
            categories_dict_legal_units[category] = category_data['legal_units']
            combo_information_fields[category] = category_data.get('combo_information_fields', {})

        self.legal_units.set_categories_sample(categories, sample_information_fields, sample_documents,
                                               combo_information_fields)
        for category in categories:
            self.legal_units.set_dict_legal_units(category, categories_dict_legal_units[category])
