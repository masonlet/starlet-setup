# Starlet Setup

Quick setup script for CMake projects. Clone, configure, and build repositories with minimal effort.
Supports both single repository setup and batch setup for mono-repo development.

## Features
- **Single Repository Mode**:
  - Clone a GitHub repository with simple `username/repo` syntax
  - Support for HTTPS (default) and SSH protocols
  - Create a dedicated build directory
  - Configure the project with CMake
  - Build the project automatically
  - Optional flags for build type, directory, cleaning, and skipping build

- **Batch/Mono-repo Mode**:
  - Clone multiple related repositories into one workspace
  - Automatically generate root CMakeLists.txt for mono-repo structure
  - Build all modules together for easy debugging and development
  - Customize which repositories to include
  - Perfect for working across multiple interdependent projects

## Prerequisites
- Python 3.6+
- Git
- CMake

## Installation
Place `starlet-setup.py` in a convenient location (e.g., `~/github/`, `C:\Users\Username\github\`) so you can use it for all your CMake projects. No installation, just run the script with python.

## Usage

### Single Repository Mode

#### Basic Usage
```bash
# Clone and build a repository via HTTPS
python starlet-setup.py username/repo
python starlet-setup.py https://github.com/username/repo.git

# Clone and build a repository via SSH
python starlet-setup.py username/repo --ssh
python starlet-setup.py git@github.com:username/repo.git
```

#### Advanced Usage
```bash
# Specify build type (Debug, Release, RelWithDebInfo, MinSizeRel)
python starlet-setup.py username/repo --build-type Release

# Specify a custom build directory
python starlet-setup.py username/repo --build-dir my_build

# Only configure, skip building
python starlet-setup.py username/repo --no-build

# Clean the build directory before building
python starlet-setup.py username/repo --clean

# Show verbose output for debugging
python starlet-setup.py username/repo --verbose
```

### Batch/Mono-Repo Mode

#### Basic Usage
```bash
# Clone and build default Starlet modules with a test repository
python starlet-setup.py --batch masonlet starlet-samples

# Use SSH instead of HTTPS
python starlet-setup.py --batch masonlet starlet-samples --ssh

# Specify custom batch directory
python starlet-setup.py --batch masonlet starlet-samples --batch-dir my_starlet
```

#### Advanced Usage
```bash
# Clone non-default projects
python starlet-setup.py --batch username test_repo --repos library_1 library_2

# Verbose output for debugging
python starlet-setup.py --batch masonlet starlet-samples --verbose
```

#### Default Repositories (🚀 Starlet Ecosystem)
When using batch mode without `--repos`, the following repositories are cloned by default:
- `starlet-math`
- `starlet-logger`
- `starlet-controls`
- `starlet-scene`
- `starlet-graphics`
- `starlet-serializer`
- `starlet-engine`
- Your specified test repository (e.g., `starlet-samples`)

#### Mono-Repo Structure
Batch mode creates a workspace like this:
```
build-batch/
├── CMakeLists.txt      # Auto-generated root project
├── starlet-math/
├── starlet-logger/
├── starlet-controls/
├── starlet-scene/
├── starlet-graphics/
├── starlet-serializer/
├── starlet-engine/
├── starlet-samples/    # Your test repo
└── build/              # Single build output
```

This structure allows you to:
- Edit any module directory
- Build everything together
- Debug across module boundaries
- Commit changes without digging into build directories

## Examples

### Single Repository
```bash
cd ~/github
python starlet-setup.py masonlet/task-tracker
```

### Batch Setup for Development
```bash
# Set up complete Starlet environment for development
cd ~/github
python starlet-setup.py --batch masonlet starlet-samples

# Set up with only specific modules
python starlet-setup.py --batch masonlet starlet-image-sandbox --repos starlet-serializer starlet-logger starlet-math
```
