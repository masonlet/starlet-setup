"""Profile management for repository configurations."""

import sys
from pathlib import Path
from .config import get_config_value, save_config


def add_profile(config: dict, args_list: list[str]) -> None:
  """
  Add a new profile to the configuration.

  Args:
    config: Configuration dictionary
    args_list: [name, repo1, repo2, ...]

  Raises:
    SystemExit: If insufficient arguments provided  
  """
  if len(args_list) < 2:
    print("Error: --profile-add requires NAME REPO1 [REPO2 ...]")
    sys.exit(1)

  name = args_list[0]
  repos = args_list[1:]

  if 'profiles' not in config:
    config['profiles'] = {}

  if name in config['profiles']:
    print(f"Warning: Profile '{name}' already exists.")
    if input("Overwrite? (y/n): ").lower() != 'y':
      print("Aborted.")
      return
    
  config['profiles'][name] = repos

  config_path = save_config(config)
  print(f"Profile '{name}' added successfully")
  print(f"Configuration saved to: {config_path}")
  print(f"Profile details:")
  print(f"  Repositories ({len(repos)}):")
  for repo in repos:
    print(f"    - {repo}")
  print(f"\nUsage: {Path(sys.argv[0]).name} username/test-repo --profile {name}")


def remove_profile(config: dict, name: str) -> None:
  """
  Remove a profile from the configuration.

  Args:
    config: Configuration dictionary
    name: Profile name to remove
  """
  if 'profiles' not in config or name not in config['profiles']:
    print(f"Warning: Profile '{name}' not found.")
    return
  
  repos = config['profiles'][name]
  print(f"Profile '{name}'")
  print(f"  Libraries: {len(repos)}")
  for repo in repos:
    print(f"    - {repo}")

  if input("\nAre you sure you want to remove this profile? (y/n): ").lower() != 'y':
    print("Aborted.")
    return
  
  del config['profiles'][name]
  config_path = save_config(config)
  print(f"Profile '{name}' removed successfully")
  print(f"Configuration saved to: {config_path}")


def list_profiles(config: dict) -> None:
  """
  List all configured profiles.
  
  Args:
    config: Configuration dictionary
  """
  print("Available profiles:")
  profiles = get_config_value(config, 'profiles', {})

  if not profiles:
    print("  No profiles configured.")
    print("  Run with --init-config to create a default configuration.")
    return

  print("Configured profiles:\n")
  for profile_name, repos in profiles.items():
    print(f"  {profile_name}")
    print(f"  Repositories: ({len(repos)}):")
    for repo in repos:
      print(f"      - {repo}")
    print()