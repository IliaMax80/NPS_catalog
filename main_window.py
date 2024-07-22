import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from ui.ui_main_window import UiMainWindow
from legal_units import ContainerLegalUnits, Worker, Car
from excel_tools import import_table_worker, export_table_to_excel
from dialog_window_tools import confirm_saving, open_line_edit_window, open_confing_categories_window
from tables import UserTableModel, GeneralTableModel
from legal_unit_windows import WorkerWindow, CarWindow
from document_controller import DocumentController

# conver command: pyinstaller C:\Users\днс\Desktop\NPS_maxi\code\main_window.py
# TODO: Доработать конструктор для заполнения документов
# TODO: Дорабоать документы
# TODO: Сделать умную систему сохранения

FILE_WORKERS = "data_workers.json"
FILE_SETTINGS_WORKERS = 'settings_table_workers.json'
FILE_CARS = 'data_cars.json'
FILE_SETTINGS_CARS = 'settings_table_cars.json'
FILE_GENERAL_TABLE = 'general_table.json'


class MainWindow(QMainWindow, UiMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model_general_table = GeneralTableModel(self.general_table, FILE_GENERAL_TABLE)

        self.workers = ContainerLegalUnits(Worker, FILE_WORKERS, WorkerWindow)
        self.model_table_workers = UserTableModel(self.workers, self.table_worker, self, FILE_SETTINGS_WORKERS)
        self.import_excel_worker.clicked.connect(self.set_worker_from_excel)
        self.switching_mode_table_worker.clicked.connect(
            lambda: self.model_table_workers.switching_mode(self.switching_mode_table_worker))
        self.add_worker_button.clicked.connect(self.add_worker)
        self.add_worker_categories_command.triggered.connect(self.workers.open_window_add_categories)
        self.remove_worker_categories_command.triggered.connect(
            lambda: self.workers.open_window_remove_categories(self))
        self.export_excel_worker.clicked.connect(lambda: self.export_excel_table(self.model_table_workers))
        self.settings_table_worker.clicked.connect(self.model_table_workers.open_settings)

        self.cars = ContainerLegalUnits(Car, FILE_CARS, CarWindow)
        self.model_table_cars = UserTableModel(self.cars, self.table_car, self, FILE_SETTINGS_CARS)
        self.switching_mode_table_car.clicked.connect(
            lambda: self.model_table_cars.switching_mode(self.switching_mode_table_car))
        self.add_car_button.clicked.connect(self.add_car)
        self.add_car_categories_command.triggered.connect(self.cars.open_window_add_categories)
        self.remove_car_categories_command.triggered.connect(
            lambda: self.cars.open_window_remove_categories(self))
        self.settings_table_car.clicked.connect(self.model_table_cars.open_settings)
        self.temp = None

        self.document_controller = DocumentController()

        self.remove_value_command.triggered.connect(self.model_general_table.remove_value)
        self.remove_group_command.triggered.connect(self.model_general_table.remove_group)

        self.add_value_command.triggered.connect(self.model_general_table.add_value)
        self.add_group_command.triggered.connect(self.model_general_table.add_group)

    def set_worker_from_excel(self):
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        import_table_worker(self.workers, path)

    def save_stage(self, next_function, cancel=None):
        is_dont_change_worker = self.model_table_workers.is_table_change()
        is_dont_change = any([is_dont_change_worker])
        if is_dont_change:
            def save():
                if is_dont_change_worker:
                    self.model_table_workers.save_change()
                next_function()

            confirm_saving(window=self,
                           text='Сохранить изменения перед выходом?',
                           save=save,
                           dont_save=next_function,
                           cancel=cancel)
        else:
            next_function()

    def closeEvent(self, event):
        def close():
            self.workers.save()
            self.cars.save()
            self.model_general_table.save()
            event.accept()

        self.save_stage(close, lambda: event.ignore())

    def add_worker(self):
        def check_categories(categories):
            print(categories)
            return len(categories) == 1

        def check_id(id):
            if id:
                if id not in list(self.workers.all_legal_units.keys()):
                    return True
            return False

        def set_categories(categories, id):
            self.temp = None
            self.workers.add_legal_unit(categories[0], id)
            self.workers.open_window_legal_unit(id)
            self.workers.table.update()
            self.workers.save()

        def set_id(id):
            self.temp = open_confing_categories_window(None,
                                                       self.workers,
                                                       set_categories,
                                                       id,
                                                       check=check_categories,
                                                       is_one=True)

        self.temp = open_line_edit_window(text='Введите табельный номер сотрудника',
                                          title='Создания нового сотрудника',
                                          function=set_id,
                                          check=check_id)
    def export_excel_table(self, model_table):
        file = QtWidgets.QFileDialog.getSaveFileName()[0]
        export_table_to_excel(file, model_table)
    def add_car(self):
        def check_categories(categories):
            print(categories)
            return len(categories) == 1

        def check_number(number):
            if number:
                if number not in list(self.cars.all_legal_units.keys()):
                    return True
            return False

        def set_categories(categories, id):
            self.temp = None
            self.cars.add_legal_unit(categories[0], id)
            self.cars.get_property(id, 'гос номер').value = id
            self.cars.open_window_legal_unit(id)
            self.cars.table.update()
            self.cars.save()

        def set_id(id):
            self.temp = open_confing_categories_window(None,
                                                       self.cars,
                                                       set_categories,
                                                       id,
                                                       check=check_categories,
                                                       is_one=True)

        self.temp = open_line_edit_window(text='Введите гос номер транспортного средства',
                                          title='Создания нового транспортного средства',
                                          function=set_id,
                                          check=check_number)
    def set_path_folder_dicuments(self):
        folder = QtWidgets.QFileDialog.getOpenFileName()[0]
        self.document_controller.set_path_foldr_document(folder)

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    sys.excepthook = except_hook
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
