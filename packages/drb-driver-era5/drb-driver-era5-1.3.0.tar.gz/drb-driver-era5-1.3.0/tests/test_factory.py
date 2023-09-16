import io
import unittest

from drb.nodes.logical_node import DrbLogicalNode

from drb.drivers.era5 import Era5Factory, Era5ServiceNode

stream_era5 = b'<?xml version="1.0" encoding="UTF-8"?><WMTS_Capabilities xmlns:inspire_vs="http://inspire.ec.europa.eu/schemas/inspire_vs/1.0" xmlns:inspire_common="http://inspire.ec.europa.eu/schemas/common/1.0" version="1.3.0" updateSequence="37" xmlns="http://www.opengis.net/era5" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/era5 http://geoserver.swarm.ops.internal.gael.fr/geoserver/schemas/era5/1.3.0/capabilities_1_3_0.xsd http://inspire.ec.europa.eu/schemas/inspire_vs/1.0 https://inspire.ec.europa.eu/schemas/inspire_vs/1.0/inspire_vs.xsd">\n  <Service>\n    <Name>WMTS</Name>\n    <Title/>\n    <Abstract/>\n    <KeywordList/>\n    <OnlineResource xlink:type="simple" xlink:href="http://geoserver.swarm.ops.internal.gael.fr/geoserver/"/>\n    <ContactInformation>\n      <ContactPersonPrimary>\n        <ContactPerson/>\n        <ContactOrganization/>\n      </ContactPersonPrimary>\n      <ContactPosition/>\n      <ContactAddress>\n        <AddressType/>\n        <Address/>\n        <City/>\n        <StateOrProvince/>\n        <PostCode/>\n        <Country/>\n      </ContactAddress>\n      <ContactVoiceTelephone/>\n      <ContactFacsimileTelephone/>\n      <ContactElectronicMailAddress/>\n    </ContactInformation>\n    <Fees>none</Fees>\n    <AccessConstraints>none</AccessConstraints>\n  </Service>\n  <Capability>\n    <Request>\n      <GetCapabilities>\n        <Format>text/xml</Format>\n        <DCPType>\n          <HTTP>\n            <Get>\n              <OnlineResource xlink:type="simple" xlink:href="http://geoserver.swarm.ops.internal.gael.fr/geoserver/demo/ows?SERVICE=WMTS&amp;"/>\n            </Get>\n            <Post>\n              <OnlineResource xlink:type="simple" xlink:href="http://geoserver.swarm.ops.internal.gael.fr/geoserver/demo/ows?SERVICE=WMTS&amp;"/>\n            </Post>\n          </HTTP>\n        </DCPType>\n      </GetCapabilities>\n      <GetMap>\n        <Format>image/png</Format>\n        <Format>application/atom+xml</Format>\n        <Format>application/json;type=geojson</Format>\n        <Format>application/json;type=topojson</Format>\n        <Format>application/json;type=utfgrid</Format>\n        <Format>application/pdf</Format>\n        <Format>application/rss+xml</Format>\n        <Format>application/vnd.google-earth.kml+xml</Format>\n        <Format>application/vnd.google-earth.kml+xml;mode=networklink</Format>\n        <Format>application/vnd.google-earth.kmz</Format>\n        <Format>application/vnd.mapbox-vector-tile</Format>\n        <Format>image/geotiff</Format>\n        <Format>image/geotiff8</Format>\n        <Format>image/gif</Format>\n        <Format>image/jpeg</Format>\n        <Format>image/png; mode=8bit</Format>\n        <Format>image/svg+xml</Format>\n        <Format>image/tiff</Format>\n        <Format>image/tiff8</Format>\n        <Format>image/vnd.jpeg-png</Format>\n        <Format>image/vnd.jpeg-png8</Format>\n        <Format>text/html; subtype=openlayers</Format>\n        <Format>text/html; subtype=openlayers2</Format>\n        <Format>text/html; subtype=openlayers3</Format>\n        <DCPType>\n          <HTTP>\n            <Get>\n              <OnlineResource xlink:type="simple" xlink:href="http://geoserver.swarm.ops.internal.gael.fr/geoserver/demo/ows?SERVICE=WMTS&amp;"/>\n            </Get>\n          </HTTP>\n        </DCPType>\n      </GetMap>\n      <GetFeatureInfo>\n        <Format>text/plain</Format>\n        <Format>application/vnd.ogc.gml</Format>\n        <Format>text/xml</Format>\n        <Format>application/vnd.ogc.gml/3.1.1</Format>\n        <Format>text/xml; subtype=gml/3.1.1</Format>\n        <Format>text/html</Format>\n        <Format>text/javascript</Format>\n        <Format>application/json</Format>\n        <DCPType>\n          <HTTP>\n            <Get>\n              <OnlineResource xlink:type="simple" xlink:href="http://geoserver.swarm.ops.internal.gael.fr/geoserver/demo/ows?SERVICE=WMTS&amp;"/>\n            </Get>\n          </HTTP>\n        </DCPType>\n      </GetFeatureInfo>\n    </Request>\n    <Exception>\n      <Format>XML</Format>\n      <Format>INIMAGE</Format>\n      <Format>BLANK</Format>\n      <Format>JSON</Format>\n      <Format>JSONP</Format>\n    </Exception>\n    <Layer>\n      </Layer>\n  </Capability>\n</WMTS_Capabilities>\n'  # noqa
stream_features = b'{"type":"FeatureCollection","features":[{"type":"Feature","id":"mgrs_region.20501","geometry":{"type":"MultiPolygon","coordinates":[[[[2186283.741,6231700.7722],[2186012.7894,6246896.7124],[2185740.5019,6262119.7873],[2185466.9899,6277369.9624],[2185191.9195,6292647.3726],[2184915.6245,6307952.324],[2184637.8824,6323284.9543],[2184358.8044,6338645.231],[2184078.2793,6354033.2925],[2183796.4183,6369449.4499],[2183512.9989,6384893.8443],[2198928.6333,6385164.4408],[2214345.4922,6385406.6784],[2229763.4644,6385620.211],[2245182.4383,6385805.552],[2260602.3029,6385962.1838],[2276022.8354,6386090.4488],[2291443.9244,6386190.1735],[2306865.4587,6386261.3571],[2322287.327,6386304.1707],[2337709.3067,6386318.442],[2337709.3067,6370866.9603],[2337709.3067,6355443.7452],[2337709.3067,6340048.6553],[2337709.3067,6324681.3793],[2337709.3067,6309341.9489],[2337709.3067,6294030.0554],[2337709.3067,6278745.7317],[2337709.3067,6263488.6713],[2337709.3067,6248258.9082],[2337709.3067,6233056.3073],[2322564.5126,6233042.7998],[2307419.9411,6233002.1087],[2292275.481,6232934.2344],[2277131.5775,6232839.3463],[2261988.1192,6232717.4454],[2246845.4402,6232568.1952],[2231703.4291,6232392.1035],[2216562.4199,6232188.6656],[2201422.4126,6231958.2211],[2186283.741,6231700.7722]]]]},"geometry_name":"the_geom","properties":{"GRID1MIL":"34U","GRID100K":"DV","LONGITUDE":20.307416,"LATITUDE":49.198764},"bbox":[2183512.9989,6231700.7722,2337709.3067,6386318.442]}],"totalFeatures":"unknown","numberReturned":1,"timeStamp":"2022-06-01T13:19:28.257Z","crs":{"type":"name","properties":{"name":"urn:ogc:def:crs:EPSG::3857"}},"bbox":[2183512.9989,6231700.7722,2337709.3067,6386318.442]}'  # noqa


def get_attribute_mock(self, name: str, namespace_uri: str = None):
    return 'text/xml'


def get_impl_mock(self, impl: type, **kwargs):
    return io.BytesIO(stream_era5)


class TestEra5Factory(unittest.TestCase):
    svc_url = 'https://era5.test.com'

    def test_create(self):
        factory = Era5Factory()
        node = factory.create(self.svc_url)
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Era5ServiceNode)

    def test_create_logical_node(self):

        factory = Era5Factory()

        node = factory.create(DrbLogicalNode(self.svc_url))
        self.assertIsNotNone(node)
        self.assertIsInstance(node, Era5ServiceNode)
