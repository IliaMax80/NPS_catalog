import os

from json_controllers import JsonControl

PATH_DOCUMENT_CONTROLLER = 'settings_document_controller.json'

class DocumentController():
    def __init__(self):
        self.json_control = JsonControl(PATH_DOCUMENT_CONTROLLER)
        data = self.json_control.get_file()
        self.custom_settings = data.get('custom_settings', False)
        self.path_folder_document = data.get('path_folder_document', os.getcwd())

    def set_path_foldr_document(self, new_path):
        self.path_folder_document = new_path
        self.custom_settings = True
        self.save()

    def save(self):
        data = {'custom_settings': self.custom_settings, 'path_folder_document': self.path_folder_document}
        self.json_control.set_file(data)
