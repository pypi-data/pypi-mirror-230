from nonebot import get_bot
from nonebot.adapters.onebot.v11 import Bot
from nonebot_plugin_session import Session, SessionLevel


async def get_user_nickname(session: Session) -> str:
    bot: Bot = get_bot(session.bot_id)
    if session.level == SessionLevel.LEVEL2:
        user_info = await bot.get_group_member_info(group_id=int(session.id2), user_id=int(session.id1))
        return user_info["card"] or user_info["nickname"]
    else:
        user_info = await bot.get_stranger_info(user_id=int(session.id1))
        return user_info["nickname"]
