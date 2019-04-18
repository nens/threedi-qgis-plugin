from . import models
from . import constants

from sqlalchemy import func


class ModelSchema:
    def __init__(self, threedi_db, declared_models=models.DECLARED_MODELS):
        self.db = threedi_db
        self.declared_models = declared_models
        if not self.is_latest_migration():
            print("WARNING: model is not the latest migration!")

    def is_latest_migration(self):
        """Return if the database contains the latest migration"""
        session = self.db.get_session()
        latest_migration_id = session.query(
            func.max(models.SouthMigrationHistory.id)
        ).scalar()
        latest_migration_name = session.query(
            models.SouthMigrationHistory.migration).filter(
            models.SouthMigrationHistory.id == latest_migration_id
        ).scalar()
        return (latest_migration_id == constants.LATEST_MIGRATION_ID
                and latest_migration_name == constants.LATEST_MIGRATION_NAME)

    def get_missing_tables(self):
        pass

    def get_missing_columns(self):
        pass
