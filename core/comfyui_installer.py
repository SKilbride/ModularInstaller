"""
ComfyUI Installation Module

Handles cross-platform installation of ComfyUI from GitHub with Miniconda support.
Supports both Windows and Linux platforms.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path
from typing import Optional, Tuple


class ComfyUIInstaller:
    """Manages ComfyUI installation with Miniconda environment."""

    def __init__(self, install_path: Path, log_file: Optional[Path] = None):
        """
        Initialize ComfyUI installer.

        Args:
            install_path: Path where ComfyUI should be installed
            log_file: Optional log file for installation output
        """
        self.install_path = Path(install_path)
        self.log_file = log_file
        self.platform = sys.platform
        self.is_windows = self.platform == "win32"
        self.is_linux = self.platform.startswith("linux")

    def log(self, message: str, level: str = "INFO"):
        """Log a message to console and optionally to file."""
        formatted = f"[{level}] {message}"
        print(formatted)
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(formatted + '\n')

    def check_conda_installed(self) -> Tuple[bool, Optional[str]]:
        """
        Check if Conda is installed and accessible.

        Returns:
            Tuple of (is_installed, conda_executable_path)
        """
        self.log("Checking for Conda installation...")

        # Try to find conda executable
        conda_commands = ['conda', 'mamba']  # mamba is a faster conda alternative

        for cmd in conda_commands:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.log(f"Found {cmd}: {version}")

                    # Get conda executable path
                    which_cmd = 'where' if self.is_windows else 'which'
                    result = subprocess.run(
                        [which_cmd, cmd],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    conda_path = result.stdout.strip().split('\n')[0] if result.returncode == 0 else cmd
                    return True, conda_path
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
                continue

        self.log("Conda not found on system", "WARNING")
        return False, None

    def install_miniconda_windows(self) -> bool:
        """
        Install Miniconda on Windows using winget.

        Returns:
            True if installation succeeded, False otherwise
        """
        self.log("Installing Miniconda on Windows via winget...")

        try:
            # Check if winget is available
            result = subprocess.run(
                ['winget', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.log("winget not available. Please install Windows Package Manager.", "ERROR")
                return False

            self.log("Installing Miniconda3 via winget...")
            result = subprocess.run(
                ['winget', 'install', '--id', 'Anaconda.Miniconda3', '--silent', '--accept-package-agreements', '--accept-source-agreements'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            if result.returncode == 0:
                self.log("✓ Miniconda installed successfully")
                self.log("Please restart your terminal/command prompt for conda to be available in PATH")
                return True
            else:
                self.log(f"✗ Miniconda installation failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Failed to install Miniconda: {e}", "ERROR")
            return False

    def install_miniconda_linux(self) -> bool:
        """
        Install Miniconda on Linux using the official installer script.

        Returns:
            True if installation succeeded, False otherwise
        """
        self.log("Installing Miniconda on Linux...")

        try:
            import tempfile
            import urllib.request

            # Determine architecture
            machine = platform.machine()
            if machine == 'x86_64':
                installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
            elif machine == 'aarch64':
                installer_url = "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"
            else:
                self.log(f"Unsupported architecture: {machine}", "ERROR")
                return False

            # Download installer
            self.log(f"Downloading Miniconda installer from {installer_url}...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.sh') as tmp_file:
                installer_path = tmp_file.name
                urllib.request.urlretrieve(installer_url, installer_path)

            # Make installer executable
            os.chmod(installer_path, 0o755)

            # Run installer
            home_dir = Path.home()
            miniconda_path = home_dir / "miniconda3"

            self.log(f"Running Miniconda installer (installing to {miniconda_path})...")
            result = subprocess.run(
                ['bash', installer_path, '-b', '-p', str(miniconda_path)],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            # Clean up installer
            os.unlink(installer_path)

            if result.returncode == 0:
                self.log("✓ Miniconda installed successfully")

                # Initialize conda for the current shell
                conda_path = miniconda_path / "bin" / "conda"
                self.log("Initializing conda for bash...")
                subprocess.run(
                    [str(conda_path), 'init', 'bash'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                self.log("Please run 'source ~/.bashrc' or restart your terminal for conda to be available")
                return True
            else:
                self.log(f"✗ Miniconda installation failed: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Failed to install Miniconda: {e}", "ERROR")
            return False

    def ensure_conda_installed(self) -> Optional[str]:
        """
        Ensure Conda is installed, installing if necessary.

        Returns:
            Path to conda executable if successful, None otherwise
        """
        is_installed, conda_path = self.check_conda_installed()

        if is_installed:
            return conda_path

        # Conda not installed, prompt user
        self.log("Miniconda is not installed on this system.", "WARNING")
        response = input("Would you like to install Miniconda now? (y/n): ").strip().lower()

        if response not in ['y', 'yes']:
            self.log("Installation cancelled by user", "WARNING")
            return None

        # Install based on platform
        if self.is_windows:
            success = self.install_miniconda_windows()
        elif self.is_linux:
            success = self.install_miniconda_linux()
        else:
            self.log(f"Unsupported platform: {self.platform}", "ERROR")
            return None

        if not success:
            return None

        # Check again after installation
        is_installed, conda_path = self.check_conda_installed()
        if is_installed:
            return conda_path
        else:
            self.log("Conda installed but not found in PATH. Please restart your terminal.", "ERROR")
            return None

    def create_conda_environment(self, env_name: str = "comfyui_bp", python_version: str = "3.11") -> bool:
        """
        Create a conda environment for ComfyUI.

        Args:
            env_name: Name of the conda environment (default: comfyui_bp)
            python_version: Python version to use (default: 3.11)

        Returns:
            True if successful, False otherwise
        """
        conda_path = self.ensure_conda_installed()
        if not conda_path:
            return False

        self.log(f"Creating conda environment '{env_name}' with Python {python_version}...")

        try:
            # Check if environment already exists
            result = subprocess.run(
                [conda_path, 'env', 'list'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if env_name in result.stdout:
                self.log(f"Environment '{env_name}' already exists")
                response = input(f"Remove and recreate environment '{env_name}'? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    self.log(f"Removing existing environment '{env_name}'...")
                    subprocess.run(
                        [conda_path, 'env', 'remove', '-n', env_name, '-y'],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                else:
                    self.log(f"Using existing environment '{env_name}'")
                    return True

            # Create new environment
            self.log(f"Creating environment with Python {python_version}...")
            result = subprocess.run(
                [conda_path, 'create', '-n', env_name, f'python={python_version}', '-y'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            if result.returncode == 0:
                self.log(f"✓ Conda environment '{env_name}' created successfully")
                return True
            else:
                self.log(f"✗ Failed to create environment: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Failed to create conda environment: {e}", "ERROR")
            return False

    def clone_comfyui_from_github(self, repo_url: str = "https://github.com/comfyanonymous/ComfyUI.git") -> bool:
        """
        Clone ComfyUI from GitHub.

        Args:
            repo_url: ComfyUI GitHub repository URL

        Returns:
            True if successful, False otherwise
        """
        self.log(f"Cloning ComfyUI from {repo_url}...")

        # Check if git is available
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                self.log("Git is not installed. Please install Git first.", "ERROR")
                return False
        except FileNotFoundError:
            self.log("Git is not installed. Please install Git first.", "ERROR")
            return False

        # Check if directory already exists
        if self.install_path.exists():
            if (self.install_path / ".git").exists():
                self.log(f"ComfyUI repository already exists at {self.install_path}")
                response = input("Update existing repository? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    return self.update_comfyui_repo()
                else:
                    return True
            else:
                self.log(f"Directory {self.install_path} exists but is not a git repository", "ERROR")
                response = input("Remove existing directory and clone fresh? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    shutil.rmtree(self.install_path)
                else:
                    return False

        # Create parent directory if needed
        self.install_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self.log("Cloning repository (this may take a few minutes)...")
            result = subprocess.run(
                ['git', 'clone', repo_url, str(self.install_path)],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes
            )

            if result.returncode == 0:
                self.log(f"✓ ComfyUI cloned successfully to {self.install_path}")
                return True
            else:
                self.log(f"✗ Failed to clone ComfyUI: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Failed to clone ComfyUI: {e}", "ERROR")
            return False

    def update_comfyui_repo(self) -> bool:
        """
        Update an existing ComfyUI repository.

        Returns:
            True if successful, False otherwise
        """
        self.log("Updating ComfyUI repository...")

        try:
            result = subprocess.run(
                ['git', 'pull'],
                cwd=self.install_path,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.log("✓ ComfyUI updated successfully")
                return True
            else:
                self.log(f"✗ Failed to update ComfyUI: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Failed to update ComfyUI: {e}", "ERROR")
            return False

    def install_comfyui_dependencies(self, env_name: str = "comfyui_bp") -> bool:
        """
        Install ComfyUI dependencies in the conda environment.

        Args:
            env_name: Name of the conda environment

        Returns:
            True if successful, False otherwise
        """
        conda_path = self.ensure_conda_installed()
        if not conda_path:
            return False

        # Check if requirements.txt exists
        requirements_file = self.install_path / "requirements.txt"
        if not requirements_file.exists():
            self.log(f"requirements.txt not found at {requirements_file}", "ERROR")
            return False

        self.log(f"Installing ComfyUI dependencies in environment '{env_name}'...")

        try:
            # Get conda base path
            result = subprocess.run(
                [conda_path, 'info', '--base'],
                capture_output=True,
                text=True,
                timeout=30
            )
            conda_base = result.stdout.strip()

            # Construct path to python in the conda environment
            if self.is_windows:
                env_python = Path(conda_base) / "envs" / env_name / "python.exe"
            else:
                env_python = Path(conda_base) / "envs" / env_name / "bin" / "python"

            if not env_python.exists():
                self.log(f"Python not found in environment at {env_python}", "ERROR")
                return False

            # Install dependencies using pip in the conda environment
            self.log("Installing dependencies (this may take several minutes)...")
            result = subprocess.run(
                [str(env_python), '-m', 'pip', 'install', '-r', str(requirements_file)],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes
            )

            if result.returncode == 0:
                self.log("✓ ComfyUI dependencies installed successfully")

                # Install PyTorch with CUDA support if on Linux
                if self.is_linux:
                    self.log("Installing PyTorch with CUDA support...")
                    result = subprocess.run(
                        [str(env_python), '-m', 'pip', 'install', 'torch', 'torchvision', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cu121'],
                        capture_output=True,
                        text=True,
                        timeout=1800
                    )
                    if result.returncode == 0:
                        self.log("✓ PyTorch with CUDA support installed")
                    else:
                        self.log(f"⚠ PyTorch installation warning: {result.stderr}", "WARNING")

                return True
            else:
                self.log(f"✗ Failed to install dependencies: {result.stderr}", "ERROR")
                return False

        except Exception as e:
            self.log(f"✗ Failed to install dependencies: {e}", "ERROR")
            return False

    def full_install(self, env_name: str = "comfyui_bp", python_version: str = "3.11") -> bool:
        """
        Perform a full ComfyUI installation.

        Args:
            env_name: Name of the conda environment
            python_version: Python version to use

        Returns:
            True if successful, False otherwise
        """
        self.log("=" * 60)
        self.log("Starting ComfyUI Installation")
        self.log("=" * 60)

        # Step 1: Ensure conda is installed
        if not self.ensure_conda_installed():
            return False

        # Step 2: Create conda environment
        if not self.create_conda_environment(env_name, python_version):
            return False

        # Step 3: Clone ComfyUI
        if not self.clone_comfyui_from_github():
            return False

        # Step 4: Install dependencies
        if not self.install_comfyui_dependencies(env_name):
            return False

        self.log("=" * 60)
        self.log("✓ ComfyUI installation completed successfully!")
        self.log("=" * 60)
        self.log(f"Installation path: {self.install_path}")
        self.log(f"Conda environment: {env_name}")
        self.log("")
        self.log("To activate the environment, run:")
        self.log(f"  conda activate {env_name}")
        self.log("")
        self.log("To start ComfyUI, run:")
        self.log(f"  cd {self.install_path}")
        self.log(f"  python main.py")

        return True


def main():
    """CLI interface for ComfyUI installer."""
    import argparse

    parser = argparse.ArgumentParser(description='ComfyUI Installer with Miniconda support')
    parser.add_argument('--install-path', type=Path, default=Path.home() / "ComfyUI",
                       help='Path where ComfyUI should be installed (default: ~/ComfyUI)')
    parser.add_argument('--env-name', type=str, default='comfyui_bp',
                       help='Name of conda environment (default: comfyui_bp)')
    parser.add_argument('--python-version', type=str, default='3.11',
                       help='Python version to use (default: 3.11)')
    parser.add_argument('--log-file', type=Path, help='Path to log file')
    parser.add_argument('--check-only', action='store_true',
                       help='Only check if conda is installed, don\'t install anything')

    args = parser.parse_args()

    installer = ComfyUIInstaller(args.install_path, args.log_file)

    if args.check_only:
        is_installed, conda_path = installer.check_conda_installed()
        if is_installed:
            print(f"Conda is installed: {conda_path}")
            sys.exit(0)
        else:
            print("Conda is not installed")
            sys.exit(1)
    else:
        success = installer.full_install(args.env_name, args.python_version)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
