"""
KIYA Piano Studio Pro
Professional Arranger Workstation Desktop Application
Entry Point
"""

import sys
import os

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.application import KiyaApplication

def main():
    app = KiyaApplication(sys.argv)
    exit_code = app.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
