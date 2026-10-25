"""
Render offscreen screenshot of the newly redesigned ArrangerPage.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['QT_QPA_FONTDIR'] = 'C:/Windows/Fonts'

from PySide6.QtWidgets import QApplication
from ui.pages.arranger_page import ArrangerPage
from arranger.style_loader import StyleLoader

def render():
    app = QApplication.instance() or QApplication([])
    
    styles_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "resources", "styles"))
    styles = StyleLoader.load_all_styles(styles_dir)
    
    page = ArrangerPage(styles)
    page.resize(1200, 750)
    page.show()
    QApplication.processEvents()

    pix = page.grab()
    out = "artifacts/arranger_page_redesign.png"
    pix.save(out)
    print(f"Saved {out} ({pix.width()}x{pix.height()})")

    app.quit()

if __name__ == "__main__":
    render()
