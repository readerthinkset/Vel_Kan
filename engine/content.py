"""AI phrase generation with permanent no-repeat history."""

from __future__ import annotations

import json
import random
import time
from datetime import datetime

import requests

import config
from config import CATEGORIES, CATEGORIES_NATIVE, HISTORY_DIR, MAX_RECENT_CATEGORIES

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"

PHRASE_KEY = config.LANGUAGE["history_key"]
LANGUAGE_NAME = config.LANGUAGE["name"]
NATIVE_NAME = config.LANGUAGE["native_name"]

# ==== FALLBACK PHRASES START ====
FALLBACK_PHRASES = [
    {"english": "Hello, nice to meet you.", "native": "ನಮಸ್ಕಾರ, ನಿಮ್ಮೊಂದಿಗೆ ಭೇಟಿಯಾಗಿ ಸಂತೋಷವಾಗಿದೆ.", "transliteration": "Namaskaara, nimmondige bhetiyaagi santoshaagaide."},
    {"english": "Good morning!", "native": "ಶುಭೋದಯ!", "transliteration": "Shubhodaya!"},
    {"english": "Good evening, how are you?", "native": "ಶುಭ ಸಂಜೆ, ಹೇಗಿದ್ದೀರಿ?", "transliteration": "Shubha sanje, hegiddeeri?"},
    {"english": "See you tomorrow!", "native": "ನಾಳೆ ಭೇಟಿ!", "transliteration": "Naale bheti!"},
    {"english": "Goodbye, take care.", "native": "ವಿದಾಯ, ಕಾಳಜಿ ವಹಿಸಿ.", "transliteration": "Vidaaya, kaalaji vahisi."},
    {"english": "Thank you very much.", "native": "ತುಂಬಾ ಧನ್ಯವಾದಗಳು.", "transliteration": "Tumbaa dhanyavaadagalu."},
    {"english": "You're welcome.", "native": "ದೇವರು ಕಾಪಾಡಲಿ.", "transliteration": "Devaru kaapaadali."},
    {"english": "I'm sorry, excuse me.", "native": "ಕ್ಷಮಿಸಿ.", "transliteration": "Kshamisi."},
    {"english": "Yes, that's correct.", "native": "ಹೌದು, ಅದು ಸರಿ.", "transliteration": "Haudu, adu sari."},
    {"english": "No, I don't think so.", "native": "ಇಲ್ಲ, ನನಗೆ ಹಾಗನ್ನಿಸುತ್ತಿಲ್ಲ.", "transliteration": "Illa, nanage haagannisuttilla."},
    {"english": "How are you doing today?", "native": "ಇಂದು ಹೇಗಿದ್ದೀರಿ?", "transliteration": "Indu hegiddeeri?"},
    {"english": "I'm fine, thank you.", "native": "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ, ಧನ್ಯವಾದಗಳು.", "transliteration": "Naanu chennaagidduene, dhanyavaadagalu."},
    {"english": "What's your name?", "native": "ನಿಮ್ಮ ಹೆಸರೇನು?", "transliteration": "Nimma hesarenu?"},
    {"english": "My name is...", "native": "ನನ್ನ ಹೆಸರು...", "transliteration": "Nanna hesaru..."},
    {"english": "Nice to meet you too.", "native": "ನಿಮ್ಮೊಂದಿಗೆ ಭೇಟಿಯಾಗಿ ಸಂತೋಷ.", "transliteration": "Nimmondige bhetiyaagi santosha."},
    {"english": "Where is the bathroom?", "native": "ಬಾತ್‌ರೂಮ್ ಎಲ್ಲಿದೆ?", "transliteration": "Bathroom ellidde?"},
    {"english": "How do I get there?", "native": "ಅಲ್ಲಿಗೆ ಹೇಗೆ ಹೋಗುವುದು?", "transliteration": "Allige hege hoguvudu?"},
    {"english": "I need a taxi, please.", "native": "ನಮಗೆ ಟ್ಯಾಕ್ಸಿ ಬೇಕು, ದಯವಿಟ್ಟು.", "transliteration": "Namage taxi beku, dayavittu."},
    {"english": "Take me to the hotel.", "native": "ಹೋಟೆಲ್‌ಗೆ ಕರೆದುಕೊಂಡು ಹೋಗಿ.", "transliteration": "Hotelige karedukoNDu hogi."},
    {"english": "How much does it cost?", "native": "ಎಷ್ಟು ಬೆಲೆ?", "transliteration": "Eshtu belya?"},
    {"english": "Can I see the menu?", "native": "ಮೆನು ತೋರಿಸಬಹುದೇ?", "transliteration": "Menu torisbahudey?"},
    {"english": "This looks delicious!", "native": "ಇದು ರುಚಿಯಾಗಿ ಕಾಣುತ್ತಿದೆ!", "transliteration": "Idu ruchiyaagi kaanuttidde!"},
    {"english": "Water, please.", "native": "ನೀರು, ದಯವಿಟ್ಟು.", "transliteration": "Neeru, dayavittu."},
    {"english": "Check, please.", "native": "ಬಿಲ್, ದಯವಿಟ್ಟು.", "transliteration": "Billu, dayavittu."},
    {"english": "It was delicious!", "native": "ತುಂಬಾ ರುಚಿಯಾಗಿತ್ತು!", "transliteration": "Tumbaa ruchiyaagittu!"},
    {"english": "How much is this?", "native": "ಇದು ಎಷ್ಟು?", "transliteration": "Idu eshtu?"},
    {"english": "Can I try this on?", "native": "ಇದನ್ನು ಪ್ರಯತ್ನಿಸಬಹುದೇ?", "transliteration": "Idannu prayatnisbahudey?"},
    {"english": "Do you have a smaller size?", "native": "ಸಣ್ಣ ಗಾತ್ರ ಇದೆಯೇ?", "transliteration": "Sanna gaatra iddeyaa?"},
    {"english": "I'll take this one.", "native": "ಇದನ್ನು ತೆಗೆದುಕೊಳ್ಳುತ್ತೇನೆ.", "transliteration": "Idannu tegedukoLLuttene."},
    {"english": "Can I pay by card?", "native": "ಕಾರ್ಡ್‌ನಿಂದ ಪಾವತಿಸಬಹುದೇ?", "transliteration": "Cardninda paavatisbahudey?"},
    {"english": "Help me, please!", "native": "ಸಹಾಯ ಮಾಡಿ!", "transliteration": "Sahaaya maadi!"},
    {"english": "Call the police!", "native": "ಪೊಲೀಸ್‌ಗೆ ಕರೆ ಮಾಡಿ!", "transliteration": "Policege kare maadi!"},
    {"english": "I need a doctor.", "native": "ನನಗೆ ವೈದ್ಯರು ಬೇಕು.", "transliteration": "Nanage vaidhyaru beku."},
    {"english": "Where is the hospital?", "native": "ಆಸ್ಪತ್ರೆ ಎಲ್ಲಿದೆ?", "transliteration": "Aaspatre ellidde?"},
    {"english": "I'm lost, can you help?", "native": "ನಾನು ದಾರಿ ತಪ್ಪಿದ್ದೇನೆ, ಸಹಾಯ ಮಾಡಬಹುದೇ?", "transliteration": "Naanu daari tappiddene, sahaaya maadabahudey?"},
    {"english": "This is my mother.", "native": "ಇವರು ನನ್ನ ಅಮ್ಮ.", "transliteration": "Ivaru nanna amma."},
    {"english": "This is my father.", "native": "ಇವರು ನನ್ನ ಅಪ್ಪ.", "transliteration": "Ivaru nanna appa."},
    {"english": "I have an older brother.", "native": "ನನಗೆ ಅಣ್ಣ ಇದ್ದಾರೆ.", "transliteration": "Nanage anna iddaare."},
    {"english": "I have a younger sister.", "native": "ನನಗೆ ತಂಗಿ ಇದ್ದಾಳೆ.", "transliteration": "Nanage tangi iddaaLe."},
    {"english": "These are my parents.", "native": "ಇವರು ನನ್ನ ತಂದೆ ತಾಯಿ.", "transliteration": "Ivaru nanna tande taayi."},
    {"english": "One, two, three.", "native": "ಒಂದು, ಎರಡು, ಮೂರು.", "transliteration": "Ondu, eradu, mooru."},
    {"english": "Four, five, six.", "native": "ನಾಲ್ಕು, ಐದು, ಆರು.", "transliteration": "Naalku, aidu, aaru."},
    {"english": "Seven, eight, nine, ten.", "native": "ಏಳು, ಎಂಟು, ಒಂಬತ್ತು, ಹತ್ತು.", "transliteration": "Eelu, entu, ombattu, hattu."},
    {"english": "What number is this?", "native": "ಇದು ಯಾವ ಸಂಖ್ಯೆ?", "transliteration": "Idu yaava sankhye?"},
    {"english": "Give me two, please.", "native": "ಎರಡು ಕೊಡಿ, ದಯವಿಟ್ಟು.", "transliteration": "Eradu kodi, dayavittu."},
    {"english": "What time is it?", "native": "ಈಗ ಎಷ್ಟು ಗಂಟೆ?", "transliteration": "Eega eshtu gante?"},
    {"english": "It's three o'clock.", "native": "ಮೂರು ಗಂಟೆ ಆಗಿದೆ.", "transliteration": "Mooru gante aagide."},
    {"english": "See you at noon.", "native": "ಮಧ್ಯಾಹ್ನ ಭೇಟಿ.", "transliteration": "Madhyaahna bheti."},
    {"english": "I'll be there in five minutes.", "native": "ಐದು ನಿಮಿಷದಲ್ಲಿ ಬರುತ್ತೇನೆ.", "transliteration": "Aidu nimishadali baruttene."},
    {"english": "What day is today?", "native": "ಇಂದು ಯಾವ ದಿನ?", "transliteration": "Indu yaava dina?"},
    {"english": "Believe in yourself.", "native": "ನಿಮ್ಮಲ್ಲಿ ನಂಬಿಕೆ ಇಡಿ.", "transliteration": "Nimmalli nambike idi."},
    {"english": "You are capable of amazing things.", "native": "ನೀವು ಅದ್ಭುತವಾದ ವಿಷಯಗಳನ್ನು ಮಾಡಬಲ್ಲಿರಿ.", "transliteration": "Neevu adbuthavaada vishayagalannu maadaballiri."},
    {"english": "Dream big, start small.", "native": "ದೊಡ್ಡ ಕನಸು ಕಾಣಿ, ಸಣ್ಣದರಿಂದ ಶುರುಮಾಡಿ.", "transliteration": "Dodda kanasu kaani, sannadarinda shurumaadi."},
    {"english": "Your future is created by your actions.", "native": "ನಿಮ್ಮ ಭವಿಷ್ಯವನ್ನು ನಿಮ್ಮ ಕ್ರಿಯೆಗಳು ನಿರ್ಮಿಸುತ್ತವೆ.", "transliteration": "Nimma bhavishyavannu nimma kriyeygalu nirmisuttave."},
    {"english": "Never give up on your dreams.", "native": "ನಿಮ್ಮ ಕನಸುಗಳನ್ನು ಎಂದಿಗೂ ಬಿಡಬೇಡಿ.", "transliteration": "Nimma kanasugalannu endigoo bidabedi."},
    {"english": "Love yourself first.", "native": "ಮೊದಲು ನಿಮ್ಮನ್ನು ಪ್ರೀತಿಸಿ.", "transliteration": "Modalu nimmannu preetisi."},
    {"english": "Love makes everything possible.", "native": "ಪ್ರೀತಿ ಎಲ್ಲವನ್ನೂ ಸಾಧ್ಯವಾಗಿಸುತ್ತದೆ.", "transliteration": "Preeti ellavannoo saadhyavaagisuttade."},
    {"english": "You are loved more than you know.", "native": "ನೀವು ಊಹಿಸಿದ್ದಕ್ಕಿಂತ ಹೆಚ್ಚು ಪ್ರೀತಿಸಲ್ಪಡುತ್ತಿದ್ದೀರಿ.", "transliteration": "Neevu oohisiddakkinta hechu preetispaduttiddeeri."},
    {"english": "Love is the greatest power.", "native": "ಪ್ರೀತಿಯೇ ಅತ್ಯುತ್ತಮ ಶಕ್ತಿ.", "transliteration": "Preetiya athyuttama shakti."},
    {"english": "Spread love everywhere you go.", "native": "ಎಲ್ಲಿಗೆ ಹೋದರೂ ಪ್ರೀತಿಯನ್ನು ಹರಡಿ.", "transliteration": "Ellige hodaroo dayeyannu haradi."},
    {"english": "Success comes from hard work.", "native": "ಯಶಸ್ಸು ಕಠಿಣ ಪರಿಶ್ರಮದಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Yashassu kathina parishramadinda baruttade."},
    {"english": "Keep going, you're getting there.", "native": "ಮುಂದುವರಿಸಿ, ನೀವು ತಲುಪುತ್ತಿದ್ದೀರಿ.", "transliteration": "Munduvarisi, neevu taluputtiddeeri."},
    {"english": "Every step counts toward success.", "native": "ಪ್ರತಿ ಹೆಜ್ಜೆಯೂ ಯಶಸ್ಸಿಗೆ ದಾರಿ ಮಾಡುತ್ತದೆ.", "transliteration": "Prati hejjeyoo yashassige daari maaduttade."},
    {"english": "Your effort will pay off.", "native": "ನಿಮ್ಮ ಪರಿಶ್ರಮ ಫಲ ನೀಡುತ್ತದೆ.", "transliteration": "Nimma parishrama phala needuttade."},
    {"english": "Success is a journey, not a destination.", "native": "ಯಶಸ್ಸು ಪ್ರಯಾಣ, ಗಮ್ಯಸ್ಥಾನವಲ್ಲ.", "transliteration": "Yashassu prayaana, gamyasthaanavalla."},
    {"english": "Knowledge is power.", "native": "ಜ್ಞಾನವೇ ಶಕ್ತಿ.", "transliteration": "Jnaanave shakti."},
    {"english": "Learn from yesterday, live for today.", "native": "ನಿನ್ನೆಯಿಂದ ಕಲಿಯಿರಿ, ಇಂದು ಬದುಕಿ.", "transliteration": "Ninneyinda kaliyiri, indu baduki."},
    {"english": "The wise learn from others' mistakes.", "native": "ಬುದ್ಧಿವಂತರು ಇತರರ ತಪ್ಪುಗಳಿಂದ ಕಲಿಯುತ್ತಾರೆ.", "transliteration": "Buddhivantaree itarara tappugalinda kaliyuttaare."},
    {"english": "Experience is the best teacher.", "native": "ಅನುಭವವೇ ಅತ್ಯುತ್ತಮ ಗುರು.", "transliteration": "Anubhavavee athyuttama guru."},
    {"english": "Wisdom comes with age.", "native": "ವಯಸ್ಸಿನೊಂದಿಗೆ ಜ್ಞಾನ ಬರುತ್ತದೆ.", "transliteration": "Vayassindige jnaana baruttade."},
    {"english": "Happiness is a choice.", "native": "ಸಂತೋಷವು ಒಂದು ಆಯ್ಕೆ.", "transliteration": "Santoshavu ondu aayke."},
    {"english": "Find joy in the little things.", "native": "ಸಣ್ಣ ವಿಷಯಗಳಲ್ಲಿ ಆನಂದ ಹುಡುಕಿ.", "transliteration": "Sanna vishayagalalli aananda huduki."},
    {"english": "Your happiness matters most.", "native": "ನಿಮ್ಮ ಸಂತೋಷವೇ ಅತ್ಯಂತ ಮುಖ್ಯ.", "transliteration": "Nimma santoshavee athyanta mukhya."},
    {"english": "Smile, it makes others happy.", "native": "ನಗಿ, ಇದು ಇತರರನ್ನು ಸಂತೋಷಪಡಿಸುತ್ತದೆ.", "transliteration": "Nagi, idu itararannu santoshapadisuttade."},
    {"english": "Happiness is contagious, spread it.", "native": "ಸಂತೋಷ ಸಾಂಕ್ರಾಮಿಕ, ಹರಡಿ.", "transliteration": "Santosha saankraamika, haradi."},
    {"english": "Better today than yesterday.", "native": "ನಿನ್ನೆಗಿಂತ ಇಂದು ಉತ್ತಮ.", "transliteration": "Ninneginta indu uttama."},
    {"english": "Small steps lead to big changes.", "native": "ಸಣ್ಣ ಹೆಜ್ಜೆಗಳು ದೊಡ್ಡ ಬದಲಾವಣೆಗೆ ಕಾರಣವಾಗುತ್ತವೆ.", "transliteration": "Sanna hejjegalalu dodda badalaavage kaaraNaavaaguttave."},
    {"english": "Invest in yourself daily.", "native": "ಪ್ರತಿದಿನ ನಿಮ್ಮಲ್ಲಿ ಹೂಡಿಕೆ ಮಾಡಿ.", "transliteration": "Pratidina nimmalli hooduke maadi."},
    {"english": "Growth requires discomfort.", "native": "ಬೆಳವಣಿಗೆಗೆ ಅಸೌಕರ್ಯ ಅಗತ್ಯ.", "transliteration": "BeLavaNigegi asoukarjya agatya."},
    {"english": "Be your own competition.", "native": "ನಿಮ್ಮ ಸ್ವಂತ ಸ್ಪರ್ಧಿಯಾಗಿರಿ.", "transliteration": "Nimma svanta spardhiyaagiri."},
    {"english": "I am grateful for today.", "native": "ಇಂದಿಗೆ ನಾನು ಕೃತಜ್ಞನಾಗಿದ್ದೇನೆ.", "transliteration": "Indige naanu krutajnnnaagiddene."},
    {"english": "Thank you for everything.", "native": "ಎಲ್ಲಕ್ಕೂ ಧನ್ಯವಾದಗಳು.", "transliteration": "Ellakkoo dhanyavaadagalu."},
    {"english": "Gratitude turns what we have into enough.", "native": "ಕೃತಜ್ಞತೆ ನಮ್ಮಲ್ಲಿರುವುದನ್ನು ಸಾಕಾಗಿಸುತ್ತದೆ.", "transliteration": "Krutajnate nammalliruvudannu saakaagisuttade."},
    {"english": "Count your blessings daily.", "native": "ಪ್ರತಿದಿನ ನಿಮ್ಮ ಆಶೀರ್ವಾದಗಳನ್ನು ಲೆಕ್ಕಿಸಿ.", "transliteration": "Pratidina nimma aasheervaadagalannu lekkisi."},
    {"english": "A grateful heart is a happy heart.", "native": "ಕೃತಜ್ಞ ಹೃದಯ ಸಂತೋಷದ ಹೃದಯ.", "transliteration": "Krutajna hrudaya santoshada hrudaya."},
    {"english": "Friends make life better.", "native": "ಸ್ನೇಹಿತರು ಜೀವನವನ್ನು ಸುಂದರಗೊಳಿಸುತ್ತಾರೆ.", "transliteration": "Snehitaru jevanavannu sundaragoLisuttaare."},
    {"english": "A true friend is always there.", "native": "ನಿಜವಾದ ಸ್ನೇಹಿತ ಯಾವಾಗಲೂ ಇರುತ್ತಾನೆ.", "transliteration": "Nijavaada snehitha yaavagaroo iruttaane."},
    {"english": "Friendship is a precious gift.", "native": "ಸ್ನೇಹವು ಬೆಲೆಯುಳ್ಳ ಕೊಡುಗೆ.", "transliteration": "Snehavu beleyuLLa koduge."},
    {"english": "Good friends are like stars.", "native": "ಒಳ್ಳೆಯ ಸ್ನೇಹಿತರು ನಕ್ಷತ್ರಗಳಂತೆ.", "transliteration": "OLLeeya snehitaru nakshatragalante."},
    {"english": "Cherish your true friends.", "native": "ನಿಮ್ಮ ನಿಜವಾದ ಸ್ನೇಹಿತರನ್ನು ಬೆಲೆ ಕೊಡಿ.", "transliteration": "Nimma nijavaada snehitarannu bele kodi."},
    {"english": "Hope never dies.", "native": "ಭಾವನೆ ಎಂದಿಗೂ ಸಾಯುವುದಿಲ್ಲ.", "transliteration": "Bhaavne endigoo saayuvudilla."},
    {"english": "Tomorrow is a new beginning.", "native": "ನಾಳೆ ಹೊಸ ಆರಂಭ.", "transliteration": "Naale hosa aarambha."},
    {"english": "Keep hope alive in your heart.", "native": "ನಿಮ್ಮ ಹೃದಯದಲ್ಲಿ ಭಾವನೆಯನ್ನು ಜೀವಂತವಾಗಿಡಿ.", "transliteration": "Nimma hrudadayadalli bhaavaneyannu jevantavaagidi."},
    {"english": "Hope is the light in darkness.", "native": "ಭಾವನೆ ಕತ್ತಲೆಯಲ್ಲಿ ಬೆಳಕು.", "transliteration": "Bhaavne kattaleyalli beLaku."},
    {"english": "Where there's hope, there's life.", "native": "ಭಾವನೆ ಇರುವಲ್ಲಿ ಜೀವನವಿದೆ.", "transliteration": "Bhaavne iruvalli jevanavide."},
    {"english": "Create something beautiful today.", "native": "ಇಂದು ಏನಾದರೂ ಸುಂದರವಾಗಿ ಸೃಷ್ಟಿಸಿ.", "transliteration": "Indu enaadadoo sundaravaagi srishtisi."},
    {"english": "Your creativity is unique.", "native": "ನಿಮ್ಮ ಸೃಜನಶೀಲತೆ ಅನನ್ಯ.", "transliteration": "Nimma srujanashilathey ananya."},
    {"english": "Let your imagination run wild.", "native": "ನಿಮ್ಮ ಕಲ್ಪನೆಯನ್ನು ಸ್ವತಂತ್ರವಾಗಿ ಬಿಡಿ.", "transliteration": "Nimma kalpaneeyannu svatantaravaagi bidi."},
    {"english": "Art comes from the heart.", "native": "ಕಲೆ ಹೃದಯದಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Kale hrudayadinda baruttade."},
    {"english": "Every day is a canvas.", "native": "ಪ್ರತಿ ದಿನವೂ ಒಂದು ಕ್ಯಾನ್ವಾಸ್.", "transliteration": "Prati dinavoo ondu canvas."},
    {"english": "Find peace within yourself.", "native": "ನಿಮ್ಮೊಳಗೆ ಶಾಂತಿ ಹುಡುಕಿ.", "transliteration": "NimmooLage shaanti huduki."},
    {"english": "Calm mind, happy heart.", "native": "ಶಾಂತ ಮನಸ್ಸು, ಸಂತೋಷದ ಹೃದಯ.", "transliteration": "Shaanta manassu, santoshada hrudaya."},
    {"english": "Peace begins with a smile.", "native": "ಶಾಂತಿ ನಗುವಿನಿಂದ ಶುರುವಾಗುತ್ತದೆ.", "transliteration": "Shaanti naguvininda shuruyaaguttade."},
    {"english": "Breathe deeply, let go.", "native": "ಆಳವಾಗಿ ಉಸಿರಾಡಿ, ಬಿಡಿ.", "transliteration": "AaLavaagi usiraadi, bidi."},
    {"english": "Your inner peace is precious.", "native": "ನಿಮ್ಮ ಆಂತರ್ಯದ ಶಾಂತಿ ಬೆಲೆಯುಳ್ಳದ್ದು.", "transliteration": "Nimma aantharyaada shaanti beleyuLLaddu."},
    {"english": "Believe you can, you're right.", "native": "ನೀವು ಮಾಡಬಲ್ಲಿರಿ ಎಂದು ನಂಬಿ, ನಿಮಗೆ ಸರಿ.", "transliteration": "Neevu maadaballiri endu nambi, nimige sari."},
    {"english": "You are stronger than you think.", "native": "ನೀವು ಯೋಚಿಸಿದ್ದಕ್ಕಿಂತ ಬಲಶಾಲಿಯಾಗಿದ್ದೀರಿ.", "transliteration": "Neevu yoochisiddakkinta balashaaliyaagiddiri."},
    {"english": "Confidence comes from within.", "native": "ಆತ್ಮವಿಶ್ವಾಸ ಒಳಗಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Aatmavishvaasa oLagina baruttade."},
    {"english": "Stand tall, be proud.", "native": "ನೇರವಾಗಿ ನಿಲ್ಲಿ, ಹೆಮ್ಮೆಯಾಗಿರಿ.", "transliteration": "Naeravaagi nilli, hemmeyaagiri."},
    {"english": "You have what it takes.", "native": "ನಿಮಗೆ ಬೇಕಾದುದು ನಿಮ್ಮಲ್ಲಿದೆ.", "transliteration": "Nimage beekaadu nimmmalliide."},
    {"english": "Never give up, keep going.", "native": "ಎಂದಿಗೂ ಬಿಡಬೇಡಿ, ಮುಂದುವರಿಸಿ.", "transliteration": "Endigoo bidabedi, munduvarisi."},
    {"english": "Persistence beats talent.", "native": "ಪಟ್ಟುಬಿಡುವಿಕೆ ಪ್ರತಿಭೆಯನ್ನು ಸೋಲಿಸುತ್ತದೆ.", "transliteration": "PattuviDUvike pratibheyannu soLisuttade."},
    {"english": "Fall seven times, rise eight.", "native": "ಏಳು ಬಾರಿ ಬಿದ್ದರೆ ಎಂಟು ಬಾರಿ ಏಳಿ.", "transliteration": "Eelu baari biddare entu baari eLi."},
    {"english": "Hard work pays off eventually.", "native": "ಕಠಿಣ ಪರಿಶ್ರಮ ಕೊನೆಗೆ ಫಲ ನೀಡುತ್ತದೆ.", "transliteration": "Kathina parishrama konege phala needuttade."},
    {"english": "Stay the course, don't quit.", "native": "ಮಾರ್ಗದಲ್ಲಿ ಇರಿ, ಬಿಡಬೇಡಿ.", "transliteration": "Maargadalli iri, bidabedi."},
    {"english": "Let inspiration guide you.", "native": "ಸ್ಫೂರ್ತಿ ನಿಮ್ಮನ್ನು ಮಾರ್ಗದರ್ಶನ ಮಾಡಲಿ.", "transliteration": "Sphoorthi nimmanu maargadarshana maadali."},
    {"english": "Be the inspiration others need.", "native": "ಇತರರಿಗೆ ಬೇಕಾದ ಸ್ಫೂರ್ತಿಯಾಗಿರಿ.", "transliteration": "Itararige beekaada sphoorthiyaagiri."},
    {"english": "Inspire by example, not words.", "native": "ಮಾತುಗಳಿಂದಲ್ಲ, ಆದರ್ಶದಿಂದ ಸ್ಫೂರ್ತಿ ನೀಡಿ.", "transliteration": "Maatugalindalla, aadarshadinda sphoorthi needi."},
    {"english": "Your story inspires others.", "native": "ನಿಮ್ಮ ಕಥೆ ಇತರರಿಗೆ ಸ್ಫೂರ್ತಿ ನೀಡುತ್ತದೆ.", "transliteration": "Nimma kathe itararige sphoorthi needuttade."},
    {"english": "Find inspiration in nature.", "native": "ಪ್ರಕೃತಿಯಲ್ಲಿ ಸ್ಫೂರ್ತಿ ಹುಡುಕಿ.", "transliteration": "Pakruthiyalli sphoorthi huduki."},
    {"english": "Choose positivity every day.", "native": "ಪ್ರತಿದಿನ ಸಕಾರಾತ್ಮಕತೆಯನ್ನು ಆಯ್ಕೆ ಮಾಡಿ.", "transliteration": "Pratidina sakaaraatmakateyannu aayake maadi."},
    {"english": "Positive thoughts create positive life.", "native": "ಸಕಾರಾತ್ಮಕ ಆಲೋಚನೆಗಳು ಸಕಾರಾತ್ಮಕ ಜೀವನವನ್ನು ಸೃಷ್ಟಿಸುತ್ತವೆ.", "transliteration": "Sakaaraatmaka aalochanegalalu sakaaraatmaka jevanavannu srishtisuttave."},
    {"english": "Surround yourself with positivity.", "native": "ನಿಮ್ಮನ್ನು ಸಕಾರಾತ್ಮಕತೆಯಿಂದ ಸುತ್ತುವರಿಯಿರಿ.", "transliteration": "Nimmmannu sakaaraatmakateyinda suttuvariyiri."},
    {"english": "Every day is a fresh start.", "native": "ಪ್ರತಿ ದಿನವೂ ಹೊಸ ಆರಂಭ.", "transliteration": "Prati dinavoo hosa aarambha."},
    {"english": "Live life with a positive heart.", "native": "ಸಕಾರಾತ್ಮಕ ಹೃದಯದಿಂದ ಜೀವಿಸಿ.", "transliteration": "Sakaaraatmaka hrudayadinda jevisi."},
    {"english": "Be brave, take the leap.", "native": "ಧೈರ್ಯವಾಗಿರಿ, ಮುಂದಕ್ಕೆ ಹೋಗಿ.", "transliteration": "Dhairayavaagiri, mundakke hogi."},
    {"english": "Courage is not absence of fear.", "native": "ಧೈರ್ಯವೆಂದರೆ ಭಯವಿಲ್ಲದಿರುವುದು ಅಲ್ಲ.", "transliteration": "Dhairyavendare bhayavilladairuvudu alla."},
    {"english": "Face your fears with courage.", "native": "ಧೈರ್ಯದಿಂದ ನಿಮ್ಮ ಭಯಗಳನ್ನು ಎದುರಿಸಿ.", "transliteration": "Dhairyadinda nimma bhayagalannu edurisi."},
    {"english": "Brave hearts change the world.", "native": "ಧೈರ್ಯಶಾಲಿ ಹೃದಯಗಳು ಪ್ರಪಂಚವನ್ನು ಬದಲಾಯಿಸುತ್ತವೆ.", "transliteration": "Dhairyashaali hrudayagalu prapanchavannu badalaayisuttave."},
    {"english": "Courage grows with use.", "native": "ಧೈರ್ಯ ಬಳಸಿದಷ್ಟು ಬೆಳೆಯುತ್ತದೆ.", "transliteration": "Dhairya baLasidastu beLeyuttade."},
    {"english": "Be kind to everyone you meet.", "native": "ನೀವು ಭೇಟಿಯಾಗುವ ಪ್ರತಿಯೊಬ್ಬರಿಗೂ ದಯೆ ತೋರಿಸಿ.", "transliteration": "Neevu bhetiyaagu pratiyobborigoo daye toorisi."},
    {"english": "Kindness costs nothing, means everything.", "native": "ದಯೆಗೆ ಬೆಲೆಯಿಲ್ಲ, ಅದು ಎಲ್ಲವನ್ನೂ ಅರ್ಥ ಮಾಡುತ್ತದೆ.", "transliteration": "Dayege belyilla, adu ellavannoo artha maaduttade."},
    {"english": "A kind word warms the heart.", "native": "ದಯೆಯ ಮಾತು ಹೃದಯವನ್ನು ಬೆಚ್ಚಗಾಗಿಸುತ್ತದೆ.", "transliteration": "Dayeya maathu hrudayavannu bechchagaagisuttade."},
    {"english": "Spread kindness wherever you go.", "native": "ಎಲ್ಲಿಗೆ ಹೋದರೂ ದಯೆಯನ್ನು ಹರಡಿ.", "transliteration": "Ellige hodaroo dayeyannu haradi."},
    {"english": "Kindness makes the world better.", "native": "ದಯೆ ಪ್ರಪಂಚವನ್ನು ಉತ್ತಮಗೊಳಿಸುತ್ತದೆ.", "transliteration": "Daye prapanchavannu uttamagoLisuttade."},
    {"english": "Good things come to those who wait.", "native": "ಕಾಯುವವರಿಗೆ ಒಳ್ಳೆಯ ವಿಷಯಗಳು ಬರುತ್ತವೆ.", "transliteration": "Kaayuvarige oL Leya vishayagalu baruttave."},
    {"english": "Patience is a virtue.", "native": "ತಾಳ್ಮೆಯು ಒಂದು ಗುಣ.", "transliteration": "TaaLmeyu ondu guna."},
    {"english": "Take your time, don't rush.", "native": "ನಿಮ್ಮ ಸಮಯ ತೆಗೆದುಕೊಳ್ಳಿ, ಅವಸರಪಡಬೇಡಿ.", "transliteration": "Nimma samaya tegedukoLLi, avarsarapadabedi."},
    {"english": "Patience brings peace of mind.", "native": "ತಾಳ್ಮೆ ಮನಸ್ಸಿಗೆ ಶಾಂತಿ ತರುತ್ತದೆ.", "transliteration": "TaaLme manassige shaanti taruttade."},
    {"english": "Wait patiently, trust the process.", "native": "ತಾಳ್ಮೆಯಿಂದ ಕಾಯಿರಿ, ಪ್ರಕ್ರಿಯೆಯನ್ನು ನಂಬಿ.", "transliteration": "TaaLmeyinda kaayiri, prakriyeyannu nambi."},
    {"english": "Forgive and set yourself free.", "native": "ಕ್ಷಮಿಸಿ, ನಿಮ್ಮನ್ನು ವಿಮುಕ್ತಗೊಳಿಸಿ.", "transliteration": "Kshamisi, nimmanne vimuktagoLisi."},
    {"english": "Forgiveness is a gift to yourself.", "native": "ಕ್ಷಮಾಪಣೆ ನಿಮಗೆ ನೀವೇ ಕೊಟ್ಟ ಕೊಡುಗೆ.", "transliteration": "Kshamaapane nimage neeve kotta koduge."},
    {"english": "Let go of grudges, find peace.", "native": "ಅಸಹ್ಯವನ್ನು ಬಿಡಿ, ಶಾಂತಿ ಹುಡುಕಿ.", "transliteration": "Asahyavannu bidi, shaanti huduki."},
    {"english": "To err is human, to forgive divine.", "native": "ತಪ್ಪು ಮಾಡುವುದು ಮಾನವ ಸಹಜ, ಕ್ಷಮಿಸುವುದು ದೈವಿಕ.", "transliteration": "Tappu maaduvudu maanava sahaja, kshamisuvudu daivika."},
    {"english": "Forgiveness heals all wounds.", "native": "ಕ್ಷಮಾಪಣೆ ಎಲ್ಲ ಗಾಯಗಳನ್ನು ಗುಣಪಡಿಸುತ್ತದೆ.", "transliteration": "Kshamaapane ella gaayagalannu gunapadisuttade."},
    {"english": "You are stronger than you know.", "native": "ನೀವು ತಿಳಿದುದಕ್ಕಿಂತ ಬಲಶಾಲಿಯಾಗಿದ್ದೀರಿ.", "transliteration": "Neevu tiLidudakkinta balashaaliyaagiddiri."},
    {"english": "Strength comes from within.", "native": "ಬಲ ಒಳಗಿಂದ ಬರುತ್ತದೆ.", "transliteration": "Bala oLagina baruttade."},
    {"english": "Your struggles develop your strength.", "native": "ನಿಮ್ಮ ಹೋರಾಟಗಳು ನಿಮ್ಮ ಬಲವನ್ನು ಬೆಳೆಸುತ್ತವೆ.", "transliteration": "Nimma horaatagalu nimma balavannu beLusuttave."},
    {"english": "Be strong, stay steady.", "native": "ಬಲವಾಗಿರಿ, ಸ್ಥಿರವಾಗಿರಿ.", "transliteration": "Balavaagiri, sthiravaagiri."},
    {"english": "Inner strength conquers all.", "native": "ಆಂತರ್ಯದ ಬಲ ಎಲ್ಲವನ್ನೂ ಗೆಲ್ಲುತ್ತದೆ.", "transliteration": "Aantharyada bala ellavannoo geLuttade."},
    {"english": "Find joy in every moment.", "native": "ಪ್ರತಿ ಕ್ಷಣದಲ್ಲಿ ಆನಂದ ಹುಡುಕಿ.", "transliteration": "Prati kshaNadaLLi aananda huduki."},
    {"english": "Joy is contagious, spread it.", "native": "ಆನಂದ ಸಾಂಕ್ರಾಮಿಕ, ಹರಡಿ.", "transliteration": "Aananda saankraamika, haradi."},
    {"english": "Let joy fill your heart today.", "native": "ಇಂದು ಆನಂದ ನಿಮ್ಮ ಹೃದಯ ತುಂಬಲಿ.", "transliteration": "Indu aananda nimma hrudaya tumbali."},
    {"english": "Choose joy over worry.", "native": "ಚಿಂತೆಗಿಂತ ಆನಂದವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ.", "transliteration": "Chinteginta aanandavannu aayake maadi."},
    {"english": "Joy is the simplest form of gratitude.", "native": "ಆನಂದವು ಕೃತಜ್ಞತೆಯ ಸರಳ ರೂಪ.", "transliteration": "Aanandavu krutajnateya sarala roopa."},
    {"english": "Find balance in your life.", "native": "ನಿಮ್ಮ ಜೀವನದಲ್ಲಿ ಸಮತೋಲನ ಹುಡುಕಿ.", "transliteration": "Nimma jevanadalli samatoLana huduki."},
    {"english": "Balance is the key to happiness.", "native": "ಸಮತೋಲನವೇ ಸಂತೋಷಕ್ಕೆ ಮಾರ್ಗ.", "transliteration": "Samato Lanave santoshakke maarga."},
    {"english": "Work hard, rest well.", "native": "ಗಟ್ಟಿಯಾಗಿ ಕೆಲಸ ಮಾಡಿ, ಚೆನ್ನಾಗಿ ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ.", "transliteration": "Gattiyaagi kelasa maadi, chennaagi vishraanti tegedukoLLi."},
    {"english": "A balanced life is a peaceful life.", "native": "ಸಮತೋಲಿತ ಜೀವನವೇ ಶಾಂತಿಮಯ ಜೀವನ.", "transliteration": "SamatoLita jevanave shaantimaya jevana."},
    {"english": "Prioritize what matters most.", "native": "ಅತ್ಯಂತ ಮುಖ್ಯವಾದುದಕ್ಕೆ ಆದ್ಯತೆ ನೀಡಿ.", "transliteration": "Athyanta mukhyavaadudake aadyate needi."},
    {"english": "Growth happens outside your comfort zone.", "native": "ಬೆಳವಣಿಗೆ ನಿಮ್ಮ ಆರಾಮ ವಲಯದ ಹೊರಗೆ ಆಗುತ್ತದೆ.", "transliteration": "BeLavaNige nimma aaraama valayada horage aaguttade."},
    {"english": "Embrace change, grow stronger.", "native": "ಬದಲಾವಣೆಯನ್ನು ಸ್ವಾಗತಿಸಿ, ಬಲವಾಗಿ ಬೆಳೆಯಿರಿ.", "transliteration": "Badalaavaneyannu svaagatisi, balavaagi beLeyiri."},
    {"english": "Every challenge is a growth opportunity.", "native": "ಪ್ರತಿ ಸವಾಲೂ ಬೆಳವಣಿಗೆಗೆ ಅವಕಾಶ.", "transliteration": "Prathi savaalooo beLavaNigege avakaasha."},
    {"english": "Grow through what you go through.", "native": "ನಿಮ್ಮ ಅನುಭವಗಳ ಮೂಲಕ ಬೆಳೆಯಿರಿ.", "transliteration": "Nimma anubhavagala moolaka beLeyiri."},
    {"english": "Personal growth is a lifelong journey.", "native": "ವೈಯಕ್ತಿಕ ಬೆಳವಣಿಗೆ ಜೀವನಪರ ಪ್ರಯಾಣ.", "transliteration": "Vaiyaktika beLavaNigejeevanapara prayaana."},
    {"english": "Find your purpose, live it.", "native": "ನಿಮ್ಮ ಉದ್ದೇಶವನ್ನು ಕಂಡುಕೊಳ್ಳಿ, ಅದನ್ನು ಜೀವಿಸಿ.", "transliteration": "Nimma udeshavannu kaNDukoLLi, adannu jevisi."},
    {"english": "Purpose gives life meaning.", "native": "ಉದ್ದೇಶವು ಜೀವನಕ್ಕೆ ಅರ್ಥ ನೀಡುತ್ತದೆ.", "transliteration": "Uddeshavu jevanakke artha needuttade."},
    {"english": "Live with purpose and passion.", "native": "ಉದ್ದೇಶ ಮತ್ತು ಆಸಕ್ತಿಯೊಂದಿಗೆ ಜೀವಿಸಿ.", "transliteration": "UdDesha mattu aasaktiyondige jevisi."},
    {"english": "Your purpose is your calling.", "native": "ನಿಮ್ಮ ಉದ್ದೇಶವೇ ನಿಮ್ಮ ಕರೆ.", "transliteration": "Nimma udeshavee nimma kare."},
    {"english": "Discover purpose in everyday moments.", "native": "ದೈನಂದಿನ ಕ್ಷಣಗಳಲ್ಲಿ ಉದ್ದೇಶವನ್ನು ಕಂಡುಕೊಳ್ಳಿ.", "transliteration": "Dainandina kshaNagaLiLLi udeshavannu kaNDukoLLi."},
    {"english": "Be present in this moment.", "native": "ಈ ಕ್ಷಣದಲ್ಲಿ ಇರಿ.", "transliteration": "Ee kshaNadaLLi iri."},
    {"english": "Mindfulness brings inner peace.", "native": "ಜಾಗೃತಿ ಆಂತರ್ಯದ ಶಾಂತಿ ತರುತ್ತದೆ.", "transliteration": "Jaagruthi aantharyada shaanti taruttade."},
    {"english": "Breathe deeply, stay mindful.", "native": "ಆಳವಾಗಿ ಉಸಿರಾಡಿ, ಜಾಗರೂಕರಾಗಿರಿ.", "transliteration": "AaLavaagi usiraadi, jaagarookaraagiri."},
    {"english": "The present moment is all we have.", "native": "ಪ್ರಸ್ತುತ ಕ್ಷಣವೇ ನಮ್ಮಲ್ಲಿರುವುದೆಲ್ಲ.", "transliteration": "Prasthutha kshaNavee nammalliruvudella."},
    {"english": "Practice mindfulness daily.", "native": "ಪ್ರತಿದಿನ ಜಾಗೃತಿ ಅಭ್ಯಾಸ ಮಾಡಿ.", "transliteration": "Pratidina jaagruthi abhyaasa maadi."},
]
# ==== FALLBACK PHRASES END ====


