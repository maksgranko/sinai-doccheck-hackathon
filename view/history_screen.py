"""
Экран истории верификаций
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger
from kivy.metrics import dp
from datetime import datetime

from viewmodel.history_viewmodel import HistoryViewModel
from security.biometric_auth import BiometricAuth
from model.document_model import VerificationRecord


class HistoryScreen(Screen):
    """Экран истории верификаций"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = HistoryViewModel()
        self.biometric_auth = BiometricAuth()
        self.authenticated = False
        
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Заголовок
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        title = Label(
            text='Журнал верификаций',
            size_hint_x=0.7,
            font_size=dp(20),
            bold=True
        )
        
        back_button = Button(
            text='Назад',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        
        header.add_widget(title)
        header.add_widget(back_button)
        layout.add_widget(header)
        
        # Контейнер для истории
        scroll = ScrollView()
        self.history_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            size_hint_y=None
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll.add_widget(self.history_layout)
        layout.add_widget(scroll)
        
        # Кнопки управления
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        refresh_button = Button(
            text='Обновить',
            on_press=self.refresh_history
        )
        
        clear_button = Button(
            text='Очистить',
            on_press=self.clear_history,
            size_hint_x=0.3
        )
        
        button_layout.add_widget(refresh_button)
        button_layout.add_widget(clear_button)
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Вызывается при входе на экран"""
        # Требуется биометрическая аутентификация
        if not self.authenticated:
            self.request_authentication()
        else:
            self.refresh_history()
    
    def request_authentication(self):
        """Запрос биометрической аутентификации"""
        if self.biometric_auth.is_available:
            self.biometric_auth.authenticate(
                reason="Требуется аутентификация для доступа к журналу верификаций",
                callback=self.on_authentication_result
            )
        else:
            # Если биометрия недоступна, разрешаем доступ (для тестирования)
            Logger.warning("HistoryScreen: Биометрия недоступна, разрешен доступ")
            self.authenticated = True
            self.refresh_history()
    
    def on_authentication_result(self, success: bool):
        """Обработка результата аутентификации"""
        if success:
            self.authenticated = True
            self.refresh_history()
        else:
            Logger.warning("HistoryScreen: Аутентификация не пройдена")
            # Возврат на предыдущий экран
            self.go_back(None)
    
    def refresh_history(self, instance=None):
        """Обновление истории верификаций"""
        if not self.authenticated:
            return
        
        # Очистка текущего списка
        self.history_layout.clear_widgets()
        
        # Получение записей
        records = self.viewmodel.get_all_verifications()
        
        if not records:
            no_records = Label(
                text='История пуста',
                size_hint_y=None,
                height=dp(50),
                font_size=dp(16)
            )
            self.history_layout.add_widget(no_records)
            return
        
        # Добавление записей
        for record in records:
            record_widget = self.create_record_widget(record)
            self.history_layout.add_widget(record_widget)
        
        Logger.info(f"HistoryScreen: Загружено {len(records)} записей")
    
    def create_record_widget(self, record: VerificationRecord) -> BoxLayout:
        """Создание виджета записи"""
        container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            padding=dp(10),
            spacing=dp(10)
        )
        
        # Индикатор статуса
        status_color = self.viewmodel.get_status_color(record.status)
        status_indicator = BoxLayout(
            size_hint_x=None,
            width=dp(10)
        )
        with status_indicator.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*status_color)
            Rectangle(size=status_indicator.size, pos=status_indicator.pos)
        
        status_indicator.bind(size=self._update_status_rect, pos=self._update_status_rect)
        container.add_widget(status_indicator)
        
        # Информация о документе
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        doc_id_label = Label(
            text=f"ID: {record.document_id[:20]}...",
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            halign='left',
            text_size=(None, None)
        )
        doc_id_label.bind(texture_size=doc_id_label.setter('size'))
        
        status_label = Label(
            text=self.viewmodel.get_status_text(record.status),
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            halign='left'
        )
        
        time_str = ""
        if record.timestamp:
            time_str = record.timestamp.strftime("%d.%m.%Y %H:%M")
        time_label = Label(
            text=time_str,
            size_hint_y=None,
            height=dp(25),
            font_size=dp(10),
            halign='left'
        )
        
        info_layout.add_widget(doc_id_label)
        info_layout.add_widget(status_label)
        info_layout.add_widget(time_label)
        container.add_widget(info_layout)
        
        # Кнопка удаления
        delete_button = Button(
            text='×',
            size_hint_x=None,
            width=dp(40),
            on_press=lambda x, r=record: self.delete_record(r)
        )
        container.add_widget(delete_button)
        
        return container
    
    def _update_status_rect(self, *args):
        """Обновление прямоугольника статуса"""
        pass
    
    def delete_record(self, record: VerificationRecord):
        """Удаление записи"""
        if record.id:
            if self.viewmodel.delete_verification(record.id):
                self.refresh_history()
    
    def clear_history(self, instance):
        """Очистка всей истории"""
        if self.viewmodel.clear_all():
            self.refresh_history()
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.authenticated = False
        self.manager.current = 'scanner'



