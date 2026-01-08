import argparse
import json
import os
import sys
import zipfile
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.manifest_handler import ManifestHandler
from core.package_manager import PackageManager


def extract_manifest_from_zip(zip_path: Path, temp_dir: Path) -> Path:
    """
    Extract manifest.json from ZIP package.
    Returns path to extracted manifest.json.
    """
    print(f"[1/3] Extracting manifest from package...")

    # Create temporary extraction directory
    temp_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        # Look for manifest.json at root or in common locations
        manifest_locations = ['manifest.json', 'manifest.yaml', 'manifest.yml']
        manifest_file = None

        for loc in manifest_locations:
            if loc in zf.namelist():
                manifest_file = loc
                break

        if not manifest_file:
            raise FileNotFoundError("No manifest.json/yaml found in ZIP package")

        # Extract manifest
        zf.extract(manifest_file, temp_dir)
        manifest_path = temp_dir / manifest_file

        print(f"✓ Manifest extracted to: {manifest_path}")
        return manifest_path


def main():
    """Main installer entry point."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(
        description="ComfyUI Modular Installer - Install models, custom nodes, and assets from manifest files."
    )
    parser.add_argument("-c", "--comfy_path", type=str, required=True,
                        help="Path to ComfyUI installation folder")
    parser.add_argument("-m", "--manifest", type=str,
                        help="Path to manifest.json/yaml file or ZIP package containing manifest")
    parser.add_argument("-l", "--log", nargs='?', const=True, default=False,
                        help="Enable logging to file")
    parser.add_argument("-t", "--temp_path", type=str,
                        help="Alternate temporary directory for extraction")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force re-download/installation of all items")
    parser.add_argument("--required-only", action="store_true",
                        help="Only install items marked as required")
    parser.add_argument("--no-verify", action="store_true",
                        help="Skip checksum verification for downloads")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview actions without executing downloads")
    parser.add_argument("--sequential", action="store_true",
                        help="Disable parallel downloads (use sequential mode)")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of parallel download workers (default: 4)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Disable resume capability for interrupted downloads")
    parser.add_argument("--list-contents", action="store_true",
                        help="List manifest contents without installing")
    parser.add_argument("--cleanup", action="store_true",
                        help="Clean up partial download files and exit")

    args = parser.parse_args()

    if not args.manifest and not args.cleanup:
        parser.error("--manifest (-m) is required unless using --cleanup")

    comfy_path = Path(args.comfy_path).resolve()

    # Validate ComfyUI path
    if not comfy_path.exists():
        print(f"❌ ERROR: ComfyUI path does not exist: {comfy_path}")
        return 1

    # === CLEANUP MODE ===
    if args.cleanup:
        print("Cleaning up partial downloads...")
        handler = ManifestHandler(
            manifest_path=comfy_path / "manifest.json",  # Dummy path
            comfy_path=comfy_path,
            resume_downloads=True
        )
        handler.cleanup_partial_downloads()
        return 0

    # === LOG FILE ===
    log_file = None
    if args.log is not False:
        manifest_basename = Path(args.manifest).stem
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        log_file = Path(args.log).resolve() if args.log is not True else Path(f"{manifest_basename}_install_{timestamp}.txt").resolve()
        if log_file.is_dir():
            log_file = log_file / f"{manifest_basename}_install_{timestamp}.txt"
        print(f"Logging to: {log_file}")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"Installation started: {datetime.now()}\n")

    manifest_path = Path(args.manifest).resolve()
    temp_dir = None
    package_manager = None

    try:
        print("\n" + "=" * 60)
        print("ComfyUI Modular Installer")
        print("=" * 60)
        print(f"ComfyUI Path: {comfy_path}")
        print(f"Manifest: {manifest_path}")
        print("=" * 60 + "\n")

        # === HANDLE MANIFEST SOURCE ===
        if manifest_path.suffix.lower() == '.zip':
            # Extract manifest from ZIP package
            temp_dir = Path(args.temp_path) / f"manifest_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}" if args.temp_path else comfy_path / f"temp_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            manifest_path = extract_manifest_from_zip(manifest_path, temp_dir)

            # Also use PackageManager to extract bundled files if present
            print("\n[2/3] Extracting bundled files from package...")
            package_manager = PackageManager(
                zip_path=Path(args.manifest).resolve(),
                comfy_path=comfy_path,
                temp_path=args.temp_path,
                extract_minimal=False,
                force_extract=args.force,
                log_file=log_file
            )
            # PackageManager will handle extraction of bundled files
            try:
                package_manager.extract_zip()
                print("✓ Bundled files extracted")
            except Exception as e:
                print(f"⚠ No bundled files in package or extraction failed: {e}")

        elif manifest_path.suffix.lower() in ['.json', '.yaml', '.yml']:
            print(f"Using manifest: {manifest_path}")
        else:
            raise ValueError("Manifest must be .json, .yaml, .yml, or .zip file")

        # === INITIALIZE MANIFEST HANDLER ===
        print("\n[2/3] Loading manifest...")
        handler = ManifestHandler(
            manifest_path=manifest_path,
            comfy_path=comfy_path,
            log_file=log_file,
            max_workers=args.workers,
            resume_downloads=not args.no_resume
        )

        # Load and validate manifest
        handler.load_manifest()
        handler.validate_manifest()

        # Print summary
        handler.print_summary()

        # === LIST CONTENTS MODE ===
        if args.list_contents:
            print("\n" + "=" * 60)
            print("MANIFEST ITEMS")
            print("=" * 60)
            for item in handler.manifest['items']:
                print(f"\n{item['name']}")
                print(f"  Type: {item['type']}")
                print(f"  Source: {item['source']}")
                if 'path' in item:
                    print(f"  Destination: {item['path']}")
                if item.get('required'):
                    print(f"  Required: Yes")
                if item.get('size_mb'):
                    print(f"  Size: {item['size_mb']:.1f} MB")
            print("=" * 60 + "\n")
            return 0

        # === DOWNLOAD/INSTALL ITEMS ===
        print("\n[3/3] Installing items...")
        handler.download_items(
            skip_existing=not args.force,
            required_only=args.required_only,
            verify_checksums=not args.no_verify,
            dry_run=args.dry_run,
            parallel=not args.sequential
        )

        if args.dry_run:
            print("\n✓ Dry run completed (no changes made)")
            return 0

        # === INSTALLATION SUMMARY ===
        print("\n" + "=" * 60)
        print("INSTALLATION COMPLETE")
        print("=" * 60)

        package_info = handler.manifest.get('package', {})
        package_name = package_info.get('name', 'unknown')

        print(f"Package: {package_name}")
        if package_info.get('version'):
            print(f"Version: {package_info['version']}")
        print(f"ComfyUI Path: {comfy_path}")

        # Print what was downloaded/installed
        if handler.downloaded_items:
            print(f"\n✓ Items installed: {len(handler.downloaded_items)}")
            for item in handler.downloaded_items[:5]:  # Show first 5
                print(f"  - {item['name']}")
            if len(handler.downloaded_items) > 5:
                print(f"  ... and {len(handler.downloaded_items) - 5} more")

        if handler.skipped_items:
            print(f"\n⊘ Items skipped (already up-to-date): {len(handler.skipped_items)}")

        # Check if restart is needed
        if handler.custom_nodes_were_downloaded():
            print(f"\n⚠️  IMPORTANT: Restart ComfyUI to load new custom nodes")

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
        return 1
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        if log_file:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Cleanup temporary files
        if temp_dir and temp_dir.exists():
            print("\nCleaning up temporary files...")
            import shutil
            try:
                shutil.rmtree(temp_dir)
                print("✓ Cleanup complete")
            except Exception as e:
                print(f"⚠ Cleanup warning: {e}")

        if log_file:
            print(f"\nLog file: {log_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
