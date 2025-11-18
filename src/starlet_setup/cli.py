"""Command-line argument parsing."""

import argparse
from argparse import Namespace
from typing import Any
from .config import get_config_value, load_config


def _add_common_args(
  parser, 
  config: dict[str, Any]
) -> None:
  parser.add_argument(
    '--ssh',
    action='store_true',
    default=get_config_value(config, 'configs.default.ssh', False),
    help='Use SSH instead of HTTPS for cloning'
  )
  parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    default=get_config_value(config, 'configs.default.verbose', False),
    help='Show detailed command output'
  )
  parser.add_argument(
    '--cmake-arg',
    action='append',
    dest='cmake_arg',
    help='Additional CMake arguments (e.g., --cmake-arg=-D_BUILD_TESTS=ON). Can be used multiple times.'
  )


def _add_config_management_args(parser) -> None:
  parser.add_argument(
    '--init-config',
    action='store_true',
    help='Create a default config file in the current directory'
  )
  parser.add_argument(
    '--config-add',
    metavar=('NAME'),
    help="Add a new config"
  )
  parser.add_argument(
    '--config-remove',
    metavar='NAME',
    help='Remove a saved configuration'
  )
  parser.add_argument(
    '--list-configs',
    action='store_true',
    help='List all saved configs'
  )


def _add_profile_management_args(parser) -> None:
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


def _add_build_args(parser, config: dict[str, Any]) -> None:
  parser.add_argument(
    '-b', '--build-type',
    choices=['Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel'],
    default=get_config_value(config, 'configs.default.build_type', 'Debug'),
    help='CMake build type (default: %(default)s)'
  )
  parser.add_argument(
    '-d', '--build-dir',
    default=get_config_value(config, 'configs.default.build_dir', 'build'),
    help='Build directory name (default: %(default)s)'
  )
  parser.add_argument(
    '-n', '--no-build',
    action='store_true',
    default=get_config_value(config, 'configs.default.no_build', False),
    help='Skip building, only configure'
  )
  parser.add_argument(
    '-c', '--clean',
    action='store_true',
    help='Clean build directory before building'
  )


def _add_mono_repo_args(parser, config: dict[str, Any]) -> None:
  parser.add_argument(
    '--mono-repo',
    action='store_true',
    help='Mono-repo mode: clone multiple repositories along with test repo'
  )
  parser.add_argument(
    '--mono-dir',
    default=get_config_value(config, 'configs.default.mono_dir', 'build-mono'),
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


def parse_args() -> Namespace:
  """
  Parse command-line arguments for Starlet Setup.

  Returns:
    Parsed arguments namespace
  """
  config, config_path = load_config()

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

  Config Mangement:
    %(prog)s --init-config
    %(prog)s --list-configs
    %(prog)s --config-add myconfig
    %(prog)s --config-add myconfig --ssh --no-build --build-type Release
    %(prog)s --config-remove myconfig
    """
  )

  # Repository argument
  parser.add_argument(
    'repo',
    nargs='?',
    help='Repository name (username/repo) or full GitHub URL'
  )
  _add_common_args(parser, config)
  _add_config_management_args(parser)
  _add_profile_management_args(parser)
  _add_build_args(parser, config)
  _add_mono_repo_args(parser, config)

  args = parser.parse_args()
  args.config = config
  args.config_path = config_path

  if args.init_config \
     or args.list_configs or args.config_add or args.config_remove \
     or args.list_profiles or args.profile_add or args.profile_remove:
    return args

  if args.repos and args.profile:
    parser.error("Cannot use both --repos and --profile")
  if args.repos or args.profile:
    args.mono_repo = True

  return args