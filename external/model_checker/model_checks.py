from itertools import chain

from sqlalchemy import func, types
from geoalchemy2.types import Geometry
from geoalchemy2 import functions as geo_func

from .schema_checks import ModelSchema
from . import models, model_errors, custom_types
from .model_errors import (NullColumnError, yield_model_errors)


def query_missing_foreign_key(session, origin_column, ref_column):
    """Check all values in origin_column are in ref_column.

    Null values are ignored.

    :param session: sqlalchemy.orm.session.Session
    :param origin_column: InstrumentedAttribute
    :param ref_column: InstrumentedAttribute
    :return: list of declared models instances of origin_column.class
    """
    q = session.query(origin_column.table).filter(
        origin_column.notin_(session.query(ref_column)), origin_column != None
    )
    return q


def get_foreign_key_errors(session, origin_column, ref_column):
    missing_fk_q = query_missing_foreign_key(session, origin_column,ref_column)
    errors = yield_model_errors(
        model_errors.MissingForeignKeyError,
        missing_fk_q,
        origin_column,
        ref_column=ref_column
    )
    return errors


def query_not_unique(session, column):
    """Return all values in column that are not unique

    Null values are ignored.

    :param session: sqlalchemy.orm.session.Session
    :param column: InstrumentedAttribute
    :return: list of declared models instances of column.class
    """
    duplicate_values = (
        session.query(column).group_by(column).having(func.count(column) > 1)
    )
    q = session.query(column.table).filter(column.in_(duplicate_values))
    return q


def get_not_unique_errors(session, column):
    not_unique_q = query_not_unique(session, column)
    errors = yield_model_errors(
        model_errors.NotUniqueError, not_unique_q, column)
    return errors


def query_not_null(session, column):
    """Return all values that are not null

    :param session: sqlalchemy.orm.session.Session
    :param column: sqlalchemy.Column
    :return: sqlalchemy.orm.query.Query
    """
    q = session.query(column.table).filter(column == None)
    return q


def get_null_errors(session, column):
    """Return an iterator which yields NullColumnError for all values in
    column which are null.

    :param session:
    :param column: sqlalchemy.Column
    :return: iterator
    """
    q = query_not_null(session, column)
    errors = yield_model_errors(
        NullColumnError, q, column)
    return errors


def query_invalid_type(session, column):
    """Return all values in column that are not of the column defined type.

    Null values are ignored.

    Only relevant for sqlite as it supports dynamic typing
    (https://www.sqlite.org/datatype3.html).

    :param session: sqlalchemy.orm.session.Session
    :param column: sqlalchemy.Column
    :return: list
    """
    if "sqlite" not in session.bind.dialect.dialect_description:
        return []

    expected_type = sqlalchemy_to_sqlite_type(column.type)
    q = session.query(column.table).filter(
        func.typeof(column) != expected_type,
        func.typeof(column) != "null"
    )
    return q


def get_invalid_type_errors(session, column):
    invalid_types_q = query_invalid_type(session, column)
    expected_type = sqlalchemy_to_sqlite_type(column.type)
    invalid_type_errors = yield_model_errors(
        model_errors.InvalidTypeError,
        invalid_types_q,
        column,
        expected_type=expected_type)
    return invalid_type_errors


def query_invalid_geometry(session, column):
    """Return all rows which have an invalid geometry in column.

    Null values are ignored

    :param session: sqlalchemy.orm.session.Session
    :param column: sqlalchemy.Column
    :return:
    """
    invalid_geometries = session.query(column.table).filter(
        geo_func.ST_IsValid(column) != True,
        column != None
    )
    return invalid_geometries


def get_invalid_geometry_errors(session, column):
    """

    :param session: sqlalchemy.orm.session.Session
    :param column: sqlalchemy.Column
    :return:
    """
    invalid_geometry_q = query_invalid_geometry(session, column)
    invalid_geometry_errors = yield_model_errors(
        model_errors.InvalidGeometry,
        invalid_geometry_q,
        column
    )
    return invalid_geometry_errors


def query_invalid_geometry_types(session, column):
    """Return all rows which have an unexpected geometry type in column.

    Null values are ignored

    :param session: sqlalchemy.orm.session.Session
    :param column: sqlalchemy.Column
    :return:
    """
    expected_geometry_type = _get_geometry_type(
        column,
        dialect=session.bind.dialect.name
    )
    invalid_geometry_types_q = session.query(column.table).filter(
        geo_func.ST_GeometryType(column) != expected_geometry_type,
        column != None
    )
    return invalid_geometry_types_q


def get_invalid_geometry_type_errors(session, column):
    invalid_geometry_types_q = query_invalid_geometry_types(session, column)
    invalid_geometry_type_errors = yield_model_errors(
        model_errors.InvalidGeometry,
        invalid_geometry_types_q,
        column
    )
    return invalid_geometry_type_errors


def query_invalid_enums(session, column):
    """Return all rows which have an unexpected value in column

    Unexpected values are values not defined by its enum_class.
    Null values are ignored

    :param session: sqlalchemy.orm.session.Session
    :param column: sqlalchemy.Column
    :return:
    """
    invalid_values_q = session.query(column.table).filter(
        column.notin_(list(column.type.enum_class))
    )
    return invalid_values_q


