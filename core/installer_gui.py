"""GUI for ComfyUI Modular Installer."""

import sys
import os
from pathlib import Path
from typing import Optional

try:
    from qtpy.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
        QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox,
        QCheckBox, QFormLayout, QTextEdit, QProgressBar
    )
    from qtpy.QtCore import Qt, QThread, Signal
    from qtpy.QtGui import QFont, QIcon
    QT_AVAILABLE = True
except Exception:
    QT_AVAILABLE = False


class InstallerThread(QThread):
    """Thread for running installer operations."""
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal(bool, str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        """Run the installation in a separate thread."""
        try:
            # Import here to avoid circular imports
            from core.comfyui_installer import ComfyUIInstaller
            from core.manifest_handler import ManifestHandler

            self.log_signal.emit("Starting installation...")

            # Install/detect ComfyUI
            if not self.config.get('comfy_path'):
                self.log_signal.emit("Checking for ComfyUI installation...")
                install_path_str = self.config.get('install_path', '~/ComfyUI_BP')
                install_path = Path(os.path.expanduser(install_path_str))
                installer = ComfyUIInstaller(install_path=install_path)

                if not installer.check_existing_installation():
                    self.log_signal.emit("ComfyUI not found. Installing...")
                    success, message = installer.install_comfyui()
                    if not success:
                        self.finished_signal.emit(False, message)
                        return
                    self.log_signal.emit(f"✓ {message}")

                info = installer.get_installation_info()
                comfy_path = info['comfyui_path']
                python_executable = info['python_executable']

                # Install Blender if requested
                if self.config.get('install_blender') and sys.platform == 'win32':
                    self.log_signal.emit("Checking Blender installation...")
                    if not installer.check_blender_installed():
                        self.log_signal.emit("Installing Blender 4.5 LTS...")
                        success, message = installer.install_blender()
                        self.log_signal.emit(f"Blender: {message}")
                else:
                    if sys.platform == 'win32':
                        msg = "⊘ Skipping Blender installation (disabled by user)"
                        self.log_signal.emit(msg)
                        print(msg)  # Also print to console
                    else:
                        msg = "⊘ Skipping Blender installation (not supported on this platform)"
                        self.log_signal.emit(msg)
                        print(msg)  # Also print to console
            else:
                comfy_path = Path(self.config['comfy_path'])
                python_executable = None

            # Process manifest
            manifest_path = Path(self.config['manifest_path'])
            self.log_signal.emit(f"Loading manifest: {manifest_path.name}")

            handler = ManifestHandler(
                manifest_path=manifest_path,
                comfy_path=comfy_path,
                python_executable=python_executable,
                max_workers=self.config.get('workers', 4)
            )

            handler.load_manifest()
            handler.validate_manifest()

            self.log_signal.emit("Downloading and installing items...")
            handler.download_items(
                skip_existing=not self.config.get('force', False),
                required_only=self.config.get('required_only', False),
                parallel=True
            )

            self.log_signal.emit("\n✓ Installation completed successfully!")
            self.finished_signal.emit(True, "Installation completed successfully")

        except Exception as e:
            self.log_signal.emit(f"\n✗ Error: {str(e)}")
            self.finished_signal.emit(False, str(e))


def run_installer_gui() -> dict:
    """Launch the installer GUI."""
    if not QT_AVAILABLE:
        print("Qt bindings not found. Please install PySide6 or PyQt5.")
        sys.exit(1)

    app = QApplication(sys.argv)

    # Set window icon
    script_dir = Path(__file__).parent
    icon_path = script_dir / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    win = InstallerWindow()
    win.show()

    app.exec_()

    if win.result:
        return win.result
    else:
        sys.exit(0)


class InstallerWindow(QWidget):
    """Main installer GUI window."""

    def __init__(self):
        super().__init__()
        self.result = None
        self.installer_thread = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("ComfyUI Modular Installer")
        self.setMinimumSize(700, 600)
        self.resize(700, 600)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # Title
        title = QLabel("ComfyUI Modular Installer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        # === INSTALLATION OPTIONS ===
        install_group = QGroupBox("Installation Options")
        install_layout = QFormLayout()
        install_group.setLayout(install_layout)

        # ComfyUI Path
        comfy_layout = QHBoxLayout()
        self.comfy_path_edit = QLineEdit()
        self.comfy_path_edit.setPlaceholderText("Auto-install to ~/ComfyUI_BP")
        comfy_browse_btn = QPushButton("Browse...")
        comfy_browse_btn.clicked.connect(self.browse_comfy_path)
        comfy_layout.addWidget(self.comfy_path_edit)
        comfy_layout.addWidget(comfy_browse_btn)
        install_layout.addRow("ComfyUI Path (optional):", comfy_layout)

        # Manifest Path
        manifest_layout = QHBoxLayout()
        self.manifest_path_edit = QLineEdit()
        self.manifest_path_edit.setPlaceholderText("Select manifest.json or package.zip")
        manifest_browse_btn = QPushButton("Browse...")
        manifest_browse_btn.clicked.connect(self.browse_manifest)
        manifest_layout.addWidget(self.manifest_path_edit)
        manifest_layout.addWidget(manifest_browse_btn)
        install_layout.addRow("Manifest File*:", manifest_layout)

        main_layout.addWidget(install_group)

        # === DOWNLOAD OPTIONS ===
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)

        self.force_checkbox = QCheckBox("Force re-download all items")
        self.required_only_checkbox = QCheckBox("Install only required items")
        self.install_blender_checkbox = QCheckBox("Install Blender 4.5 LTS (Windows only)")
        self.install_blender_checkbox.setChecked(True)

        if sys.platform != "win32":
            self.install_blender_checkbox.setEnabled(False)
            self.install_blender_checkbox.setToolTip("Blender auto-install is Windows-only")

        options_layout.addWidget(self.force_checkbox)
        options_layout.addWidget(self.required_only_checkbox)
        options_layout.addWidget(self.install_blender_checkbox)

        main_layout.addWidget(options_group)

        # === PROGRESS ===
        progress_group = QGroupBox("Installation Progress")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(200)
        progress_layout.addWidget(self.log_output)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        main_layout.addWidget(progress_group)

        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.install_btn = QPushButton("Install")
        self.install_btn.setMinimumWidth(120)
        self.install_btn.clicked.connect(self.start_installation)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumWidth(120)
        self.cancel_btn.clicked.connect(self.close)

        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(button_layout)

    def browse_comfy_path(self):
        """Browse for ComfyUI directory."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select ComfyUI Directory",
            str(Path.home())
        )
        if path:
            self.comfy_path_edit.setText(path)

    def browse_manifest(self):
        """Browse for manifest file or package."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Manifest or Package",
            str(Path.home()),
            "Manifest Files (manifest.json manifest.yaml manifest.yml *.zip);;All Files (*)"
        )
        if path:
            self.manifest_path_edit.setText(path)

    def start_installation(self):
        """Start the installation process."""
        manifest_path = self.manifest_path_edit.text().strip()

        if not manifest_path:
            QMessageBox.warning(self, "Missing Information", "Please select a manifest file or package.")
            return

        if not Path(manifest_path).exists():
            QMessageBox.warning(self, "File Not Found", f"Manifest file not found: {manifest_path}")
            return

        # Disable controls
        self.install_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.log_output.clear()

        # Build configuration
        config = {
            'manifest_path': manifest_path,
            'force': self.force_checkbox.isChecked(),
            'required_only': self.required_only_checkbox.isChecked(),
            'install_blender': self.install_blender_checkbox.isChecked(),
        }

        comfy_path = self.comfy_path_edit.text().strip()
        if comfy_path:
            config['comfy_path'] = comfy_path

        # Start installer thread
        self.installer_thread = InstallerThread(config)
        self.installer_thread.log_signal.connect(self.append_log)
        self.installer_thread.finished_signal.connect(self.installation_finished)
        self.installer_thread.start()

    def append_log(self, message: str):
        """Append message to log output."""
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def installation_finished(self, success: bool, message: str):
        """Handle installation completion."""
        self.progress_bar.setVisible(False)
        self.install_btn.setEnabled(True)

        if success:
            QMessageBox.information(
                self,
                "Installation Complete",
                "ComfyUI and all components have been installed successfully!"
            )
            self.result = {'success': True}
            self.close()
        else:
            QMessageBox.critical(
                self,
                "Installation Failed",
                f"Installation failed:\n\n{message}"
            )


if __name__ == "__main__":
    run_installer_gui()
