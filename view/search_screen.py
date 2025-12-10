"""
Экран поиска документов
Новая фича: Поиск по истории верификаций
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.clock import Clock

from viewmodel.history_viewmodel import HistoryViewModel
from model.document_model import VerificationRecord
try:
    from design.modern_theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY, TEXT_SECONDARY
    )
except ImportError:
    from design.theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY, TEXT_SECONDARY
    )

from design.components import PrimaryButton, SecondaryButton, TitleLabel, BodyLabel, CaptionLabel, Card


class SearchScreen(Screen):
    """Экран поиска документов"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = HistoryViewModel()
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        layout = BoxLayout(
            orientation='vertical',
            padding=[dp(16), dp(8)],
            spacing=dp(16)
        )
        
        # Заголовок
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
            text='Поиск',
            size_hint_x=0.7,
            color=(1, 1, 1, 1)
        )
        
        back_button = SecondaryButton(
            text='Назад',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        back_button.color = (1, 1, 1, 1)
        
        header.add_widget(title)
        header.add_widget(back_button)
        layout.add_widget(header)
        
        # Поле поиска
        search_input = TextInput(
            hint_text='Введите ID документа или тип...',
            size_hint_y=None,
            height=dp(45),
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            font_size=dp(14),
            padding_x=dp(12),
            padding_y=dp(10)
        )
        search_input.bind(text=self.on_search_text)
        self.search_input = search_input
        layout.add_widget(search_input)
        
        # Результаты поиска
        scroll = ScrollView()
        self.results_layout = GridLayout(
            cols=1,
            spacing=dp(12),
            size_hint_y=None,
            padding=[dp(8), dp(8)]
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        scroll.add_widget(self.results_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_search_text(self, instance, text):
        """Обработка изменения текста поиска"""
        # Задержка для оптимизации
        Clock.unschedule(self._perform_search)
        Clock.schedule_once(lambda dt: self._perform_search(text), 0.3)
    
    def _perform_search(self, query):
        """Выполнение поиска"""
        self.results_layout.clear_widgets()
        
        if not query or len(query.strip()) < 2:
            return
        
        query_lower = query.lower().strip()
        all_records = self.viewmodel.get_all_verifications(limit=1000)
        
        # Фильтрация
        filtered = [
            r for r in all_records
            if query_lower in r.document_id.lower() or
            (r.document_type and query_lower in r.document_type.lower()) or
            (r.issuer and query_lower in r.issuer.lower())
        ]
        
        if not filtered:
            no_results_card = Card(
                size_hint_y=None,
                height=dp(80),
                padding=[dp(20), dp(16)]
            )
            no_results_label = BodyLabel(
                text='Ничего не найдено',
                halign='center',
                valign='middle',
                text_size=(None, None)
            )
            no_results_label.bind(texture_size=no_results_label.setter('size'))
            no_results_card.add_widget(no_results_label)
            self.results_layout.add_widget(no_results_card)
            return
        
        # Отображение результатов
        for record in filtered[:50]:  # Ограничение до 50 результатов
            record_widget = self.create_result_widget(record)
            self.results_layout.add_widget(record_widget)
    
    def create_result_widget(self, record: VerificationRecord) -> Card:
        """Создание виджета результата"""
        card = Card(
            size_hint_y=None,
            height=dp(70),
            spacing=dp(6),
            padding=[dp(12), dp(8)]
        )
        
        info_container = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        # Индикатор статуса
        status_color = self.viewmodel.get_status_color(record.status)
        if len(status_color) == 3:
            status_color_rgba = (status_color[0], status_color[1], status_color[2], 0.2)
        else:
            status_color_rgba = status_color[:3] + (0.2,)
        
        status_indicator = BoxLayout(
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5}
        )
        
        with status_indicator.canvas.before:
            Color(*status_color_rgba)
            status_circle = RoundedRectangle(
                size=status_indicator.size,
                pos=status_indicator.pos,
                radius=[dp(12), dp(12), dp(12), dp(12)]
            )
        
        # Информация
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.8, spacing=dp(2))
        
        doc_id_label = BodyLabel(
            text=record.document_id,
            size_hint_y=None,
            height=dp(22),
            halign='left',
            bold=True
        )
        
        status_text = self.viewmodel.get_status_text(record.status)
        status_label = CaptionLabel(
            text=status_text,
            size_hint_y=None,
            height=dp(18),
            halign='left',
            color=status_color if len(status_color) >= 4 else status_color + (1.0,)
        )
        
        info_layout.add_widget(doc_id_label)
        info_layout.add_widget(status_label)
        
        info_container.add_widget(status_indicator)
        info_container.add_widget(info_layout)
        
        card.add_widget(info_container)
        card.record = record
        card.bind(on_touch_down=lambda instance, touch: self.on_result_touch(instance, touch) if instance.collide_point(*touch.pos) and touch.is_double_tap else False)
        
        return card
    
    def on_result_touch(self, instance, touch):
        """Обработка касания результата"""
        if hasattr(instance, 'record'):
            from view.history_screen import HistoryScreen
            history_screen = self.manager.get_screen('history')
            history_screen.view_details(instance.record)
            self.manager.current = 'document_detail'
        return True
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.manager.current = 'scanner'

