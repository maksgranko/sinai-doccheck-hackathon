"""
Экран входа/настройки
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from kivy.metrics import dp

from security.biometric_auth import BiometricAuth
from security.pin_storage import PinStorage


class LoginScreen(Screen):
    """Экран входа в приложение"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.biometric_auth = BiometricAuth()
        self.pin_storage = PinStorage()
        
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        layout = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Заголовок
        title = Label(
            text='Верификатор документов',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(24),
            bold=True
        )
        layout.add_widget(title)
        
        subtitle = Label(
            text='Проверка подлинности электронных документов',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14)
        )
        layout.add_widget(subtitle)
        
        # Поле для PIN-кода (опционально)
        pin_label = Label(
            text='PIN-код (опционально):',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12)
        )
        layout.add_widget(pin_label)
        
        self.pin_input = TextInput(
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16)
        )
        layout.add_widget(self.pin_input)
        
        # Кнопка входа
        login_button = Button(
            text='Войти',
            size_hint_y=None,
            height=dp(50),
            on_press=self.login
        )
        layout.add_widget(login_button)
        
        # Кнопка биометрической аутентификации
        if self.biometric_auth.is_available:
            bio_button = Button(
                text='Войти с биометрией',
                size_hint_y=None,
                height=dp(50),
                on_press=self.login_with_biometric
            )
            layout.add_widget(bio_button)
        
        # Информация
        info_label = Label(
            text='Для начала работы нажмите "Войти"',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12)
        )
        layout.add_widget(info_label)
        
        self.add_widget(layout)
    
    def login(self, instance):
        """Вход в приложение"""
        pin = self.pin_input.text.strip()
        
        if pin:
            # Сохранение PIN-кода
            self.pin_storage.save_pin(pin)
            Logger.info("LoginScreen: PIN-код сохранен")
        
        # Переход к экрану сканирования
        self.manager.current = 'scanner'
        Logger.info("LoginScreen: Вход выполнен")
    
    def login_with_biometric(self, instance):
        """Вход с биометрической аутентификацией"""
        self.biometric_auth.authenticate(
            reason="Вход в приложение",
            callback=self.on_biometric_result
        )
    
    def on_biometric_result(self, success: bool):
        """Обработка результата биометрической аутентификации"""
        if success:
            # Переход к экрану сканирования
            self.manager.current = 'scanner'
            Logger.info("LoginScreen: Биометрический вход выполнен")
        else:
            Logger.warning("LoginScreen: Биометрическая аутентификация не пройдена")



