"""Tests for utils module."""

import subprocess

import pytest
from unittest.mock import patch, Mock
from starlet_setup.utils import (
    check_prerequisites,
    run_command
)


class TestCheckPrerequisites:
  def test_passes_when_tools_installed(self):
    """Should complete without error when git and cmake exist."""
    with patch('shutil.which', return_value='/usr/bin/git'):
      check_prerequisites()

  def test_exits_when_tools_missing(self, capsys):
    """Should exit with error message when tools missing."""
    with patch('shutil.which', return_value=None), pytest.raises(SystemExit) as exc_info:
      check_prerequisites()

    assert exc_info.value.code == 1
    assert "Missing required tools: git, cmake" in capsys.readouterr().out

  def test_shows_found_tools_in_verbose_mode(self, capsys):
    """Should print found tools when verbose enabled."""
    with patch('shutil.which', return_value='/usr/bin/tool'):
      check_prerequisites(verbose=True)

    output = capsys.readouterr().out
    assert "Found git" in output
    assert "Found cmake" in output

class TestRunCommand:
  def test_executes_command_successfully(self):
    """Should run command and return CompletedProcess."""
    with patch('subprocess.run') as mock_run:
      mock_run.return_value = Mock(stdout="output", returncode=0)
      result = run_command(['echo', 'test'])
      mock_run.assert_called_once()
      assert result.returncode == 0

  def test_exits_on_command_failure(self, capsys):
    """Should exit when command returns non-zero."""
    with patch('subprocess.run') as mock_run, pytest.raises(SystemExit) as exc_info:
      mock_run.side_effect = subprocess.CalledProcessError(
        1, ['false'], stderr="error"
      )
      run_command(['false'])

    assert exc_info.value.code == 1
    assert "Error running command" in capsys.readouterr().out

  def test_exits_on_command_not_found(self, capsys):
    """Should exit when command does not exist."""
    with patch('subprocess.run') as mock_run, pytest.raises(SystemExit) as exc_info:
      mock_run.side_effect = FileNotFoundError()
      run_command(['nonexistent'])

    assert exc_info.value.code == 1
    assert "Command not found: nonexistent" in capsys.readouterr().out

  def test_uses_working_directory(self, tmp_path):
    """Should execute command in specific directory."""
    with patch('subprocess.run') as mock_run:
      mock_run.return_value = Mock(returncode=0)
      run_command(['ls'], cwd=tmp_path)

      assert mock_run.call_args[1]['cwd'] == tmp_path

  def test_prints_details_in_verbose_mode(self, capsys):
    """Should show command and directory in verbose mode."""
    with patch('subprocess.run') as mock_run:
      mock_run.return_value = Mock(stdout="output", returncode=0)
      run_command(['echo', 'test'], cwd='/tmp', verbose=True)

    output = capsys.readouterr().out
    assert "Running: echo test" in output
    assert "in directory: /tmp" in output