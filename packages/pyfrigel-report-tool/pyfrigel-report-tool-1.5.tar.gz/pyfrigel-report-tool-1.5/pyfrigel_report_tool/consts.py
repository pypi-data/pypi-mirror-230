from reportlab.lib.colors import HexColor
import pathlib
from os import path

# import font Ubuntu 
#---------------------------------------------
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

UBUNTU_FONT = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'Ubuntu', 'Ubuntu-Regular.ttf')
UBUNTU_BOLD_FONT = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'Ubuntu', 'Ubuntu-Bold.ttf')
UBUNTU_ITALIC_FONT = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'Ubuntu', 'Ubuntu-Italic.ttf')

pdfmetrics.registerFont(TTFont('Ubuntu', UBUNTU_FONT))
pdfmetrics.registerFont(TTFont('Ubuntu-Bold', UBUNTU_BOLD_FONT))
pdfmetrics.registerFont(TTFont('Ubuntu-Italic', UBUNTU_ITALIC_FONT))

pdfmetrics.registerFontFamily('Ubuntu', normal='Ubuntu-Regular', bold='Ubuntu-Bold', italic='Ubuntu-Italic')
#---------------------------------------------

DEFAULT_SPACING = 8
DEFAULT_STARTING_POSITION = 24
CIRCLE_SIZE = 4

DEFAULT_FONT = 'Ubuntu'
DEFAULT_FONT_BOLD = 'Ubuntu-Bold'

DEFAULT_LOGO_PATH = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'frigel_logo.png')
DEFAULT_MACHINE_PATH = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'RSY_con_display.jpeg')
DEFAULT_SYNCRO_LOGO_PATH = path.join(pathlib.Path(__file__).parent.resolve(), 'assets', 'Syncro.png')

WORKING_MODE_TYPES = ['standard', 'production', 'maintenance']

DEFAULT_ON_COLOR = HexColor("#B9E0A1")
DEFAULT_OFF_COLOR = HexColor("#CECECE")
DEFAULT_NEGATIVE_COLOR = HexColor("#CD1414")
DEFAULT_STROKE_COLOR = HexColor("#E9E9E9")
DEFAULT_FOOTER_COLOR = HexColor("#8A8A8A")
WORKING_MODES_COLORS = (HexColor("#6BCE70"), HexColor("#BEDAA4"), HexColor("#4E70AB"), HexColor("#CECECE"))