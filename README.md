# Barcode Generator - Code128 Desktop App

A simple desktop application built with Python and tkinter for generating Code128 barcodes. The app includes a text file database to track generated barcodes and prevent duplicates.

## Features

- **Code128 Barcode Generation**: Generate barcodes from any text input
- **Real-time Duplicate Detection**: Shows if a code already exists as you type
- **Database Management**: Stores all generated barcodes in a text file with timestamps
- **User-friendly Interface**: Clean and intuitive tkinter GUI
- **Barcode Image Export**: Saves barcodes as PNG files in organized folders
- **Image Viewer**: View generated barcodes directly from the application
- **Database Cleanup**: Clean database and delete all images with confirmation
- **Windows Installer**: Create professional Windows installer without antivirus warnings

## Installation

1. **Install Python** (if not already installed)
   - Download from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

       Or install manually:
    ```bash
    pip install python-barcode==0.15.1 Pillow>=8.0.0
    ```

## Usage

1. **Run the Application**
   ```bash
   python barcode_app.py
   ```

2. **Generate Barcodes**
   - Enter text in the input field
   - The app will show if the code already exists in real-time
   - Click "Generate Barcode" to create the barcode
   - Barcode images are saved as PNG files in the same directory

3. **Database Features**
   - All generated barcodes are stored in `barcode_database.txt`
   - The database shows code, timestamp, and status
   - Duplicate codes are detected and warned about

## File Structure

```
barcode_app/
├── barcode_app.py          # Main application
├── requirements.txt        # Python dependencies
├── setup.py               # cx_Freeze setup for installer
├── build_installer.py      # Automated build script
├── README.md              # This file
├── LICENSE                # MIT License
├── barcode_database.txt    # Database file (created automatically)
├── codes/                 # Barcode images folder (created automatically)
│   └── barcode_*.png      # Generated barcode images
└── dist/                  # Installer output (created by build script)
```

## Database Format

The database file (`barcode_database.txt`) stores entries in the format:
```
CODE|TIMESTAMP
```

Example:
```
ABC123|2024-01-15 14:30:25
XYZ789|2024-01-15 14:35:10
```

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- python-barcode library
- Pillow library
- cx_Freeze (for creating installer)

## Creating Windows Installer

### Method 1: Automated Build Script (Recommended)

1. **Install build dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the build script:**
   ```bash
   python build_installer.py
   ```

3. **Find your installer:**
   - If Inno Setup is installed: `dist/BarcodeGenerator_Setup.exe`
   - Otherwise: `dist/` folder contains the portable version

### Method 2: Manual Build

1. **Install cx_Freeze:**
   ```bash
   pip install cx_Freeze
   ```

2. **Build executable:**
   ```bash
   python setup.py build
   ```

3. **Create installer (optional):**
   - Install [Inno Setup](https://jrsoftware.org/isinfo.php)
   - Run: `python setup.py bdist_msi`

### Installer Features

- **No Antivirus Warnings**: Uses trusted libraries and proper signing
- **Professional Setup**: Modern installer with proper Windows integration
- **Desktop Shortcut**: Optional desktop icon creation
- **Start Menu Integration**: Proper Windows application registration
- **Uninstall Support**: Clean removal from Windows

## Troubleshooting

- **Import Error**: Make sure you've installed the requirements with `pip install -r requirements.txt`
- **Permission Error**: Ensure the application has write permissions in the directory
- **Database Issues**: The app will create the database file automatically on first run
- **Build Errors**: Make sure you have Visual Studio Build Tools installed for cx_Freeze

## License

This project is open source and available under the MIT License.
