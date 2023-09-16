import unittest

from drb.drivers.era5 import Era5ServiceNode, EraNodeData


class TestEra5NodeDataset(unittest.TestCase):

    res = {'resultType': 'url',
           'contentType': 'application/x-netcdf',
           'contentLength': 2086244,
           'location': 'https://download-0003-clone.copernicus-climate.eu'
                       '/cache-compute-0003/cache/data5/'
                       'adaptor.mars.internal-1658932556.1103284-'
                       '7260-10-58044ab6-c73d-4f2a-b833-428b587ab377.nc'}

    @staticmethod
    def create_data_node():
        service_era5 = Era5ServiceNode('https+era5://w_sample_x',
                                       auth='key:pass')
        node = service_era5['reanalysis-era5-single-levels']

        return EraNodeData(node, TestEra5NodeDataset.res)

    def test_attributes(self):
        data_node = TestEra5NodeDataset.create_data_node()
        self.assertEqual('url',
                         data_node.attributes[('resultType', None)])
        self.assertEqual('application/x-netcdf',
                         data_node.attributes[('contentType', None)])

    def test_get_attributes_monthly(self):
        data_node = TestEra5NodeDataset.create_data_node()

        self.assertEqual('url',
                         data_node.get_attribute('resultType'))

    def test_client_cds(self):
        data_node = TestEra5NodeDataset.create_data_node()

        self.assertEqual(data_node.parent.client_cds,
                         data_node.client_cds)

    def test_value(self):
        data_node = TestEra5NodeDataset.create_data_node()

        self.assertEqual(TestEra5NodeDataset.res,
                         data_node.value)
