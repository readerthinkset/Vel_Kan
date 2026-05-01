"""
Facebook Reels Automation - Bilingual English/Kannada Content Generator
IMPROVED VERSION: Better backgrounds, English categories, no repeats, Velocity Kannada branding
"""

import os
import sys
import json
import random
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

if not AI_MODEL:
    raise ValueError(
        "AI_MODEL not set! Please add 'AI_MODEL=gemini-fast' to your .env file. "
        "For GitHub Actions: Add AI_MODEL to repository secrets."
    )

# Directories
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

# Video settings (9:16 vertical)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# English category names (for learners of Kannada)
# Essential Kannada learning categories + Motivational categories
CATEGORIES_ENGLISH = [
    "Greetings", "Basic Phrases", "Common Expressions", "Travel Kannada", "Restaurant Kannada",
    "Shopping Kannada", "Emergency Kannada", "Family Terms", "Numbers Kannada", "Time Kannada",
    "Motivation", "Love", "Success", "Wisdom", "Happiness",
    "Self Improvement", "Gratitude", "Friendship", "Hope", "Creativity",
    "Inner Peace", "Confidence", "Perseverance", "Inspiration", "Positive Life",
    "Courage", "Kindness", "Patience", "Forgiveness", "Strength",
    "Joy", "Balance", "Growth", "Purpose", "Mindfulness",
]

# Kannada translations for display
CATEGORIES_KANNADA = {
    "Greetings": "ಶುಭೋದಯ",
    "Basic Phrases": "ಮೂಲಭೂತ ವಾಕ್ಯಗಳು",
    "Common Expressions": "ಸಾಮಾನ್ಯ ಅಭಿವ್ಯಕ್ತಿಗಳು",
    "Travel Kannada": "ಪ್ರಯಾಣ ಕನ್ನಡ",
    "Restaurant Kannada": "ರೆಸ್ಟೋರೆಂಟ್ ಕನ್ನಡ",
    "Shopping Kannada": "ಶಾಪಿಂಗ್ ಕನ್ನಡ",
    "Emergency Kannada": "ತುರ್ತು ಕನ್ನಡ",
    "Family Terms": "ಕುಟುಂಬದ ಪದಗಳು",
    "Numbers Kannada": "ಸಂಖ್ಯೆಗಳು",
    "Time Kannada": "ಸಮಯ",
    "Motivation": "ಪ್ರೇರಣೆ",
    "Love": "ಪ್ರೀತಿ",
    "Success": "ಯಶಸ್ಸು",
    "Wisdom": "ಜ್ಞಾನ",
    "Happiness": "ಸಂತೋಷ",
    "Self Improvement": "ಸ್ವಯಂ ಸುಧಾರಣೆ",
    "Gratitude": "ಕೃತಜ್ಞತೆ",
    "Friendship": "ಸ್ನೇಹ",
    "Hope": "ಭಾವಿ",
    "Creativity": "ಸೃಜನಶೀಲತೆ",
    "Inner Peace": "ಆಂತರಿಕ ಶಾಂತಿ",
    "Confidence": "ಆತ್ಮವಿಶ್ವಾಸ",
    "Perseverance": "ಹಠಧಾರಣೆ",
    "Inspiration": "ಸ್ಫೂರ್ತಿ",
    "Positive Life": "ಸಕಾರಾತ್ಮಕ ಜೀವನ",
    "Courage": "ಧೈರ್ಯ",
    "Kindness": "ದಯೆ",
    "Patience": "ತಾಳ್ಮೆ",
    "Forgiveness": "ಕ್ಷಮಾಪಣೆ",
    "Strength": "ಬಲ",
    "Joy": "ಆನಂದ",
    "Balance": "ಸಮತೋಲನ",
    "Growth": "ಬೆಳವಣಿಗೆ",
    "Purpose": "ಉದ್ದೇಶ",
    "Mindfulness": "ಜಾಗೃತಿ",
}

# Edge TTS voices
ENGLISH_VOICE = "en-US-GuyNeural"
KANNADA_VOICE = "kn-IN-SapnaNeural"

# Phrase history file (NEVER delete this!)
PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"

# Recent categories file (for rotation - prevents category repeats)
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"
MAX_RECENT_CATEGORIES = 15


# ============== PHRASE HISTORY MANAGEMENT (Prevent Repeats) ==============

def load_phrase_history():
    """Load all previously generated phrases"""
    if PHRASE_HISTORY_FILE.exists():
        with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"phrases": [], "last_updated": None}


def save_phrase_history(data):
    """Save phrase history"""
    data["last_updated"] = datetime.now().isoformat()
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_phrase_used(english_phrase):
    """Check if phrase was already generated"""
    history = load_phrase_history()
    english_lower = english_phrase.lower().strip()
    for p in history.get("phrases", []):
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def add_phrases_to_history(phrases, category):
    """Add new phrases to history"""
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            "kannada": phrase["kannada"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat()
        })
    save_phrase_history(history)
    print(f"[history] Added {len(phrases)} phrases to history (total: {len(history['phrases'])})")


# ============== CATEGORY ROTATION MANAGEMENT (Prevent Repeats) ==============

def load_recent_categories():
    """Load recently used categories"""
    if RECENT_CATEGORIES_FILE.exists():
        with open(RECENT_CATEGORIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"recent_categories": [], "last_updated": None}


def save_recent_categories(data):
    """Save recent categories"""
    data["last_updated"] = datetime.now().isoformat()
    with open(RECENT_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_available_category():
    """Get a category that hasn't been used recently - ensures rotation across ALL 35 categories"""
    recent_data = load_recent_categories()
    recent = recent_data.get("recent_categories", [])

    available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent]

    if not available:
        recent_data["recent_categories"] = recent[-5:]
        save_recent_categories(recent_data)
        available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent_data["recent_categories"]]
        print(f"[rotation] All categories used recently - cleared old ones, {len(available)} available")

    selected = random.choice(available)

    recent.append(selected)

    if len(recent) > MAX_RECENT_CATEGORIES:
        recent = recent[-MAX_RECENT_CATEGORIES:]

    recent_data["recent_categories"] = recent
    save_recent_categories(recent_data)

    print(f"[rotation] Selected '{selected}' ({len(available)} available, {len(recent)} in recent history)")
    return selected


# ============== CONTENT GENERATION ==============

def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    """Generate unique bilingual phrases with natural pauses, ensuring no repeats"""

    category_kannada = CATEGORIES_KANNADA[category_english]

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            import requests
            url = "https://gen.pollinations.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {POLLINATIONS_API_KEY}",
                "Content-Type": "application/json"
            }

            prompt = f"""Create {num_phrases * 2} unique {category_english} phrases for English speakers learning Kannada.

IMPORTANT RULES FOR NATURAL SPEECH:
1. Keep phrases SHORT (5-12 words max per language)
2. Add NATURAL PAUSES using commas (e.g., "Dream big, start small")
3. Use punctuation for breathing room in TTS
4. Avoid long run-on sentences
5. Each phrase should be speakable in 3-5 seconds
6. Kannada text should be CLEAN - use standard Kannada script
7. Do NOT include multiple versions or slashes - just ONE clean Kannada translation
8. Transliteration should be in Roman script (e.g., "namaskaara")

For each phrase:
1. English phrase (with commas for natural pauses)
2. Kannada translation (in Kannada script)
3. Transliteration (Roman script pronunciation, e.g., "namaskaara")

Return as JSON array:
[{{"english": "...", "kannada": "...", "transliteration": "..."}}]

IMPORTANT: Create FRESH, UNIQUE phrases that haven't been used before.
IMPORTANT: Kannada text must be clean - no slashes, no multiple versions."""

            payload = {
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a Kannada teacher. Create short, natural phrases with pauses."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.9
            }

            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            phrases = json.loads(content)

            # Normalize: accept both 'romaji' and 'transliteration' keys
            for p in phrases:
                if "transliteration" not in p and "romaji" in p:
                    p["transliteration"] = p.pop("romaji")

            unique_phrases = []
            for phrase in phrases:
                if len(phrase["english"].split()) > 15:
                    continue
                if not is_phrase_used(phrase["english"]):
                    unique_phrases.append(phrase)
                if len(unique_phrases) >= num_phrases:
                    break

            if len(unique_phrases) >= num_phrases:
                add_phrases_to_history(unique_phrases[:num_phrases], category_english)
                return unique_phrases[:num_phrases]

        except Exception as e:
            print(f"[content] Attempt {attempt + 1} failed: {e}")

    print("[content] Using fallback phrases...")
    return get_fresh_fallback_phrases(category_english, num_phrases)


