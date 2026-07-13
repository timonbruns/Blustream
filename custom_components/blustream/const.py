"""Konstanten für die Blustream Integration."""

DOMAIN = "blustream"
DEFAULT_PORT = 23

# Status-Abfrage-Intervall in Sekunden (5 Minuten).
DEFAULT_SCAN_INTERVAL = 300

# Config-Entry Keys
CONF_MODEL = "model"
CONF_INPUT_NAMES = "input_names"
CONF_OUTPUT_NAMES = "output_names"

# Plattformen, die diese Integration bereitstellt
PLATFORMS = ["media_player", "switch", "number", "select", "button", "sensor"]

# ---------------------------------------------------------------------------
# Geräteprofile
# ---------------------------------------------------------------------------
MODEL_MFP62 = "mfp62"
MODEL_DA11ABL = "da11abl_v2"

# Auswahlliste für den Config Flow (Wert -> Anzeigename).
MODELS = {
    MODEL_MFP62: "Blustream MFP62",
    MODEL_DA11ABL: "Blustream DA11ABL-V2 (Bluetooth-Empfänger)",
}

# ---------------------------------------------------------------------------
# MFP62 Profil
# ---------------------------------------------------------------------------
# Feste Eingänge (FR-Befehlscode -> Standard-Klarname):
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

# ---------------------------------------------------------------------------
# DA11ABL-V2 Profil (Bluetooth-/Analog-Audio-Empfänger)
# ---------------------------------------------------------------------------
# Eingangsquellen: IN SOURCE 1 = Analog, IN SOURCE 2 = Bluetooth
DA11_SOURCES = {
    1: "Analog",
    2: "Bluetooth",
}

# BT PAIR MODE 0/1/2
DA11_PAIR_MODE_OPTIONS = {
    "0": "Pairing aus",
    "1": "Pairing an",
    "2": "Pairing manuell",
}

# PRIORITY 1/2 -> welcher Eingang hat Vorrang
DA11_PRIORITY_OPTIONS = {
    "1": "Analog bevorzugt",
    "2": "Bluetooth bevorzugt",
}

# BT PRIORITY 0/1 -> welches BT-Gerät hat Vorrang
DA11_BT_PRIORITY_OPTIONS = {
    "0": "Zuerst verbundenes Gerät",
    "1": "Zuletzt verbundenes Gerät",
}

# Pegelbereiche (Gerätewerte 0-15; 0 = höchster Pegel)
DA11_GAIN_MIN = 0
DA11_GAIN_MAX = 15
DA11_SENS_MIN = 0
DA11_SENS_MAX = 15

# BT TIMEOUT Bereich in Sekunden
DA11_TIMEOUT_MIN = 1
DA11_TIMEOUT_MAX = 999

# AUTO SW Bereich in Sekunden
DA11_AUTOSW_MIN = 0
DA11_AUTOSW_MAX = 999

# Pegel-Tabellen aus der Geräte-Hilfe (Firmware V1.4.0)
# OUT GAIN xx: 0 = +20dBu ... 15 = -28dBV
DA11_GAIN_OPTIONS = {
    "0": "+20 dBu",
    "1": "+18 dBu",
    "2": "+15 dBu",
    "3": "+12 dBu",
    "4": "+9 dBu",
    "5": "+6 dBu",
    "6": "+4 dBu",
    "7": "0 dBu",
    "8": "0 dBV",
    "9": "-3 dBV",
    "10": "-6 dBV",
    "11": "-10 dBV",
    "12": "-14 dBV",
    "13": "-20 dBV",
    "14": "-24 dBV",
    "15": "-28 dBV",
}

# ANA IN SENS xx: 0 = +24dBu ... 15 = -28dBV
DA11_SENS_OPTIONS = {
    "0": "+24 dBu",
    "1": "+21 dBu",
    "2": "+18 dBu",
    "3": "+15 dBu",
    "4": "+12 dBu",
    "5": "+9 dBu",
    "6": "+6 dBu",
    "7": "+4 dBu",
    "8": "0 dBu",
    "9": "0 dBV",
    "10": "-3 dBV",
    "11": "-6 dBV",
    "12": "-10 dBV",
    "13": "-14 dBV",
    "14": "-20 dBV",
    "15": "-28 dBV",
}
