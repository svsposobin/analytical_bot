from pathlib import Path
from typing import Dict, Any
from json import load as jsonload, JSONDecodeError

from src.handlers.sso.constants import MAX_FILE_SIZE_MB


class FileValidator:

    @staticmethod
    def validate_json_file(file_path: str | Path) -> Dict[str, Any]:
        """Валидирует JSON файл и возвращает его содержимое"""
        path: Path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        max_size: int = MAX_FILE_SIZE_MB * 1024 * 1024
        if path.stat().st_size > max_size:
            raise ValueError(
                f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE_MB}MB, "
                f"текущий: {path.stat().st_size / 1024 / 1024:.2f}MB"
            )

        if not path.is_file():
            raise ValueError(f"Указанный путь не является файлом: {file_path}")

        try:
            with open(path, 'r', encoding='utf-8') as file:
                data = jsonload(file)
        except JSONDecodeError as e:
            raise ValueError(f"Некорректный JSON в файле: {str(e)}")
        except UnicodeDecodeError as e:
            raise ValueError(f"Ошибка кодировки файла: {str(e)}")

        if not isinstance(data, dict):
            raise ValueError("Корневой элемент JSON должен быть объектом")
        if 'videos' not in data:
            raise ValueError("Отсутствует обязательный ключ 'videos' в JSON")
        if not isinstance(data['videos'], list):
            raise ValueError("'videos' должен быть списком")

        return data
