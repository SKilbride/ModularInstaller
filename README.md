# ComfyUI Modular Installer

## Overview
The ComfyUI Modular Installer is a manifest-driven system for installing ComfyUI models, custom nodes, and assets. It uses declarative manifest files to specify what should be downloaded and where, supporting multiple sources including HuggingFace, Git repositories, direct URLs, and local files.

### Key Features
- **Cross-Platform Installation**: Git-based ComfyUI installation with conda environments (Windows/Linux/Mac) or Windows portable installation
- **Conda Environment Management**: Automatic miniconda installation and Python 3.13 environment setup for git-based installs
- **Blender Integration**: Auto-install Blender 4.5 LTS via winget (Windows only)
- **GUI and CLI modes**: Choose between graphical interface or command-line operation
- **Manifest-driven**: Declare all dependencies in a single JSON/YAML file
- **Multiple sources**: HuggingFace Hub, Git repositories, direct URLs, local files, pip packages, winget, and bundled files
- **Conditional Processing**: Install different packages based on runtime conditions (e.g., git vs portable install)
- **Advanced Pip Support**: Custom index URLs, uninstall options, and flexible pip arguments
- **Flexible path management**: Install to ComfyUI, home directory, temp, or absolute paths
- **Embedded Python support**: Automatically uses ComfyUI's embedded Python or conda environment for package installations
- **Smart caching**: Skip already-downloaded files and verify checksums
- **Parallel downloads**: Download multiple items simultaneously for faster installation
- **Resume capability**: Continue interrupted downloads from where they left off
- **Bundled packages**: Include files directly in ZIP packages alongside the manifest
- **PyInstaller Ready**: Build standalone executables with bundled packages

## Prerequisites
1. Python 3.8 or higher (for the installer itself)
2. Git (automatically installed on Windows via winget; manual installation required on Linux/Mac)
3. Optional: Miniconda (automatically installed on Windows for git-based ComfyUI; manual installation recommended on Linux)
4. Optional: HuggingFace token for gated models (set `HF_TOKEN` environment variable)

**Note on ComfyUI Installation:**
- **Windows**: Supports both portable installation (embedded Python) and git-based installation (conda environment)
- **Linux/Mac**: Git-based installation with conda is the default and recommended method

## Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/SKilbride/ModularInstaller
   cd ModularInstaller
   ```

2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Quick Start

### GUI Mode (Recommended for Beginners)
Launch the graphical installer:

```bash
python ModularInstaller.py --gui
```

The GUI provides:
- Visual file selection for manifest and ComfyUI path
- Checkbox options for installation settings
- Real-time progress display
- Error handling with clear messages

### CLI Mode - Auto-Install (Windows Only)
The installer can automatically download and set up ComfyUI portable:

```bash
# ComfyUI will be installed to ~/ComfyUI_BP automatically
python ModularInstaller.py -m manifest.json
```

The installer will:
1. Check if ComfyUI exists at `~/ComfyUI_BP`
2. If not found, prompt to download ComfyUI portable (~2GB download)
3. Extract to `~/ComfyUI_BP`
4. Prompt to install Blender 4.5 LTS (used for 3D workflows)
5. Use embedded Python for all package installations

### Git-Based Installation (Cross-Platform)

Install ComfyUI from GitHub using conda environment for a clean, isolated Python setup:

```bash
# Installs ComfyUI via git with conda environment
python ModularInstaller.py -m manifest.json --git-install-comfyui
```

**Linux Default:** On Linux systems, git-based installation is the default method.

The installer will:
1. Check/install miniconda if needed:
   - **Windows**: `winget install miniconda3 --source winget`
   - **Linux**: Downloads and runs Miniconda installer script
2. Create `comfyui_bp` conda environment with Python 3.13
3. Clone ComfyUI from https://github.com/Comfy-Org/ComfyUI.git
4. Set environment variables:
   - `COMFYUI_BASE`: Installation path (e.g., `~/ComfyUI_BP`)
   - `COMFYUI_PYTHON`: Path to conda Python executable
   - `COMFYUI_PYTHON_TYPE`: Set to `conda` (vs `embedded` for portable)

**Advantages:**
- **Cross-platform**: Works on Windows, Linux, and Mac
- **Clean environment**: Isolated Python 3.13 with conda
- **Up-to-date**: Always installs latest ComfyUI from GitHub
- **Easy updates**: Simple `git pull` to update
- **Package management**: Full conda and pip support

### Manual ComfyUI Path
If you have ComfyUI installed elsewhere:

```bash
python ModularInstaller.py -c /path/to/ComfyUI -m manifest.json
```

### With ZIP Package
```bash
python ModularInstaller.py -m package.zip
```

### Preview Before Installing
```bash
python ModularInstaller.py -m manifest.json --list-contents
python ModularInstaller.py -m manifest.json --dry-run
```

## Command Line Arguments

### Required Arguments
- **`-m, --manifest PATH`** - Path to manifest.json/yaml file or ZIP package

### Optional Arguments

**Installation Options:**
- **`-c, --comfy_path PATH`** - Path to ComfyUI installation (default: auto-install to ~/ComfyUI_BP/ComfyUI)
- **`--install-path PATH`** - Custom installation path for ComfyUI portable (default: ~/ComfyUI_BP)
- **`--git-install-comfyui`** - Install ComfyUI from GitHub using conda environment (default on Linux)
- **`--no-auto-install`** - Disable automatic ComfyUI installation if not found
- **`--skip-blender`** - Skip Blender 4.5 LTS installation (Windows only)
- **`--set-condition COND`** - Set a condition for conditional manifest processing (can be used multiple times)
- **`--gui`** - Launch graphical installer interface

**Download Options:**
- **`-f, --force`** - Force re-download/installation of all items
- **`--required-only`** - Only install items marked as required
- **`--no-verify`** - Skip checksum verification
- **`--sequential`** - Disable parallel downloads
- **`--workers N`** - Number of parallel workers (default: 4)
- **`--no-resume`** - Disable resume capability

**Utility Options:**
- **`-l, --log [FILE]`** - Enable logging to file (auto-generated name if not specified)
- **`-t, --temp_path PATH`** - Alternate temporary directory
- **`--dry-run`** - Preview actions without downloading
- **`--list-contents`** - List manifest items without installing
- **`--cleanup`** - Clean up partial download files and exit

## Manifest Format

The manifest is a JSON or YAML file that declares what to install.

### Basic Structure

```json
{
  "package": {
    "name": "My ComfyUI Setup",
    "version": "1.0.0",
    "description": "Complete setup for image generation"
  },
  "metadata": {
    "total_size_mb": 1500,
    "estimated_time": "5-10 minutes",
    "tags": ["sdxl", "flux", "video"],
    "details": "Includes SDXL models and custom nodes"
  },
  "items": [
    {
      "name": "SDXL Base Model",
      "type": "model",
      "source": "huggingface",
      "repo": "stabilityai/stable-diffusion-xl-base-1.0",
      "file": "sd_xl_base_1.0.safetensors",
      "path": "models/checkpoints/sd_xl_base_1.0.safetensors",
      "sha256": "abc123...",
      "size_mb": 6938,
      "required": true
    }
  ]
}
```

### Item Types

Each item in the `items` array represents something to install:

| Type | Description |
|------|-------------|
| `model` | Model files (checkpoints, LoRAs, VAE, etc.) |
| `custom_node` | ComfyUI custom nodes (typically Git repositories) |
| `file` | Generic file to download |
| `directory` | Directory to download/clone (use with Git for non-custom-node repos) |
| `pip_package` | Python package to install via pip |
| `config` | Configuration file |
| `application` | Windows application (via winget) |

### Path Base Options

The `path_base` field determines where files are installed relative to a base directory:

| Path Base | Description | Example Result |
|-----------|-------------|----------------|
| `comfyui` (default) | Relative to ComfyUI installation directory | `~/ComfyUI_BP/ComfyUI/models/checkpoints/model.safetensors` |
| `home` | Relative to user home directory | `~/my-folder/file.txt` |
| `temp` | System temporary directory | `/tmp/file.txt` (Linux) or `%TEMP%\file.txt` (Windows) |
| `appdata` | Application data directory | `~/.local/share/app/` (Linux), `~/Library/Application Support/` (Mac), `%APPDATA%\app\` (Windows) |
| `absolute` | Use path as-is (must be absolute path) | `/opt/shared/model.safetensors` |
| `install_temp` | Relative to InstallTemp folder in ZIP package | Used for bundled files referenced by manifest |

**Default:** If `path_base` is not specified, it defaults to `comfyui`.

### Source Types

<details>
<summary><strong>1. HuggingFace Hub</strong> - Download files from HuggingFace repositories</summary>

#### 1. HuggingFace Hub

Download files from HuggingFace repositories:

```json
{
  "name": "FLUX.1 Dev Model",
  "type": "model",
  "source": "huggingface",
  "repo": "black-forest-labs/FLUX.1-dev",
  "file": "flux1-dev.safetensors",
  "path": "models/checkpoints/flux1-dev.safetensors",
  "sha256": "optional-checksum",
  "size_mb": 23800,
  "required": true,
  "gated": true
}
```

**Fields:**
- `repo` - HuggingFace repository ID (e.g., "username/repo-name")
- `file` - Filename in the repository
- `path` - Destination path relative to ComfyUI directory
- `path_base` - (Optional) Base path type (default: `comfyui`)
- `remote_path` - (Optional) If file is in a subdirectory, full path like "repo/tree/main/subfolder"
- `gated` - (Optional) Set to `true` if model requires license acceptance
- `sha256` or `sha` - (Optional) SHA256 checksum for verification

</details>

<details>
<summary><strong>2. Git Repository</strong> - Clone Git repositories for custom nodes and other tools</summary>

#### 2. Git Repository

**Example 1: Custom Node (default ComfyUI location)**

```json
{
  "name": "ComfyUI Manager",
  "type": "custom_node",
  "source": "git",
  "url": "https://github.com/ltdrdata/ComfyUI-Manager.git",
  "path": "custom_nodes/ComfyUI-Manager",
  "path_base": "comfyui",
  "ref": "main",
  "install_requirements": true,
  "required": true
}
```

**Example 2: Clone Repository to Custom Location (directory type)**

Use `type: "directory"` for non-custom-node repositories:

```json
{
  "name": "Stable Diffusion WebUI",
  "type": "directory",
  "source": "git",
  "url": "https://github.com/AUTOMATIC1111/stable-diffusion-webui.git",
  "path": "stable-diffusion-webui",
  "path_base": "home",
  "ref": "master",
  "required": false
}
```

This installs to `~/stable-diffusion-webui/`.

**Example 3: Clone to Absolute Path**

```json
{
  "name": "Shared Repository",
  "type": "directory",
  "source": "git",
  "url": "https://github.com/user/shared-repo.git",
  "path": "/opt/shared/repo",
  "path_base": "absolute",
  "ref": "main"
}
```

**Fields:**
- `url` - Git repository URL
- `path` - Destination path (relative to path_base)
- `path_base` - (Optional) Base path type (default: `comfyui`)
- `ref` - (Optional) Branch, tag, or commit (default: "main")
- `install_requirements` - (Optional) Run `pip install -r requirements.txt` after cloning

</details>

<details>
<summary><strong>3. Direct URL</strong> - Download files from direct URLs</summary>

#### 3. Direct URL

Download files from direct URLs:

```json
{
  "name": "Custom VAE",
  "type": "model",
  "source": "url",
  "url": "https://example.com/models/vae.safetensors",
  "path": "models/vae/vae.safetensors",
  "sha256": "optional-checksum",
  "executable": false
}
```

**Fields:**
- `url` - Direct download URL
- `path` - Destination path (relative to path_base)
- `path_base` - (Optional) Base path type (default: `comfyui`)
- `executable` - (Optional) Make file executable after download (Linux/Mac)
- `sha256` or `sha` - (Optional) SHA256 checksum for verification

</details>

<details>
<summary><strong>4. Local File</strong> - Copy files from local filesystem</summary>

#### 4. Local File

Copy files from local filesystem:

```json
{
  "name": "Custom Config",
  "type": "config",
  "source": "local",
  "source_path": "/path/to/local/config.yaml",
  "path": "user/config.yaml"
}
```

**Fields:**
- `source_path` - Path to source file or directory
- `path` - Destination path (relative to path_base)
- `path_base` - (Optional) Base path type (default: `comfyui`)

</details>

<details>
<summary><strong>5. Bundled in ZIP</strong> - Files included in ZIP package (extracted automatically)</summary>

#### 5. Bundled in ZIP

Files included in the ZIP package (extracted automatically):

```json
{
  "name": "Workflow Files",
  "type": "file",
  "source": "bundled",
  "path": "user/workflows/"
}
```

**Note:** Bundled files are extracted from the ZIP's `ComfyUI/` folder structure.

</details>

<details>
<summary><strong>6. Pip Package</strong> - Install Python packages via pip with advanced options</summary>

#### 6. Pip Package

Install Python packages via pip with advanced options:

**Basic Installation:**
```json
{
  "name": "OpenCV",
  "type": "pip_package",
  "source": "pip",
  "package": "opencv-python",
  "version": "4.8.0.74",
  "required": false
}
```

**Advanced PyTorch with Custom Index:**
```json
{
  "name": "PyTorch CUDA 13.0",
  "type": "pip_package",
  "source": "pip",
  "package": "torch",
  "version": "2.5.1",
  "extra_index_url": "https://download.pytorch.org/whl/cu130",
  "uninstall_current": true
}
```

**With Custom Pip Arguments:**
```json
{
  "name": "Package with Options",
  "type": "pip_package",
  "source": "pip",
  "package": "some-package",
  "pip_args": "--no-deps --force-reinstall"
}
```

**Uninstall Only:**
```json
{
  "name": "Remove Old Package",
  "type": "pip_package",
  "source": "pip",
  "package": "old-package",
  "uninstall_only": true
}
```

**Fields:**
- `package` - Package name on PyPI or path to wheel file
- `version` - (Optional) Specific version to install
- `index_url` - (Optional) Replace PyPI with custom index (use `extra_index_url` instead for PyTorch)
- `extra_index_url` - (Optional) Additional index URL (e.g., PyTorch CUDA wheels)
- `find_links` - (Optional) Additional URLs to search for packages
- `pip_args` - (Optional) Additional pip arguments (string or list)
- `uninstall_current` - (Optional) Uninstall current version before installing (default: false)
- `uninstall_only` - (Optional) Only uninstall, don't install (default: false)

**Important for PyTorch:** Use `extra_index_url` not `index_url` to add PyTorch's index alongside PyPI, allowing PyTorch and other packages to install correctly.

</details>

<details>
<summary><strong>7. InstallTemp (Bundled Packages)</strong> - Reference files bundled in ZIP's InstallTemp folder</summary>

#### 7. InstallTemp (Bundled Packages)

Reference files bundled in the ZIP package's `InstallTemp/` folder.

**Example 1: Bundled Wheel Package**

```json
{
  "name": "Bundled Wheel Package",
  "type": "pip_package",
  "source": "install_temp",
  "source_path": "wheels/custom_package-1.0.0-py3-none-any.whl"
}
```

**Example 2: Copy Bundled File**

```json
{
  "name": "Bundled Config",
  "type": "file",
  "source": "install_temp",
  "source_path": "configs/settings.yaml",
  "path": "user/settings.yaml",
  "path_base": "comfyui"
}
```

**Example 3: Copy Bundled Folder**

```json
{
  "name": "Bundled Workflows",
  "type": "directory",
  "source": "install_temp",
  "source_path": "workflows",
  "path": "user/default/workflows",
  "path_base": "comfyui"
}
```

This copies the entire `InstallTemp/workflows/` folder to ComfyUI's `user/default/workflows/`.

**Example 4: Copy to Custom Location**

```json
{
  "name": "Shared Models",
  "type": "directory",
  "source": "install_temp",
  "source_path": "models/shared",
  "path": ".comfyui/shared-models",
  "path_base": "home"
}
```

This copies `InstallTemp/models/shared/` to `~/.comfyui/shared-models/`.

**Fields:**
- `source_path` - Path relative to `InstallTemp/` folder in ZIP
- `path` - Destination path (relative to path_base, for files/directories only)
- `path_base` - (Optional) Base path type (default: `comfyui`)

**Package Structure:**
```
package.zip
├── manifest.json
├── InstallTemp/              # Bundled files referenced by manifest
│   ├── wheels/
│   │   └── package.whl
│   └── configs/
│       └── settings.yaml
└── ComfyUI/                  # Files extracted directly to ComfyUI
    └── user/
        └── workflows/
