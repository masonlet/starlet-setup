import argparse
from .config import get_config_value, load_config

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

  Mono-repo Repository Mode:
    %(prog)s username/repo --mono-repo
    %(prog)s username/repo --mono-repo --ssh --mono-dir my_workspace
    %(prog)s username/repo --repos user/lib1 user/lib2 user/lib3

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
  
  # Mono-repo repo mode arguments
  parser.add_argument(
    '--mono-repo',
    action='store_true',
    help='Mono-repo mode: clone multiple repositories along with test repo'
  )
  parser.add_argument(
    '--mono-dir',
    default=get_config_value(config, 'defaults.mono_dir', 'build-mono'),
    help='Directory name for mono-repo cloning (default: %(default)s)'
  )
  parser.add_argument(
    '--repos',
    nargs='+',
    metavar='REPO',
    help='List of library repositories to clone in mono-repo mode'
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

  if args.profile or args.repos:
    args.mono_repo = True

  if args.repos and args.profile:
    parser.error("Cannot use both --repos and --profile")

  return args