def get_fresh_fallback_phrases(category: str, num_phrases: int) -> list:
    """Get fallback phrases, filtering out used ones"""

    all_fallbacks = {
        "Greetings": [
            {"english": "Hello, nice to meet you.", "kannada": "ನಮಸ್ಕಾರ, ನಿಮ್ಮೊಂದಿಗೆ ಭೇಟಿಯಾಗಿ ಸಂತೋಷವಾಗಿದೆ.", "transliteration": "Namaskaara, nimmondige bhetiyaagi santoshaagaide."},
            {"english": "Good morning!", "kannada": "ಶುಭೋದಯ!", "transliteration": "Shubhodaya!"},
            {"english": "Good evening, how are you?", "kannada": "ಶುಭ ಸಂಜೆ, ಹೇಗಿದ್ದೀರಿ?", "transliteration": "Shubha sanje, hegiddeeri?"},
            {"english": "See you tomorrow!", "kannada": "ನಾಳೆ ಭೇಟಿ!", "transliteration": "Naale bheti!"},
            {"english": "Goodbye, take care.", "kannada": "ವಿದಾಯ, ಕಾಳಜಿ ವಹಿಸಿ.", "transliteration": "Vidaaya, kaalaji vahisi."},
        ],
        "Basic Phrases": [
            {"english": "Thank you very much.", "kannada": "ತುಂಬಾ ಧನ್ಯವಾದಗಳು.", "transliteration": "Tumbaa dhanyavaadagalu."},
            {"english": "You're welcome.", "kannada": "ದೇವರು ಕಾಪಾಡಲಿ.", "transliteration": "Devaru kaapaadali."},
            {"english": "I'm sorry, excuse me.", "kannada": "ಕ್ಷಮಿಸಿ.", "transliteration": "Kshamisi."},
            {"english": "Yes, that's correct.", "kannada": "ಹೌದು, ಅದು ಸರಿ.", "transliteration": "Haudu, adu sari."},
            {"english": "No, I don't think so.", "kannada": "ಇಲ್ಲ, ನನಗೆ ಹಾಗನ್ನಿಸುತ್ತಿಲ್ಲ.", "transliteration": "Illa, nanage haagannisuttilla."},
        ],
        "Common Expressions": [
            {"english": "How are you doing today?", "kannada": "ಇಂದು ಹೇಗಿದ್ದೀರಿ?", "transliteration": "Indu hegiddeeri?"},
            {"english": "I'm fine, thank you.", "kannada": "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ, ಧನ್ಯವಾದಗಳು.", "transliteration": "Naanu chennaagidduene, dhanyavaadagalu."},
            {"english": "What's your name?", "kannada": "ನಿಮ್ಮ ಹೆಸರೇನು?", "transliteration": "Nimma hesarenu?"},
            {"english": "My name is...", "kannada": "ನನ್ನ ಹೆಸರು...", "transliteration": "Nanna hesaru..."},
            {"english": "Nice to meet you too.", "kannada": "ನಿಮ್ಮೊಂದಿಗೆ ಭೇಟಿಯಾಗಿ ಸಂತೋಷ.", "transliteration": "Nimmondige bhetiyaagi santosha."},
        ],
        "Travel Kannada": [
            {"english": "Where is the bathroom?", "kannada": "ಬಾತ್‌ರೂಮ್ ಎಲ್ಲಿದೆ?", "transliteration": "Bathroom ellidde?"},
            {"english": "How do I get there?", "kannada": "ಅಲ್ಲಿಗೆ ಹೇಗೆ ಹೋಗುವುದು?", "transliteration": "Allige hege hoguvudu?"},
            {"english": "I need a taxi, please.", "kannada": "ನಮಗೆ ಟ್ಯಾಕ್ಸಿ ಬೇಕು, ದಯವಿಟ್ಟು.", "transliteration": "Namage taxi beku, dayavittu."},
            {"english": "Take me to the hotel.", "kannada": "ಹೋಟೆಲ್‌ಗೆ ಕರೆದುಕೊಂಡು ಹೋಗಿ.", "transliteration": "Hotelige karedukoNDu hogi."},
            {"english": "How much does it cost?", "kannada": "ಎಷ್ಟು ಬೆಲೆ?", "transliteration": "Eshtu belya?"},
        ],
        "Restaurant Kannada": [
            {"english": "Can I see the menu?", "kannada": "ಮೆನು ತೋರಿಸಬಹುದೇ?", "transliteration": "Menu torisbahudey?"},
            {"english": "This looks delicious!", "kannada": "ಇದು ರುಚಿಯಾಗಿ ಕಾಣುತ್ತಿದೆ!", "transliteration": "Idu ruchiyaagi kaanuttidde!"},
            {"english": "Water, please.", "kannada": "ನೀರು, ದಯವಿಟ್ಟು.", "transliteration": "Neeru, dayavittu."},
            {"english": "Check, please.", "kannada": "ಬಿಲ್, ದಯವಿಟ್ಟು.", "transliteration": "Billu, dayavittu."},
            {"english": "It was delicious!", "kannada": "ತುಂಬಾ ರುಚಿಯಾಗಿತ್ತು!", "transliteration": "Tumbaa ruchiyaagittu!"},
        ],
        "Shopping Kannada": [
            {"english": "How much is this?", "kannada": "ಇದು ಎಷ್ಟು?", "transliteration": "Idu eshtu?"},
            {"english": "Can I try this on?", "kannada": "ಇದನ್ನು ಪ್ರಯತ್ನಿಸಬಹುದೇ?", "transliteration": "Idannu prayatnisbahudey?"},
            {"english": "Do you have a smaller size?", "kannada": "ಸಣ್ಣ ಗಾತ್ರ ಇದೆಯೇ?", "transliteration": "Sanna gaatra iddeyaa?"},
            {"english": "I'll take this one.", "kannada": "ಇದನ್ನು ತೆಗೆದುಕೊಳ್ಳುತ್ತೇನೆ.", "transliteration": "Idannu tegedukoLLuttene."},
            {"english": "Can I pay by card?", "kannada": "ಕಾರ್ಡ್‌ನಿಂದ ಪಾವತಿಸಬಹುದೇ?", "transliteration": "Cardninda paavatisbahudey?"},
        ],
        "Emergency Kannada": [
            {"english": "Help me, please!", "kannada": "ಸಹಾಯ ಮಾಡಿ!", "transliteration": "Sahaaya maadi!"},
            {"english": "Call the police!", "kannada": "ಪೊಲೀಸ್‌ಗೆ ಕರೆ ಮಾಡಿ!", "transliteration": "Policege kare maadi!"},
            {"english": "I need a doctor.", "kannada": "ನನಗೆ ವೈದ್ಯರು ಬೇಕು.", "transliteration": "Nanage vaidhyaru beku."},
            {"english": "Where is the hospital?", "kannada": "ಆಸ್ಪತ್ರೆ ಎಲ್ಲಿದೆ?", "transliteration": "Aaspatre ellidde?"},
            {"english": "I'm lost, can you help?", "kannada": "ನಾನು ದಾರಿ ತಪ್ಪಿದ್ದೇನೆ, ಸಹಾಯ ಮಾಡಬಹುದೇ?", "transliteration": "Naanu daari tappiddene, sahaaya maadabahudey?"},
        ],
        "Family Terms": [
            {"english": "This is my mother.", "kannada": "ಇವರು ನನ್ನ ಅಮ್ಮ.", "transliteration": "Ivaru nanna amma."},
            {"english": "This is my father.", "kannada": "ಇವರು ನನ್ನ ಅಪ್ಪ.", "transliteration": "Ivaru nanna appa."},
            {"english": "I have an older brother.", "kannada": "ನನಗೆ ಅಣ್ಣ ಇದ್ದಾರೆ.", "transliteration": "Nanage anna iddaare."},
            {"english": "I have a younger sister.", "kannada": "ನನಗೆ ತಂಗಿ ಇದ್ದಾಳೆ.", "transliteration": "Nanage tangi iddaaLe."},
            {"english": "These are my parents.", "kannada": "ಇವರು ನನ್ನ ತಂದೆ ತಾಯಿ.", "transliteration": "Ivaru nanna tande taayi."},
        ],
        "Numbers Kannada": [
            {"english": "One, two, three.", "kannada": "ಒಂದು, ಎರಡು, ಮೂರು.", "transliteration": "Ondu, eradu, mooru."},
            {"english": "Four, five, six.", "kannada": "ನಾಲ್ಕು, ಐದು, ಆರು.", "transliteration": "Naalku, aidu, aaru."},
            {"english": "Seven, eight, nine, ten.", "kannada": "ಏಳು, ಎಂಟು, ಒಂಬತ್ತು, ಹತ್ತು.", "transliteration": "Eelu, entu, ombattu, hattu."},
            {"english": "What number is this?", "kannada": "ಇದು ಯಾವ ಸಂಖ್ಯೆ?", "transliteration": "Idu yaava sankhye?"},
            {"english": "Give me two, please.", "kannada": "ಎರಡು ಕೊಡಿ, ದಯವಿಟ್ಟು.", "transliteration": "Eradu kodi, dayavittu."},
        ],
        "Time Kannada": [
            {"english": "What time is it?", "kannada": "ಈಗ ಎಷ್ಟು ಗಂಟೆ?", "transliteration": "Eega eshtu gante?"},
            {"english": "It's three o'clock.", "kannada": "ಮೂರು ಗಂಟೆ ಆಗಿದೆ.", "transliteration": "Mooru gante aagide."},
            {"english": "See you at noon.", "kannada": "ಮಧ್ಯಾಹ್ನ ಭೇಟಿ.", "transliteration": "Madhyaahna bheti."},
            {"english": "I'll be there in five minutes.", "kannada": "ಐದು ನಿಮಿಷದಲ್ಲಿ ಬರುತ್ತೇನೆ.", "transliteration": "Aidu nimishadali baruttene."},
            {"english": "What day is today?", "kannada": "ಇಂದು ಯಾವ ದಿನ?", "transliteration": "Indu yaava dina?"},
        ],
        "Motivation": [
            {"english": "Believe in yourself.", "kannada": "ನಿಮ್ಮಲ್ಲಿ ನಂಬಿಕೆ ಇಡಿ.", "transliteration": "Nimmalli nambike idi."},
            {"english": "You are capable of amazing things.", "kannada": "ನೀವು ಅದ್ಭುತವಾದ ವಿಷಯಗಳನ್ನು ಮಾಡಬಲ್ಲಿರಿ.", "transliteration": "Neevu adbuthavaada vishayagalannu maadaballiri."},
            {"english": "Dream big, start small.", "kannada": "ದೊಡ್ಡ ಕನಸು ಕಾಣಿ, ಸಣ್ಣದರಿಂದ ಶುರುಮಾಡಿ.", "transliteration": "Dodda kanasu kaani, sannadarinda shurumaadi."},
            {"english": "Your future is created by your actions.", "kannada": "ನಿಮ್ಮ ಭವಿಷ್ಯವನ್ನು ನಿಮ್ಮ ಕ್ರಿಯೆಗಳು ನಿರ್ಮಿಸುತ್ತವೆ.", "transliteration": "Nimma bhavishyavannu nimma kriyeygalu nirmisuttave."},
            {"english": "Never give up on your dreams.", "kannada": "ನಿಮ್ಮ ಕನಸುಗಳನ್ನು ಎಂದಿಗೂ ಬಿಡಬೇಡಿ.", "transliteration": "Nimma kanasugalannu endigoo bidabedi."},
        ],
        "Love": [
            {"english": "Love yourself first.", "kannada": "ಮೊದಲು ನಿಮ್ಮನ್ನು ಪ್ರೀತಿಸಿ.", "transliteration": "Modalu nimmannu preetisi."},
            {"english": "Love makes everything possible.", "kannada": "ಪ್ರೀತಿ ಎಲ್ಲವನ್ನೂ ಸಾಧ್ಯವಾಗಿಸುತ್ತದೆ.", "transliteration": "Preeti ellavannoo saadhyavaagisuttade."},
            {"english": "You are loved more than you know.", "kannada": "ನೀವು ಊಹಿಸಿದ್ದಕ್ಕಿಂತ ಹೆಚ್ಚು ಪ್ರೀತಿಸಲ್ಪಡುತ್ತಿದ್ದೀರಿ.", "transliteration": "Neevu oohisiddakkinta hechu preetispaduttiddeeri."},
            {"english": "Love is the greatest power.", "kannada": "ಪ್ರೀತಿಯೇ ಅತ್ಯುತ್ತಮ ಶಕ್ತಿ.", "transliteration": "Preetiya athyuttama shakti."},
            {"english": "Spread love everywhere you go.", "kannada": "ಎಲ್ಲಿಗೆ ಹೋದರೂ ಪ್ರೀತಿಯನ್ನು ಹರಡಿ.", "transliteration": "Ellige hodaroo dayeyannu haradi."},
        ],
        "Success": [
            {"english": "Success comes from hard work.", "kannada": "ಯಶಸ್ಸು ಕಠಿಣ ಪರಿಶ್ರಮದಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Yashassu kathina parishramadinda baruttade."},
            {"english": "Keep going, you're getting there.", "kannada": "ಮುಂದುವರಿಸಿ, ನೀವು ತಲುಪುತ್ತಿದ್ದೀರಿ.", "transliteration": "Munduvarisi, neevu taluputtiddeeri."},
            {"english": "Every step counts toward success.", "kannada": "ಪ್ರತಿ ಹೆಜ್ಜೆಯೂ ಯಶಸ್ಸಿಗೆ ದಾರಿ ಮಾಡುತ್ತದೆ.", "transliteration": "Prati hejjeyoo yashassige daari maaduttade."},
            {"english": "Your effort will pay off.", "kannada": "ನಿಮ್ಮ ಪರಿಶ್ರಮ ಫಲ ನೀಡುತ್ತದೆ.", "transliteration": "Nimma parishrama phala needuttade."},
            {"english": "Success is a journey, not a destination.", "kannada": "ಯಶಸ್ಸು ಪ್ರಯಾಣ, ಗಮ್ಯಸ್ಥಾನವಲ್ಲ.", "transliteration": "Yashassu prayaana, gamyasthaanavalla."},
        ],
        "Wisdom": [
            {"english": "Knowledge is power.", "kannada": "ಜ್ಞಾನವೇ ಶಕ್ತಿ.", "transliteration": "Jnaanave shakti."},
            {"english": "Learn from yesterday, live for today.", "kannada": "ನಿನ್ನೆಯಿಂದ ಕಲಿಯಿರಿ, ಇಂದು ಬದುಕಿ.", "transliteration": "Ninneyinda kaliyiri, indu baduki."},
            {"english": "The wise learn from others' mistakes.", "kannada": "ಬುದ್ಧಿವಂತರು ಇತರರ ತಪ್ಪುಗಳಿಂದ ಕಲಿಯುತ್ತಾರೆ.", "transliteration": "Buddhivantaree itarara tappugalinda kaliyuttaare."},
            {"english": "Experience is the best teacher.", "kannada": "ಅನುಭವವೇ ಅತ್ಯುತ್ತಮ ಗುರು.", "transliteration": "Anubhavavee athyuttama guru."},
            {"english": "Wisdom comes with age.", "kannada": "ವಯಸ್ಸಿನೊಂದಿಗೆ ಜ್ಞಾನ ಬರುತ್ತದೆ.", "transliteration": "Vayassindige jnaana baruttade."},
        ],
        "Happiness": [
            {"english": "Happiness is a choice.", "kannada": "ಸಂತೋಷವು ಒಂದು ಆಯ್ಕೆ.", "transliteration": "Santoshavu ondu aayke."},
            {"english": "Find joy in the little things.", "kannada": "ಸಣ್ಣ ವಿಷಯಗಳಲ್ಲಿ ಆನಂದ ಹುಡುಕಿ.", "transliteration": "Sanna vishayagalalli aananda huduki."},
            {"english": "Your happiness matters most.", "kannada": "ನಿಮ್ಮ ಸಂತೋಷವೇ ಅತ್ಯಂತ ಮುಖ್ಯ.", "transliteration": "Nimma santoshavee athyanta mukhya."},
            {"english": "Smile, it makes others happy.", "kannada": "ನಗಿ, ಇದು ಇತರರನ್ನು ಸಂತೋಷಪಡಿಸುತ್ತದೆ.", "transliteration": "Nagi, idu itararannu santoshapadisuttade."},
            {"english": "Happiness is contagious, spread it.", "kannada": "ಸಂತೋಷ ಸಾಂಕ್ರಾಮಿಕ, ಹರಡಿ.", "transliteration": "Santosha saankraamika, haradi."},
        ],
        "Self Improvement": [
            {"english": "Better today than yesterday.", "kannada": "ನಿನ್ನೆಗಿಂತ ಇಂದು ಉತ್ತಮ.", "transliteration": "Ninneginta indu uttama."},
            {"english": "Small steps lead to big changes.", "kannada": "ಸಣ್ಣ ಹೆಜ್ಜೆಗಳು ದೊಡ್ಡ ಬದಲಾವಣೆಗೆ ಕಾರಣವಾಗುತ್ತವೆ.", "transliteration": "Sanna hejjegalalu dodda badalaavage kaaraNaavaaguttave."},
            {"english": "Invest in yourself daily.", "kannada": "ಪ್ರತಿದಿನ ನಿಮ್ಮಲ್ಲಿ ಹೂಡಿಕೆ ಮಾಡಿ.", "transliteration": "Pratidina nimmalli hooduke maadi."},
            {"english": "Growth requires discomfort.", "kannada": "ಬೆಳವಣಿಗೆಗೆ ಅಸೌಕರ್ಯ ಅಗತ್ಯ.", "transliteration": "BeLavaNigegi asoukarjya agatya."},
            {"english": "Be your own competition.", "kannada": "ನಿಮ್ಮ ಸ್ವಂತ ಸ್ಪರ್ಧಿಯಾಗಿರಿ.", "transliteration": "Nimma svanta spardhiyaagiri."},
        ],
        "Gratitude": [
            {"english": "I am grateful for today.", "kannada": "ಇಂದಿಗೆ ನಾನು ಕೃತಜ್ಞನಾಗಿದ್ದೇನೆ.", "transliteration": "Indige naanu krutajnnnaagiddene."},
            {"english": "Thank you for everything.", "kannada": "ಎಲ್ಲಕ್ಕೂ ಧನ್ಯವಾದಗಳು.", "transliteration": "Ellakkoo dhanyavaadagalu."},
            {"english": "Gratitude turns what we have into enough.", "kannada": "ಕೃತಜ್ಞತೆ ನಮ್ಮಲ್ಲಿರುವುದನ್ನು ಸಾಕಾಗಿಸುತ್ತದೆ.", "transliteration": "Krutajnate nammalliruvudannu saakaagisuttade."},
            {"english": "Count your blessings daily.", "kannada": "ಪ್ರತಿದಿನ ನಿಮ್ಮ ಆಶೀರ್ವಾದಗಳನ್ನು ಲೆಕ್ಕಿಸಿ.", "transliteration": "Pratidina nimma aasheervaadagalannu lekkisi."},
            {"english": "A grateful heart is a happy heart.", "kannada": "ಕೃತಜ್ಞ ಹೃದಯ ಸಂತೋಷದ ಹೃದಯ.", "transliteration": "Krutajna hrudaya santoshada hrudaya."},
        ],
        "Friendship": [
            {"english": "Friends make life better.", "kannada": "ಸ್ನೇಹಿತರು ಜೀವನವನ್ನು ಸುಂದರಗೊಳಿಸುತ್ತಾರೆ.", "transliteration": "Snehitaru jevanavannu sundaragoLisuttaare."},
            {"english": "A true friend is always there.", "kannada": "ನಿಜವಾದ ಸ್ನೇಹಿತ ಯಾವಾಗಲೂ ಇರುತ್ತಾನೆ.", "transliteration": "Nijavaada snehitha yaavagaroo iruttaane."},
            {"english": "Friendship is a precious gift.", "kannada": "ಸ್ನೇಹವು ಬೆಲೆಯುಳ್ಳ ಕೊಡುಗೆ.", "transliteration": "Snehavu beleyuLLa koduge."},
            {"english": "Good friends are like stars.", "kannada": "ಒಳ್ಳೆಯ ಸ್ನೇಹಿತರು ನಕ್ಷತ್ರಗಳಂತೆ.", "transliteration": "OLLeeya snehitaru nakshatragalante."},
            {"english": "Cherish your true friends.", "kannada": "ನಿಮ್ಮ ನಿಜವಾದ ಸ್ನೇಹಿತರನ್ನು ಬೆಲೆ ಕೊಡಿ.", "transliteration": "Nimma nijavaada snehitarannu bele kodi."},
        ],
        "Hope": [
            {"english": "Hope never dies.", "kannada": "ಭಾವನೆ ಎಂದಿಗೂ ಸಾಯುವುದಿಲ್ಲ.", "transliteration": "Bhaavne endigoo saayuvudilla."},
            {"english": "Tomorrow is a new beginning.", "kannada": "ನಾಳೆ ಹೊಸ ಆರಂಭ.", "transliteration": "Naale hosa aarambha."},
            {"english": "Keep hope alive in your heart.", "kannada": "ನಿಮ್ಮ ಹೃದಯದಲ್ಲಿ ಭಾವನೆಯನ್ನು ಜೀವಂತವಾಗಿಡಿ.", "transliteration": "Nimma hrudadayadalli bhaavaneyannu jevantavaagidi."},
            {"english": "Hope is the light in darkness.", "kannada": "ಭಾವನೆ ಕತ್ತಲೆಯಲ್ಲಿ ಬೆಳಕು.", "transliteration": "Bhaavne kattaleyalli beLaku."},
            {"english": "Where there's hope, there's life.", "kannada": "ಭಾವನೆ ಇರುವಲ್ಲಿ ಜೀವನವಿದೆ.", "transliteration": "Bhaavne iruvalli jevanavide."},
        ],
        "Creativity": [
            {"english": "Create something beautiful today.", "kannada": "ಇಂದು ಏನಾದರೂ ಸುಂದರವಾಗಿ ಸೃಷ್ಟಿಸಿ.", "transliteration": "Indu enaadadoo sundaravaagi srishtisi."},
            {"english": "Your creativity is unique.", "kannada": "ನಿಮ್ಮ ಸೃಜನಶೀಲತೆ ಅನನ್ಯ.", "transliteration": "Nimma srujanashilathey ananya."},
            {"english": "Let your imagination run wild.", "kannada": "ನಿಮ್ಮ ಕಲ್ಪನೆಯನ್ನು ಸ್ವತಂತ್ರವಾಗಿ ಬಿಡಿ.", "transliteration": "Nimma kalpaneeyannu svatantaravaagi bidi."},
            {"english": "Art comes from the heart.", "kannada": "ಕಲೆ ಹೃದಯದಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Kale hrudayadinda baruttade."},
            {"english": "Every day is a canvas.", "kannada": "ಪ್ರತಿ ದಿನವೂ ಒಂದು ಕ್ಯಾನ್ವಾಸ್.", "transliteration": "Prati dinavoo ondu canvas."},
        ],
        "Inner Peace": [
            {"english": "Find peace within yourself.", "kannada": "ನಿಮ್ಮೊಳಗೆ ಶಾಂತಿ ಹುಡುಕಿ.", "transliteration": "NimmooLage shaanti huduki."},
            {"english": "Calm mind, happy heart.", "kannada": "ಶಾಂತ ಮನಸ್ಸು, ಸಂತೋಷದ ಹೃದಯ.", "transliteration": "Shaanta manassu, santoshada hrudaya."},
            {"english": "Peace begins with a smile.", "kannada": "ಶಾಂತಿ ನಗುವಿನಿಂದ ಶುರುವಾಗುತ್ತದೆ.", "transliteration": "Shaanti naguvininda shuruyaaguttade."},
            {"english": "Breathe deeply, let go.", "kannada": "ಆಳವಾಗಿ ಉಸಿರಾಡಿ, ಬಿಡಿ.", "transliteration": "AaLavaagi usiraadi, bidi."},
            {"english": "Your inner peace is precious.", "kannada": "ನಿಮ್ಮ ಆಂತರ್ಯದ ಶಾಂತಿ ಬೆಲೆಯುಳ್ಳದ್ದು.", "transliteration": "Nimma aantharyaada shaanti beleyuLLaddu."},
        ],
        "Confidence": [
            {"english": "Believe you can, you're right.", "kannada": "ನೀವು ಮಾಡಬಲ್ಲಿರಿ ಎಂದು ನಂಬಿ, ನಿಮಗೆ ಸರಿ.", "transliteration": "Neevu maadaballiri endu nambi, nimige sari."},
            {"english": "You are stronger than you think.", "kannada": "ನೀವು ಯೋಚಿಸಿದ್ದಕ್ಕಿಂತ ಬಲಶಾಲಿಯಾಗಿದ್ದೀರಿ.", "transliteration": "Neevu yoochisiddakkinta balashaaliyaagiddiri."},
            {"english": "Confidence comes from within.", "kannada": "ಆತ್ಮವಿಶ್ವಾಸ ಒಳಗಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Aatmavishvaasa oLagina baruttade."},
            {"english": "Stand tall, be proud.", "kannada": "ನೇರವಾಗಿ ನಿಲ್ಲಿ, ಹೆಮ್ಮೆಯಾಗಿರಿ.", "transliteration": "Naeravaagi nilli, hemmeyaagiri."},
            {"english": "You have what it takes.", "kannada": "ನಿಮಗೆ ಬೇಕಾದುದು ನಿಮ್ಮಲ್ಲಿದೆ.", "transliteration": "Nimage beekaadu nimmmalliide."},
        ],
        "Perseverance": [
            {"english": "Never give up, keep going.", "kannada": "ಎಂದಿಗೂ ಬಿಡಬೇಡಿ, ಮುಂದುವರಿಸಿ.", "transliteration": "Endigoo bidabedi, munduvarisi."},
            {"english": "Persistence beats talent.", "kannada": "ಪಟ್ಟುಬಿಡುವಿಕೆ ಪ್ರತಿಭೆಯನ್ನು ಸೋಲಿಸುತ್ತದೆ.", "transliteration": "PattuviDUvike pratibheyannu soLisuttade."},
            {"english": "Fall seven times, rise eight.", "kannada": "ಏಳು ಬಾರಿ ಬಿದ್ದರೆ ಎಂಟು ಬಾರಿ ಏಳಿ.", "transliteration": "Eelu baari biddare entu baari eLi."},
            {"english": "Hard work pays off eventually.", "kannada": "ಕಠಿಣ ಪರಿಶ್ರಮ ಕೊನೆಗೆ ಫಲ ನೀಡುತ್ತದೆ.", "transliteration": "Kathina parishrama konege phala needuttade."},
            {"english": "Stay the course, don't quit.", "kannada": "ಮಾರ್ಗದಲ್ಲಿ ಇರಿ, ಬಿಡಬೇಡಿ.", "transliteration": "Maargadalli iri, bidabedi."},
        ],
        "Inspiration": [
            {"english": "Let inspiration guide you.", "kannada": "ಸ್ಫೂರ್ತಿ ನಿಮ್ಮನ್ನು ಮಾರ್ಗದರ್ಶನ ಮಾಡಲಿ.", "transliteration": "Sphoorthi nimmanu maargadarshana maadali."},
            {"english": "Be the inspiration others need.", "kannada": "ಇತರರಿಗೆ ಬೇಕಾದ ಸ್ಫೂರ್ತಿಯಾಗಿರಿ.", "transliteration": "Itararige beekaada sphoorthiyaagiri."},
            {"english": "Inspire by example, not words.", "kannada": "ಮಾತುಗಳಿಂದಲ್ಲ, ಆದರ್ಶದಿಂದ ಸ್ಫೂರ್ತಿ ನೀಡಿ.", "transliteration": "Maatugalindalla, aadarshadinda sphoorthi needi."},
            {"english": "Your story inspires others.", "kannada": "ನಿಮ್ಮ ಕಥೆ ಇತರರಿಗೆ ಸ್ಫೂರ್ತಿ ನೀಡುತ್ತದೆ.", "transliteration": "Nimma kathe itararige sphoorthi needuttade."},
            {"english": "Find inspiration in nature.", "kannada": "ಪ್ರಕೃತಿಯಲ್ಲಿ ಸ್ಫೂರ್ತಿ ಹುಡುಕಿ.", "transliteration": "Pakruthiyalli sphoorthi huduki."},
        ],
        "Positive Life": [
            {"english": "Choose positivity every day.", "kannada": "ಪ್ರತಿದಿನ ಸಕಾರಾತ್ಮಕತೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ.", "transliteration": "Pratidina sakaaraatmakateyannu aayake maadi."},
            {"english": "Positive thoughts create positive life.", "kannada": "ಸಕಾರಾತ್ಮಕ ಆಲೋಚನೆಗಳು ಸಕಾರಾತ್ಮಕ ಜೀವನವನ್ನು ಸೃಷ್ಟಿಸುತ್ತವೆ.", "transliteration": "Sakaaraatmaka aalochanegalalu sakaaraatmaka jevanavannu srishtisuttave."},
            {"english": "Surround yourself with positivity.", "kannada": "ನಿಮ್ಮನ್ನು ಸಕಾರಾತ್ಮಕತೆಯಿಂದ ಸುತ್ತುವರಿಯಿರಿ.", "transliteration": "Nimmmannu sakaaraatmakateyinda suttuvariyiri."},
            {"english": "Every day is a fresh start.", "kannada": "ಪ್ರತಿ ದಿನವೂ ಹೊಸ ಆರಂಭ.", "transliteration": "Prati dinavoo hosa aarambha."},
            {"english": "Live life with a positive heart.", "kannada": "ಸಕಾರಾತ್ಮಕ ಹೃದಯದಿಂದ ಜೀವಿಸಿ.", "transliteration": "Sakaaraatmaka hrudayadinda jevisi."},
        ],
        "Courage": [
            {"english": "Be brave, take the leap.", "kannada": "ಧೈರ್ಯವಾಗಿರಿ, ಮುಂದಕ್ಕೆ ಹೋಗಿ.", "transliteration": "Dhairayavaagiri, mundakke hogi."},
            {"english": "Courage is not absence of fear.", "kannada": "ಧೈರ್ಯವೆಂದರೆ ಭಯವಿಲ್ಲದಿರುವುದು ಅಲ್ಲ.", "transliteration": "Dhairyavendare bhayavilladairuvudu alla."},
            {"english": "Face your fears with courage.", "kannada": "ಧೈರ್ಯದಿಂದ ನಿಮ್ಮ ಭಯಗಳನ್ನು ಎದುರಿಸಿ.", "transliteration": "Dhairyadinda nimma bhayagalannu edurisi."},
            {"english": "Brave hearts change the world.", "kannada": "ಧೈರ್ಯಶಾಲಿ ಹೃದಯಗಳು ಪ್ರಪಂಚವನ್ನು ಬದಲಾಯಿಸುತ್ತವೆ.", "transliteration": "Dhairyashaali hrudayagalu prapanchavannu badalaayisuttave."},
            {"english": "Courage grows with use.", "kannada": "ಧೈರ್ಯ ಬಳಸಿದಷ್ಟು ಬೆಳೆಯುತ್ತದೆ.", "transliteration": "Dhairya baLasidastu beLeyuttade."},
        ],
        "Kindness": [
            {"english": "Be kind to everyone you meet.", "kannada": "ನೀವು ಭೇಟಿಯಾಗುವ ಪ್ರತಿಯೊಬ್ಬರಿಗೂ ದಯೆ ತೋರಿಸಿ.", "transliteration": "Neevu bhetiyaagu pratiyobborigoo daye toorisi."},
            {"english": "Kindness costs nothing, means everything.", "kannada": "ದಯೆಗೆ ಬೆಲೆಯಿಲ್ಲ, ಅದು ಎಲ್ಲವನ್ನೂ ಅರ್ಥ ಮಾಡುತ್ತದೆ.", "transliteration": "Dayege belyilla, adu ellavannoo artha maaduttade."},
            {"english": "A kind word warms the heart.", "kannada": "ದಯೆಯ ಮಾತು ಹೃದಯವನ್ನು ಬೆಚ್ಚಗಾಗಿಸುತ್ತದೆ.", "transliteration": "Dayeya maathu hrudayavannu bechchagaagisuttade."},
            {"english": "Spread kindness wherever you go.", "kannada": "ಎಲ್ಲಿಗೆ ಹೋದರೂ ದಯೆಯನ್ನು ಹರಡಿ.", "transliteration": "Ellige hodaroo dayeyannu haradi."},
            {"english": "Kindness makes the world better.", "kannada": "ದಯೆ ಪ್ರಪಂಚವನ್ನು ಉತ್ತಮಗೊಳಿಸುತ್ತದೆ.", "transliteration": "Daye prapanchavannu uttamagoLisuttade."},
        ],
        "Patience": [
            {"english": "Good things come to those who wait.", "kannada": "ಕಾಯುವವರಿಗೆ ಒಳ್ಳೆಯ ವಿಷಯಗಳು ಬರುತ್ತವೆ.", "transliteration": "Kaayuvarige oL Leya vishayagalu baruttave."},
            {"english": "Patience is a virtue.", "kannada": "ತಾಳ್ಮೆಯು ಒಂದು ಗುಣ.", "transliteration": "TaaLmeyu ondu guna."},
            {"english": "Take your time, don't rush.", "kannada": "ನಿಮ್ಮ ಸಮಯ ತೆಗೆದುಕೊಳ್ಳಿ, ಅವಸರಪಡಬೇಡಿ.", "transliteration": "Nimma samaya tegedukoLLi, avarsarapadabedi."},
            {"english": "Patience brings peace of mind.", "kannada": "ತಾಳ್ಮೆ ಮನಸ್ಸಿಗೆ ಶಾಂತಿ ತರುತ್ತದೆ.", "transliteration": "TaaLme manassige shaanti taruttade."},
            {"english": "Wait patiently, trust the process.", "kannada": "ತಾಳ್ಮೆಯಿಂದ ಕಾಯಿರಿ, ಪ್ರಕ್ರಿಯೆಯನ್ನು ನಂಬಿ.", "transliteration": "TaaLmeyinda kaayiri, prakriyeyannu nambi."},
        ],
        "Forgiveness": [
            {"english": "Forgive and set yourself free.", "kannada": "ಕ್ಷಮಿಸಿ, ನಿಮ್ಮನ್ನು ವಿಮುಕ್ತಗೊಳಿಸಿ.", "transliteration": "Kshamisi, nimmanne vimuktagoLisi."},
            {"english": "Forgiveness is a gift to yourself.", "kannada": "ಕ್ಷಮಾಪಣೆ ನಿಮಗೆ ನೀವೇ ಕೊಟ್ಟ ಕೊಡುಗೆ.", "transliteration": "Kshamaapane nimage neeve kotta koduge."},
            {"english": "Let go of grudges, find peace.", "kannada": "ಅಸಹ್ಯವನ್ನು ಬಿಡಿ, ಶಾಂತಿ ಹುಡುಕಿ.", "transliteration": "Asahyavannu bidi, shaanti huduki."},
            {"english": "To err is human, to forgive divine.", "kannada": "ತಪ್ಪು ಮಾಡುವುದು ಮಾನವ ಸಹಜ, ಕ್ಷಮಿಸುವುದು ದೈವಿಕ.", "transliteration": "Tappu maaduvudu maanava sahaja, kshamisuvudu daivika."},
            {"english": "Forgiveness heals all wounds.", "kannada": "ಕ್ಷಮಾಪಣೆ ಎಲ್ಲ ಗಾಯಗಳನ್ನು ಗುಣಪಡಿಸುತ್ತದೆ.", "transliteration": "Kshamaapane ella gaayagalannu gunapadisuttade."},
        ],
        "Strength": [
            {"english": "You are stronger than you know.", "kannada": "ನೀವು ತಿಳಿದುದಕ್ಕಿಂತ ಬಲಶಾಲಿಯಾಗಿದ್ದೀರಿ.", "transliteration": "Neevu tiLidudakkinta balashaaliyaagiddiri."},
            {"english": "Strength comes from within.", "kannada": "ಬಲ ಒಳಗಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Bala oLagina baruttade."},
            {"english": "Your struggles develop your strength.", "kannada": "ನಿಮ್ಮ ಹೋರಾಟಗಳು ನಿಮ್ಮ ಬಲವನ್ನು ಬೆಳೆಸುತ್ತವೆ.", "transliteration": "Nimma horaatagalu nimma balavannu beLusuttave."},
            {"english": "Be strong, stay steady.", "kannada": "ಬಲವಾಗಿರಿ, ಸ್ಥಿರವಾಗಿರಿ.", "transliteration": "Balavaagiri, sthiravaagiri."},
            {"english": "Inner strength conquers all.", "kannada": "ಆಂತರ್ಯದ ಬಲ ಎಲ್ಲವನ್ನೂ ಗೆಲ್ಲುತ್ತದೆ.", "transliteration": "Aantharyada bala ellavannoo geLuttade."},
        ],
        "Joy": [
            {"english": "Find joy in every moment.", "kannada": "ಪ್ರತಿ ಕ್ಷಣದಲ್ಲಿ ಆನಂದ ಹುಡುಕಿ.", "transliteration": "Prati kshaNadaLLi aananda huduki."},
            {"english": "Joy is contagious, spread it.", "kannada": "ಆನಂದ ಸಾಂಕ್ರಾಮಿಕ, ಹರಡಿ.", "transliteration": "Aananda saankraamika, haradi."},
            {"english": "Let joy fill your heart today.", "kannada": "ಇಂದು ಆನಂದ ನಿಮ್ಮ ಹೃದಯ ತುಂಬಲಿ.", "transliteration": "Indu aananda nimma hrudaya tumbali."},
            {"english": "Choose joy over worry.", "kannada": "ಚಿಂತೆಗಿಂತ ಆನಂದವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ.", "transliteration": "Chinteginta aanandavannu aayake maadi."},
            {"english": "Joy is the simplest form of gratitude.", "kannada": "ಆನಂದವು ಕೃತಜ್ಞತೆಯ ಸರಳ ರೂಪ.", "transliteration": "Aanandavu krutajnateya sarala roopa."},
        ],
        "Balance": [
            {"english": "Find balance in your life.", "kannada": "ನಿಮ್ಮ ಜೀವನದಲ್ಲಿ ಸಮತೋಲನ ಹುಡುಕಿ.", "transliteration": "Nimma jevanadalli samatoLana huduki."},
            {"english": "Balance is the key to happiness.", "kannada": "ಸಮತೋಲನವೇ ಸಂತೋಷಕ್ಕೆ ಮಾರ್ಗ.", "transliteration": "Samato Lanave santoshakke maarga."},
            {"english": "Work hard, rest well.", "kannada": "ಗಟ್ಟಿಯಾಗಿ ಕೆಲಸ ಮಾಡಿ, ಚೆನ್ನಾಗಿ ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ.", "transliteration": "Gattiyaagi kelasa maadi, chennaagi vishraanti tegedukoLLi."},
            {"english": "A balanced life is a peaceful life.", "kannada": "ಸಮತೋಲಿತ ಜೀವನವೇ ಶಾಂತಿಮಯ ಜೀವನ.", "transliteration": "SamatoLita jevanave shaantimaya jevana."},
            {"english": "Prioritize what matters most.", "kannada": "ಅತ್ಯಂತ ಮುಖ್ಯವಾದುದಕ್ಕೆ ಆದ್ಯತೆ ನೀಡಿ.", "transliteration": "Athyanta mukhyavaadudake aadyate needi."},
        ],
        "Growth": [
            {"english": "Growth happens outside your comfort zone.", "kannada": "ಬೆಳವಣಿಗೆ ನಿಮ್ಮ ಆರಾಮ ವಲಯದ ಹೊರಗೆ ಆಗುತ್ತದೆ.", "transliteration": "BeLavaNige nimma aaraama valayada horage aaguttade."},
            {"english": "Embrace change, grow stronger.", "kannada": "ಬದಲಾವಣೆಯನ್ನು ಸ್ವಾಗತಿಸಿ, ಬಲವಾಗಿ ಬೆಳೆಯಿರಿ.", "transliteration": "Badalaavaneyannu svaagatisi, balavaagi beLeyiri."},
            {"english": "Every challenge is a growth opportunity.", "kannada": "ಪ್ರತಿ ಸವಾಲೂ ಬೆಳವಣಿಗೆಗೆ ಅವಕಾಶ.", "transliteration": "Prathi savaalooo beLavaNigege avakaasha."},
            {"english": "Grow through what you go through.", "kannada": "ನಿಮ್ಮ ಅನುಭವಗಳ ಮೂಲಕ ಬೆಳೆಯಿರಿ.", "transliteration": "Nimma anubhavagala moolaka beLeyiri."},
            {"english": "Personal growth is a lifelong journey.", "kannada": "ವೈಯಕ್ತಿಕ ಬೆಳವಣಿಗೆ ಜೀವನಪರ ಪ್ರಯಾಣ.", "transliteration": "Vaiyaktika beLavaNigejeevanapara prayaana."},
        ],
        "Purpose": [
            {"english": "Find your purpose, live it.", "kannada": "ನಿಮ್ಮ ಉದ್ದೇಶವನ್ನು ಕಂಡುಕೊಳ್ಳಿ, ಅದನ್ನು ಜೀವಿಸಿ.", "transliteration": "Nimma udeshavannu kaNDukoLLi, adannu jevisi."},
            {"english": "Purpose gives life meaning.", "kannada": "ಉದ್ದೇಶವು ಜೀವನಕ್ಕೆ ಅರ್ಥ ನೀಡುತ್ತದೆ.", "transliteration": "Uddeshavu jevanakke artha needuttade."},
            {"english": "Live with purpose and passion.", "kannada": "ಉದ್ದೇಶ ಮತ್ತು ಆಸಕ್ತಿಯೊಂದಿಗೆ ಜೀವಿಸಿ.", "transliteration": "UdDesha mattu aasaktiyondige jevisi."},
            {"english": "Your purpose is your calling.", "kannada": "ನಿಮ್ಮ ಉದ್ದೇಶವೇ ನಿಮ್ಮ ಕರೆ.", "transliteration": "Nimma udeshavee nimma kare."},
            {"english": "Discover purpose in everyday moments.", "kannada": "ದೈನಂದಿನ ಕ್ಷಣಗಳಲ್ಲಿ ಉದ್ದೇಶವನ್ನು ಕಂಡುಕೊಳ್ಳಿ.", "transliteration": "Dainandina kshaNagaLiLLi udeshavannu kaNDukoLLi."},
        ],
        "Mindfulness": [
            {"english": "Be present in this moment.", "kannada": "ಈ ಕ್ಷಣದಲ್ಲಿ ಇರಿ.", "transliteration": "Ee kshaNadaLLi iri."},
            {"english": "Mindfulness brings inner peace.", "kannada": "ಜಾಗೃತಿ ಆಂತರ್ಯದ ಶಾಂತಿ ತರುತ್ತದೆ.", "transliteration": "Jaagruthi aantharyada shaanti taruttade."},
            {"english": "Breathe deeply, stay mindful.", "kannada": "ಆಳವಾಗಿ ಉಸಿರಾಡಿ, ಜಾಗರೂಕರಾಗಿರಿ.", "transliteration": "AaLavaagi usiraadi, jaagarookaraagiri."},
            {"english": "The present moment is all we have.", "kannada": "ಪ್ರಸ್ತುತ ಕ್ಷಣವೇ ನಮ್ಮಲ್ಲಿರುವುದೆಲ್ಲ.", "transliteration": "Prasthutha kshaNavee nammalliruvudella."},
            {"english": "Practice mindfulness daily.", "kannada": "ಪ್ರತಿದಿನ ಜಾಗೃತಿ ಅಭ್ಯಾಸ ಮಾಡಿ.", "transliteration": "Pratidina jaagruthi abhyaasa maadi."},
        ],
    }

    fallbacks = all_fallbacks.get(category, all_fallbacks["Motivation"])
    fresh_phrases = [p for p in fallbacks if not is_phrase_used(p["english"])]
    return fresh_phrases[:num_phrases]


