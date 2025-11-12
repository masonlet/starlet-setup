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
  Single Repository:
    %(prog)s username/repo
    %(prog)s username/repo --ssh
    %(prog)s username/repo --build-dir build_name
    %(prog)s username/repo --build-type Release
    %(prog)s username/repo --no-build
    %(prog)s https://github.com/username/repo.git
    %(prog)s git@github.com:username/repo.git
  Batch Setup:
    %(prog)s --batch masonlet starlet-samples
    %(prog)s --batch masonlet starlet-samples --ssh
    %(prog)s --batch masonlet starlet-samples --batch-dir my_starlet
    %(prog)s --batch masonlet starlet-image-sandbox --repos starlet-serializer
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
    '--init-config',
    action='store_true',
    help='Create a default config file in the current directory'
  )
  parser.add_argument(
    '--cmake-arg',
    nargs='*',
    default=None,
    help='Additional CMake arguments (e.g., --cmake-arg=-D_BUILD_TESTS=ON)'
  )
  # Single repo mode arguments
  parser.add_argument(
    'repo',
    nargs='?',
    help='Repository name (username/repo) or full GitHub URL'
  )
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
  # Batch repo mode arguments
  parser.add_argument(
    '--batch',
    nargs=2,
    metavar=('USER', 'TEST_REPO'),
    help='Batch mode: clone multiple repositories (USER TEST_REPO)'
  )
  parser.add_argument(
    '--batch-dir',
    default=get_config_value(config, 'defaults.batch_dir', 'build-batch'),
    help='Directory name for batch cloning (default: %(default)s)'
  )
  parser.add_argument(
    '--repos',
    nargs='*',
    help='Custom list of repositories to clone in batch mode'
  )
  args = parser.parse_args()

  if args.init_config:
    return args

  if not args.batch and not args.repo:
    parser.error("Either provide a repository or use --batch mode")

  if args.batch and args.repo:
    parser.error("Cannot use both single repo and --batch mode")

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
    "batch": {
      "default_user": "masonlet",
      "default_repos": [
        "starlet-math",
        "starlet-logger",
        "starlet-controls",
        "starlet-scene",
        "starlet-graphics",
        "starlet-serializer",
        "starlet-engine"
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
  print("\nEdit this file to customize your defaults.")
  print("Config files are checked in this order:")
  print(" 1. ./.starlet-setup.json (current directory)")
  print(" 2. ~/.starlet-setup.json (home directory)")


# Helper Functions

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


def get_default_repos(config: dict, user: str, test_repo: str) -> list[str]:
  """
  Get the default list of Starlet repositories.

  Args:
    user: GitHub username
    test_repo: Test repository name

  Returns:
    List of repository paths (username/repo format)
  """
  default_repos = get_config_value(config, 'batch.default_repos', None)

  if default_repos:
    repos = [f"{user}/{repo}" for repo in default_repos]
    repos.append(f"{user}/{test_repo}")
    return repos

  return [
    f"{user}/starlet-math",
    f"{user}/starlet-logger",
    f"{user}/starlet-controls",
    f"{user}/starlet-scene",
    f"{user}/starlet-graphics",
    f"{user}/starlet-serializer",
    f"{user}/starlet-engine",
    f"{user}/{test_repo}"
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
    test_repo: Name of the test repository (startup project)
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
  print(f"Created root CMakeLists.txt at {batch_dir}")


# Main Functions

def single_repo_mode(args, config):
  """Handle single repository setup."""
  print("Starlet Setup: Single Repository Mode\n")

  repo_url = resolve_repo_url(args.repo, args.ssh)
  repo_name = Path(repo_url).stem.replace('.git', '')
  
  if Path(repo_name).exists():
    print(f"Repository {repo_name} already exists")
    if input("Update existing repository? (y/n): ").lower() == 'y':
      print(f"Updating {repo_name}")
      run_command(['git', 'pull'], cwd=repo_name, verbose=args.verbose)
  else:
    print(f"Cloning {repo_name}")
    run_command(['git', 'clone', repo_url], verbose=args.verbose)
  
  build_path = Path(repo_name) / args.build_dir
  if args.clean and build_path.exists():
    print("\nCleaning build directory")
    shutil.rmtree(build_path)

  print(f"Creating build directory: {args.build_dir}")
  build_path.mkdir(exist_ok=True)

  print("\nConfiguring with CMake")
  cmake_cmd = ['cmake', '..', f'-DCMAKE_BUILD_TYPE={args.build_type}']
  cmake_arg = args.cmake_arg if args.cmake_arg is not None else get_config_value(config, 'defaults.cmake_arg', [])
  if cmake_arg:
    cmake_cmd.extend(cmake_arg)
  run_command(cmake_cmd, cwd=build_path, verbose=args.verbose)

  if not args.no_build:
    print("\nBuilding project")
    build_cmd = ['cmake', '--build', '.']
    if args.build_type:
      build_cmd.extend(['--config', args.build_type])
    run_command(build_cmd, cwd=build_path, verbose=args.verbose)

  print(f"\nProject finished in {repo_name}/{args.build_dir}")


def batch_mode(args, config):
  """Handle batch cloning and building of multiple repositories."""
  user, test_repo = args.batch

  if not user:
    user = get_config_value(config, 'batch.default_user', None)
    if not user:
      print("Error: No user specified and no default_user in config")
      sys.exit(1)

  print("Starlet Setup: Batch Mode\n")
  print(f"User: {user}")
  print(f"Test Repository: {test_repo}")
  print(f"Clone Method: {'SSH' if args.ssh else 'HTTPS'}")
  print(f"Batch Directory: {args.batch_dir}\n")

  if args.repos:
    repos = [f"{user}/{repo}" if '/' not in repo else repo for repo in args.repos]
    test_repo_path = f"{user}/{test_repo}"
    if test_repo_path not in repos:
      repos.append(test_repo_path)
  else:
    repos = get_default_repos(config, user, test_repo)

  batch_path = Path(args.batch_dir)
  print(f"Creating directory: {batch_path}")
  batch_path.mkdir(exist_ok=True)

  print("\nCloning repositories")
  for repo in repos:
    try:
      clone_repository(repo, batch_path, args.ssh, args.verbose)
    except SystemExit:
      sys.exit(1)
  print(f"Finished cloning ({len(repos)} repositories)")
  
  print("\nCreating mono-repo configuration")
  create_batch_cmakelists(batch_path, test_repo, repos)

  print("Building project")
  build_path = batch_path / 'build' 
  build_path.mkdir(exist_ok=True)
  
  print(f"\nConfiguring with CMake in {build_path}")
  cmake_cmd = ['cmake', '-DBUILD_LOCAL=ON', '..']
  cmake_arg = args.cmake_arg if args.cmake_arg is not None else get_config_value(config, 'defaults.cmake_arg', [])
  if cmake_arg:
    cmake_cmd.extend(cmake_arg)
  run_command(cmake_cmd, cwd=build_path, verbose=args.verbose)

  if not args.no_build:
    print("\nBuilding project")
    run_command(['cmake', '--build', '.'], cwd=build_path, verbose=args.verbose)

  print("\nSetup complete")
  print(f"Repositories in: {batch_path.absolute()}")
  print(f"Build output in: {build_path.absolute()}")


# Main Function

def main():
  """Main entry point for Starlet Setup."""
  args = parse_args()

  if args.init_config:
    create_default_config()
    return

  check_prerequisites(args.verbose)  
  config = load_config()

  if args.batch:
    batch_mode(args, config)
  else:
    single_repo_mode(args, config)

 
if __name__ == "__main__":
  main()
