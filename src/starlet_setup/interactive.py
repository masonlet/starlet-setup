"""Interactive CLI for starlet-setup."""

from argparse import Namespace


def _ask(prompt: str) -> str:
  """Basic prompt wrapper"""
  return input(f"{prompt}: ").strip()


def _ask_default(prompt: str, default: str) -> str:
  """Prompt with a default value"""
  val = input(f"{prompt} [{default}]: ").strip()
  return val if val else default


def _ask_yesno(prompt: str, default: bool) -> bool:
  """Prompt a yes/no question with default."""
  default_char = "Y" if default else "N"
  val = input(f"{prompt} (y/n) [{default_char}]: ").strip().lower()
  return default if not val else val.startswith("y")


def interactive_mode(args: Namespace) -> Namespace:
  """Interactive CLI mode for starlet-setup."""
  print("Starlet Setup Interactive Mode")

  if not args.repo:
    repo = ""
    while not repo:
      repo = _ask("Enter repository (user/repo or URL)")
    args.repo = repo

  if not args.ssh:
    args.ssh = _ask_yesno("Use SSH?", False)
    
  if not args.verbose:
    args.verbose = _ask_yesno("Verbose?", False,)
    
  if not args.clean:
    args.clean = _ask_yesno("Clean build directory if exists?", False)

  if not args.mono_repo:
    mode = ''
    while mode not in ('1', '2'):
      mode = _ask("Selected mode: (1) Single Repo (2) Mono-Repo")
    args.mono_repo = (mode == '2')

  if args.mono_repo and not args.profile and not args.repos:
    choice = ''
    while choice not in ('1', '2'):
      choice = _ask("Mono-repo: (1) Use profile (2) Manual repo list")
  
    if choice == '1':
      profile = ""
      while not profile:
        profile = _ask("Profile name")
      args.profile = profile
    else:
      repo_list = ""
      while not repo_list:
        repo_list = _ask("Enter repos (space separated 'username/lib1 username/libe2')")
      args.repos = repo_list.split()

  args.build_type = _ask_default("Build type", args.build_type)
  args.build_dir = _ask_default("Build directory", args.build_dir)

  if not args.cmake_arg:
    cmake_extra = _ask_default("Additional CMake args (space separated '-DBUILD_TESTS=ON -DBUILD_LOCAL=ON')", "")
    args.cmake_arg = cmake_extra.split() if cmake_extra else []

  if not args.no_build:
    args.no_build = _ask_yesno("Configure only (skip build)?", False)

  print("\nInteractive mode complete")
  return args
