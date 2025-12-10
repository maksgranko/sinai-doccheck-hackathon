"""
Экран детальной информации о документе
Новая фича: Детальный просмотр документа с возможностью экспорта
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from datetime import date, datetime

from model.document_model import DocumentModel
try:
    from design.modern_theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, ACCENT_EXPORT,
        TEXT_PRIMARY, TEXT_SECONDARY
    )
except ImportError:
    from design.theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_VALID, STATUS_WARNING, STATUS_INVALID, STATUS_NEUTRAL,
        BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY, TEXT_SECONDARY
    )
    ACCENT_EXPORT = PRIMARY_COLOR

from design.components import PrimaryButton, SecondaryButton, TitleLabel, BodyLabel, CaptionLabel, Card


class DocumentDetailScreen(Screen):
    """Экран детальной информации о документе"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.document = None
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
            text='Детали документа',
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
        
        # Контейнер для деталей
        scroll = ScrollView()
        self.details_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(16),
            size_hint_y=None,
            padding=[dp(8), dp(8)]
        )
        self.details_layout.bind(minimum_height=self.details_layout.setter('height'))
        
        scroll.add_widget(self.details_layout)
        layout.add_widget(scroll)
        
        # Кнопки действий
        actions_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=BUTTON_HEIGHT,
            spacing=dp(12)
        )
        
        self.export_button = PrimaryButton(
            text='Экспорт PDF',
            size_hint_x=0.5,
            on_press=self.export_pdf
        )
        
        share_button = SecondaryButton(
            text='Поделиться',
            size_hint_x=0.5,
            on_press=self.share_document
        )
        
        actions_layout.add_widget(self.export_button)
        actions_layout.add_widget(share_button)
        layout.add_widget(actions_layout)
        
        self.add_widget(layout)
    
    def show_document(self, document: DocumentModel):
        """Отображение документа"""
        self.document = document
        self.details_layout.clear_widgets()
        
        if not document:
            return
        
        # Карточка статуса
        status_card = self.create_status_card(document)
        self.details_layout.add_widget(status_card)
        
        # Карточка основной информации
        info_card = self.create_info_card(document)
        self.details_layout.add_widget(info_card)
        
        # Карточка метаданных
        if document.metadata:
            meta_card = self.create_metadata_card(document)
            self.details_layout.add_widget(meta_card)
    
    def create_status_card(self, document: DocumentModel) -> Card:
        """Создание карточки статуса"""
        card = Card(
            size_hint_y=None,
            height=dp(120),
            padding=[dp(16), dp(12)]
        )
        
        status_color = self.get_status_color(document.status)
        status_text = self.get_status_text(document.status)
        
        # Большой индикатор статуса
        status_container = BoxLayout(
            orientation='horizontal',
            spacing=dp(16)
        )
        
        status_indicator = BoxLayout(
            size_hint=(None, None),
            size=(dp(60), dp(60)),
            pos_hint={'center_y': 0.5}
        )
        
        with status_indicator.canvas.before:
            Color(*status_color)
            status_circle = RoundedRectangle(
                size=status_indicator.size,
                pos=status_indicator.pos,
                radius=[dp(30), dp(30), dp(30), dp(30)]
            )
        
        status_info = BoxLayout(
            orientation='vertical',
            spacing=dp(4)
        )
        
        status_label = TitleLabel(
            text=status_text,
            font_size=dp(20),
            color=status_color,
            halign='left'
        )
        
        doc_id_label = BodyLabel(
            text=f"ID: {document.document_id}",
            halign='left'
        )
        
        status_info.add_widget(status_label)
        status_info.add_widget(doc_id_label)
        
        status_container.add_widget(status_indicator)
        status_container.add_widget(status_info)
        
        card.add_widget(status_container)
        return card
    
    def create_info_card(self, document: DocumentModel) -> Card:
        """Создание карточки информации"""
        card = Card(
            size_hint_y=None,
            height=dp(200),
            padding=[dp(16), dp(12)]
        )
        
        info_title = TitleLabel(
            text='Информация о документе',
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(info_title)
        
        # Детали
        details = []
        if document.document_type:
            details.append(('Тип документа', document.document_type))
        if document.issuer:
            details.append(('Выдан', document.issuer))
        if document.issue_date:
            details.append(('Дата выдачи', str(document.issue_date)))
        if document.expiry_date:
            expiry_str = str(document.expiry_date)
            if isinstance(document.expiry_date, date):
                days_left = (document.expiry_date - date.today()).days
                if days_left > 0:
                    expiry_str += f" (осталось {days_left} дней)"
                else:
                    expiry_str += " (истек)"
            details.append(('Срок действия', expiry_str))
        
        for label, value in details:
            detail_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(30),
                spacing=dp(12)
            )
            
            label_widget = CaptionLabel(
                text=label + ':',
                size_hint_x=0.4,
                halign='left'
            )
            
            value_widget = BodyLabel(
                text=str(value),
                size_hint_x=0.6,
                halign='left',
                bold=True
            )
            
            detail_row.add_widget(label_widget)
            detail_row.add_widget(value_widget)
            card.add_widget(detail_row)
        
        return card
    
    def create_metadata_card(self, document: DocumentModel) -> Card:
        """Создание карточки метаданных"""
        card = Card(
            size_hint_y=None,
            height=dp(150),
            padding=[dp(16), dp(12)]
        )
        
        meta_title = TitleLabel(
            text='Дополнительная информация',
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(meta_title)
        
        import json
        meta_text = json.dumps(document.metadata, indent=2, ensure_ascii=False) if document.metadata else "Нет данных"
        
        meta_label = BodyLabel(
            text=meta_text,
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        meta_label.bind(texture_size=meta_label.setter('size'))
        
        card.add_widget(meta_label)
        return card
    
    def get_status_color(self, status: str) -> tuple:
        """Получение цвета статуса"""
        colors = {
            'valid': STATUS_VALID,
            'warning': STATUS_WARNING,
            'invalid': STATUS_INVALID,
        }
        color = colors.get(status, STATUS_NEUTRAL)
        if len(color) == 3:
            return color + (1.0,)
        return color
    
    def get_status_text(self, status: str) -> str:
        """Получение текста статуса"""
        texts = {
            'valid': 'Документ подлинный',
            'warning': 'Предупреждение',
            'invalid': 'Документ недействителен',
        }
        return texts.get(status, 'Неизвестный статус')
    
    def export_pdf(self, instance):
        """Экспорт документа в PDF"""
        if not self.document:
            return
        
        try:
            from services.pdf_export import PDFExportService
            export_service = PDFExportService()
            pdf_path = export_service.export_verification_result(self.document)
            
            if pdf_path:
                from kivy.uix.popup import Popup
                from kivy.uix.label import Label
                
                popup = Popup(
                    title='Экспорт успешен',
                    content=Label(text=f'PDF создан:\n{pdf_path}'),
                    size_hint=(0.8, 0.4)
                )
                popup.open()
        except Exception as e:
            Logger.error(f"DocumentDetail: Ошибка экспорта PDF: {e}")
    
    def share_document(self, instance):
        """Поделиться документом"""
        Logger.info("DocumentDetail: Поделиться документом")
        # В будущем можно добавить интеграцию с системным sharing
    
    def go_back(self, instance):
        """Возврат на предыдущий экран"""
        self.manager.current = 'scanner'