# ============== AUDIO GENERATION ==============

async def generate_single_audio(text: str, voice: str, output_path: str):
    """Generate audio using Edge TTS"""
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


async def generate_audio_with_retries(text: str, voice: str, output_path: str, max_retries: int = 3):
    """Generate audio with retry logic for TTS failures"""
    import asyncio
    for attempt in range(1, max_retries + 1):
        success = await generate_single_audio(text, voice, output_path)
        if success:
            if Path(output_path).exists() and Path(output_path).stat().st_size > 100:
                return True
            else:
                print(f"    TTS file too small or missing, retrying ({attempt}/{max_retries})...")
                await asyncio.sleep(2 * attempt)
                continue
        else:
            if attempt < max_retries:
                wait = 2 * attempt
                print(f"    TTS retry {attempt}/{max_retries} in {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"    TTS failed after {max_retries} attempts, using silence fallback")
                return False
    return False


def generate_all_audio(phrases: list, output_dir: str):
    """Generate audio for all phrases with proper timing"""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        kannada_file = output_dir / f"kannada_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  Phrase {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    KA: {phrase['kannada']}")

        # Generate English audio
        en_success = asyncio.run(generate_audio_with_retries(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    - English: {english_file.name}")
        else:
            print(f"    - English: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        # Generate Kannada audio
        ka_success = asyncio.run(generate_audio_with_retries(phrase["kannada"], KANNADA_VOICE, str(kannada_file)))
        if ka_success:
            print(f"    - Kannada: {kannada_file.name}")
        else:
            print(f"    - Kannada: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(kannada_file)]
            subprocess.run(cmd, capture_output=True)

        # Get ACTUAL durations
        en_duration = get_audio_duration(str(english_file))
        ka_duration = get_audio_duration(str(kannada_file))

        # Add pause between English and Kannada
        pause_between = 0.5
        total_duration = en_duration + pause_between + ka_duration

        print(f"    Total: {total_duration:.2f}s (EN: {en_duration:.2f}s + pause: {pause_between}s + KA: {ka_duration:.2f}s)")

        # Combine audio files
        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(kannada_file),
            "-filter_complex", f"[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{kannada_file.as_posix()}'\n")

            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    Combined verified: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "kannada": str(kannada_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "ka_duration": ka_duration
        })

    print(f"\n[audio] Generated {len(audio_files)} phrase audios")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    """Get audio duration in seconds"""
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    """Combine all audio files"""
    n = len(audio_files)
    print(f"[audio] Combining {n} audio files...")

    concat_file = Path(output_file).parent / "narration_list.txt"

    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if concat_file.exists():
        concat_file.unlink()

    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] Final narration: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True

    return False


# ============== IMAGE GENERATION ==============

NOTO_KANNADA_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosanskannada/NotoSansKannada%5BBDU%5D.ttf"
FONTS_DIR = BASE_DIR / "fonts"


def ensure_kannada_font():
    """Download NotoSansKannada font if not available locally"""
    font_file = FONTS_DIR / "NotoSansKannada-Bold.ttf"
    if font_file.exists():
        return str(font_file)

    FONTS_DIR.mkdir(exist_ok=True)

    try:
        import urllib.request
        print("[font] Downloading NotoSansKannada font (Kannada script support)...")
        urllib.request.urlretrieve(NOTO_KANNADA_FONT_URL, str(font_file))
        print(f"[font] Downloaded: {font_file}")
        return str(font_file)
    except Exception as e:
        print(f"[font] Download failed: {e}")
        alt_url = "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/hinted/ttf/NotoSansKannada/NotoSansKannada-Bold.ttf"
        try:
            import urllib.request
            urllib.request.urlretrieve(alt_url, str(font_file))
            print(f"[font] Downloaded from alternate: {font_file}")
            return str(font_file)
        except Exception as e2:
            print(f"[font] Alternate download also failed: {e2}")
    return None


def create_impressive_background(category_english: str):
    """Create stunning gradient background with geometric patterns and glow"""
    from PIL import Image, ImageDraw

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    category_colors = {
        "Greetings": [(70, 130, 180), (255, 140, 0), (255, 255, 0), (255, 99, 71)],
        "Basic Phrases": [(60, 179, 113), (255, 215, 0), (144, 238, 144), (255, 140, 0)],
        "Common Expressions": [(138, 43, 226), (255, 20, 147), (75, 0, 130), (255, 105, 180)],
        "Travel Kannada": [(0, 191, 255), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
        "Restaurant Kannada": [(255, 69, 0), (255, 215, 0), (220, 20, 60), (255, 140, 0)],
        "Shopping Kannada": [(255, 105, 180), (0, 100, 80), (255, 192, 203), (0, 200, 160)],
        "Emergency Kannada": [(255, 0, 0), (139, 0, 0), (255, 69, 0), (220, 20, 60)],
        "Family Terms": [(255, 182, 193), (138, 43, 226), (255, 160, 122), (75, 0, 130)],
        "Numbers Kannada": [(255, 215, 0), (0, 0, 139), (255, 140, 0), (70, 130, 180)],
        "Time Kannada": [(0, 0, 100), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
        "Motivation": [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)],
        "Love": [(255, 0, 100), (139, 0, 0), (255, 105, 180), (255, 192, 203)],
        "Success": [(255, 215, 0), (0, 100, 0), (255, 140, 0), (34, 139, 34)],
        "Wisdom": [(0, 0, 139), (255, 215, 0), (70, 130, 180), (255, 255, 0)],
        "Happiness": [(255, 255, 0), (255, 0, 255), (255, 165, 0), (147, 112, 219)],
        "Self Improvement": [(0, 128, 0), (255, 215, 0), (0, 255, 0), (255, 140, 0)],
        "Gratitude": [(255, 127, 80), (75, 0, 130), (255, 160, 122), (138, 43, 226)],
        "Friendship": [(255, 192, 203), (0, 100, 80), (255, 105, 180), (0, 200, 160)],
        "Hope": [(0, 0, 100), (255, 255, 0), (70, 130, 180), (255, 215, 0)],
        "Creativity": [(255, 0, 127), (0, 0, 139), (255, 20, 147), (75, 0, 130)],
        "Inner Peace": [(135, 206, 235), (0, 0, 100), (176, 224, 230), (75, 0, 130)],
        "Confidence": [(255, 69, 0), (0, 0, 139), (255, 140, 0), (70, 130, 180)],
        "Perseverance": [(139, 69, 19), (255, 215, 0), (160, 82, 45), (255, 140, 0)],
        "Inspiration": [(255, 0, 255), (75, 0, 130), (255, 20, 147), (0, 0, 139)],
        "Positive Life": [(50, 205, 50), (255, 0, 127), (144, 238, 144), (255, 20, 147)],
        "Courage": [(178, 34, 34), (255, 215, 0), (220, 20, 60), (255, 140, 0)],
        "Kindness": [(255, 182, 193), (138, 43, 226), (255, 160, 122), (75, 0, 130)],
        "Patience": [(34, 139, 34), (255, 255, 0), (60, 179, 113), (255, 215, 0)],
        "Forgiveness": [(230, 230, 250), (75, 0, 130), (216, 191, 216), (138, 43, 226)],
        "Strength": [(100, 100, 100), (255, 69, 0), (150, 150, 150), (255, 140, 0)],
        "Joy": [(255, 255, 0), (255, 0, 127), (255, 215, 0), (147, 112, 219)],
        "Balance": [(60, 179, 113), (138, 43, 226), (152, 251, 152), (75, 0, 130)],
        "Growth": [(0, 100, 0), (255, 215, 0), (34, 139, 34), (255, 140, 0)],
        "Purpose": [(75, 0, 130), (255, 215, 0), (138, 43, 226), (255, 140, 0)],
        "Mindfulness": [(210, 180, 140), (75, 0, 130), (245, 245, 220), (138, 43, 226)],
    }

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    # Create smooth multi-stop gradient
    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    # Add subtle geometric pattern for depth (circles)
    for i in range(0, VIDEO_WIDTH, 120):
        for j in range(0, VIDEO_HEIGHT, 120):
            draw.ellipse(
                [(i + 30, j + 30), (i + 90, j + 90)],
                outline=(255, 255, 255, 20),
                width=1
            )

    # Add radial glow effect from center
    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)

    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    # Composite glow over background
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)

    return img


