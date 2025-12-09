"""
Экран сканирования QR-кодов
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.logger import Logger
from kivy.metrics import dp
try:
    # Правильный импорт для decode
    from pyzbar.pyzbar import decode as zbar_decode
except Exception:
    zbar_decode = None
from PIL import Image as PILImage
import io

from viewmodel.scanner_viewmodel import ScannerViewModel
from model.document_model import DocumentModel


class ScannerScreen(Screen):
    """Экран сканирования QR-кодов и штрихкодов"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = ScannerViewModel()
        self.viewmodel.on_status_changed = self.on_document_verified
        self.viewmodel.on_error = self.on_verification_error
        
        self.camera = None
        self.scanning = False
        self.status_light = None
        
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса"""
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Заголовок
        title = Label(
            text='Сканирование документа',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(20),
            bold=True
        )
        layout.add_widget(title)
        
        # Контейнер для камеры и рамки захвата
        camera_container = BoxLayout(orientation='vertical', size_hint_y=0.7)
        
        # Камера
        self.camera = Camera(
            resolution=(640, 480),
            play=False,
            size_hint_y=1
        )
        camera_container.add_widget(self.camera)
        
        # Рамка захвата QR-кода (визуальный помощник)
        self.scan_frame = BoxLayout(
            size_hint=(None, None),
            size=(dp(250), dp(250)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.scan_frame.bind(pos=self.update_scan_frame, size=self.update_scan_frame)
        
        with self.scan_frame.canvas.before:
            Color(1, 1, 1, 0.3)  # Полупрозрачный белый
            self.frame_rect = Rectangle(size=self.scan_frame.size, pos=self.scan_frame.pos)
        
        camera_container.add_widget(self.scan_frame)
        layout.add_widget(camera_container)
        
        # Светофор статуса
        status_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            spacing=dp(10)
        )
        
        # Индикатор статуса (светофор)
        self.status_light = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            pos_hint={'center_x': 0.5}
        )
        self.status_light.bind(size=self.update_status_light)
        
        with self.status_light.canvas.before:
            Color(0.5, 0.5, 0.5)  # Серый по умолчанию
            self.status_circle = Ellipse(size=(dp(50), dp(50)), pos=self.status_light.pos)
        
        self.status_light.bind(pos=self.update_status_light)
        
        status_label = Label(
            text='Наведите камеру на QR-код',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14)
        )
        self.status_text_label = status_label
        
        status_container.add_widget(self.status_light)
        status_container.add_widget(status_label)
        layout.add_widget(status_container)
        
        # Кнопки управления
        button_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        self.start_button = Button(
            text='Начать сканирование',
            on_press=self.toggle_scanning
        )
        
        self.history_button = Button(
            text='История',
            on_press=self.go_to_history,
            size_hint_x=0.3
        )
        
        button_layout.add_widget(self.start_button)
        button_layout.add_widget(self.history_button)
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def update_scan_frame(self, *args):
        """Обновление позиции рамки захвата"""
        if hasattr(self, 'frame_rect'):
            self.frame_rect.pos = self.scan_frame.pos
            self.frame_rect.size = self.scan_frame.size
    
    def update_status_light(self, *args):
        """Обновление позиции индикатора статуса"""
        if hasattr(self, 'status_circle'):
            self.status_circle.pos = (
                self.status_light.x + self.status_light.width / 2 - dp(25),
                self.status_light.y + self.status_light.height / 2 - dp(25)
            )
    
    def toggle_scanning(self, instance):
        """Переключение режима сканирования"""
        if not self.scanning:
            self.start_scanning()
        else:
            self.stop_scanning()
    
    def start_scanning(self):
        """Запуск сканирования"""
        if self.camera:
            self.camera.play = True
            self.scanning = True
            self.start_button.text = 'Остановить сканирование'
            self.status_text_label.text = 'Сканирование...'
            
            # Запуск периодического сканирования
            Clock.schedule_interval(self.scan_qr_code, 0.5)
            Logger.info("Scanner: Сканирование запущено")
    
    def stop_scanning(self):
        """Остановка сканирования"""
        if self.camera:
            self.camera.play = False
            self.scanning = False
            self.start_button.text = 'Начать сканирование'
            Clock.unschedule(self.scan_qr_code)
            Logger.info("Scanner: Сканирование остановлено")
    
    def scan_qr_code(self, dt):
        """Сканирование QR-кода с камеры"""
        if not self.camera or not self.camera.texture:
            return
        
        if zbar_decode is None:
            Logger.error("Scanner: pyzbar не установлен")
            return
        
        try:
            # Получение изображения с камеры
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            
            # Конвертация в PIL Image
            pil_image = PILImage.frombytes('RGBA', size, pixels)
            
            # Конвертация в grayscale для pyzbar
            pil_image = pil_image.convert('RGB')
            
            # Детекция QR-кодов и штрихкодов
            barcodes = zbar_decode(pil_image)
            
            if barcodes:
                # Берем первый найденный код
                barcode = barcodes[0]
                document_id = barcode.data.decode('utf-8')
                
                Logger.info(f"Scanner: Найден код: {document_id}")
                
                # Остановка сканирования и верификация
                self.stop_scanning()
                self.status_text_label.text = 'Верификация...'
                self.viewmodel.verify_document(document_id)
        
        except Exception as e:
            Logger.error(f"Scanner: Ошибка сканирования: {e}")
    
    def on_document_verified(self, document: DocumentModel):
        """Обработка результата верификации"""
        Logger.info(f"Scanner: Документ верифицирован, статус: {document.status}")
        
        # Обновление светофора
        color = self.viewmodel.get_status_color(document.status)
        status_text = self.viewmodel.get_status_text(document.status)
        
        with self.status_light.canvas.before:
            self.status_light.canvas.before.clear()
            Color(*color)
            self.status_circle = Ellipse(
                size=(dp(50), dp(50)),
                pos=(
                    self.status_light.x + self.status_light.width / 2 - dp(25),
                    self.status_light.y + self.status_light.height / 2 - dp(25)
                )
            )
        
        # Обновление текста статуса
        details = []
        if document.document_type:
            details.append(f"Тип: {document.document_type}")
        if document.issuer:
            details.append(f"Выдан: {document.issuer}")
        
        status_info = status_text
        if details:
            status_info += "\n" + "\n".join(details)
        
        self.status_text_label.text = status_info
    
    def on_verification_error(self, error_msg: str):
        """Обработка ошибки верификации"""
        Logger.error(f"Scanner: Ошибка верификации: {error_msg}")
        
        # Красный статус при ошибке
        with self.status_light.canvas.before:
            self.status_light.canvas.before.clear()
            Color(0.9, 0.2, 0.2)  # Красный
            self.status_circle = Ellipse(
                size=(dp(50), dp(50)),
                pos=(
                    self.status_light.x + self.status_light.width / 2 - dp(25),
                    self.status_light.y + self.status_light.height / 2 - dp(25)
                )
            )
        
        self.status_text_label.text = f"Ошибка: {error_msg}"
    
    def go_to_history(self, instance):
        """Переход к экрану истории"""
        self.manager.current = 'history'
    
    def on_leave(self):
        """Вызывается при уходе с экрана"""
        self.stop_scanning()

