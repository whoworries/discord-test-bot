import random

import os
import sys
import asyncio
import aiohttp
import tempfile
import textwrap
import json
import datetime
from pathlib import Path
from typing import Literal, Optional
from dotenv import load_dotenv
load_dotenv()

import discord
from discord import app_commands
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


async def setup_hook():
    # Registers the / versions of the commands with Discord
    bot.add_view(QuoteView())   # makes old "Another quote" buttons work after a restart
    bot.add_view(TweetView())
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands")

bot.setup_hook = setup_hook

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    if not seasonal_icon_check.is_running():
        seasonal_icon_check.start()
    if not twitch_check.is_running():
        twitch_check.start()
    await apply_saved_status()

@bot.hybrid_command()
async def hello(ctx):
    """Says hi. Sort of."""
    await ctx.send("Leave me alone")

@bot.hybrid_command()
async def ping(ctx):
    """Shows the bot's response time."""
    await ctx.send(f"Pong! 🏓 {round(bot.latency * 1000)}ms", ephemeral=True)

@bot.hybrid_command()
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

@bot.hybrid_command()
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


@bot.hybrid_command()
async def weather(ctx, *, city: str):
    """Get the current weather for a city."""
    await ctx.defer()
    params = {"q": city, "appid": os.getenv("WEATHER_API_KEY"), "units": "imperial"}
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.openweathermap.org/data/2.5/weather", params=params) as response:
            ok = response.status == 200
            data = await response.json() if ok else None

    if ok:
        weather_desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]

        await ctx.send(
            f"🌤️ Weather in **{city.title()}**:\n"
            f"> **{weather_desc}**\n"
            f"> Temperature: {temp}°F (feels like {feels_like}°F)\n"
            f"> Humidity: {humidity}%"
        )
    else:
        await ctx.send("❌ Couldn't find that city. Please check the spelling and try again.")

# ---------------- Holiday server icons ----------------
# Put one image per season in the "icons" folder, named like icons/halloween.png
# (.png, .jpg, .jpeg, .gif or .webp all work). The bot checks every hour and
# swaps the server icon when a new season starts.

ICON_DIR = Path(__file__).parent / "icons"
STATE_FILE = Path(__file__).parent / "icon_state.json"

SEASON_NAMES = {
    "newyear": "New Year's",
    "anniversary": "Server Anniversary",
    "valentines": "Valentine's Day",
    "stpatricks": "St. Patrick's Day",
    "fourth": "4th of July",
    "halloween": "Halloween",
    "thanksgiving": "Thanksgiving",
    "christmas": "Christmas",
    "aprilfools": "April Fools' Day",
    "easter": "Easter",
    "summer": "Summer",
    "default": "Normal",
}


def thanksgiving_date(year):
    """4th Thursday of November."""
    nov1 = datetime.date(year, 11, 1)
    return nov1 + datetime.timedelta(days=(3 - nov1.weekday()) % 7 + 21)


def easter_date(year):
    """Easter Sunday (Western), using the standard Gregorian calculation."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month, day = divmod(h + l - 7 * m + 114, 31)
    return datetime.date(year, month, day + 1)


def current_season(today=None):
    """Works out which holiday season a date falls in."""
    today = today or datetime.date.today()
    md = (today.month, today.day)

    if md >= (12, 26) or md == (1, 1):
        return "newyear"          # Dec 26 - Jan 1
    if md < (1, 18):
        return "default"          # Jan 2 - Jan 17
    if md <= (1, 25):
        return "anniversary"      # Jan 18 - Jan 25 (week before the server anniversary)
    if md < (2, 1):
        return "default"          # Jan 26 - Jan 31
    if md < (3, 1):
        return "valentines"       # all of February
    if md <= (3, 17):
        return "stpatricks"       # Mar 1 - Mar 17
    if md == (4, 1):
        return "aprilfools"       # Apr 1 only (beats Easter if they overlap)
    easter = easter_date(today.year)
    if easter - datetime.timedelta(days=6) <= today <= easter:
        return "easter"           # the week leading up to Easter Sunday
    if md < (6, 20):
        return "default"          # rest of Mar 18 - Jun 19
    if md <= (7, 4):
        return "fourth"           # Jun 20 - Jul 4
    if md <= (7, 31):
        return "summer"           # Jul 5 - Jul 31
    if md < (10, 1):
        return "default"          # Aug 1 - Sep 30
    if md <= (10, 31):
        return "halloween"        # all of October
    if today <= thanksgiving_date(today.year):
        return "thanksgiving"     # Nov 1 - Thanksgiving Day
    return "christmas"            # day after Thanksgiving - Dec 25


def find_icon(season):
    for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
        path = ICON_DIR / f"{season}{ext}"
        if path.exists():
            return path
    return None


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


async def apply_season_icon(guild, season, force=False):
    """Sets the guild icon for a season. Returns True if it changed."""
    state = load_state()
    if not force and state.get(str(guild.id)) == season:
        return False

    # First run: back up the server's current icon as the "normal" one
    ICON_DIR.mkdir(exist_ok=True)
    if find_icon("default") is None and guild.icon:
        (ICON_DIR / "default.png").write_bytes(await guild.icon.with_format("png").read())
        print(f"[icons] Saved {guild.name}'s current icon as icons/default.png")

    path = find_icon(season)
    if path is None:
        print(f"[icons] No icon file for '{season}' in the icons folder, skipping")
        return False

    try:
        await guild.edit(icon=path.read_bytes(), reason=f"Seasonal icon: {SEASON_NAMES[season]}")
    except discord.Forbidden:
        print(f"[icons] I need the Manage Server permission in {guild.name}")
        return False
    except discord.HTTPException as e:
        print(f"[icons] Discord rejected {path.name}: {e}")
        return False

    state[str(guild.id)] = season
    save_state(state)
    print(f"[icons] {guild.name} icon set to {SEASON_NAMES[season]}")
    return True


@tasks.loop(hours=1)
async def seasonal_icon_check():
    season = current_season()
    for guild in bot.guilds:
        await apply_season_icon(guild, season)


@seasonal_icon_check.before_loop
async def before_icon_check():
    await bot.wait_until_ready()


@bot.hybrid_command()
@commands.guild_only()
async def season(ctx):
    """Shows which holiday icon season we're in."""
    await ctx.send(f"🎉 Current season: **{SEASON_NAMES[current_season()]}**")


