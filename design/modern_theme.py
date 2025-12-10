"""
Современная цветовая схема - чистый и профессиональный дизайн
"""
from kivy.metrics import dp

# Основные цвета (Современный Material Design 3 с градиентами)
PRIMARY_COLOR = (0.12, 0.47, 0.90, 1.0)  # Яркий синий
PRIMARY_DARK = (0.08, 0.35, 0.75, 1.0)
PRIMARY_LIGHT = (0.40, 0.65, 0.95, 1.0)
PRIMARY_GRADIENT_START = (0.12, 0.47, 0.90, 1.0)
PRIMARY_GRADIENT_END = (0.20, 0.55, 0.95, 1.0)

# Акцентные цвета для фич
ACCENT_EXPORT = (0.18, 0.75, 0.35, 1.0)  # Зеленый для экспорта
ACCENT_STATS = (0.65, 0.35, 0.95, 1.0)  # Фиолетовый для статистики
ACCENT_OFFLINE = (1.0, 0.65, 0.0, 1.0)  # Оранжевый для офлайн

# Фон
BACKGROUND_COLOR = (0.96, 0.97, 0.98, 1.0)  # Очень светло-серый
SURFACE_COLOR = (1.0, 1.0, 1.0, 1.0)  # Чистый белый
CARD_COLOR = (1.0, 1.0, 1.0, 1.0)

# Текст (высокий контраст)
TEXT_PRIMARY = (0.08, 0.08, 0.08, 1.0)  # Почти черный
TEXT_SECONDARY = (0.45, 0.45, 0.45, 1.0)  # Серый
TEXT_HINT = (0.70, 0.70, 0.70, 1.0)  # Светло-серый

# Статусы (яркие и понятные)
STATUS_VALID = (0.18, 0.75, 0.35, 1.0)  # Зеленый
STATUS_WARNING = (1.0, 0.65, 0.0, 1.0)  # Оранжевый
STATUS_INVALID = (0.95, 0.25, 0.25, 1.0)  # Красный
STATUS_NEUTRAL = (0.65, 0.65, 0.65, 1.0)  # Серый

# Границы
BORDER_COLOR = (0.88, 0.88, 0.88, 1.0)
SHADOW_COLOR = (0.0, 0.0, 0.0, 0.08)
SHADOW_COLOR_DARK = (0.0, 0.0, 0.0, 0.15)  # Более темная тень для карточек

# Анимации
ANIMATION_DURATION = 0.3
ANIMATION_DURATION_SLOW = 0.5

# Размеры (оптимизированные для мобильных - компактные)
CARD_PADDING = dp(12)
CARD_SPACING = dp(8)
BUTTON_HEIGHT = dp(40)
INPUT_HEIGHT = dp(40)
BORDER_RADIUS = dp(8)

# Типографика (компактная для мобильных)
FONT_SIZE_H1 = dp(18)
FONT_SIZE_H2 = dp(16)
FONT_SIZE_BODY = dp(14)
FONT_SIZE_CAPTION = dp(12)
FONT_SIZE_BUTTON = dp(14)


