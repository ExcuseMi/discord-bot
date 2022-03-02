# bot.py
import os
import discord
import json
import stats
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

ranks = {
    'Supersonic Legend' : { 'color': discord.Colour(0x65186D)}, 
    'Grand Champion III' : { 'color': discord.Colour(0x981ECD)},
    'Grand Champion II' : { 'color': discord.Colour(0x981ECD)},
    'Grand Champion I' : { 'color': discord.Colour(0x981ECD)},
    'Champion III' : { 'color': discord.Colour(0xd6c2fb)},
    'Champion II' : { 'color': discord.Colour(0xc0aee1)},
    'Champion I' : { 'color': discord.Colour(0xab9bc8)},
    'Diamond III' : { 'color': discord.Colour(0x46cae1)},
    'Diamond II' : { 'color': discord.Colour(0x3eb4c8)},
    'Diamond I' : { 'color': discord.Colour(0x4ee1fb)},
    'Platinum III' : { 'color': discord.Colour(0x9EE2F2)},
    'Platinum II' : { 'color': discord.Colour(0x9EE2F2)},
    'Platinum I' : { 'color': discord.Colour(0x9EE2F2)},
    'Gold III' : { 'color': discord.Colour(0xEFDA33)},
    'Gold II' : { 'color': discord.Colour(0xEFDA33)},
    'Gold I' : { 'color': discord.Colour(0xEFDA33)},
    'Silver III' : { 'color': discord.Colour(0x8F9596)},
    'Silver II' : { 'color': discord.Colour(0x8F9596)},   
    'Silver I' : { 'color': discord.Colour(0x8F9596)},
    'Bronze III' : { 'color': discord.Colour(0xCF8035)},
    'Bronze II' : { 'color': discord.Colour(0xCF8035)},
    'Bronze I' : { 'color': discord.Colour(0xCF8035)},
    'Unranked' : { 'color': discord.Colour(0x4C4E53)}
     }
   
userFile = 'users.json'
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')

intents = discord.Intents.all()
bot = commands.Bot(intents=discord.Intents.all(), command_prefix="rl")
slash = SlashCommand(bot, sync_commands=True)
guild_ids = [int(GUILD)] # Put your server ID in this array.
playlists = ['Ranked Duel 1v1','Ranked Doubles 2v2','Ranked Standard 3v3']

actualGuild = None
def getUsers():
    if os.path.exists(userFile):
        f = open(userFile)
        users = json.load(f)
    else:
        users = {}
    return users

def getAllStats():
    users = getUsers()
    if(len(users) > 0):
        epicUsers = list(map(lambda user: users[user].get('epic-username'), users))
        return stats.getAllStats(epicUsers)
    return None
def matchRank(rank):
    for r in list(ranks.keys()):
        if rank.get('name') == r:
            return r
    return None
def getBestRank(stat):
    userRank = None
    ranknames = list(ranks.keys())
    for s in stat:
        if s in playlists:
            matchedRank = matchRank(stat[s])
            if matchedRank:
                if userRank == None or ranknames.index(matchedRank) < ranknames.index(userRank):
                    userRank = matchedRank
    return userRank

def findRLRoles(member):
    rlRoles = []
    for role in member.roles:   
        if role in ranks.keys():
            rlRoles.append(member)
    return rlRoles

def findRole(roles, name):
    for role in roles:
        if role.name == name:
            return role
    return None

async def processData(stats):
    users = getUsers()
    for user in users:
        userData = users[user]
        username = userData.get('epic-username')
        if username:
            stat = stats.get(username)
            bestRank = getBestRank(stat)
            if bestRank:
                guild = await bot.fetch_guild(guild_ids[0])
                member = await guild.fetch_member(int(user))
                rlRoles = findRLRoles(member)
                print(member.name + ': ' + bestRank)
                if not bestRank in rlRoles:
                    roles = await guild.fetch_roles()
                    role = findRole(roles, bestRank)
                    if role:
                        await member.add_roles(role, atomic=True)
                for rlRole in rlRoles:
                    await member.remove_roles(rlRole)


@slash.slash(name="rl-register", description="Register to have the DireBot read your rocket league rank.", guild_ids=guild_ids, options=[
    create_option(
      name="epic_username",
      description="Epic Username",
      required=True,
      option_type=3
    )
  ]
)
async def _register(ctx, epic_username): # Defines a new "context" (ctx) command called "ping."
    ctx.author.id
    addToUserData(ctx.author.id, epic_username)
    await ctx.send("You been added to the RL registry!")


def addToUserData(id, epic_username):
    users = getUsers()
    users[str(id)] = { 'epic-username' : epic_username}
    jsonStr = json.dumps(users, indent=4)
    with open(userFile, "w") as outfile:
        outfile.write(jsonStr)

       
@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            actualGuild = guild
            break

    #for role in guild.roles:
    #    if role.name in ranks.keys():
    #        await role.delete()
    

    for rank in list(ranks.keys()):
        role = findRole(guild.roles, rank)
        if(role == None):
            role = await guild.create_role(name=rank, hoist=True, colour=ranks[rank]['color'], mentionable=True)
        else:
            await role.edit(hoist=True, colour=ranks[rank]['color'], mentionable=True)

    print(
        f'{bot.user} is connected to the following guild: \n' 
        f'{guild.name} (id: {guild.id})'
    )

    # just trying to debug here

    channels = '\n - '.join([channel.name + '-' + str(channel.id) for channel in guild.text_channels])

    members = '\n - '.join([member.name + '-' + str(member.id) for member in guild.members])
    roles = '\n - '.join([role.name + '-' + str(role.position) for role in guild.roles])

    print(f'Guild Channels:\n - {channels}')
    print(f'Guild Members:\n - {members}')
    print(f'Guild Roles:\n - {roles}')

import asyncio
import traceback

timerDelay = 10*1
async def my_background_task():
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(CHANNEL) # replace with channel_id
    lastResultJson = None
    while not bot.is_closed():
        try:
            stats = getAllStats()
            jsonStr = json.dumps(stats, indent=4)
            #if lastResultJson != jsonStr:
                #for s in stats:
                    #await channel.send(s + ': ' + json.dumps(stats[s], indent=4))
            lastResultJson = jsonStr
            with open('stats.json', "w") as outfile:
                outfile.write(jsonStr)
            await processData(stats)

        except:
            traceback.print_exc()
      
        await asyncio.sleep(timerDelay)

bot.loop.create_task(my_background_task())

bot.run(TOKEN)