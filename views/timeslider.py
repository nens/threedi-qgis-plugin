from qgis.PyQt.QtCore import pyqtSignal
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QSlider


class TimesliderWidget(QSlider):
    """QGIS Plugin Implementation."""

    datasource_changed = pyqtSignal()

    def __init__(self, iface, ts_datasources):
        """TimesliderWidget which allows the user to specify a timestamp of the current
        active datasource.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        :type ts_datasources: TimeseriesDatasourceModel
        """
        # Save reference to the QGIS interface
        super().__init__(Qt.Horizontal)

        self.iface = iface
        self.ts_datasources = ts_datasources
        self.active_ts_datasource = None
        # ^^^ TODO: the plugin itself also already has this variable, though
        # it doesn't seem to be used. Choose one spot.

        self.setEnabled(False)
        self.ts_datasources.dataChanged.connect(self.datasource_data_changed)
        self.ts_datasources.rowsInserted.connect(self.on_insert_datasource)
        self.ts_datasources.rowsRemoved.connect(self.on_remove_datasource)

    def on_insert_datasource(self, parent, start, end):
        """
        Set slider settings based on loaded netCDF. based on Qt addRows
        model trigger.

        Note:   for now only take first netCDF from list, todo: support more

        :param parent: parent of event (Qt parameter)
        :param start: first row nr
        :param end: last row nr
        """
        if self.ts_datasources.rowCount() > 0:
            self.setEnabled(True)
            datasource = self.ts_datasources.rows[0]
            if datasource != self.active_ts_datasource:

                self.timestamps = datasource.threedi_result().get_timestamps()
                self.min_value = self.timestamps[0]
                self.max_value = self.timestamps[-1]
                self.interval = self.timestamps[1] - self.timestamps[0]
                self.nr_values = len(self.timestamps)

                self.setMaximum(self.nr_values - 1)
                self.setMinimum(0)
                self.setTickPosition(QSlider.TicksBelow)
                self.setTickInterval(1)
                self.setSingleStep(1)
                self.active_ts_datasource = datasource
                self.setValue(0)
                self.datasource_changed.emit()
        else:
            self.setMaximum(1)
            self.setValue(0)
            self.setEnabled(False)
            self.active_ts_datasource = None

    def on_remove_datasource(self, index, start, end):
        """
        Set slider settings based on loaded netCDF. based on Qt model
        removeRows trigger
        :param index: Qt Index (not used)
        :param start: first row nr
        :param end: last row nr
        """
        # for now: try to init first netCDF
        self.on_insert_datasource(None, None, None)

    def datasource_data_changed(self, index):
        """
        Set slider settings based on loaded netCDF. based on Qt
        data change trigger
        :param index: index of changed field
        """
        # for now: try to init first netCDF
        self.on_insert_datasource(None, None, None)

    def index_to_duration(self, index):
        """Return the duration between start of simulation and the selected time index

        Duration is returned as a tuple (days, hours, minutes) of the current active
        datasource, rounded down.

        Args:
            index (int): time index of the current selected datasource

        Returns:
            tuple days, hours, minutes

        """
        selected_timestamp = int(self.timestamps[index])
        days = selected_timestamp // 86400
        hours = (selected_timestamp // 3600) % 24
        minutes = (selected_timestamp // 60) % 60
        return days, hours, minutes
