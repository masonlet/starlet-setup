from pathlib import Path
from .config import get_config_value
from .utils import run_command

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
  

def get_default_repos(config: dict) -> list[str]:
  """
  Get the default list of Starlet repositories.

  Args:
    config: Configuration dictionary

  Returns:
    List of repository paths (username/repo format)
  """
  default_repos = get_config_value(config, 'profiles.default', None)
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
