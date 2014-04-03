from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase
from beast.util.ReadEnvFile import read_env_file

JSON = """
{
  "FOO": "foo",
  "BAR": "bar bar bar"
}"""

ENV = """
# An env file.
FOO=foo
export BAR="bar bar bar"
# export BAZ=baz should be ignored.

"""

RESULT = {'FOO': 'foo', 'BAR': 'bar bar bar'}

BAD_ENV = ENV + """
This line isn't right.
NO SPACES IN NAMES="valid value"
"""

class test_ReadEnvFile(TestCase):
  def testReadJson(self):
    self.assertEqual(read_env_file(JSON), RESULT)

  def testReadEnv(self):
    self.assertEqual(read_env_file(ENV), RESULT)
