# setup.py
import subprocess
import sys
from pathlib import Path

def run():
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    Path('logs').mkdir(exist_ok=True)
    Path('outputs').mkdir(exist_ok=True)
    print("Setup complete! Run: python GUI.py")

if __name__ == "__main__":
    run()