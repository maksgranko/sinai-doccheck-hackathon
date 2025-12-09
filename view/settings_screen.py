"""
Экран настроек
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.logger import Logger
from kivy.metrics import dp

from security.pin_storage import PinStorage


class SettingsScreen(Screen):
    """Экран настроек приложения"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin_storage = PinStorage()
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Заголовок
        title = Label(
            text='Настройки',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        layout.add_widget(title)
        
        # Кнопка очистки PIN
        clear_pin_button = Button(
            text='Удалить сохраненный PIN',
            size_hint_y=None,
            height=dp(50),
            on_press=self.clear_pin
        )
        layout.add_widget(clear_pin_button)
        
        # Кнопка назад
        back_button = Button(
            text='Назад',
            size_hint_y=None,
            height=dp(50),
            on_press=self.go_back
        )
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def clear_pin(self, instance):
        """Очистка сохраненного PIN-кода"""
        if self.pin_storage.delete_pin():
            Logger.info("SettingsScreen: PIN-код удален")
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.manager.current = 'scanner'



