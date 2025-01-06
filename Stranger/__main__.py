import asyncio
import importlib
from . import app,userbot ,LOGGER_ID, LOGGER
from Stranger.plugins import ALL_MODULES
from pyrogram import idle
from pyrogram.errors import ChannelInvalid, PeerIdInvalid


async def init():
    await app.start()
    await userbot.start()
    for all_module in ALL_MODULES:
        importlib.import_module("Stranger.plugins" + all_module)

    try:
        await app.send_message(chat_id=LOGGER_ID,text="Bot Started")
    except (ChannelInvalid, PeerIdInvalid):
            LOGGER(__name__).error(
                "Bot has failed to access the log group/channel. Make sure that you have added your bot to your log group/channel."
            )
            exit()
    except Exception as ex:
            LOGGER(__name__).error(
                f"Bot has failed to access the log group/channel.\n  Reason : {type(ex).__name__}."
            )
            exit()

    await idle()
    await app.stop()
    await userbot.stop()


if __name__ =="__main__":
    asyncio.get_event_loop().run_until_complete(init())
