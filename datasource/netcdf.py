import glob
from itertools import (starmap, product)
import json
import os

from netCDF4 import Dataset
import numpy as np

from ..utils.user_messages import log
from ..utils import cached_property
from .spatialite import (
    normalized_object_type,
    get_variables,
    SUBGRID_MAP_VARIABLES,
    AGGREGATION_VARIABLES,
    AGGREGATION_OPTIONS,
)

# Explanation: aggregation using the cumulative method integrates the variable
# over time. Therefore the units must be multiplied by the time also.
CUMULATIVE_AGGREGATION_UNITS = {
    's1': 'm MSL s',
    'q': 'm3',
    'u1': 'm',
    'vol': 'm3 s',
    'q_pump': 'm3',
    'qp': 'm3',
    'up1': 'm',
    }


def find_id_mapping_file(netcdf_file_path):
    """An ad-hoc way to get the id_mapping file.

    We assume the id_mapping file is in on of the following locations (note:
    this order is also the searching order):

    1) . (in the same dir as the netcdf)
    2) ../input_generated

    relative to the netcdf file and that it starts with 'id_mapping'.

    Args:
        netcdf_file_path: path to the result netcdf

    Returns:
        id_mapping file path

    Raises:
        IndexError if nothing is found
    """
    pattern = 'id_mapping*'
    inpdir = os.path.join(os.path.dirname(netcdf_file_path),
                          '..', 'input_generated')
    resultdir = os.path.dirname(netcdf_file_path)

    from_inpdir = glob.glob(os.path.join(inpdir, pattern))
    from_resultdir = glob.glob(os.path.join(resultdir, pattern))

    inpfiles = from_resultdir + from_inpdir
    return inpfiles[0]


def find_aggregation_netcdf(netcdf_file_path):
    """An ad-hoc way to find the aggregation netcdf file.

    It is assumed that the file is called 'flow_aggregate.nc' and in the same
    directory as the 'regular' result netcdf.

    Args:
        netcdf_file_path: path to the result netcdf

    Returns:
        the aggregation netcdf path

    Raises:
        IndexError if nothing is found
    """
    pattern = 'flow_aggregate.nc'
    result_dir = os.path.dirname(netcdf_file_path)
    return glob.glob(os.path.join(result_dir, pattern))[0]


# TODO: this function doesn't work correctly because multiple links can
# belong to one inp id.
# I.e.: dict(cm) is wrong, because len(dict(cm)) != len(cm)
def construct_channel_mapping(ds):
    """Map inp ids to flowline ids.

    Note that you need to subtract 1 from the resulting flowline id because of
    Python's 0-based indexing array (versus Fortran's 1-based indexing). These
    flowline ids are used for  pipes, weirs and orifices.
    """
    cm = np.copy(ds.variables['channel_mapping'])
    cm[:, 1] = cm[:, 1] - 1  # the index transformation
    # TODO: not a dict anymore, needs changing other places
    return dict(cm)
    # return cm


def construct_node_mapping(ds):
    """Map inp ids to node ids.

    Note that you need to subtract 1 from the resulting node id because of
    Python's 0-based indexing array (versus Fortran's 1-based indexing). These
    node ids are used for manholes.
    """
    cm = np.copy(ds.variables['node_mapping'])
    cm[:, 1] = cm[:, 1] - 1  # the index transformation
    return dict(cm)


def get_timesteps(ds):
    """Timestep determination using consecutive element difference"""
    return np.ediff1d(ds.variables['time'])


# Note: copied from threedi codebase
def product_and_concat(variables, aggregation_options=AGGREGATION_OPTIONS):
    """Make combinatons with cartesian product and concatenate the pairs
    with an underscore.

    Returns:
        the combinations as an iterable

    >>> sorted(list(product_and_concat(['a'], ['b'])))
    ['a_b']
    >>> sorted(product_and_concat(['a', 'b'], ['c']))
    ['a_c', 'b_c']
    >>> sorted(product_and_concat(['a'], ['b', 'c']))
    ['a_b', 'a_c']
    >>> sorted(product_and_concat(['a', 'b'], ['c', 'd']))
    ['a_c', 'a_d', 'b_c', 'b_d']
    >>> sorted(product_and_concat('q'))
    ['q_avg', 'q_cum', 'q_max', 'q_min']
    """
    prods = product(variables, aggregation_options)
    nc_vars = starmap(lambda x, y: '%s_%s' % (x, y), prods)
    return nc_vars