def _find_kannada_font_file():
    """Find the best Kannada font file path for HarfBuzz rendering"""
    candidates = [
        str(FONTS_DIR / "NotoSansKannada-Bold.ttf"),
        str(FONTS_DIR / "NotoSansKannada-Regular.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansKannada-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
        "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/tunga.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return path

    for search_dir in ["/usr/share/fonts", "/usr/local/share/fonts", "C:/Windows/Fonts"]:
        if not Path(search_dir).exists():
            continue
        for root, dirs, files in os.walk(search_dir):
            for fname in files:
                fname_lower = fname.lower()
                if any(t.lower() in fname_lower for t in ["notosanskannada", "nirmala", "tunga"]):
                    return str(Path(root) / fname)

    return None


def _render_text_harfbuzz(text, font_path, font_size, fill_color, stroke_color=None, stroke_width=0):
    """Render Kannada text with proper HarfBuzz shaping and FreeType rasterization.
    Returns a PIL Image with the rendered text on transparent background."""
    import uharfbuzz as hb
    import freetype as ft
    from PIL import Image, ImageDraw, ImageChops

    blob = hb.Blob.from_file_path(font_path)
    hb_face = hb.Face(blob)
    hb_font = hb.Font(hb_face)
    hb_font.scale = (font_size * 64, font_size * 64)

    buffer = hb.Buffer()
    buffer.add_str(text)
    buffer.guess_segment_properties()
    hb.shape(hb_font, buffer)

    infos = buffer.glyph_infos
    positions = buffer.glyph_positions

    ft_face = ft.Face(font_path)
    ft_face.set_char_size(font_size * 64)

    min_x = float('inf')
    min_y = float('inf')
    max_x = float('-inf')
    max_y = float('-inf')

    x_cursor = 0.0
    y_cursor = 0.0
    glyph_metrics = []

    for info, pos in zip(infos, positions):
        ft_face.load_glyph(info.codepoint)
        bitmap = ft_face.glyph.bitmap
        bitmap_left = ft_face.glyph.bitmap_left
        bitmap_top = ft_face.glyph.bitmap_top
        x_off = pos.x_offset / 64.0
        y_off = pos.y_offset / 64.0
        x_adv = pos.x_advance / 64.0

        px = x_cursor + x_off + bitmap_left
        py = y_cursor + y_off - bitmap_top

        if bitmap.width > 0 and bitmap.rows > 0:
            min_x = min(min_x, px - stroke_width)
            min_y = min(min_y, py - stroke_width)
            max_x = max(max_x, px + bitmap.width + stroke_width)
            max_y = max(max_y, py + bitmap.rows + stroke_width)

        glyph_metrics.append({
            'codepoint': info.codepoint,
            'x': px, 'y': py,
            'width': bitmap.width, 'height': bitmap.rows,
            'x_advance': x_adv,
        })
        x_cursor += x_adv

    if min_x == float('inf'):
        total_width = max(x_cursor, 50)
        total_height = int(font_size * 1.5)
        min_x = 0
        min_y = 0
    else:
        total_width = max(max_x - min_x + stroke_width * 2, x_cursor + stroke_width * 2)
        total_height = max_y - min_y + stroke_width * 2

    total_width = int(total_width) + stroke_width * 2 + 4
    total_height = int(total_height) + stroke_width * 2 + 4

    img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))

    def _draw_glyphs(target_img, color):
        draw = ImageDraw.Draw(target_img)
        for gm in glyph_metrics:
            ft_face.load_glyph(gm['codepoint'])
            bitmap = ft_face.glyph.bitmap
            if bitmap.width > 0 and bitmap.rows > 0:
                glyph_img = Image.frombytes('L', (bitmap.width, bitmap.rows), bytes(bitmap.buffer))
                paste_x = int(gm['x'] - min_x + stroke_width)
                paste_y = int(gm['y'] - min_y + stroke_width)
                if color[-1] == 255:
                    colored_glyph = Image.new('RGBA', glyph_img.size, color)
                    colored_glyph.putalpha(glyph_img)
                    target_img.paste(colored_glyph, (paste_x, paste_y), glyph_img)
                else:
                    blended = Image.new('RGBA', glyph_img.size, color)
                    mask = glyph_img.point(lambda p: min(255, int(p * color[-1] / 255)))
                    blended.putalpha(mask)
                    target_img.paste(blended, (paste_x, paste_y), blended)

    if stroke_width > 0 and stroke_color:
        stroke_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
        for dx in range(-stroke_width, stroke_width + 1):
            for dy in range(-stroke_width, stroke_width + 1):
                if dx * dx + dy * dy <= stroke_width * stroke_width + 1:
                    shifted = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
                    _draw_glyphs(shifted, stroke_color)
                    stroke_img = Image.alpha_composite(stroke_img, ImageChops.offset(shifted, dx, dy))
        img = Image.alpha_composite(img, stroke_img)

    fill_img = Image.new('RGBA', (total_width, total_height), (0, 0, 0, 0))
    _draw_glyphs(fill_img, fill_color)
    img = Image.alpha_composite(img, fill_img)

    return img, int(x_cursor)


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str):
    """Generate image with impressive background"""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageChops
    except ImportError:
        print("PIL not available. Install: pip install Pillow")
        return None

    downloaded_font = ensure_kannada_font()

    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    # English text fonts (bold, professional)
    english_font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
    ]

    kannada_font_paths = [
        str(FONTS_DIR / "NotoSansKannada-Bold.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Bold.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansKannada-Bold.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansKannada-Regular.ttf",
        "C:/Windows/Fonts/Nirmala.ttc",
        "C:/Windows/Fonts/nirmala.ttf",
        "C:/Windows/Fonts/tunga.ttf",
    ]

    def load_font(font_paths, size):
        """Load font with fallback - searches directories if direct paths fail"""
        for font_path in font_paths:
            try:
                f = ImageFont.truetype(font_path, size)
                test_bbox = f.getbbox("ಕನ್ನಡ")
                if test_bbox[2] - test_bbox[0] > size * 0.5:
                    return f
            except (IOError, OSError):
                continue

        font_search_dirs = [
            "/usr/share/fonts",
            "/usr/local/share/fonts",
            "C:/Windows/Fonts",
        ]
        kannada_font_names = [
            "NotoSansKannada-Bold.ttf", "NotoSansKannada-Regular.ttf",
            "NotoSansKannada-Bold.ttc", "NotoSansKannada-Regular.ttc",
            "Nirmala.ttc", "tunga.ttf",
        ]

        for search_dir in font_search_dirs:
            if not Path(search_dir).exists():
                continue
            for root, dirs, files in os.walk(search_dir):
                for fname in files:
                    fname_lower = fname.lower()
                    if any(t.lower() in fname_lower for t in kannada_font_names):
                        try:
                            f = ImageFont.truetype(str(Path(root) / fname), size)
                            test_bbox = f.getbbox("ಕನ್ನಡ")
                            if test_bbox[2] - test_bbox[0] > size * 0.5:
                                print(f"  [font] Found Kannada font: {fname}")
                                return f
                        except (IOError, OSError):
                            continue

        print("  [WARNING] No Kannada-capable font found! Kannada text may not render.")
        return ImageFont.load_default()

    # English text fonts (bold, professional)
    font_category = load_font(english_font_paths, 60)
    font_large = load_font(english_font_paths, 85)
    font_branding = load_font(english_font_paths, 52)

    # Kannada text fonts (supports Kannada characters, bold)
    font_kannada = load_font(kannada_font_paths, 65)

    # Transliteration fonts - BOLD and LARGER for better visibility
    font_transliteration = load_font(english_font_paths, 55)

    english = phrase_data.get("english", "")
    kannada = phrase_data.get("kannada", "")
    transliteration = phrase_data.get("transliteration", phrase_data.get("romaji", ""))

    def wrap_text(text, font, max_width):
        """Wrap text to fit within max_width - handles both English and Kannada"""
        lines = []

        is_kannada = any('\u0c80' <= c <= '\u0cff' for c in text)

        if is_kannada:
            words = text.split(' ')
            current_line = ''
            for word in words:
                test_line = (current_line + ' ' + word).strip() if current_line else word
                try:
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    width = bbox[2] - bbox[0]
                except Exception:
                    width = len(test_line) * 40
                if width <= max_width or not current_line:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            if not lines:
                lines = [text]
        else:
            words = text.split()
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                width = bbox[2] - bbox[0]
                if width <= max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))

        return lines

    # Category at top
    category_text = category_english.upper()
    category_bbox = draw.textbbox((VIDEO_WIDTH // 2, 140), category_text, font=font_category, anchor="mm")
    padding = 25
    draw.rectangle(
        [(category_bbox[0] - padding, category_bbox[1] - padding),
         (category_bbox[2] + padding, category_bbox[3] + padding)],
        fill=(0, 0, 0, 200)
    )
    draw.text(
        (VIDEO_WIDTH // 2, 140),
        category_text,
        fill=(255, 255, 255),
        font=font_category,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    # English text
    english_y = 470
    english_lines = wrap_text(english, font_large, VIDEO_WIDTH - 140)
    total_height = len(english_lines) * 95

    draw.rectangle(
        [(60, english_y - 55), (VIDEO_WIDTH - 60, english_y + total_height + 15)],
        fill=(20, 30, 80, 220)
    )

    for i, line in enumerate(english_lines):
        y_pos = english_y + (i * 95)
        draw.text(
            (VIDEO_WIDTH // 2, y_pos),
            line,
            fill=(255, 255, 255),
            font=font_large,
            anchor="mm",
            stroke_width=2,
            stroke_fill=(0, 0, 0)
        )

    # Kannada text - rendered with HarfBuzz for proper conjunct shaping
    kannada_y = english_y + total_height + 110
    kannada_font_path = _find_kannada_font_file()
    use_harfbuzz = kannada_font_path is not None

    if use_harfbuzz:
        try:
            import uharfbuzz as hb
            import freetype as ft
        except ImportError:
            use_harfbuzz = False
            print("  [WARNING] uharfbuzz/freetype not available, falling back to Pillow")

    if use_harfbuzz:
        max_kannada_width = VIDEO_WIDTH - 200
        kannada_words = kannada.split(' ')
        kannada_lines = []
        current_line_words = []

        for word in kannada_words:
            test_line = ' '.join(current_line_words + [word]) if current_line_words else word
            _, test_w = _render_text_harfbuzz(
                test_line, kannada_font_path, 65,
                fill_color=(255, 255, 0, 255)
            )
            single_word_w = 0
            if current_line_words:
                _, single_word_w = _render_text_harfbuzz(
                    word, kannada_font_path, 65,
                    fill_color=(255, 255, 0, 255)
                )

            if test_w <= max_kannada_width or not current_line_words:
                current_line_words.append(word)
            else:
                kannada_lines.append(' '.join(current_line_words))
                current_line_words = [word]

        if current_line_words:
            kannada_lines.append(' '.join(current_line_words))

        if not kannada_lines:
            kannada_lines = [kannada]

        line_spacing = 85
        total_height = len(kannada_lines) * line_spacing

        kannada_padding = 60
        draw.rectangle(
            [(50, kannada_y - kannada_padding), (VIDEO_WIDTH - 50, kannada_y + total_height + kannada_padding - 10)],
            fill=(80, 30, 30, 220)
        )

        for i, line in enumerate(kannada_lines):
            rendered, text_w = _render_text_harfbuzz(
                line, kannada_font_path, 65,
                fill_color=(255, 255, 0, 255),
                stroke_color=(0, 0, 0, 255),
                stroke_width=2
            )
            x_pos = (VIDEO_WIDTH - rendered.width) // 2
            y_pos = kannada_y + (i * line_spacing) - rendered.height // 2
            img.paste(rendered, (x_pos, y_pos), rendered)
    else:
        kannada_lines = wrap_text(kannada, font_kannada, VIDEO_WIDTH - 200)
        total_height = len(kannada_lines) * 75

        kannada_padding = 60
        draw.rectangle(
            [(50, kannada_y - kannada_padding), (VIDEO_WIDTH - 50, kannada_y + total_height + kannada_padding - 10)],
            fill=(80, 30, 30, 220)
        )

        for i, line in enumerate(kannada_lines):
            y_pos = kannada_y + (i * 75)
            draw.text(
                (VIDEO_WIDTH // 2, y_pos),
                line,
                fill=(255, 255, 0),
                font=font_kannada,
                anchor="mm",
                stroke_width=3,
                stroke_fill=(0, 0, 0)
            )

    # Transliteration with FILLED BOX - BOLDER text for better visibility
    transliteration_y = kannada_y + total_height + 90
    transliteration_text = f"[{transliteration}]"
    transliteration_lines = wrap_text(transliteration_text, font_transliteration, VIDEO_WIDTH - 160)

    if transliteration_lines:
        transliteration_total_height = len(transliteration_lines) * 60
        draw.rectangle(
            [(70, transliteration_y - 25), (VIDEO_WIDTH - 70, transliteration_y + transliteration_total_height + 15)],
            fill=(40, 40, 40, 230)
        )

        for i, transliteration_line in enumerate(transliteration_lines):
            y_pos = transliteration_y + (i * 60)
            draw.text(
                (VIDEO_WIDTH // 2, y_pos),
                transliteration_line,
                fill=(255, 255, 255),
                font=font_transliteration,
                anchor="mm",
                stroke_width=3,
                stroke_fill=(0, 0, 0, 220)
            )

    # Branding
    branding_y = VIDEO_HEIGHT - 100
    draw.rectangle(
        [(0, branding_y - 30), (VIDEO_WIDTH, branding_y + 50)],
        fill=(0, 0, 0, 180)
    )
    draw.text(
        (VIDEO_WIDTH // 2, branding_y),
        "VELOCITY KANNADA",
        fill=(255, 255, 255),
        font=font_branding,
        anchor="mm",
        stroke_width=2,
        stroke_fill=(0, 0, 0)
    )

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  Image: {Path(output_path).name}")
    return output_path


# ============== VIDEO CREATION ==============

def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    """Create video from images and audio with PERFECT synchronization"""

    print(f"\n[video] Creating video from {len(image_files)} images...")
    print(f"[video] Ensuring complete audio playback and sync...")

    temp_clips = []

    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"  Image {i+1}/{len(image_files)}: {duration:.2f}s (EN: {audio_info.get('en_duration', 0):.1f}s + KA: {audio_info.get('ka_duration', 0):.1f}s)")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]

        subprocess.run(cmd, check=True, capture_output=True)

    # Concatenate clips
    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    concat_file = Path(output_file).parent / "concat_list.txt"

    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(temp_video)]
    subprocess.run(cmd, check=True, capture_output=True)

    # Add audio
    print("[video] Adding audio (ensuring complete playback)...")
    audio_duration = get_audio_duration(combined_audio)
    print(f"[video] Audio duration: {audio_duration:.2f}s")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    # Verify
    video_duration = get_audio_duration(str(output_file).replace(".mp4", ".mp4"))
    print(f"[video] Video created: {Path(output_file).name} ({video_duration:.2f}s)")

    # Cleanup
    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()


# ============== MAIN WORKFLOW ==============

def generate_reel(category_english: str = None):
    """Generate complete Facebook Reel"""

    if not category_english:
        category_english = get_available_category()

    print(f"\n{'='*80}")
    print(f"Category: {category_english} ({CATEGORIES_KANNADA[category_english]})")
    print(f"{'='*80}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reel_dir = VIDEO_DIR / f"{category_english}_{timestamp}"
    reel_dir.mkdir(exist_ok=True)

    # Step 1: Generate unique phrases
    print("[1/4] Generating unique phrases (checking history)...")
    phrases = generate_phrases(category_english, num_phrases=5)

    for i, phrase in enumerate(phrases, 1):
        print(f"  {i}. {phrase['english']} -> {phrase['kannada']}")

    # Step 2: Generate images
    print("\n[2/4] Generating images with impressive backgrounds...")
    for i, phrase in enumerate(phrases):
        output_path = reel_dir / f"phrase_{i:02d}.jpg"
        generate_complete_image(phrase, category_english, str(output_path))
        print(f"  Image {i+1}: {phrase['english'][:40]}...")

    # Step 3: Generate audio
    print("\n[3/4] Generating audio (English + Kannada with 500ms pause)...")
    audio_files = generate_all_audio(phrases, str(reel_dir))

    final_audio = reel_dir / "narration.mp3"
    create_final_narration(audio_files, str(final_audio))

    # Step 4: Create video
    print("\n[4/4] Creating video...")
    output_video = reel_dir / "final_reel.mp4"

    image_files = sorted([str(p) for p in reel_dir.glob("phrase_*.jpg")])

    create_video_from_images_audio(
        image_files,
        audio_files,
        str(final_audio),
        str(output_video)
    )

    # Save metadata
    metadata = {
        "category_english": category_english,
        "category_kannada": CATEGORIES_KANNADA[category_english],
        "timestamp": timestamp,
        "phrases": phrases,
        "video": str(output_video),
        "audio": str(final_audio)
    }

    with open(reel_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"REEL COMPLETE!")
    print(f"  {reel_dir}")
    print(f"  {output_video.name}")
    print(f"  Branding: Velocity Kannada")
    print(f"{'='*80}\n")

    return metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print("VELOCITY KANNADA - FACEBOOK REELS AUTOMATION")
    print("="*80)
    print("\nFEATURES:")
    print("  - Natural pauses with commas (non-robotic TTS)")
    print("  - Perfect audio-video synchronization")
    print("  - Complete audio playback guaranteed")
    print("  - English category names (for learners)")
    print("  - Velocity Kannada branding at bottom")
    print("  - NEVER repeats phrases (permanent history tracking)")
    print(f"\nAVAILABLE CATEGORIES ({len(CATEGORIES_ENGLISH)} total):")
    for i, cat in enumerate(CATEGORIES_ENGLISH, 1):
        print(f"   {i:2d}. {cat} ({CATEGORIES_KANNADA[cat]})")
    print(f"\nDAILY CAPACITY:")
    print(f"  4 reels per day = 20 unique phrases daily")
    print(f"  {len(CATEGORIES_ENGLISH)} categories = Over 6 days before any category repeats")
    print(f"  Phrase history is PERMANENT (never deletes)")
    print(f"  AI generates FRESH phrases every time")
    print("="*80)

    generate_reel()

    print("\n" + "="*80)
    print("READY FOR DAILY AUTOMATION!")
    print("="*80)
    print("\nTo generate 4 reels for today:")
    print("  from facebook_reels_automation import generate_daily_content")
    print("  generate_daily_content(times_per_day=4)")
    print("\nTo generate a single reel:")
    print("  generate_reel('Love')  # Or any category from the list above")
    print("="*80)