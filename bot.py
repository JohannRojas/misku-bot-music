import os, asyncio, discord, yt_dlp
from discord.ext import commands

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"        
}
ytdl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "ytsearch",  
}
ytdl = yt_dlp.YoutubeDL(ytdl_opts)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅  Conectado como {bot.user} ({bot.user.id})")

@bot.command()
async def join(ctx):
    """El bot entra al canal de voz del autor."""
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
    else:
        await ctx.reply("🚫 Debes estar en un canal de voz.")

@bot.command()
async def play(ctx, *, query: str):
    """Reproduce un audio (URL o búsqueda)."""
    vc = ctx.voice_client or await ctx.author.voice.channel.connect()

    data = ytdl.extract_info(query, download=False)
    url = data["url"] if "url" in data else data["entries"][0]["url"]

    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTS)
    vc.play(source, after=lambda e: print("Finalizó" if not e else e))

    await ctx.reply(f"▶️ Reproduciendo **{data.get('title', query)}**")

@bot.command()
async def leave(ctx):
    """Sale del canal de voz."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

bot.run(os.getenv("DISCORD_TOKEN"))