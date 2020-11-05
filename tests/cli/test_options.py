import os
from unittest import TestCase
import sys

from tradingkit.cli.cli import CLI


class TestOptions(TestCase):

    def test_empty(self):
        sys.argv = ['tk']
        self.assertRaises(SystemExit, CLI.main)

    def test_version(self):
        sys.argv = ['tk', '-v']
        self.assertRaises(SystemExit, CLI.main)

    def test_help(self):
        sys.argv = ['tk', '-h']
        self.assertRaises(SystemExit, CLI.main)

