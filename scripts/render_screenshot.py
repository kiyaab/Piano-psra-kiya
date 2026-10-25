"""
Render offscreen screenshot of KIYA Piano Studio Pro PSR-S975 interface.
"""
import os
import sys

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_QPA_FONTDIR'] = 'C:/Windows/Fonts'

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSize
from app.application import KiyaApplication

def capture():
    app = KiyaApplication([])
    w = app.window
    
    # 1. 1600x900 capture
    w.resize(1600, 900)
    w.show()
    QApplication.processEvents()
    
    # Save 1600x900
    pix1600 = w.grab()
    out1600 = "artifacts/psr_s975_hardware_1600x900.png"
    pix1600.save(out1600)
    print(f"Saved {out1600} ({pix1600.width()}x{pix1600.height()})")

    # 2. 1280x720 capture
    w.resize(1280, 720)
    QApplication.processEvents()
    pix1280 = w.grab()
    out1280 = "artifacts/psr_s975_hardware_1200x720.png"
    pix1280.save(out1280)
    print(f"Saved {out1280} ({pix1280.width()}x{pix1280.height()})")

    app.quit()

if __name__ == "__main__":
    capture()