```

**Note:** `InstallTemp` items are always copied/installed, even if destination exists. Use for authoritative bundled content.

</details>

<details>
<summary><strong>8. Winget (Windows Package Manager)</strong> - Install Windows applications via winget</summary>

#### 8. Winget (Windows Package Manager)

Install Windows applications via winget:

```json
{
  "name": "Visual Studio Code",
  "type": "application",
  "source": "winget",
  "package_id": "Microsoft.VisualStudioCode",
  "winget_source": "winget",
  "silent": true,
  "accept_agreements": true,
  "required": false
}
```

**Fields:**
- `package_id` - Winget package ID (e.g., "Git.Git", "Microsoft.VisualStudioCode")
- `winget_source` - (Optional) Source name (default: "winget", can be "msstore")
- `silent` - (Optional) Silent installation (default: true)
- `accept_agreements` - (Optional) Auto-accept agreements (default: true)

**Note:** Automatically skipped on non-Windows platforms.

</details>

### Common Fields

All items support these fields:

- **`name`** (required) - Human-readable name
- **`type`** (required) - Item type (see table above)
- **`source`** (required) - Source type (see source types above)
- **`path`** (usually required) - Relative path for installation (see `path_base` below)
- **`path_base`** (optional) - Base path type for installation (default: `comfyui`)
  - `comfyui` - Install relative to ComfyUI directory (default)
  - `home` - Install relative to user home directory
  - `temp` - Install to temporary directory
  - `appdata` - Install to application data directory
  - `absolute` - Use absolute path (path must be absolute)
  - `install_temp` - Install relative to InstallTemp folder (for bundled packages)
- **`required`** (optional) - If `true`, installation fails if this item fails
- **`size_mb`** (optional) - Size in megabytes (for display purposes)
- **`conditions`** (optional) - Advanced conditional processing object (see below)

**Note:** See the "Path Base Options" table above for detailed information on all path_base types and their behavior.

### Conditional Processing

Install different packages based on runtime conditions with OS detection, AND/OR logic, and flexible condition timing.

#### Automatic Conditions

The installer automatically sets these conditions:

**OS Detection:**
- **`os_windows`** - Windows systems
- **`os_linux`** - Linux systems
- **`os_mac`** - macOS systems (recommended)
- **`os_darwin`** - macOS systems (alternative)

**Installation Type:**
- **`comfyui_git_install`** - Git-based installation (conda environment)
- **`comfyui_portable_install`** - Portable installation (Windows default)

**Custom Conditions:**
- Set via `--set-condition` flag (can be used multiple times)

#### Conditions Structure

```yaml
items:
  - name: "Item Name"
    type: pip_package
    source: pip
    package: "package-name"
    conditions:
      match_type: any  # Options: [any, all] (default: any)
      match_conditions:
        - condition: os_windows
        - condition: comfyui_git_install
      set_conditions:
        - condition: dependencies_installed
          set_condition_when: installed  # Options: [installed, always] (default: installed)
