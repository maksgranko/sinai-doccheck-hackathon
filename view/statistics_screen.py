"""
Экран статистики и аналитики
KILLER FEATURE #3: Статистика с графиками и фильтрами
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from datetime import datetime, timedelta
from collections import Counter

from viewmodel.history_viewmodel import HistoryViewModel
try:
    from design.modern_theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, ACCENT_STATS,
        TEXT_PRIMARY, TEXT_SECONDARY
    )
except ImportError:
    from design.theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY, TEXT_SECONDARY
    )
    ACCENT_STATS = PRIMARY_COLOR

from design.components import PrimaryButton, SecondaryButton, TitleLabel, BodyLabel, CaptionLabel, Card


class StatisticsScreen(Screen):
    """Экран статистики и аналитики"""
    
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
            Color(*ACCENT_STATS)
            self.header_bg = Rectangle(size=header.size, pos=header.pos)
        
        def update_header_bg(instance, value):
            if hasattr(self, 'header_bg'):
                self.header_bg.size = instance.size
                self.header_bg.pos = instance.pos
        
        header.bind(size=update_header_bg, pos=update_header_bg)
        
        title = TitleLabel(
            text='Статистика',
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
        
        # Контейнер для статистики
        scroll = ScrollView()
        stats_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            padding=[dp(8), dp(8)]
        )
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        self.stats_layout = stats_layout
        scroll.add_widget(stats_layout)
        layout.add_widget(scroll)
        
        # Кнопки управления
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            spacing=dp(12)
        )
        
        refresh_button = PrimaryButton(
            text='Обновить',
            size_hint_x=0.5,
            on_press=self.refresh_stats
        )
        
        export_button = SecondaryButton(
            text='Экспорт',
            size_hint_x=0.5,
            on_press=self.export_stats
        )
        
        button_layout.add_widget(refresh_button)
        button_layout.add_widget(export_button)
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
        self.refresh_stats()
    
    def refresh_stats(self, instance=None):
        """Обновление статистики"""
        records = self.viewmodel.get_all_verifications()
        
        # Очистка
        self.stats_layout.clear_widgets()
        
        if not records:
            no_data_card = Card(
                size_hint_y=None,
                height=dp(100),
                padding=[dp(20), dp(16)]
            )
            no_data_label = BodyLabel(
                text='Нет данных для статистики\nОтсканируйте документы, чтобы они появились здесь',
                halign='center',
                valign='middle',
                text_size=(None, None)
            )
            no_data_label.bind(texture_size=no_data_label.setter('size'))
            no_data_card.add_widget(no_data_label)
            self.stats_layout.add_widget(no_data_card)
            return
        
        # Подсчет статистики
        total = len(records)
        status_counts = Counter(r.status for r in records)
        valid_count = status_counts.get('valid', 0)
        warning_count = status_counts.get('warning', 0)
        invalid_count = status_counts.get('invalid', 0)
        
        # Статистика по дням (последние 7 дней)
        today = datetime.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(7)]
        daily_counts = Counter()
        for record in records:
            if record.timestamp:
                record_date = record.timestamp.date()
                if record_date in last_7_days:
                    daily_counts[record_date] += 1
        
        # Карточка общей статистики
        total_card = self.create_stat_card(
            'Всего проверок',
            str(total),
            PRIMARY_COLOR
        )
        self.stats_layout.add_widget(total_card)
        
        # Карточки по статусам
        stats_row = GridLayout(
            cols=3,
            spacing=dp(12),
            size_hint_y=None,
            height=dp(120)
        )
        
        stats_row.add_widget(self.create_stat_card(
            'Подлинных',
            str(valid_count),
            STATUS_VALID
        ))
        stats_row.add_widget(self.create_stat_card(
            'Предупреждений',
            str(warning_count),
            STATUS_WARNING
        ))
        stats_row.add_widget(self.create_stat_card(
            'Недействительных',
            str(invalid_count),
            STATUS_INVALID
        ))
        
        self.stats_layout.add_widget(stats_row)
        
        # График активности (текстовый)
        activity_card = Card(
            size_hint_y=None,
            height=dp(200),
            padding=[dp(16), dp(12)]
        )
        
        activity_title = TitleLabel(
            text='Активность за последние 7 дней',
            size_hint_y=None,
            height=dp(30)
        )
        activity_card.add_widget(activity_title)
        
        # Простой текстовый график
        max_count = max(daily_counts.values()) if daily_counts else 1
        for day in reversed(last_7_days):
            count = daily_counts.get(day, 0)
            bar_width = int((count / max_count) * 100) if max_count > 0 else 0
            
            day_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(20),
                spacing=dp(8)
            )
            
            day_label = CaptionLabel(
                text=day.strftime('%d.%m'),
                size_hint_x=0.3,
                halign='left'
            )
            
            bar_container = BoxLayout(
                orientation='horizontal',
                size_hint_x=0.7
            )
            
            if count > 0:
                with bar_container.canvas.before:
                    Color(*PRIMARY_COLOR)
                    bar = Rectangle(
                        size=(dp(bar_width), dp(16)),
                        pos=(bar_container.pos[0], bar_container.pos[1] + dp(2))
                    )
            
            count_label = CaptionLabel(
                text=str(count),
                size_hint_x=None,
                width=dp(30),
                halign='right'
            )
            
            day_row.add_widget(day_label)
            day_row.add_widget(bar_container)
            day_row.add_widget(count_label)
            activity_card.add_widget(day_row)
        
        self.stats_layout.add_widget(activity_card)
        
        Logger.info(f"StatisticsScreen: Статистика обновлена, всего записей: {total}")
    
    def create_stat_card(self, title, value, color):
        """Создание карточки статистики"""
        card = Card(
            size_hint_y=None,
            height=dp(100),
            padding=[dp(12), dp(10)]
        )
        
        with card.canvas.before:
            # Акцентная полоска сверху
            Color(*color)
            self.accent_bar = Rectangle(
                size=(card.size[0], dp(4)),
                pos=(card.pos[0], card.pos[1] + card.size[1] - dp(4))
            )
        
        def update_accent_bar(instance, value):
            if hasattr(self, 'accent_bar'):
                self.accent_bar.size = (instance.size[0], dp(4))
                self.accent_bar.pos = (instance.pos[0], instance.pos[1] + instance.size[1] - dp(4))
        
        card.bind(size=update_accent_bar, pos=update_accent_bar)
        
        value_label = TitleLabel(
            text=value,
            font_size=dp(28),
            halign='center',
            color=color
        )
        
        title_label = CaptionLabel(
            text=title,
            halign='center'
        )
        
        card.add_widget(value_label)
        card.add_widget(title_label)
        
        return card
    
    def export_stats(self, instance):
        """Экспорт статистики"""
        Logger.info("StatisticsScreen: Экспорт статистики")
        # Интеграция с экспортом в PDF будет добавлена
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        
        popup = Popup(
            title='Экспорт',
            content=Label(text='Экспорт статистики будет доступен в следующей версии'),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.manager.current = 'scanner'