@bot.hybrid_command()
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def seticon(ctx, image: discord.Attachment):
    """Changes the server icon to an attached image (until the next season starts)."""
    await ctx.defer(ephemeral=True)
    image = await image.read()
    try:
        await ctx.guild.edit(icon=image, reason=f"Changed by {ctx.author}")
    except discord.HTTPException:
        await ctx.send("❌ Couldn't set that as the icon. Make sure it's a PNG, JPG or GIF.", ephemeral=True)
        return
    await ctx.send("Server icon updated.", ephemeral=True)


@bot.hybrid_command()
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def refreshicon(ctx):
    """Puts the current holiday icon back."""
    await ctx.defer(ephemeral=True)
    season = current_season()
    if await apply_season_icon(ctx.guild, season, force=True):
        await ctx.send(f"Icon reset to **{SEASON_NAMES[season]}**.", ephemeral=True)
    else:
        await ctx.send(f"❌ No icon file found for **{SEASON_NAMES[season]}** (or I'm missing permissions).", ephemeral=True)


def root_error(error):
    """Digs through the wrapper errors discord.py adds to find the real one."""
    while hasattr(error, "original"):
        error = error.original
    return error


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need the Manage Server permission to do that.", ephemeral=True)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"You're missing something. Usage: `!{ctx.command.name} {ctx.command.signature}`", ephemeral=True)
    elif isinstance(error, commands.NotOwner):
        await ctx.send("Only the bot owner can use that.", ephemeral=True)
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("That only works in a server.", ephemeral=True)
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"That didn't look right. Usage: `!{ctx.command.name} {ctx.command.signature}`", ephemeral=True)
    elif isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(root_error(error), discord.Forbidden):
        where = f"#{ctx.channel.name}" if ctx.guild else "here"
        print(f"[permissions] /{ctx.command.name} in {where}: {root_error(error).text}")
        try:
            await ctx.author.send(f"❌ I don't have permission to do `/{ctx.command.name}` in {where}. "
                                  f"Check my role's permissions for that channel (usually **Send Messages**).")
        except discord.HTTPException:
            pass
    else:
        raise error


# ---------------- Soundboard spam ----------------
# !spam <sound name> [times]  - joins your voice channel and spams that sound
# !sounds                     - lists the sounds you can use
# !stop                       - stops spamming and leaves the call

SPAM_DEFAULT = 5      # how many times if you don't give a number
SPAM_MAX = 100       # upper limit so it can't run forever
SPAM_DELAY = 2.0      # seconds between sounds

spam_tasks = {}            # guild id -> running spam task
_default_sounds_cache = []


async def all_sounds(guild):
    """The server's own soundboard sounds plus Discord's built-in ones."""
    global _default_sounds_cache
    if not _default_sounds_cache:
        try:
            _default_sounds_cache = await bot.fetch_soundboard_default_sounds()
        except discord.HTTPException:
            pass
    return list(guild.soundboard_sounds) + list(_default_sounds_cache)


async def find_sound(guild, name):
    sounds = await all_sounds(guild)
    name = name.lower().strip()
    for s in sounds:                      # exact name first
        if s.name.lower() == name:
            return s
    for s in sounds:                      # then partial match
        if name in s.name.lower():
            return s
    return None


async def join_voice(ctx):
    """Joins (or moves to) the command user's voice channel. Returns the voice client or None."""
    target = ctx.author.voice.channel
    vc = ctx.guild.voice_client
    try:
        if vc is None:
            vc = await target.connect(self_deaf=False)
        elif vc.channel != target:
            await vc.move_to(target)
    except RuntimeError:
        await ctx.send("❌ Voice support isn't installed. Run: `venv\\Scripts\\python -m pip install \"discord.py[voice]\"`")
        return None
    except (discord.ClientException, asyncio.TimeoutError):
        await ctx.send("❌ I couldn't join that voice channel.")
        return None
    return vc


async def run_spam(ctx, voice_client, sound, times):
    channel = voice_client.channel
    try:
        for _ in range(times):
            await channel.send_sound(sound)
            await asyncio.sleep(SPAM_DELAY)
    except discord.Forbidden:
        await ctx.send("❌ I need the **Speak** and **Use Soundboard** permissions in that channel.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Discord stopped the sound: {e.text or e}")
    finally:
        spam_tasks.pop(ctx.guild.id, None)
        if voice_client.is_connected():
            await voice_client.disconnect()


