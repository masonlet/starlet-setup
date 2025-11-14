"""Configuration file management"""


import json
from pathlib import Path
from typing import Any


def load_config() -> tuple[dict, Path | None]:
  """
  Load configuration from file, falling back to defaults.
  
  Returns:
    Configuration dictionary, empty dict if not config found
  """
  config_locations = [
    Path('.starlet-setup.json'),
    Path.home() / '.starlet-setup.json'
  ]

  invalid_count = 0
  for config_path in config_locations:
    if config_path.exists():
      try:
        with open(config_path) as f:
          return json.load(f), config_path
      except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in {config_path}: {e}")
        invalid_count += 1
        continue
      except PermissionError:
        print(f"Error: No permission to read the file in {config_path}.")
        invalid_count += 1
        continue
      except Exception as e:
        print(f"An unexpected error occurred reading {config_path}: {e}")
        invalid_count += 1
        continue


  if invalid_count != 0:
    print(f"Found {invalid_count} config file{'s' if invalid_count != 1 else ''} that had errors")
  else:
    print("Failed to find config file")
  return {}, None


def save_config(
  config: dict, 
  config_path: Path | None = None
) -> Path:
  """
  Save configuration to a file.

  Args:
    config: Configuration dictionary to save

  Returns:
      Path where config was saved
  """
  if config_path is None:
    config_path = Path('.starlet-setup.json')
  
  try:
    with open(config_path, 'w') as f:
      json.dump(config, f, indent=2)
  except PermissionError:
    print(f"Error: No permission to write to {config_path}")
    raise
  except Exception as e:
    print(f"An unexpected error occurred writing {config_path}: {e}")
    raise
  return config_path


def get_config_value(config: dict, key: str, default: Any) -> Any:
  """
  Get a config value with fallback to default.

  Args:
    config: Configuration dictionary
    key: Dot-separated key path (e.g, 'defaults.ssh')
    default: Default value if key not found
  """
  parts = key.split('.')
  value = config
  for part in parts:
    if not isinstance(value, dict) or part not in value:
      return default
    value = value[part]
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

  try:
    with open(config_path, 'w') as f:
      json.dump(default_config, f, indent=2)
  except PermissionError:
    print(f"Error: No permission to write to {config_path}")
    return
  except Exception as e:
    print(f"An unexpected error occurred writing {config_path}: {e}")
    return

  print(f"Created config file: {config_path.absolute()}")
  print("Edit this file to customize your defaults.")
  print("\nConfig files are checked in this order:")
  print(" 1. ./.starlet-setup.json (current directory)")
  print(" 2. ~/.starlet-setup.json (home directory)")