```

**Field Descriptions:**

- **`match_type`** - How to evaluate multiple conditions:
  - `any` (default) - Install if ANY condition is met (OR logic)
  - `all` - Install if ALL conditions are met (AND logic)

- **`match_conditions`** - List of conditions that must be met
  - Simple format: `- condition: os_windows`
  - If omitted, item always processes

- **`set_conditions`** - Conditions to set after processing
  - **`condition`** - Condition name to set
  - **`set_condition_when`** - When to set:
    - `installed` (default) - Only if item was installed
    - `always` - Even if item was skipped (already exists)

#### Example 1: OS-Specific Packages

```yaml
items:
  # Windows only
  - name: Microsoft.VCRedist.2015+.x64
    type: application
    source: winget
    package_id: Microsoft.VCRedist.2015+.x64
    conditions:
      match_type: any
      match_conditions:
        - condition: os_windows

  # Linux only
  - name: "Linux Dependencies"
    type: pip_package
    source: pip
    package: "linux-package"
    conditions:
      match_type: any
      match_conditions:
        - condition: os_linux
```

#### Example 2: Installation Type-Specific

```yaml
items:
  # Git install: CUDA PyTorch
  - name: "PyTorch CUDA"
    type: pip_package
    source: pip
    package: "torch"
    extra_index_url: "https://download.pytorch.org/whl/cu130"
    conditions:
      match_type: any
      match_conditions:
        - condition: comfyui_git_install

  # Portable install: CPU PyTorch
  - name: "PyTorch CPU"
    type: pip_package
    source: pip
    package: "torch"
    conditions:
      match_type: any
      match_conditions:
        - condition: comfyui_portable_install
```

#### Example 3: Combined Conditions (AND Logic)

```yaml
items:
  # Windows + Git Install (both required)
  - name: "Windows Git Package"
    type: pip_package
    source: pip
    package: "windows-git-package"
    conditions:
      match_type: all  # Requires BOTH
      match_conditions:
        - condition: os_windows
        - condition: comfyui_git_install
```

#### Example 4: Dependency Chains

```yaml
items:
  # Install core first
  - name: "Core Dependencies"
    type: pip_package
    source: pip
    package: "numpy"
    conditions:
      set_conditions:
        - condition: core_installed
          set_condition_when: installed

  # Plugin requires core
  - name: "Advanced Plugin"
    type: pip_package
    source: pip
    package: "plugin"
    conditions:
      match_type: any
      match_conditions:
        - condition: core_installed
