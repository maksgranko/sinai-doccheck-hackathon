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
try:
    from design.modern_theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        INPUT_HEIGHT, BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY
    )
except ImportError:
    from design.theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        INPUT_HEIGHT, BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY
    )
from design.components import PrimaryButton, SecondaryButton, StyledTextInput, TitleLabel, SubtitleLabel, BodyLabel, CaptionLabel, Card


class LoginScreen(Screen):
    """Экран входа в приложение"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.biometric_auth = BiometricAuth()
        self.pin_storage = PinStorage()
        
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        # Адаптивные размеры
        from kivy.core.window import Window
        is_mobile = Window.width < 400 or Window.height < 600
        
        padding_h = dp(20) if is_mobile else dp(32)
        padding_v = dp(24) if is_mobile else dp(40)
        
        # Основной контейнер
        main_container = BoxLayout(
            orientation='vertical',
            padding=[padding_h, padding_v],
            spacing=dp(20),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        # Контейнер для карточки входа
        card_height = dp(420) if is_mobile else dp(450)
        card_container = Card(
            size_hint=(0.92, None),
            height=card_height,
            pos_hint={'center_x': 0.5}
        )
        
        # Внутренний контейнер карточки (уже есть padding в Card)
        card_content = BoxLayout(
            orientation='vertical',
            spacing=dp(20)
        )
        
        # Логотип/иконка - простой и элегантный
        icon_container = BoxLayout(
            size_hint_y=None,
            height=dp(75),
            pos_hint={'center_x': 0.5}
        )
        icon_label = BodyLabel(
            text='DOC',
            font_size=dp(42),
            halign='center',
            bold=True,
            color=PRIMARY_COLOR
        )
        icon_container.add_widget(icon_label)
        
        # Заголовок - адаптивный размер для мобильных устройств
        title_font_size = dp(20) if is_mobile else dp(24)
        title = TitleLabel(
            text='Верификатор\nдокументов' if is_mobile else 'Верификатор документов',
            size_hint_y=None,
            height=dp(50) if is_mobile else dp(58),
            halign='center',
            font_size=title_font_size,
            text_size=(None, None)  # Разрешаем перенос строк
        )
        title.bind(texture_size=title.setter('size'))
        
        subtitle_font_size = dp(13) if is_mobile else dp(15)
        subtitle = SubtitleLabel(
            text='Проверка подлинности\nэлектронных документов' if is_mobile else 'Проверка подлинности электронных документов',
            size_hint_y=None,
            height=dp(38) if is_mobile else dp(42),
            halign='center',
            font_size=subtitle_font_size,
            text_size=(None, None)  # Разрешаем перенос строк
        )
        subtitle.bind(texture_size=subtitle.setter('size'))
        
        # Поле для PIN-кода
        pin_label = BodyLabel(
            text='PIN-код (опционально)',
            size_hint_y=None,
            height=dp(26),
            halign='left',
            font_size=dp(14)
        )
        
        self.pin_input = StyledTextInput(
            password=True,
            hint_text='Введите PIN-код',
            size_hint_y=None,
            height=INPUT_HEIGHT
        )
        
        # Кнопка входа
        login_button = PrimaryButton(
            text='Войти',
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            on_press=self.login
        )
        
        # Кнопка биометрической аутентификации
        bio_button = None
        if self.biometric_auth.is_available:
            bio_button = SecondaryButton(
                text='Войти с биометрией',
                size_hint_y=None,
                height=BUTTON_HEIGHT,
                on_press=self.login_with_biometric
            )
        
        # Сборка карточки
        card_container.add_widget(icon_container)
        card_container.add_widget(title)
        card_container.add_widget(subtitle)
        card_container.add_widget(BoxLayout(size_hint_y=None, height=dp(28)))  # Отступ
        card_container.add_widget(pin_label)
        card_container.add_widget(self.pin_input)
        card_container.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))  # Отступ
        card_container.add_widget(login_button)
        
        if bio_button:
            card_container.add_widget(BoxLayout(size_hint_y=None, height=dp(16)))  # Отступ
            card_container.add_widget(bio_button)
        
        main_container.add_widget(card_container)
        
        # Информация внизу
        info_label = CaptionLabel(
            text='Для начала работы нажмите "Войти"',
            size_hint_y=None,
            height=dp(24),
            halign='center'
        )
        main_container.add_widget(info_label)
        
        self.add_widget(main_container)
    
    
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



