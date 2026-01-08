# ComfyUI Modular Installer

## Overview
The ComfyUI Modular Installer is a flexible system for installing ComfyUI workflows, models, custom nodes, and assets from packaged distributions. It automates the extraction and installation process, handling dependencies, model downloads, and custom node setup.

Key features:
- Installs workflow packages (ZIP archives) containing models, nodes, and assets
- Smart extraction that skips already-installed files
- Manifest support for downloading models from HuggingFace, Git repositories, and URLs
- Automatic custom node installation with dependency management
- Supports both GUI and command-line interfaces
- Validates package structure and workflow JSON before installation

## Prerequisites
1. A working ComfyUI installation
2. Git (for cloning repositories and custom nodes)
3. Python 3.8 or higher

## Installation/Setup
1. Install ComfyUI (portable, manual installation, or desktop app version)
2. Open a command prompt, PowerShell, or terminal in the ComfyUI folder
3. Clone this repository:
   ```bash
   git clone https://github.com/SKilbride/ModularInstaller
   ```
4. Navigate to the ModularInstaller directory:
   ```bash
   cd ModularInstaller
   ```
5. Install dependencies (use the Python environment from your ComfyUI installation):
   ```bash
   python -m pip install -r requirements.txt
   ```

## Usage

### GUI Mode
The GUI provides a visual interface for selecting installation options:

```bash
python ModularInstaller.py --gui
```

**ComfyUI Folder:**
> Select the "ComfyUI" folder of your ComfyUI installation

**Workflow Package:**
> Select the workflow ZIP package to install, or a workflow JSON file

**Options:**
- **Extract Minimal**: Only extract workflow JSON files (assumes models/nodes already installed)
- **Force Extract**: Re-extract all files even if they already exist
- **Verify Only**: Check package validity without installing

### CLI Mode
Install packages using command-line options:

```bash
python ModularInstaller.py -c /path/to/ComfyUI -w /path/to/package.zip
```

#### Common Examples

**Basic installation:**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip
```

**Installation with logging:**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip -l install.log
```

**Force reinstallation of all files:**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip -f
```

**Minimal extraction (workflow files only):**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip -e
```

**List package contents without installing:**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip --list-contents
```

**Verify package without installing:**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip --verify-only
```

**Use alternate temporary directory:**
```bash
python ModularInstaller.py -c ./ComfyUI -w workflow_package.zip -t /mnt/temp
```

## Command Line Arguments

### Required Arguments
- **`-c, --comfy_path`** - Path to ComfyUI installation directory (not needed with `--gui`)
- **`-w, --workflow_path`** - Path to workflow ZIP package, JSON file, or directory (not needed with `--gui`)

### Optional Arguments
- **`--gui`** - Launch the graphical user interface
- **`-e, --extract_minimal`** - Extract only JSON files (assumes models/nodes already installed)
- **`-f, --force-extract`** - Force re-extraction of all files even if they exist
- **`-l, --log [FILE]`** - Enable logging to file (auto-generated name if no file specified)
- **`-t, --temp_path PATH`** - Alternate temporary directory for extraction
- **`--verify-only`** - Verify package structure without installing
- **`--list-contents`** - List package contents without extracting
- **`-h, --help`** - Show help message

## Package Format

Workflow packages are ZIP archives containing all necessary files, models, and configurations. Files must be at the root level (no extra folders in the ZIP).

### Required Files

| File | Description |
|------|-------------|
| **workflow.json** | ComfyUI workflow in API format (required) |

### Optional Files

| File | Description |
|------|-------------|
| **warmup.json** | Simplified workflow variant (optional) |
| **baseconfig.json** | Package configuration settings (optional) |
| **manifest.json** | Model download manifest for HuggingFace/Git/URLs (optional) |
| **pre.py** | Python script to run before installation (optional) |
| **post.py** | Python script to run after installation (optional) |

### Folder Structure

