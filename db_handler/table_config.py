# Конфигурация таблиц базы данных
TABLES_CONFIG = {
    "users": {
        "columns": {
            "id": "BIGINT PRIMARY KEY",
            "name": "VARCHAR(255)"
        },
        "description": "Таблица пользователей"
    },
    "vocab_request_stage": {
        "columns": {
            "id": "BIGSERIAL PRIMARY KEY",
            "codeName": "VARCHAR(50)",
            "name": "VARCHAR(255)"
        },
        "description": "Справочник этапов запроса",
        "initial_data": [
            {"codeName": "requestForTitle", "name": "Запрос поиска"},
            {"codeName": "lookForTitle", "name": "Поиск по названию"},
            {"codeName": "checkIfRight", "name": "Проверка верности поиска"},
            {"codeName": "lookForReviewsAndPrices", "name": "Поиск отзывов и цен"}
        ]
    },
    "requests": {
        "columns": {
            "id": "BIGSERIAL PRIMARY KEY",
            "name": "VARCHAR(255)",
            "madeat": "TIMESTAMP",
            "success": "BOOLEAN",
            "stage": "BIGINT REFERENCES vocab_request_stage(id)",
            "user_id": "BIGINT REFERENCES users(id) ON DELETE CASCADE"
        },
        "description": "Таблица запросов пользователей"
    },
    "response": {
        "columns": {
            "id": "BIGSERIAL PRIMARY KEY",
            "request_id": "BIGINT REFERENCES requests(id) ON DELETE CASCADE",
            "user_id": "BIGINT REFERENCES users(id) ON DELETE CASCADE",
            "ai_response": "TEXT",
            "marketplace_reviews": "JSONB",
            "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        },
        "description": "Таблица ответов и отзывов",
        "indexes": [
            "CREATE INDEX IF NOT EXISTS idx_response_request_id ON response(request_id)",
            "CREATE INDEX IF NOT EXISTS idx_response_user_id ON response(user_id)"
        ]
    }
} 