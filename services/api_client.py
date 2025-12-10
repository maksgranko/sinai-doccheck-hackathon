"""
HTTP-клиент для обращения к внешнему PHP API.
"""
import json
import time
from urllib import request, error, parse
from typing import Optional, Dict, Any

from kivy.logger import Logger

import config
from model.document_model import DocumentModel


class ApiClient:
    """Минимальный клиент для verify/document"""

    def __init__(self):
        self.base_url = config.API_BASE_URL.rstrip("/")
        self.verify_path = config.API_VERIFY_PATH
        self.document_path = config.API_DOCUMENT_PATH
        self.timeout = config.HTTP_TIMEOUT
        self.max_retries = config.MAX_RETRIES

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = json.dumps(payload).encode("utf-8") if payload is not None else None

        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8") if resp.length is None or resp.length > 0 else ""
                return json.loads(body) if body else {}
        except error.HTTPError as e:
            # Читаем тело ошибки, если есть
            try:
                body = e.read().decode("utf-8")
                return json.loads(body) if body else {"status": "error", "message": str(e)}
            except Exception:
                return {"status": "error", "message": str(e)}
        except error.URLError as e:
            raise ConnectionError(f"Ошибка сети: {e}") from e
        except TimeoutError as e:
            raise

    def verify_document(self, public_code: str, pin_code: Optional[str] = None) -> DocumentModel:
        """
        POST verify.
        """
        payload = {"public_code": public_code}
        if pin_code:
            payload["pin"] = pin_code

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self._request("POST", self.verify_path, payload)
                return self._parse_document_response(public_code, response)
            except (ConnectionError, TimeoutError) as e:
                last_exc = e
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt
                    Logger.warning(f"ApiClient: Повтор через {delay}с из-за {e}")
                    time.sleep(delay)
                else:
                    raise e

        raise last_exc or ConnectionError("Неизвестная ошибка запроса")

    def get_document(self, public_code: str) -> DocumentModel:
        """
        GET document. Для совместимости используем query-параметр public_code.
        """
        query = parse.urlencode({"public_code": public_code})
        path = f"{self.document_path}?{query}"

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self._request("GET", path)
                return self._parse_document_response(public_code, response)
            except (ConnectionError, TimeoutError) as e:
                last_exc = e
                if attempt < self.max_retries - 1:
                    delay = 2 ** attempt
                    Logger.warning(f"ApiClient: Повтор через {delay}с из-за {e}")
                    time.sleep(delay)
                else:
                    raise e

        raise last_exc or ConnectionError("Неизвестная ошибка запроса")

    @staticmethod
    def _parse_document_response(public_code: str, response: Dict[str, Any]) -> DocumentModel:
        """
        Преобразуем ответ API в DocumentModel.
        Ожидаем структуру вида:
        { "status": "ok", "data": { "public_code": "...", "status": "valid", ... } }
        или { "status": "error", "message": "..." }
        """
        if not isinstance(response, dict):
            return DocumentModel(
                document_id=public_code,
                status="invalid",
                metadata={"error": "Не является документом"}
            )

        if response.get("status") == "ok":
            data = response.get("data", {})
            return DocumentModel(
                document_id=data.get("public_code", public_code),
                status=data.get("status", "invalid"),
                document_type=data.get("document_type"),
                issuer=data.get("issuer"),
                issue_date=data.get("issue_date"),
                expiry_date=data.get("expiry_date"),
                metadata=data.get("metadata"),
            )

        # Ошибка от API
        message = response.get("message") or response.get("error") or "Не является документом"
        return DocumentModel(
            document_id=public_code,
            status="invalid",
            metadata={"error": message}
        )


