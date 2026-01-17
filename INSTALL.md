# ComfyUI Installation Guide

This guide explains how to install ComfyUI from GitHub with cross-platform support using the ModularInstaller framework.

## Overview

The ModularInstaller now supports automated installation of ComfyUI from GitHub with the following features:

- **Cross-platform support**: Works on both Windows and Linux
- **Miniconda integration**: Automatically installs and configures Miniconda if not present
- **Isolated environments**: Creates a dedicated conda environment (`comfyui_bp`) for ComfyUI
- **Automated setup**: Clones ComfyUI from GitHub and installs all dependencies
- **Flexible installation**: Choose between portable (Windows) or GitHub-based installation

## Installation Methods

### Method 1: Automated Installation (Recommended)

This method automatically handles everything for you.

#### Prerequisites

- **Git**: Must be installed and available in PATH
- **Internet connection**: Required for downloading Miniconda and ComfyUI

#### Windows Installation

```bash
# Install ComfyUI from GitHub with conda environment
python ModularInstaller.py --install-comfyui --comfy_path C:\ComfyUI

# Specify custom conda environment name and Python version
python ModularInstaller.py --install-comfyui --comfy_path C:\ComfyUI --conda-env myenv --python-version 3.10
```

**What happens:**
1. Checks if Miniconda is installed
2. If not, installs Miniconda3 via `winget` (requires Windows Package Manager)
3. Creates conda environment named `comfyui_bp` (or custom name)
4. Clones ComfyUI from GitHub to the specified path
5. Installs all Python dependencies in the conda environment

#### Linux Installation

```bash
# Install ComfyUI from GitHub with conda environment
python ModularInstaller.py --install-comfyui --comfy_path ~/ComfyUI

# Specify custom conda environment name and Python version
python ModularInstaller.py --install-comfyui --comfy_path ~/ComfyUI --conda-env myenv --python-version 3.10
```

**What happens:**
1. Checks if Miniconda is installed
2. If not, downloads and installs Miniconda to `~/miniconda3`
3. Creates conda environment named `comfyui_bp` (or custom name)
4. Clones ComfyUI from GitHub to the specified path
5. Installs all Python dependencies including PyTorch with CUDA support

### Method 2: Manual Installation

If you prefer to install components separately:

#### Step 1: Check Conda Installation

```bash
# Check if conda is already installed
python ModularInstaller.py --check-conda
```

If conda is not installed, proceed to Step 2. Otherwise, skip to Step 3.

#### Step 2: Install Miniconda

**Windows:**
```bash
# Using winget (recommended)
winget install Anaconda.Miniconda3

# Restart your terminal after installation
```

**Linux:**
```bash
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p ~/miniconda3

# Initialize conda for your shell
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

#### Step 3: Create Conda Environment

```bash
# Create environment with Python 3.11
conda create -n comfyui_bp python=3.11 -y
conda activate comfyui_bp
```

#### Step 4: Clone ComfyUI

```bash
# Clone ComfyUI repository
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
```

#### Step 5: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# On Linux, also install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## Running Benchmarks with Installed ComfyUI

After installation, you can run benchmarks using the installed ComfyUI:

```bash
# Basic benchmark run
python ModularInstaller.py -c /path/to/ComfyUI --conda-env comfyui_bp -w /path/to/workflow.zip

# With multiple generations
python ModularInstaller.py -c /path/to/ComfyUI --conda-env comfyui_bp -w /path/to/workflow.zip -g 10

# With GUI
python ModularInstaller.py --gui --conda-env comfyui_bp
```

**Important:** When using a conda environment, always specify `--conda-env` to ensure the correct Python executable is used.

## Command-Line Options

### Installation Options

| Option | Description | Default |
|--------|-------------|---------|
| `--install-comfyui` | Install ComfyUI from GitHub with conda environment | - |
| `--conda-env` | Conda environment name to use/create | `comfyui_bp` |
| `--python-version` | Python version for conda environment | `3.11` |
| `--check-conda` | Check if conda is installed and exit | - |

### Example Commands

```bash
# Check if conda is installed
python ModularInstaller.py --check-conda

# Install ComfyUI with default settings
python ModularInstaller.py --install-comfyui --comfy_path ~/ComfyUI

# Install ComfyUI with custom environment name
python ModularInstaller.py --install-comfyui --comfy_path ~/ComfyUI --conda-env my_comfy_env

# Install ComfyUI with Python 3.10
python ModularInstaller.py --install-comfyui --comfy_path ~/ComfyUI --python-version 3.10

