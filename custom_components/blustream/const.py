"""Konstanten für die Blustream Integration."""

DOMAIN = "blustream"
DEFAULT_PORT = 23

# Status-Abfrage-Intervall in Sekunden (5 Minuten).
# Da keine Fernbedienung / kein Front-Panel-Betrieb durch den Kunden
# vorgesehen ist, reicht ein seltenes Polling als Sicherheitsnetz aus.
DEFAULT_SCAN_INTERVAL = 300

# Config-Entry Keys
CONF_MODEL = "model"
CONF_INPUT_NAMES = "input_names"
CONF_OUTPUT_NAMES = "output_names"

# Plattformen, die diese Integration bereitstellt
PLATFORMS = ["media_player", "switch", "number", "select", "button"]

# ---------------------------------------------------------------------------
# Geräteprofile
# ---------------------------------------------------------------------------
MODEL_MFP62 = "mfp62"

# Auswahlliste für den Config Flow (Wert -> Anzeigename).
# Weitere Geräte können hier später ergänzt werden.
MODELS = {
    MODEL_MFP62: "Blustream MFP62",
}

# MFP62: feste Eingänge (FR-Befehlscode -> Standard-Klarname).
# Der Befehlssatz des MFP62 ordnet die Eingänge fest zu:
#   01-03 = HDMI, 04 = DisplayPort, 05 = USB-C, 06 = VGA
MFP62_INPUTS = [
    (1, "HDMI 1"),
    (2, "HDMI 2"),
    (3, "HDMI 3"),
    (4, "DisplayPort"),
    (5, "USB-C"),
    (6, "VGA"),
]

# MFP62: 2 Ausgänge (gespiegeltes Signal, aber einzeln schaltbar).
MFP62_OUTPUTS = 2

# ---------------------------------------------------------------------------
# Auswahloptionen
# ---------------------------------------------------------------------------
# OUT RES rr  -> Scaler-Ausgangsauflösung (Code -> Label)
RESOLUTION_OPTIONS = {
    "00": "1024x768@60Hz",
    "01": "1280x800@60Hz",
    "02": "1360x768@60Hz",
    "03": "1440x900@60Hz",
    "04": "1680x1050@60Hz",
    "05": "1920x1200@60Hz",
    "06": "720p@50Hz",
    "07": "720p@60Hz",
    "08": "1080p@50Hz",
    "09": "1080p@60Hz",
    "10": "4K2K@25Hz",
    "11": "4K2K@30Hz",
    "12": "4K2K@50Hz",
    "13": "4K2K@60Hz",
    "14": "DCI 4K2K@25Hz",
    "15": "DCI 4K2K@30Hz",
    "16": "DCI 4K2K@50Hz",
    "17": "DCI 4K2K@60Hz",
    "18": "Auto",
}

# MIC MIX mm -> Mikrofon-Mix-Modus (Code -> Label)
MIC_MIX_OPTIONS = {
    "ON": "Mix (MIC + Hintergrund)",
    "BGO": "Nur Hintergrund-Audio",
    "MICO": "Nur Mikrofon",
}
