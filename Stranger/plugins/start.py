import re
import os
import time
import asyncio

from pyromod.exceptions import ListenerTimeout
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, FloodWait
from pyrogram.enums import MessageMediaType
from Stranger import app , OWNER_ID, userbot , LOGGER_ID
from Stranger.plugins.helpers import get_link, progress_for_pyrogram

queue = []
pattern = "https://t.me/(?:c/)?(.*)/(\d+)"

async def clone(sender , s_channel_id, des_channel_id , i, channel_id):
    try:
        msg = await userbot.get_messages(s_channel_id , i)
        file = await userbot.download_media(
            msg,
            in_memory=True
            )
        caption = None
        if msg.caption is not None:
            caption = msg.caption
        if msg.media==MessageMediaType.VIDEO_NOTE:              
            await userbot.send_video_note(
                chat_id=des_channel_id,
                video_note=file,
            )
        elif msg.media==MessageMediaType.VIDEO and msg.video.mime_type in ["video/mp4", "video/x-matroska"]:
            await userbot.send_video(
                chat_id=des_channel_id,
                video=file,
                caption=caption,
                supports_streaming=True,
            )
        elif msg.media==MessageMediaType.PHOTO:
            await userbot.send_photo(des_channel_id, file, caption=caption)
        else:
            await userbot.send_document(
                des_channel_id,
                file, 
                caption=caption,
            )
        try:
            os.remove(file)
            if os.path.isfile(file) == True:
                os.remove(file)
        except Exception:
            pass

        await app.send_message(LOGGER_ID,"https://t.me/c/{}/{}".format(channel_id,i))
    except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
        await app.send_message(sender, "Have you joined the channel?")
        return
    except FloodWait as fw:
        await asyncio.sleep(int(fw.x) + 10)
        return await clone(sender , s_channel_id, des_channel_id , i, channel_id ,xx)
    except Exception as e:
        print(e)
        return

async def run_batch(sender ,d, s, start_msg_id, end_msg_id, channel_id):
    yy = await app.send_message(sender,".")
    total = end_msg_id-start_msg_id
    for i in range(start_msg_id,end_msg_id+1):
        if (i//10) == 0:
            await yy.edit(f"Sending message {i-start_msg_id + 1} of {total}...")
        try: 
            if not sender in queue:
                await app.send_message(sender, "Batch completed.")
                break
        except Exception as e:
            print(e)
            await app.send_message(sender, "Batch completed.")
            break
        try:
            await clone(sender , s, d, i, channel_id)
        except FloodWait as fw:
            await app.send_message(sender, "Floodwait {}".format(int(fw.x)))
            await asyncio.sleep(int(fw.x) + 5)
            await clone(sender ,s, d, i, channel_id, xx)
        await asyncio.sleep(60)
        

@app.on_message(filters.command("cancel") & filters.private & filters.user(OWNER_ID))
async def cancel(client, message:Message):
    if not message.from_user.id in queue:
        return await message.reply_text("No tasks to cancel.")
    queue.clear()
    await message.reply_text("Tasks cancelled.")

@app.on_message(filters.command("start") & filters.private & filters.user(OWNER_ID))
async def batch(client, message:Message):
    sender = message.from_user.id
    s_channel_id =None
    if sender in queue:
        return await message.reply_text("You already have a batch running.")
    chat = message.chat
    while True:
        try:
            response = await chat.ask("Send me the destination channel link", timeout=60)
        except ListenerTimeout:
            return await message.reply_text("No response received.")
        link = response.text
        if not link:
            await response.reply("Not a valid link found. Try again")
            continue
        try:
            des = await userbot.get_chat(link)
            des_channel_id = des.id
            break
        except Exception as e:
            print(e)
            await response.reply("Not a valid link found. Try again")
            continue

    while True:
        try:
            response = await chat.ask("Send me the message link you want to start saving from", timeout=60)
        except ListenerTimeout:
            return await message.reply_text("No response received.")
  
        try:
            matches = re.match(pattern, response.text)
            if not matches:
                await response.reply("Not a valid link found. Try again")
                continue
            channel_id = matches.group(1)
            s_channel_id= int(f"-100{channel_id}")
            start_msg_id = int(matches.group(2))
            break
        except Exception as e:
            print(e)
            await response.reply("Not a valid link found. Try again")
            continue
    
    while True:
        try:
            response = await chat.ask("Send me the message link until where you want to save", timeout=60)
        except ListenerTimeout:
            return await message.reply_text("No response received.")
        
        try:
            d_link = get_link(response.text)
            if not d_link:
                await response.reply("Not a valid link found. Try again")
                continue
            matches = re.match(pattern, response.text)
            if not matches:
                await response.reply("Not a valid link found. Try again")
                continue
            channel_id = matches.group(1)
            if s_channel_id != int(f"-100{channel_id}"):
                await response.reply("Ending msg link is not from the same source channel . Try again")
                continue
            end_msg_id = int(matches.group(2))
            break
        except Exception as e:
            print(e)
            await message.reply_text("No link found.")
            break

    queue.append(sender)
    await app.send_message(LOGGER_ID,"Batch started. Messages will be saved between {} and {}".format(s_channel_id,des_channel_id))
    if start_msg_id == end_msg_id:
        return await message.reply_text("start msg id and end msg id can't be same. Cancelling the process")
    elif start_msg_id > end_msg_id:
        x = start_msg_id
        start_msg_id = end_msg_id
        end_msg_id = x
    await run_batch(sender ,des_channel_id, s_channel_id, start_msg_id, end_msg_id ,channel_id)
    queue.clear()
