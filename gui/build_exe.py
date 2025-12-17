"""
Build script for creating Windows .exe from Python GUI
Uses PyInstaller to create standalone executable
"""

import PyInstaller.__main__
import os
from pathlib import Path

# Build configuration
app_name = "KOSMOS-Setup"
script_path = "gui/setup_gui.py"
icon_path = "gui/kosmos.ico"  # Optional: add your icon

# Build options
build_options = [
    script_path,
    '--name', app_name,
    '--onefile',  # Single executable
    '--windowed',  # No console window
    '--clean',
    '--noconfirm',
    # Include data files
    '--add-data', 'scripts;scripts',
    '--add-data', '*.md;.',
    # Exclude unnecessary modules
    '--exclude-module', 'pytest',
    '--exclude-module', 'setuptools',
]

# Add icon if exists
if os.path.exists(icon_path):
    build_options.extend(['--icon', icon_path])

# Add version info
build_options.extend([
    '--version-file', 'gui/version_info.txt'
])

# Run PyInstaller
print("=" * 60)
print(f"Building {app_name}.exe...")
print("=" * 60)

PyInstaller.__main__.run(build_options)

print("\n" + "=" * 60)
print("Build complete!")
print(f"Executable: dist/{app_name}.exe")
print("=" * 60)
