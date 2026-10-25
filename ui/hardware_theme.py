"""
KIYA Piano Studio Pro - Hardware Workstation Theme & Visual Styling
PSR-S975-inspired dark charcoal instrument chassis, physical button textures,
LED jewels, brushed metal accents, and recessed color LCD display styling.
"""

from PySide6.QtGui import QColor, QFont, QLinearGradient, QRadialGradient, QPen, QBrush
from PySide6.QtCore import Qt, QRectF

# --- Primary Chassis Hardware Palette ---
HW_CHASSIS_BASE      = "#111214"   # Main cabinet deep charcoal
HW_CHASSIS_DARK      = "#0B0C0E"   # Deepest shadow / base bevel
HW_PANEL_UPPER       = "#181A1E"   # Upper console panel
HW_PANEL_ELEVATED    = "#22252B"   # Raised control bays
HW_PANEL_RECESS      = "#08090A"   # Screen bay and slot insets
HW_BEZEL_BORDER      = "#2B2F38"   # Subtle panel seams and divider lines
HW_BEZEL_HIGHLIGHT   = "#454A56"   # Top-edge metallic reflection
HW_SPEAKER_GRILLE    = "#0D0E10"   # Speaker grille flank texture
HW_ACCENT_SILVER     = "#8E96A4"   # Silk-screened lettering / silver branding

# --- Physical Buttons & Knobs ---
HW_BTN_SURFACE       = "#282B32"   # Normal unpressed plastic button face
HW_BTN_HOVER         = "#343842"   # Subtle mouse hover face
HW_BTN_PRESSED       = "#1C1E23"   # Depressed button face
HW_BTN_BORDER        = "#14161A"   # Dark button border
HW_BTN_HIGHLIGHT     = "#555A66"   # 1px top highlight bevel
HW_BTN_SHADOW        = "#07080A"   # Bottom ambient shadow
HW_BTN_TEXT          = "#DCE1E8"   # Primary button silkscreen text
HW_BTN_TEXT_SEC      = "#848D9C"   # Secondary subscript text
HW_BTN_START_STOP    = "#323842"   # Large start/stop physical button base

# --- Active Hardware Indicator LEDs ---
LED_OFF              = "#1C2026"   # Unlit dark LED jewel
LED_GREEN_ON         = "#65D878"   # Glowing Emerald Green (Rhythm/Main active)
LED_GREEN_GLOW       = "#1B5E20"   # Green diffuse halo
LED_RED_ON           = "#F05D52"   # Brilliant Ruby Red (Rec/Stop/Ending)
LED_RED_GLOW         = "#7F0000"   # Red diffuse halo
LED_AMBER_ON         = "#FFA726"   # Warm Amber (Standby/Transition/OTS)
LED_AMBER_GLOW       = "#E65100"   # Amber diffuse halo
LED_BLUE_ON          = "#4DA3FF"   # Cool Blue (Dual/Layer/Freeze)
LED_BLUE_GLOW        = "#0D47A1"   # Blue diffuse halo

# --- 7-Inch Color LCD Display Palette ---
LCD_BG_DARK          = "#141C24"   # Recessed LCD deep gray-blue
LCD_BG_PANEL         = "#1A2530"   # Inner LCD info panel background
LCD_BG_HEADER        = "#202E3C"   # LCD top title bar
LCD_BORDER           = "#090D12"   # Screen outer bezel border
LCD_BORDER_INNER     = "#263544"   # Sub-window divider border
LCD_TEXT_PRIMARY     = "#E8EDF1"   # High-contrast white/light silver text
LCD_TEXT_SECONDARY   = "#8FA3B4"   # Soft cyan/gray label text
LCD_TEXT_MUTED       = "#526270"   # Inactive/subdued text
LCD_ACCENT_ORANGE    = "#FF9800"   # Chord / selected style warm orange
LCD_ACCENT_GREEN     = "#65D878"   # Tempo / beat neon green
LCD_ACCENT_BLUE      = "#4DA3FF"   # Part selection cyan/blue
LCD_SELECTED_ITEM    = "#2E4760"   # Selected list item highlight

# --- Piano Keybed Palette ---
KEY_WHITE_TOP        = "#FAF9F6"   # Creamy ivory white key surface top
KEY_WHITE_BOTTOM     = "#EBE7E0"   # Subtle lower gradient
KEY_WHITE_PRESSED    = "#FFE0B2"   # Pressed white key amber glow
KEY_WHITE_SPLIT      = "#E3EEF9"   # Left split chord zone soft blue tint
KEY_WHITE_BORDER     = "#A4A8B0"   # Fine key separator border
KEY_WHITE_LIP_SHADOW = "#C8CBD2"   # 3D lower lip shadow

KEY_BLACK_TOP        = "#22252A"   # Ebony black key body top sheen
KEY_BLACK_BASE       = "#121417"   # Matte ebony black key body
KEY_BLACK_PRESSED    = "#FFA726"   # Pressed black key amber glow
KEY_BLACK_HIGHLIGHT  = "#3D424B"   # Subtle top-edge bevel highlight

# --- Fonts Factory ---
def get_hardware_font(size: int = 9, bold: bool = False) -> QFont:
    """Return clean technical typography for instrument silkscreen labels."""
    font = QFont("Segoe UI", size)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    font.setBold(bold)
    return font

def get_lcd_font(size: int = 10, bold: bool = False) -> QFont:
    """Return crisp compact typography for LCD screen information."""
    font = QFont("Consolas", size)
    font.setStyleHint(QFont.StyleHint.Monospace)
    font.setBold(bold)
    return font

