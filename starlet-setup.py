"""
Starlet Setup - Quick setup for CMake projects.

A utility to quickly clone and build CMake repositories.
Supports single repository setup and batch setup of mono-repo projects.
"""

import sys
import subprocess
import shutil
import argparse
import json
from pathlib import Path


# CLI

def parse_args():
  """
  Parse command-line arguments for Starlet Setup.

  Returns:
    Parsed arguments namespace
  """
  config = load_config()

  parser = argparse.ArgumentParser(
    description="Starlet Setup - Quick setup script for CMake projects",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  Single Repository Mode:
    %(prog)s https://github.com/username/repo.git
    %(prog)s git@github.com:username/repo.git
    %(prog)s username/repo
    %(prog)s username/repo --ssh
    %(prog)s username/repo --no-build
    %(prog)s username/repo --build-dir build_name --build-type Release

  Batch Repository Mode:
    %(prog)s username/repo --batch --repos user/lib1 user/lib2 user/lib3
    %(prog)s username/repo --batch --ssh --batch-dir my_workspace

  Profile Repository Mode:
    %(prog)s username/repo --profile
    %(prog)s username/repo --profile myprofile

  Profile Management:
    %(prog)s --list-profiles
    %(prog)s --profile-add myprofile user/lib1 user/lib2 user/lib3
    %(prog)s --profile-remove myprofile

  Config:
    %(prog)s --init-config
    """
  )

  # Common arguments
  parser.add_argument(
    '--ssh',
    action='store_true',
    default=get_config_value(config, 'defaults.ssh', False),
    help='Use SSH instead of HTTPS for cloning'
  )
  parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    default=get_config_value(config, 'defaults.verbose', False),
    help='Show detailed command output'
  )
  parser.add_argument(
    '--cmake-arg',
    nargs='*',
    default=None,
    help='Additional CMake arguments (e.g., --cmake-arg=-D_BUILD_TESTS=ON)'
  )

  # Configuration arguments
  parser.add_argument(
    '--init-config',
    action='store_true',
    help='Create a default config file in the current directory'
  )

  # Profile management arguments
  parser.add_argument(
    '--profile-add',
    nargs='+',
    metavar=('NAME', 'REPO'),
    help='Add a new profile: NAME REPO1 [REPO2 ...]'
  )
  parser.add_argument(
    '--profile-remove',
    metavar='NAME',
    help='Remove a saved profile'
  )
  parser.add_argument(
    '--list-profiles',
    action='store_true',
    help='List all saved profiles'
  )

  # Build arguments
  parser.add_argument(
    '-b', '--build-type',
    choices=['Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel'],
    default=get_config_value(config, 'defaults.build_type', 'Debug'),
    help='CMake build type (default: %(default)s)'
  )
  parser.add_argument(
    '-d', '--build-dir',
    default=get_config_value(config, 'defaults.build_dir', 'build'),
    help='Build directory name (default: %(default)s)'
  )
  parser.add_argument(
    '-n', '--no-build',
    action='store_true',
    default=get_config_value(config, 'defaults.no_build', False),
    help='Skip building, only configure'
  )
  parser.add_argument(
    '-c', '--clean',
    action='store_true',
    help='Clean build directory before building'
  )

  # Repository argument
  parser.add_argument(
    'repo',
    nargs='?',
    help='Repository name (username/repo) or full GitHub URL'
  )
  
  # Batch repo mode arguments
  parser.add_argument(
    '--batch',
    action='store_true',
    help='Batch mode: clone multiple repositories along with test repo'
  )
  parser.add_argument(
    '--batch-dir',
    default=get_config_value(config, 'defaults.batch_dir', 'build-batch'),
    help='Directory name for batch cloning (default: %(default)s)'
  )
  parser.add_argument(
    '--repos',
    nargs='+',
    metavar='REPO',
    help='List of library repositories to clone in batch mode'
  )
  parser.add_argument(
    '--profile',
    nargs='?',
    const='default',
    metavar='NAME',
    help='Use saved profile for library repositories (uses "default" if no name given)'
  )

  args = parser.parse_args()

  if args.init_config or args.list_profiles or args.profile_add or args.profile_remove:
    return args

  if not args.repo:
    parser.error("Repository argument is required")

  if args.batch and args.profile:
    parser.error("Cannot use both --batch and --profile")

  if args.repos and not args.batch:
    parser.error("--repos requires --batch mode")

  return args


# Config functions


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
      "batch_dir": "build-batch",
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


# Helper Functions

def check_prerequisites(verbose=False):
  """Check if required tools are installed."""
  required = ['git', 'cmake']
  missing = []

  for tool in required:
    if not shutil.which(tool):
      missing.append(tool)
    elif verbose:
      print(f"Found {tool}")

  if missing:
    print(f"Error: Missing required tools: {', '.join(missing)}")
    sys.exit(1)


def resolve_repo_url(repo_input, use_ssh=False):
  """
  Convert repository input to full URL.

  Args:
    repo_input: Either 'username/repo' or full URL
    use_ssh: Whether to use SSH protocol

  Returns:
    Full repository URL
  """
  if repo_input.startswith('http') or repo_input.startswith('git@'):
    return repo_input

  if use_ssh:
    return f"git@github.com:{repo_input}.git"
  else:
    return f"https://github.com/{repo_input}.git"


def run_command(cmd, cwd=None, verbose=False):
  if verbose:
    print(f"Running: {' '.join(cmd)}")
    if cwd:
      print(f"  in directory: {cwd}")

  try:
    result = subprocess.run(
      cmd,
      cwd=cwd,
      check=True,
      capture_output=not verbose,
      text=True
    )
    if verbose and result.stdout:
      print(result.stdout)
  except subprocess.CalledProcessError as e:
    print(f"Error running command: {' '.join(cmd)}")
    if e.stderr:
      print(e.stderr)
    sys.exit(1)


def get_default_repos(config: dict) -> list[str]:
  """
  Get the default list of Starlet repositories.

  Args:
    config: Configuration dictionary

  Returns:
    List of repository paths (username/repo format)
  """
  default_repos = get_config_value(config, 'batch.default_repos', None)
  if default_repos:
    return list(default_repos)

  return [
    "masonlet/starlet-math",
    "masonlet/starlet-logger",
    "masonlet/starlet-controls",
    "masonlet/starlet-scene",
    "masonlet/starlet-graphics",
    "masonlet/starlet-serializer",
    "masonlet/starlet-engine"
  ]


def clone_repository(repo_path: str, target_dir: Path, use_ssh: bool, verbose: bool):
  """
  Clone a single repository.

  Args:
    repo_path: Repository path (username/repo)
    target_dir: Parent directory for cloning
    use_ssh: Whether to use SSH
    verbose: Whether to show verbose output
  """
  repo_name = repo_path.split('/')[-1]
  repo_dir = target_dir / repo_name

  if repo_dir.exists():
    print(f"\n  {repo_name} already exists")
    return 
  
  print(f"\n  Cloning {repo_name}")
  repo_url = resolve_repo_url(repo_path, use_ssh)

  try:
    run_command(['git', 'clone', repo_url], cwd=target_dir, verbose=verbose)
  except SystemExit:
    print(f"  Failed to clone {repo_path}")
    raise


def create_batch_cmakelists(batch_dir: Path, test_repo: str, repos: list[str]):
  """
  Create a root CMakeLists.txt for the mono-repo.

  Args:
    batch_dir: Directory containing all cloned repos
    test_repo: Test repository name
    repos: List of all repository paths that were cloned
  """
  module_names = [repo.split('/')[-1] for repo in repos]
  modules_cmake = '\n  '.join(module_names)

  cmake_content = f"""cmake_minimum_required(VERSION 3.23)

# Config
project(batch_dev LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)

if(NOT EXISTS "${{CMAKE_CURRENT_SOURCE_DIR}}/{test_repo}/CMakeLists.txt")
  message(FATAL_ERROR "Test repository '{test_repo}' not found")
endif()

set(BATCH_MODULES 
  {modules_cmake}
)

foreach(module IN LISTS BATCH_MODULES)
  if(EXISTS "${{CMAKE_CURRENT_SOURCE_DIR}}/${{module}}/CMakeLists.txt")
    add_subdirectory(${{module}})
  else()
    message(WARNING "Module ${{module}} not found or missing CMakeLists.txt")
  endif()
endforeach()

# IDE organization
set_property(GLOBAL PROPERTY USE_FOLDERS ON)
set_property(GLOBAL PROPERTY PREDEFINED_TARGETS_FOLDER "External")

# IDE startup project
string(REPLACE "-" "_" target "{test_repo}")
set_property(DIRECTORY ${{CMAKE_CURRENT_SOURCE_DIR}} PROPERTY VS_STARTUP_PROJECT ${{target}})
"""

  cmake_file = batch_dir / "CMakeLists.txt"
  cmake_file.write_text(cmake_content)
  print(f"Created root CMakeLists.txt at {batch_dir}\n")


# Profile Functions

def add_profile(config, args_list):
  """
  Add a new profile to the configuration.

  Args:
    config: Configuration dictionary
    args_list: [name, repo1, repo2, ...]
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


def remove_profile(config, name):
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


def list_profiles(config):
  """List all configured profiles."""
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


# Mode Functions


def single_repo_mode(args, config):
  """Handle single repository setup."""
  repo_url = resolve_repo_url(args.repo, args.ssh)
  repo_name = Path(repo_url).stem.replace('.git', '')

  print("Starlet Setup: Single Repository Mode")
  print(f"  Repository: {repo_name}")
  print(f"  Clone Method: {'SSH' if args.ssh else 'HTTPS'}\n")
  
  if Path(repo_name).exists():
    print(f"Repository {repo_name} already exists")
    if input("Update existing repository? (y/n): ").lower() == 'y':
      print(f"Updating {repo_name}\n")
      run_command(['git', 'pull'], cwd=repo_name, verbose=args.verbose)
  else:
    print(f"Cloning {repo_name}\n")
    run_command(['git', 'clone', repo_url], verbose=args.verbose)
  
  build_path = Path(repo_name) / args.build_dir
  if args.clean and build_path.exists():
    print("Cleaning build directory\n")
    shutil.rmtree(build_path)

  print(f"Creating build directory: {args.build_dir}\n")
  build_path.mkdir(exist_ok=True)

  print("Configuring with CMake\n")
  cmake_cmd = ['cmake', '..', f'-DCMAKE_BUILD_TYPE={args.build_type}']
  cmake_arg = args.cmake_arg if args.cmake_arg is not None else get_config_value(config, 'defaults.cmake_arg', [])
  if cmake_arg:
    cmake_cmd.extend(cmake_arg)
  run_command(cmake_cmd, cwd=build_path, verbose=args.verbose)

  if not args.no_build:
    print("Building project\n")
    build_cmd = ['cmake', '--build', '.']
    if args.build_type:
      build_cmd.extend(['--config', args.build_type])
    run_command(build_cmd, cwd=build_path, verbose=args.verbose)

  print(f"Project finished in {repo_name}/{args.build_dir}")


def batch_mode(args, config):
  """Handle batch cloning and building of multiple repositories."""
  test_repo_input = args.repo

  if test_repo_input.startswith('http') or test_repo_input.startswith('git@'):
    if 'github.com/' in test_repo_input or 'github.com:' in test_repo_input:
      parts = test_repo_input.split('/')[-2:]
      test_repo = f"{parts[0].split(':')[-1]}/{parts[1].replace('.git', '')}"
    else:
      print("Error: Could not parse repository URL")
      sys.exit(1)
  elif '/' in test_repo_input:
    test_repo = test_repo_input
  else:
    print("Error: Repository must be in format 'username/repo' for batch mode")
    sys.exit(1)

  test_repo_name = test_repo.split('/')[-1]

  if args.profile:
    profiles = get_config_value(config, 'profiles', {})

    if args.profile not in profiles:
      print(f"Error: Profile '{args.profile}' not found\n")
      list_profiles(config)
      sys.exit(1)

    profile_repos = profiles[args.profile]

    if not profile_repos:
      print(f"Error: Profile '{args.profile}' has no repositories")
      sys.exit(1)

    print(f"Starlet Setup: Profile Repository Mode")
    print(f"  Profile: {args.profile}")
    print(f"  Test Repository: {test_repo}")
    print(f"  Clone Method: {'SSH' if args.ssh else 'HTTPS'}")
    print(f"  Directory: {args.batch_dir}")
    print(f"  Libraries: {len(profile_repos)}\n")
    repos = list(profile_repos) 

  elif args.repos:
    print(f"Starlet Setup: Batch Repository Mode")
    print(f"  Test Repository: {test_repo}")
    print(f"  Clone Method: {'SSH' if args.ssh else 'HTTPS'}")
    print(f"  Directory: {args.batch_dir}\n") 
    repos = list(args.repos)

  else:
    print(f"Starlet Setup: Batch Repository Mode")
    print(f"  Test Repository: {test_repo}")
    print(f"  Clone Method: {'SSH' if args.ssh else 'HTTPS'}")
    print(f"  Directory: {args.batch_dir}\n") 
    repos = get_default_repos(config)

  if test_repo not in repos:
    repos.append(test_repo)

  print(f"Total repositories: {len(repos)}\n")

  batch_path = Path(args.batch_dir)
  print(f"Creating directory: {batch_path}\n")
  batch_path.mkdir(exist_ok=True)

  print("Cloning repositories")
  for repo in repos:
    try:
      clone_repository(repo, batch_path, args.ssh, args.verbose)
    except SystemExit:
      sys.exit(1)
  print(f"\n  Finished cloning ({len(repos)} repositories)\n")
  
  print("Creating mono-repo configuration")
  create_batch_cmakelists(batch_path, test_repo_name, repos)

  print("Creating build directory\n")
  build_path = batch_path / 'build' 
  build_path.mkdir(exist_ok=True)
  
  print(f"Configuring with CMake in {build_path}\n")
  cmake_cmd = ['cmake', '-DBUILD_LOCAL=ON', '..']
  cmake_arg = args.cmake_arg if args.cmake_arg is not None else get_config_value(config, 'defaults.cmake_arg', [])
  if cmake_arg:
    cmake_cmd.extend(cmake_arg)
  run_command(cmake_cmd, cwd=build_path, verbose=args.verbose)

  if not args.no_build:
    print("Building project\n")
    run_command(['cmake', '--build', '.'], cwd=build_path, verbose=args.verbose)

  print("Setup complete")
  print(f"Repositories in: {batch_path.absolute()}")
  print(f"Build output in: {build_path.absolute()}")


# Main Function

def main():
  """Main entry point for Starlet Setup."""
  args = parse_args()

  if args.init_config:
    create_default_config()
    return

  config = load_config()

  if args.list_profiles:
    list_profiles(config)
    return
  
  if args.profile_add:
    add_profile(config, args.profile_add)
    return
  
  if args.profile_remove:
    remove_profile(config, args.profile_remove)
    return

  check_prerequisites(args.verbose) 

  if args.batch or args.profile:
    batch_mode(args, config)
  else:
    single_repo_mode(args, config)

 
if __name__ == "__main__":
  main()
