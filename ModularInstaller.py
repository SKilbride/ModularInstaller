import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.workflow_manager import WorkflowManager
from core.package_manager import PackageManager
from core.gui import run_gui


class YamlObject:
    """Helper class for reading YAML configuration files."""
    def __init__(self, yaml_path):
        import yaml
        self.yaml_path = yaml_path
        self.data = None
        self.load()

    def load(self):
        import yaml
        if os.path.exists(self.yaml_path):
            with open(self.yaml_path, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}

    def exists(self):
        return os.path.exists(self.yaml_path)

    def get(self, key, default=None):
        if self.data is None:
            self.load()
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value


def load_baseconfig(comfy_path, temp_dir=None, log_file=None):
    """Load configuration from baseconfig.json if it exists."""
    baseconfig_path = Path(comfy_path) / "baseconfig.json"
    paths_to_check = [baseconfig_path]
    if temp_dir:
        paths_to_check.append(Path(temp_dir) / "baseconfig.json")

    selected_path = None
    for path in paths_to_check:
        if path.exists():
            selected_path = path
            break

    if not selected_path:
        print(f"Info: baseconfig.json not found. Using defaults.")
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"Info: baseconfig.json not found. Using defaults.\n")
        return {}

    try:
        with open(selected_path, 'r', encoding='utf-8') as f:
            baseconfig = json.load(f)
        if not isinstance(baseconfig, dict):
            raise ValueError("Invalid baseconfig.json")

        print(f"Loaded baseconfig from: {selected_path}")
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"Loaded baseconfig from {selected_path}\n")
        return baseconfig
    except Exception as e:
        print(f"Failed to load baseconfig: {e}. Using defaults.")
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"Failed to load baseconfig: {e}\n")
        return {}