```

#### Command Line Conditions

```bash
# Set custom conditions
python ModularInstaller.py -m manifest.yaml --set-condition cuda_support

# Multiple conditions
python ModularInstaller.py -m manifest.yaml --set-condition cuda_support --set-condition high_vram
```

**See CONDITIONAL_PROCESSING.md for comprehensive examples, advanced patterns, and troubleshooting.**

## Complete Example Manifest

This example demonstrates various features including conditional processing, advanced pip options, and different source types:

```json
{
  "package": {
    "name": "SDXL Complete Setup",
    "version": "1.0.0",
    "description": "Full SDXL setup with custom nodes and conditional PyTorch"
  },
  "metadata": {
    "total_size_mb": 15000,
    "estimated_time": "10-15 minutes",
    "tags": ["sdxl", "upscaling"],
    "details": "Includes SDXL base, refiner, VAE, essential custom nodes, and platform-specific PyTorch"
  },
  "items": [
    {
      "name": "SDXL Base 1.0",
      "type": "model",
      "source": "huggingface",
      "repo": "stabilityai/stable-diffusion-xl-base-1.0",
      "file": "sd_xl_base_1.0.safetensors",
      "path": "models/checkpoints/sd_xl_base_1.0.safetensors",
      "sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b",
      "size_mb": 6938,
      "required": true,
      "conditions": {
        "set_conditions": [
          {
            "condition": "base_model_installed",
            "set_condition_when": "installed"
          }
        ]
      }
    },
    {
      "name": "SDXL Refiner 1.0",
      "type": "model",
      "source": "huggingface",
      "repo": "stabilityai/stable-diffusion-xl-refiner-1.0",
      "file": "sd_xl_refiner_1.0.safetensors",
      "path": "models/checkpoints/sd_xl_refiner_1.0.safetensors",
      "size_mb": 6075,
      "required": false,
      "conditions": {
        "match_type": "any",
        "match_conditions": [
          { "condition": "base_model_installed" }
        ]
      }
    },
    {
      "name": "SDXL VAE",
      "type": "model",
      "source": "huggingface",
      "repo": "stabilityai/sdxl-vae",
      "file": "sdxl_vae.safetensors",
      "path": "models/vae/sdxl_vae.safetensors",
      "size_mb": 335,
      "required": true
    },
    {
      "name": "ComfyUI Manager",
      "type": "custom_node",
      "source": "git",
      "url": "https://github.com/ltdrdata/ComfyUI-Manager.git",
      "path": "custom_nodes/ComfyUI-Manager",
      "ref": "main",
      "install_requirements": true,
      "required": true
    },
    {
      "name": "ControlNet Preprocessors",
      "type": "custom_node",
      "source": "git",
      "url": "https://github.com/Fannovel16/comfyui_controlnet_aux.git",
      "path": "custom_nodes/comfyui_controlnet_aux",
      "install_requirements": true,
      "required": false
    },
    {
      "name": "PyTorch CUDA 13.0 (Git Install)",
      "type": "pip_package",
      "source": "pip",
      "package": "torch",
      "version": "2.5.1",
      "extra_index_url": "https://download.pytorch.org/whl/cu130",
      "uninstall_current": true,
      "required": false,
      "conditions": {
        "match_type": "any",
        "match_conditions": [
          { "condition": "comfyui_git_install" }
        ]
      }
    },
    {
      "name": "Torchvision CUDA 13.0 (Git Install)",
      "type": "pip_package",
      "source": "pip",
      "package": "torchvision",
      "version": "0.20.1",
      "extra_index_url": "https://download.pytorch.org/whl/cu130",
      "uninstall_current": true,
      "required": false,
      "conditions": {
        "match_type": "any",
        "match_conditions": [
          { "condition": "comfyui_git_install" }
        ]
      }
    },
    {
      "name": "NumPy",
      "type": "pip_package",
      "source": "pip",
      "package": "numpy",
      "version": "1.24.3",
      "required": false
    },
    {
      "name": "Bundled Custom Wheel",
      "type": "pip_package",
      "source": "install_temp",
      "source_path": "wheels/custom_package-1.0.0-py3-none-any.whl",
      "required": false
    },
    {
      "name": "Bundled Workflow",
      "type": "file",
      "source": "install_temp",
      "source_path": "workflows/sdxl_workflow.json",
      "path": "user/default/workflows/sdxl_workflow.json"
    }
  ]
}
```

**Conditional Features Demonstrated:**
- **set_conditions**: Base model sets condition after installation
- **match_conditions**: Refiner only installs if base model installed
- **match_type**: Demonstrates ANY logic for conditions
- **comfyui_git_install**: PyTorch CUDA packages only for git-based installs
- **uninstall_current**: Remove existing PyTorch before installing new version
- **extra_index_url**: PyTorch CUDA wheels from custom index
- **install_temp**: Bundled files from ZIP package

## Package Structure (ZIP)

When distributing as a ZIP package, use this structure:

```
package.zip
├── manifest.json          # Required: Installation manifest
├── InstallTemp/          # Optional: Files referenced by manifest
│   ├── wheels/           # Bundled wheel packages
│   │   └── package.whl
│   ├── configs/          # Configuration files
│   │   └── settings.yaml
│   └── models/           # Small models (large models should be downloaded)
│       └── small_model.safetensors
└── ComfyUI/              # Optional: Files extracted directly
    ├── models/
    │   └── ...
    ├── custom_nodes/
    │   └── ...
    └── user/
        └── workflows/
            └── workflow.json
