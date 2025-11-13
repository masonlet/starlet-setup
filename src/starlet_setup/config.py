import json
from pathlib import Path

def load_config():
  """Load configuration from file, falling back to defaults."""
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


def save_config(config):
  """Save configuration to a file."""
  config_path = Path('.starlet-setup.json')
  if not config_path.exists():
    config_path = Path.home() / '.starlet-setup.json'

  with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

  return config_path


def get_config_value(config, key, default):
  """Get a config value with fallback to default."""
  parts = key.split('.')
  value = config
  for part in parts:
    if isinstance(value, dict) and part in value:
      value = value[part]
    else:
      return default
  return value


def create_default_config():
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
