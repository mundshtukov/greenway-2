"""Заглушка для модуля imghdr для совместимости с Python 3.13+"""

def what(file):
    """Простая заглушка для функции what из imghdr"""
    return None

def test_jpeg(h, f):
    """JPEG тест"""
    if h.startswith(b'\xff\xd8'):
        return 'jpeg'

def test_png(h, f):
    """PNG тест"""
    if h.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'png'

def test_gif(h, f):
    """GIF тест"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def test_webp(h, f):
    """WebP тест"""
    if h.startswith(b'RIFF') and h[8:12] == b'WEBP':
        return 'webp'

# Список тестов
tests = [test_jpeg, test_png, test_gif, test_webp]
