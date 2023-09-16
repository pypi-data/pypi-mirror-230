import unittest
from unittest import mock
import cdsapi as cdsapi
from drb.exceptions.core import DrbException

from drb.drivers.era5 import EraNodeData, Era5ServiceNode, \
    Era5PredicateEra5SingleLevelsByHour, \
    Era5PredicateEra5SingleLevelsByMonth, Era5NodeDataSet


def mock_execute_request(self, item):
    if item['format'] == 'netcdf' and item['variable'] == \
            'surface_pressure' and item['product_type'] is not None:
        res = {'resultType': 'url',
               'contentType': 'application/x-netcdf',
               'contentLength': 2086244,
               'location': 'https://download-0003-clone.copernicus-climate.eu'
                           '/cache-compute-0003/cache/data5/'
                           'adaptor.mars.internal-1658932556.1103284-'
                           '7260-10-58044ab6-c73d-4f2a-b833-428b587ab377.nc'}
    else:
        raise DrbException

    return EraNodeData(self, res)


class TestEra5NodeDataset(unittest.TestCase):

    def test_namespace(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-single-levels']
        self.assertEqual(node.namespace_uri, 'ERA5')

    def test_attributes(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-single-levels']
        self.assertIn('ensemble_spread',
                      node.attributes[('product_type', None)])

    def test_attributes_monthly(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-pressure-levels-monthly-means']
        self.assertNotIn('ensemble_spread',
                         node.attributes[('product_type', None)])
        self.assertIn('monthly_averaged_ensemble_members_by_hour_of_day',
                      node.attributes[('product_type', None)])

    def test_name(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-single-levels']

        self.assertEqual(node.name, 'reanalysis-era5-single-levels')

    def test_path(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-single-levels']

        self.assertEqual(node.path.name,
                         'https://w_sample_x/reanalysis-era5-single-levels')

    def test_children_single_levels(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']

        self.assertTrue(node.has_child('mean_wave_direction'))

        self.assertIsNotNone(node['mean_wave_direction'])

        self.assertFalse(node.has_child('ozone_mass_mixing_ratio'))

    def test_children_land(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-land']

        self.assertTrue(node.has_child('surface_pressure'))

        self.assertIsNotNone(node['surface_pressure'])

        self.assertFalse(node.has_child('mean_wave_direction'))

    def test_children_pressure(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-pressure-levels-monthly-means']

        self.assertTrue(node.has_child('geopotential'))

        self.assertIsNotNone(node['geopotential'])

        self.assertFalse(node.has_child('surface_pressure'))

    def test_client_cds(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-pressure-levels-monthly-means']

        self.assertIsInstance(node.client_cds, cdsapi.api.Client)
        self.assertEqual(node.client_cds, node.parent.client_cds)

    def test_get_predicate_allowed(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']

        self.assertEqual(node.get_predicate_allowed(),
                         Era5PredicateEra5SingleLevelsByHour)

        node = service_era5['reanalysis-era5-single-levels-monthly-means']

        self.assertEqual(node.get_predicate_allowed(),
                         Era5PredicateEra5SingleLevelsByMonth)

    def test_get_item_predicate(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']
        predicate = Era5PredicateEra5SingleLevelsByHour(
            year=1959,
            month=1,
            day=1,
            time=0,
            variable='surface_pressure')
        with mock.patch.object(
                Era5NodeDataSet,
                'execute_request',
                new=mock_execute_request):
            res_node = node[predicate]

            self.assertIsInstance(res_node, EraNodeData)

    def test_get_item_dict(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']
        dict_request = {'year': 1959,
                        'month': 1,
                        'day': 1,
                        'time': 0,
                        'variable': 'surface_pressure',
                        'format': 'netcdf',
                        'product_type': 'reanalysis'
                        }
        dict_request_variable_false = {'year': 1959,
                                       'month': 1,
                                       'day': 1,
                                       'time': 0,
                                       'format': 'netcdf',
                                       'product_type': 'reanalysis',
                                       'variable': 'reanalysis'
                                       }

        with mock.patch.object(
                Era5NodeDataSet,
                'execute_request',
                new=mock_execute_request):
            res_node = node[dict_request]

            self.assertIsInstance(res_node, EraNodeData)

            with self.assertRaises(DrbException):
                node[dict_request_variable_false]

    def test_get_item_predicate_EraNode(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']
        node = node['surface_pressure']

        predicate = Era5PredicateEra5SingleLevelsByHour(
            year=1959,
            month=1,
            day=1,
            time=0)
        with mock.patch.object(
                Era5NodeDataSet,
                'execute_request',
                new=mock_execute_request):
            res_node = node[predicate]

            self.assertIsInstance(res_node, EraNodeData)
            self.assertEqual(res_node.name,
                             'adaptor.mars.internal-1658932556.1103284-7260-'
                             '10-58044ab6-c73d-4f2a-b833-428b587ab377.nc')

    def test_get_item_dict_EraNode(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']
        node = node['surface_pressure']

        dict_request = {'year': 1959,
                        'month': 1,
                        'day': 1,
                        'time': 0,
                        'format': 'netcdf',
                        'product_type': 'reanalysis'
                        }
        with mock.patch.object(
                Era5NodeDataSet,
                'execute_request',
                new=mock_execute_request):
            res_node = node[dict_request]

            self.assertIsInstance(res_node, EraNodeData)

    def test_name_EraNode(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']
        node = node['surface_pressure']

        self.assertEqual(node.name, 'surface_pressure')

    def test_client_cds_EraNode(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        node = service_era5['reanalysis-era5-single-levels']
        node = node['surface_pressure']

        self.assertEqual(node.client_cds, service_era5.client_cds)

    def test_attributes_EraNode(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-single-levels']
        node = node['surface_pressure']

        self.assertIn('ensemble_spread',
                      node.attributes[('product_type', None)])

    def test_attributes_monthly_EraNode(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        node = service_era5['reanalysis-era5-pressure-levels-monthly-means']
        node = node['vorticity']

        self.assertNotIn('ensemble_spread',
                         node.attributes[('product_type', None)])
        self.assertIn('monthly_averaged_ensemble_members_by_hour_of_day',
                      node.attributes[('product_type', None)])
