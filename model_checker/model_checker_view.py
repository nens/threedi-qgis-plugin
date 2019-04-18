import os
import collections

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog
from qgis.PyQt.QtCore import QSettings

from .model_checker_dialog import Ui_Dialog
from ThreeDiToolbox.utils.threedi_database import get_databases, \
    ThreediDatabase

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), 'model_checker_dialog.ui')
)


class ModelCheckerDialogWidget(QDialog, FORM_CLASS):
    def __init__(self, iface, command):
        super(ModelCheckerDialogWidget, self).__init__()
        self.setupUi(self)
        self.iface = iface
        self.command = command
        self.available_databases = get_databases()

        self.database_combobox.addItems(list(self.available_databases.keys()))
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.on_cancel)

    def on_accept(self):
        selected_database_key = self.database_combobox.currentText()
        selected_db = self.available_databases.get(selected_database_key)
        db_type = selected_db.get('db_type')
        connection_settings = selected_db.get('db_settings')

        threedi_db = ThreediDatabase(connection_settings, db_type=db_type)
        self.command.run_it(threedi_db)
        print('accept!')

    def on_cancel(self):
        print('reject!')