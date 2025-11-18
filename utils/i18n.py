"""
Internationalization utility for loading translations
"""
import json
import os

# Get the directory of this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')

_translations = {}


def load_translations():
    """Load all translation files"""
    global _translations
    for lang in ['en', 'pt']:
        file_path = os.path.join(LOCALES_DIR, f'{lang}.json')
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                _translations[lang] = json.load(f)


def get_text(key, language='en', default=None):
    """Get translated text for a key"""
    if not _translations:
        load_translations()
    
    if language not in _translations:
        language = 'en'
    
    return _translations.get(language, {}).get(key, default or key)


# Load translations on import
load_translations()

