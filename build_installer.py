#!/usr/bin/env python3
"""
Build script for Barcode Generator Windows Installer
This script automates the process of creating a Windows installer.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['cx_Freeze', 'python-barcode', 'Pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ['build', 'dist']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"🧹 Cleaning {dir_name} directory...")
            shutil.rmtree(dir_name)

def build_executable():
    """Build the executable using cx_Freeze"""
    print("🔨 Building executable...")
    
    try:
        result = subprocess.run([
            sys.executable, 'setup.py', 'build'
        ], capture_output=True, text=True, check=True)
        
        print("✅ Executable built successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def create_installer():
    """Create installer using Inno Setup (if available)"""
    print("📦 Creating installer...")
    
    # Check if Inno Setup is available
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    
    if not os.path.exists(inno_compiler):
        print("⚠️  Inno Setup not found. Creating basic installer...")
        return create_basic_installer()
    
    # Create Inno Setup script
    create_inno_script()
    
    try:
        result = subprocess.run([
            inno_compiler, "installer_script.iss"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Installer created successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installer creation failed: {e}")
        return False

def create_inno_script():
    """Create Inno Setup script"""
    script_content = '''[Setup]
AppName=Barcode Generator
AppVersion=1.0.0
AppPublisher=Barcode Generator Team
AppPublisherURL=https://github.com/barcodegenerator
AppSupportURL=https://github.com/barcodegenerator/support
AppUpdatesURL=https://github.com/barcodegenerator/updates
DefaultDirName={autopf}\\Barcode Generator
DefaultGroupName=Barcode Generator
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=dist
OutputBaseFilename=BarcodeGenerator_Setup
SetupIconFile=icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "build\\exe.win-amd64-3.*\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\Barcode Generator"; Filename: "{app}\\BarcodeGenerator.exe"
Name: "{autodesktop}\\Barcode Generator"; Filename: "{app}\\BarcodeGenerator.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\\BarcodeGenerator.exe"; Description: "{cm:LaunchProgram,Barcode Generator}"; Flags: nowait postinstall skipifsilent
'''
    
    with open('installer_script.iss', 'w') as f:
        f.write(script_content)

def create_basic_installer():
    """Create a basic installer by copying files"""
    print("📁 Creating basic installer package...")
    
    # Create dist directory
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy build files
    build_dir = Path("build")
    if build_dir.exists():
        for item in build_dir.iterdir():
            if item.is_dir():
                shutil.copytree(item, dist_dir / item.name, dirs_exist_ok=True)
    
    print("✅ Basic installer package created in dist/ directory")
    return True

def main():
    """Main build process"""
    print("🚀 Starting Barcode Generator installer build process...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Clean previous builds
    clean_build_dirs()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create installer
    if not create_installer():
        return False
    
    print("=" * 50)
    print("🎉 Build process completed successfully!")
    print("📦 Installer files are in the dist/ directory")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
