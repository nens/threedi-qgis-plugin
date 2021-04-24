from qgis.PyQt.QtCore import Qt
from ThreeDiToolbox.tool_sideview.sideview_view import SideViewDockWidget

import qgis


class ThreeDiSideView(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface, tdi_root_tool):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        :param tdi_root_tool: 3Di root tool instance
        :type tdi_root_tool: ThreeDiPlugin
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.tdi_root_tool = tdi_root_tool

        self.icon_path = ":/plugins/ThreeDiToolbox/icons/icon_route.png"
        self.menu_text = u"Show sideview of 3Di model with results"

        self.dock_widgets = []
        self.widget_nr = 0
        self._active = False

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, activate):
        self._active = activate
        self.tdi_root_tool.update_slider_enabled_state()

    def on_unload(self):
        """
        on close of graph plugin
        """
        for widget in self.dock_widgets:
            widget.close()

    def on_close_child_widget(self, widget_nr):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        nr = None

        # find widget based on nr
        for i in range(0, len(self.dock_widgets)):
            widget = self.dock_widgets[i]
            if widget.nr == widget_nr:
                nr = i

        # close widget
        if nr is not None:
            widget = self.dock_widgets[nr]
            widget.closingWidget.disconnect(self.on_close_child_widget)

            del self.dock_widgets[nr]

        self.active = False

    def run(self):
        """
        Run method that loads and starts the plugin (docked graph widget)
        """
        # create the dockwidget
        self.widget_nr += 1
        new_widget = SideViewDockWidget(
            self.iface,
            parent_class=self,
            nr=self.widget_nr,
            tdi_root_tool=self.tdi_root_tool,
        )
        self.dock_widgets.append(new_widget)

        # connect cleanup on closing of dockwidget
        new_widget.closingWidget.connect(self.on_close_child_widget)

        # show the dockwidget
        self.iface.addDockWidget(Qt.BottomDockWidgetArea, new_widget)

        # make stack of graph widgets (instead of next to each other)
        if len(self.dock_widgets) > 1:
            window = qgis.core.QgsApplication.activeWindow()
            window.tabifyDockWidget(self.dock_widgets[0], new_widget)

        # activate timeslider
        self.active = True

        new_widget.show()
