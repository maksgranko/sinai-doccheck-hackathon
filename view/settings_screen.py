"""
Экран настроек
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

from security.pin_storage import PinStorage
try:
    from design.modern_theme import PRIMARY_COLOR, BUTTON_HEIGHT
except ImportError:
    from design.theme import PRIMARY_COLOR, BUTTON_HEIGHT
from design.components import PrimaryButton, SecondaryButton, TitleLabel, Card


class SettingsScreen(Screen):
    """Экран настроек приложения"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin_storage = PinStorage()
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        layout = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(8)],
            spacing=dp(16)
        )
        
        # Заголовок с фоном
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(56),
            padding=[dp(16), dp(8)],
            spacing=dp(12)
        )
        
        with header.canvas.before:
            Color(*PRIMARY_COLOR)
            self.header_bg = Rectangle(size=header.size, pos=header.pos)
        
        def update_header_bg(instance, value):
            if hasattr(self, 'header_bg'):
                self.header_bg.size = instance.size
                self.header_bg.pos = instance.pos
        
        header.bind(size=update_header_bg, pos=update_header_bg)
        
        title = TitleLabel(
            text='Настройки',
            size_hint_x=0.7,
            color=(1, 1, 1, 1),  # Белый текст
            text_size=(None, None)
        )
        title.bind(texture_size=title.setter('size'))
        
        back_button = SecondaryButton(
            text='Назад',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        back_button.color = (1, 1, 1, 1)
        
        header.add_widget(title)
        header.add_widget(back_button)
        layout.add_widget(header)
        
        # Карточка настроек
        settings_card = Card(
            size_hint_y=None,
            height=dp(120),
            spacing=dp(12)
        )
        
        # Кнопка очистки PIN
        clear_pin_button = PrimaryButton(
            text='Удалить сохраненный PIN',
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            on_press=self.clear_pin
        )
        
        settings_card.add_widget(clear_pin_button)
        layout.add_widget(settings_card)
        
        self.add_widget(layout)
    
    def _update_header(self, instance, value):
        """Обновление фона заголовка"""
        if hasattr(self, 'header_bg') and hasattr(instance, 'size') and hasattr(instance, 'pos'):
            self.header_bg.size = instance.size
            self.header_bg.pos = instance.pos
    
    def clear_pin(self, instance):
        """Очистка сохраненного PIN-кода"""
        if self.pin_storage.delete_pin():
            Logger.info("SettingsScreen: PIN-код удален")
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.manager.current = 'scanner'



