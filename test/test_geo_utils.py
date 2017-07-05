"""
Test geo utils.
"""
import unittest

from qgis.core import QgsVectorLayer
from qgis.core import QgsPoint

from ThreeDiToolbox.utils.geo_utils import get_distance
from ThreeDiToolbox.utils.geo_utils import get_epsg_code_from_layer
from ThreeDiToolbox.utils.geo_utils import get_coord_transformation_instance


class TestGeoUtils(unittest.TestCase):

    def test_it_can_get_epsg_code_from_layer(self):
        crs = 'EPSG:28992'
        pnt_layer = QgsVectorLayer(
            "Point?crs=" + crs, "temp_connected_pnt", "memory"
        )
        epsg_code = get_epsg_code_from_layer(pnt_layer)
        self.assertEqual(epsg_code, 28992)

    def test_it_can_get_coord_transformation_instance(self):
        src_epsg, dest_epsg = 4326, 28992
        inst = get_coord_transformation_instance(src_epsg, dest_epsg)
        self.assertEqual(
            str(inst.__class__), "<class 'qgis._core.QgsCoordinateTransform'>"
        )
        self.assertEqual(inst.destCRS().authid(), 'EPSG:28992')
        src_epsg, dest_epsg = 28992, 4326
        inst_rev = get_coord_transformation_instance(src_epsg, dest_epsg)
        self.assertEqual(inst_rev.destCRS().authid(), 'EPSG:4326')

    def test_it_can_get_distance_between_points(self):
        pnt, pnt1 = QgsPoint(0, 0), QgsPoint(0, 10)
        dist = get_distance(pnt, pnt1, 4326)
        self.assertEqual(dist, 1105854.8332357334)
        dist = get_distance(pnt, pnt1, 28992)
        self.assertEqual(dist, 10.)
