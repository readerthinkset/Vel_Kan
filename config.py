"""VELOCITY KANNADA - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY KANNADA"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "KANNADA"
HANDLE = "@velocitykannada"
MASCOT_NAME = "Velo"

# ==== LANGUAGE PACK START ====
LANGUAGE = {
    "code": "kn",
    "name": "Kannada",
    "native_name": "ಕನ್ನಡ",
    "history_key": "kannada",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "kn-IN-SapnaNeural",
    "native_fallback_voice": "kn-IN-GaganNeural",
    "native_engine": "edge",
    "native_lang_code": "kn",
    "english_rate": "-2%",
    "native_rate": "-6%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "ಕನ್ನಡ",
    "translit_label": "SAY IT LIKE",
    "greeting": "ನಮಸ್ಕಾರ!",
    "encouragement": "ಅದ್ಭುತ!",
    "rtl": False,
    "char_tiles": False,
    "script_font": "NotoSansKannada-Bold.ttf",
}
# ==== LANGUAGE PACK END ====

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4
MAX_REEL_DURATION = 88.0

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, native, icon, accent)

# ==== CATEGORY TABLE START ====
CATEGORY_TABLE = [
    ("Greetings", "ಶುಭೋದಯ", "hand", "#1CB0F6"),
    ("Basic Phrases", "ಮೂಲಭೂತ ವಾಕ್ಯಗಳು", "chat", "#58CC02"),
    ("Common Expressions", "ಸಾಮಾನ್ಯ ಅಭಿವ್ಯಕ್ತಿಗಳು", "chat", "#1CB0F6"),
    ("Travel", "ಪ್ರಯಾಣ", "plane", "#1CB0F6"),
    ("Restaurant", "ರೆಸ್ಟೋರೆಂಟ್", "fork", "#FF7A00"),
    ("Shopping", "ಖರೀದಿ", "bag", "#E056A0"),
    ("Emergency", "ತುರ್ತು", "siren", "#FF4B4B"),
    ("Family Terms", "ಕುಟುಂಬದ ಪದಗಳು", "heart", "#E056A0"),
    ("Numbers", "ಸಂಖ್ಯೆಗಳು", "hash", "#A560E8"),
    ("Time", "ಸಮಯ", "clock", "#00A889"),
    ("Motivation", "ಪ್ರೇರಣೆ", "rocket", "#A560E8"),
    ("Love", "ಪ್ರೀತಿ", "heart", "#FF4B4B"),
    ("Success", "ಯಶಸ್ಸು", "trophy", "#F5A700"),
    ("Wisdom", "ಜ್ಞಾನ", "book", "#A560E8"),
    ("Happiness", "ಸಂತೋಷ", "smile", "#F5A700"),
    ("Self Improvement", "ಸ್ವಯಂ ಸುಧಾರಣೆ", "leaf", "#58CC02"),
    ("Gratitude", "ಕೃತಜ್ಞತೆ", "heart", "#FF7A00"),
    ("Friendship", "ಸ್ನೇಹ", "users", "#00A889"),
    ("Hope", "ಭಾವಿ", "sun", "#FF7A00"),
    ("Creativity", "ಸೃಜನಶೀಲತೆ", "palette", "#E056A0"),
    ("Inner Peace", "ಆಂತರಿಕ ಶಾಂತಿ", "lotus", "#00A889"),
    ("Confidence", "ಆತ್ಮವಿಶ್ವಾಸ", "shield", "#1CB0F6"),
    ("Perseverance", "ಹಠಧಾರಣೆ", "mountain", "#FF7A00"),
    ("Inspiration", "ಸ್ಫೂರ್ತಿ", "sparkles", "#A560E8"),
    ("Positive Life", "ಸಕಾರಾತ್ಮಕ ಜೀವನ", "sun", "#58CC02"),
    ("Courage", "ಧೈರ್ಯ", "shield", "#FF4B4B"),
    ("Kindness", "ದಯೆ", "heart", "#E056A0"),
    ("Patience", "ತಾಳ್ಮೆ", "hourglass", "#00A889"),
    ("Forgiveness", "ಕ್ಷಮಾಪಣೆ", "hands", "#FF7A00"),
    ("Strength", "ಬಲ", "dumbbell", "#FF4B4B"),
    ("Joy", "ಆನಂದ", "smile", "#F5A700"),
    ("Balance", "ಸಮತೋಲನ", "scale", "#00A889"),
    ("Growth", "ಬೆಳವಣಿಗೆ", "sprout", "#58CC02"),
    ("Purpose", "ಉದ್ದೇಶ", "target", "#A560E8"),
    ("Mindfulness", "ಜಾಗೃತಿ", "lotus", "#00A889"),
]
# ==== CATEGORY TABLE END ====

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

# ==== HASHTAGS START ====
HASHTAGS = [
    "#learnkannada",
    "#kannadalessons",
    "#kannadaforbeginners",
    "#languagelearning",
    "#kannadavocabulary",
    "#velocitykannada",
    "#dailykannada",
    "#kannada",
    "#learnlanguages",
    "#speakkannada",
    "#bilingual",
    "#languagetips",
]
# ==== HASHTAGS END ====
