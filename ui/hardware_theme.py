"""
KIYA Piano Studio Pro - Premium Hardware Workstation Theme
PSR-S975-inspired ultra-premium dark chassis, physical button textures,
glowing LED jewels, brushed-metal accents, and rich color LCD display styling.
"""

from PySide6.QtGui import QColor, QFont, QLinearGradient, QRadialGradient, QPen, QBrush
from PySide6.QtCore import Qt, QRectF

# --- Primary Chassis Hardware Palette ---
HW_CHASSIS_BASE      = "#0E1016"   # Ultra-deep charcoal body
HW_CHASSIS_DARK      = "#090B0F"   # Deepest shadow / base bevel
HW_PANEL_UPPER       = "#141720"   # Upper console panel
HW_PANEL_ELEVATED    = "#1E2230"   # Raised control bays
HW_PANEL_RECESS      = "#070A0F"   # Screen bay and slot insets
HW_BEZEL_BORDER      = "#252A38"   # Subtle panel seams and divider lines
HW_BEZEL_HIGHLIGHT   = "#3A4158"   # Top-edge metallic reflection
HW_SPEAKER_GRILLE    = "#0A0C11"   # Speaker grille flank texture
HW_ACCENT_SILVER     = "#9AA4B8"   # Silk-screened lettering / silver branding
HW_ACCENT_GOLD       = "#C9A84C"   # Premium gold accent stripe

# --- Physical Buttons & Knobs ---
HW_BTN_SURFACE       = "#22283A"   # Normal unpressed plastic button face
HW_BTN_HOVER         = "#2E3550"   # Subtle mouse hover face
HW_BTN_PRESSED       = "#181C28"   # Depressed button face
HW_BTN_BORDER        = "#0F1220"   # Dark button border
HW_BTN_HIGHLIGHT     = "#4A5570"   # 1px top highlight bevel
HW_BTN_SHADOW        = "#05060C"   # Bottom ambient shadow
HW_BTN_TEXT          = "#D8E4F0"   # Primary button silkscreen text
HW_BTN_TEXT_SEC      = "#7A8BAA"   # Secondary subscript text
HW_BTN_START_STOP    = "#2A3048"   # Large start/stop physical button base

# --- Active Hardware Indicator LEDs ---
LED_OFF              = "#141826"   # Unlit dark LED jewel
LED_GREEN_ON         = "#39FF8A"   # Vivid neon green (Rhythm/Main active)
LED_GREEN_GLOW       = "#004D28"   # Green diffuse halo
LED_RED_ON           = "#FF3D45"   # Brilliant cherry red (Rec/Stop/Ending)
LED_RED_GLOW         = "#7A0008"   # Red diffuse halo
LED_AMBER_ON         = "#FFB726"   # Pure warm amber (Standby/Transition/OTS)
LED_AMBER_GLOW       = "#7A4000"   # Amber diffuse halo
LED_BLUE_ON          = "#38B4FF"   # Electric cyan-blue (Dual/Layer/Freeze)
LED_BLUE_GLOW        = "#003D70"   # Blue diffuse halo
LED_CYAN_ON          = "#00E5FF"   # Bright teal cyan accent
LED_CYAN_GLOW        = "#003344"   # Cyan diffuse halo

# --- 7-Inch Color LCD Display Palette ---
LCD_BG_DARK          = "#0A1420"   # Deep navy-black background
LCD_BG_PANEL         = "#101E30"   # Inner LCD info panel background
LCD_BG_HEADER        = "#162840"   # LCD top title bar
LCD_BORDER           = "#060B14"   # Screen outer bezel border
LCD_BORDER_INNER     = "#1A3050"   # Sub-window divider border
LCD_TEXT_PRIMARY     = "#E8F0F8"   # High-contrast white/light silver text
LCD_TEXT_SECONDARY   = "#7AAFCC"   # Soft cyan/gray label text
LCD_TEXT_MUTED       = "#3A5570"   # Inactive/subdued text
LCD_ACCENT_ORANGE    = "#FF8C00"   # Chord / selected style warm amber-orange
LCD_ACCENT_GREEN     = "#39FF8A"   # Tempo / beat vivid neon green
LCD_ACCENT_BLUE      = "#38B4FF"   # Part selection electric cyan
LCD_ACCENT_GOLD      = "#FFD060"   # Highlight gold accent
LCD_SELECTED_ITEM    = "#163050"   # Selected list item highlight