def get_invalid_enums_errors(session, column):
    invalid_enums_q = query_invalid_enums(session, column)
    invalid_enum_values_errors = yield_model_errors(
        model_errors.InvalidValue,
        invalid_enums_q,
        column
    )
    return invalid_enum_values_errors


def query_invalid_timeseries(table):
    pass


def _get_geometry_type(column, dialect):
    if dialect == 'sqlite':
        return column.type.geometry_type
    elif dialect == 'postgresql':
        geom_type = column.type.geometry_type.capitalize()
        return 'ST_%s' % geom_type
    else:
        raise TypeError("Unexpected dialect %s" % dialect)


def sqlalchemy_to_sqlite_type(column_type):
    """Convert the sqlalchemy column type to sqlite data type

    Returns the value similar as the sqlite 'typeof' function.
    Raises TypeError if the column type is unknown.

    :param column_type: sqlalchemy.column
    :return: (str)
    """
    if isinstance(column_type, types.TypeDecorator):
        column_type = column_type.impl

    if isinstance(column_type, types.String):
        return "text"
    elif isinstance(column_type, types.Float):
        return "real"
    elif isinstance(column_type, types.Integer):
        return "integer"
    elif isinstance(column_type, types.Boolean):
        return "integer"
    elif isinstance(column_type, types.Numeric):
        return "numeric"
    elif isinstance(column_type, types.Date):
        return "text"
    elif isinstance(column_type, Geometry):
        return "blob"
    elif isinstance(column_type, types.TIMESTAMP):
        return "text"
    else:
        raise TypeError("Unknown column type: %s" % column_type)


def get_none_nullable_columns(table):
    """Return all non-nullable columns of the given table.

    :param table: sqlalchemy.sql.schema.Table
    :return: list of columns
    """
    not_null_columns = []
    for column in table.columns:
        if not column.nullable:
            not_null_columns.append(column)
    return not_null_columns


def get_unique_columns(table):
    unique_colums = []
    for column in table.columns:
        if column.unique or column.primary_key:
            unique_colums.append(column)
    return unique_colums


def get_foreign_key_columns(table):
    return table.foreign_keys


def get_geometry_columns(table):
    geometry_columns = []
    for column in table.columns:
        if type(column.type) == Geometry:
            geometry_columns.append(column)
    return geometry_columns


def get_enum_columns(table):
    enum_colums = []
    for column in table.columns:
        if issubclass(type(column.type), custom_types.IntegerEnum):
            enum_colums.append(column)
    return enum_colums


class ThreediModelChecker:

    def __init__(self, threedi_db):
        self.db = threedi_db
        self.schema = ModelSchema(self.db)

    @property
    def models(self):
        return self.schema.declared_models

    def parse_model(self):
        null_errors = self.yield_null_errors()
        foreign_key_erros = self.yield_foreign_key_errors()
        not_unique_errors = self.yield_not_unique_errors()
        data_type_errors = self.yield_data_type_errors()
        geometry_errors = self.yield_invalid_geometry_errors()
        invalid_enum_values_erros = self.yield_invalid_enum_errors()
        all_errors = chain(
            null_errors,
            foreign_key_erros,
            not_unique_errors,
            data_type_errors,
            geometry_errors,
            invalid_enum_values_erros
        )
        print_errors(all_errors)

    def yield_null_errors(self):
        """Return an iterator that yields NullColumnError of this model."""
        session = self.db.get_session()
        null_column_errors = []
        for model in self.models:
            columns_to_check = get_none_nullable_columns(model.__table__)
            for column in columns_to_check:
                null_column_errors += get_null_errors(session, column)
        return chain(null_column_errors)

    def yield_foreign_key_errors(self):
        session = self.db.get_session()
        foreign_key_errors = []
        for model in self.models:
            foreign_keys = get_foreign_key_columns(model.__table__)
            for fk in foreign_keys:
                foreign_key_errors += get_foreign_key_errors(
                    session, fk.parent, fk.column
                )
        return chain(foreign_key_errors)

    def yield_not_unique_errors(self):
        session = self.db.get_session()
        not_unique_errors = []
        for model in self.models:
            for column in get_unique_columns(model.__table__):
                not_unique_errors += get_not_unique_errors(session, column)
        return chain(not_unique_errors)

    def yield_data_type_errors(self):
        session = self.db.get_session()
        data_type_errors = []
        for model in self.models:
            for column in model.__table__.columns:
                data_type_errors += get_invalid_type_errors(session, column)
        return chain(data_type_errors)

    def yield_invalid_geometry_errors(self):
        session = self.db.get_session()
        geometry_errors = []
        for model in self.models:
            for column in get_geometry_columns(model.__table__):
                geometry_errors += get_invalid_geometry_errors(session, column)
                geometry_errors += get_invalid_geometry_type_errors(
                    session, column
                )
        return chain(geometry_errors)

    def yield_invalid_enum_errors(self):
        session = self.db.get_session()
        invalid_enum_values_erros = []
        for model in self.models:
            for column in get_enum_columns(model.__table__):
                invalid_enum_values_erros += get_invalid_enums_errors(
                    session, column)
        return chain(invalid_enum_values_erros)


def print_errors(errors):
    for error in errors:
        print(error)
