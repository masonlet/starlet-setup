"""
Starlet Setup - Quick setup for CMake projects.

A utility to quickly clone and build CMake repositories.
Supports single repository setup and mono-repo setup of projects.
"""

from .cli import parse_args
from .config import create_default_config
from .profiles import list_profiles, add_profile, remove_profile
from .utils import check_prerequisites
from .commands import mono_repo_mode, single_repo_mode


def main() -> None:
  """Main entry point for Starlet Setup."""
  args = parse_args()

  if args.init_config:
    create_default_config()
    return

  if args.list_profiles:
    list_profiles(args.config)
    return
  
  if args.profile_add:
    add_profile(args.config, args.profile_add)
    return
  
  if args.profile_remove:
    remove_profile(args.config, args.profile_remove)
    return

  check_prerequisites(args.verbose) 

  if args.mono_repo or args.profile:
    mono_repo_mode(args)
  else:
    single_repo_mode(args)

 
if __name__ == "__main__":
  main()