def _load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_phrase_history():
    data = _load_json(PHRASE_HISTORY_FILE, {"phrases": [], "last_updated": None})
    data.setdefault("phrases", [])
    return data


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    _save_json(PHRASE_HISTORY_FILE, data)


def is_phrase_used(english):
    english_lower = english.lower().strip()
    for p in load_phrase_history()["phrases"]:
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def _history_native(p):
    for key in (PHRASE_KEY, "vietnamese", "native", "translation", "target"):
        value = p.get(key)
        if value:
            return str(value)
    return ""


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            PHRASE_KEY: phrase["native"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat(),
        })
    save_phrase_history(history)
    print(f"[content] Saved {len(phrases)} phrases (history total: {len(history['phrases'])})")


def get_available_category():
    data = _load_json(RECENT_CATEGORIES_FILE, {"recent_categories": [], "last_updated": None})
    recent = data.get("recent_categories", [])
    available = [c for c in CATEGORIES if c not in recent]
    if not available:
        recent = recent[-5:]
        available = [c for c in CATEGORIES if c not in recent]
        print("[rotation] Reset recent categories")
    selected = random.choice(available)
    recent.append(selected)
    data["recent_categories"] = recent[-MAX_RECENT_CATEGORIES:]
    data["last_updated"] = datetime.now().isoformat()
    _save_json(RECENT_CATEGORIES_FILE, data)
    print(f"[rotation] Category: {selected} ({len(available)} available)")
    return selected


