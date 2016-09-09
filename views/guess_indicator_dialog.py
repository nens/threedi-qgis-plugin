# -*- coding: utf-8 -*-
import os
from PyQt4.QtCore import pyqtSignal, QSettings
from PyQt4.QtGui import QDialog
from PyQt4.QtSql import QSqlDatabase
from PyQt4 import uic

from PyQt4.QtCore import SIGNAL, QRect, Qt, QObject, QMetaObject
from PyQt4.QtGui import (
    QVBoxLayout, QGroupBox, QWidget, QComboBox, QSizePolicy, QHBoxLayout,
    QCheckBox, QDialogButtonBox, QApplication)

from qgis.core import QgsDataSourceURI, QgsVectorLayer, QgsMapLayerRegistry
from qgis.gui import QgsCredentialDialog


try:
    _encoding = QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)


class GuessIndicatorDialogWidget(QDialog):

    def __init__(self, parent=None, checks=[],
                 command=None):
        """Constructor

        Args:
            parent: Qt parent Widget
            iface: QGiS interface
            ts_datasource: TimeseriesDatasourceModel instance
            command: Command instance with a run_it method which will be called
                     on acceptance of the dialog
        """
        super(GuessIndicatorDialogWidget, self).__init__(parent)
        self.checks = checks
        self.setupUi(checks)

        self.command = command

        self.databases = self.get_databases()
        self.database_combo.addItems(self.databases.keys())

        # Connect signals
        self.buttonBox.accepted.connect(self.on_accept)
        self.buttonBox.rejected.connect(self.on_reject)

        self.filename = None

    def on_accept(self):
        """Accept and run the Command.run_it method."""


        db_key = self.database_combo.currentText()

        settings = self.databases[db_key]
        db_set = settings['db_settings']

        if settings['db_type'] == 'sqlite':
            pass
        else:  # postgres

            successful_connection = False

            uname = db_set['username']
            passwd = db_set['password']
            msg = 'Log in'

            while not successful_connection:

                uri = QgsDataSourceURI()
                uri.setConnection(db_set['host'],
                                  db_set['port'],
                                  db_set['database'],
                                  db_set['username'],
                                  db_set['password'])

                # try to connect
                # create a PostgreSQL connection using QSqlDatabase
                db = QSqlDatabase.addDatabase('QPSQL')
                # check to see if it is valid

                db.setHostName(uri.host())
                db.setDatabaseName(uri.database())
                db.setPort(int(uri.port()))
                db.setUserName(uri.username())
                db.setPassword(uri.password())

                # open (create) the connection
                if db.open():
                    successful_connection = True
                    break
                else:
                    # todo - provide feedback what is wrong
                    pass

                connInfo = uri.connectionInfo()
                (success, uname, passwd) = \
                    QgsCredentialDialog.instance().get(connInfo, uname, passwd, msg)

                if success:
                    db_set['username'] = passwd
                    db_set['password'] = uname
                else:
                    return

        checks = []

        if self.check_manhole_indicator.isChecked():
            checks.append('manhole_indicator')

        if self.check_pipe_friction.isChecked():
            checks.append('pipe_friction')

        if self.check_manhole_area.isChecked():
            checks.append('manhole_area')

        self.command.run_it(checks,
                            self.check_only_empty_fields.isChecked(),
                            db_set,
                            settings['db_type'])

        self.accept()

    def on_reject(self):
        """Cancel"""
        self.reject()
        print("Reject")

    def closeEvent(self, event):
        """
        Close widget, called by Qt on close
        :param event: QEvent, close event
        """

        self.buttonBox.accepted.disconnect(self.on_accept)
        self.buttonBox.rejected.disconnect(self.on_reject)

        event.accept()

    def get_databases(self):
        available_dbs = {}
        qs = QSettings()

        spatialite_keys = (k for k in qs.allKeys() if
                           k.startswith('SpatiaLite') and k.endswith('sqlitepath'))
        for k in spatialite_keys:
            db_name = k[23:-11]
            settings = {
                'key': k,
                'db_name': db_name,
                'combo_key': 'spatialite: {0}'.format(db_name),
                'db_type': 'sqlite',
                'db_settings': {
                    'db_path': qs.value(k)
                }
            }

            available_dbs[settings['combo_key']] = settings

        postgres_keys = (k for k in qs.allKeys() if k.startswith('PostgreSQL') and k.endswith('host'))
        for k in postgres_keys:
            db_name = k[23:-5]
            prefix = k[:-5]
            settings = {
                'key': k,
                'db_name': db_name,
                'combo_key': 'postgres: {0}'.format(db_name),
                'db_type': 'postgres',
                'db_settings': {
                    'host': qs.value(prefix + '/host'),
                    'port': qs.value(prefix + '/port'),
                    'database': qs.value(prefix + '/database'),
                    'username': qs.value(prefix + '/username'),
                    'password': qs.value(prefix + '/password'),
                }
            }

            if qs.value(prefix + '/saveUsername') == u'true':
                settings['saveUsername'] = True
                settings['db_settings']['username'] = qs.value(prefix + '/username')
            else:
                settings['saveUsername'] = False

            if qs.value(prefix + '/savePassword') == u'true':
                settings['savePassword'] = True
                settings['db_settings']['password'] = qs.value(prefix + '/password')
            else:
                settings['savePassword'] = False

            available_dbs[settings['combo_key']] = settings

        return available_dbs


    def setupUi(self, checks):


        self.resize(515, 250)
        self.verticalLayout = QVBoxLayout(self)

        # self.file_combo = QComboBox(self.horizontalLayoutWidget)
        # sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.file_combo.sizePolicy().hasHeightForWidth())
        # self.file_combo.setSizePolicy(sizePolicy)
        # self.file_combo.setObjectName("file_combo")
        # self.horizontalLayout.addWidget(self.file_combo)
        #
        # self.file_button = QPushButton(self.horizontalLayoutWidget)
        # self.file_button.setObjectName("file_button")
        # self.horizontalLayout.addWidget(self.file_button)


        self.groupBox_2 = QGroupBox(self)
        self.groupBox_2.setObjectName("groupBox_2")
        self.database_combo = QComboBox(self.groupBox_2)
        self.database_combo.setGeometry(QRect(10, 20, 481, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.database_combo.sizePolicy().hasHeightForWidth())
        self.database_combo.setSizePolicy(sizePolicy)
        self.database_combo.setObjectName("database_combo")
        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(self)
        self.verticalLayoutBox = QVBoxLayout(self.groupBox)

        self.check_pipe_friction = QCheckBox(self.groupBox)
        #self.check_pipe_friction.setGeometry(QRect(10, 20, 171, 17))
        self.check_pipe_friction.setChecked(True)
        self.verticalLayoutBox.addWidget(self.check_pipe_friction)

        self.check_manhole_indicator = QCheckBox(self.groupBox)
        # self.check_manhole_indicator.setGeometry(QRect(10, 20, 171, 17))
        self.check_manhole_indicator.setChecked(True)
        self.verticalLayoutBox.addWidget(self.check_manhole_indicator)

        self.check_manhole_area = QCheckBox(self.groupBox)
        # self.check_manhole_indicator.setGeometry(QRect(10, 20, 171, 17))
        self.check_manhole_area.setChecked(True)
        self.verticalLayoutBox.addWidget(self.check_manhole_area)

        self.verticalLayout.addWidget(self.groupBox)

        self.check_only_empty_fields = QCheckBox(self)
        # self.check_only_empty_fields.setGeometry(QRect(10, 40, 171, 17))
        self.check_only_empty_fields.setChecked(True)
        self.verticalLayout.addWidget(self.check_only_empty_fields)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi()
        QObject.connect(self.buttonBox, SIGNAL("accepted()"),
                               self.accept)
        QObject.connect(self.buttonBox, SIGNAL("rejected()"),
                               self.reject)
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(_translate("self", "Guess indicators", None))
        self.groupBox_2.setTitle(_translate("self", "Model schematisation database", None))

        self.groupBox.setTitle(_translate("Import_dialog", "Guess", None))
        self.check_pipe_friction.setText(_translate("Import_dialog", "Pipe friction", None))
        self.check_manhole_indicator.setText(_translate("Import_dialog", "Manhole indicator", None))
        self.check_only_empty_fields.setText(_translate("Import_dialog", "Only null fields", None))
        self.check_manhole_area.setText(_translate("Import_dialog", "Manhole area (only null fields)", None))