@bot.hybrid_command()
@commands.guild_only()
@app_commands.describe(sound="Sound name, optionally followed by how many times, e.g. vine boom 10")
async def spam(ctx, *, sound: str):
    """Joins your call and spams a soundboard sound. Usage: !spam <sound> [times]"""
    args = sound
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Join a voice channel first.", ephemeral=True)
        return
    if ctx.guild.id in spam_tasks:
        await ctx.send("I'm already spamming. Use `!stop` first.", ephemeral=True)
        return

    # A number at the end is how many times, e.g. "!spam vine boom 10"
    parts = args.rsplit(" ", 1)
    times = SPAM_DEFAULT
    if len(parts) == 2 and parts[1].isdigit():
        args, times = parts[0], int(parts[1])
    times = max(1, min(times, SPAM_MAX))

    sound = await find_sound(ctx.guild, args)
    if sound is None:
        await ctx.send(f"❌ No sound called **{args}**. Use `/sounds` to see the list.", ephemeral=True)
        return
    await ctx.defer()

    target = ctx.author.voice.channel
    vc = await join_voice(ctx)
    if vc is None:
        return

    await ctx.send(f"🔊 Spamming **{sound.name}** {times} times in {target.mention}")
    spam_tasks[ctx.guild.id] = asyncio.create_task(run_spam(ctx, vc, sound, times))


@spam.autocomplete("sound")
async def spam_sound_autocomplete(interaction, current: str):
    names = sorted({s.name for s in await all_sounds(interaction.guild)})
    matches = [n for n in names if current.lower() in n.lower()]
    return [app_commands.Choice(name=n, value=n) for n in matches[:25]]


@bot.hybrid_command()
@commands.guild_only()
async def stop(ctx):
    """Stops the soundboard spam and leaves the call."""
    task = spam_tasks.pop(ctx.guild.id, None)
    if task:
        task.cancel()
    cancel_tts_leave(ctx.guild.id)
    was_connected = ctx.guild.voice_client is not None
    if was_connected:
        await ctx.guild.voice_client.disconnect()
    if task or was_connected:
        await ctx.send("🛑 Stopped." if task else "👋 Left the call.")
    else:
        await ctx.send("Nothing was playing.", ephemeral=True)


@bot.hybrid_command()
@commands.guild_only()
async def sounds(ctx):
    """Lists the soundboard sounds you can spam."""
    server = [s.name for s in ctx.guild.soundboard_sounds]
    await all_sounds(ctx.guild)
    builtin = [s.name for s in _default_sounds_cache]
    msg = "**Server sounds:** " + (", ".join(server) or "none")
    msg += "\n**Built-in sounds:** " + (", ".join(builtin) or "none")
    await ctx.send(msg[:2000], ephemeral=True)


# ---------------- Text to speech ----------------
# !tts <message>  - joins your voice channel and reads the message out loud
# Needs:  pip install edge-tts   and FFmpeg installed on the computer

TTS_MAX_CHARS = 300
TTS_STAY_SECONDS = 60   # how long the bot hangs around in the call after the last TTS message
tts_leave_tasks = {}    # guild id -> pending "leave the call" timer


def cancel_tts_leave(guild_id):
    task = tts_leave_tasks.pop(guild_id, None)
    if task:
        task.cancel()


async def leave_after_idle(guild_id, vc):
    """Leaves the call once nobody has used TTS for TTS_STAY_SECONDS (unless /spam is running)."""
    try:
        await asyncio.sleep(TTS_STAY_SECONDS)
        if guild_id not in spam_tasks and vc.is_connected() and not vc.is_playing():
            await vc.disconnect()
    except asyncio.CancelledError:
        pass
    finally:
        if tts_leave_tasks.get(guild_id) is asyncio.current_task():
            tts_leave_tasks.pop(guild_id, None)

# Name people pick -> Microsoft voice ID ("edge-tts --list-voices" shows hundreds more)
TTS_VOICES = {
    "guy": "en-US-GuyNeural",
    "aria": "en-US-AriaNeural",
    "jenny": "en-US-JennyNeural",
    "christopher": "en-US-ChristopherNeural",
    "kid": "en-US-AnaNeural",
    "british_man": "en-GB-RyanNeural",
    "british_woman": "en-GB-SoniaNeural",
    "aussie_man": "en-AU-WilliamNeural",
    "aussie_woman": "en-AU-NatashaNeural",
    "irish": "en-IE-ConnorNeural",
    "indian": "en-IN-PrabhatNeural",
}
TTS_DEFAULT_VOICE = "guy"
VoiceName = Literal[tuple(TTS_VOICES)]
USER_VOICES_FILE = Path(__file__).parent / "tts_voices.json"


