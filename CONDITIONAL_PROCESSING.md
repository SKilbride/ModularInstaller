# Advanced Conditional Processing in ModularInstaller

## Overview

The ModularInstaller supports advanced conditional processing with OS detection, match logic (AND/OR), and flexible condition timing. This allows you to create sophisticated installation manifests that adapt to different platforms, installation methods, and runtime scenarios.

## Automatic Conditions

The installer automatically sets these conditions based on the system and installation type:

### OS Detection (Automatic)
- **`os_windows`** - Set on Windows systems
- **`os_linux`** - Set on Linux systems
- **`os_mac`** - Set on macOS systems (recommended)
- **`os_darwin`** - Set on macOS systems (alias for os_mac)

### Installation Type (Automatic)
- **`comfyui_git_install`** - Set when using git-based installation (`--git-install-comfyui` or default on Linux)
- **`comfyui_portable_install`** - Set when using portable installation (Windows default)

### Command Line Conditions
- Custom conditions can be set via `--set-condition` flag (can be used multiple times)

```bash
python ModularInstaller.py -m manifest.yaml --set-condition cuda_support --set-condition high_vram
```

## Manifest Syntax

### Basic Structure

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

### Field Descriptions

#### `match_type` (Optional, default: "any")
Determines how multiple match conditions are evaluated:
- **`any`** - Item installs if ANY condition is met (OR logic) - **DEFAULT**
- **`all`** - Item installs if ALL conditions are met (AND logic)

#### `match_conditions` (Optional)
List of conditions that must be met for the item to be processed. Each can be:
- Simple string: `- condition: os_windows`
- Dict format: `- { condition: os_windows }`

If no match_conditions are specified, the item always processes.

#### `set_conditions` (Optional)
List of conditions to set after processing this item. Each entry can specify:
- **`condition`** - Name of the condition to set
- **`set_condition_when`** - When to set the condition:
  - **`installed`** (default) - Only set if item was actually installed (not skipped)
  - **`always`** - Set even if item was skipped (already exists)

## Examples

### Example 1: OS-Specific Installations

Install different packages based on the operating system:

```yaml
items:
  # Windows-only: Install Visual C++ Redistributable
  - name: Microsoft.VCRedist.2015+.x64
    type: application
    source: winget
    package_id: Microsoft.VCRedist.2015+.x64
    conditions:
      match_type: any
      match_conditions:
        - condition: os_windows

  # Linux-only: System dependencies message
  - name: "Linux System Dependencies"
    type: file
    source: local
    source_path: "docs/linux-deps.txt"
    path: "README-LINUX.txt"
    conditions:
      match_type: any
      match_conditions:
        - condition: os_linux

  # macOS-only: Homebrew dependencies
  - name: "macOS Setup Instructions"
    type: file
    source: local
    source_path: "docs/macos-setup.txt"
    path: "README-MACOS.txt"
    conditions:
      match_type: any
      match_conditions:
        - condition: os_mac
```

### Example 2: Installation Method-Specific Packages

Install different PyTorch versions based on installation type:

```yaml
items:
  # Git installation: CUDA-enabled PyTorch
  - name: "PyTorch CUDA 13.0"
    type: pip_package
    source: pip
    package: "torch"
    version: "2.5.1"
    extra_index_url: "https://download.pytorch.org/whl/cu130"
    uninstall_current: true
    conditions:
      match_type: any
      match_conditions:
        - condition: comfyui_git_install

  # Portable installation: CPU-only PyTorch
  - name: "PyTorch CPU"
    type: pip_package
    source: pip
    package: "torch"
    version: "2.5.1"
    conditions:
      match_type: any
      match_conditions:
        - condition: comfyui_portable_install
```

### Example 3: Combined OS and Installation Type (AND Logic)

Install packages only when BOTH conditions are met:

```yaml
items:
  # Windows + Git Install
  - name: "Windows Git-Specific Package"
    type: pip_package
    source: pip
    package: "windows-git-package"
    conditions:
      match_type: all  # Requires BOTH conditions
      match_conditions:
        - condition: os_windows
        - condition: comfyui_git_install

  # Linux + Portable Install (unlikely but demonstrates flexibility)
  - name: "Linux Portable Package"
    type: pip_package
    source: pip
    package: "linux-portable-package"
    conditions:
      match_type: all
      match_conditions:
        - condition: os_linux
        - condition: comfyui_portable_install
```

### Example 4: Dependency Chains with set_condition_when

Create installation dependencies where later items depend on earlier ones:

