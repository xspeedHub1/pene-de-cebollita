import discord
from discord.ext import commands
import json
import os
from datetime import datetime

import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise RuntimeError("No se encontró la variable DISCORD_TOKEN.")

PREFIX = "?"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

WARN_FILE = "warns.json"

def load_warns():
    if os.path.exists(WARN_FILE):
        with open(WARN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_warns(warns):
    with open(WARN_FILE, "w") as f:
        json.dump(warns, f, indent=4)

warns = load_warns()

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="?175 warn @user"))

@bot.command(name="175")
async def warn_command(ctx, action: str = None, member: discord.Member = None, *, reason: str = "Sin razón"):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Necesitas ser Administrador.")
        return
    
    if action is None:
        embed = discord.Embed(title="📋 Sistema de Warns 175", color=discord.Color.blue())
        embed.add_field(name="?175 warn @user [razón]", value="Dar un warn", inline=False)
        embed.add_field(name="?175 warns @user", value="Ver warns", inline=False)
        embed.add_field(name="?175 clear @user", value="Limpiar warns", inline=False)
        await ctx.send(embed=embed)
        return
    
    if action.lower() == "warns":
        if member is None:
            await ctx.send("❌ Uso: ?175 warns @user")
            return
        user_id = str(member.id)
        user_warns = warns.get(user_id, [])
        if not user_warns:
            await ctx.send(f"✅ {member.mention} no tiene warns.")
            return
        embed = discord.Embed(title=f"📊 Warns de {member.display_name}", description=f"Total: {len(user_warns)}/3", color=discord.Color.orange())
        for i, warn in enumerate(user_warns, 1):
            embed.add_field(name=f"⚠️ Warn #{i}", value=f"Razón: {warn['reason']}\nPor: {warn['moderator']}", inline=False)
        await ctx.send(embed=embed)
        return
    
    if action.lower() == "clear":
        if member is None:
            await ctx.send("❌ Uso: ?175 clear @user")
            return
        user_id = str(member.id)
        if user_id in warns:
            del warns[user_id]
            save_warns(warns)
            await ctx.send(f"✅ Warns de {member.mention} eliminados.")
        else:
            await ctx.send(f"❌ {member.mention} no tiene warns.")
        return
    
    if action.lower() == "warn":
        if member is None:
            await ctx.send("❌ Uso: ?175 warn @user [razón]")
            return
        if member == ctx.author:
            await ctx.send("❌ No puedes warnear a ti mismo.")
            return
        
        user_id = str(member.id)
        if user_id not in warns:
            warns[user_id] = []
        
        if len(warns[user_id]) >= 3:
            await ctx.send(f"⚠️ {member.mention} ya tiene 3 warns, BANEADO.")
            try:
                await member.ban(reason="3 warns - Sistema 175")
                await ctx.send(f"🔨 {member.mention} baneado.")
            except:
                await ctx.send("❌ Error al banear.")
            return
        
        warn_data = {"reason": reason, "moderator": ctx.author.display_name, "date": datetime.now().strftime("%d/%m/%Y")}
        warns[user_id].append(warn_data)
        save_warns(warns)
        total = len(warns[user_id])
        
        await ctx.send(f"⚠️ {member.mention} recibió warn #{total}/3\n📝 Razón: {reason}")
        
        if total == 3:
            try:
                await member.ban(reason="3 warns - Sistema 175")
                await ctx.send(f"🔨 {member.mention} baneado por 3 warns.")
            except:
                await ctx.send("❌ Error al banear.")
