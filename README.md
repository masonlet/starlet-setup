# Starlet Setup

Quick setup script for CMake projects.

## Installation
This script is designed to live in one location and easily clone and build CMake projects.
To install, download and place `starlet-setup.py` in your universal GitHub folder (e.g., `~/github/`, `C:\Users\Username\github\`). 

## Prerequisites
- Python 3.6+
- Git
- CMake

## Usage
```bash
# SSH
python starlet-setup.py git@github.com:username/repo.git

# HTTPS
python starlet-setup.py https://github.com/username/repo.git
```

This will:
1. Clone the repository
2. Create a build directory
3. Run CMake
4. Build the project

## Example
```bash
cd ~/github
python starlet-setup.py https://github.com/masonlet/task-tracker.git
```