def _normalize_phrase(item):
    if not isinstance(item, dict):
        return None
    english = str(item.get("english", "")).strip()
    native = str(
        item.get(PHRASE_KEY)
        or item.get("native")
        or item.get("vietnamese")
        or item.get("translation")
        or ""
    ).strip()
    translit = str(item.get("transliteration") or item.get("romanization") or item.get("romaji") or "").strip()
    if not english or not native:
        return None
    if len(english.split()) > 16:
        return None
    if "/" in native or "|" in native:
        native = native.split("/")[0].split("|")[0].strip()
    return {
        "english": english.replace("  ", " ").strip(),
        "native": native.strip(),
        "transliteration": translit.strip().strip("[]"),
    }


def _history_keys(history):
    used_en = set()
    used_nat = set()
    for p in history.get("phrases", []):
        en = str(p.get("english", "")).lower().strip()
        nat = _history_native(p).lower().strip()
        if en:
            used_en.add(en)
        if nat:
            used_nat.add(nat)
    return used_en, used_nat


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    history = load_phrase_history()
    used_en, used_nat = _history_keys(history)
    recent_english = [
        p["english"] for p in history["phrases"] if p.get("category") == category_english
    ][-30:]

    models = [config.AI_MODEL]
    if "gemini-fast" not in models:
        models.append("gemini-fast")

    if config.POLLINATIONS_API_KEY:
        for attempt in range(5):
            model = models[0] if attempt < 3 else models[-1]
            try:
                phrases = _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model)
                unique = []
                for item in phrases:
                    p = _normalize_phrase(item)
                    if not p:
                        continue
                    key_en = p["english"].lower().strip()
                    key_nat = p["native"].lower().strip()
                    if key_en in used_en or key_nat in used_nat:
                        continue
                    if any(key_en == u["english"].lower().strip() for u in unique):
                        continue
                    used_en.add(key_en)
                    used_nat.add(key_nat)
                    unique.append(p)
                    if len(unique) >= num_phrases:
                        break
                if len(unique) >= num_phrases:
                    add_phrases_to_history(unique[:num_phrases], category_english)
                    return unique[:num_phrases]
                print(f"[content] Attempt {attempt + 1}: only {len(unique)} fresh phrases (need {num_phrases})")
            except Exception as exc:  # noqa: BLE001 - network boundary
                print(f"[content] Attempt {attempt + 1} failed ({model}): {exc}")
            time.sleep(1.5 * (attempt + 1))
    else:
        print("[content] No POLLINATIONS_API_KEY, using fallback phrases")

    fresh_fallback = []
    for p in FALLBACK_PHRASES:
        if p["english"].lower().strip() in used_en or p["native"].lower().strip() in used_nat:
            continue
        fresh_fallback.append(p)
    if not fresh_fallback:
        raise RuntimeError("Phrase API unavailable and no unused fallback phrases left; refusing to reuse phrases")
    chosen = fresh_fallback[:num_phrases]
    if len(chosen) < num_phrases:
        print(f"[content] Only {len(chosen)} fresh fallback phrases; building a shorter lesson")
    add_phrases_to_history(chosen, category_english)
    return chosen


