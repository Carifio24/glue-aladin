from glue_qt.app import GlueApplication
from glue.core import Data

from glue_aladin.tests.utils import assert_expression_value

from ..data_viewer import AladinLiteViewer


class TestAladinLiteViewer(object):

    def setup_method(self, method):
        self.d = Data(ra=[1, 2, 3], dec=[2, 3, 4], c=[4, 5, 6])
        self.application = GlueApplication()
        self.dc = self.application.data_collection
        self.dc.append(self.d)
        self.hub = self.dc.hub
        self.session = self.application.session
        self.viewer = self.application.new_data_viewer(AladinLiteViewer)
        self.options = self.viewer.options_widget()

    def register(self):
        self.viewer.register_to_hub(self.hub)

    def test_add_data(self):
        self.viewer.add_data(self.d)
        self.viewer.state.ra_att = self.d.id['ra']
        self.viewer.state.dec_att = self.d.id['dec']
        assert len(self.viewer.layers) == 1

    def test_center(self):
        self.viewer.add_data(self.d)
        self.viewer.state.ra_att = self.d.id['ra']
        self.viewer.state.dec_att = self.d.id['dec']
        self.viewer.layers[0].center()
        assert_expression_value(self.viewer.aladin_widget, "aladin.getRaDec();", "[1, 1]")