```

**Important:**
- `manifest.json` must be at the root of the ZIP
- `InstallTemp/` files are referenced in manifest with `"source": "install_temp"` and `source_path`
- `ComfyUI/` folder contents are merged directly into your ComfyUI installation
- Reference direct-extract files in manifest with `"source": "bundled"`
- Keep InstallTemp small - use download sources for large models

## Usage Examples

### Install from Manifest File
```bash
python ModularInstaller.py -c C:/ComfyUI -m sdxl_setup.json
```

### Install from ZIP Package
```bash
python ModularInstaller.py -c C:/ComfyUI -m complete_setup.zip
```

### Force Reinstall Everything
```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --force
```

### Install Only Required Items
```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --required-only
```

### Preview Before Installing
```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --list-contents
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --dry-run
```

### Install with Logging
```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json -l install.log
```

### Sequential Downloads (Slower but More Stable)
```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --sequential
```

### Clean Up Partial Downloads
```bash
python ModularInstaller.py -c C:/ComfyUI --cleanup
```

## Advanced Features

### Gated Models (HuggingFace)

Some models (like FLUX) require license acceptance and authentication. The installer **automatically prompts** for a token when gated models are detected.

**Automatic Token Prompt:**
When the installer detects gated models in the manifest and no `HF_TOKEN` is set, it will:
- **GUI Mode**: Show a password-protected dialog with instructions
- **CLI Mode**: Prompt in the terminal for token entry

**Manual Token Setup (Alternative):**
You can also set the token as an environment variable to skip the prompt:

```bash
# Windows (Command Prompt)
set HF_TOKEN=your_token_here

# Windows (PowerShell)
$env:HF_TOKEN="your_token_here"

# Linux/Mac
export HF_TOKEN=your_token_here
```

**To get a token:**
1. Visit https://huggingface.co/settings/tokens
2. Create a new token with **Read** permission
3. Accept the license for gated models on their HuggingFace pages
4. Enter the token when prompted (or set `HF_TOKEN` environment variable)

**Marking models as gated in manifest:**
```json
{
  "name": "FLUX.1 Dev",
  "type": "model",
  "source": "huggingface",
  "repo": "black-forest-labs/FLUX.1-dev",
  "file": "flux1-dev.safetensors",
  "path": "models/unet/flux1-dev.safetensors",
  "path_base": "comfyui",
  "gated": true,
  "required": true
}
```

The `"gated": true` flag tells the installer that this model requires authentication.

### Resume Interrupted Downloads

The installer automatically resumes interrupted downloads. If a download fails:

1. Fix the issue (network, disk space, etc.)
2. Run the same command again
3. Downloads resume from where they stopped

To disable resume functionality:
```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --no-resume
```

### ComfyUI Auto-Installation (Windows)

The installer can automatically download and set up ComfyUI portable on Windows:

**Automatic Installation:**
```bash
# Will auto-install to ~/ComfyUI_BP if not found
python ModularInstaller.py -m manifest.json
```

**Custom Installation Path:**
```bash
# Install to custom location
python ModularInstaller.py --install-path C:/MyComfyUI -m manifest.json
```

**Disable Auto-Install:**
```bash
# Require manual ComfyUI installation
python ModularInstaller.py --no-auto-install -m manifest.json
```

**How it works:**
1. Checks for ComfyUI at `~/ComfyUI_BP` (or custom path)
2. If found, prompts to continue with existing installation or cancel
3. If not found, prompts to download ComfyUI portable (~2GB)
4. Downloads from GitHub releases (latest version)
5. Extracts to target location using py7zr
6. Sets persistent `COMFYUI_BASE` environment variable
7. Automatically detects and uses embedded Python for all installations

**Environment Variable:**
After installation, the installer sets a persistent `COMFYUI_BASE` environment variable:
- **Value**: The base installation path (e.g., `C:\Users\YourName\ComfyUI_BP`)
- **Purpose**: Other tools and scripts can reference this location
- **Scope**: User-level (system-level requires admin/root privileges)
- **Persistence**:
  - Windows: Set via `setx` command
  - Linux/Mac: Added to `.bashrc`, `.zshrc`, or `.profile`

You can reference it in your own scripts:
```bash
# Windows
echo %COMFYUI_BASE%

# Linux/Mac
echo $COMFYUI_BASE
```

**Note:** Auto-installation is currently Windows-only. On Linux/Mac, you must:
- Install ComfyUI manually
- Specify path with `-c /path/to/ComfyUI`

### Blender Installation (Windows)

The installer can automatically install Blender 4.5 LTS for 3D object generation workflows:

**Automatic Installation:**
```bash
# Blender will be prompted during installation
python ModularInstaller.py -m manifest.json
```

**Skip Blender:**
```bash
# Skip Blender installation
python ModularInstaller.py -m manifest.json --skip-blender
```

**How it works:**
1. Checks if Blender is already installed via winget
2. If not found, prompts user to install
3. Uses `winget` to silently install Blender 4.5 LTS
4. Installation ID: `BlenderFoundation.Blender.LTS.4.5`

**Requirements:**
- Windows 10/11 with winget (App Installer from Microsoft Store)
- Automatically bypassed on Linux/Mac
- Uses silent installation (no user interaction needed)

**Manual Installation:**
If you prefer to install Blender manually:
```bash
winget install --id BlenderFoundation.Blender.LTS.4.5
```

### Embedded Python Support

When using ComfyUI portable (auto-installed or manual), the installer automatically:
- Detects the embedded Python at `ComfyUI_BP/python_embeded/python.exe`
- Uses it for all pip package installations
- Uses it for custom node `requirements.txt` installations

This ensures packages are installed into ComfyUI's isolated environment, not your system Python.

**Manual Override:**
If you want to use system Python instead:
```bash
python ModularInstaller.py -c /path/to/ComfyUI -m manifest.json
# Specifying -c manually disables embedded Python detection
```

### Parallel Downloads

By default, the installer downloads 4 items simultaneously. Adjust with `--workers`:

```bash
# Use 8 parallel workers
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --workers 8

