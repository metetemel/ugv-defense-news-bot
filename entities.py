import re

# -----------------------
# COMPANY DATABASE
# -----------------------
COMPANIES = {
    "aselsan": "Türkiye",
    "roketsan": "Türkiye",
    "havelsan": "Türkiye",
    "fnss": "Türkiye",
    "otokar": "Türkiye",
    "rheinmetall": "Almanya",
    "knds": "Fransa/Almanya",
    "general dynamics": "ABD",
    "bae systems": "UK",
    "qinetiq": "UK",
    "northrop grumman": "ABD",
    "lockheed martin": "ABD",
    "saab": "İsveç"
}

# -----------------------
# COUNTRY HINTS
# -----------------------
COUNTRY_HINTS = {
    "turkey": "Türkiye",
    "usa": "ABD",
    "united states": "ABD",
    "germany": "Almanya",
    "france": "Fransa",
    "uk": "UK",
    "britain": "UK",
    "israel": "İsrail",
    "china": "Çin",
    "russia": "Rusya"
}

# -----------------------
# SYSTEM TYPE CLASSIFIER
# -----------------------
def classify_system(text):
    t = text.lower()

    if "ugv" in t or "ground vehicle" in t:
        return "UGV"

    if "eo/ir" in t or "infrared" in t or "thermal" in t:
        return "EO/IR"

    if "sensor" in t or "camera" in t:
        return "SENSOR"

    if "autonomous" in t:
        return "AUTONOMOUS"

    return "UNKNOWN"


# -----------------------
# COMPANY EXTRACTION
# -----------------------
def extract_company(text):
    t = text.lower()

    for c in COMPANIES:
        if c in t:
            return c.upper(), COMPANIES[c]

    return None, None


# -----------------------
# COUNTRY EXTRACTION
# -----------------------
def extract_country(text):
    t = text.lower()

    for k in COUNTRY_HINTS:
        if k in t:
            return COUNTRY_HINTS[k]

    return "UNKNOWN"
