# Starlet Setup

Quick setup script for CMake projects. Clone, configure, and build repositories with minimal effort.

## Features
- Clone a GitHub repository (HTTPS or SSH)
- Create a dedicated build directory
- Configure the project with CMake
- Build the project automatically
- Optional flags for build type, directory, cleaning, and skipping build

## Prerequisites
- Python 3.6+
- Git
- CMake

## Installation
Place `starlet-setup.py` in a convenient location (e.g., `~/github/`, `C:\Users\Username\github\`) so you can use it for all your CMake projects. No installation, just run the script with python.

## Usage
```bash
# Clone and build a repository via HTTPS
python starlet-setup.py https://github.com/username/repo.git

# Clone and build a repository via SSH
python starlet-setup.py git@github.com:username/repo.git

# Specify build type (Debug, Release, RelWithDebInfo, MinSizeRel)
python starlet-setup.py <repo_url> --build-type Release

# Specify a custom build directory
python starlet-setup.py <repo_url> --build-dir my_build

# Only configure, skip building
python starlet-setup.py <repo_url> --no-build

# Clean the build directory before building
python starlet-setup.py <repo_url> --clean

# Show verbose output for debugging
python starlet-setup.py <repo_url> --verbose
```

## Example
```bash
cd ~/github
python starlet-setup.py https://github.com/masonlet/task-tracker.git
```
