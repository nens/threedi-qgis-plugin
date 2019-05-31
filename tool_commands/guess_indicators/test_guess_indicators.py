from tool_commands.guess_indicators.guess_indicators_utils import Guesser
from ThreeDiToolbox.utils.threedi_database import ThreediDatabase
from ThreeDiToolbox.test.test_init import TEST_DATA_DIR
import os
import unittest.mock


class TestGuessser(unittest.TestCase):
    """Test the QGIS Environment"""

    def setUp(self):
        sqlite_filename = "v2_bergermeer.sqlite"
        self.test_sqlite_path = os.path.join(TEST_DATA_DIR, 'testmodel', sqlite_filename)
        db_type = "spatialite"
        db_set = {"db_path": self.test_sqlite_path}
        db = ThreediDatabase(db_set, db_type)
        self.guesser = Guesser(db)

    def test_xxx(self):
        pass
