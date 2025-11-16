"""Interactive CLI for starlet-setup."""

from argparse import Namespace


def ask(prompt: str) -> str:
  """Basic prompt wrapper"""
  return input(f"{prompt}: ").strip()


def ask_default(prompt: str, default: str) -> str:
  """Prompt with a default value"""
  val = input(f"{prompt} [{default}]: ").strip()
  return val if val else default


def ask_yesno(prompt: str, default: bool) -> bool:
  """Prompt a yes/no question with default."""
  default_char = "Y" if default else "N"
  val = input(f"{prompt} (y/n) [{default_char}]: ").strip().lower()
  return default if not val else val.startswith("y")


def interactive_mode(args: Namespace) -> Namespace:
  """Interactive CLI mode for starlet-setup."""
  print("Starlet Setup Interactive Mode")

  if not getattr(args, "repo", None):
    repo = ""
    while not repo:
      repo = ask("Enter repository (user/repo or URL)")
    args.repo = repo

  if getattr(args, "ssh", None) is None:
    args.ssh = ask_yesno("Use SSH?", False)
    
  if getattr(args, "verbose", None) is None:
    args.verbose = ask_yesno("Verbose?", False,)
    
  if getattr(args, "clean", None) is None:
    args.clean = ask_yesno("Clean build directory if exists?", False)

  if getattr(args, "mono_repo", None) is None:
    mode = ''
    while mode not in ('1', '2'):
      mode = ask("Selected mode: (1) Single Repo (2) Mono-Repo")
    args.mono_repo = (mode == '2')

  if args.mono_repo:
    choice = ''
    while choice not in ('1', '2'):
      choice = ask("Mono-repo: (1) Use profile (2) Manual repo list")
  
    if choice == '1':
      profile = ""
      while not profile:
        profile = ask("Profile name")
      args.profile = profile
      args.repos = None
    else:
      repo_list = ""
      while not repo_list:
        repo_list = ask("Enter repos (space separated 'username/lib1 username/libe2')")
      args.repos = repo_list.split()
      args.profile = None

  default_build = getattr(args, "build_type", "Release") or "Release"
  args.build_type = ask_default("Build type", default_build)

  default_build_dir = getattr(args, "build_dir", "build") or "build"
  args.build_dir = ask_default("Build directory", default_build_dir)

  cmake_extra = ask_default("Additional CMake args (space separated '-DBUILD_TESTS=ON -DBUILD_LOCAL=ON')", "")
  args.cmake_arg = cmake_extra.split() if cmake_extra else []

  if getattr(args, "no_build", None) is None:
    args.no_build = ask_yesno("Configure only (skip build)?", False)

  print("\nInteractive mode complete")
  return args
