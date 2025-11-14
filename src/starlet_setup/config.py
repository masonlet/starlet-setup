"""Configuration file management"""

import sys
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
  config: dict[str, Any], 
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


def get_config_value(
  config: dict[str, Any], 
  key: str, 
  default: Any
) -> Any:
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
    "configs": {
      "default": {
        "ssh": False,
        "build_type": "Debug",
        "build_dir": "build",
        "mono_dir": "build_starlet",
        "no_build": False,
        "verbose": False,   
        "cmake_arg": []
      }
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


def add_config(
  config: dict[str, Any], 
  name: str,
  new_config: dict[str, Any]
) -> None:
  """
  Add a new config to the configuration.

  Args:
    config: Configuration dictionary
    config_name: Configuration name
  """
  if 'configs' not in config:
    config['configs'] = {}

  if name in config['configs']:
    print(f"Warning: Configuration '{name}' already exists.")
    if input("Overwrite? (y/n): ").lower() != 'y':
      print("Aborted.")
      return
    
  config['configs'][name] = new_config

  config_path = save_config(config)

  config_new = config['configs'][name]
  print(f"Configuration '{name} added successfully to {config_path}")
  print(f"Configuration details:")
  print(f"  SSH: {config_new.get('ssh')}")
  print(f"  Build Type: {config_new.get('build_type')}")
  print(f"  Build Directory: {config_new.get('build_dir')}")
  print(f"  Mono-build Directory: {config_new.get('mono_dir')}")
  print(f"  No-build flag: {config_new.get('no_build')}")
  print(f"  Verbose flag: {config_new.get('verbose')}")
  cmake_args = config_new.get("cmake_args", [])
  if cmake_args:
    if len(cmake_args) == 1:
      print(f"  CMake argument: {cmake_args[0]}")
    else:
      print("  Cmake arguments: ")
      for arg in cmake_args:
        print(f"    {arg}")
  print(f"\nUsage: {Path(sys.argv[0]).name} username/repo --config {name}\n")


def remove_config(
  config: dict[str, Any],
  name: str
) -> None:
  """
  Remove a config from the configuration.

  Args:
    config: Configuration dictionary
    name: Config name to remove
  """
  if 'configs' not in config or name not in config['configs']:
    print(f"\nWarning: Config '{name}' not found.\n")
    return
  
  config_new = config['configs'][name]
  print(f"Config {name}")
  print(f"Configuration details:")
  print(f"  SSH: {config_new.get('ssh')}")
  print(f"  Build Type: {config_new.get('build_type')}")
  print(f"  Build Directory: {config_new.get('build_dir')}")
  print(f"  Mono-build Directory: {config_new.get('mono_dir')}")
  print(f"  No-build flag: {config_new.get('no_build')}")
  print(f"  Verbose flag: {config_new.get('verbose')}")

  if input("\nAre you sure you want to remove this config? (y/n): ").lower() != 'y':
    print("Aborted.")
    return

  del config['configs'][name]
  config_path = save_config(config)
  print(f"\nConfig '{name}' was successfully removed")
  print(f"Configuration saved to: {config_path}\n")


def list_configs(config: dict[str, Any]) -> None:
  print("Available configs:")
  configs = get_config_value(config, 'configs', {})

  if not configs:
    print("  No configurations created.")
    print("  Run with --init-config to create a default configuration.")
    return
  
  print("Configurations:")
  for name, cfg in configs.items():
    print(f"\n{name}:")
    print(f"  SSH: {cfg.get('ssh')}")
    print(f"  Build Type: {cfg.get('build_type')}")
    print(f"  Build Directory: {cfg.get('build_dir')}")
    print(f"  Mono-build Directory: {cfg.get('mono_dir')}")
    print(f"  No-build flag: {cfg.get('no_build')}")
    print(f"  Verbose flag: {cfg.get('verbose')}")
    cmake_args = cfg.get("cmake_args", [])
    if not cmake_args:
      print()
    elif len(cmake_args) == 1:
      print(f"  CMake argument: {cmake_args[0]}")
    else:
      print("  CMake arguments:")
      for arg in cmake_args:
        print(f"    {arg}")