"""Tests for repository module."""

from pathlib import Path

import pytest
from unittest.mock import patch, Mock
from starlet_setup.repository import (
    resolve_repo_url,
    get_default_repos,
    clone_repository
)

class TestResolveRepoUrl:
  def test_returns_full_url_unchanged(self):
    """Should return full URLs as-is."""
    https_url = "https://github.com/user/repo.git"
    assert resolve_repo_url(https_url) == https_url
    
    git_url = "git@github.com:user/repo.git"
    assert resolve_repo_url(git_url) == git_url

  def test_converts_shorthand_to_https(self):
    """Should convert username/repo to HTTPS."""
    result = resolve_repo_url("masonlet/starlet-math")
    assert result == "https://github.com/masonlet/starlet-math.git"

  def test_converts_shorthand_to_ssh(self):
    """Should convert username/repo to SSH when requested."""
    result = resolve_repo_url("masonlet/starlet-math", use_ssh=True)
    assert result == "git@github.com:masonlet/starlet-math.git"

class TestGetDefaultRepos:
  def test_returns_repos_from_config(self):
    """Should use profiles.default from config when available."""
    config = {
      "profiles": {
        "default": ["user/repo1", "user/repo2"]
      }
    }
    result = get_default_repos(config)
    assert result == ["user/repo1", "user/repo2"]

  def test_returns_hardcoded_defaults_when_config_empty(self):
    """Should fall back to built-in Starlet repos."""
    result = get_default_repos({})
    assert "masonlet/starlet-math" in result
    assert "masonlet/starlet-engine" in result
    assert len(result) == 7

class TestCloneRepository:
  def test_clones_repository_successfully(self, tmp_path, capsys):
    """Should clone repo to target directory."""
    with patch('starlet_setup.repository.run_command') as mock_run:
      clone_repository("user/repo", tmp_path, use_ssh=False, verbose=False)
      
      mock_run.assert_called_once()
      command_args, command_kwargs = mock_run.call_args
      assert command_args[0][:2] == ['git', 'clone']
      assert 'https://github.com/user/repo.git' in command_args[0]
      assert command_kwargs['cwd'] == tmp_path

    assert "Cloning repo" in capsys.readouterr().out

  def test_skips_existing_directory(self, tmp_path, capsys):
    """Should skip cloning if directory exists."""
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    with patch('starlet_setup.repository.run_command') as mock_run:
      clone_repository("user/repo", tmp_path, use_ssh=False, verbose=False)
      mock_run.assert_not_called()

    assert "already exists" in capsys.readouterr().out

  def test_uses_ssh_when_requested(self, tmp_path):
    """Should use SSH when use_ssh is True."""
    with patch('starlet_setup.repository.run_command') as mock_run:
      clone_repository("user/repo", tmp_path, use_ssh=True, verbose=False)
      
      command_args, _ = mock_run.call_args
      assert 'git@github.com:user/repo.git' in command_args[0]

  def test_raises_on_clone_failure(self, tmp_path):
    """Should propagate SystemExit when git clone fails."""
    with patch('starlet_setup.repository.run_command') as mock_run, \
         pytest.raises(SystemExit):
      mock_run.side_effect = SystemExit(1)
      clone_repository("user/repo", tmp_path, use_ssh=False, verbose=False)