import discord
from discord.ext import commands
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "mentions.json"
CHANNEL_FILE = "channel.json"

# ================== تحميل البيانات ==================

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        mention_counts = json.load(f)
else:
    mention_counts = {}

if os.path.exists(CHANNEL_FILE):
    with open(CHANNEL_FILE, "r") as f:
        data = json.load(f)
        CHANNEL_ID = data.get("channel_id")
else:
    CHANNEL_ID = None


def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(mention_counts, f)


def save_channel(channel_id):
    with open(CHANNEL_FILE, "w") as f:
        json.dump({"channel_id": channel_id}, f)

# ================== فحص الروم القديم ==================

async def scan_channel(channel):
    async for message in channel.history(limit=None):
        for user in message.mentions:
            uid = str(user.id)
            mention_counts[uid] = mention_counts.get(uid, 0) + 1

    save_data()

# ================== أوامر ==================

@bot.command()
async def setchannel(ctx):
    global CHANNEL_ID

    CHANNEL_ID = ctx.channel.id
    save_channel(CHANNEL_ID)

    await ctx.send(f" {ctx.channel.mention}")

@bot.command()
async def mentions(ctx):
    global CHANNEL_ID

    if CHANNEL_ID is None:
        await ctx.send("❌ ما فيه روم محدد، استخدم !setchannel")
        return

    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        await ctx.send("❌ ما قدرت أوصل للروم المحدد")
        return

    # أول تشغيل = فحص القديم
    if not mention_counts:
        await ctx.send("⏳")
        await scan_channel(channel)
        await ctx.send("✅ ")

    if not mention_counts:
        await ctx.send("ما فيه أي بيانات.")
        return

    msg = "** المكلجين بالترتيب :**\n\n"

    for uid, count in sorted(mention_counts.items(), key=lambda x: x[1], reverse=True):
        try:
            user = await bot.fetch_user(int(uid))
            msg += f"{user.mention}: {count}\n"
        except:
            msg += f"User-{uid}: {count}\n"

    await ctx.send(msg)

# ================== تشغيل البوت ==================

bot.run(TOKEN)