def main():
    """Main installer entry point."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(
        description="ComfyUI Modular Installer - Install workflows, models, and custom nodes from packages."
    )
    parser.add_argument("-c", "--comfy_path", type=str, help="Path to ComfyUI folder")
    parser.add_argument("-w", "--workflow_path", type=str, help="Path to workflow ZIP or folder")
    parser.add_argument("-e", "--extract_minimal", action="store_true",
                        help="Extract only JSON files (assumes models/nodes already installed)")
    parser.add_argument("-l", "--log", nargs='?', const=True, default=False,
                        help="Enable logging to file")
    parser.add_argument("-t", "--temp_path", type=str,
                        help="Alternate temporary directory for extraction")
    parser.add_argument("--force-extract", "-f", action="store_true",
                        help="Force re-extraction of all files even if they already exist")
    parser.add_argument("--gui", action="store_true",
                        help="Show a Qt-based GUI to pick installation options")
    parser.add_argument("--verify-only", action="store_true",
                        help="Only verify the package contents without installing")
    parser.add_argument("--list-contents", action="store_true",
                        help="List package contents without extracting")

    args = parser.parse_args()

    # === GUI MODE ===
    if args.gui:
        comfy_path_arg = Path(args.comfy_path).resolve() if args.comfy_path else None
        workflow_path_arg = Path(args.workflow_path).resolve() if args.workflow_path else None
        try:
            # Note: GUI needs to be updated to remove benchmark-specific options
            gui_result = run_gui(
                comfy_path=comfy_path_arg,
                workflow_path=workflow_path_arg,
                extract_minimal=args.extract_minimal,
                force_extract=args.force_extract
            )
        except SystemExit:
            sys.exit(0)

        # Apply GUI results
        args.comfy_path = str(gui_result['comfy_path'])
        args.workflow_path = str(gui_result['workflow_path'])
        args.extract_minimal = gui_result.get('extract_minimal', False)
        args.force_extract = gui_result.get('force_extract', False)
    else:
        if not args.comfy_path:
            parser.error("--comfy_path (-c) is required when not using --gui.")
        if not args.workflow_path:
            parser.error("--workflow_path (-w) is required when not using --gui.")

    # === LOG FILE ===
    log_file = None
    if args.log is not False:
        workflow_basename = Path(args.workflow_path).stem
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        log_file = Path(args.log).resolve() if args.log is not True else Path(f"{workflow_basename}_install_{timestamp}.txt").resolve()
        if log_file.is_dir():
            log_file = log_file / f"{workflow_basename}_install_{timestamp}.txt"
        print(f"Logging to: {log_file}")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Installation started: {datetime.now()}\n")

    workflow_path = Path(args.workflow_path).resolve()
    comfy_path = Path(args.comfy_path).resolve()
    package_manager = None

    try:
        print("\n" + "=" * 60)
        print("ComfyUI Modular Installer")
        print("=" * 60)
        print(f"ComfyUI Path: {comfy_path}")
        print(f"Package: {workflow_path}")
        print("=" * 60 + "\n")

        # === LIST CONTENTS MODE ===
        if args.list_contents:
            if workflow_path.suffix.lower() == '.zip':
                import zipfile
                print("\nPackage contents:")
                print("-" * 60)
                with zipfile.ZipFile(workflow_path, 'r') as zf:
                    for info in zf.infolist():
                        if not info.is_dir():
                            size_mb = info.file_size / (1024 * 1024)
                            print(f"  {info.filename:<50} {size_mb:>8.2f} MB")
                print("-" * 60)
                return
            else:
                print("Error: --list-contents only works with ZIP files")
                return

        # === HANDLE WORKFLOW PATH ===
        if workflow_path.is_dir():
            workflow_file = workflow_path / "workflow.json"
            if not workflow_file.exists():
                raise FileNotFoundError(f"workflow.json not found in {workflow_path}")
            workflow_path = workflow_file
            print(f"Using workflow: {workflow_path}")

        elif workflow_path.suffix.lower() == '.zip':
            print("\n[1/3] Extracting package...")
            package_manager = PackageManager(
                zip_path=workflow_path,
                comfy_path=comfy_path,
                temp_path=args.temp_path,
                extract_minimal=args.extract_minimal,
                force_extract=args.force_extract,
                log_file=log_file
            )
            workflow_path = package_manager.extract_zip()
            print(f"✓ Package extracted to: {workflow_path.parent}")

        elif workflow_path.suffix.lower() == '.json':
            print(f"Using standalone workflow: {workflow_path}")
        else:
            raise ValueError("Invalid workflow path: must be .zip, .json, or directory")

        # === LOAD AND VALIDATE WORKFLOW ===
        print("\n[2/3] Loading workflow...")
        workflow_manager = WorkflowManager(workflow_path=workflow_path, log_file=log_file)
        workflow_manager.load_workflow()
        print(f"✓ Workflow loaded successfully")

        # === VERIFY MODE ===
        if args.verify_only:
            print("\n[3/3] Verification complete")
            print("\n" + "=" * 60)
            print("VERIFICATION SUMMARY")
            print("=" * 60)
            print(f"✓ Package structure is valid")
            print(f"✓ Workflow JSON is valid")
            if package_manager:
                if package_manager.has_manifest:
                    print(f"✓ Manifest detected and processed")
                if package_manager.custom_nodes_extracted:
                    print(f"✓ Custom nodes detected")
            print("=" * 60 + "\n")
            return

        # === INSTALLATION SUMMARY ===
        print("\n[3/3] Installation complete!")
        print("\n" + "=" * 60)
        print("INSTALLATION SUMMARY")
        print("=" * 60)

        package_name = workflow_path.stem if not package_manager else package_manager.package_name
        print(f"Package: {package_name}")
        print(f"ComfyUI Path: {comfy_path}")

        if package_manager:
            if package_manager.has_manifest:
                print(f"✓ Models downloaded via manifest")
            if package_manager.custom_nodes_extracted:
                print(f"✓ Custom nodes installed")
                print(f"\n⚠️  IMPORTANT: Restart ComfyUI to load new custom nodes")
            if package_manager.extractor:
                extracted_count = len(package_manager.extractor.extracted_files)
                skipped_count = len(package_manager.extractor.skipped_files)
                print(f"✓ Files extracted: {extracted_count}")
                if skipped_count > 0:
                    print(f"  Files skipped (already up-to-date): {skipped_count}")

        print(f"✓ Workflow saved to: {workflow_path}")
        print("=" * 60 + "\n")

        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\nInstallation completed: {datetime.now()}\n")
                f.write(f"Package: {package_name}\n")

    except KeyboardInterrupt:
        print("\n\nInstallation interrupted by user.")
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"Installation interrupted: {datetime.now()}\n")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"ERROR: {e}\n")
        raise
    finally:
        # Cleanup temporary files
        if package_manager:
            print("\nCleaning up temporary files...")
            package_manager.cleanup()
            print("✓ Cleanup complete")

        if log_file:
            print(f"\nLog file: {log_file}")


if __name__ == "__main__":
    main()