# Run benchmark with conda environment
python ModularInstaller.py -c ~/ComfyUI --conda-env comfyui_bp -w workflow.zip -g 10
```

## Platform-Specific Notes

### Windows

- **Miniconda Installation**: Uses `winget` (Windows Package Manager)
  - If `winget` is not available, install it from Microsoft Store or install Miniconda manually
  - After installation via `winget`, restart your terminal for conda to be available in PATH
- **Path Separators**: Use backslashes (`\`) or forward slashes (`/`) - both work
- **Virtual Environments**: Conda environments are located at `%USERPROFILE%\miniconda3\envs\`

### Linux

- **Miniconda Installation**: Downloads installer script from Anaconda repository
  - Installs to `~/miniconda3` by default
  - Automatically initializes conda for bash shell
  - Run `source ~/.bashrc` or restart terminal after installation
- **PyTorch**: Automatically installs PyTorch with CUDA 12.1 support for GPU acceleration
- **Permissions**: Ensure you have write permissions to the installation directory
- **Virtual Environments**: Conda environments are located at `~/miniconda3/envs/`

## Troubleshooting

### Conda Not Found After Installation

**Windows:**
```bash
# Restart your terminal/command prompt
# If still not found, add to PATH manually:
# %USERPROFILE%\miniconda3\condabin
```

**Linux:**
```bash
# Re-initialize your shell
source ~/.bashrc

# Or manually run conda init
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

### Git Not Installed

**Windows:**
```bash
winget install Git.Git
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install git
```

### Installation Fails Due to Network Issues

The installer automatically retries failed operations, but if you encounter persistent network issues:

1. Check your internet connection
2. If behind a proxy, configure git and conda to use it:
   ```bash
   # Git proxy
   git config --global http.proxy http://proxy.example.com:8080

   # Conda proxy
   conda config --set proxy_servers.http http://proxy.example.com:8080
   ```

### ComfyUI Already Installed

If the ComfyUI directory already exists:
- The installer will prompt you to update (if it's a git repository)
- Or offer to remove and reinstall (if it's not a git repository)
- You can cancel and use the existing installation

### Conda Environment Already Exists

If the conda environment already exists:
- The installer will prompt you to remove and recreate it
- Or you can choose to use the existing environment
- To manually remove: `conda env remove -n comfyui_bp`

## Advanced Usage

### Using the Installer Module Directly

You can use the `ComfyUIInstaller` class programmatically:

```python
from pathlib import Path
from core.comfyui_installer import ComfyUIInstaller

# Create installer instance
installer = ComfyUIInstaller(
    install_path=Path.home() / "ComfyUI",
    log_file=Path("install.log")
)

# Check if conda is installed
is_installed, conda_path = installer.check_conda_installed()

# Install Miniconda if needed
if not is_installed:
    installer.ensure_conda_installed()

# Create conda environment
installer.create_conda_environment(env_name="comfyui_bp", python_version="3.11")

# Clone ComfyUI
installer.clone_comfyui_from_github()

# Install dependencies
installer.install_comfyui_dependencies(env_name="comfyui_bp")

# Or do everything at once
installer.full_install(env_name="comfyui_bp", python_version="3.11")
```

### Standalone Installer Script

The installer module can be run standalone:

```bash
# Run as standalone script
python core/comfyui_installer.py --install-path ~/ComfyUI --env-name comfyui_bp

# Check conda only
python core/comfyui_installer.py --check-only

# With logging
python core/comfyui_installer.py --install-path ~/ComfyUI --log-file install.log
```

## Migration from Portable Installation (Windows)

If you currently use the ComfyUI portable installation and want to switch to the GitHub-based installation:

1. **Backup your current installation:**
   ```bash
   # Backup custom_nodes, models, and workflows
   xcopy C:\ComfyUI_Portable\ComfyUI\custom_nodes C:\ComfyUI_Backup\custom_nodes /E /I
   xcopy C:\ComfyUI_Portable\ComfyUI\models C:\ComfyUI_Backup\models /E /I
   ```

2. **Install ComfyUI from GitHub:**
   ```bash
   python ModularInstaller.py --install-comfyui --comfy_path C:\ComfyUI
   ```

3. **Restore your custom files:**
   ```bash
   # Copy back custom_nodes and models
   xcopy C:\ComfyUI_Backup\custom_nodes C:\ComfyUI\custom_nodes /E /I
   xcopy C:\ComfyUI_Backup\models C:\ComfyUI\models /E /I
   ```

4. **Update benchmarks to use new installation:**
   ```bash
   python ModularInstaller.py -c C:\ComfyUI --conda-env comfyui_bp -w workflow.zip
   ```

## Environment Variables

The installer respects the following environment variables:

- `HF_TOKEN`: HuggingFace token for downloading models (set in your shell before running)
- `CONDA_PREFIX`: Current conda environment prefix (automatically set by conda)

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the main [README.md](README.md) for general framework documentation
3. Check existing GitHub issues
4. Create a new issue with:
   - Platform (Windows/Linux)
   - Installation method used
   - Error messages or logs
   - Output of `python ModularInstaller.py --check-conda`
