# Starlet Setup
A lightweight Python utility to quickly clone, configure, and build CMake projects — from single repos to full mono-repos.

[![Tests](https://github.com/masonlet/starlet-setup/actions/workflows/tests.yml/badge.svg)](https://github.com/masonlet/starlet-setup/actions/workflows/tests.yml)
[![PyPI version](https://badge.fury.io/py/starlet-setup.svg)](https://badge.fury.io/py/starlet-setup)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6%2B-blue.svg)]()

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Single Repository Mode](#single-repository-mode)
  - [Mono-Repo Mode](#mono-repository-mode)
  - [Profile Mode](#profile-mode)
  - [Config Mode](#config-mode)
- [Development](#development)
- [License](#license)



<br/>

## Quick start
```bash
pip install starlet-setup
starlet-setup username/repo
```

## Features
- **Single Repository Mode**:
  - Clone a GitHub repository with simple `username/repo` syntax
  - Support for HTTPS (default) and SSH protocols
  - Create a dedicated build directory
  - Configure the project with CMake
  - Build the project automatically
  - Optional flags for build type, directory, cleaning, and skipping build

- **Mono-repo Mode**:
  - Clone multiple related repositories into one workspace
  - Automatically generate root CMakeLists.txt for mono-repo structure
  - Build all modules together for easy debugging and development
  - Customize which repositories to include
  - Perfect for working across multiple interdependent projects

- **Profile Mode**:
  - Save frequently used mono-repo configuration as named profiles
  - Quick access to predefined repository sets
  - Manage multiple development environments effortlessly
  - Default profile includes all core Starlet modules



<br/>



## Prerequisites
- Python 3.6+
- Git
- CMake

## Installation

### From PyPI
```bash
pip install starlet-setup
```

### From GitHub
```bash
pip install git+https://github.com/masonlet/starlet-setup.git
```

Once installed, you can use the `starlet-setup` command from anywhere.   

### ⚠️ Command not found? ⚠️
<details>
<summary>If you get an error saying the command is not found, you may need to add Python's user scripts directory to your PATH.</summary>  

**Find your scripts directory**:
```bash
# Run this to find your exact scripts path
python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
```

**Then add it to your PATH**:

**Linux/macOS**:
```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent
export PATH="$HOME/.local/bin:$PATH"

# Apply changes
source ~/.bashrc # or equivalent
```

**Windows (Command Prompt)**:
```cmd
# Add to PATH via System Properties > Environment Variables
# Add: %APPDATA%\Python\Scripts
```

Alternatively, you can run the script directly:
```bash
python -m starlet_setup username/repo
```
</details>


<br/>



## Configuration
Starlet Setup supports persistent configuration through a JSON file, allowing you to save your preferred defaults (e.g., SSH mode, build directory, mono-repo repositories).

### 1. Initialize Config
```bash
# Create a default configuration file in your current directory.
starlet-setup --init-config
```
This will create a `.starlet-setup.json` that can be edited to customize your setup preferences.

### 2. File Location
Starlet Setup checks for configuration files in this order:
- `./.starlet-setup.json` (current directory)
- `~/.starlet-setup.json` (home directory)



<br/>



## Usage

### <a id="single-repository-mode"></a>
<details>
<summary>Single Repository Mode</summary>

#### Basic Usage
  
```bash
# Clone and build a repository via HTTPS
starlet-setup username/repo
starlet-setup https://github.com/username/repo.git

# Clone and build a repository via SSH
starlet-setup username/repo --ssh
starlet-setup git@github.com:username/repo.git
```

#### Advanced Usage
```bash
# Specify build type (Debug, Release, RelWithDebInfo, MinSizeRel)
starlet-setup username/repo --build-type Release

# Specify a custom build directory
starlet-setup username/repo --build-dir my-build

# Only configure, skip building
starlet-setup username/repo --no-build

# Clean the build directory before building
starlet-setup username/repo --clean

# Show verbose output for debugging
starlet-setup username/repo --verbose

# Custom CMake args
starlet-setup username/repo --cmake-arg=-DCMAKE_CXX_COMPILER=clang++
```

<br/>

</details>

### <a id="mono-repository-mode"></a>
<details>
<summary>Mono-Repo Mode</summary>

#### BUILD_LOCAL Usage
Mono-repo mode sets `BUILD_LOCAL=ON` in the root project's CMakeLists.txt.  
This flag tells your test repository to link against local modules instead of fetching them via CMake's FetchContent:
```cmake
# In your test repo's CMakeLists.txt
if(NOT BUILD_LOCAL)
    # Fetch dependencies from GitHub
    FetchContent_Declare(starlet_engine
      GIT_REPOSITORY https://github.com/masonlet/starlet-engine.git 
      GIT_TAG main
    )
    # ... other dependencies
endif()
```

**With mono-repo mode** (`BUILD_LOCAL=ON`):
- All modules link locally from subdirectories
- Changes in any module immediately affect your test repo
- Full debugging across module boundaries
- Single unified build for the entire ecosystem

**Without mono-repo mode** (`BUILD_LOCAL` undefined):
- Dependencies fetched via FetchContent
- Standalone builds work independently
- Users can build your repo without the full ecosystem
- Automatic dependency management

This dual-mode design allows both integrated development and standalone distribution.

#### Basic Usage
**Note:** When using `--repos` or `--profile`, mono-repo mode is automatically enabled, so the `--mono-repo` flag is optional.

```bash
# Clone and build default Starlet modules with a test repository
starlet-setup username/repo --mono-repo 

# Use SSH instead of HTTPS
starlet-setup username/repo --mono-repo --ssh

# Clone non-default repositories
starlet-setup username/repo --repos user/lib1 user/lib2
```

#### Advanced Usage
```bash
# Multiple flags
starlet-setup username/repo --mono-repo --verbose --mono-dir my-starlet

# Custom repos and multiple flags
starlet-setup username/repo --repos user/lib1 user/lib2 --ssh --verbose

# Custom CMake args
starlet-setup username/repo --mono-repo --cmake-arg=-DCMAKE_CXX_COMPILER=clang++
```

#### Default Repositories (🚀 Starlet Ecosystem)
When using mono-repo mode without `--repos` or `--profile`, the script clones repositories based on your configuration. The default profile includes:
- `masonlet/starlet-math`
- `masonlet/starlet-logger`
- `masonlet/starlet-controls`
- `masonlet/starlet-scene`
- `masonlet/starlet-graphics`
- `masonlet/starlet-serializer`
- `masonlet/starlet-engine`
- Your specified test repository (e.g., `masonlet/starlet-samples`)

#### Mono-Repo Structure
Mono-repo mode creates a workspace like this:
```
build-mono/
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

<br/>

</details>

### <a id="profile-mode"></a>
<details>
<summary>Profile Mode (Saved Configurations)</summary>

#### Managing Profiles
```bash
# Add a new profile
starlet-setup --profile-add myprofile user/lib1 user/lib2

# List all saved profiles
starlet-setup --list-profiles

# Remove a profile
starlet-setup --profile-remove myprofile
```

#### Using Profiles
```bash
# Use the default profile
starlet-setup username/repo --profile

# Use a named profile
starlet-setup username/repo --profile myprofile

# Use a profile with SSH
starlet-setup username/repo --profile myprofile --ssh
```

<br/>

</details>

### <a id="config-mode"></a>
<details>
<summary>Config Mode (Saved Build Settings)</summary>

#### Managing Configs
```bash
# List all saved configurations
starlet-setup --list-configs

# Add a new configuration with flags
starlet-setup --config-add myconfig --ssh --build-type Release --no-build

# Remove a configuration
starlet-setup --config-remove myconfig
```

#### Using Configs
```bash
# Use a saved config
starlet-setup username/repo --config myconfig

# Override specific settings
starlet-setup username/repo --config myconfig --verbose

# Config with mono-repo mode
starlet-setup username/repo --mono-repo --config myconfig --ssh
```

<br/>

</details>


<br/>

## Development

### <a id="development"></a>
<details>
<summary>Development</summary>

### Running Tests

#### 1. Clone starlet-setup
```bash
git clone https://github.com/masonlet/starlet-setup.git
cd starlet-setup
```

#### 2. Install in Development Mode
```bash
pip install -e .
```

#### 3. Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run tests with flags
pytest -v
```
</details>


<br/>



## License
MIT License — see [LICENSE](./LICENSE) for details.
