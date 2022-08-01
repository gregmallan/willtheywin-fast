def normalize_str(value: str) -> str:
    return ' '.join(word.strip() for word in value.strip().split(' ') if word).lower()
