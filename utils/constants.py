# connection node constants
NODE_CALC_TYPE_BOUNDARY = -1
NODE_CALC_TYPE_ISOLATED = 1
NODE_CALC_TYPE_CONNECTED = 2
NODE_CALC_TYPE_EMBEDDED = 0
NODE_CALC_TYPE_BROAD_CRESTED = 3
NODE_CALC_TYPE_SHORT_CRESTED = 4
NODE_CALC_TYPE_DOUBLE_CONNECTED = 5

CALC_TYPE_RANKING = (
    NODE_CALC_TYPE_BOUNDARY,          # -1
    NODE_CALC_TYPE_EMBEDDED,          # 0
    NODE_CALC_TYPE_ISOLATED,          # 1
    NODE_CALC_TYPE_DOUBLE_CONNECTED,  # 5
    NODE_CALC_TYPE_CONNECTED,         # 2
    NODE_CALC_TYPE_BROAD_CRESTED,     # 3
    NODE_CALC_TYPE_SHORT_CRESTED      # 4
)

# different range is used to reflect
# that objects have their own geometry,
# e.g. channels and culverts
CALC_TYPE_MAP = {
    101: NODE_CALC_TYPE_ISOLATED,
    105: NODE_CALC_TYPE_DOUBLE_CONNECTED,
    102: NODE_CALC_TYPE_CONNECTED,
    100: NODE_CALC_TYPE_EMBEDDED,
}

CONNECTED_PNTS_THRESHOLD = {
    NODE_CALC_TYPE_BOUNDARY: 0,
    NODE_CALC_TYPE_ISOLATED: 0,
    NODE_CALC_TYPE_EMBEDDED: 0,
    NODE_CALC_TYPE_CONNECTED: 1,
    NODE_CALC_TYPE_DOUBLE_CONNECTED: 2
}

DEGREE_IN_METERS = 111325.0

TABLE_NAME_CALC_PNT = 'v2_calculation_point'
TABLE_NAME_CONN_PNT = 'v2_connected_pnt'
TABLE_NAME_LEVEE = 'v2_levee'

EPSG_WGS84 = 4326
EPSG_RD_NEW = 28992

# A dictionary to link tables names to the table views names
DICT_TABLE_NAMES = {
    "culvert": "v2_culvert",
    "orifice": "v2_orifice",
    "pumpstation": "v2_pumpstation",
    "weir": "v2_weir"
}
# A dictionary to link tables names to the id names
DICT_TABLE_ID = {
    "culvert": "cul_id",
    "orifice": "orf_id",
    "pumpstation": "pump_id",
    "weir": "weir_id"
}
# A dictionary to link the table view names to the action types
DICT_ACTION_TYPES = {
    "culvert": ["set_discharge_coefficient"],
    "orifice": ["set_crest_level", "set_discharge_coefficient"],
    "pumpstation": ["set_capacity"],
    "weir": ["set_crest_level", "set_discharge_coefficient"]
}

V2_TABLES = [
    'v2_1d_boundary_conditions',
    'v2_1d_lateral',
    'v2_2d_boundary_conditions',
    'v2_2d_lateral',
    'v2_aggregation_settings',
    'v2_calculation_point',
    'v2_channel',
    'v2_connected_pnt',
    'v2_connection_nodes',
    'v2_control',
    'v2_control_delta',
    'v2_control_group',
    'v2_control_measure_group',
    'v2_control_measure_map',
    'v2_control_memory',
    'v2_control_pid',
    'v2_control_table',
    'v2_control_timed',
    'v2_cross_section_definition',
    'v2_cross_section_location',
    'v2_cross_section_view',
    'v2_culvert',
    'v2_culvert_view',
    'v2_dem_average_area',
    'v2_global_settings',
    'v2_grid_refinement',
    'v2_grid_refinement_area',
    'v2_groundwater',
    'v2_impervious_surface',
    'v2_impervious_surface_map',
    'v2_interflow',
    'v2_levee',
    'v2_manhole',
    'v2_manhole_view',
    'v2_numerical_settings',
    'v2_obstacle',
    'v2_orifice',
    'v2_pipe',
    'v2_pumpstation',
    'v2_simple_infiltration',
    'v2_surface',
    'v2_surface_map',
    'v2_surface_parameters',
    'v2_weir',
    'v2_windshielding',
]

NON_SETTINGS_TBL_WITH_RASTERS = {
    'v2_simple_infiltration':   'simple_infiltration_setting_id',
    'v2_groundwater':           'groundwater_setting_id',
    'v2_interflow':             'interflow_setting_id'
}

