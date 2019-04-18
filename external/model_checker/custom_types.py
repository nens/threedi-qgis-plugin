from sqlalchemy.types import TypeDecorator, Integer, VARCHAR


class IntegerEnum(TypeDecorator):
    """Column type for storing integer python enums.

    The IntegerEnum will make use of the backend INTEGER datatype to store
    the data. Data is converted back it's enum_class python object if possible.
    If not, the raw INTEGER is returned.

    IntegerEnum is used to indicate that a column is only allowed to store a
    specified set of values, given by the Enum.
    """

    impl = Integer

    def __init__(self, enum_class):
        """

        :param enum_class: instance of enum.Enum
        """
        super(IntegerEnum, self).__init__()
        self.enum_class = enum_class
        self.enums = [e.value for e in enum_class]

    def process_bind_param(self, value, dialect):
        if isinstance(value, self.enum_class):
            return value.value
        else:
            return value

    def process_result_value(self, value, dialect):
        if isinstance(value, self.enum_class):
            return self.enum_class(value)
        else:
            return value


class VarcharEnum(IntegerEnum):

    impl = VARCHAR
