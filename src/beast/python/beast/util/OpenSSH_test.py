from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from beast.util import String
from beast.util import OpenSSH

class OpenSSH_test(TestCase):
    def test_parse_version_number(self):
        self.assertEquals(OpenSSH.parse_version_number('0x0090300f'), [0, 9, 3, ''])
        self.assertEquals(OpenSSH.parse_version_number('0x0090301f'), [0, 9, 3, 'a'])
        self.assertEquals(OpenSSH.parse_version_number('0x0090400f'), [0, 9, 4, ''])
        self.assertEquals(OpenSSH.parse_version_number('0x102031af'), [1, 2, 3, 'z'])

    def test_split_version_string(self):
        self.assertEquals(OpenSSH.split_version_string('0.9.3'), [0, 9, 3, ''])
        self.assertEquals(OpenSSH.split_version_string('0.9.3a'), [0, 9, 3, 'a'])
        self.assertEquals(OpenSSH.split_version_string('0.9.4'), [0, 9, 4, ''])
        self.assertEquals(OpenSSH.split_version_string('1.2.3z'), [1, 2, 3, 'z'])