# --- Piano Keybed Palette ---
KEY_WHITE_TOP        = "#FDFCF8"   # Pristine ivory white key surface top
KEY_WHITE_MID        = "#F8F6F0"   # Mid gradient warm cream
KEY_WHITE_BOTTOM     = "#EDE8DF"   # Subtle lower gradient warm bone
KEY_WHITE_PRESSED    = "#FFE066"   # Pressed white key golden glow
KEY_WHITE_SPLIT      = "#DFF0FF"   # Left split chord zone soft ice blue
KEY_WHITE_BORDER     = "#B0BAC8"   # Fine key separator border
KEY_WHITE_LIP_SHADOW = "#C4BEB0"   # 3D lower lip shadow

KEY_BLACK_TOP        = "#1E222C"   # Deep ebony top gloss
KEY_BLACK_MID        = "#141820"   # Mid dark ebony
KEY_BLACK_BASE       = "#0D0F16"   # Matte ebony base
KEY_BLACK_PRESSED    = "#FF8C00"   # Pressed black key vivid amber glow
KEY_BLACK_HIGHLIGHT  = "#353C4E"   # Subtle top-edge bevel highlight


# --- Fonts Factory ---
def get_hardware_font(size: int = 9, bold: bool = False) -> QFont:
    """Return clean technical typography for instrument silkscreen labels."""
    for family in ["Segoe UI", "Inter", "Arial"]:
        font = QFont(family, size)
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
    ACCENT_GOLD     = HW_ACCENT_GOLD

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
    LCD_GOLD        = LCD_ACCENT_GOLD

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
        return get_hardware_font(13, True)

    @staticmethod
    def display_bold() -> QFont:
        return get_lcd_font(11, True)


def draw_led_jewel(painter, cx: float, cy: float, radius: float, is_on: bool, color_type: str = "green"):
    """Render a premium circular jewel LED with intense diffuse glowing halo and glass lens reflection."""
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
    elif color_type == "cyan":
        on_col = QColor(LED_CYAN_ON)
        glow_col = QColor(LED_CYAN_GLOW)
    else:  # green
        on_col = QColor(LED_GREEN_ON)
        glow_col = QColor(LED_GREEN_GLOW)

    # 1. Outer dark recessed bezel socket with subtle depth ring
    painter.setPen(QPen(QColor("#04050A"), 1.0))
    painter.setBrush(QColor("#0C0F18"))
    painter.drawEllipse(QRectF(cx - radius - 1.5, cy - radius - 1.5, (radius + 1.5) * 2, (radius + 1.5) * 2))

    if is_on:
        # 2. Intense atmospheric halo glow (larger, more vivid)
        glow_grad = QRadialGradient(cx, cy, radius * 3.2)
        glow_grad.setColorAt(0.0, QColor(on_col.red(), on_col.green(), on_col.blue(), 180))
        glow_grad.setColorAt(0.4, QColor(on_col.red(), on_col.green(), on_col.blue(), 70))
        glow_grad.setColorAt(0.7, QColor(glow_col.red(), glow_col.green(), glow_col.blue(), 30))
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(glow_grad)
        painter.drawEllipse(QRectF(cx - radius * 3.2, cy - radius * 3.2, radius * 6.4, radius * 6.4))

        # 3. Brilliant glowing LED core with intense center
        core_grad = QRadialGradient(cx - (radius * 0.25), cy - (radius * 0.25), radius)
        core_grad.setColorAt(0.0, QColor("#FFFFFF"))
        core_grad.setColorAt(0.2, QColor(min(255, on_col.red() + 80), min(255, on_col.green() + 80), min(255, on_col.blue() + 80)))
        core_grad.setColorAt(0.6, on_col)
        core_grad.setColorAt(1.0, glow_col)
        painter.setBrush(core_grad)
        painter.setPen(QPen(on_col.darker(120), 0.5))
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

        # 4. Glass specular highlight on top-left of LED
        spec_grad = QRadialGradient(cx - radius * 0.3, cy - radius * 0.4, radius * 0.5)
        spec_grad.setColorAt(0.0, QColor(255, 255, 255, 200))
        spec_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(spec_grad)
        painter.drawEllipse(QRectF(cx - radius * 0.8, cy - radius * 0.9, radius * 0.9, radius * 0.7))
    else:
        # Unlit darkened lens with subtle depth
        dim_grad = QRadialGradient(cx - (radius * 0.3), cy - (radius * 0.3), radius)
        dim_grad.setColorAt(0.0, QColor("#20242E"))
        dim_grad.setColorAt(0.7, QColor("#0E1018"))
        dim_grad.setColorAt(1.0, QColor("#08090F"))
        painter.setPen(QPen(QColor("#060810"), 0.5))
        painter.setBrush(dim_grad)
        painter.drawEllipse(QRectF(cx - radius, cy - radius, radius * 2, radius * 2))

    painter.restore()
