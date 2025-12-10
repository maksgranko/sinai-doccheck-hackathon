"""
Сервис экспорта результатов в PDF
KILLER FEATURE #1: Экспорт в PDF с QR-кодом и детальной информацией
"""
from kivy.logger import Logger
from datetime import datetime
from pathlib import Path
import os

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    Logger.warning("PDFExport: reportlab не установлен, экспорт в PDF недоступен")

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    Logger.warning("PDFExport: qrcode не установлен, QR-коды в PDF недоступны")


class PDFExportService:
    """Сервис для экспорта результатов верификации в PDF"""
    
    def __init__(self, output_dir="exports"):
        """
        Инициализация сервиса
        
        Args:
            output_dir: Директория для сохранения PDF файлов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_verification_result(self, document, output_filename=None):
        """
        Экспорт результата верификации в PDF
        
        Args:
            document: DocumentModel объект
            output_filename: Имя файла (если None, генерируется автоматически)
            
        Returns:
            Путь к созданному PDF файлу или None в случае ошибки
        """
        if not REPORTLAB_AVAILABLE:
            Logger.error("PDFExport: reportlab не установлен")
            return None
        
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"verification_{document.document_id}_{timestamp}.pdf"
        
        output_path = self.output_dir / output_filename
        
        try:
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            story = []
            styles = getSampleStyleSheet()
            
            # Заголовок
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1E88E5'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            title = Paragraph("Результат верификации документа", title_style)
            story.append(title)
            story.append(Spacer(1, 12*mm))
            
            # QR-код документа
            if QRCODE_AVAILABLE:
                qr_path = self._generate_qr_code(document.document_id)
                if qr_path and os.path.exists(qr_path):
                    qr_image = Image(str(qr_path), width=60*mm, height=60*mm)
                    story.append(qr_image)
                    story.append(Spacer(1, 5*mm))
            
            # Информация о документе
            doc_data = [
                ['Параметр', 'Значение'],
                ['ID документа', document.document_id],
                ['Статус', self._format_status(document.status)],
            ]
            
            if document.document_type:
                doc_data.append(['Тип документа', document.document_type])
            if document.issuer:
                doc_data.append(['Выдан', document.issuer])
            if document.issue_date:
                doc_data.append(['Дата выдачи', str(document.issue_date)])
            if document.expiry_date:
                doc_data.append(['Срок действия', str(document.expiry_date)])
            
            doc_data.append(['Дата проверки', datetime.now().strftime("%d.%m.%Y %H:%M")])
            
            # Таблица с данными
            table = Table(doc_data, colWidths=[60*mm, 100*mm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E88E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(table)
            story.append(Spacer(1, 10*mm))
            
            # Дополнительная информация
            if document.metadata:
                meta_style = ParagraphStyle(
                    'MetaStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    textColor=colors.HexColor('#666666'),
                    alignment=TA_LEFT
                )
                meta_text = "Дополнительная информация:\n" + str(document.metadata)
                meta_para = Paragraph(meta_text, meta_style)
                story.append(meta_para)
            
            # Создание PDF
            doc.build(story)
            
            Logger.info(f"PDFExport: PDF создан: {output_path}")
            return str(output_path)
            
        except Exception as e:
            Logger.error(f"PDFExport: Ошибка создания PDF: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_qr_code(self, document_id):
        """Генерация QR-кода для документа"""
        if not QRCODE_AVAILABLE:
            return None
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(document_id)
            qr.make(fit=True)
            
            qr_path = self.output_dir / f"qr_{document_id}.png"
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(str(qr_path))
            
            return str(qr_path)
        except Exception as e:
            Logger.error(f"PDFExport: Ошибка генерации QR-кода: {e}")
            return None
    
    def _format_status(self, status):
        """Форматирование статуса для PDF"""
        status_map = {
            'valid': 'Подлинный',
            'warning': 'Предупреждение',
            'invalid': 'Недействителен'
        }
        return status_map.get(status, status)

