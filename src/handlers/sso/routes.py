from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Any

from aiogram import Router, F
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.sso.processor import UploadRepository
from src.handlers.sso.schemas import UploadJsonSchema
from src.handlers.sso.utils import FileValidator

router: Router = Router(name="upload")


@router.message(F.document & ~F.command)
async def handle_document(
        message: Message,
        db_session: AsyncSession
):
    """Обработчик json-документов"""
    document = message.document

    if not document or not document.file_name or not document.file_name.lower().endswith('.json'):
        await message.answer(
            "❌ Я поддерживаю только JSON-файлы для анализа данных.\n"
            "Используйте команду /uploadjson для загрузки данных."
        )
        return

    processing_msg = await message.answer("🔄 Начинаю обработку файла...")

    try:
        file_info = await message.bot.get_file(document.file_id)  # type: ignore
        downloaded_file = await message.bot.download_file(file_info.file_path)  # type: ignore

        with NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as tmp:
            tmp.write(downloaded_file.read())  # type: ignore
            tmp_path = tmp.name

        try:
            json_data: Dict[str, Any] = FileValidator.validate_json_file(file_path=tmp_path)
            upload_data = UploadJsonSchema.model_validate(json_data)

            await processing_msg.edit_text(
                f"📊 Найдено {len(upload_data.videos)} видео и "
                f"{sum(len(v.snapshots) for v in upload_data.videos)} снапшотов\n"
                "🔄 Начинаю загрузку в базу данных..."
            )

            stats: Dict[str, Any] = await UploadRepository.save_upload_data(
                session=db_session,
                upload_data=upload_data
            )
            report: str = (
                "✅ Данные успешно загружены!\n\n"
                f"📊 Статистика:\n"
                f"• Видео: {stats['videos_created']} создано\n"
                f"• Снапшотов: {stats['snapshots_created']} создано\n\n"
            )

            await processing_msg.edit_text(report)

        except ValueError as error:
            error_text = str(error)
            if len(error_text) > 1000:
                error_text = error_text[:1000] + "..."
            await processing_msg.edit_text(f"❌ Ошибка валидации: {error_text}")

        except Exception as error:
            error_text = str(error)
            if len(error_text) > 1000:
                error_text = error_text[:1000] + "..."
            await processing_msg.edit_text(f"❌ Ошибка при обработке: {error_text}")

        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except Exception as e:
        error_text = str(e)
        if len(error_text) > 1000:
            error_text = error_text[:1000] + "..."
        await processing_msg.edit_text(f"❌ Ошибка при скачивании файла: {error_text}")
