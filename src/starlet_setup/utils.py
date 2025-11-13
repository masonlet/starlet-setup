"""Utility functions for Starlet Setup."""

import sys
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Union


def check_prerequisites(verbose: bool=False) -> None:
  """
  Check if required tools are installed.
  
  Args:
    verbose: Show detailed output

  Raises:
    SystemExit: If required tools are missing
  """
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


def run_command(
  cmd: list[str], 
  cwd: Optional[Union[str, Path]]=None, 
  verbose: bool=False
) -> subprocess.CompletedProcess:
  """
  Run a shell command with proper error handling

  Args:
    cmd: Command and arguments as list
    cwd: Working directory for command execution
    verbose: Show detailed output

  Returns:
    CompletedProcess object

  Raises:
    SystemExit: If command fails
  """
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
    return result
  except subprocess.CalledProcessError as e:
    print(f"Error running command: {' '.join(cmd)}")
    if e.stderr:
      print(e.stderr)
    sys.exit(1)
  except FileNotFoundError as e:
    print(f"Error: Command not found: {cmd[0]}")
    sys.exit(1)