#!/usr/bin/env python3
"""
Launcher script for Irish Steel Billing System
This script starts the Streamlit application and opens it in the default browser.
"""

import subprocess
import sys
import os
import time
import webbrowser
import threading
from pathlib import Path

def start_streamlit():
    """Start the Streamlit application"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Start Streamlit with specific configuration
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.headless", "true",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.serverAddress", "localhost"
    ]
    
    print("Starting Irish Steel Billing System...")
    print("Please wait while the application loads...")
    
    # Start Streamlit process
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment for the server to start
    time.sleep(3)
    
    # Open browser
    url = "http://localhost:8501"
    print(f"Opening application in browser: {url}")
    webbrowser.open(url)
    
    print("\n" + "="*50)
    print("Irish Steel Billing System is now running!")
    print("If the browser didn't open automatically, go to:")
    print(f"  {url}")
    print("\nTo stop the application, close this window or press Ctrl+C")
    print("="*50 + "\n")
    
    # Wait for the process to complete
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down Irish Steel Billing System...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    try:
        start_streamlit()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)