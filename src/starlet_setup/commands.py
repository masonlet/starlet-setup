import sys
import shutil
from pathlib import Path
from .repository import resolve_repo_url, get_default_repos, clone_repository
from .config import get_config_value
from .profiles import list_profiles
from .utils import run_command


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



def _create_mono_repo_cmakelists(mono_dir: Path, test_repo: str, repos: list[str]):
  """
  Create a root CMakeLists.txt for the mono-repo.

  Args:
    repo_dir: Directory containing all cloned repos
    test_repo: Test repository name
    repos: List of all repository paths that were cloned
  """
  module_names = [repo.split('/')[-1] for repo in repos]
  modules_cmake = '\n  '.join(module_names)

  cmake_content = f"""cmake_minimum_required(VERSION 3.23)

# Config
project(starlet_dev LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)

if(NOT EXISTS "${{CMAKE_CURRENT_SOURCE_DIR}}/{test_repo}/CMakeLists.txt")
  message(FATAL_ERROR "Test repository '{test_repo}' not found")
endif()

set(MONO_REPO_MODULES 
  {modules_cmake}
)

foreach(module IN LISTS MONO_REPO_MODULES)
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

  cmake_file = mono_dir / "CMakeLists.txt"
  cmake_file.write_text(cmake_content)
  print(f"Created root CMakeLists.txt at {mono_dir}\n")


def mono_repo_mode(args, config):
  """Handle mono-repo cloning and building."""
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
    print("Error: Repository must be in format 'username/repo' for mono-repo mode")
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
    print(f"  Directory: {args.mono_dir}")
    print(f"  Libraries: {len(profile_repos)}\n")
    repos = list(profile_repos) 

  elif args.repos:
    print(f"Starlet Setup: Mono-repository Mode")
    print(f"  Test Repository: {test_repo}")
    print(f"  Clone Method: {'SSH' if args.ssh else 'HTTPS'}")
    print(f"  Directory: {args.mono_dir}\n") 
    repos = list(args.repos)

  else:
    print(f"Starlet Setup: Mono-repository Mode")
    print(f"  Test Repository: {test_repo}")
    print(f"  Clone Method: {'SSH' if args.ssh else 'HTTPS'}")
    print(f"  Directory: {args.mono_dir}\n") 
    repos = get_default_repos(config)

  if test_repo not in repos:
    repos.append(test_repo)

  print(f"Total repositories: {len(repos)}\n")

  mono_repo_path = Path(args.mono_dir)
  print(f"Creating directory: {mono_repo_path}\n")
  mono_repo_path.mkdir(exist_ok=True)

  print("Cloning repositories")
  for repo in repos:
    try:
      clone_repository(repo, mono_repo_path, args.ssh, args.verbose)
    except SystemExit:
      sys.exit(1)
  print(f"\n  Finished cloning ({len(repos)} repositories)\n")
  
  print("Creating mono-repo configuration")
  _create_mono_repo_cmakelists(mono_repo_path, test_repo_name, repos)

  print("Creating build directory\n")
  build_path = mono_repo_path / 'build' 
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
  print(f"Repositories in: {mono_repo_path.absolute()}")
  print(f"Build output in: {build_path.absolute()}")