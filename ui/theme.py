"""
KIYA Piano Studio Pro - Professional UI Theme & Styling
Defines the dark graphite color scheme and modern Qt Stylesheets.
"""

from app.constants import (
    COLOR_BG,
    COLOR_PANEL_MAIN,
    COLOR_PANEL_SECONDARY,
    COLOR_PANEL_ELEVATED,
    COLOR_BORDER,
    COLOR_BORDER_LIGHT,
    COLOR_ACCENT_ORANGE,
    COLOR_ACCENT_ORANGE_HOVER,
    COLOR_ACCENT_BLUE,
    COLOR_ACCENT_BLUE_HOVER,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_TEXT_MUTED,
    COLOR_SUCCESS,
    COLOR_ERROR,
    COLOR_WARNING
)

def get_dark_stylesheet() -> str:
    """Return the complete dark graphite Qt stylesheet."""
    return f"""
    /* Global Application Styles */
    QMainWindow, QDialog, QWidget#CentralWidget {{
        background-color: {COLOR_BG};
        color: {COLOR_TEXT_PRIMARY};
        font-family: 'Segoe UI', 'SF Pro Text', -apple-system, sans-serif;
        font-size: 13px;
    }}

    QWidget {{
        background-color: transparent;
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* Panels & GroupBoxes */
    QGroupBox {{
        background-color: {COLOR_PANEL_MAIN};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
        margin-top: 24px;
        padding: 12px 10px 10px 10px;
        font-weight: bold;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        left: 14px;
        top: 6px;
        padding: 0 6px;
        color: {COLOR_ACCENT_ORANGE};
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    QFrame.panel {{
        background-color: {COLOR_PANEL_MAIN};
        border: 1px solid {COLOR_BORDER};
        border-radius: 8px;
    }}

    QFrame.panel-secondary {{
        background-color: {COLOR_PANEL_SECONDARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
    }}

    /* Buttons */
    QPushButton {{
        background-color: {COLOR_PANEL_SECONDARY};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 6px;
        padding: 6px 14px;
        font-weight: 600;
        min-height: 22px;
    }}

    QPushButton:hover {{
        background-color: {COLOR_PANEL_ELEVATED};
        border-color: {COLOR_BORDER_LIGHT};
    }}

    QPushButton:pressed {{
        background-color: {COLOR_BORDER};
    }}

    QPushButton:checked {{
        background-color: {COLOR_ACCENT_ORANGE};
        color: #101216;
        border-color: {COLOR_ACCENT_ORANGE_HOVER};
        font-weight: bold;
    }}

    QPushButton.btn-primary {{
        background-color: {COLOR_ACCENT_ORANGE};
        color: #101216;
        border: 1px solid {COLOR_ACCENT_ORANGE_HOVER};
        font-weight: bold;
    }}

    QPushButton.btn-primary:hover {{
        background-color: {COLOR_ACCENT_ORANGE_HOVER};
    }}

    QPushButton.btn-accent-blue {{
        background-color: {COLOR_ACCENT_BLUE};
        color: #101216;
        border: 1px solid {COLOR_ACCENT_BLUE_HOVER};
        font-weight: bold;
    }}

    QPushButton.btn-danger {{
        background-color: {COLOR_ERROR};
        color: #FFFFFF;
        border: 1px solid #FF8087;
        font-weight: bold;
    }}

    QPushButton:disabled {{
        background-color: #161A20;
        color: {COLOR_TEXT_MUTED};
        border-color: #202632;
    }}

    /* Navigation Tabs */
    QTabWidget::pane {{
        border: 1px solid {COLOR_BORDER};
        background-color: {COLOR_PANEL_MAIN};
        border-radius: 0 0 8px 8px;
        top: -1px;
    }}

    QTabBar::tab {{
        background-color: {COLOR_PANEL_SECONDARY};
        color: {COLOR_TEXT_SECONDARY};
        padding: 8px 16px;
        border: 1px solid {COLOR_BORDER};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        margin-right: 4px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        background-color: {COLOR_PANEL_MAIN};
        color: {COLOR_ACCENT_ORANGE};
        border-bottom: 2px solid {COLOR_ACCENT_ORANGE};
    }}

    QTabBar::tab:hover:!selected {{
        background-color: {COLOR_PANEL_ELEVATED};
        color: {COLOR_TEXT_PRIMARY};
    }}

    /* Input Controls */
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
        background-color: #13161C;
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER};
        border-radius: 5px;
        padding: 5px 8px;
        selection-background-color: {COLOR_ACCENT_ORANGE};
        selection-color: #101216;
    }}

    QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border-color: {COLOR_ACCENT_BLUE};
    }}

    QComboBox::drop-down {{
        border: none;
        width: 20px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {COLOR_PANEL_MAIN};
        border: 1px solid {COLOR_BORDER};
        color: {COLOR_TEXT_PRIMARY};
        selection-background-color: {COLOR_PANEL_ELEVATED};
        selection-color: {COLOR_ACCENT_ORANGE};
        padding: 4px;
    }}

    /* Sliders */
    QSlider::groove:horizontal {{
        height: 6px;
        background: #15181F;
        border: 1px solid {COLOR_BORDER};
        border-radius: 3px;
    }}

    QSlider::sub-page:horizontal {{
        background: {COLOR_ACCENT_ORANGE};
        border-radius: 3px;
    }}

    QSlider::handle:horizontal {{
        background: #F4F6FA;
        border: 2px solid {COLOR_ACCENT_ORANGE};
        width: 16px;
        margin-top: -6px;
        margin-bottom: -6px;
        border-radius: 8px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {COLOR_ACCENT_ORANGE};
        border-color: #FFFFFF;
    }}

    QSlider::groove:vertical {{
        width: 8px;
        background: #15181F;
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
    }}

    QSlider::sub-page:vertical {{
        background: #15181F;
        border-radius: 4px;
    }}

    QSlider::add-page:vertical {{
        background: {COLOR_ACCENT_BLUE};
        border-radius: 4px;
    }}

    QSlider::handle:vertical {{
        background: #F4F6FA;
        border: 2px solid {COLOR_ACCENT_BLUE};
        height: 18px;
        margin-left: -6px;
        margin-right: -6px;
        border-radius: 9px;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background: {COLOR_BG};
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {COLOR_BORDER};
        min-height: 20px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: {COLOR_BORDER_LIGHT};
    }}

    QScrollBar:horizontal {{
        background: {COLOR_BG};
        height: 10px;
        margin: 0;
    }}

    QScrollBar::handle:horizontal {{
        background: {COLOR_BORDER};
        min-width: 20px;
        border-radius: 5px;
    }}

    QScrollBar::add-line, QScrollBar::sub-line {{
        border: none;
        background: none;
    }}

    /* Tooltips */
    QToolTip {{
        background-color: {COLOR_PANEL_MAIN};
        color: {COLOR_TEXT_PRIMARY};
        border: 1px solid {COLOR_BORDER_LIGHT};
        padding: 5px 8px;
        border-radius: 4px;
        font-size: 11px;
    }}

    /* Labels */
    QLabel.heading {{
        font-size: 16px;
        font-weight: bold;
        color: {COLOR_TEXT_PRIMARY};
    }}

    QLabel.subheading {{
        font-size: 12px;
        color: {COLOR_TEXT_SECONDARY};
    }}

    QLabel.accent {{
        color: {COLOR_ACCENT_ORANGE};
        font-weight: bold;
    }}
    """
