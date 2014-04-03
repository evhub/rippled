from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from beast.util.ReadEnvFile import read_env_file

JSON = """
{
  "foo": "FOO",
  "bar": "BAR"
}"""

class test_ReadEnvFile(TestCase):
  def testReadJson(self):
    self.assertEqual(read_env_file(JSON), {'foo': 'FOO', 'bar': 'BAR'})