def load_user_voices():
    try:
        return json.loads(USER_VOICES_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def voice_for(user_id, chosen=None):
    """Voice for this message: the one picked now, else the user's saved one, else the default."""
    if chosen:
        return chosen
    saved = load_user_voices().get(str(user_id))
    return saved if saved in TTS_VOICES else TTS_DEFAULT_VOICE


@bot.hybrid_command(usage="[voice] <message>")
@commands.guild_only()
@app_commands.describe(text="What the bot should say", voice="Which voice to use (default: your /myvoice choice)")
async def tts(ctx, voice: Optional[VoiceName] = None, *, text: commands.clean_content):
    """Says your message out loud in your voice channel. Usage: !tts [voice] <message>"""
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Join a voice channel first.", ephemeral=True)
        return
    if len(text) > TTS_MAX_CHARS:
        await ctx.send(f"That's too long. Keep it under {TTS_MAX_CHARS} characters.", ephemeral=True)
        return
    try:
        import edge_tts
    except ImportError:
        await ctx.send("❌ TTS isn't installed. Run: `venv\\Scripts\\python -m pip install edge-tts`", ephemeral=True)
        return

    await ctx.defer()
    cancel_tts_leave(ctx.guild.id)   # don't leave while we're about to talk
    vc = await join_voice(ctx)
    if vc is None:
        return
    if vc.is_playing():
        await ctx.send("I'm already talking, wait a sec.")
        tts_leave_tasks[ctx.guild.id] = asyncio.create_task(leave_after_idle(ctx.guild.id, vc))
        return

    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        await edge_tts.Communicate(str(text), TTS_VOICES[voice_for(ctx.author.id, voice)]).save(path)
        done = asyncio.Event()
        try:
            # apad adds a little silence at the end so the last word isn't clipped
            vc.play(discord.FFmpegPCMAudio(path, options="-af apad=pad_dur=0.75"),
                    after=lambda e: bot.loop.call_soon_threadsafe(done.set))
        except discord.ClientException:
            await ctx.send("❌ FFmpeg isn't installed (or isn't on PATH), so I can't play audio.")
            return
        if ctx.interaction:
            await ctx.send(f"🗣️ {text}")
        else:
            await ctx.message.add_reaction("🗣️")
        await done.wait()
        await asyncio.sleep(1)   # let the last bit of audio reach Discord
    except Exception as e:
        await ctx.send(f"❌ TTS failed: {e}")
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
        # stay in the call for a bit so back-to-back TTS doesn't leave/rejoin
        if vc.is_connected():
            cancel_tts_leave(ctx.guild.id)
            tts_leave_tasks[ctx.guild.id] = asyncio.create_task(leave_after_idle(ctx.guild.id, vc))


@bot.hybrid_command(usage="[voice]")
@app_commands.describe(voice="Your new default voice (leave empty to see your current one)")
async def myvoice(ctx, voice: Optional[VoiceName] = None):
    """Sets the voice /tts uses for you by default."""
    if voice is None:
        await ctx.send(f"🗣️ Your TTS voice is **{voice_for(ctx.author.id)}**. "
                       f"Change it with `/myvoice` (see `/voices` for options).", ephemeral=True)
        return
    saved = load_user_voices()
    saved[str(ctx.author.id)] = voice
    USER_VOICES_FILE.write_text(json.dumps(saved, indent=2))
    await ctx.send(f"✅ Your TTS voice is now **{voice}**.", ephemeral=True)


@bot.hybrid_command()
async def voices(ctx):
    """Lists the voices you can use with /tts."""
    names = ", ".join(f"`{n}`" for n in TTS_VOICES)
    await ctx.send(f"🗣️ **TTS voices:** {names}\nExample: `!tts british_man hello there`. Set your own default with `/myvoice`.", ephemeral=True)


# ---------------- Twitch live alerts ----------------
# Posts the stream link when the streamer goes live.
# Needs TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET in .env (free app at dev.twitch.tv)
# Run !streamhere in the channel where alerts should go.

TWITCH_STREAMER = "mtsuesports"
TWITCH_GAMES = {"valorant"}   # only announce when streaming one of these (lowercase). Empty set = any game
STREAM_STATE_FILE = Path(__file__).parent / "stream_state.json"

_twitch_token = None


def load_stream_state():
    try:
        return json.loads(STREAM_STATE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_stream_state(state):
    STREAM_STATE_FILE.write_text(json.dumps(state, indent=2))


async def get_twitch_token(session):
    """Gets an app access token from Twitch using the client ID and secret."""
    global _twitch_token
    async with session.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": os.getenv("TWITCH_CLIENT_ID"),
        "client_secret": os.getenv("TWITCH_CLIENT_SECRET"),
        "grant_type": "client_credentials",
    }) as resp:
        resp.raise_for_status()
        _twitch_token = (await resp.json())["access_token"]


async def get_live_stream(streamer):
    """Returns Twitch's info about the stream if they're live, otherwise None."""
    async with aiohttp.ClientSession() as session:
        if _twitch_token is None:
            await get_twitch_token(session)
        for attempt in range(2):
            headers = {
                "Client-ID": os.getenv("TWITCH_CLIENT_ID"),
                "Authorization": f"Bearer {_twitch_token}",
            }
            async with session.get("https://api.twitch.tv/helix/streams",
                                   params={"user_login": streamer}, headers=headers) as resp:
                if resp.status == 401 and attempt == 0:   # token expired, get a new one
                    await get_twitch_token(session)
                    continue
                resp.raise_for_status()
                data = (await resp.json())["data"]
                return data[0] if data else None


@tasks.loop(minutes=2)
async def twitch_check():
    if not os.getenv("TWITCH_CLIENT_ID") or not os.getenv("TWITCH_CLIENT_SECRET"):
        print("[twitch] TWITCH_CLIENT_ID / TWITCH_CLIENT_SECRET missing from .env, alerts are off")
        twitch_check.cancel()
        return

    state = load_stream_state()
    try:
        stream = await get_live_stream(TWITCH_STREAMER)
    except Exception as e:
        print(f"[twitch] Couldn't check Twitch: {e}")
        return

    if stream is None:
        return
    if state.get("last_stream_id") == stream["id"]:
        return   # already announced this stream
    if TWITCH_GAMES and (stream.get("game_name") or "").lower() not in TWITCH_GAMES:
        return   # live, but not in VALORANT. Not marked as announced, so switching to it later still alerts

    state["last_stream_id"] = stream["id"]
    save_stream_state(state)

    channel = bot.get_channel(state.get("channel_id", 0))
    if channel is None:
        print("[twitch] Streamer is live but no alert channel is set. Run !streamhere in Discord.")
        return

    # escape so "||" in titles (e.g. NECC streams) doesn't turn into a spoiler box
    title = discord.utils.escape_markdown(stream.get("title") or "")
    game = discord.utils.escape_markdown(stream.get("game_name") or "")
    role = channel.guild.get_role(state.get("role_id", 0)) if channel.guild else None
    msg = f"{role.mention} " if role else ""
    msg += f"🔴 **{stream['user_name']}** is live!"
    if title:
        msg += f" *{title}*"
    if game:
        msg += f" ({game})"
    msg += f"\nhttps://twitch.tv/{TWITCH_STREAMER}"
    await channel.send(msg, allowed_mentions=discord.AllowedMentions(roles=True))
    print(f"[twitch] Announced stream {stream['id']}")


