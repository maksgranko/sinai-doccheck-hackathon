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
from view.statistics_screen import StatisticsScreen
from view.document_detail_screen import DocumentDetailScreen
from view.search_screen import SearchScreen


class DocumentVerifierApp(App):
    """Главный класс приложения"""
    
    def build(self):
        """Создание интерфейса приложения"""
        self.title = "DocCheck"
        Logger.info("App: Инициализация приложения")
        
        # Настройка размера окна для мобильных устройств
        # Автоматическое определение размера экрана
        from kivy.core.window import Window
        if Window.width < 400:  # Мобильное устройство
            Window.size = (360, 640)
        else:  # Десктоп
            Window.size = (400, 700)
        
        # Установка цвета фона приложения (современная тема)
        try:
            from design.modern_theme import BACKGROUND_COLOR
        except ImportError:
            from design.theme import BACKGROUND_COLOR
        Window.clearcolor = BACKGROUND_COLOR
        
        # Включение адаптивного масштабирования
        Window.bind(on_resize=self.on_window_resize)
        
        # Создание менеджера экранов
        sm = ScreenManager()
        
        # Добавление экранов
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ScannerScreen(name='scanner'))
        sm.add_widget(HistoryScreen(name='history'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(StatisticsScreen(name='statistics'))
        sm.add_widget(DocumentDetailScreen(name='document_detail'))
        sm.add_widget(SearchScreen(name='search'))
        
        # Установка начального экрана
        sm.current = 'login'
        
        return sm
    
    def on_start(self):
        """Вызывается при запуске приложения"""
        Logger.info("App: Приложение запущено")
    
    def on_stop(self):
        """Вызывается при закрытии приложения"""
        Logger.info("App: Приложение закрыто")
    
    def on_window_resize(self, window, width, height):
        """Обработка изменения размера окна"""
        Logger.info(f"App: Размер окна изменен: {width}x{height}")


if __name__ == '__main__':
    DocumentVerifierApp().run()



