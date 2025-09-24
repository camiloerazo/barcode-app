import sys
import os
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "tkinter", 
        "os", 
        "datetime", 
        "barcode", 
        "subprocess", 
        "platform",
        "PIL",
        "PIL._tkinter_finder"
    ],
    "excludes": [
        "unittest",
        "test",
        "distutils",
        "setuptools",
        "email",
        "http",
        "urllib",
        "xml",
        "pydoc",
        "doctest",
        "argparse",
        "difflib",
        "inspect",
        "pdb",
        "pickle",
        "profile",
        "pstats",
        "shelve",
        "traceback",
        "warnings"
    ],
    "include_files": [
        ("README.md", "README.md"),
        ("requirements.txt", "requirements.txt")
    ],
    "optimize": 2,
    "include_msvcr": True,
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Application information
app_name = "Barcode Generator"
app_version = "1.0.0"
app_description = "A desktop application for generating Code128 barcodes with database management"
app_author = "Barcode Generator Team"
app_author_email = "support@barcodegenerator.com"

setup(
    name=app_name,
    version=app_version,
    description=app_description,
    author=app_author,
    author_email=app_author_email,
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "barcode_app.py",
            base=base,
            target_name="BarcodeGenerator.exe",
            icon=None,  # You can add an icon file here: "icon.ico"
            shortcut_name=app_name,
            shortcut_dir="DesktopFolder",
            copyright="Copyright (c) 2024 Barcode Generator Team"
        )
    ]
)
