import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"
CHANNEL_FILE = "channel.json"

# ================== تحميل البيانات ==================

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
else:
    data = {}

if os.path.exists(CHANNEL_FILE):
    with open(CHANNEL_FILE, "r") as f:
        CHANNEL_ID = json.load(f).get("channel_id")
else:
    CHANNEL_ID = None

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def save_channel(cid):
    with open(CHANNEL_FILE, "w") as f:
        json.dump({"channel_id": cid}, f)

# ================== جلب بيانات روم ==================

def get_channel_data(channel_id):
    cid = str(channel_id)
    if cid not in data:
        data[cid] = {}
    return data[cid]

# ================== فحص الروم القديم ==================

async def scan_channel(channel):
    channel_data = get_channel_data(channel.id)

    async for message in channel.history(limit=None):
        for user in message.mentions:
            uid = str(user.id)
            channel_data[uid] = channel_data.get(uid, 0) + 1

    save_data()

# ================== أوامر ==================

@bot.command()
async def setchannel(ctx):
    global CHANNEL_ID

    CHANNEL_ID = ctx.channel.id
    save_channel(CHANNEL_ID)

    await ctx.send(f": {ctx.channel.mention}")

@bot.command()
async def mentions(ctx):
    global CHANNEL_ID

    if CHANNEL_ID is None:
        await ctx.send("❌ استخدم !setchannel أول")
        return

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        await ctx.send("❌ ما قدرت أوصل للروم")
        return

    channel_data = get_channel_data(CHANNEL_ID)

    # أول مرة يسوي سكان
    if not channel_data:
        await ctx.send("⏳ ...")
        await scan_channel(channel)
        await ctx.send("✅ ")

    channel_data = get_channel_data(CHANNEL_ID)

    if not channel_data:
        await ctx.send("ما فيه بيانات.")
        return

    msg = "**📊 توب المنغوليين:**\n\n"

    for uid, count in sorted(channel_data.items(), key=lambda x: x[1], reverse=True):
        try:
            user = await bot.fetch_user(int(uid))
            msg += f"{user.mention} — {count} تكليجه\n"
        except:
            msg += f"User-{uid} — {count} تكليجه\n"

    await ctx.send(msg)

# ================== تحديث مباشر (الجديد) ==================

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if CHANNEL_ID and message.channel.id == CHANNEL_ID:
        channel_data = get_channel_data(CHANNEL_ID)

        for user in message.mentions:
            uid = str(user.id)
            channel_data[uid] = channel_data.get(uid, 0) + 1

        save_data()

    await bot.process_commands(message)

# ================== تشغيل ==================

bot.run(TOKEN)
