from nonebot import get_bot
from nonebot.adapters.qqguild import Bot
from nonebot_plugin_session import Session, SessionIdType

from .cache import cache


async def get_user_nickname(session: Session) -> str:
    cache_key = session.get_id(SessionIdType.GROUP_USER, include_bot_id=False)

    res = cache.get(cache_key)
    if res is None:
        bot: Bot = get_bot(session.bot_id)
        member = await bot.get_member(guild_id=session.id3, user_id=session.id1)
        res = member.nick

    cache[cache_key] = res
    return res