# Disable parallelism
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --sequential
```

### Checksum Verification

The installer verifies SHA256 checksums for model files when provided. To skip verification:

```bash
python ModularInstaller.py -c C:/ComfyUI -m manifest.json --no-verify
```

## Troubleshooting

### "Manifest not found in ZIP"
- Ensure `manifest.json` is at the root of the ZIP file
- Check if it's named `manifest.json` (not `manifest.txt` or inside a folder)

### "Checksum mismatch"
- File may be corrupted
- Use `--force` to re-download
- Verify the SHA256 in your manifest is correct

### "Gated model" error
- Model requires license acceptance on HuggingFace
- Accept license and set `HF_TOKEN` environment variable
- Mark item with `"gated": true` in manifest

### "Git clone failed"
- Check internet connection
- Verify Git is installed and in PATH
- Try cloning the repository manually to test

### Custom nodes not loading
- Restart ComfyUI after installing custom nodes
- Check `ComfyUI/custom_nodes/` directory for errors
- Review installation logs for dependency errors

### Disk space issues
- Use `-t` to specify alternate temp directory
- Check available space before installing
- Clean up old installations: `--cleanup`

## Creating Your Own Manifests

1. **Start with package metadata:**
   ```json
   {
     "package": {
       "name": "My Setup",
       "version": "1.0.0",
       "description": "Description here"
     },
     "items": []
   }
   ```

2. **Add items for each resource:**
   - Models from HuggingFace
   - Custom nodes from Git
   - Local files or configs

3. **Set required flags appropriately:**
   - `"required": true` for essential items
   - `"required": false` for optional enhancements

4. **Include checksums for models:**
   - Download file first
   - Calculate SHA256: `sha256sum file.safetensors`
   - Add to manifest

5. **Test your manifest:**
   ```bash
   python ModularInstaller.py -c /path/to/test/ComfyUI -m your_manifest.json --dry-run
   ```

## Building Standalone Installers with PyInstaller

You can create standalone executable installers that bundle your manifest and optional InstallTemp files for distribution.

### Basic Setup

1. **Install PyInstaller:**
   ```bash
   pip install pyinstaller
   ```

2. **Create your package structure:**
   ```
   MyComfyUISetup/
   ├── package.zip              # Your package (manifest + optional InstallTemp)
   │   ├── manifest.json        # Required
   │   └── InstallTemp/         # Optional bundled files
   │       └── wheels/
   │           └── package.whl
   ├── ModularInstaller.py      # From this repo
   ├── core/                    # From this repo
   │   ├── __init__.py
   │   ├── manifest_handler.py
   │   ├── comfyui_installer.py
   │   ├── installer_gui.py
   │   └── ...
   └── requirements.txt         # From this repo
   ```

### Building the Installer

#### Option 1: Bundled Package (Recommended)

Bundle your `package.zip` inside the executable:

```bash
pyinstaller --noconfirm --onefile --windowed \
  --name "MyComfyUIInstaller" \
  --add-data "package.zip;." \
  --hidden-import=core.manifest_handler \
  --hidden-import=core.comfyui_installer \
  --hidden-import=core.installer_gui \
  --hidden-import=qtpy \
  --collect-all qtpy \
  --icon=icon.ico \
  ModularInstaller.py
```

**On Linux/Mac:**
```bash
pyinstaller --noconfirm --onefile --windowed \
  --name "MyComfyUIInstaller" \
  --add-data "package.zip:." \
  --hidden-import=core.manifest_handler \
  --hidden-import=core.comfyui_installer \
  --hidden-import=core.installer_gui \
  --hidden-import=qtpy \
  --collect-all qtpy \
  ModularInstaller.py
```

The installer automatically:
- Detects frozen executable mode
- Launches in GUI mode
- Looks for bundled `package.zip` in `sys._MEIPASS` (PyInstaller temp dir)
- Falls back to external `package.zip` in same directory as exe

#### Option 2: External Package

Build executable without bundled package (user provides package.zip):

```bash
pyinstaller --noconfirm --onefile --windowed \
  --name "ModularInstaller" \
  --hidden-import=core.manifest_handler \
  --hidden-import=core.comfyui_installer \
  --hidden-import=core.installer_gui \
  --hidden-import=qtpy \
  --collect-all qtpy \
  --icon=icon.ico \
  ModularInstaller.py
```

Users run: `ModularInstaller.exe` (launches GUI with file picker)

#### Option 3: PyInstaller Spec File (Advanced)

Create `installer.spec` for more control:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['ModularInstaller.py'],
    pathex=[],
    binaries=[],
    datas=[('package.zip', '.')],  # Bundle package.zip
    hiddenimports=[
        'core.manifest_handler',
        'core.comfyui_installer',
        'core.installer_gui',
        'core.package_manager',
        'qtpy',
        'PySide6',  # Or PyQt5
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Collect all qtpy files
from PyInstaller.utils.hooks import collect_all
qtpy_datas, qtpy_binaries, qtpy_hiddenimports = collect_all('qtpy')
a.datas += qtpy_datas
a.binaries += qtpy_binaries
a.hiddenimports += qtpy_hiddenimports

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MyComfyUIInstaller',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed mode (no console)
    disable_windowing_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Optional: Add custom icon
)
```

