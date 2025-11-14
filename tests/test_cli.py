"""Tests for CLI module."""

import pytest
from unittest.mock import patch
from starlet_setup.cli import parse_args


class TestParseArgs:
  def test_parses_basic_repository(self):
    """Should parse repository argument."""
    with patch('sys.argv', ['prog', 'user/repo']):
      args = parse_args()
      assert args.repo == 'user/repo'
      assert args.ssh is False
      assert args.verbose is False


  def test_applies_config_defaults(self):
    """Should use config values as default."""
    config = {
      "defaults": {"ssh": True, "verbose": True, "build_type": "Release"}
    }
    with patch('starlet_setup.cli.load_config', return_value=(config,None)), \
         patch('sys.argv', ['prog', 'user/repo']):
      args = parse_args()
      assert args.ssh is True
      assert args.verbose is True
      assert args.build_type == "Release"


  def test_command_line_overrides_config(self):
    """Should allow CLI args to override config defaults."""
    config = {"defaults": {"ssh": False}}
    with patch('starlet_setup.cli.load_config', return_value=(config, None)), \
         patch('sys.argv', ['prog', 'user/repo', '--ssh']):
      args = parse_args()
      assert args.ssh is True


  def test_requires_repo_argument(self):
    """Should error when repo not provided and no special flags."""
    with patch('sys.argv', ['prog']), pytest.raises(SystemExit):
      parse_args()


  def test_allows_config_management_without_repo(self):
    """Should allow profile commands without repo argument."""
    with patch('sys.argv', ['prog', '--list-profiles']):
      args = parse_args()
      assert args.list_profiles is True


  def test_enables_mono_repo_with_repos_flag(self):
    """Should enable mono-repo mode when --repos specified."""
    with patch('sys.argv', ['prog', 'user/repo', '--repos', 'lib1', 'lib2']):
      args = parse_args()
      assert args.mono_repo is True
      assert args.repos == ['lib1', 'lib2']


  def test_enables_mono_repo_with_profile_flag(self):
    """Should enable mono-repo mode when --profile specified."""
    with patch('sys.argv', ['prog', 'user/repo', '--profile']):
      args = parse_args()
      assert args.mono_repo is True
      assert args.profile == 'default'


  def test_profile_uses_default_when_no_name_given(self):
    """Should use 'default' profile name when none specified."""
    with patch('sys.argv', ['prog', 'user/repo', '--profile']):
      args = parse_args()
      assert args.profile == 'default'


  def test_errors_on_both_repos_and_profile(self):
    """Should error when both --repos and --profile specified."""
    with patch('sys.argv', ['prog', 'user/repo', '--repos', 'lib1', '--profile']), \
         pytest.raises(SystemExit):
      parse_args()


  def test_parses_build_options(self):
    """Should parse build configuration options."""
    with patch('sys.argv', ['prog', 'user/repo', '-b', 'Release', '-d', 'mybuild', '--no-build']):
      args = parse_args()
      assert args.build_type == 'Release'
      assert args.build_dir == 'mybuild'
      assert args.no_build is True


  def test_parses_cmake_arguments(self):
    """Should parse additional CMake arguments."""
    with patch('sys.argv', ['prog', 'user/repo', '--cmake-arg=-DTEST=ON', '--cmake-arg=-DDEBUG=OFF']):
      args = parse_args() 
      assert args.cmake_arg == ['-DTEST=ON', '-DDEBUG=OFF']


  def test_attaches_config_to_args(self):
    """Should attach loaded config to args namespace."""
    config = {"defaults": {}}
    with patch('starlet_setup.cli.load_config', return_value=(config, None)), \
         patch('sys.argv', ['prog', 'user/repo']):
      args = parse_args()
      assert args.config == config