| Folder | Description |
|--------|-------------|
| **ComfyUI/** | Contains subfolders/files to install into ComfyUI (models, custom_nodes, etc.) |

### Example Package Structure
```
package.zip
├── workflow.json           # Required: Main workflow
├── warmup.json            # Optional: Simplified workflow
├── baseconfig.json        # Optional: Configuration
├── manifest.json          # Optional: Model download manifest
├── pre.py                 # Optional: Pre-installation script
├── post.py                # Optional: Post-installation script
└── ComfyUI/               # Installation root
    ├── models/
    │   ├── checkpoints/
    │   │   └── model.safetensors
    │   ├── vae/
    │   │   └── vae.safetensors
    │   └── loras/
    │       └── lora.safetensors
    ├── custom_nodes/
    │   └── custom_node_name/
    │       ├── __init__.py
    │       ├── requirements.txt
    │       └── pyproject.toml
    └── input/
        └── input_image.jpg
```

**Important Notes:**
- Zip the contents directly (no top-level folder in the ZIP)
- Models, LoRAs, and custom nodes go in their respective folders under `ComfyUI/`
- Input assets (images, videos) should be referenced from the `input/` folder in workflows
- Custom nodes with dependencies can include `requirements.txt` for automatic installation

## Manifest Support

The installer supports manifest files for downloading models from external sources:

### Manifest Format (manifest.json)
```json
{
  "models": [
    {
      "type": "huggingface",
      "repo": "black-forest-labs/FLUX.1-dev",
      "filename": "flux1-dev.safetensors",
      "destination": "models/checkpoints/flux1-dev.safetensors",
      "sha256": "optional-checksum-here"
    },
    {
      "type": "url",
      "url": "https://example.com/model.safetensors",
      "destination": "models/vae/model.safetensors"
    },
    {
      "type": "git",
      "repo": "https://github.com/username/repo.git",
      "destination": "custom_nodes/repo_name"
    }
  ]
}
```

### Supported Download Types
- **huggingface**: Download from HuggingFace Hub
- **url**: Direct download from URL
- **git**: Clone Git repository

The installer automatically:
- Downloads missing files
- Verifies checksums (if provided)
- Skips already-downloaded files (unless `--force-extract` is used)
- Handles parallel downloads for faster installation

## Output and Logging

The installer provides clear output during installation:

```
============================================================
ComfyUI Modular Installer
============================================================
ComfyUI Path: /path/to/ComfyUI
Package: workflow_package.zip
============================================================

[1/3] Extracting package...
[package_manager] Checking for manifest...
[package_manager] ✅ Manifest processed - models downloaded
[smart_extractor] Mode: SMART
[smart_extractor] Extracted root: workflow.json
✓ Package extracted to: /tmp/temp_abc123

[2/3] Loading workflow...
✓ Workflow loaded successfully

[3/3] Installation complete!

============================================================
INSTALLATION SUMMARY
============================================================
Package: workflow_package
ComfyUI Path: /path/to/ComfyUI
✓ Models downloaded via manifest
✓ Custom nodes installed
✓ Files extracted: 125
  Files skipped (already up-to-date): 42
✓ Workflow saved to: /tmp/temp_abc123/workflow.json

⚠️  IMPORTANT: Restart ComfyUI to load new custom nodes
============================================================
```

## Troubleshooting

**Package structure invalid:**
- Ensure `workflow.json` exists at the root of the ZIP
- Check that the ZIP doesn't have an extra top-level folder

**Models not installing:**
- Verify manifest.json syntax
- Check internet connection for downloads
- Use `--force-extract` to re-download

**Custom nodes not working:**
- Restart ComfyUI after installation (custom nodes require restart)
- Check custom node `requirements.txt` for missing dependencies
- Review installation logs for errors

**Disk space issues:**
- Use `-t` to specify an alternate temporary directory
- Clear old temporary files from ComfyUI/temp

**Workflow validation errors:**
- Ensure workflow is exported in API format (not UI format)
- Use "Save (API Format)" in ComfyUI to export workflows

## Advanced Features

### Pre/Post Installation Scripts

Include `pre.py` or `post.py` in your package for custom installation logic:

**pre.py** - Runs before file extraction:
```python
import os
import shutil

# Create custom directories
os.makedirs("custom_folder", exist_ok=True)
print("Pre-installation setup complete")
```

**post.py** - Runs after file extraction:
```python
import subprocess
import sys

# Install additional dependencies
subprocess.check_call([sys.executable, "-m", "pip", "install", "custom-package"])

# Signal that ComfyUI restart is required (optional)
print("BENCHMARK_RESTART_REQUIRED")
print("Post-installation setup complete")
```

### Smart Extraction

The installer intelligently skips files that are already installed and up-to-date:
- Compares file sizes to detect changes
- Checks custom node versions via `pyproject.toml`
- Only extracts changed or new files
- Use `--force-extract` to override and reinstall everything

## Development

### Project Structure
```
ModularInstaller/
├── ModularInstaller.py      # Main installer script
├── core/
│   ├── package_manager.py   # Coordinates extraction and manifest
│   ├── smart_extractor.py   # Smart file extraction
│   ├── workflow_manager.py  # Workflow loading and validation
│   ├── manifest_handler.py  # Model download management
│   ├── manifest_integration.py  # Manifest integration
│   └── gui.py              # Qt-based GUI
├── workflows/
│   └── workflows.json       # Example workflow registry
├── requirements.txt         # Python dependencies
└── README.md               # This file
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