@twitch_check.before_loop
async def before_twitch_check():
    await bot.wait_until_ready()


@bot.hybrid_command()
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
@app_commands.describe(role="Role to ping when the stream goes live (optional)")
async def streamhere(ctx, role: Optional[discord.Role] = None):
    """Makes Twitch live alerts post in this channel, optionally pinging a role."""
    if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
        await ctx.author.send(f"❌ I need **Send Messages** in #{ctx.channel.name} to post live alerts there.")
        return
    state = load_stream_state()
    state["channel_id"] = ctx.channel.id
    if role is not None:
        state["role_id"] = role.id
    save_stream_state(state)
    saved_role = ctx.guild.get_role(state.get("role_id", 0))
    msg = f"✅ Live alerts for **{TWITCH_STREAMER}** will post in {ctx.channel.mention}"
    msg += f" and ping {saved_role.mention}." if saved_role else "."
    if saved_role and not saved_role.mentionable and not ctx.channel.permissions_for(ctx.guild.me).mention_everyone:
        msg += ("\n⚠️ I can't actually ping that role yet. Turn on **Allow anyone to @mention this role** "
                "for it, or give me **Mention @everyone, @here, and All Roles**.")
    await ctx.send(msg, allowed_mentions=discord.AllowedMentions.none(), ephemeral=True)


# ---------------- Snipe ----------------
# Remembers the last deleted message in each channel (only in memory, gone on restart).

last_deleted = {}   # channel id -> info about the deleted message


@bot.event
async def on_message_delete(message):
    if message.guild is None or message.author.bot:
        return
    if not message.content and not message.attachments:
        return
    last_deleted[message.channel.id] = {
        "author": message.author.display_name,
        "avatar": message.author.display_avatar.url,
        "content": message.content,
        "attachments": len(message.attachments),
        "time": message.created_at,
    }


@bot.hybrid_command()
@commands.guild_only()
async def snipe(ctx):
    """Shows the last deleted message in this channel."""
    info = last_deleted.get(ctx.channel.id)
    if info is None:
        await ctx.send("Nothing to snipe here.")
        return
    embed = discord.Embed(description=info["content"] or "*no text*",
                          color=discord.Color.red(), timestamp=info["time"])
    embed.set_author(name=info["author"], icon_url=info["avatar"])
    if info["attachments"]:
        embed.set_footer(text=f"had {info['attachments']} attachment(s)")
    await ctx.send(embed=embed)


# ---------------- Black Friday countdown ----------------
def black_friday_date(year):
    return thanksgiving_date(year) + datetime.timedelta(days=1)


@bot.hybrid_command()
async def countdown(ctx):
    """Says how many days until Black Friday."""
    today = datetime.date.today()
    day = black_friday_date(today.year)
    if today > day:
        day = black_friday_date(today.year + 1)
    days = (day - today).days
    if days == 0:
        await ctx.send("🛒 **It's Black Friday.**")
    elif days == 1:
        await ctx.send("🛒 **1 day** until Black Friday.")
    else:
        await ctx.send(f"🛒 **{days} days** until Black Friday ({day.strftime('%B %d').replace(' 0', ' ')}).")


# ---------------- Quotes ----------------
# /quotechannel (run in your quotes channel) tells the bot where the quotes are.
# /quote posts a random message from that channel.

QUOTES_FILE = Path(__file__).parent / "quotes.json"
quote_ids = {}   # guild id -> list of message ids in the quotes channel (filled on first use)


