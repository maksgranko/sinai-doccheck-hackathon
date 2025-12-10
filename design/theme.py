"""
Цветовая схема и тема приложения
"""
from kivy.metrics import dp

# Основные цвета (Современный Material Design)
PRIMARY_COLOR = (0.26, 0.52, 0.96, 1.0)  # Яркий синий
PRIMARY_DARK = (0.20, 0.40, 0.85, 1.0)
PRIMARY_LIGHT = (0.45, 0.65, 0.98, 1.0)

SECONDARY_COLOR = (0.3, 0.7, 0.5, 1.0)  # Зеленый
ACCENT_COLOR = (1.0, 0.6, 0.0, 1.0)  # Оранжевый

# Фон (более контрастный)
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

# Границы и тени
BORDER_COLOR = (0.88, 0.88, 0.88, 1.0)
SHADOW_COLOR = (0.0, 0.0, 0.0, 0.08)

# Размеры (оптимизированные для мобильных)
CARD_PADDING = dp(24)
CARD_SPACING = dp(18)
BUTTON_HEIGHT = dp(54)
INPUT_HEIGHT = dp(54)
BORDER_RADIUS = dp(14)

# Типографика (читаемая)
FONT_SIZE_H1 = dp(24)  # Заголовок
FONT_SIZE_H2 = dp(18)  # Подзаголовок
FONT_SIZE_BODY = dp(15)  # Основной текст
FONT_SIZE_CAPTION = dp(13)  # Подпись
FONT_SIZE_BUTTON = dp(15)  # Кнопка

# Анимации
ANIMATION_DURATION = 0.3

