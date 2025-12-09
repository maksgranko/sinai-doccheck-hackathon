"""
Главный файл приложения - Верификатор подлинности электронных документов
"""
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.logger import Logger

from view.scanner_screen import ScannerScreen
from view.history_screen import HistoryScreen
from view.settings_screen import SettingsScreen
from view.login_screen import LoginScreen


class DocumentVerifierApp(App):
    """Главный класс приложения"""
    
    def build(self):
        """Создание интерфейса приложения"""
        Logger.info("App: Инициализация приложения")
        
        # Настройка размера окна для мобильных устройств
        Window.size = (360, 640)
        
        # Создание менеджера экранов
        sm = ScreenManager()
        
        # Добавление экранов
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ScannerScreen(name='scanner'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(SettingsScreen(name='settings'))
        
        # Установка начального экрана
        sm.current = 'login'
        
        return sm
    
    def on_start(self):
        """Вызывается при запуске приложения"""
        Logger.info("App: Приложение запущено")
    
    def on_stop(self):
        """Вызывается при закрытии приложения"""
        Logger.info("App: Приложение закрыто")


if __name__ == '__main__':
    DocumentVerifierApp().run()



