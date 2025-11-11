"""
Starlet Setup - Quick setup for CMake projects.

A utility to quickly clone and build CMake repositories.
"""

import sys
import subprocess
import shutil
import argparse
from pathlib import Path


# CLI

def parse_args():
  """
  Parse command-line arguments for Starlet Setup.

  Returns:
    Parsed arguments namespace
  """
  parser = argparse.ArgumentParser(
    description="Starlet Setup - Quick setup script for CMake projects",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  %(prog)s https://github.com/username/repo.git
  %(prog)s https://github.com/username/repo.git --build-dir build_name
  %(prog)s git@github.com:username/repo.git
  %(prog)s git@github.com:username/repo.git --no-build
  %(prog)s git@github.com:username/repo.git --build-type Release
    """
  )

  parser.add_argument(
    'repo_url',
    help='GitHub repository URL (HTTPS or SSH)'
  )
  parser.add_argument(
    '-b', '--build-type',
    choices=['Debug', 'Release', 'RelWithDebInfo', 'MinSizeRel'],
    default='Debug',
    help='CMake build type (default: %(default)s)'
  )
  parser.add_argument(
    '-d', '--build-dir',
    default='build',
    help='Build directory name (default: %(default)s)'
  )
  parser.add_argument(
    '-n', '--no-build',
    action='store_true',
    help='Skip building, only configure'
  )
  parser.add_argument(
    '-c', '--clean',
    action='store_true',
    help='Clean build directory before building'
  )
  parser.add_argument(
    '-v', '--verbose',
    action='store_true',
    help='Show detailed command output'
  )

  return parser.parse_args()
  

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


# Main Function

def main():
  """Main entry point for Starlet Setup."""
  args = parse_args()
    
  check_prerequisites(args.verbose)  

  repo_name = Path(args.repo_url).stem.replace('.git', '')
  if Path(repo_name).exists():
    print(f"Repository {repo_name} already exists")
    response = input("Update existing repository? (y/n): ")
    if response.lower() == 'y':
      print(f"Updating {repo_name}")
      run_command(['git', 'pull'], cwd=repo_name, verbose=args.verbose)
  else:
    print(f"Cloning {repo_name}")
    run_command(['git', 'clone', args.repo_url], verbose=args.verbose)
  print()
  
  build_path = Path(repo_name) / args.build_dir
  if args.clean and build_path.exists():
    print("Cleaning build directory")
    shutil.rmtree(build_path)

  print(f"Creating build directory: {args.build_dir}")
  build_path.mkdir(exist_ok=True)
  print()

  print("Configuring with CMake")
  cmake_cmd = ['cmake', '..', f'-DCMAKE_BUILD_TYPE={args.build_type}']
  run_command(cmake_cmd, cwd=build_path, verbose=args.verbose)
  print()

  if not args.no_build:
    print("Building project")
    build_cmd = ['cmake', '--build', '.']

    if args.build_type:
      build_cmd.extend(['--config', args.build_type])

    run_command(build_cmd, cwd=build_path, verbose=args.verbose)
    print()

  print(f"Project finished in {repo_name}/{args.build_dir}")

if __name__ == "__main__":
  main()
