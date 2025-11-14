"""Tests for profiles module."""

from pathlib import Path
import pytest
from unittest.mock import patch
from starlet_setup.profiles import (
  add_profile,
  remove_profile,
  list_profiles
)


class TestAddProfile:
  def test_adds_new_profile(self, capsys):
    """Should add new profile to config."""
    config = {'profiles': {}}

    with patch('starlet_setup.config.save_config', return_value=Path('config.json')):
      add_profile(config, ['myprofile', 'user/repo1', 'user/repo2'])

    assert 'myprofile' in config['profiles']
    assert config['profiles']['myprofile'] == ['user/repo1', 'user/repo2']
    assert "added successfully" in capsys.readouterr().out


  def test_creates_profiles_key_if_missing(self):
    """Should create profiles dict if not present."""
    config = {}

    with patch('starlet_setup.config.save_config', return_value=Path('config.json')):
      add_profile(config, ['myprofile', 'user/repo1'])

    assert 'profiles' in config
    assert 'myprofile' in config['profiles']

  
  def test_overwrites_existing_profile_when_confirmed(self):
    """Should overwrite existing profile when user confirms."""
    config = {'profiles': {'myprofile': ['old/repo']}}

    with patch('starlet_setup.config.save_config', return_value=Path('config.json')), \
         patch('builtins.input', return_value='y'):
      add_profile(config, ['myprofile', 'new/repo1', 'new/repo2'])
      
    assert config['profiles']['myprofile'] == ['new/repo1', 'new/repo2']


  def test_aborts_overwrite_when_not_confirmed(self, capsys):
    """Should not overwrite when user declines."""
    config = {'profiles': {'myprofile': ['old/repo']}}

    with patch('starlet_setup.config.save_config'), \
         patch('builtins.input', return_value='n'):
      add_profile(config, ['myprofile', 'new/repo1'])
      
    assert config['profiles']['myprofile'] == ['old/repo']
    assert "Aborted" in capsys.readouterr().out

  
  def test_errors_on_insufficient_arguments(self):
    """Should exit when not enough arguments provided."""
    config = {}
        
    with pytest.raises(SystemExit):
      add_profile(config, ['myprofile'])


class TestRemoveProfile:
  def test_removes_existing_profile(self):
    """Should remove profile when confirmed."""
    config = {'profiles': {'myprofile': ['user/repo1', 'user/repo2']}}
    
    with patch('starlet_setup.config.save_config', return_value=Path('config.json')), \
         patch('builtins.input', return_value='y'):
      remove_profile(config, 'myprofile')

    assert 'myprofile' not in config['profiles']

  
  def test_aborts_removal_when_not_confirmed(self, capsys):
    """Should not remove profile when declined."""
    config = {'profiles': {'myprofile': ['user/repo1', 'user/repo2']}}
    
    with patch('builtins.input', return_value='n'):
      remove_profile(config, 'myprofile')

    assert 'myprofile' in config['profiles']
    assert "Aborted" in capsys.readouterr().out

  
  def test_handles_nonexistent_profile(self, capsys):
    """Should warn when profile doesn't exist."""
    config = {'profiles': {}}

    remove_profile(config, 'nonexistent')
    assert "not found" in capsys.readouterr().out


class TestListProfiles:
  def test_lists_all_profiles(self, capsys):
    """Should display all configured profiles."""
    config = {
      'profiles': {
        'profile1': ['user/repo1', 'user/repo2'],
        'profile2': ['user/repo3']
      }
    }

    list_profiles(config)

    output = capsys.readouterr().out
    assert 'profile1' in output
    assert 'profile2' in output
    assert 'user/repo1' in output
    assert 'user/repo3' in output


  def test_handles_empty_profiles(self, capsys):
    """Should show message when no profiles configured."""
    config = {'profiles': {}}

    list_profiles(config)

    assert "No profiles configured" in capsys.readouterr().out


  def test_handles_missing_profiles_key(self, capsys):
    """Should handle config without profiles key."""
    config = {}
    list_profiles(config)
    assert "No profiles configured" in capsys.readouterr().out