class HardwareColors:
    CHASSIS_BG      = HW_CHASSIS_BASE
    CHASSIS_DARK    = HW_CHASSIS_DARK
    PANEL_DARK      = HW_PANEL_UPPER
    PANEL_ELEVATED  = HW_PANEL_ELEVATED
    PANEL_RECESS    = HW_PANEL_RECESS
    BEZEL_BORDER    = HW_BEZEL_BORDER
    BEZEL_HIGHLIGHT = HW_BEZEL_HIGHLIGHT
    SPEAKER_GRILLE  = HW_SPEAKER_GRILLE
    ACCENT_SILVER   = HW_ACCENT_SILVER

    BUTTON_DARK      = HW_BTN_SURFACE
    BUTTON_HOVER     = HW_BTN_HOVER
    BUTTON_PRESSED   = HW_BTN_PRESSED
    BUTTON_BORDER    = HW_BTN_BORDER
    BUTTON_HIGHLIGHT = HW_BTN_HIGHLIGHT
    BUTTON_SHADOW    = HW_BTN_SHADOW
    BUTTON_TEXT      = HW_BTN_TEXT
    BUTTON_TEXT_SEC  = HW_BTN_TEXT_SEC
    BUTTON_START_STOP= HW_BTN_START_STOP

    LED_OFF         = LED_OFF
    LED_GREEN       = LED_GREEN_ON
    LED_RED         = LED_RED_ON
    LED_AMBER       = LED_AMBER_ON
    LED_BLUE        = LED_BLUE_ON

    LCD_BG          = LCD_BG_DARK
    LCD_PANEL       = LCD_BG_PANEL
    LCD_HEADER      = LCD_BG_HEADER
    LCD_BORDER      = LCD_BORDER
    LCD_TEXT        = LCD_TEXT_PRIMARY
    LCD_TEXT_SEC    = LCD_TEXT_SECONDARY
    LCD_TEXT_MUTED  = LCD_TEXT_MUTED
    LCD_ORANGE      = LCD_ACCENT_ORANGE
    LCD_GREEN       = LCD_ACCENT_GREEN
    LCD_BLUE        = LCD_ACCENT_BLUE

    KEY_WHITE_TOP        = KEY_WHITE_TOP
    KEY_WHITE_BOTTOM     = KEY_WHITE_BOTTOM
    KEY_WHITE_PRESSED    = KEY_WHITE_PRESSED
    KEY_WHITE_SPLIT      = KEY_WHITE_SPLIT
    KEY_BLACK_TOP        = KEY_BLACK_TOP
    KEY_BLACK_BASE       = KEY_BLACK_BASE
    KEY_BLACK_PRESSED    = KEY_BLACK_PRESSED


class HardwareFonts:
    @staticmethod
    def micro_regular() -> QFont:
        return get_hardware_font(8, False)

    @staticmethod
    def micro_bold() -> QFont:
        return get_hardware_font(8, True)

    @staticmethod
    def label_regular() -> QFont:
        return get_hardware_font(9, False)

    @staticmethod
    def label_bold() -> QFont:
        return get_hardware_font(9, True)

    @staticmethod
    def sub_bold() -> QFont:
        return get_hardware_font(10, True)

    @staticmethod
    def title_bold() -> QFont:
        return get_hardware_font(12, True)

    @staticmethod
    def display_bold() -> QFont:
        return get_lcd_font(11, True)

def draw_led_jewel(painter, cx: float, cy: float, radius: float, is_on: bool, color_type: str = "green"):
    """Render a realistic circular jewel LED with diffuse glowing halo and lens reflection."""
    painter.save()
    painter.setRenderHint(painter.RenderHint.Antialiasing, True)

    # Pick colors based on LED type
    if color_type == "red":
        on_col = QColor(LED_RED_ON)
        glow_col = QColor(LED_RED_GLOW)
    elif color_type == "amber":
        on_col = QColor(LED_AMBER_ON)
        glow_col = QColor(LED_AMBER_GLOW)
    elif color_type == "blue":
        on_col = QColor(LED_BLUE_ON)
        glow_col = QColor(LED_BLUE_GLOW)
    else:  # green
        on_col = QColor(LED_GREEN_ON)
        glow_col = QColor(LED_GREEN_GLOW)

    # 1. Outer dark recessed bezel socket
    painter.setPen(QPen(QColor("#08090B"), 1.0))
    painter.setBrush(QColor("#0F1115"))
    painter.drawEllipse(QRectF(cx - radius - 1.2, cy - radius - 1.2, (radius + 1.2) * 2, (radius + 1.2) * 2))

    if is_on:
        # 2. Diffuse atmospheric halo glow
        glow_grad = QRadialGradient(cx, cy, radius * 2.5)
        glow_grad.setColorAt(0.0, QColor(on_col.red(), on_col.green(), on_col.blue(), 120))
        glow_grad.setColorAt(0.6, QColor(glow_col.red(), glow_col.green(), glow_col.blue(), 40))
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow_grad)
        painter.drawEllipse(QRectF(cx - radius * 2.5, cy - radius * 2.5, radius * 5, radius * 5))

        # 3. Brilliant glowing LED core
        core_grad = QRadialGradient(cx - (radius * 0.3), cy - (radius * 0.3), radius)
        core_grad.setColorAt(0.0, QColor("#FFFFFF"))
        core_grad.setColorAt(0.35, on_col)
        core_grad.setColorAt(1.0, glow_col)
        painter.setBrush(core_grad)
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))
    else:
        # Unlit darkened lens
        dim_grad = QRadialGradient(cx - (radius * 0.3), cy - (radius * 0.3), radius)
        dim_grad.setColorAt(0.0, QColor("#2A2E38"))
        dim_grad.setColorAt(1.0, QColor("#121419"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dim_grad)
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    painter.restore()
