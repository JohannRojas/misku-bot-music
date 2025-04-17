import os, asyncio, discord, yt_dlp
from discord.ext import commands

FFMPEG_PATH = "C:\\Users\\User\\Documents\\Programmer\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe"
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

queues = {}  # Diccionario:-> lista de canciones

def get_queue(guild_id):
    return queues.setdefault(guild_id, [])


@bot.event
async def on_ready():
    print(f"✅  Conectado como {bot.user} ({bot.user.id})")

@bot.command()
async def next(ctx):
    queue = get_queue(ctx.guild.id)
    if not queue:
        await ctx.send("📭 La cola está vacía.")
        return
    song = queue.pop(0)

    source = await discord.FFmpegOpusAudio.from_probe(song['url'], executable=FFMPEG_PATH, **FFMPEG_OPTS)
    ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(next(ctx), bot.loop))

    embed = discord.Embed(
        title="▶️ Reproduciendo",
        description=f"**{song['title']}**\n🎙️ Autor: `{song['uploader']}`",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"🎧 Pedido por: {song['requester']}")
    await ctx.send(embed=embed)


@bot.command()
async def play(ctx, *, query: str):

    # Si el canal de voz no está conectado, se conecta.
    if ctx.author.voice:
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
    else:
        await ctx.reply("🚫 Debes estar en un canal de voz.")
        return
    
        """Reproduce un audio (URL o búsqueda)."""
    vc = ctx.voice_client or await ctx.author.voice.channel.connect()

    data = ytdl.extract_info(query, download=False)
    info = data["entries"][0] if "entries" in data else data
    url = info["url"]
    title = info.get("title", "Sin título")
    uploader = info.get("uploader", "Sin autor")

    queue = get_queue(ctx.guild.id)
    queue.append({
        "url": url,
        "title": title,
        "uploader": uploader,
        "requester": ctx.author.name
    })

    if not ctx.voice_client.is_playing():
        await next(ctx)
    else:
        await ctx.send(f"🎶 Agregado a la cola: **{title}**")

@bot.command()
async def leave(ctx):
    """Sale del canal de voz."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        queues.pop(ctx.guild.id, None)
        await ctx.send("👋 Me fui del canal de voz.")
bot.run(os.getenv("DISCORD_TOKEN"))