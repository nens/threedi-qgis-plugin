import os
import copy

import ogr
from pyspatialite import dbapi2
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .sqlalchemy_add_columns import create_and_upgrade
from ThreeDiToolbox.sql_models.model_schematisation import Base


class ThreediDatabase(object):

    def __init__(self, connection_settings, db_type='sqlite', echo=False):
        """

        :param connection_settings:
        db_type (str choice): database type. 'sqlite' and 'postgresql' are supported
        """
        self.settings = connection_settings
        self.db_type = db_type
        self.echo = echo

        self._engine = None
        self._combined_base = None
        self._base = None

    def create_and_check_fields(self):

        create_and_upgrade(self.engine, self.get_base().metadata)

    def create_db(self, overwrite=False):
        if self.db_type == 'sqlite':

            if overwrite and os.path.isfile(self.settings['db_file']):
                os.remove(self.settings['db_file'])

            drv = ogr.GetDriverByName('SQLite')
            db = drv.CreateDataSource(self.settings['db_file'],
                                      ["SPATIALITE=YES"])
            Base.metadata.create_all(self.engine)

            #todo: add settings to improve database creation speed for older versions of gdal

    @property
    def engine(self):
        if self._engine is None:
            if self.db_type == 'sqlite':
                self._engine = create_engine('sqlite:///{0}'.format(
                                                self.settings['db_file']),
                                             module=dbapi2,
                                             echo=self.echo)
            elif self.db_type == 'postgres':
                con = "postgresql://{username}:{password}@{host}:{port}/{database}".format(**self.settings)

                self._engine = create_engine(con,
                                             echo=self.echo)

        return self._engine

    def get_base(self, including_existing_tables=True):

        if including_existing_tables:
            if self._combined_base is None:
                self._combined_base = copy.deepcopy(Base)
                self._combined_base.metadata.bind = self.engine
                self._combined_base.metadata.reflect(extend_existing=True)
            return self._combined_base
        else:
            if self._base is None:
                self._base = copy.deepcopy(Base)
            return self._base

    def get_session(self):
        return sessionmaker(bind=self.engine)()