def _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model=None):
    avoid = ""
    if recent_english:
        avoid = "\nDo NOT reuse any of these phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

    prompt = f"""Create {num_phrases * 6} unique {category_english} phrases for English speakers learning {LANGUAGE_NAME}.
{avoid}

Rules:
1. Keep every phrase short and natural (4-11 words in English).
2. Use natural commas for TTS breathing pauses.
3. Each phrase must be speakable in 2-4 seconds.
4. Write clean {LANGUAGE_NAME} in {NATIVE_NAME} with correct accents and orthography. One translation only, no slashes.
5. Transliteration is a friendly Roman-script pronunciation guide for English speakers (not IPA).
6. Vary the sentence patterns and emotions. No duplicates.
7. Phrases must feel like real everyday language, not textbook filler.

Return ONLY a JSON array:
[{{"english": "...", "native": "...", "transliteration": "..."}}]"""

    response = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.POLLINATIONS_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model or config.AI_MODEL,
            "messages": [
                {"role": "system", "content": f"You are a {LANGUAGE_NAME} teacher creating short, natural, varied bilingual phrases. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": min(0.95 + attempt * 0.02, 1.0),
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()

    start = content.find("[")
    end = content.rfind("]")
    if start >= 0 and end > start:
        content = content[start:end + 1]

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("AI did not return a JSON array")
    return data
