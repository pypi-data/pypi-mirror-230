# -*- coding: UTF-8 -*-
# Copyright 2014-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from os.path import join, dirname
from atelier.test import TestCase
from lino_xl.lib.finan.validate import validate_pain001

class SepaTests(TestCase):
    def test_sepa(self):
        fn = join(dirname(__file__), 'finan.PaymentOrder-63.xml')
        validate_pain001(fn)
