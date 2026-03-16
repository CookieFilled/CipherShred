<h1 align="center">CipherShred</h1>

<p align="center">
  <strong>Security-Grade Data Annihilation Engine</strong>
</p>

---

## Overview

CipherShred is a standalone, lightweight desktop application designed to permanently destroy sensitive files and directories. Standard operating system deletion merely removes file pointers, leaving raw data intact and easily recoverable. CipherShred bypasses this by actively overwriting physical disk sectors using cryptographic and military-standard algorithms, followed by aggressive metadata scrubbing to destroy Master File Table (MFT) traces.

Built with Python and CustomTkinter, it features a threaded, non-blocking modern UI with real-time progress tracking.

## Features

* **Multi-Tiered Algorithms:** Choose from Quick (1-Pass), DoD 5220.22-M (3-Pass), Gutmann Extreme (7-Pass), or Gutmann Paranoid (35-Pass).
* **Metadata Scrubbing:** Renames files dynamically multiple times before final deletion to overwrite journaling and directory entries.
* **Asynchronous Engine:** Heavy I/O operations are offloaded to background threads, ensuring the UI remains responsive even when wiping massive directories.
* **Modern Glass UI:** Clean, responsive interface featuring 7 dynamic color palettes (including CommsLink Dark and Terminal Matrix) with frosted transparency effects.

## IMPORTANT SECURITY DISCLAIMER

**WARNING: DATA ANNIHILATED BY THIS TOOL CANNOT BE RECOVERED.**

Do not use this tool on system files or directories you do not explicitly intend to destroy. 

*Hardware Note for SSDs:* Modern Solid State Drives (SSDs) utilize wear-leveling controllers and over-provisioning. While this tool aggressively overwrites allocated space, fragments of data may temporarily persist in hardware-managed unallocated blocks out of the operating system's reach. For absolute nation-state level security on modern SSDs, this tool should be used in conjunction with Full Disk Encryption (FDE) like BitLocker or LUKS.

## Installation

### Option 1: Run from Source

1. Clone the repository:
   ```bash
   git clone [https://github.com/CookieFilled/CipherShred.git](https://github.com/CookieFilled/CipherShred.git)
   cd CipherShred
   ```
2. Install the required dependencies:
   ```bash
   pip install customtkinter
   ```
3. Execute the engine:
   ```bash
   python shredder.py
   ```

### Option 2: Build Executable

To compile CipherShred into a standalone Windows `.exe` file without requiring a Python installation:

1. Ensure PyInstaller is installed:
   ```bash
   pip install pyinstaller
   ```
2. Run the build command from the project root:
   ```bash
   python -m pyinstaller --noconfirm --onefile --windowed --icon=app_icon.ico --collect-all customtkinter shredder.py
   ```
3. Locate the compiled `shredder.exe` in the generated `dist` folder.

## Usage Guide

1. Launch `shredder.exe`.
2. Select your desired UI Theme and Wipe Method from the top navigation bar.
3. Click **Select File** or **Select Folder**.
4. Acknowledge the critical warning prompt.
5. Wait for the progress bar and status indicator to confirm successful data annihilation.

## Tech Stack

* **Language:** Python 3.x
* **GUI Framework:** CustomTkinter (CTk)
* **Concurrency:** Native Python `threading` and `queue` libraries
* **Compilation:** PyInstaller

