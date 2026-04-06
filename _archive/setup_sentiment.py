# setup_sentiment.py
"""
Setup script for installing sentiment analysis dependencies
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install the required packages for sentiment analysis"""
    required_packages = [
        "openai>=1.0.0",
        "pandas",
        "numpy",
        "matplotlib",
        # webbrowser is part of the Python standard library, so we don't need to install it
    ]

    print("Installing sentiment analysis dependencies...")

    # Check if running in a virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("Warning: It looks like you're not running in a virtual environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return

    # Install each package
    for package in required_packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            return

    print("\nAll dependencies installed successfully!")
    print("\nTo use the sentiment analysis feature, you need an OpenAI API key.")
    print("You can either:")
    print("1. Set it in config.py (OPENAI_API_KEY variable)")
    print("2. Set it as an environment variable (OPENAI_API_KEY)")
    print("3. Enter it in the application UI when prompted")

def create_directory_structure():
    """Create the sentiment directory structure if it doesn't exist"""
    # Create the sentiment directory
    os.makedirs("sentiment", exist_ok=True)

    # Create empty __init__.py file
    init_file = os.path.join("sentiment", "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# Sentiment analysis package\n")

    print("Directory structure created.")

if __name__ == "__main__":
    create_directory_structure()
    install_dependencies()