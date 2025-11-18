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
      ssh=False,
      verbose=False,
      clean=False,
      mono_repo=False,
      profile=None,
      repos=None,
      build_type="Release",
      build_dir="build",
      cmake_arg=None,
      no_build=False,
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

  def test_uses_defaults_on_empty_input(self):
    """Should use default values when user presses Enter without input."""
    inputs = [
      "my/repo",
      '',
      '',
      '',
      '1',
      '',
      '',
      '',
      ''
    ]

    args = Namespace(
      repo=None,
      ssh=False,
      verbose=False,
      clean=False,
      mono_repo=False,
      profile=None,
      repos=None,
      build_type="Release",
      build_dir="build",
      cmake_arg=None,
      no_build=False,
    )

    with patch("builtins.input", side_effect=inputs):
      result = interactive_mode(args)

    self.assertFalse(result.ssh)
    self.assertFalse(result.verbose)
    self.assertFalse(result.clean)
    self.assertEqual(result.build_type, "Release")
    self.assertEqual(result.build_dir, "build")
    self.assertFalse(result.no_build)

  def test_respects_cli_flags(self):
    """Should skip prompts for values already set via CLI flags."""
    inputs = [
      "my/repo",
      'n',
      '1',
      "",
      "",
      "",
      'n'
    ]

    args = Namespace(
      repo=None,
      ssh=True,    
      verbose=True, 
      clean=False,
      mono_repo=False,
      profile=None,
      repos=None,
      build_type="Release",
      build_dir="custom",
      cmake_arg=["-DBUILD_TESTS=ON"],
      no_build=False,
    )

    with patch("builtins.input", side_effect=inputs):
      result = interactive_mode(args)

    self.assertEqual(result.repo, "my/repo")
    self.assertTrue(result.ssh)  
    self.assertTrue(result.verbose)  
    self.assertFalse(result.mono_repo)
    self.assertEqual(result.cmake_arg, ["-DBUILD_TESTS=ON"]) 

  def test_mono_repo_with_manual_repos(self):
    """Should handle mono-repo mode with manual repository list."""
    inputs = [
      "my/repo",
      'n',
      'n', 
      'n',
      '2',  
      '2',  
      "user/lib1 user/lib2",
      "Release",
      "build",
      "-DBUILD_TESTS=ON",
      'n'
    ]

    args = Namespace(
      repo=None,
      ssh=False,
      verbose=False,
      clean=False,
      mono_repo=False,
      profile=None,
      repos=None,
      build_type="Debug",
      build_dir="build",
      cmake_arg=None,
      no_build=False,
    )

    with patch("builtins.input", side_effect=inputs):
      result = interactive_mode(args)

    self.assertTrue(result.mono_repo)
    self.assertEqual(result.repos, ["user/lib1", "user/lib2"])
    self.assertIsNone(result.profile)
    self.assertEqual(result.cmake_arg, ["-DBUILD_TESTS=ON"])

  def test_skips_mono_repo_prompts_when_repos_provided(self):
    """Should skip mono-repo choice prompts when --repos already provided."""
    inputs = [
      "my/repo",
      'n',
      'n',
      'n',
      '2',  
      "",
      "",
      "Debug",
      "build",
      "",
      'n'
    ]

    args = Namespace(
      repo=None,
      ssh=False,
      verbose=False,
      clean=False,
      mono_repo=False,
      profile=None,
      repos=["user/lib1"], 
      build_type="Release",
      build_dir="build",
      cmake_arg=None,
      no_build=False,
    )

    with patch("builtins.input", side_effect=inputs):
      result = interactive_mode(args)

    self.assertTrue(result.mono_repo)
    self.assertEqual(result.repos, ["user/lib1"])  
    self.assertIsNone(result.profile)

  def test_skips_mono_repo_prompts_when_profile_provided(self):
    """Should skip mono-repo choice prompts when --profile already provided."""
    inputs = [
      "my/repo",
      'n',
      'n',
      'n',
      '2',  
      "",
      "",
      "",
      'n'
    ] 

    args = Namespace(
      repo=None,
      ssh=False,
      verbose=False,
      clean=False,
      mono_repo=False,
      profile="myprofile",
      repos=None,
      build_type="Release",
      build_dir="build",
      cmake_arg=None,
      no_build=False,
    )

    with patch("builtins.input", side_effect=inputs):
      result = interactive_mode(args)

    self.assertTrue(result.mono_repo)
    self.assertEqual(result.profile, "myprofile") 
    self.assertIsNone(result.repos)