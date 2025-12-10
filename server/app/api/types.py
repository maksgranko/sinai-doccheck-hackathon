"""
API endpoints для типов документов
"""
from fastapi import APIRouter
from typing import List

router = APIRouter()


@router.get("/document-types")
async def get_document_types():
    """
    Получение списка типов документов
    """
    return {
        "types": [
            "Справка",
            "Сертификат",
            "Удостоверение",
            "Лицензия",
            "Диплом",
            "Аттестат"
        ]
    }


@router.get("/verification-templates")
async def get_verification_templates():
    """
    Получение шаблонов проверки документов
    """
    return {
        "templates": [
            {
                "id": "template1",
                "name": "Стандартная проверка",
                "checks": ["validity", "issuer", "signature", "expiry"]
            },
            {
                "id": "template2",
                "name": "Расширенная проверка",
                "checks": ["validity", "issuer", "signature", "expiry", "revocation", "chain"]
            }
        ]
    }