def load_quote_settings():
    try:
        return json.loads(QUOTES_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def quote_channel_for(guild):
    channel_id = load_quote_settings().get(str(guild.id))
    return guild.get_channel(channel_id) if channel_id else None


ATTRIBUTION_MAX_GAP = datetime.timedelta(minutes=10)


def is_attribution(message):
    """A short follow-up like '-Name' that says who said the quote above it."""
    text = (message.content or "").strip()
    return (not message.attachments and text[:1] in ("-", "—", "–", "~")
            and len(text) <= 40 and len(text.split()) <= 5)


def is_quotable(message):
    return (not message.author.bot and (message.content or message.attachments)
            and not is_attribution(message))


async def load_quote_ids(channel):
    ids = [m.id async for m in channel.history(limit=None) if is_quotable(m)]
    quote_ids[channel.guild.id] = ids
    return ids


@bot.listen("on_message")
async def remember_new_quote(message):
    """Adds new messages in the quotes channel to the list without re-reading the whole channel."""
    if message.guild is None or message.guild.id not in quote_ids or not is_quotable(message):
        return
    channel = quote_channel_for(message.guild)
    if channel and message.channel.id == channel.id:
        quote_ids[message.guild.id].append(message.id)


async def make_quote(guild):
    """Picks a random quote. Returns (embed, None) or (None, error message)."""
    channel = quote_channel_for(guild)
    if channel is None:
        return None, "No quotes channel set yet. Someone with Manage Server can run `/quotechannel` in it."
    try:
        ids = quote_ids.get(guild.id) or await load_quote_ids(channel)
    except discord.Forbidden:
        return None, f"❌ I can't read {channel.mention}. I need **Read Message History** there."

    message = None
    while ids and message is None:
        pick = random.choice(ids)
        try:
            message = await channel.fetch_message(pick)   # fresh copy so images still load
        except discord.NotFound:
            ids.remove(pick)                              # quote was deleted
    if message is None:
        return None, f"{channel.mention} doesn't have any quotes yet."

    # Pair the quote with a "-Name" message posted right before/after it
    attribution = None
    if is_attribution(message):
        attribution = message
        async for before in channel.history(before=message, limit=1):
            if message.created_at - before.created_at <= ATTRIBUTION_MAX_GAP:
                message = before
    else:
        async for after in channel.history(after=message, limit=1, oldest_first=True):
            if is_attribution(after) and after.created_at - message.created_at <= ATTRIBUTION_MAX_GAP:
                attribution = after

    text = message.content or ""
    if attribution is not None and attribution.id != message.id:
        name = attribution.content.strip().lstrip("-—–~ ").strip()
        if name:
            text = f"{text}\n\n— **{name}**" if text else f"— **{name}**"

    embed = discord.Embed(description=text or None, color=discord.Color.gold(),
                          timestamp=message.created_at)
    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    image = next((a for a in message.attachments
                  if a.content_type and a.content_type.startswith("image/")), None)
    if image:
        embed.set_image(url=image.url)
    embed.add_field(name="\u200b", value=f"[Jump to message]({message.jump_url})")
    return embed, None


class QuoteView(discord.ui.View):
    """The 'Another quote' button. Persistent, so it keeps working after the bot restarts."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Another quote", style=discord.ButtonStyle.secondary,
                       custom_id="roach:another_quote")
    async def another(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.guild is None:
            return
        await interaction.response.defer()
        embed, error = await make_quote(interaction.guild)
        if error:
            await interaction.followup.send(error, ephemeral=True)
            return
        try:
            await interaction.message.edit(view=None)   # old quote loses its button
        except discord.HTTPException:
            pass
        await interaction.followup.send(embed=embed, view=QuoteView())


@bot.hybrid_command()
@commands.guild_only()
async def quote(ctx):
    """Posts a random quote from the quotes channel."""
    if quote_channel_for(ctx.guild) is None:
        await ctx.send("No quotes channel set yet. Someone with Manage Server can run `/quotechannel` in it.",
                       ephemeral=True)
        return
    await ctx.defer()
    embed, error = await make_quote(ctx.guild)
    if error:
        await ctx.send(error)
        return
    await ctx.send(embed=embed, view=QuoteView())


@bot.hybrid_command()
@commands.guild_only()
@commands.has_permissions(manage_guild=True)
@app_commands.default_permissions(manage_guild=True)
async def quotechannel(ctx):
    """Makes this channel the one /quote picks from."""
    if not ctx.channel.permissions_for(ctx.guild.me).read_message_history:
        await ctx.author.send(f"❌ I need **Read Message History** in #{ctx.channel.name} to pick quotes from it.")
        return
    settings = load_quote_settings()
    settings[str(ctx.guild.id)] = ctx.channel.id
    QUOTES_FILE.write_text(json.dumps(settings, indent=2))
    quote_ids.pop(ctx.guild.id, None)   # re-read the new channel next time
    await ctx.send(f"✅ `/quote` will now pick from {ctx.channel.mention}.", ephemeral=True)


# ---------------- Video to GIF ----------------
# /gif <video> [start] [length] [width]   or reply to a video with !gif
GIF_MAX_LENGTH = 10            # seconds
GIF_MAX_DOWNLOAD = 50_000_000  # don't download videos bigger than 50 MB
GIF_TIMEOUT = 180              # give up if FFmpeg takes longer than this (seconds)
gif_lock = asyncio.Semaphore(1)   # one conversion at a time so the Pi doesn't melt


def is_video(attachment):
    if attachment.content_type and attachment.content_type.startswith("video/"):
        return True
    return attachment.filename.lower().endswith((".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"))


# Meme-style fonts to try, in order (Impact on Windows, DejaVu Bold on the Pi)
CAPTION_FONTS = [
    "C:/Windows/Fonts/impact.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
CAPTION_MAX_CHARS = 100


def ffmpeg_path(path):
    """Writes a file path the way FFmpeg filters want it (forward slashes, escaped colon)."""
    return str(path).replace("\\", "/").replace(":", "\\:")


def caption_filters(caption, width, tmpdir):
    """Builds drawtext filters: centered white text with a black outline, wrapped over lines."""
    if not caption:
        return ""
    font = next((f for f in CAPTION_FONTS if os.path.exists(f)), None)
    size = max(14, width // 11)
    chars_per_line = max(8, int(width / (size * 0.55)))
    parts = []
    for i, line in enumerate(textwrap.wrap(caption, chars_per_line)[:4]):
        # Text goes in a file so quotes/colons in the caption can't break the command
        text_file = os.path.join(tmpdir, f"caption{i}.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(line)
        opts = [f"textfile='{ffmpeg_path(text_file)}'", f"fontsize={size}", "fontcolor=white",
                f"borderw={max(2, size // 12)}", "bordercolor=black",
                "x=(w-text_w)/2", f"y={int(size * 0.3 + i * size * 1.15)}"]
        if font:
            opts.insert(0, f"fontfile='{ffmpeg_path(font)}'")
        parts.append("drawtext=" + ":".join(opts))
    return "," + ",".join(parts)


async def ffmpeg_to_gif(src, dst, start, length, width, fps, caption=None):
    text = caption_filters(caption, width, os.path.dirname(dst))
    filters = (f"fps={fps},scale={width}:-2:flags=lanczos{text},split[a][b];"
               f"[a]palettegen=max_colors=256:stats_mode=diff[p];"
               f"[b][p]paletteuse=dither=bayer:bayer_scale=5")
    proc = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(length), "-i", src,
        "-vf", filters, "-loop", "0", dst,
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)
    try:
        _, err = await asyncio.wait_for(proc.communicate(), timeout=GIF_TIMEOUT)
    except asyncio.TimeoutError:
        proc.kill()
        raise RuntimeError("took too long")
    if proc.returncode != 0:
        raise RuntimeError(err.decode(errors="replace").strip()[-300:] or "FFmpeg failed")


@bot.hybrid_command()
@app_commands.describe(video="The video to turn into a GIF",
                       start="Where to start, in seconds (default 0)",
                       length=f"How many seconds long (default 5, max {GIF_MAX_LENGTH})",
                       width="Width in pixels (default 480)",
                       caption="Text to put on top of the GIF (optional)")
async def gif(ctx, video: Optional[discord.Attachment] = None, start: float = 0.0,
              length: float = 5.0, width: app_commands.Range[int, 120, 720] = 480,
              *, caption: Optional[str] = None):
    """Turns a video into a GIF. Attach a video, or reply to one with !gif."""
    # For !gif as a reply, use the video in the message being replied to
    if video is None and ctx.message and ctx.message.reference:
        ref = ctx.message.reference.resolved
        if not isinstance(ref, discord.Message):
            ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        video = next((a for a in ref.attachments if is_video(a)), None)
    if video is None or not is_video(video):
        await ctx.send("Attach a video, or reply to a message that has one.", ephemeral=True)
        return
    if video.size > GIF_MAX_DOWNLOAD:
        await ctx.send("That video is too big (max 50 MB).", ephemeral=True)
        return

    if caption and len(caption) > CAPTION_MAX_CHARS:
        await ctx.send(f"Caption's too long. Keep it under {CAPTION_MAX_CHARS} characters.", ephemeral=True)
        return
    start = max(0.0, start)
    length = max(0.5, min(length, GIF_MAX_LENGTH))
    limit = ctx.guild.filesize_limit if ctx.guild else 10 * 1024 * 1024

    await ctx.defer()
    if gif_lock.locked():
        await ctx.send("⏳ Another GIF is being made, yours is next...")

    async with gif_lock:
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "input" + (Path(video.filename).suffix or ".mp4"))
            dst = os.path.join(tmp, "output.gif")
            await video.save(src)

            # Try smaller sizes until the GIF fits under Discord's upload limit
            attempts = [(width, 15), (int(width * 0.75), 12), (int(width * 0.5), 10)]
            for w, fps in attempts:
                try:
                    await ffmpeg_to_gif(src, dst, start, length, w, fps, caption)
                except FileNotFoundError:
                    await ctx.send("❌ FFmpeg isn't installed (or isn't on PATH).")
                    return
                except RuntimeError as e:
                    await ctx.send(f"❌ Couldn't convert that video: {e}")
                    return
                if os.path.exists(dst) and 0 < os.path.getsize(dst) <= limit:
                    name = Path(video.filename).stem[:40] + ".gif"
                    await ctx.send(file=discord.File(dst, filename=name))
                    return

    await ctx.send("❌ Even shrunk down, that GIF is too big for Discord. Try a shorter `length`.")


# ---------------- Tweets ----------------
# /tweet posts a random tweet from @ractingting. The tweets come from tweets.json,
# made by running import_tweets.py on the account's archive (data/tweets.js).

TWEET_HANDLE = "ractingting"
TWEET_EMBED_DOMAIN = "fixupx.com"   # alternatives: fxtwitter.com, vxtwitter.com
TWEETS_FILE = Path(__file__).parent / "tweets.json"
_tweets_cache = {"mtime": None, "tweets": []}


def load_tweets():
    """Reads tweets.json, re-reading it only if the file changed (e.g. after a new import)."""
    try:
        mtime = TWEETS_FILE.stat().st_mtime
    except FileNotFoundError:
        return []
    if _tweets_cache["mtime"] != mtime:
        try:
            _tweets_cache["tweets"] = json.loads(TWEETS_FILE.read_text(encoding="utf-8"))
            _tweets_cache["mtime"] = mtime
        except json.JSONDecodeError:
            return _tweets_cache["tweets"]
    return _tweets_cache["tweets"]


def random_tweet_link():
    tweets = load_tweets()
    if not tweets:
        return None
    # fixupx.com gives Discord a proper preview (X's own links often show a blank "X on X" card)
    url = f"https://{TWEET_EMBED_DOMAIN}/{TWEET_HANDLE}/status/{random.choice(tweets)['id']}"
    # Small gray "view on X" link instead of the full URL; Discord still shows the preview under it
    return f"-# [view on X]({url})"


class TweetView(discord.ui.View):
    """The 'Another tweet' button. Persistent, so it keeps working after restarts."""

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Another tweet", style=discord.ButtonStyle.secondary,
                       custom_id="roach:another_tweet")
    async def another(self, interaction: discord.Interaction, button: discord.ui.Button):
        link = random_tweet_link()
        if link is None:
            await interaction.response.send_message("No tweets loaded.", ephemeral=True)
            return
        await interaction.response.send_message(link, view=TweetView())
        try:
            await interaction.message.edit(view=None)   # old tweet loses its button
        except discord.HTTPException:
            pass


@bot.hybrid_command()
async def tweet(ctx):
    """Posts a random tweet from @ractingting."""
    link = random_tweet_link()
    if link is None:
        await ctx.send("No tweets loaded yet. Run import_tweets.py on the archive's tweets.js.", ephemeral=True)
        return
    await ctx.send(link, view=TweetView())


# ---------------- Help ----------------
# Commands are listed automatically using their descriptions (the """docstring""").
# Add new command names to a category here; anything not listed shows under "Other".

HELP_CATEGORIES = {
    "🎉 Fun": ["hello", "ping", "ben", "bugfact", "weather", "snipe", "quote", "tweet", "gif", "countdown"],
    "🔊 Voice": ["spam", "sounds", "stop", "tts", "voices", "myvoice"],
    "🖼️ Server icon": ["season", "seticon", "refreshicon"],
    "⚙️ Setup": ["quotechannel", "streamhere"],
}
ADMIN_COMMANDS = {"seticon", "refreshicon", "streamhere", "quotechannel"}
OWNER_COMMANDS = {"restart", "update", "setstatus"}


@bot.hybrid_command(name="help")
async def help_command(ctx):
    """Shows all of the bot's commands."""
    embed = discord.Embed(title="🪳 Bot commands", color=discord.Color.orange(),
                          description="Every command works with `/` or `!`. 🔒 = needs Manage Server.")
    listed = set()
    commands_by_name = {c.name: c for c in bot.commands
                        if not c.hidden and c.name not in OWNER_COMMANDS}

    def line(cmd):
        lock = " 🔒" if cmd.name in ADMIN_COMMANDS else ""
        usage = f" {cmd.signature}" if cmd.signature else ""
        return f"`/{cmd.name}{usage}`{lock} - {cmd.short_doc or 'No description'}"

    for category, names in HELP_CATEGORIES.items():
        lines = [line(commands_by_name[n]) for n in names if n in commands_by_name]
        listed.update(names)
        if lines:
            embed.add_field(name=category, value="\n".join(lines), inline=False)

    other = [line(c) for name, c in sorted(commands_by_name.items())
             if name not in listed and name != "help"]
    if other:
        embed.add_field(name="Other", value="\n".join(other), inline=False)

    await ctx.send(embed=embed, ephemeral=True)


# ---------------- Bot status ----------------
STATUS_FILE = Path(__file__).parent / "bot_status.json"
ACTIVITY_TYPES = {
    "playing": discord.ActivityType.playing,
    "watching": discord.ActivityType.watching,
    "listening": discord.ActivityType.listening,
    "competing": discord.ActivityType.competing,
}


def make_activity(kind, text):
    if not text:
        return None
    if kind in ACTIVITY_TYPES:
        return discord.Activity(type=ACTIVITY_TYPES[kind], name=text)
    return discord.CustomActivity(name=text)   # plain status message


async def apply_saved_status():
    try:
        saved = json.loads(STATUS_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return
    await bot.change_presence(activity=make_activity(saved.get("kind"), saved.get("text")))


@bot.hybrid_command()
@commands.is_owner()
@app_commands.describe(kind="Playing / Watching / Listening to / Competing in (leave empty for a plain message)",
                       text="The status text (leave everything empty to clear it)")
async def setstatus(ctx, kind: Optional[Literal["playing", "watching", "listening", "competing"]] = None,
                    *, text: Optional[str] = None):
    """(Owner only) Sets the bot's status message."""
    if text and len(text) > 128:
        await ctx.send("That's too long. Statuses can be up to 128 characters.", ephemeral=True)
        return
    await bot.change_presence(activity=make_activity(kind, text))
    STATUS_FILE.write_text(json.dumps({"kind": kind, "text": text}))
    if not text:
        await ctx.send("✅ Status cleared.", ephemeral=True)
    else:
        label = {"playing": "Playing ", "watching": "Watching ", "listening": "Listening to ",
                 "competing": "Competing in "}.get(kind, "")
        await ctx.send(f"✅ Status set to: **{label}{text}**", ephemeral=True)


# ---------------- Restart ----------------
restart_requested = False


@bot.hybrid_command()
@commands.is_owner()
async def restart(ctx):
    """(Owner only) Restarts the bot."""
    await ctx.send("🔄 Restarting...", ephemeral=True)
    print("[restart] Restart requested by", ctx.author)
    await restart_bot()


async def restart_bot():
    global restart_requested
    restart_requested = True
    await bot.close()


BOT_DIR = Path(__file__).parent


async def run_cmd(*args):
    """Runs a program in the bot folder. Returns (exit code, output text)."""
    proc = await asyncio.create_subprocess_exec(
        *args, cwd=BOT_DIR,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    out, _ = await proc.communicate()
    return proc.returncode, out.decode(errors="replace").strip()


@bot.hybrid_command()
@commands.is_owner()
async def update(ctx):
    """(Owner only) Pulls the latest code from GitHub and restarts."""
    await ctx.defer(ephemeral=True)
    try:
        _, before = await run_cmd("git", "rev-parse", "HEAD")
        code, output = await run_cmd("git", "pull", "--ff-only")
    except FileNotFoundError:
        await ctx.send("❌ git isn't installed on this computer.", ephemeral=True)
        return
    if code != 0:
        await ctx.send(f"❌ git pull failed:\n```{output[-1500:]}```", ephemeral=True)
        return

    _, after = await run_cmd("git", "rev-parse", "HEAD")
    if before == after:
        await ctx.send("✅ Already up to date, nothing to restart.", ephemeral=True)
        return

    _, changed = await run_cmd("git", "diff", "--name-only", before, after)
    _, log = await run_cmd("git", "log", "--oneline", f"{before}..{after}")
    msg = f"⬇️ Pulled new code:\n```{log[:1200]}```"

    if "requirements.txt" in changed.splitlines():
        code, pip_out = await run_cmd(sys.executable, "-m", "pip", "install", "-r", "requirements.txt")
        if code != 0:
            await ctx.send(msg + f"\n❌ Installing requirements failed, not restarting:\n```{pip_out[-800:]}```",
                           ephemeral=True)
            return
        msg += "\n📦 Installed new requirements."

    await ctx.send(msg + "\n🔄 Restarting...", ephemeral=True)
    print("[update] Updated to", after[:7], "- restarting")
    await restart_bot()


bot_token = os.getenv("DISCORD_TOKEN")
bot.run(bot_token)

if restart_requested:
    # Start a fresh copy of the bot with the same command it was launched with
    os.execv(sys.executable, [sys.executable] + sys.argv)
