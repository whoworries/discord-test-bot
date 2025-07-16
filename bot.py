import requests
import random

import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command()
async def hello(ctx):
    await ctx.send("Leave me alone")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

@bot.command()
async def ben(ctx):
    """Shows our very own baby boy."""
    messages = [
        "https://media.discordapp.net/attachments/683335468632637481/1394515508652671016/bensfamily.png?ex=687868c6&is=68771746&hm=1d7d67d4cbfcd2a50e14bbe9c3035e3a2081235bc0778ec1b3bd726ceb54cd17&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/683335468632637481/1394463230201692240/image.jpg?ex=68783815&is=6876e695&hm=a05a4318239515369ae69bb14889b031764ebe242e4d26810adfd8197015f2cd&=&format=webp&width=720&height=960",
        "https://media.discordapp.net/attachments/683335468632637481/1394462952249229373/good_job_ben.jpg?ex=687837d3&is=6876e653&hm=06c5863d29aac1a982a8799c4b18ffb778f00672b6b2ded36c88a8b12a87daca&=&format=webp&width=444&height=960",
        "https://media.discordapp.net/attachments/683335468632637481/1394462603799036024/ben-glasses.jpg?ex=68783780&is=6876e600&hm=be8778945c6258160cda70f979786a42e7498e2fba479ccdd36aa8df4218e075&=&format=webp",
        "https://media.discordapp.net/attachments/683335468632637481/1394455834427396238/unknown.png?ex=68783132&is=6876dfb2&hm=84043c15beaf0a13463aa26a10fe44ff8b9ded2687f7ef64afcc23bf74abe91f&=&format=webp&quality=lossless&width=720&height=960",
        "https://media.discordapp.net/attachments/591762087513030686/1394881879668428991/1231e-as33512das-2131412.png?ex=68786c7b&is=68771afb&hm=70a92d649a977f28b2a3591e8790d9f9f9b6ab58b01d3990d2380b7ddc9420cb&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/591762087513030686/1394881891752214589/ben1.png?ex=68786c7e&is=68771afe&hm=8dc4ff77eb41667610489b7bb6be3fd192c00c1188fec42d50a80250b9552fc3&=&format=webp&quality=lossless&width=251&height=350",
        "https://media.discordapp.net/attachments/591762087513030686/1394881897888219166/ben2.PNG?ex=68786c80&is=68771b00&hm=6517b1095d2e78950dcdf060491846b1deecd5a78c8e4b5fd57157fa5f26754d&=&format=webp&quality=lossless",
        "https://media.discordapp.net/attachments/591762087513030686/1394881905219862631/ben4.PNG?ex=68786c81&is=68771b01&hm=c02fc36e70c73620a14d6ac4f83bfa9e81e882a9368f0dcc6e0e8e33e5f9128a&=&format=webp&quality=lossless"
    ]
    choice = random.choice(messages)
    await ctx.send(choice)

@bot.command()
async def bugfact(ctx):
    """Teaches you a lesson about life."""
    facts = [
        "Bees can recognize human faces — they remember and recognize patterns just like we do.",
        "Dragonflies can fly in six directions — up, down, forward, backward, and side to side.",
        "Cockroaches can live for a week without their heads — they only die because they can’t drink water.",
        "A single ant can carry 10–50 times its body weight — it’s like you lifting a car.",
        "There are more insects on Earth than stars in the Milky Way — by a lot.",
        "Ladybugs bleed from their knees when threatened — it’s a defense mechanism!",
        "A praying mantis can turn its head 180 degrees — it's one of the few insects that can do this.",
        "Butterflies taste with their feet — receptors on their feet help them detect nectar.",
        "Fireflies aren’t actually flies — they’re beetles!",
        "Mosquitoes are attracted to body heat and CO₂ — and they prefer people who just exercised (or ate bananas 👀)."
    ]
    choice = random.choice(facts)
    await ctx.send(choice)


@bot.command()
async def weather(ctx, *, city: str):
    """Get the current weather for a city."""
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather_desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        await ctx.send(
            f"🌤️ Weather in **{city.title()}**:\n"
            f"> **{weather_desc}**\n"
            f"> Temperature: {temp}°C (feels like {feels_like}°C)\n"
            f"> Humidity: {humidity}%"
        )
    else:
        await ctx.send("❌ Couldn't find that city. Please check the spelling and try again.")

bot_token = os.getenv("DISCORD_TOKEN")
bot.run(bot_token)