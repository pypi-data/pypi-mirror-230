from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER
from reportlab.lib.units import inch


HALF_INCH = inch * .5
A4LETTER = (913.92, 666.96)

# Define some default styles.
STYLES = getSampleStyleSheet()

NORMAL_STYLE = STYLES['Normal']

HEADING_STYLE = STYLES['Heading5']

TITLE_STYLE = STYLES['Title']
TITLE_STYLE.alignment = 1
TITLE_STYLE.fontSize = 48
TITLE_STYLE.fontName = 'Helvetica'

SUBTITLE_STYLE = ParagraphStyle(
    'Subtitle',
    parent=STYLES['Title'],
    fontSize=22,
    spaceAfter=6
)

BOLD_STYLE = ParagraphStyle(
    'NormalBold',
    parent=STYLES['Normal'],
    fontName='Helvetica-Bold',
)

CENTERED_STYLE = ParagraphStyle(
    'NormalCenter',
    parent=STYLES['Normal'],
    alightment=TA_CENTER,
)

SMALL_STYLE = ParagraphStyle(
    'Small',
    parent=STYLES['Normal'],
    fontSize=6,
)

BLUE_HIGHLIGHT_STYLE = ParagraphStyle(
    'BlueHighlight',
    parent=STYLES['Normal'],
    backColor=colors.blue,
)

YELLOW_HIGHLIGHT_STYLE = ParagraphStyle(
    'YellowHighlight',
    parent=STYLES['Normal'],
    backColor=colors.yellow,
)

GREEN_HIGHLIGHT_STYLE = ParagraphStyle(
    'GreenHighlight',
    parent=STYLES['Normal'],
    backColor=colors.green,
)

BLUE_HIGHLIGHT_STYLE.backColor = colors.PCMYKColor(
    25, 0, 0, 0
)

YELLOW_HIGHLIGHT_STYLE.backColor = colors.PCMYKColor(
    0, 0, 33, 0
)

GREEN_HIGHLIGHT_STYLE.backColor = colors.PCMYKColor(
    25, 0, 25, 0
)

STYLES.add(SUBTITLE_STYLE)
STYLES.add(BOLD_STYLE)
STYLES.add(CENTERED_STYLE)
STYLES.add(SMALL_STYLE)
STYLES.add(BLUE_HIGHLIGHT_STYLE)
STYLES.add(YELLOW_HIGHLIGHT_STYLE)
STYLES.add(GREEN_HIGHLIGHT_STYLE)

ALL_CUSTOM_STYLES = [
    NORMAL_STYLE,
    HEADING_STYLE,
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BOLD_STYLE,
    CENTERED_STYLE,
    SMALL_STYLE,
    BLUE_HIGHLIGHT_STYLE,
    YELLOW_HIGHLIGHT_STYLE,
    GREEN_HIGHLIGHT_STYLE
]