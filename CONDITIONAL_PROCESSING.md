# Conditional Processing in ModularInstaller

## Overview

The ModularInstaller now supports conditional processing of manifest items. This allows you to control which items are installed based on runtime conditions that can be set via command line arguments or automatically based on the installation type.

## Features

### 1. Setting Conditions via Command Line

You can set conditions using the `--set-condition` flag (can be used multiple times):

```bash
python ModularInstaller.py -m manifest.yaml --set-condition my_condition --set-condition another_condition
```

### 2. Automatic Conditions

Some conditions are set automatically based on the installation type:

- `comfyui_git_install`: Automatically set when using git-based ComfyUI installation (--git-install-comfyui flag or default on Linux)

### 3. Manifest Syntax

#### match_condition

Items can specify a `match_condition` field. If set, the item will only be processed if that condition exists:

```yaml
items:
  - name: "torchvision CUDA 13.0"
    type: pip_package
    source: pip
    package: "torchvision"
    version: "0.24.1"
    extra_index_url: "https://download.pytorch.org/whl/cu130"
    uninstall_current: true
    match_condition: comfyui_git_install  # Only install if git installation is used
```

#### set_condition

Items can specify a `set_condition` field. When the item is processed (even if skipped because it already exists), the condition(s) will be added to the active condition set:

```yaml
items:
  - name: "Base Package"
    type: pip_package
    source: pip
    package: "numpy"
    set_condition: base_installed  # Sets this condition after processing

  - name: "Optional Package"
    type: pip_package
    source: pip
    package: "scipy"
    match_condition: base_installed  # Only processes if base_installed condition is set
```

The `set_condition` field supports both single strings and lists:

```yaml
# Single condition
set_condition: my_condition

# Multiple conditions
set_condition:
  - condition_one
  - condition_two
```

## Use Cases

### 1. Platform-Specific Packages

Install different packages based on the installation type:

```yaml
items:
  # Portable installation packages
  - name: "Portable Python Package"
    type: pip_package
    source: pip
    package: "some-package"
    match_condition: comfyui_portable_install

  # Git installation packages
  - name: "Conda Python Package"
    type: pip_package
    source: pip
    package: "some-package"
    match_condition: comfyui_git_install
```

### 2. Dependency Chains

Create dependencies between items:

```yaml
items:
  - name: "Core Library"
    type: pip_package
    source: pip
    package: "core-lib"
    set_condition: core_ready

  - name: "Plugin A"
    type: pip_package
    source: pip
    package: "plugin-a"
    match_condition: core_ready

  - name: "Plugin B"
    type: pip_package
    source: pip
    package: "plugin-b"
    match_condition: core_ready
```

### 3. Optional Feature Groups

Allow users to selectively install feature groups:

```bash
# Install with CUDA support
python ModularInstaller.py -m manifest.yaml --set-condition cuda_support

# Install with CPU-only support
python ModularInstaller.py -m manifest.yaml --set-condition cpu_only
```

```yaml
items:
  - name: "PyTorch CUDA"
    type: pip_package
    source: pip
    package: "torch"
    extra_index_url: "https://download.pytorch.org/whl/cu130"
    match_condition: cuda_support

  - name: "PyTorch CPU"
    type: pip_package
    source: pip
    package: "torch"
    match_condition: cpu_only
```

## Implementation Details

### Condition Storage

Conditions are stored as a Python `set` in the `ManifestHandler` instance. This ensures:
- Fast lookup (O(1) for checking if a condition exists)
- No duplicates
- Order doesn't matter

### Processing Order

1. Items are processed in the order they appear in the manifest
2. Before processing an item, `match_condition` is checked
3. If the condition doesn't exist, the item is skipped
4. After successfully processing an item (or if it's skipped because it already exists), `set_condition` is processed
5. Conditions set by early items can affect later items in the same run

### Skipped Items

Items that are skipped due to missing conditions are logged with a message like:

```
⊘ Skipping Item Name (condition not met: required_condition)
```

## GUI Support

The GUI automatically supports conditions through the config dictionary. The automatic `comfyui_git_install` condition is set when the "Install ComfyUI from GitHub using conda" checkbox is selected.

## Example Manifest

```yaml
package:
  name: "Conditional Example"
  version: "1.0.0"

items:
  # Always installed
  - name: "ComfyUI Manager"
    type: custom_node
    source: git
    url: "https://github.com/ltdrdata/ComfyUI-Manager.git"
    path: "custom_nodes/ComfyUI-Manager"
    set_condition: manager_installed

  # Only for git installations
  - name: "Conda Dependencies"
    type: pip_package
    source: pip
    package: "conda-specific-package"
    match_condition: comfyui_git_install

  # Only after manager is installed
  - name: "Manager Plugin"
    type: file
    source: url
    url: "https://example.com/plugin.json"
    path: "custom_nodes/ComfyUI-Manager/plugin.json"
    match_condition: manager_installed
```