```yaml
items:
  # Install core dependencies first
  - name: "Core Dependencies"
    type: pip_package
    source: pip
    package: "numpy"
    version: "1.24.3"
    conditions:
      set_conditions:
        - condition: core_installed
          set_condition_when: installed  # Only if actually installed

  # Plugin requires core to be installed
  - name: "Advanced Plugin"
    type: pip_package
    source: pip
    package: "advanced-plugin"
    conditions:
      match_type: any
      match_conditions:
        - condition: core_installed  # Won't install unless core_installed is set
      set_conditions:
        - condition: plugin_ready
          set_condition_when: installed
```

### Example 5: Always Set Conditions

Set conditions regardless of whether the item was installed or skipped:

```yaml
items:
  # Check if base model exists, set condition either way
  - name: "SDXL Base Model"
    type: model
    source: huggingface
    repo: "stabilityai/stable-diffusion-xl-base-1.0"
    file: "sd_xl_base_1.0.safetensors"
    path: "models/checkpoints/sd_xl_base_1.0.safetensors"
    conditions:
      set_conditions:
        - condition: sdxl_available
          set_condition_when: always  # Set even if file already exists

  # Optional refiner, only if SDXL is available
  - name: "SDXL Refiner"
    type: model
    source: huggingface
    repo: "stabilityai/stable-diffusion-xl-refiner-1.0"
    file: "sd_xl_refiner_1.0.safetensors"
    path: "models/checkpoints/sd_xl_refiner_1.0.safetensors"
    conditions:
      match_type: any
      match_conditions:
        - condition: sdxl_available
```

### Example 6: Custom Conditions from Command Line

Combine automatic and custom conditions:

```bash
# Run with CUDA support flag
python ModularInstaller.py -m manifest.yaml --set-condition cuda_support
```

```yaml
items:
  # Only install if user explicitly requests CUDA support
  - name: "CUDA Toolkit Dependencies"
    type: pip_package
    source: pip
    package: "nvidia-cuda-runtime-cu12"
    conditions:
      match_type: all
      match_conditions:
        - condition: os_windows
        - condition: cuda_support  # From command line

  # Install CPU fallback if CUDA NOT requested
  - name: "CPU Optimized Libraries"
    type: pip_package
    source: pip
    package: "openvino"
    # No match_conditions = always installs if cuda_support isn't handled elsewhere
```

### Example 7: Platform-Specific Applications

```yaml
items:
  # Windows package manager installs
  - name: "Git for Windows"
    type: application
    source: winget
    package_id: "Git.Git"
    conditions:
      match_type: any
      match_conditions:
        - condition: os_windows
      set_conditions:
        - condition: git_installed
          set_condition_when: installed

  # Linux: Assumes git is installed via package manager
  - name: "Git Check (Linux)"
    type: file
    source: bundled
    path: ".git-installed"  # Marker file
    conditions:
      match_type: any
      match_conditions:
        - condition: os_linux
      set_conditions:
        - condition: git_installed
          set_condition_when: always
```

### Example 8: Complex Multi-Condition Scenarios

```yaml
items:
  # Windows + Git Install + CUDA Support
  - name: "Full Windows CUDA Stack"
    type: pip_package
    source: pip
    package: "torch torchvision torchaudio"
    extra_index_url: "https://download.pytorch.org/whl/cu130"
    conditions:
      match_type: all  # Must meet ALL three conditions
      match_conditions:
        - condition: os_windows
        - condition: comfyui_git_install
        - condition: cuda_support

  # Any platform + Git Install (no CUDA)
  - name: "Cross-Platform CPU PyTorch"
    type: pip_package
    source: pip
    package: "torch torchvision torchaudio"
    conditions:
      match_type: all
      match_conditions:
        - condition: comfyui_git_install
      # Note: Explicitly NOT checking for cuda_support
```

## Use Cases

### 1. Cross-Platform Packages
Install platform-specific versions or configurations:
- Different binary wheels for Windows/Linux/macOS
- Platform-specific configuration files
- OS-specific dependencies or prerequisites

### 2. Installation Type Optimization
Tailor packages to installation method:
- CUDA PyTorch for git installs (assumes user has GPU)
- CPU PyTorch for portable installs (broader compatibility)
- Conda-specific packages vs pip packages

### 3. Progressive Enhancement
Build features progressively:
- Core dependencies set conditions
- Advanced features check for core conditions
- Optional plugins require specific capabilities

### 4. User-Driven Customization
Let users choose features at install time:
- `--set-condition professional` for pro features
- `--set-condition minimal` for lightweight install
- `--set-condition development` for dev tools

