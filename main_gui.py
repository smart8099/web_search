#!/usr/bin/env python3
"""
GUI Entry Point for HTML Search Engine

This is the main entry point for running the graphical user interface
version of the HTML search engine application.

Usage:
    python3 main_gui.py
    or
    ./main_gui.py
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def check_gui_availability():
    """Check if GUI libraries are available before importing."""
    try:
        import tkinter
        from tkinter import ttk
        return True, None
    except ImportError as e:
        return False, str(e)

# Check GUI availability first
gui_available, gui_error = check_gui_availability()

if not gui_available:
    print("HTML Search Engine - GUI Version")
    print("=" * 40)
    print(f"✗ GUI libraries not available: {gui_error}")
    print()
    print("The GUI version requires tkinter, which is not installed.")
    print("Solutions:")
    print()
    print("1. 🖥️  Use the console version instead:")
    print("   python3 main.py")
    print()
    print("2. 📦 Install tkinter for your system:")
    print("   • macOS: brew install python@3.13")
    print("   • Ubuntu: sudo apt-get install python3-tk") 
    print("   • Windows: Reinstall Python with GUI support")
    print()
    print("3. 📖 See GUI_INSTALL.md for detailed instructions")
    print()
    print("The console version provides all the same functionality!")
    sys.exit(1)

try:
    from gui_app import GuiApp
except ImportError as e:
    print(f"Error importing GUI modules: {e}")
    print("Make sure all required files are present:")
    print("- gui_app.py")
    print("- gui_components.py") 
    print("- gui_styles.py")
    print("- html_indexer.py")
    sys.exit(1)


def check_prerequisites():
    """Check if all required files and dependencies are available."""
    # Check for Jan.zip
    if not os.path.exists("Jan.zip"):
        print("Warning: Jan.zip file not found in current directory.")
        print("The application will show an error when trying to initialize.")
        print("Make sure Jan.zip is in the same directory as this script.")
        return False
        
    # Check for required Python modules
    try:
        import tkinter
        from tkinter import ttk
        print("✓ tkinter GUI library found")
    except ImportError as e:
        print(f"✗ Error: tkinter GUI library not found: {e}")
        print("\nGUI libraries are not available. Solutions:")
        print("1. Use console version: python3 main.py")  
        print("2. Install tkinter (see GUI_INSTALL.md for instructions)")
        print("3. On macOS with pyenv, you may need to reinstall Python with tkinter support")
        print("\nFor quick setup:")
        print("- macOS: brew install python@3.13  # then use /opt/homebrew/bin/python3")
        print("- Ubuntu: sudo apt-get install python3-tk")
        print("- Windows: Reinstall Python with 'tcl/tk and IDLE' option")
        return False
    
    try:
        import threading
        import zipfile
        from bs4 import BeautifulSoup
        print("✓ All other dependencies found")
    except ImportError as e:
        print(f"✗ Error: Required Python module not found: {e}")
        print("Please install missing dependencies:")
        print("pip install beautifulsoup4 lxml")
        return False
        
    return True


def main():
    """Main entry point for the GUI application."""
    print("HTML Search Engine - GUI Version")
    print("=" * 40)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPrerequisite check failed. Please resolve the issues above.")
        input("Press Enter to continue anyway, or Ctrl+C to exit...")
    
    try:
        # Create and run the GUI application
        print("Starting GUI application...")
        app = GuiApp("Jan.zip")
        
        # Handle cleanup on exit
        def on_closing():
            print("Closing application...")
            app.quit()
            
        app.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Run the application
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please check the error details above and try again.")
        return 1
    
    print("Application closed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())