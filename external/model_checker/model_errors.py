class BaseModelError (object):
    """Dataclass to store error information of a model

    Base class to group all model errors"""

    def __init__(self, instance, column, **kwargs):
        self.instance = instance
        self.column = column
        self.id = getattr(self.instance, 'id')

    def __str__(self):
        return "%s: Unexpected value '%s' in column '%s' for id %s" % (
            type(self).__name__,
            getattr(self.instance, self.column.name),
            self.column,
            self.id
        )


class MissingForeignKeyError(BaseModelError):

    def __init__(self, ref_column, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_column = ref_column

    def __str__(self):
        return "%s: Missing foreign key in column %s for id %s, expected " \
               "reference to %s" % (
                   type(self).__name__,
                   self.column,
                   self.id,
                   self.ref_column
               )


class NullColumnError(BaseModelError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s: Unexpected null value in column '%s' for id %s" % (
            type(self).__name__,
            self.column,
            self.id)


class InvalidTypeError(BaseModelError):
    def __init__(self, expected_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_type = expected_type

    def __str__(self):
        return "%s: Invalid type in column '%s' for id %s, expected type '%s'" % (
            type(self).__name__,
            self.column,
            self.id,
            self.expected_type,
        )


class NotUniqueError(BaseModelError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s: Duplicate value '%s' in column '%s' for id %s" % (
            type(self).__name__,
            getattr(self.instance, self.column.name),
            self.column,
            self.id
        )


class InvalidGeometry(BaseModelError):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s: Invalid geometry '%s' in column %s for id %s" % (
            type(self).__name__,
            getattr(self.instance, self.column.name),
            self.column,
            self.id
        )


class InvalidValue(BaseModelError):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "%s: Invalid value '%s' in column %s for id %s, expected " \
               "one of the following values: %s" % (
                   type(self).__name__,
                   getattr(self.instance, self.column.name),
                   self.column,
                   self.id,
                   list(self.column.type.enum_class)
               )


def yield_model_errors(klass, instances, column, **kwargs):
    """Helper function to instantiate ModelError with data from
    sqlalchemy.orm.query.Query

    :param klass: BaseModelError or subclass
    :param instances: sqlalchemy.orm.query.Query
    :param column: sqlalchemy.Column
    :param kwargs: See klass for specific kwargs.
    :return:
    """
    for instance in instances:
        yield klass(instance=instance, column=column, **kwargs)
