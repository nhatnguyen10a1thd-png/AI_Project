MOJIBAKE_MARKERS = ("Ã", "Â", "â", "Ä", "Æ", "áº", "á»", "ðŸ")


def repair_text(text):
    """Repair UTF-8 text that was accidentally decoded as Latin-1/CP1252."""
    if not isinstance(text, str):
        return text

    value = text
    for _ in range(2):
        current_score = sum(value.count(marker) for marker in MOJIBAKE_MARKERS)
        if current_score == 0:
            break
        candidates = []
        for encoding in ("latin1", "cp1252"):
            try:
                candidate = value.encode(encoding).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            score = sum(candidate.count(marker) for marker in MOJIBAKE_MARKERS)
            candidates.append((score, candidate))
        if not candidates:
            break
        score, candidate = min(candidates, key=lambda item: item[0])
        if score >= current_score:
            break
        value = candidate
    return value


class Font:
    """Small pygame Font proxy that repairs broken source strings before rendering."""

    def __init__(self, pygame_font):
        self._font = pygame_font

    def render(self, text, antialias, color, background=None):
        text = repair_text(text)
        if background is None:
            return self._font.render(text, antialias, color)
        return self._font.render(text, antialias, color, background)

    def size(self, text):
        return self._font.size(repair_text(text))

    def __getattr__(self, name):
        return getattr(self._font, name)
