from sitebuilder.navbuilder import make_nav
from plumbum import LocalPath


HERE = LocalPath(__file__).up()


class TestNavBuilder(object):
    def test_whole(self):
        tplPath = HERE / 'data' / 'templates'
        print make_nav(str(tplPath), None)
        assert 0
