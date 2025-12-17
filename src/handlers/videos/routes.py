from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ChatAction
from sqlalchemy.ext.asyncio import AsyncSession

from src.handlers.sso.text_handler import text_query_handler
from src.handlers.videos.schemas import QueryResponse

router: Router = Router(name="text_router")


@router.message(F.text & ~F.command)
async def handle_text_query(message: Message, db_session: AsyncSession) -> None:
    user_query: str = message.text.strip()  # type: ignore
    if len(user_query) < 3:
        await message.answer("❌ Запрос слишком короткий. Пожалуйста, задайте более развернутый вопрос.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)  # type: ignore

    result: QueryResponse = await text_query_handler.process_text_query(
        user_query=user_query,
        session=db_session
    )

    if not result.status:
        await message.answer(str(result.details))
    else:
        await message.answer(str(result.result))
