import re,base64,aiohttp,random

from nonebot import on_message, logger
from nonebot.adapters.onebot.v11 import *
from nonebot.plugin import PluginMetadata

__plugin_meta__ = PluginMetadata(
    name="复读",
    description="复读",
    usage="""复读"""
)

m = on_message(priority=10, block=False)

last_message_list = {}
message_times = {}

async def message_preprocess(message,url):
    images = re.findall(r'\[CQ:image.*?]', message)
    if images != []:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    message = base64.b64encode(image_data)
                else:
                    message = None
        picture_type = True
    else:
        picture_type = False
    raw_message = message
    return message,raw_message,picture_type


@m.handle()
async def repeater(bot: Bot, event: GroupMessageEvent):
    gid = str(event.group_id)
    global last_message_list, message_times
    url = str(event.message)[(str(event.message).find("url=")+4):(str(event.message).find("file_size=")-1)]
    message,raw_message,picture_type = await message_preprocess(str(event.message),url)
    try:
        last_message = last_message_list[gid][0]
    except:
        last_message = None
        
    if last_message != message:
        message_times[gid] = 1
    else:
        try:
            message_times[gid] += 1
        except:
            message_times[gid] = 1
        
    logger.debug(f'[复读姬] 群聊{gid}已重复次数: {message_times.get(gid)}/{3}')
    
    if message_times.get(gid) == 3:
        
        try:
            if last_message_list[gid][0] != None:
                if not last_message_list[gid][1]:
                    msg = raw_message
                elif last_message_list[gid][1]:
                    msg = MessageSegment.image(base64.b64decode(raw_message))
                
                _stop = random.choice([True,False])
                
                if _stop:
                    pass
                else:
                    msg = "打断施法！"
                
                await bot.send_group_msg(group_id=event.group_id, message=msg, auto_escape=False)
                # await m.send(msg)
                
        except Exception as e:
            logger.opt(colors=True).error(f"<red>{e}</red>")
        finally:
            message_times[gid] = 0
            
    last_message_list[gid] = [message,picture_type]