class NetcdfDataSource(object):
    """This netCDF datasource combines three things:

    1. the regular 3Di result netcdf: subgrid_map.nc
    2. the spatialite mappings from id_mapping.json
    3. the aggregation netcdf flow_aggregate.nc

    To initialize this class only the subgrid_map.nc netcdf is required though,
    the locations of the other two files can be derived from it. Furthermore,
    the other files should be lazily loaded because they are not required in
    all use cases and/or they are not always available. In the latter case you
    will still want the parts of your program to work that DO NOT require the
    additional files. However, if you DO want to enforce these files to be
    required, you can do so by checking them using the helper functions
    'find_id_mapping_file' and 'find_aggregation_netcdf'.
    """

    def __init__(self, file_path, load_properties=True):
        """
        Args:
            file_path: path to result netcdf
        """
        self.file_path = file_path
        # Load netcdf
        self.ds = Dataset(self.file_path, mode='r', format='NETCDF4')
        log("Opened netcdf: %s" % self.file_path)
        self.cache = dict()

        if load_properties:
            self.load_properties()

    def load_properties(self):
        """Load and pre-calculate some properties.

        Note: these properties are required for node_type_of and
        line_type_of to work.
        """
        # Nodes
        self.n2dtot = self.ds.nFlowElem2d
        self.n1dtot = self.ds.nFlowElem1d
        self.n2dobc = self.ds.nFlowElem2dBounds
        self.end_n1dtot = self.n2dtot + self.n1dtot
        self.end_n2dobc = self.n2dtot + self.n1dtot + self.n2dobc
        self.nodall = self.ds.nFlowElem
        # Links
        self.nFlowLine2d = self.ds.nFlowLine2d
        self.nFlowLine = self.ds.nFlowLine
        self.end_2d_bound_line = self.nFlowLine - self.ds.nFlowLine1dBounds
        self.end_1d_line = (self.nFlowLine - self.ds.nFlowLine2dBounds -
                            self.ds.nFlowLine1dBounds)

    @cached_property
    def id_mapping(self):
        # Load id mapping
        with open(find_id_mapping_file(self.file_path)) as f:
            return json.load(f)

    @cached_property
    def ds_aggregation(self):
        """The aggregation netcdf dataset."""
        # Load aggregation netcdf
        aggregation_netcdf_file = find_aggregation_netcdf(self.file_path)
        log("Opening aggregation netcdf: %s" % aggregation_netcdf_file)
        return Dataset(aggregation_netcdf_file, mode='r',
                       format='NETCDF4')

    @cached_property
    def channel_mapping(self):
        return construct_channel_mapping(self.ds)

    @cached_property
    def node_mapping(self):
        return construct_node_mapping(self.ds)

    @cached_property
    def timesteps(self):
        return get_timesteps(self.ds)

    @cached_property
    def timestamps(self):
        return self.get_timestamps()

    @cached_property
    def available_subgrid_map_vars(self):
        return self.get_available_variables(
            only_subgrid_map=True)['subgrid_map']

    @cached_property
    def available_aggregation_vars(self):
        try:
            vars = self.get_available_variables(
                only_aggregation=True)['aggregation']
        except IndexError:
            # If we're here it means no agg. netCDF was found. Fail without
            # error, but do log it.
            log("No aggregation netCDF was found, only the data from the "
                "regular netCDF will be used.", level='WARNING')
            vars = []
        return vars

    @property
    def metadata(self):
        pass

    def get_timestamps(self, object_type=None, parameter=None):
        return self.ds.variables['time'][:]

    def get_agg_var_timestamps(self, aggregation_variable_name):
        """Get timestamps for aggregation variables.

        Example: for 's1_max' the time variable name is 'time_s1_max'.
        """
        time_var_name = 'time_%s' % aggregation_variable_name
        return self.ds_aggregation.variables[time_var_name][:]

    def get_object_types(self, parameter=None):
        pass

    def get_objects(self, object_type):
        pass

    def get_object_count(self, object_type):
        pass

    def get_parameters(self, object_type=None):
        pass

    def get_available_variables(self, only_subgrid_map=False,
                                only_aggregation=False):
        """Query the netCDF files and get all variables which we can retrieve
        data for.

        Returns:
            a dict with entries for subgrid_map and aggregation vars
        """
        do_all = not any([only_subgrid_map, only_aggregation])
        result = dict()

        if do_all or only_subgrid_map:
            possible_subgrid_map_vars = [v for v, _, _ in
                                         SUBGRID_MAP_VARIABLES]
            subgrid_map_vars = self.ds.variables.keys()
            available_subgrid_map_vars = set(
                possible_subgrid_map_vars).intersection(set(subgrid_map_vars))
            result['subgrid_map'] = list(available_subgrid_map_vars)
        if do_all or only_aggregation:
            possible_agg_vars = [product_and_concat([v]) for v, _, _ in
                                 AGGREGATION_VARIABLES]
            # This flattens the list of lists
            possible_agg_vars = [item for sublist in possible_agg_vars for
                                 item in sublist]
            agg_vars = self.ds_aggregation.variables.keys()
            available_agg_vars = set(
                possible_agg_vars).intersection(set(agg_vars))
            result['aggregation'] = list(available_agg_vars)
        return result

    def get_object(self, object_type, object_id):
        pass

    def inp_id_from(self, object_id, normalized_object_type):
        """Get the id mapping dict correctly and then return the mapped id,
        aka: the inp_id"""
        try:
            # This is the sewerage situation
            obj_id_mapping = self.id_mapping[normalized_object_type]
        except KeyError:
            # This is the v2 situation
            # TODO: another v2 <-> sewerage difference...
            log("id_mapping json v2 <-> sewerage naming discrepancy",
                level='WARNING')
            v2_object_type = 'v2_' + normalized_object_type
            obj_id_mapping = self.id_mapping[v2_object_type]
        return obj_id_mapping[str(object_id)]  # strings because JSON

    def netcdf_id_from(self, inp_id, object_type):
        """Get the node or flow link id needed to get data from netcdf."""
        # Note: because pumpstation uses q_pump it also has a special way of
        # accessing that array.
        if object_type in ['pumpstation']:
            return inp_id - 1
        elif object_type in ['manhole', 'connection_nodes']:
            return self.node_mapping[inp_id]
        else:
            return self.channel_mapping[inp_id]

    def node_type_of(self, node_idx):
        """Get the node type based on its index."""
        # Order of nodes in netCDF is:
        # 1. nFlowElem2d
        # 2. nFlowElem1d
        # 3. nFlowElem2dBounds
        # 4. nFlowElem1dBounds
        #    ----------------- +
        #    nFlowElem
        if node_idx < self.n2dtot:
            return '2d'
        elif node_idx < self.end_n1dtot:
            return '1d'
        elif node_idx < self.end_n2dobc:
            return '2d_bound'
        elif node_idx < self.nodall:
            return '1d_bound'
        else:
            raise ValueError(
                "Index %s is not smaller than the number of nodes (%s)" %
                (node_idx, self.nodall))

    def line_type_of(self, line_idx):
        """Get line type based on its index."""
        # Order of links in netCDF is:
        # - 2d links (x and y) (nr: part of ds.ds.nFlowLine2d)
        # - 1d links (nr: ds.ds.nFlowLine1d)
        # - 1d-2d links (nr: part of ds.ds.nFlowLine2d)
        # - 2d bound links (nr: ds.ds.nFlowLine2dBounds)
        # - 1d bound links (nr: ds.ds.nFlowLine1dBounds)
        if line_idx < self.nFlowLine2d:
            return '2d'
        elif line_idx < self.end_1d_line:
            return '1d'
        elif line_idx < self.end_2d_bound_line:
            return '2d_bound'
        elif line_idx < self.nFlowLine:
            return '1d_bound'
        else:
            raise ValueError(
                "Index %s is not smaller than the number of lines (%s)" %
                (line_idx, self.nFlowLine))

    def obj_to_netcdf_id(self, object_id, normalized_object_type):
        # Here we map the feature ids (== object ids) to internal netcdf ids.
        # Note: 'flowline' and 'node' are memory layers that are made from the
        # netcdf, so they don't need an id mapping or netcdf mapping
        if normalized_object_type in ['flowline', 'node', 'pumpline']:
            # TODO: need to test this id to make sure (-1/+1??)!!
            netcdf_id = object_id - 1
        else:
            # Mapping: spatialite id -> inp id -> netcdf id
            inp_id = self.inp_id_from(object_id, normalized_object_type)
            netcdf_id = self.netcdf_id_from(inp_id, normalized_object_type)
        return netcdf_id

    def get_timeseries(self, object_type, object_id, parameters, start_ts=None,
                       end_ts=None):
        """Get a list of time series from netcdf.

        Note: you can have multiple parameters, all result values are put
        into a dict under the corresponding key of the parameter. If a
        parameter is unknown it will be skipped.

        Args:
            object_type: e.g. 'v2_weir'
            object_id: spatialite id
            parameters: a list of params, e.g.: ['q', 'q_pump']

        Returns:
            a dict of timeseries (lists of 2-tuples (time, value))
        """
        # Normalize the name
        n_object_type = normalized_object_type(object_type)

        # Derive the netcdf id
        netcdf_id = self.obj_to_netcdf_id(object_id, n_object_type)

        variables = get_variables(n_object_type, parameters)

        # Get data from all variables and just put them in a dict:
        result = dict()
        for v in variables:
            # Get values
            try:
                if v in self.available_subgrid_map_vars:
                    vals = self.ds.variables[v][:, netcdf_id]
                elif v in self.available_aggregation_vars:
                    vals = self.ds_aggregation.variables[v][:, netcdf_id]
                else:
                    continue
            except KeyError:
                log("Variable not in netCDF: %s, skipping..." % v)
                continue
            except IndexError:
                log("Netcdf id %s not found for %s" % (netcdf_id, v))
                continue

            # Get timestamps
            if v in self.available_subgrid_map_vars:
                timestamps = self.timestamps
            elif v in self.available_aggregation_vars:
                timestamps = self.get_agg_var_timestamps(v)
            else:
                continue

            # Zip timeseries together
            result[v] = zip(timestamps, vals)
        return result

    # TODO: doesn't work with agg vars yet?
    def get_timeseries_values(self, object_type, object_id, parameters,
                              source='default', caching=True):
        """Get a list of time series from netcdf; only the values.

        Note: you can have multiple parameters, all result values are put
        into a dict under the corresponding key of the parameter. If a
        parameter is unknown it will be skipped.

        Note 2: source defines the netcdf file source we should get our data
        from, because the NetcdfDataSource can contain the default netcdf
        but also an aggregation netcdf.

        Args:
            object_type: e.g. 'v2_weir'
            object_id: spatialite id
            parameters: a list of params, e.g.: ['q', 'q_pump']
            source: the netcdf source type, i.e., 'default' (subgrid_map.nc)
                or 'aggregation' (flow_aggregate.nc)
            caching: if True, keep netcdf array in memory

        Important note: using True instead of False as a default for the
        'caching' kwarg makes this method much faster. Branch prediction?

        Returns:
            a dict of arrays of values
        """
        # Normalize the name
        n_object_type = normalized_object_type(object_type)

        # Derive the netcdf id
        netcdf_id = self.obj_to_netcdf_id(object_id, n_object_type)

        variables = get_variables(n_object_type, parameters)

        # Get data from all variables and put them in a dict:
        timeseries_vals = dict()
        for v in variables:
            # Select the source netcdf:
            if v in self.available_subgrid_map_vars:
                ds = self.ds
            elif v in self.available_aggregation_vars:
                ds = self.ds_aggregation
            else:
                continue

            # Keep the netCDF array in memory for performance
            if caching:
                try:
                    variable = self.cache[v]
                except KeyError:
                    try:
                        variable = ds.variables[v][:]  # make copy
                        self.cache[v] = variable
                    except KeyError:
                        log("Variable not in netCDF: %s, skipping..." % v)
                        continue
            else:
                variable = ds.variables[v][:]

            try:
                # shape ds.variables['q'] array = (t, number of ids)
                vals = variable[:, netcdf_id]
            except KeyError:
                log("Variable not in netCDF: %s, skipping..." % v)
                continue
            except IndexError:
                log("Id %s not found for %s" % (netcdf_id, v))
                continue
            timeseries_vals[v] = vals
        return timeseries_vals
