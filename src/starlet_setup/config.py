"""Configuration file management"""


import json
from pathlib import Path
from typing import Any


def load_config() -> dict:
  """
  Load configuration from file, falling back to defaults.
  
  Returns:
    Configuration dictionary, empty dict if not config found
  """
  config_locations = [
    Path('.starlet-setup.json'),
    Path.home() / '.starlet-setup.json'
  ]

  for config_path in config_locations:
    if config_path.exists():
      try:
        with open(config_path) as f:
          return json.load(f)
      except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {config_path}: {e}")
        continue

  return {}


def save_config(config) -> Path:
  """
  Save configuration to a file.

  Args:
    config: Configuration dictionary to save

  Returns:
      Path where config was saved
  """
  config_path = Path('.starlet-setup.json')
  if not config_path.exists():
    config_path = Path.home() / '.starlet-setup.json'

  with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

  return config_path


def get_config_value(config: dict, key: str, default: Any) -> Any:
  """
  Get a config value with fallback to default.

  Args:
    config: Configuration dictionary
    key: Dot-seperated key path (e.g, 'defaults.ssh')
    default: Default value if key not found
  """
  parts = key.split('.')
  value = config
  for part in parts:
    if isinstance(value, dict) and part in value:
      value = value[part]
    else:
      return default
  return value


def create_default_config() -> None:
  """Create a default configuration file."""
  default_config = {
    "defaults": {
      "ssh": False,
      "build_type": "Debug",
      "build_dir": "build",
      "mono_dir": "build_starlet",
      "no_build": False,
      "verbose": False,   
      "cmake_arg": []
    },
    "profiles": {
      "default": [
        "masonlet/starlet-math",
        "masonlet/starlet-logger",
        "masonlet/starlet-controls",
        "masonlet/starlet-scene",
        "masonlet/starlet-graphics",
        "masonlet/starlet-serializer",
        "masonlet/starlet-engine"
      ]
    }
  }

  config_path = Path('.starlet-setup.json')

  if config_path.exists():
    if input(f"{config_path} already exists. Overwrite? (y/n): ").lower() != 'y':
      print("Aborted.")
      return

  with open(config_path, 'w') as f:
    json.dump(default_config, f, indent=2)

  print(f"Created config file: {config_path.absolute()}")
  print("Edit this file to customize your defaults.")
  print("\nConfig files are checked in this order:")
  print(" 1. ./.starlet-setup.json (current directory)")
  print(" 2. ~/.starlet-setup.json (home directory)")