RASTER_CHECKER_MAPPER = [
    {'check_id': 1,
     'phase': 1,
     'base_check_name': 'tif_exists',
     'description': '{{check_id}}: Do the referenced rasters (in all '
                    'v2_tables) exist on your machine?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} found for setting_id {{setting_id}}',
        'warning': '',
        'error': '{{raster}} not found for setting_id {{setting_id}}',
        },
     },
    {'check_id': 2,
     'phase': 1,
     'base_check_name': 'extension',
     'blocking': False,
     'description': '{{check_id}}: Is the raster file extension .tif / .tiff?',
     'feedback': {
        'info': '{{raster}} has a valid extension',
        'warning': '',
        'error': '{{raster}} has an invalid extension. Must be .tif or .tiff',
        },
     },
    {'check_id': 3,
     'phase': 1,
     'base_check_name': 'filename',
     'blocking': False,
     'description': "{{check_id}}: Is the raster filename valid? (no special "
                    "characters, no space, max one '.' and '/')",
     'feedback': {
        'info': '{{raster}} has a valid filename',
        'warning': '',
        'error': '{{raster}} has an invalid filename. Please remove special '
                 'chars',
        },
     },
    {'check_id': 4,
     'phase': 2,
     'base_check_name': 'singleband',
     'description': '{{check_id}}: Is the raster single- (not multi-) band?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} is a single-band raster',
        'warning': '',
        'error': '{{raster}} is not (but must be) a single-band raster',
        },
     },
    {'check_id': 5,
     'phase': 2,
     'base_check_name': 'nodata',
     'description': '{{check_id}}: Is the raster nodata value -9999?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} nodata value -9999',
        'warning': '',
        'error': '{{raster}} nodata value is not (but must be) -9999',
        },
     },
    {'check_id': 6,
     'phase': 2,
     'base_check_name': 'utm',
     'description': '{{check_id}}: Does the raster have UTM projection '
                    '(unit: meters)?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} has UTM projection',
        'warning': '',
        'error': '{{raster}} has no (but must have) UTM projection '
                 '(unit: meter)',
        },
     },
    {'check_id': 7,
     'phase': 2,
     'base_check_name': 'flt32',
     'description': '{{check_id}}: Is the raster data type float 32?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} datatype is float_32',
        'warning': '',
        'error': '{{raster}} datatype is not (but must be) float_32',
        },
     },
    {'check_id': 8,
     'phase': 2,
     'base_check_name': 'compress',
     'description': '{{check_id}}: Is the raster compressed? '
                    '(compression=deflate)',
     'blocking': False,
     'feedback': {
        'info': '{{raster}} is compressed',
        'warning': "{{raster}} is not (but should be) compressed. Please use "
                   "e.g. <gdal_translate -co 'COMPRESS=DEFLATE'>",
        'error': '',
        },
     },
    {'check_id': 9,
     'phase': 2,
     'base_check_name': 'pixel_decimal',
     'description': '{{check_id}}: Does the pixelsize have max three '
                    'decimal places?',
     'blocking': False,
     'feedback': {
        'info': '{{raster}} has a pixel resolution with less than three '
                'decimal places',
        'warning': '{{raster}} has a pixel resolution with more than three '
                 'decimal places',
        'error': '',
        },
     },
    {'check_id': 10,
     'phase': 2,
     'base_check_name': 'square_pixel',
     'description': '{{check_id}}: Are the pixels square?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} does have square pixels',
        'warning': '',
        'error': '{{raster}} does not have square pixels',
        },
     },
    {'check_id': 11,
     'phase': 2,
     'base_check_name': 'extreme_value',
     'description': '{{check_id}}: Are there no extreme pixel values? (dem: '
                    '-10kmMSL<x<10kmMSL, other rasters: 0<x<10k)',
     'blocking': False,
     'feedback': {
        'info': '{{raster}} has no extreme values',
        'warning': '{{raster}} has an extreme minimum or maximum',
        'error': '',
        },
     },
    {'check_id': 12,
     'phase': 3,
     'base_check_name': 'proj',
     'description': '{{check_id}}: Is the projection equal to the dem '
                    'projection?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} projection equals dem projection',
        'warning': '',
        'error': '{{raster}} projection differs from dem projection',
        },
     },
    {'check_id': 13,
     'phase': 3,
     'base_check_name': 'pixelsize',
     'description': '{{check_id}}: Is the pixel size equal to the dem pixel '
                    'size?',
     'blocking': True,
     'feedback': {
        'info': '{{raster}} pixel size equals dem pixel size',
        'warning': '',
        'error': '{{raster}} pixel size differs from dem pixel size',
        },
     },
    {'check_id': 14,
     'phase': 3,
     'base_check_name': 'cnt_nodata',
     'blocking': False,
     'description': '{{check_id}}: Is the number of data/nodata pixels equal '
                    'to the dem',
     'feedback': {
        'info': '{{raster}} count of data/nodata pixels equals dem',
        'warning': '',
        'error': '{{raster}} count of data/nodata pixels differs from dem'
        },
     },
    {'check_id': 15,
     'phase': 3,
     'base_check_name': 'extent',
     'description': '{{check_id}}: Is the number of rows-colums equal to '
                    'the dem?',
     'blocking': False,
     'feedback': {
        'info': '{{raster}} extent equals dem extent',
        'warning': '',
        'error': '{{raster}} extent differs from dem extent',
        },
     },
    {'check_id': 16,
     'phase': 4,
     'base_check_name': 'pixel_alignment',
     'blocking': True,
     'description': '{{check_id}}: Are pixels correctly aligned (data and '
                    'nodata locations) with the dem?',
     'feedback': {
        'info': '{{raster}} data and nodata is aligned with the dem',
        'warning': '',
        'error': '{{raster}} data and nodata are not aligned with the dem. '
                 'The mismatch locations have been written to .shp file',
        },
     }
]
