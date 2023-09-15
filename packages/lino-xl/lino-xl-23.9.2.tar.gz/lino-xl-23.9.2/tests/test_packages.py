from lino.utils.pythontest import TestCase
from lino_xl import SETUP_INFO


class PackagesTests(TestCase):
    def test_01(self):
        self.run_packages_test(SETUP_INFO['packages'])
