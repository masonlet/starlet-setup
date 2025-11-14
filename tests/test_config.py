"""Tests for config module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from starlet_setup.config import (
  load_config,
  save_config,
  get_config_value,
  create_default_config
)


@pytest.fixture
def valid_config():
  """Sample valid config."""
  return {
    "defaults": {"ssh": True, "verbose": False},
    "profiles": {"default": ["repo1", "repo2"]}
  }


class TestLoadConfig:
  def test_loads_from_current_directory(self, tmp_path, valid_config, monkeypatch):
    """Should prioritize current directory config."""
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / ".starlet-setup.json"
    with open(config_path, 'w') as f:
      json.dump(valid_config, f)

    config, path = load_config()
    assert config == valid_config
    assert path.resolve() == config_path.resolve()

  def test_returns_empty_dict_when_no_config_exists(self, tmp_path, monkeypatch, capsys):
    """Should return empty dict when no config found."""
    monkeypatch.chdir(tmp_path)
    config, path = load_config()
    assert config == {}
    assert path is None
    assert "Failed to find config file" in capsys.readouterr().out


  def test_handles_invalid_json(self, tmp_path, monkeypatch, capsys):
    """Should handle malformed JSON."""
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / ".starlet-setup.json"
    with open(config_path, 'w') as f:
      f.write("{invalid json")

    config, path = load_config()
    assert config == {}
    captured = capsys.readouterr()
    assert "Invalid JSON" in captured.out


class TestSaveConfig:
  def test_saves_config_successfully(self, tmp_path, valid_config):
    """Should write config to specified path."""
    config_path = tmp_path / "test-config.json"
    result_path = save_config(valid_config, config_path)

    assert result_path == config_path
    with open(config_path) as f:
      saved_config = json.load(f)
    assert saved_config == valid_config

  def test_uses_default_path_when_none_provided(self, tmp_path, valid_config, monkeypatch):
    """Should use default to .starlet-setup.json in current directory."""
    monkeypatch.chdir(tmp_path)
    result_path = save_config(valid_config)

    assert result_path == Path('.starlet-setup.json')
    assert (tmp_path / ".starlet-setup.json").exists()


class TestGetConfigValue:
  def test_retrieves_nested_value(self, valid_config):
    """Should navigate dot-separated keys."""
    assert get_config_value(valid_config, "defaults.ssh", False) is True
    assert get_config_value(valid_config, "defaults.verbose", True) is False

  def test_returns_default_when_key_missing(self, valid_config):
    """Should return default for non-existent keys."""
    assert get_config_value(valid_config, "fake.key", "default") == "default"
    assert get_config_value(valid_config, "defaults.numbermissing", 42) == 42

  def test_handles_non_dict_intermediate_values(self):
    """Should return default when path encounters non-dict."""
    config = {"key": "string_value"}
    assert get_config_value(config, "key.nested", "default") == "default"


class TestCreateDefaultConfig:
  def test_creates_config_file(self, tmp_path, monkeypatch):
    """Should create default config file."""
    monkeypatch.chdir(tmp_path)
    with patch('builtins.input', return_value='y'):
      create_default_config()

    config_path = tmp_path / ".starlet-setup.json"
    assert config_path.exists()
    with open(config_path) as f:
      config = json.load(f)
    assert "defaults" in config
    assert "profiles" in config

  def test_prompts_before_overwriting(self, tmp_path, monkeypatch, capsys):
    """Should ask permission before overwriting existing config."""
    monkeypatch.chdir(tmp_path)
    config_path = tmp_path / ".starlet-setup.json"
    config_path.write_text("{}")

    with patch('builtins.input', return_value='n'):
      create_default_config()

    assert "Aborted" in capsys.readouterr().out
    assert config_path.read_text() == "{}"