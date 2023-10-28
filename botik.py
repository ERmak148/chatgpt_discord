import json
import time
import datetime
import openai
import discord
from discord.ext import commands
from discord.ext import tasks

openai.api_key = "openai token here"

config = {
    'token': 'Discord bot token here',
    'prefix': '!',
}

userschat = {}
usersimage = {}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=True, intents=intents)

with open("log.json", "w+") as file:
    json.dump({"GPT": [], "IMAGE": []}, file, indent=1)
@bot.event
async def on_ready():
    chatcooldown.start()
    imagecooldown.start()
    # wolframcooldown.start()
    print("ready")

@bot.event
async def on_guild_join(guild: discord.Guild):
    print(guild.name, guild.id)


@bot.command()
async def chat(ctx: commands.Context, *, request: str):
    if (ctx.author.id not in userschat):
        embed = discord.Embed(title="Loading. Please wait.")
        userschat[ctx.author.id] = time.time()
        msg = await ctx.reply(embed=embed)
        rel = f"Username: {ctx.author.display_name}; Request: \"{request}\""
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": rel},
            ],
            temperature=0.7,
            max_tokens=512,
        )

        res = response.choices[0].message.content
        with open("log.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        data["GPT"].append({
            "user": ctx.author.name,
            "datetime": str(datetime.datetime.now()),
            "request": request,
            "formattedrequest": rel,
            "gpt": res
        })
        with open("log.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=1, ensure_ascii=False)
        embed1 = discord.Embed(title="ChatGPT answer", description=res)
        await msg.edit(content="", embed=embed1)
    else:
        await ctx.reply("Cooldown has not yet passed!")


@bot.command()
async def image(ctx: commands.Context, *, request: str):
    if (ctx.author.id not in usersimage):
        usersimage[ctx.author.id] = time.time()
        image = await openai.Image.acreate(
            prompt=request,
            n=1,
            size="256x256"
        )
        image_url = image['data'][0]['url']
        embd = discord.Embed(title=f"Image for the request: {request}")
        embd.set_image(url=image_url)
        with open("log.json", "r", encoding="utf-8") as file:
            data = json.load(file)
        data["IMAGE"].append({
            "user": ctx.author.name,
            "datetime": str(datetime.datetime.now()),
            "request": request,
            "DALLE": image_url
        })
        with open("log.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=1, ensure_ascii=False)
        return await ctx.reply(embed=embd)
    else:
        await ctx.reply("Cooldown has not yet passed!")


@tasks.loop(seconds=8)
async def chatcooldown():

    for k, v in userschat.copy().items():
        # print(((time.time() - v) ))
        if ((time.time() - v)) >= 100:
            del userschat[k]

@tasks.loop(seconds=8)
async def imagecooldown():

    for k, v in usersimage.copy().items():
        # print(((time.time() - v) ))
        if ((time.time() - v)) >= 450:
            del usersimage[k]




@bot.event
async def on_command_error(ctx, error):
    await ctx.reply(error)

bot.run(config["token"])
