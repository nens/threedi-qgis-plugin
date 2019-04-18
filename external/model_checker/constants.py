from enum import Enum

LATEST_MIGRATION_ID = 173
LATEST_MIGRATION_NAME = "0171_auto__chg_field_v2aggregationsettings_aggregation_method__del_field_v2"  # noqa


class BoundaryType(Enum):
    WATERLEVEL = 1
    VELOCITY = 2
    DISCHARGE = 3
    SOMMERFELD = 5


class Later2dType(Enum):
    SURFACE = 1


class FlowVariable(Enum):
    DISCHARGE = 'discharge'
    FLOW_VELOCITY = 'flow_velocity'
    PUMP_DISCHARGE = 'pump_discharge'
    RAIN = 'rain'
    WATERLEVEL = 'waterlevel'
    WET_CROSS_SECTION = 'wet_cross-section'
    WET_SURFACE = 'wet_surface'
    LATERAL_DISCHARGE  = 'lateral_discharge'
    VOLUM = 'volume'
    SIMPLE_INFILTRATION = 'simple_infiltration'
    LEAKAGE = 'leakage'
    INTERCEPTION = 'interception'


class AggregationMethod(Enum):
    AVERAGE = 'avg'
    MINIMUM = 'min'
    MAXIMUM = 'max'
    CUMULATIVE = 'cum'
    MEDIAN = 'med'
    CUMULATIVE_NEGATIVE = 'cum_negative'
    CUMULATIVE_POSITIVE = 'cum_positive'
    CURRENT = 'current'


class CalculationType(Enum):
    EMBEDDED = 100
    STANDALONE = 101
    CONNECTED = 102
    DOUBLE_CONNECTED = 105


class CalculationTypeNode(Enum):
    EMBEDDED = 0
    ISOLATED = 1
    CONNECTED = 2


class CrossSectionShape(Enum):
    RECTANGLE = 1
    CIRCLE = 2
    EGG = 3
    TABULATED_RECTANGLE = 5
    TABULATED_TRAPEZIUM = 6


class FrictionType(Enum):
    CHEZY = 1
    MANNING = 2


class InitializationType(Enum):
    MAX = 0
    MIN = 1
    AVERAGE = 2


class SurfaceInclinationType(Enum):
    VLAK = 'vlak'
    HELLEND = 'hellend'
    UITGESTREKT = 'uitgestrekt'


class SurfaceClass(Enum):
    GESLOTEN_VERHARDING = 'gesloten verharding'
    OPEN_VERHARDING = 'open verharding'
    HALF_VERHARD = 'half verhard'
    ONVERHARD = 'onverhard'
    PAND = 'pand'


class SurfaceType(Enum):
    SURFACE = 'v2_surface'
    IMPERVIOUS_SURFACE = 'v2_impervious_surface'


class InterflowType(Enum):
    NO_INTERLFOW = 0
    LOCAL_DEEPEST_POINT_SCALED_POROSITY = 1
    GLOBAL_DEEPEST_POINT_SCALED_POROSITY = 2
    LOCAL_DEEPEST_POINT_CONSTANT_POROSITY = 3
    GLOBAL_DEEPEST_POINT_CONSTANT_POROSITY = 4


class Material(Enum):
    SAND = 1
    CLAY = 2


class CrestType(Enum):
    BROAD_CRESTED = 3
    SHORT_CRESTED = 4


class SewerageType(Enum):
    MIXED = 0
    RAIN_WATER = 1
    DRY_WEATHER_FLOW = 2
    TRANSPORT = 3
    SPILLWAY = 4
    ZINKER = 5
    STORAGE = 6
    STORAGE_TANK = 7


class PumpType(Enum):
    SUCTION_SIDE = 1
    DELIVERY_SIDE = 2


class InfiltrationSurfaceOption(Enum):
    RAIN = 0
    WHOLE_SURFACE = 1
    WET_SURFACE = 2
