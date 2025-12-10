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
from kivy.graphics import Color, Rectangle, RoundedRectangle
from datetime import datetime

from viewmodel.history_viewmodel import HistoryViewModel
from security.biometric_auth import BiometricAuth
from model.document_model import VerificationRecord
try:
    from design.modern_theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING
    )
except ImportError:
    from design.theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING
    )
from design.components import PrimaryButton, SecondaryButton, TitleLabel, BodyLabel, CaptionLabel, Card


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
            text='Журнал верификаций',
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
        
        # Контейнер для истории
        scroll = ScrollView()
        self.history_layout = GridLayout(
            cols=1,
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(8), dp(8)]
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll.add_widget(self.history_layout)
        layout.add_widget(scroll)
        
        # Кнопки управления
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            spacing=dp(12),
            padding=[dp(0), dp(8)]
        )
        
        refresh_button = PrimaryButton(
            text='Обновить',
            size_hint_x=0.7,
            on_press=self.refresh_history
        )
        
        clear_button = SecondaryButton(
            text='Очистить',
            size_hint_x=0.3,
            on_press=self.clear_history
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
            no_records_card = Card(
                size_hint_y=None,
                height=dp(100),
                padding=[dp(20), dp(16)]
            )
            no_records_label = BodyLabel(
                text='История пуста\nОтсканируйте документы, чтобы они появились здесь',
                halign='center',
                valign='middle',
                text_size=(None, None)
            )
            no_records_label.bind(texture_size=no_records_label.setter('size'))
            no_records_card.add_widget(no_records_label)
            self.history_layout.add_widget(no_records_card)
            return
        
        # Добавление записей с анимацией появления
        for i, record in enumerate(records):
            record_widget = self.create_record_widget(record)
            self.history_layout.add_widget(record_widget)
            
            # Анимация появления
            record_widget.opacity = 0
            from kivy.animation import Animation
            anim = Animation(opacity=1, duration=0.3, transition='out_quad')
            anim.start(record_widget)
        
        Logger.info(f"HistoryScreen: Загружено {len(records)} записей")
    
    def create_record_widget(self, record: VerificationRecord) -> Card:
        """Создание виджета записи - улучшенный дизайн с возможностью просмотра деталей"""
        card = Card(
            size_hint_y=None,
            height=dp(90),
            spacing=dp(6),
            padding=[dp(12), dp(10)]
        )
        
        # Добавляем эффект нажатия
        card.bind(on_touch_down=self.on_card_touch)
        
        # Контейнер с информацией
        info_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(10)
        )
        
        # Индикатор статуса (компактный)
        status_color = self.viewmodel.get_status_color(record.status)
        status_indicator = BoxLayout(
            size_hint=(None, None),
            size=(dp(32), dp(32)),
            pos_hint={'center_y': 0.5}
        )
        
        # Убеждаемся, что status_color - это кортеж из 3 элементов (R, G, B)
        if len(status_color) == 3:
            status_color_rgba = (status_color[0], status_color[1], status_color[2], 0.2)
        else:
            status_color_rgba = (status_color[0], status_color[1], status_color[2], 0.2) if len(status_color) >= 3 else (0.5, 0.5, 0.5, 0.2)
        
        with status_indicator.canvas.before:
            Color(*status_color_rgba)  # Полупрозрачный фон
            status_circle = RoundedRectangle(
                size=status_indicator.size,
                pos=status_indicator.pos,
                radius=[dp(16), dp(16), dp(16), dp(16)]
            )
        
        def update_status_circle(instance, value):
            if hasattr(status_indicator, 'canvas') and hasattr(status_indicator.canvas, 'before'):
                status_circle.size = instance.size
                status_circle.pos = instance.pos
        
        status_indicator.bind(size=update_status_circle, pos=update_status_circle)
        
        # Информация о документе - компактная
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_x=0.75,
            spacing=dp(2)
        )
        
        # ID документа
        doc_id_label = BodyLabel(
            text=record.document_id,
            size_hint_y=None,
            height=dp(24),
            halign='left',
            text_size=(None, None),
            bold=True
        )
        doc_id_label.bind(texture_size=doc_id_label.setter('size'))
        
        # Статус с цветом
        status_text = self.viewmodel.get_status_text(record.status)
        # Убеждаемся, что color - это кортеж из 4 элементов (R, G, B, A)
        if len(status_color) == 3:
            status_label_color = (status_color[0], status_color[1], status_color[2], 1.0)
        else:
            status_label_color = status_color if len(status_color) >= 4 else (0.5, 0.5, 0.5, 1.0)
        
        status_label = BodyLabel(
            text=status_text,
            size_hint_y=None,
            height=dp(20),
            halign='left',
            color=status_label_color,
            text_size=(None, None)
        )
        status_label.bind(texture_size=status_label.setter('size'))
        
        # Время
        time_str = ""
        if record.timestamp:
            time_str = record.timestamp.strftime('%d.%m.%Y %H:%M')
        time_label = CaptionLabel(
            text=time_str,
            size_hint_y=None,
            height=dp(18),
            halign='left',
            text_size=(None, None)
        )
        time_label.bind(texture_size=time_label.setter('size'))
        
        info_layout.add_widget(doc_id_label)
        info_layout.add_widget(status_label)
        info_layout.add_widget(time_label)
        
        # Кнопки действий
        actions_container = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            width=dp(120),
            spacing=dp(6)
        )
        
        # Кнопка просмотра деталей
        view_button = SecondaryButton(
            text='Детали',
            size_hint_x=None,
            width=dp(55),
            height=dp(36),
            font_size=dp(11),
            on_press=lambda x, r=record: self.view_details(r)
        )
        
        # Кнопка удаления
        delete_button = SecondaryButton(
            text='Удалить',
            size_hint_x=None,
            width=dp(55),
            height=dp(36),
            font_size=dp(11),
            on_press=lambda x, r=record: self.delete_record(r)
        )
        
        actions_container.add_widget(view_button)
        actions_container.add_widget(delete_button)
        
        info_container.add_widget(status_indicator)
        info_container.add_widget(info_layout)
        info_container.add_widget(actions_container)
        
        card.add_widget(info_container)
        card.record = record  # Сохраняем запись для доступа
        return card
    
    
    def on_card_touch(self, instance, touch):
        """Обработка касания карточки"""
        if instance.collide_point(*touch.pos) and touch.is_double_tap:
            # Двойное касание для просмотра деталей
            if hasattr(instance, 'record'):
                self.view_details(instance.record)
            return True
        return False
    
    def view_details(self, record: VerificationRecord):
        """Просмотр деталей записи"""
        # Создаем DocumentModel из записи
        from model.document_model import DocumentModel
        document = DocumentModel(
            document_id=record.document_id,
            status=record.status,
            document_type=record.document_type,
            issuer=record.issuer
        )
        
        # Переходим на экран деталей
        if 'document_detail' not in [screen.name for screen in self.manager.screens]:
            from view.document_detail_screen import DocumentDetailScreen
            detail_screen = DocumentDetailScreen(name='document_detail')
            self.manager.add_widget(detail_screen)
        
        detail_screen = self.manager.get_screen('document_detail')
        detail_screen.show_document(document)
        self.manager.current = 'document_detail'
    
    def delete_record(self, record: VerificationRecord):
        """Удаление записи с подтверждением"""
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout
        from kivy.uix.label import Label
        from design.components import PrimaryButton, SecondaryButton
        
        def confirm_delete(instance):
            if record.id:
                if self.viewmodel.delete_verification(record.id):
                    self.refresh_history()
            popup.dismiss()
        
        content = PopupBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        content.add_widget(Label(
            text=f'Удалить запись\n{record.document_id}?',
            text_size=(None, None),
            halign='center'
        ))
        
        buttons = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        yes_btn = PrimaryButton(text='Да', size_hint_x=0.5, on_press=confirm_delete)
        no_btn = SecondaryButton(text='Нет', size_hint_x=0.5, on_press=popup.dismiss)
        buttons.add_widget(yes_btn)
        buttons.add_widget(no_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title='Подтверждение',
            content=content,
            size_hint=(0.7, 0.3)
        )
        popup.open()
    
    def clear_history(self, instance):
        """Очистка всей истории"""
        if self.viewmodel.clear_all():
            self.refresh_history()
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.authenticated = False
        self.manager.current = 'scanner'



