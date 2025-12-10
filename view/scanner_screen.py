"""
Экран сканирования QR-кодов
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
try:
    from kivy.uix.camera import Camera
    CAMERA_AVAILABLE = True
except:
    Camera = None
    CAMERA_AVAILABLE = False
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.animation import Animation
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.core.window import Window

try:
    from design.modern_theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_NEUTRAL, STATUS_VALID, STATUS_WARNING, STATUS_INVALID,
        INPUT_HEIGHT, BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY, TEXT_SECONDARY
    )
except ImportError:
    from design.theme import (
        PRIMARY_COLOR, SURFACE_COLOR, BACKGROUND_COLOR, BORDER_RADIUS,
        STATUS_NEUTRAL, STATUS_VALID, STATUS_WARNING, STATUS_INVALID,
        INPUT_HEIGHT, BUTTON_HEIGHT, CARD_PADDING, CARD_SPACING, TEXT_PRIMARY, TEXT_SECONDARY
    )

# Попытка импорта pyzbar
try:
    from pyzbar import pyzbar
except (ImportError, FileNotFoundError, OSError):
    pyzbar = None
    Logger.warning("Scanner: pyzbar недоступен")

# Попытка импорта PIL
try:
    from PIL import Image as PILImage
    PIL_AVAILABLE = True
except ImportError:
    PILImage = None
    PIL_AVAILABLE = False
    Logger.warning("Scanner: PIL/Pillow недоступен")

# Попытка импорта OpenCV для камеры на Windows
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False
    Logger.info("Scanner: OpenCV недоступен")

import io
import threading
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

from viewmodel.scanner_viewmodel import ScannerViewModel
from model.document_model import DocumentModel


class ScannerScreen(Screen):
    """Экран сканирования QR-кодов и штрихкодов"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewmodel = ScannerViewModel()
        self.viewmodel.on_status_changed = self.on_document_verified
        self.viewmodel.on_error = self.on_verification_error
        self.viewmodel.on_loading = self.on_loading_changed
        
        self.camera = None
        self.cv2_camera = None
        self.cv2_image = None
        self.scanning = False
        self.status_light = None
        self.cv2_thread_running = False
        self.last_verified_document = None
        
        self.build_ui()
    
    def build_ui(self):
        """Построение интерфейса - правильная структура без наслоения"""
        # Основной контейнер - без padding для камеры
        layout = BoxLayout(
            orientation='vertical',
            spacing=0
        )
        
        # Заголовок - фиксированная высота
        from design.components import TitleLabel, SecondaryButton, PrimaryButton
        
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(12), dp(8)],
            spacing=dp(10)
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
            text='Сканирование',
            size_hint_x=0.7,
            color=(1, 1, 1, 1)
        )
        
        settings_btn = SecondaryButton(
            text='Настройки',
            size_hint_x=0.3,
            color=(1, 1, 1, 1),
            on_press=lambda x: setattr(self.manager, 'current', 'settings')
        )
        
        header.add_widget(title)
        header.add_widget(settings_btn)
        layout.add_widget(header)
        
        # Контейнер для камеры - занимает всё доступное пространство
        camera_container = BoxLayout(
            orientation='vertical',
            size_hint_y=1
        )
        
        # Инициализация камеры
        self.camera_available = False
        
        # Пробуем стандартную камеру Kivy
        if CAMERA_AVAILABLE and Camera is not None:
            try:
                self.camera = Camera(
                    resolution=(640, 480),
                    play=False,
                    size_hint=(1, 1)
                )
                camera_container.add_widget(self.camera)
                self.camera_available = True
                Logger.info("Scanner: Камера Kivy инициализирована")
            except Exception as e:
                Logger.warning(f"Scanner: Камера Kivy недоступна: {e}")
                self.camera_available = False
        
        # Пробуем OpenCV камеру
        if not self.camera_available and CV2_AVAILABLE:
            try:
                self.cv2_camera = cv2.VideoCapture(0)
                if self.cv2_camera.isOpened():
                    self.cv2_camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cv2_camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.camera_available = True
                    Logger.info("Scanner: Камера OpenCV инициализирована")
                    
                    self.cv2_image = Image(size_hint=(1, 1))
                    camera_container.add_widget(self.cv2_image)
                    
                    self.cv2_thread_running = True
                    threading.Thread(target=self._update_cv2_frame, daemon=True).start()
                else:
                    self.cv2_camera = None
            except Exception as e:
                Logger.warning(f"Scanner: Ошибка OpenCV камеры: {e}")
                self.camera_available = False
        
        # Заглушка если камера недоступна
        if not self.camera_available:
            from design.components import BodyLabel
            placeholder = BodyLabel(
                text='Камера недоступна\nИспользуйте поле ввода ниже',
                size_hint=(1, 1),
                halign='center',
                valign='middle',
                text_size=(None, None)
            )
            placeholder.bind(texture_size=placeholder.setter('size'))
            camera_container.add_widget(placeholder)
        
        layout.add_widget(camera_container)
        
        # Нижняя панель с функционалом - адаптивная высота
        from kivy.core.window import Window
        is_mobile = Window.width < 400
        bottom_panel_height = dp(260) if is_mobile else dp(250)
        
        bottom_panel = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=bottom_panel_height,
            padding=[dp(10), dp(8)],
            spacing=dp(8)
        )
        
        # Статус - компактный
        from design.components import Card, BodyLabel
        
        # Адаптивная высота карточки статуса для длинного текста
        from kivy.core.window import Window
        is_mobile = Window.width < 400
        status_card_height = dp(70) if is_mobile else dp(55)
        
        status_card = Card(
            orientation='horizontal',
            size_hint_y=None,
            height=status_card_height,
            spacing=dp(10),
            padding=[dp(10), dp(8)]
        )
        
        # Индикатор статуса
        self.status_light = BoxLayout(
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'center_y': 0.5}
        )
        
        with self.status_light.canvas.before:
            Color(*STATUS_NEUTRAL)
            self.status_circle = RoundedRectangle(
                size=self.status_light.size,
                pos=self.status_light.pos,
                radius=[dp(15), dp(15), dp(15), dp(15)]
            )
            # Внешнее кольцо для эффекта
            Color(STATUS_NEUTRAL[0], STATUS_NEUTRAL[1], STATUS_NEUTRAL[2], 0.3)
            self.status_ring = RoundedRectangle(
                size=(dp(40), dp(40)),
                pos=(self.status_light.pos[0] - dp(5), self.status_light.pos[1] - dp(5)),
                radius=[dp(20), dp(20), dp(20), dp(20)]
            )
        
        def update_status_ring(instance, value):
            if hasattr(self, 'status_ring'):
                self.status_ring.pos = (self.status_light.pos[0] - dp(5), self.status_light.pos[1] - dp(5))
        
        self.status_light.bind(pos=update_status_ring)
        def update_status_light_callback(instance, value):
            self.update_status_light(instance, value)
        
        self.status_light.bind(size=update_status_light_callback, pos=update_status_light_callback)
        
        # Текст статуса - с поддержкой переноса строк и адаптивным размером
        from kivy.core.window import Window
        is_mobile = Window.width < 400
        status_font_size = dp(11) if is_mobile else dp(12)
        
        self.status_text_label = BodyLabel(
            text='Наведите камеру на QR-код',
            size_hint_x=1,
            halign='left',
            valign='top' if is_mobile else 'middle',
            text_size=(None, None),
            font_size=status_font_size,
            max_lines=4 if is_mobile else 3  # Больше строк на мобильных
        )
        
        # Индикатор загрузки (анимированная точка)
        self.loading_indicator = Label(
            text='',
            size_hint=(None, None),
            size=(dp(20), dp(20)),
            pos_hint={'center_y': 0.5}
        )
        self.loading_animation = None
        
        # Функция для обновления размера текста
        def update_text_size(instance, value):
            if hasattr(instance, 'width') and instance.width:
                instance.text_size = (instance.width - dp(10), None)
        
        self.status_text_label.bind(width=update_text_size)
        self.status_text_label.bind(texture_size=self.status_text_label.setter('size'))
        
        status_card.add_widget(self.status_light)
        status_card.add_widget(self.status_text_label)
        status_card.add_widget(self.loading_indicator)  # Добавляем индикатор загрузки
        bottom_panel.add_widget(status_card)
        
        # Поле для ручного ввода QR-кода
        from design.components import PrimaryButton
        
        input_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )
        
        # Стандартное поле ввода
        self.qr_input = TextInput(
            hint_text='Или введите код вручную',
            size_hint_x=0.7,
            multiline=False,
            background_color=(1, 1, 1, 1),
            foreground_color=(0, 0, 0, 1),
            font_size=dp(14),
            padding_x=dp(8),
            padding_y=dp(8)
        )
        
        # Кнопка проверки
        verify_btn = PrimaryButton(
            text='Проверить',
            size_hint_x=0.3,
            on_press=self.verify_manual_input
        )
        
        input_row.add_widget(self.qr_input)
        input_row.add_widget(verify_btn)
        bottom_panel.add_widget(input_row)
        
        # Кнопки управления - улучшенный layout с новыми фичами
        from design.components import SecondaryButton
        
        # Верхний ряд кнопок - три кнопки
        top_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),
            spacing=dp(6)
        )
        
        if self.camera_available:
            self.start_button = PrimaryButton(
                text='Сканировать',
                size_hint_x=0.4,
                on_press=self.toggle_scanning
            )
        else:
            self.start_button = SecondaryButton(
                text='Камера недоступна',
                size_hint_x=0.4,
                disabled=True
            )
        
        self.stats_button = SecondaryButton(
            text='Статистика',
            size_hint_x=0.3,
            on_press=self.go_to_statistics
        )
        
        search_button = SecondaryButton(
            text='Поиск',
            size_hint_x=0.3,
            on_press=self.go_to_search
        )
        
        top_buttons.add_widget(self.start_button)
        top_buttons.add_widget(self.stats_button)
        top_buttons.add_widget(search_button)
        bottom_panel.add_widget(top_buttons)
        
        # Нижний ряд кнопок
        bottom_buttons = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )
        
        self.history_button = SecondaryButton(
            text='История',
            size_hint_x=0.5,
            on_press=self.go_to_history
        )
        
        self.export_button = SecondaryButton(
            text='Экспорт PDF',
            size_hint_x=0.5,
            on_press=self.export_to_pdf,
            disabled=True  # Будет активирована после верификации
        )
        
        bottom_buttons.add_widget(self.history_button)
        bottom_buttons.add_widget(self.export_button)
        bottom_panel.add_widget(bottom_buttons)
        
        layout.add_widget(bottom_panel)
        self.add_widget(layout)
        Logger.info("Scanner: Интерфейс построен")
    
    def update_status_light(self, *args):
        """Обновление позиции индикатора статуса"""
        if hasattr(self, 'status_circle'):
            self.status_circle.pos = self.status_light.pos
            self.status_circle.size = self.status_light.size
        if hasattr(self, 'status_ring') and hasattr(self.status_light, 'pos'):
            self.status_ring.pos = (self.status_light.pos[0] - dp(5), self.status_light.pos[1] - dp(5))
    
    def toggle_scanning(self, instance):
        """Переключение режима сканирования"""
        if not self.scanning:
            self.start_scanning()
        else:
            self.stop_scanning()
    
    def start_scanning(self):
        """Запуск сканирования"""
        if self.camera_available:
            try:
                self.scanning = True
                self.start_button.text = 'Остановить'
                self.status_text_label.text = 'Сканирование...'
                
                if self.camera:
                    self.camera.play = True
                    Clock.schedule_interval(self.scan_qr_code, 0.5)
                
                # Анимация индикатора
                self.status_text_label.text = 'Сканирование... Наведите камеру на QR-код'
                anim = Animation(size=(dp(45), dp(45)), duration=0.5) + Animation(size=(dp(40), dp(40)), duration=0.5)
                anim.repeat = True
                anim.start(self.status_light)
                
                Logger.info("Scanner: Сканирование запущено")
            except Exception as e:
                Logger.error(f"Scanner: Ошибка запуска: {e}")
        else:
            self.status_text_label.text = 'Камера недоступна. Используйте ручной ввод.'
    
    def stop_scanning(self):
        """Остановка сканирования"""
        self.scanning = False
        
        if self.camera:
            self.camera.play = False
            Clock.unschedule(self.scan_qr_code)
        
        # Остановка анимации
        Animation.cancel_all(self.status_light)
        if hasattr(self, 'start_button'):
            self.start_button.text = 'Начать сканирование'
        
        Logger.info("Scanner: Сканирование остановлено")
    
    def _update_cv2_frame(self):
        """Обновление кадров с OpenCV камеры"""
        from kivy.clock import Clock
        import time
        while hasattr(self, 'cv2_thread_running') and self.cv2_thread_running and self.cv2_camera:
            try:
                ret, frame = self.cv2_camera.read()
                if ret and PIL_AVAILABLE:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_flipped = cv2.flip(frame_rgb, 0)
                    pil_image = PILImage.fromarray(frame_flipped)
                    
                    Clock.schedule_once(lambda dt: self._update_cv2_texture(pil_image), 0)
                    
                    if self.scanning and PIL_AVAILABLE:
                        document_id = None
                        
                        if pyzbar:
                            try:
                                barcodes = pyzbar.decode(pil_image)
                                if barcodes:
                                    document_id = barcodes[0].data.decode('utf-8')
                                    Logger.info(f"Scanner: Найден код через pyzbar: {document_id}")
                            except:
                                pass
                        
                        if not document_id and CV2_AVAILABLE:
                            try:
                                qr_detector = cv2.QRCodeDetector()
                                retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(frame)
                                if retval and decoded_info:
                                    for info in decoded_info:
                                        if info:
                                            document_id = info
                                            Logger.info(f"Scanner: Найден код через OpenCV: {document_id}")
                                            break
                            except:
                                pass
                        
                        if document_id:
                            Clock.schedule_once(lambda dt, doc_id=document_id: self._process_qr_code(doc_id), 0)
                
                time.sleep(0.033)
            except Exception as e:
                Logger.error(f"Scanner: Ошибка обновления кадра: {e}")
                break
    
    def _update_cv2_texture(self, pil_image):
        """Обновление текстуры изображения OpenCV"""
        if hasattr(self, 'cv2_image') and self.cv2_image:
            try:
                from kivy.core.image import Image as CoreImage
                import io
                img_bytes = io.BytesIO()
                pil_image.save(img_bytes, format='png')
                img_bytes.seek(0)
                self.cv2_image.texture = CoreImage(img_bytes, ext='png').texture
            except Exception as e:
                Logger.error(f"Scanner: Ошибка обновления текстуры: {e}")
    
    def _process_qr_code(self, document_id):
        """Обработка найденного QR-кода"""
        # Валидация перед обработкой
        if not document_id or len(document_id.strip()) < 3:
            self.status_text_label.text = 'Неверный формат QR-кода'
            return
        
        self.stop_scanning()
        self.status_text_label.text = 'Верификация...'
        from security.pin_storage import PinStorage
        pin_storage = PinStorage()
        pin_code = pin_storage.get_pin()
        self.viewmodel.verify_document(document_id.strip(), pin_code)
    
    def scan_qr_code(self, dt):
        """Сканирование QR-кода с камеры (для стандартной камеры Kivy)"""
        if self.cv2_camera:
            return
        
        if not self.camera or not self.camera_available or not self.camera.texture:
            return
        
        if not PIL_AVAILABLE:
            return
        
        try:
            texture = self.camera.texture
            size = texture.size
            pixels = texture.pixels
            
            pil_image = PILImage.frombytes('RGBA', size, pixels)
            pil_image = pil_image.convert('RGB')
            
            document_id = None
            
            if pyzbar:
                try:
                    barcodes = pyzbar.decode(pil_image)
                    if barcodes:
                        document_id = barcodes[0].data.decode('utf-8')
                        Logger.info(f"Scanner: Найден код через pyzbar: {document_id}")
                except:
                    pass
            
            if not document_id and CV2_AVAILABLE:
                try:
                    import numpy as np
                    frame = np.array(pil_image)
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    
                    qr_detector = cv2.QRCodeDetector()
                    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(frame_bgr)
                    if retval and decoded_info:
                        for info in decoded_info:
                            if info:
                                document_id = info
                                Logger.info(f"Scanner: Найден код через OpenCV: {document_id}")
                                break
                except Exception as e:
                    Logger.debug(f"Scanner: Ошибка сканирования QR через OpenCV: {e}")
            
            if document_id:
                self.stop_scanning()
                self.status_text_label.text = 'Верификация...'
                from security.pin_storage import PinStorage
                pin_storage = PinStorage()
                pin_code = pin_storage.get_pin()
                self.viewmodel.verify_document(document_id, pin_code)
        
        except Exception as e:
            Logger.debug(f"Scanner: Ошибка сканирования: {e}")
    
    def verify_manual_input(self, instance):
        """Верификация документа по введенному вручную QR-коду"""
        if hasattr(self, 'qr_input'):
            document_id = self.qr_input.text.strip()
            if document_id:
                # Валидация перед отправкой
                if len(document_id) < 3:
                    self.status_text_label.text = 'ID документа слишком короткий'
                    return
                self.status_text_label.text = 'Верификация...'
                from security.pin_storage import PinStorage
                pin_storage = PinStorage()
                pin_code = pin_storage.get_pin()
                self.viewmodel.verify_document(document_id, pin_code)
                # Очищаем поле ввода после начала верификации
                self.qr_input.text = ''
            else:
                self.status_text_label.text = 'Введите QR-код документа'
    
    def on_document_verified(self, document: DocumentModel):
        """Обработка результата верификации"""
        Logger.info(f"Scanner: Документ верифицирован, статус: {document.status}")
        
        color = self.viewmodel.get_status_color(document.status)
        status_text = self.viewmodel.get_status_text(document.status)
        
        # Анимация изменения цвета статуса
        with self.status_light.canvas.before:
            self.status_light.canvas.before.clear()
            # Внешнее кольцо
            Color(color[0], color[1], color[2], 0.3)
            self.status_ring = RoundedRectangle(
                size=(dp(50), dp(50)),
                pos=(self.status_light.pos[0] - dp(5), self.status_light.pos[1] - dp(5)),
                radius=[dp(25), dp(25), dp(25), dp(25)]
            )
            # Основной круг
            Color(*color)
            self.status_circle = RoundedRectangle(
                size=self.status_light.size,
                pos=self.status_light.pos,
                radius=[dp(20), dp(20), dp(20), dp(20)]
            )
        
        # Формирование детальной информации - компактное отображение
        details = []
        if document.document_type:
            # Сокращаем длинные типы документов
            doc_type = document.document_type
            if len(doc_type) > 20:
                doc_type = doc_type[:17] + "..."
            details.append(f"Тип: {doc_type}")
        if document.issuer:
            # Сокращаем длинные названия организаций
            issuer = document.issuer
            if len(issuer) > 25:
                issuer = issuer[:22] + "..."
            details.append(f"Выдан: {issuer}")
        if document.expiry_date:
            from datetime import date
            if isinstance(document.expiry_date, date):
                days_left = (document.expiry_date - date.today()).days
                if days_left > 0:
                    details.append(f"До: {document.expiry_date.strftime('%d.%m.%Y')} ({days_left}д)")
                else:
                    details.append(f"Истек: {document.expiry_date.strftime('%d.%m.%Y')}")
            else:
                expiry_str = str(document.expiry_date)
                if len(expiry_str) > 15:
                    expiry_str = expiry_str[:12] + "..."
                details.append(f"До: {expiry_str}")
        
        # Формируем текст статуса с переносами строк для лучшей читаемости
        status_info = status_text
        if details:
            # Используем переносы строк вместо разделителей для мобильных устройств
            from kivy.core.window import Window
            is_mobile = Window.width < 400
            if is_mobile:
                status_info = status_text + "\n" + "\n".join(details)
            else:
                status_info = status_text + " | " + " | ".join(details)
        
        self.status_text_label.text = status_info
        # Обновляем размер текста после установки
        if hasattr(self.status_text_label, 'width'):
            self.status_text_label.text_size = (self.status_text_label.width, None)
        
        # Сохранение документа для экспорта
        self.last_verified_document = document
        
        # Активация кнопки экспорта
        if hasattr(self, 'export_button'):
            self.export_button.disabled = False
        
        # Кэширование для офлайн режима
        try:
            from services.offline_cache import OfflineCache
            cache = OfflineCache()
            cache.cache_document(document)
        except Exception as e:
            Logger.warning(f"Scanner: Не удалось закэшировать документ: {e}")
        
        # Анимация пульсации для успешной верификации
        if document.status == 'valid':
            anim = Animation(size=(dp(45), dp(45)), duration=0.3) + Animation(size=(dp(40), dp(40)), duration=0.3)
            anim.start(self.status_light)
    
    def on_loading_changed(self, loading: bool):
        """Обработка изменения состояния загрузки"""
        if loading:
            # Показываем анимацию загрузки
            if hasattr(self, 'loading_indicator'):
                self.loading_indicator.text = '...'
                from kivy.animation import Animation
                anim = Animation(opacity=0.3, duration=0.5) + Animation(opacity=1.0, duration=0.5)
                anim.repeat = True
                self.loading_animation = anim
                anim.start(self.loading_indicator)
        else:
            # Скрываем анимацию
            if hasattr(self, 'loading_indicator'):
                if hasattr(self, 'loading_animation') and self.loading_animation:
                    self.loading_animation.cancel(self.loading_indicator)
                    self.loading_animation = None
                self.loading_indicator.text = ''
                self.loading_indicator.opacity = 1.0
    
    def on_verification_error(self, error_msg: str):
        """Обработка ошибки верификации"""
        Logger.error(f"Scanner: Ошибка верификации: {error_msg}")
        
        # Улучшенное отображение ошибки
        error_display = error_msg
        if len(error_msg) > 60:
            error_display = error_msg[:57] + "..."
        
        self.status_text_label.text = error_display
        
        # Останавливаем анимацию загрузки
        if hasattr(self, 'loading_animation') and self.loading_animation:
            self.loading_animation.cancel(self.loading_indicator)
            self.loading_animation = None
            self.loading_indicator.text = ''
        
        with self.status_light.canvas.before:
            self.status_light.canvas.before.clear()
            Color(*STATUS_INVALID)
            self.status_circle = RoundedRectangle(
                size=self.status_light.size,
                pos=self.status_light.pos,
                radius=[dp(25), dp(25), dp(25), dp(25)]
            )
        
        self.status_text_label.text = f"Ошибка: {error_msg}"
    
    def go_to_history(self, instance):
        """Переход к экрану истории"""
        self.manager.current = 'history'
    
    def go_to_statistics(self, instance):
        """Переход к экрану статистики"""
        self.manager.current = 'statistics'
    
    def go_to_search(self, instance):
        """Переход к экрану поиска"""
        self.manager.current = 'search'
    
    def export_to_pdf(self, instance):
        """Экспорт результата верификации в PDF"""
        if not self.last_verified_document:
            self.status_text_label.text = 'Нет данных для экспорта'
            return
        
        try:
            from services.pdf_export import PDFExportService
            export_service = PDFExportService()
            pdf_path = export_service.export_verification_result(self.last_verified_document)
            
            if pdf_path:
                from kivy.uix.popup import Popup
                from kivy.uix.label import Label
                from kivy.uix.boxlayout import BoxLayout as PopupBoxLayout
                
                content = PopupBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
                content.add_widget(Label(
                    text=f'PDF создан:\n{pdf_path}',
                    text_size=(None, None),
                    halign='center'
                ))
                
                close_btn = PrimaryButton(text='OK', size_hint_y=None, height=dp(40))
                popup = Popup(
                    title='Экспорт успешен',
                    content=content,
                    size_hint=(0.8, 0.4)
                )
                close_btn.bind(on_press=popup.dismiss)
                content.add_widget(close_btn)
                popup.open()
                
                self.status_text_label.text = f'PDF экспортирован: {pdf_path.split("/")[-1]}'
            else:
                self.status_text_label.text = 'Ошибка экспорта PDF'
        except ImportError:
            self.status_text_label.text = 'PDF экспорт недоступен (установите reportlab)'
        except Exception as e:
            Logger.error(f"Scanner: Ошибка экспорта PDF: {e}")
            self.status_text_label.text = f'Ошибка: {str(e)}'
    
    def on_leave(self):
        """Вызывается при уходе с экрана"""
        self.stop_scanning()
        if hasattr(self, 'cv2_thread_running'):
            self.cv2_thread_running = False
        if self.cv2_camera:
            self.cv2_camera.release()
            self.cv2_camera = None
