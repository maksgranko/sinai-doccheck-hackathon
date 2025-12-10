"""
Переиспользуемые компоненты дизайна
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
try:
    from design.modern_theme import *
except ImportError:
    from design.theme import *


class Card(BoxLayout):
    """Карточка с тенью и скругленными углами - улучшенный дизайн с градиентами"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = CARD_PADDING
        self.spacing = CARD_SPACING
        self.size_hint_y = None
        
        with self.canvas.before:
            # Многослойная тень для глубины
            Color(*SHADOW_COLOR)
            self.shadow1 = RoundedRectangle(
                size=(self.size[0] - dp(1), self.size[1] - dp(1)),
                pos=(self.pos[0] + dp(0.5), self.pos[1] - dp(2)),
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
            Color(0, 0, 0, 0.04)
            self.shadow2 = RoundedRectangle(
                size=(self.size[0] - dp(2), self.size[1] - dp(2)),
                pos=(self.pos[0] + dp(1), self.pos[1] - dp(1)),
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
            # Основной фон
            Color(*CARD_COLOR)
            self.bg = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
            # Тонкая граница с градиентом
            Color(*BORDER_COLOR)
            self.border = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
        
        self.bind(size=self._update_bg, pos=self._update_bg)
    
    def _update_bg(self, *args):
        if hasattr(self, 'bg'):
            self.bg.size = self.size
            self.bg.pos = self.pos
        if hasattr(self, 'shadow1'):
            self.shadow1.size = (self.size[0] - dp(1), self.size[1] - dp(1))
            self.shadow1.pos = (self.pos[0] + dp(0.5), self.pos[1] - dp(2))
        if hasattr(self, 'shadow2'):
            self.shadow2.size = (self.size[0] - dp(2), self.size[1] - dp(2))
            self.shadow2.pos = (self.pos[0] + dp(1), self.pos[1] - dp(1))
        if hasattr(self, 'border'):
            self.border.size = self.size
            self.border.pos = self.pos


class PrimaryButton(Button):
    """Основная кнопка с современным дизайном и эффектом нажатия"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = BUTTON_HEIGHT
        self.font_size = FONT_SIZE_BUTTON
        self.bold = True
        self.background_color = (0, 0, 0, 0)  # Прозрачный фон для кастомного
        self.color = (1, 1, 1, 1)  # Белый текст
        
        with self.canvas.before:
            # Тень кнопки
            Color(0, 0, 0, 0.1)
            self.shadow = RoundedRectangle(
                size=(self.size[0], self.size[1] - dp(2)),
                pos=(self.pos[0], self.pos[1] - dp(1)),
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
            # Основной фон
            Color(*PRIMARY_COLOR)
            self.bg = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
        
        self.bind(size=self._update_bg, pos=self._update_bg)
        self.bind(on_press=self._on_press, on_release=self._on_release)
    
    def _update_bg(self, *args):
        if hasattr(self, 'bg'):
            self.bg.size = self.size
            self.bg.pos = self.pos
        if hasattr(self, 'shadow'):
            self.shadow.size = (self.size[0], self.size[1] - dp(2))
            self.shadow.pos = (self.pos[0], self.pos[1] - dp(1))
    
    def _on_press(self, instance):
        """Анимация нажатия"""
        from kivy.animation import Animation
        anim = Animation(size=(self.size[0] * 0.98, self.size[1] * 0.98), duration=0.1)
        anim.start(self)
    
    def _on_release(self, instance):
        """Анимация отпускания"""
        from kivy.animation import Animation
        anim = Animation(size=(self.size[0] / 0.98, self.size[1] / 0.98), duration=0.1)
        anim.start(self)


class SecondaryButton(Button):
    """Вторичная кнопка"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = BUTTON_HEIGHT
        self.font_size = FONT_SIZE_BUTTON
        self.background_color = (0, 0, 0, 0)  # Прозрачный фон для кастомного
        self.color = TEXT_PRIMARY
        
        with self.canvas.before:
            Color(*BORDER_COLOR)
            self.bg = RoundedRectangle(
                size=self.size,
                pos=self.pos,
                radius=[BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS, BORDER_RADIUS]
            )
        
        self.bind(size=self._update_bg, pos=self._update_bg)
    
    def _update_bg(self, *args):
        if hasattr(self, 'bg'):
            self.bg.size = self.size
            self.bg.pos = self.pos


class StyledTextInput(TextInput):
    """Стилизованное поле ввода - упрощенное для совместимости"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = INPUT_HEIGHT
        self.font_size = FONT_SIZE_BODY
        # Используем стандартные настройки для лучшей совместимости
        self.multiline = False
        self.background_color = (1, 1, 1, 1)  # Белый фон
        self.foreground_color = TEXT_PRIMARY
        # Простой padding для совместимости
        try:
            self.padding_x = dp(12)
            self.padding_y = dp(8)
        except:
            pass


class TitleLabel(Label):
    """Заголовок"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = FONT_SIZE_H1
        self.bold = True
        self.color = TEXT_PRIMARY
        self.text_size = (None, None)  # Адаптивный размер текста
        self.valign = 'middle'
        self.halign = 'left'


class SubtitleLabel(Label):
    """Подзаголовок"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = FONT_SIZE_H2
        self.color = TEXT_SECONDARY
        self.text_size = (None, None)  # Адаптивный размер текста
        self.valign = 'middle'
        self.halign = 'left'


class BodyLabel(Label):
    """Основной текст"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = FONT_SIZE_BODY
        self.color = TEXT_PRIMARY
        self.text_size = (None, None)  # Адаптивный размер текста
        self.valign = 'middle'
        self.halign = 'left'


class CaptionLabel(Label):
    """Подпись"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = FONT_SIZE_CAPTION
        self.color = TEXT_SECONDARY
        self.text_size = (None, None)  # Адаптивный размер текста
        self.valign = 'middle'
        self.halign = 'left'

