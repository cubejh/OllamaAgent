import subprocess
import sys
import os

def install_requirements():
    if os.path.exists("requirements.txt"):
        print("Found requirements.txt. Installing packages...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("Packages installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error during installation: {e}")
    else:
        print("requirements.txt not found. Please make sure the file is in the same directory.")

install_requirements()
