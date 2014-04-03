from __future__ import absolute_import, division, print_function, unicode_literals

from unittest import TestCase

from beast.util import String

class String_test(TestCase):
  def test_comments(self):
    self.assertEqual(String.remove_comment(''), '')
    self.assertEqual(String.remove_comment('#'), '')
    self.assertEqual(String.remove_comment('# a comment'), '')
    self.assertEqual(String.remove_comment('hello # a comment'), 'hello ')
    self.assertEqual(String.remove_comment(
      r'hello \# not a comment # a comment'),
      'hello # not a comment ')

  def test_remove_quotes(self):
    pass