Build with:
```bash
pyinstaller installer.spec
```

### PyInstaller Best Practices

#### 1. Hidden Imports

ModularInstaller requires these hidden imports:
```python
hiddenimports=[
    'core.manifest_handler',
    'core.comfyui_installer',
    'core.installer_gui',
    'core.package_manager',
    'qtpy',
    'yaml',
    'requests',
    'huggingface_hub',
]
```

#### 2. Qt Bindings

The installer uses `qtpy` for Qt compatibility. Include Qt files:
```bash
--collect-all qtpy
```

Or specify your Qt backend:
```bash
--collect-all PySide6
# OR
--collect-all PyQt5
```

#### 3. Data Files

Bundle your package and any additional resources:
```python
# Windows
datas=[
    ('package.zip', '.'),
    ('icon.ico', '.'),
    ('README.txt', '.'),
]

# Linux/Mac - use ':' instead of ';'
datas=[
    ('package.zip', '.'),
    ('icon.png', '.'),
    ('README.txt', '.'),
]
```

#### 4. Reducing Executable Size

Exclude unnecessary modules:
```python
excludes=[
    'matplotlib',
    'pandas',
    'scipy',
    'PIL',
    'tkinter',
]
```

Use UPX compression:
```bash
--upx-dir=/path/to/upx
```

#### 5. Icon

Add a custom icon (Windows `.ico`, Linux/Mac `.png`):
```bash
--icon=icon.ico
```

### Package Distribution Structure

**Internal Bundle (Recommended):**
```
MyComfyUIInstaller.exe     # Everything in one file
```

**External Package:**
```
dist/
├── MyComfyUIInstaller.exe
└── package.zip             # User can replace with custom package
```

**With InstallTemp:**

Your `package.zip` structure:
```
package.zip
├── manifest.json
└── InstallTemp/
    ├── wheels/
    │   ├── custom_package1.whl
    │   └── custom_package2.whl
    ├── configs/
    │   └── settings.yaml
    └── models/
        └── small_model.safetensors
```

Large files (models, checkpoints) should be downloaded via manifest, not bundled in InstallTemp.

### Testing Your Build

1. **Test the executable:**
   ```bash
   # Windows
   dist\MyComfyUIInstaller.exe

   # Linux/Mac
   ./dist/MyComfyUIInstaller
   ```

2. **Test on clean system:**
   - No Python installed
   - No dependencies installed
   - Different Windows versions (7, 10, 11)
   - Different Linux distributions

3. **Verify bundled package:**
   - Check that GUI opens automatically
   - Verify package.zip is detected
   - Test installation flow

### Common Issues and Solutions

**Issue:** `FileNotFoundError: package.zip`
- **Solution:** Ensure package.zip is in `--add-data` list or next to executable

**Issue:** `ModuleNotFoundError: qtpy`
- **Solution:** Add `--collect-all qtpy` and ensure PySide6/PyQt5 installed

**Issue:** `Import error: No module named 'core.manifest_handler'`
- **Solution:** Add all core modules to `hiddenimports`

**Issue:** Large executable size (>100MB)
- **Solution:** Use `--exclude` for unused modules, enable UPX compression

**Issue:** Antivirus false positives
- **Solution:** Code sign your executable (requires certificate)

### Advanced: Code Signing (Windows)

Sign your executable to avoid SmartScreen warnings:

```bash
# Using signtool (Windows SDK)
signtool sign /f certificate.pfx /p password /tr http://timestamp.digicert.com /td sha256 /fd sha256 MyComfyUIInstaller.exe
```

Or use a cloud signing service like:
- DigiCert
- GlobalSign
- Sectigo

### Example: Complete Build Script

**build_installer.bat** (Windows):
```batch
@echo off
echo Building ModularInstaller...

REM Clean previous builds
rmdir /s /q build dist

REM Build with PyInstaller
pyinstaller --noconfirm --onefile --windowed ^
  --name "MyComfyUISetup" ^
  --add-data "package.zip;." ^
  --hidden-import=core.manifest_handler ^
  --hidden-import=core.comfyui_installer ^
  --hidden-import=core.installer_gui ^
  --hidden-import=core.package_manager ^
  --collect-all qtpy ^
  --icon=icon.ico ^
  --upx-dir=C:\upx ^
  ModularInstaller.py

echo.
echo Build complete! Executable at: dist\MyComfyUISetup.exe
pause
```

**build_installer.sh** (Linux/Mac):
```bash
#!/bin/bash
echo "Building ModularInstaller..."

# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller --noconfirm --onefile --windowed \
  --name "MyComfyUISetup" \
  --add-data "package.zip:." \
  --hidden-import=core.manifest_handler \
  --hidden-import=core.comfyui_installer \
  --hidden-import=core.installer_gui \
  --hidden-import=core.package_manager \
  --collect-all qtpy \
  ModularInstaller.py

echo ""
echo "Build complete! Executable at: dist/MyComfyUISetup"
```

### Distributing Your Installer

1. **GitHub Releases:** Upload `.exe` with release notes
2. **Direct download:** Host on website with SHA256 checksums
3. **With documentation:** Include README with:
   - System requirements
   - Installation steps
   - Troubleshooting
   - License information

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Add your license information here]

## Support

For issues or questions:
- Open an issue on GitHub
- Check the troubleshooting section above
- Review installation logs for detailed error messages
