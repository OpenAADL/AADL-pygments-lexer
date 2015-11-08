"""Implementation of a Pygments Lexer for the AADL language."""

from setuptools import setup, find_packages

__author__ = 'Jerome Hugues, <hugues.jerome@gmail.com>'

setup (
  name='aadllexer',
  version='0.1.0',
  description=__doc__,
  author=__author__,
  packages=["aadllexer"],
  entry_points =
  """
  [pygments.lexers]
  aadllexer = aadllexer.lexer:AADLLexer
  """,
)
