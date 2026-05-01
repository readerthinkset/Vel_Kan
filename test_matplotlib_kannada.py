import sys
sys.stdout.reconfigure(encoding="utf-8")

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pathlib import Path

# Use relative path for fonts
fonts_dir = Path(__file__).parent / 'fonts'

# Test if matplotlib can render Kannada correctly
test_phrases = [
    'ಒಂದು, ಎರಡು, ಮೂರು',
    'ನಮಸ್ಕಾರ',
    'ಕ್ಷಮಿಸಿ',
    'ಹಠಧಾರಣೆ',
    'ಶುಭೋದಯ',
]

# Find Kannada fonts
fonts_to_test = [
    ('NotoSansKannada-Bold', str(fonts_dir / 'NotoSansKannada-Bold.ttf')),
    ('NotoSansKannada-Regular', str(fonts_dir / 'NotoSansKannada-Regular.ttf')),
    ('Nirmala', 'C:/Windows/Fonts/Nirmala.ttc'),
    ('Noto Sans (system)', None),  # Let matplotlib find it
]

for name, path in fonts_to_test:
    try:
        if path:
            prop = fm.FontProperties(fname=path, size=40)
        else:
            prop = fm.FontProperties(family='Noto Sans', size=40)

        fig, ax = plt.subplots(figsize=(10.8, 1.5), dpi=100)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        fig.patch.set_facecolor('#141428')

        text = ' | '.join(test_phrases)
        ax.text(0.5, 0.5, text, fontproperties=prop, color='yellow',
                ha='center', va='center')

        out_path = f'output/test_matplotlib_{name.replace(" ", "_").replace("(", "").replace(")", "")}.png'
        # Ensure output directory exists
        Path('output').mkdir(exist_ok=True)
        fig.savefig(out_path, dpi=100, bbox_inches='tight', facecolor='#141428')
        plt.close()
        print(f'{name}: saved to {out_path}')
    except Exception as e:
        print(f'{name}: ERROR: {e}')

print('\nDone - check the images in output/ folder')