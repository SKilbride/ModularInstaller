# ComfyUI Modular Installer

## Overview
The ComfyUI Modular Installer is a manifest-driven system for installing ComfyUI models, custom nodes, and assets. It uses declarative manifest files to specify what should be downloaded and where, supporting multiple sources including HuggingFace, Git repositories, direct URLs, and local files.

### Key Features
- **Automatic ComfyUI Installation**: Automatically downloads and installs ComfyUI portable on Windows
- **Blender Integration**: Auto-install Blender 4.5 LTS via winget (Windows only)
- **GUI and CLI modes**: Choose between graphical interface or command-line operation
- **Manifest-driven**: Declare all dependencies in a single JSON/YAML file
- **Multiple sources**: HuggingFace Hub, Git repositories, direct URLs, local files, and pip packages
- **Flexible path management**: Install to ComfyUI, home directory, temp, or absolute paths
- **Embedded Python support**: Automatically uses ComfyUI's embedded Python for package installations
- **Smart caching**: Skip already-downloaded files and verify checksums
- **Parallel downloads**: Download multiple items simultaneously for faster installation
- **Resume capability**: Continue interrupted downloads from where they left off
- **Bundled packages**: Include files directly in ZIP packages alongside the manifest

## Prerequisites
1. Git (for cloning custom node repositories)
2. Python 3.8 or higher (for the installer itself; ComfyUI portable includes embedded Python)
3. Optional: HuggingFace token for gated models (set `HF_TOKEN` environment variable)
4. Windows (for auto-installation feature; manual ComfyUI installation required on Linux/Mac)

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
- **`--no-auto-install`** - Disable automatic ComfyUI installation if not found
- **`--skip-blender`** - Skip Blender 4.5 LTS installation (Windows only)
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
| `directory` | Directory to download/clone |
| `pip_package` | Python package to install via pip |
| `config` | Configuration file |

### Source Types

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
- `remote_path` - (Optional) If file is in a subdirectory, full path like "repo/tree/main/subfolder"
- `gated` - (Optional) Set to `true` if model requires license acceptance
- `sha256` or `sha` - (Optional) SHA256 checksum for verification

#### 2. Git Repository

Clone Git repositories (perfect for custom nodes):

```json
{
  "name": "ComfyUI Manager",
  "type": "custom_node",
  "source": "git",
  "url": "https://github.com/ltdrdata/ComfyUI-Manager.git",
  "path": "custom_nodes/ComfyUI-Manager",
  "ref": "main",
  "install_requirements": true,
  "required": true
}
```

**Fields:**
- `url` - Git repository URL
- `path` - Destination path relative to ComfyUI directory
- `ref` - (Optional) Branch, tag, or commit (default: "main")
- `install_requirements` - (Optional) Run `pip install -r requirements.txt` after cloning

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
- `path` - Destination path relative to ComfyUI directory
- `executable` - (Optional) Make file executable after download (Linux/Mac)
- `sha256` or `sha` - (Optional) SHA256 checksum for verification

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
- `path` - Destination path relative to ComfyUI directory

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

#### 6. Pip Package

Install Python packages via pip:

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

**Fields:**
- `package` - Package name on PyPI
- `version` - (Optional) Specific version to install

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
- **`required`** (optional) - If `true`, installation fails if this item fails
- **`size_mb`** (optional) - Size in megabytes (for display purposes)

#### Path Base Examples

```json
{
  "name": "SDXL Model",
  "path": "models/checkpoints/sdxl.safetensors",
  "path_base": "comfyui"  // Installs to ComfyUI/models/checkpoints/
},
{
  "name": "User Config",
  "path": ".comfyui/settings.json",
  "path_base": "home"  // Installs to ~/. comfyui/settings.json
},
{
  "name": "Shared Model",
  "path": "/opt/models/shared/model.safetensors",
  "path_base": "absolute"  // Installs to exact path
}
```

## Complete Example Manifest

```json
{
  "package": {
    "name": "SDXL Complete Setup",
    "version": "1.0.0",
    "description": "Full SDXL setup with custom nodes"
  },
  "metadata": {
    "total_size_mb": 15000,
    "estimated_time": "10-15 minutes",
    "tags": ["sdxl", "upscaling"],
    "details": "Includes SDXL base, refiner, VAE, and essential custom nodes"
  },
  "items": [
    {
      "name": "SDXL Base 1.0",
      "type": "model",
      "source": "huggingface",
      "repo": "stabilityai/stable-diffusion-xl-base-1.0",
      "file": "sd_xl_base_1.0.safetensors",
      "path": "models/checkpoints/sd_xl_base_1.0.safetensors",
      "size_mb": 6938,
      "required": true
    },
    {
      "name": "SDXL Refiner 1.0",
      "type": "model",
      "source": "huggingface",
      "repo": "stabilityai/stable-diffusion-xl-refiner-1.0",
      "file": "sd_xl_refiner_1.0.safetensors",
      "path": "models/checkpoints/sd_xl_refiner_1.0.safetensors",
      "size_mb": 6075,
      "required": false
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
      "name": "NumPy",
      "type": "pip_package",
      "source": "pip",
      "package": "numpy",
      "version": "1.24.3",
      "required": false
    }
  ]
}
```

## Package Structure (ZIP)

When distributing as a ZIP package, use this structure:

```
package.zip
├── manifest.json          # Required: Installation manifest
└── ComfyUI/              # Optional: Bundled files
    ├── models/
    │   └── ...
    ├── custom_nodes/
    │   └── ...
    └── user/
        └── ...
```

**Important:**
- `manifest.json` must be at the root of the ZIP
- Files in `ComfyUI/` folder are extracted directly to your ComfyUI installation
- Reference bundled files in manifest with `"source": "bundled"`

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

Some models require license acceptance. To download gated models:

1. Accept the license on HuggingFace website
2. Create a HuggingFace access token with read permissions
3. Set environment variable:
   ```bash
   # Windows
   set HF_TOKEN=your_token_here

   # Linux/Mac
   export HF_TOKEN=your_token_here
   ```
4. Run installer normally

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
