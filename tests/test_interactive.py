"""Test for interactive module."""

import unittest
from unittest.mock import patch

from argparse import Namespace
from starlet_setup.interactive import interactive_mode

class TestInteractiveMode(unittest.TestCase):
  def test_full_interactive_mode(self):
    """Should fill in all interactive fields based on user input."""

    inputs = [
      "my/repo",
      'y',
      'n',
      'y',
      '2',
      '1',
      "myprofile",
      "Debug",
      "out",
      "",
      'n'
    ]

    args = Namespace(
      repo=None,
      ssh=None,
      verbose=None,
      clean=None,
      mono_repo=None,
      profile=None,
      repos=None,
      build_type=None,
      build_dir=None,
      cmake_arg=None,
      no_build=None,
    )

    with patch("builtins.input", side_effect=inputs):
      result = interactive_mode(args)

    self.assertEqual(result.repo, "my/repo")
    self.assertTrue(result.ssh)
    self.assertFalse(result.verbose)
    self.assertTrue(result.clean)
    self.assertTrue(result.mono_repo)

    self.assertEqual(result.profile, "myprofile")
    self.assertIsNone(result.repos)

    self.assertEqual(result.build_type, "Debug")
    self.assertEqual(result.build_dir, "out")
    self.assertEqual(result.cmake_arg, [])
    self.assertFalse(result.no_build)