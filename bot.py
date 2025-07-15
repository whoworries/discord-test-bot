import requests

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
    await ctx.send("Hey there! 👋")

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms")



@bot.command()
async def weather(ctx, *, city: str):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

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