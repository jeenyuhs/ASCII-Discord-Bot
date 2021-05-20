
from hata import Client
import config
import PIL.Image
import requests
import log

DN = Client(config.bot_token)

ASCII_CHARS = ["@", "#", "S", "%", "?", "*", "+", ";", ":", "/", "!", ",", "."]

def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    return image.resize((new_width, new_height)), new_width

def grayify(image):
    return image.convert("L")

def img_to_ascii(url):
    img = PIL.Image.open(requests.get(url, stream=True).raw)
    img = grayify(img)
    img, new_width = resize_image(img)

    pixels = img.getdata()
    chars = "".join([ASCII_CHARS[pixel//20] for pixel in pixels])

    chars_len = len(chars)
    return "\n".join(chars[i:(i+new_width)] for i in range(0, chars_len, new_width))


@DN.events
async def ready(ctx):
    log.info("Logged in.")

@DN.events
async def message_create(ctx, message):
    if message.author.is_bot:
        return

    if message.content.lower().startswith("+convert"):
        if message.attachments:
            ascii = img_to_ascii(message.attachments[0].proxy_url)
        else:
            for content in message.contents:
                space_split = content.split(" ")
                for word in space_split:
                    if word.startswith("<:") and word.endswith(">"):
                        id = word.split("<:")[1].split(":")[1][:-1]
                        ascii = img_to_ascii("https://cdn.discordapp.com/emojis/{}.png?v=1".format(id))

        if len(ascii) <= 2000:
            await ctx.message_create(message.channel, "`{}`".format(ascii))
            return

        await ctx.message_create(message.channel, "Sending ascii... ({} characters).".format(len(ascii)))

        while True:
            if len(ascii) >= 1010:
                await ctx.message_create(message.channel, "`{}`".format(ascii[:1010]))

                ascii = ascii[1010:]
            else:
                await ctx.message_create(message.channel, "`{}`".format(ascii))
                break

            continue

        return

    return


DN.start()
