"""ComfyUI portable installation and detection."""

import os
import sys
import shutil
import requests
from pathlib import Path
from typing import Optional, Tuple
from tqdm import tqdm
import py7zr


class ComfyUIInstaller:
    """Handles ComfyUI portable installation and detection."""

    COMFYUI_DOWNLOAD_URL = "https://github.com/comfyanonymous/ComfyUI/releases/latest/download/ComfyUI_windows_portable_nvidia.7z"
    DEFAULT_INSTALL_PATH = Path(os.path.expanduser("~")) / "ComfyUI_BP"

    def __init__(self, install_path: Optional[Path] = None, log_file: Optional[Path] = None):
        """
        Initialize ComfyUI installer.

        Args:
            install_path: Path where ComfyUI should be installed (default: ~/ComfyUI_BP)
            log_file: Optional log file path
        """
        self.install_path = Path(install_path) if install_path else self.DEFAULT_INSTALL_PATH
        self.log_file = log_file

    def log(self, message: str, level: str = "INFO"):
        """Log message to console and file."""
        print(message)
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{level}] {message}\n")

    def check_existing_installation(self) -> bool:
        """
        Check if ComfyUI is already installed at the target location.

        Returns:
            True if installation exists, False otherwise
        """
        if not self.install_path.exists():
            return False

        # Check for key ComfyUI files/directories
        key_files = [
            self.install_path / "ComfyUI" / "main.py",
            self.install_path / "python_embeded"  # Note: ComfyUI uses 'embeded' not 'embedded'
        ]

        return any(f.exists() for f in key_files)

    def get_python_executable(self) -> Optional[Path]:
        """
        Get path to embedded Python executable.

        Returns:
            Path to python.exe if found, None otherwise
        """
        # ComfyUI portable uses 'python_embeded' (not 'embedded')
        possible_paths = [
            self.install_path / "python_embeded" / "python.exe",
            self.install_path / "python_embedded" / "python.exe",  # Just in case
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return None

    def get_comfyui_path(self) -> Optional[Path]:
        """
        Get path to ComfyUI directory.

        Returns:
            Path to ComfyUI folder if found, None otherwise
        """
        comfyui_path = self.install_path / "ComfyUI"
        return comfyui_path if comfyui_path.exists() else None

    def download_comfyui(self, output_path: Path) -> bool:
        """
        Download ComfyUI portable archive.

        Args:
            output_path: Where to save the downloaded .7z file

        Returns:
            True if successful, False otherwise
        """
        self.log(f"Downloading ComfyUI portable from GitHub...")
        self.log(f"URL: {self.COMFYUI_DOWNLOAD_URL}")

        try:
            response = requests.get(self.COMFYUI_DOWNLOAD_URL, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Download with progress bar
            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True,
                         desc="Downloading ComfyUI", ncols=80) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            self.log(f"✓ Download complete: {output_path}")
            return True

        except Exception as e:
            self.log(f"✗ Download failed: {e}", "ERROR")
            return False

    def extract_comfyui(self, archive_path: Path, extract_to: Path) -> bool:
        """
        Extract ComfyUI 7z archive.

        Args:
            archive_path: Path to .7z file
            extract_to: Directory to extract to

        Returns:
            True if successful, False otherwise
        """
        self.log(f"Extracting ComfyUI to: {extract_to}")

        try:
            # Ensure extraction directory exists
            extract_to.mkdir(parents=True, exist_ok=True)

            # Extract with py7zr
            with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                archive.extractall(path=extract_to)

            self.log(f"✓ Extraction complete")
            return True

        except Exception as e:
            self.log(f"✗ Extraction failed: {e}", "ERROR")
            return False

    def install_comfyui(self, force_reinstall: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Install ComfyUI portable to the target location.

        Args:
            force_reinstall: If True, reinstall even if already exists

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check for existing installation
        if self.check_existing_installation() and not force_reinstall:
            return True, f"ComfyUI already installed at {self.install_path}"

        # Create temp directory for download
        temp_dir = Path(os.path.expanduser("~")) / "temp_comfyui_install"
        temp_dir.mkdir(parents=True, exist_ok=True)
        archive_path = temp_dir / "ComfyUI_portable.7z"

        try:
            # Download
            if not self.download_comfyui(archive_path):
                return False, "Failed to download ComfyUI"

            # Extract
            if not self.extract_comfyui(archive_path, self.install_path):
                return False, "Failed to extract ComfyUI"

            # Verify installation
            if not self.check_existing_installation():
                return False, "Installation verification failed"

            # Cleanup
            self.log("Cleaning up temporary files...")
            shutil.rmtree(temp_dir, ignore_errors=True)

            return True, f"ComfyUI successfully installed to {self.install_path}"

        except Exception as e:
            self.log(f"✗ Installation failed: {e}", "ERROR")
            # Cleanup on failure
            shutil.rmtree(temp_dir, ignore_errors=True)
            return False, f"Installation failed: {e}"

    def get_installation_info(self) -> dict:
        """
        Get information about the ComfyUI installation.

        Returns:
            Dictionary with installation details
        """
        info = {
            'installed': self.check_existing_installation(),
            'install_path': self.install_path,
            'comfyui_path': self.get_comfyui_path(),
            'python_executable': self.get_python_executable(),
            'is_portable': False,
            'platform': sys.platform
        }

        if info['python_executable']:
            info['is_portable'] = True

        return info

    @staticmethod
    def prompt_user_action() -> int:
        """
        Prompt user for action when existing installation is found.

        Returns:
            1 for install/resume, 2 for cancel
        """
        print("\n" + "=" * 60)
        print("EXISTING COMFYUI INSTALLATION DETECTED")
        print("=" * 60)
        print("An existing ComfyUI installation was found.")
        print("\nHow would you like to proceed?")
        print("  1. Install or resume install into existing ComfyUI")
        print("  2. Cancel installation")
        print("=" * 60)

        while True:
            try:
                choice = input("\nEnter your choice (1 or 2): ").strip()
                if choice in ['1', '2']:
                    return int(choice)
                else:
                    print("Invalid choice. Please enter 1 or 2.")
            except (KeyboardInterrupt, EOFError):
                print("\n\nCancelled by user.")
                return 2


if __name__ == "__main__":
    """Test the ComfyUI installer."""
    installer = ComfyUIInstaller()

    print("ComfyUI Installation Info:")
    print("-" * 40)
    info = installer.get_installation_info()
    for key, value in info.items():
        print(f"{key}: {value}")

    if not info['installed']:
        print("\n" + "=" * 40)
        print("ComfyUI not found. Install? (y/n): ", end="")
        response = input().strip().lower()
        if response == 'y':
            success, message = installer.install_comfyui()
            print(message)
