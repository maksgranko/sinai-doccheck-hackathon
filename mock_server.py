"""
Mock сервер для тестирования приложения
Запуск: python mock_server.py
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs


class MockAPIHandler(BaseHTTPRequestHandler):
    """Обработчик запросов к mock API"""
    
    # Mock база данных документов
    MOCK_DOCUMENTS = {
        "DOC001": {
            "document_id": "DOC001",
            "status": "valid",
            "document_type": "Справка",
            "issuer": "Госструктура",
            "issue_date": "2024-01-15",
            "expiry_date": "2025-01-15",
            "metadata": {}
        },
        "DOC002": {
            "document_id": "DOC002",
            "status": "warning",
            "document_type": "Сертификат",
            "issuer": "Банк",
            "issue_date": "2023-06-01",
            "expiry_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "metadata": {"warning": "Срок действия истекает через 10 дней"}
        },
        "DOC003": {
            "document_id": "DOC003",
            "status": "invalid",
            "document_type": "Справка",
            "issuer": "Организация",
            "issue_date": "2023-01-01",
            "expiry_date": "2024-01-01",
            "metadata": {"error": "Документ отозван"}
        }
    }
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-PIN-Code')
        self.end_headers()
    
    def do_POST(self):
        """Обработка POST запросов"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/v1/documents/verify':
            self.handle_verify_document()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_GET(self):
        """Обработка GET запросов"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/v1/document-types':
            self.handle_get_document_types()
        elif parsed_path.path == '/v1/verification-templates':
            self.handle_get_templates()
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_verify_document(self):
        """Обработка запроса верификации документа"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            document_id = data.get('document_id')
            pin_code = self.headers.get('X-PIN-Code')
            
            # Проверка PIN (для демонстрации)
            if pin_code and pin_code != "1234":
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "error": "Неверный PIN-код"
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Поиск документа
            if document_id in self.MOCK_DOCUMENTS:
                document = self.MOCK_DOCUMENTS[document_id]
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(document).encode())
            else:
                # Документ не найден
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "document_id": document_id,
                    "status": "invalid",
                    "error": "Документ не найден в реестре"
                }
                self.wfile.write(json.dumps(response).encode())
        
        except Exception as e:
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def handle_get_document_types(self):
        """Обработка запроса типов документов"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "types": ["Справка", "Сертификат", "Удостоверение", "Лицензия"]
        }
        self.wfile.write(json.dumps(response).encode())
    
    def handle_get_templates(self):
        """Обработка запроса шаблонов проверки"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "templates": [
                {
                    "id": "template1",
                    "name": "Стандартная проверка",
                    "checks": ["validity", "issuer", "signature"]
                }
            ]
        }
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Переопределение логирования"""
        print(f"[Mock Server] {format % args}")


def run_server(port=8000):
    """Запуск mock сервера"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockAPIHandler)
    print(f"Mock API сервер запущен на http://localhost:{port}")
    print("Доступные endpoints:")
    print("  POST /v1/documents/verify")
    print("  GET /v1/document-types")
    print("  GET /v1/verification-templates")
    print("\nТестовые документы:")
    print("  DOC001 - валидный документ")
    print("  DOC002 - документ с предупреждением")
    print("  DOC003 - недействительный документ")
    print("\nДля остановки нажмите Ctrl+C")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
        httpd.shutdown()


if __name__ == '__main__':
    run_server()



