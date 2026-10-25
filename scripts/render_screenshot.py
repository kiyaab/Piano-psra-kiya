"""
Render offscreen screenshots of KIYA Piano Studio Pro PSR-S975 interface.
Captures both the Main Performance Page and the USB File Explorer / Upload Page.
"""
import os
import sys

# Ensure workspace root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_QPA_FONTDIR'] = 'C:/Windows/Fonts'

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from app.application import KiyaApplication

def capture():
    app = KiyaApplication([])
    w = app.window

    # 1. 1600x900 Main Performance Page
    w.resize(1600, 900)
    w.show()
    QApplication.processEvents()
    pix1600 = QPixmap(1600, 900)
    w.render(pix1600)
    out1600 = "artifacts/psr_s975_hardware_1600x900.png"
    pix1600.save(out1600)
    print(f"Saved {out1600} ({pix1600.width()}x{pix1600.height()})", flush=True)

    # 2. Switch to USB/File Explorer Page (Page 6) to demonstrate file upload/import UI
    if hasattr(w, "shell") and hasattr(w.shell, "control_panel"):
        lcd = w.shell.control_panel.lcd_screen
        lcd.switch_to_page(6)
        QApplication.processEvents()
        pix_file = QPixmap(1600, 900)
        w.render(pix_file)
        out_file = "artifacts/psr_s975_hardware_file_manager.png"
        pix_file.save(out_file)
        print(f"Saved {out_file} ({pix_file.width()}x{pix_file.height()})", flush=True)

        # Switch back to main page
        lcd.switch_to_page(0)
        QApplication.processEvents()

    # 3. 1280x720 capture
    w.resize(1280, 720)
    QApplication.processEvents()
    pix1280 = QPixmap(1280, 720)
    w.render(pix1280)
    out1280 = "artifacts/psr_s975_hardware_1200x720.png"
    pix1280.save(out1280)
    print(f"Saved {out1280} ({pix1280.width()}x{pix1280.height()})", flush=True)

    os._exit(0)

if __name__ == "__main__":
    import traceback
    try:
        capture()
    except Exception as e:
        traceback.print_exc()
        os._exit(1)
