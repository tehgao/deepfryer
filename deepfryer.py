import logging as log

from PIL import Image
from functools import reduce
from pathlib import Path
from io import BytesIO
import deeppyer, asyncio, discord, os, requests

class DeepFryer(discord.Client):

    async def on_ready(self):
        log.info('Started bot with username {0.name} and ID {0.id}'.format(self.user))

    async def on_message(self, message):
        url = ''

        if len(message.mentions) > 0 and message.mentions[0].id == self.user.id:
            most_recent_images = list(filter(lambda msg: len(msg.attachments) > 0 , await message.channel.history(limit=20).flatten()))
            if len(most_recent_images) > 0:
                url = most_recent_images[0].attachments[0].url
                if reduce(lambda a, b : a or b, [url.endswith(x) for x in ['jpg', 'png', 'jpeg']]):
                    log.info('We found an image: {0}'.format(url))
                    resp = requests.get(url)
                    img = Image.open(BytesIO(resp.content))
                    deepfried = await deeppyer.deepfry(img, flares=False)
                    with BytesIO() as deepfried_binary:
                        format = 'JPEG' if Path(url).suffix[1:] == 'jpg' else Path(url).suffix[1:]
                        deepfried.save(deepfried_binary, format)
                        deepfried_binary.seek(0)
                        await message.channel.send(file=discord.File(fp = deepfried_binary, filename = 'deepfried' + Path(url).suffix))

client = DeepFryer()
client.run(os.environ.get('BOT_KEY'))