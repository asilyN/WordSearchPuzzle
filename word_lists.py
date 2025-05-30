"""
Word lists for different difficulty levels
"""

WORD_LISTS = {
    "easy": [
        "CAT", "DOG", "SUN", "RUN", "FUN", "BAT", "HAT", "CAR", "TOP", "CUP",
        "BOX", "FOX", "BED", "RED", "BIG", "PIG", "EGG", "BAG", "RAG", "TAG",
        "LOG", "HOG", "JOG", "BUG", "HUG", "RUG", "DIG", "FIG", "WIG", "ZIP",
        "TIP", "LIP", "HIP", "SIP", "DIP", "POP", "MOP", "HOP", "COP", "TOP",
        "NET", "PET", "SET", "WET", "GET", "LET", "BET", "JET", "MET", "VET"
    ],
    
    "medium": [
        "HOUSE", "WATER", "LIGHT", "WORLD", "MUSIC", "HAPPY", "SMILE", "DANCE", "PEACE", "DREAM",
        "OCEAN", "BEACH", "HEART", "MAGIC", "TOWER", "PLANT", "RIVER", "STONE", "CLOUD", "STORM",
        "BRAVE", "SMART", "QUICK", "FRESH", "SWEET", "CLEAR", "SHARP", "BRIGHT", "CLEAN", "SMOOTH",
        "FOREST", "ANIMAL", "FLOWER", "GARDEN", "WINDOW", "CASTLE", "BRIDGE", "ISLAND", "VALLEY", "MOUNTAIN",
        "PURPLE", "ORANGE", "YELLOW", "SILVER", "GOLDEN", "DIAMOND", "CRYSTAL", "MARBLE", "COPPER", "BRONZE"
    ],
    
    "hard": [
        "PYTHON", "ALGORITHM", "COMPUTER", "SOFTWARE", "HARDWARE", "INTERNET", "DATABASE", "SECURITY", "NETWORK", "PROTOCOL",
        "PROGRAMMING", "DEVELOPMENT", "ARTIFICIAL", "INTELLIGENCE", "MACHINE", "LEARNING", "BLOCKCHAIN", "ENCRYPTION", "CYBERSECURITY", "QUANTUM",
        "TECHNOLOGY", "INNOVATION", "SCIENTIFIC", "MATHEMATICS", "ENGINEERING", "ARCHITECTURE", "PHILOSOPHY", "PSYCHOLOGY", "SOCIOLOGY", "ANTHROPOLOGY",
        "EXTRAORDINARY", "REVOLUTIONARY", "MAGNIFICENT", "SPECTACULAR", "PHENOMENAL", "EXCEPTIONAL", "OUTSTANDING", "REMARKABLE", "INCREDIBLE", "WONDERFUL",
        "CHAMPIONSHIP", "COMPETITION", "TOURNAMENT", "ACHIEVEMENT", "PERFORMANCE", "EXCELLENCE", "LEADERSHIP", "INSPIRATION", "MOTIVATION", "DETERMINATION"
    ]
}

def get_words_by_difficulty(difficulty):
    """Get words for a specific difficulty level"""
    return WORD_LISTS.get(difficulty, WORD_LISTS["easy"])

def get_random_words(difficulty, count):
    """Get a random selection of words from a difficulty level"""
    import random
    words = get_words_by_difficulty(difficulty)
    return random.sample(words, min(count, len(words)))

def validate_word(word):
    """Validate that a word only contains letters"""
    return word.isalpha() and word.isupper()

def get_word_statistics():
    """Get statistics about the word lists"""
    stats = {}
    
    for difficulty, words in WORD_LISTS.items():
        stats[difficulty] = {
            'total_words': len(words),
            'min_length': min(len(word) for word in words),
            'max_length': max(len(word) for word in words),
            'avg_length': sum(len(word) for word in words) / len(words)
        }
    
    return stats

def search_words(query, difficulty=None):
    """Search for words containing a specific substring"""
    results = []
    
    if difficulty:
        word_lists = {difficulty: WORD_LISTS[difficulty]}
    else:
        word_lists = WORD_LISTS
    
    query_upper = query.upper()
    
    for diff_level, words in word_lists.items():
        for word in words:
            if query_upper in word:
                results.append({
                    'word': word,
                    'difficulty': diff_level,
                    'length': len(word)
                })
    
    return results

def get_words_by_length(length, difficulty=None):
    """Get words of a specific length"""
    results = []
    
    if difficulty:
        word_lists = {difficulty: WORD_LISTS[difficulty]}
    else:
        word_lists = WORD_LISTS
    
    for diff_level, words in word_lists.items():
        for word in words:
            if len(word) == length:
                results.append({
                    'word': word,
                    'difficulty': diff_level
                })
    
    return results

def add_custom_word(word, difficulty):
    """Add a custom word to a difficulty level (runtime only)"""
    if difficulty in WORD_LISTS and validate_word(word):
        WORD_LISTS[difficulty].append(word)
        return True
    return False

def get_difficulty_for_word(word):
    """Find which difficulty level(s) contain a specific word"""
    word_upper = word.upper()
    difficulties = []
    
    for difficulty, words in WORD_LISTS.items():
        if word_upper in words:
            difficulties.append(difficulty)
    
    return difficulties