### 5. Dependency Management
Ensure correct installation order:
- Base libraries installed first
- Framework packages second
- Application-specific packages last
- Each sets conditions for the next

## Best Practices

### 1. Use Descriptive Condition Names
```yaml
# Good
- condition: cuda_gpu_available
- condition: professional_features_enabled

# Avoid
- condition: flag1
- condition: temp_cond
```

### 2. Default to `match_type: any`
Most use cases benefit from OR logic. Only use `all` when you truly need AND logic.

### 3. Use `set_condition_when: installed` by Default
Only use `always` when you need to set conditions for items that might already exist (like checking for existing files).

### 4. Document Custom Conditions
If your manifest uses custom conditions (via `--set-condition`), document them in the manifest metadata:

```yaml
package:
  name: "My Package"
  version: "1.0.0"
  description: "Install with --set-condition cuda_support for GPU acceleration"
```

### 5. Test All Branches
Test your manifest with different combinations:
- Each OS platform
- Git vs portable installation
- With and without custom conditions

### 6. Provide Fallbacks
Always provide sensible defaults:

```yaml
items:
  # Preferred: CUDA version
  - name: "PyTorch CUDA"
    conditions:
      match_conditions:
        - condition: cuda_support

  # Fallback: CPU version (no conditions = always installs if CUDA doesn't)
  - name: "PyTorch CPU"
    # Will be skipped if CUDA version already installed
```

## Troubleshooting

### Item Not Installing

**Check active conditions:**
The installer logs active conditions at startup. Verify your expected conditions are set.

**Check match_type:**
- `match_type: all` requires ALL conditions
- `match_type: any` requires ANY condition
- Missing match_type defaults to `any`

**Check condition spelling:**
Condition names are case-sensitive:
- ✓ `os_windows`
- ✗ `OS_Windows`
- ✗ `windows`

### Condition Not Being Set

**Check set_condition_when:**
- `installed` (default) - Only if item was actually processed
- `always` - Even if item was skipped

**Check installation success:**
If an item fails to install, conditions won't be set (even with `installed`).

### Unexpected Behavior

**Check condition order:**
Conditions are evaluated in manifest order. Ensure dependencies are listed before dependents.

**Check for condition conflicts:**
Using `match_type: all` with conditions that can't both be true:
```yaml
# This will NEVER install (can't be both Windows and Linux)
conditions:
  match_type: all
  match_conditions:
    - condition: os_windows
    - condition: os_linux
```

## Advanced Patterns

### Feature Flags
```yaml
items:
  # Enable feature with --set-condition experimental
  - name: "Experimental Features"
    type: pip_package
    source: pip
    package: "experimental-package"
    conditions:
      match_type: any
      match_conditions:
        - condition: experimental
```

### Cascade Conditions
```yaml
items:
  - name: "Level 1"
    conditions:
      set_conditions:
        - condition: level1_done
          set_condition_when: installed

  - name: "Level 2"
    conditions:
      match_conditions:
        - condition: level1_done
      set_conditions:
        - condition: level2_done
          set_condition_when: installed

  - name: "Level 3"
    conditions:
      match_conditions:
        - condition: level2_done
```

### Mutual Exclusion
```yaml
items:
  # Either CUDA...
  - name: "CUDA Backend"
    conditions:
      match_conditions:
        - condition: use_cuda
      set_conditions:
        - condition: backend_configured
          set_condition_when: installed

  # ...OR CPU
  - name: "CPU Backend"
    conditions:
      match_conditions:
        - condition: use_cpu
      set_conditions:
        - condition: backend_configured
          set_condition_when: installed
```

## Reference

### Automatic Conditions Summary

| Condition | When Set | Description |
|-----------|----------|-------------|
| `os_windows` | Always on Windows | Windows operating system |
| `os_linux` | Always on Linux | Linux operating system |
| `os_mac` | Always on macOS | macOS (recommended name) |
| `os_darwin` | Always on macOS | macOS (alternative name) |
| `comfyui_git_install` | Git-based install | Conda environment install |
| `comfyui_portable_install` | Portable install | Windows portable install |

### match_type Values

| Value | Logic | When Item Installs |
|-------|-------|-------------------|
| `any` (default) | OR | If ANY match_condition is met |
| `all` | AND | If ALL match_conditions are met |

### set_condition_when Values

| Value | When Condition Is Set |
|-------|----------------------|
| `installed` (default) | Only if item was actually installed |
| `always` | Even if item was skipped (already exists) |

## See Also

- README.md - Main documentation with manifest format
- Example manifests in the repository
- `--list-contents` flag to preview what would be installed
- `--dry-run` flag to test conditional logic without installing
