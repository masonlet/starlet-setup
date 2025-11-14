"""Tests for commands module."""

from argparse import Namespace
import pytest
from unittest.mock import patch
from starlet_setup.commands import (
    single_repo_mode,
    mono_repo_mode,
    _create_mono_repo_cmakelists
)


class TestSingleRepoMode:
  def test_clones_and_builds_new_repo(self, tmp_path, monkeypatch):
    """Should clone and build repository when it doesn't exist."""
    monkeypatch.chdir(tmp_path)
    args = Namespace (
      repo='user/repo',
      ssh=False,
      verbose=False,
      build_dir='build',
      build_type='Debug',
      clean=False,
      no_build=False,
      cmake_arg=None,
      config={}
    )

    def create_repo_on_clone(*args, **kwargs):
      if 'clone' in str(args):
        (tmp_path / 'repo').mkdir()
        
    with patch('starlet_setup.commands.run_command', side_effect=create_repo_on_clone) as mock_run:
      single_repo_mode(args)
      assert mock_run.call_count >= 2
      assert any ('git' in str(c) and 'clone' in str(c) for c in mock_run.call_args_list)


  def test_updates_existing_repo_when_confirmed(self, tmp_path, monkeypatch):
    """Should update existing repository when user confirms."""
    monkeypatch.chdir(tmp_path)
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    args = Namespace(
      repo='user/repo',
      ssh=False,
      verbose=False,
      build_dir='build',
      build_type='Debug',
      clean=False,
      no_build=False,
      cmake_arg=None,
      config={}
    )

    with patch('starlet_setup.commands.run_command') as mock_run, \
         patch('builtins.input', return_value='y'):
      single_repo_mode(args)
      assert any('pull' in str(c) for c in mock_run.call_args_list)


  def test_skips_build_when_no_build_flag_set(self, tmp_path, monkeypatch):
    """Should skip build step when no_build is True."""
    monkeypatch.chdir(tmp_path)
    args = Namespace(
      repo='user/repo',
      ssh=False,
      verbose=False,
      build_dir='build',
      build_type='Debug',
      clean=False,
      no_build=True,
      cmake_arg=None,
      config={}
    )

    with patch('starlet_setup.commands.run_command') as mock_run, \
         patch('builtins.input', return_value='n'):
      (tmp_path / 'repo').mkdir() 
      single_repo_mode(args)
      assert not any('--build' in str(c) for c in mock_run.call_args_list)


  def test_uses_ssh_when_requested(self, tmp_path, monkeypatch):
    """Should use SSH URL when ssh flag is True."""
    monkeypatch.chdir(tmp_path)
    args = Namespace(
      repo='user/repo',
      ssh=True,
      verbose=False,
      build_dir='build',
      build_type='Debug',
      clean=False,
      no_build=True,
      cmake_arg=None,
      config={}
    )

    def create_repo_on_clone(*args, **kwargs):
      if 'clone' in str(args):
        (tmp_path / 'repo').mkdir()

    with patch('starlet_setup.commands.run_command', side_effect=create_repo_on_clone) as mock_run:
      single_repo_mode(args)
      clone_call = [c for c in mock_run.call_args_list if 'clone' in str(c)][0]
      assert 'git@github.com' in str(clone_call)


class TestMonoRepoMode:
  def test_clones_multiple_repos(self, tmp_path, monkeypatch):
    """Should clone all specified repositories."""
    monkeypatch.chdir(tmp_path)
    args = Namespace (
      repo='user/test-repo',
      repos=['user/lib1', 'user/lib2'],
      profile=None,
      ssh=False,
      verbose=False,
      mono_dir='mono',
      no_build=False,
      cmake_arg=None,
      config={}
    )

    with patch('starlet_setup.commands.clone_repository') as mock_clone, \
         patch('starlet_setup.commands.run_command'):
      mono_repo_mode(args)
      assert mock_clone.call_count >= 3


  def test_uses_profile_repos(self, tmp_path, monkeypatch):
    """Should use repositories from specified profile."""
    monkeypatch.chdir(tmp_path)
    config = {
      'profiles': {
        'myprofile': ['user/lib1', 'user/lib2']
      }
    }
    args = Namespace(
      repo='user/test-repo',
      repos=None,
      profile='myprofile',
      ssh=False,
      verbose=False,
      mono_dir='mono',
      no_build=False,
      cmake_arg=None,
      config=config
    )

    with patch('starlet_setup.commands.clone_repository') as mock_clone, \
         patch('starlet_setup.commands.run_command'):
      mono_repo_mode(args)
      assert mock_clone.call_count >= 3


  def test_errors_on_missing_profile(self, tmp_path, monkeypatch):
    """Should exit when specified profile doesn't exist."""
    monkeypatch.chdir(tmp_path)
    args = Namespace (
      repo='user/test-repo',
      repos=None,
      profile='nonexistent',
      ssh=False,
      verbose=False,
      mono_dir='mono',
      no_build=False,
      cmake_arg=None,
      config={'profiles': {}}
    )
    with pytest.raises(SystemExit):
      mono_repo_mode(args)


  def test_creates_cmakelists(self, tmp_path, monkeypatch):
    """Should create root CMakeLists.txt."""
    monkeypatch.chdir(tmp_path)
    args = Namespace(
      repo='user/test-repo',
      repos=['user/lib1'],
      profile=None,
      ssh=False,
      verbose=False,
      mono_dir='mono',
      no_build=False,
      cmake_arg=None,
      config={}
    )
    
    with patch('starlet_setup.commands.clone_repository'), \
      patch('starlet_setup.commands.run_command'):
      mono_repo_mode(args)
      
      cmake_file = tmp_path / 'mono' / 'CMakeLists.txt'
      assert cmake_file.exists()


class TestCreateMonoRepoCMakeLists:
  def test_creates_cmakelists_with_repos(self, tmp_path):
    """Should create CMakeLists.txt with all repositories."""
    repos = ['user/lib1', 'user/lib2']
    _create_mono_repo_cmakelists(tmp_path, 'test-repo', repos)
    
    cmake_file = tmp_path / 'CMakeLists.txt'
    assert cmake_file.exists()
    
    content = cmake_file.read_text()
    assert 'lib1' in content
    assert 'lib2' in content
    assert 'test-repo' in content