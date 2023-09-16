import io
import unittest

import cdsapi as cdsapi
from drb.exceptions.core import DrbException

from drb.drivers.era5 import Era5ServiceNode, Era5NodeDataSet


class TestEra5ServiceNode(unittest.TestCase):

    def test_namespace(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')

        self.assertEqual(service_era5.namespace_uri, 'ERA5')

    def test_name(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')

        self.assertEqual(service_era5.name, 'https://w_sample_x')

    def test_path(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')

        self.assertEqual(service_era5.path.name, 'https://w_sample_x')

    def test_attributes(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')

        self.assertEqual(service_era5.attributes, {})

    def test_has_impl(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')

        self.assertFalse(service_era5.has_impl(io.BufferedIOBase))

    def test_get_impl(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')
        with self.assertRaises(DrbException):
            service_era5.get_impl(io.BufferedIOBase)

    def test_get_attributes(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x')

        with self.assertRaises(DrbException):
            service_era5.get_attribute('test', None)

    def test_auth(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        self.assertEqual(service_era5.auth, 'key;pass')

    def test_value(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        self.assertIsNone(service_era5.value)

    def test_children(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        self.assertEqual(len(service_era5.children), 6)

        self.assertTrue(service_era5.has_child('reanalysis-era5-land'))
        self.assertFalse(service_era5.has_child('reanalysis-era5-lands'))

        self.assertIsNotNone(service_era5['reanalysis-era5-single-levels'])

        self.assertIsInstance(service_era5['reanalysis-era5-single-levels'],
                              Era5NodeDataSet)

    def test_client_cds(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')

        self.assertIsInstance(service_era5.client_cds, cdsapi.api.Client)

    def test_predicate_allowed(self):
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       'key;pass')
        self.assertIsNone(service_era5.get_predicate_allowed())
