#!/usr/bin/env python3
"""
Auto-Launcher for HTML Search Engine

This script automatically detects available GUI libraries and launches
the appropriate version (GUI or Console) of the HTML Search Engine.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def check_gui_availability():
    """Check if GUI libraries are available."""
    try:
        import tkinter
        from tkinter import ttk
        return True
    except ImportError:
        return False


def launch_gui():
    """Launch the GUI version."""
    try:
        from gui_app import GuiApp
        print("🎨 Launching GUI version...")
        app = GuiApp("Jan.zip")
        app.run()
        return True
    except Exception as e:
        print(f"GUI launch failed: {e}")
        return False


def launch_console():
    """Launch the console version."""
    try:
        from console_app import ConsoleApp
        print("🖥️  Launching console version...")
        app = ConsoleApp("Jan.zip")
        app.run()
        return True
    except Exception as e:
        print(f"Console launch failed: {e}")
        return False


def main():
    """Main entry point with automatic version detection."""
    print("HTML Search Engine - Auto Launcher")
    print("=" * 42)
    
    # Check for Jan.zip
    if not os.path.exists("Jan.zip"):
        print("⚠️  Warning: Jan.zip not found!")
        print("The application may not work properly without the data file.")
        print()
    
    # Check GUI availability
    gui_available = check_gui_availability()
    
    if gui_available:
        print("✅ GUI libraries detected")
        print("🎨 Starting GUI version (modern interface)...")
        print("   • Dynamic layout transitions")  
        print("   • Card-based results display")
        print("   • File content previews")
        print("   • Real-time statistics")
        print()
        
        success = launch_gui()
        if not success:
            print("GUI version failed, falling back to console...")
            launch_console()
    else:
        print("ℹ️  GUI libraries not available (tkinter missing)")
        print("🖥️  Starting console version (fully functional)...")
        print("   • Interactive search loop")
        print("   • All search functionality")  
        print("   • Same performance as GUI")
        print()
        
        launch_console()
    
    print("Application finished.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)