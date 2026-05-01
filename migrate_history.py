"""
Migrate phrase history from Telugu to Kannada format
Converts 'telugu' -> 'kannada'
Also adds a note that these are legacy Telugu phrases
"""
import json
from pathlib import Path

HISTORY_FILE = Path("output/history/all_generated_phrases.json")

if HISTORY_FILE.exists():
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    updated_count = 0
    for phrase in data.get("phrases", []):
        # Convert Telugu fields to Kannada fields
        if "telugu" in phrase:
            phrase["kannada"] = phrase.pop("telugu")
            phrase["is_legacy_telugu"] = True  # Mark as legacy
            updated_count += 1
    
    # Save updated history
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Migrated {updated_count} phrases from Telugu to Kannada format")
    print(f"   - 'telugu' → 'kannada'")
    print(f"   - Legacy Telugu phrases marked with 'is_legacy_telugu: True'")
    print(f"\n💡 These legacy phrases won't block new Kannada content generation")
else:
    print("No phrase history found to migrate")
