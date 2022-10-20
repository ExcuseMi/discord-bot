# bot.py
import os
import json
import stats
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from dateutil import parser
from datetime import timezone
import datetime
import random
import pytz

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
vipQuoteFile = 'vip-posts.json'
bannedChannelsFile = 'banned-channels.json'
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')
VIP = os.getenv('VIP')
VIP_MESSAGE_CHANNEL = os.getenv('VIP_MESSAGE_CHANNEL')
intents = discord.Intents.all()
bot = commands.Bot(intents=discord.Intents.all(), command_prefix="rl")
slash = SlashCommand(bot, sync_commands=True)
guild_ids = [int(GUILD)] # Put your server ID in this array.
#playlists = ['Rumble']
playlists = ['Ranked Duel 1v1','Ranked Doubles 2v2','Ranked Standard 3v3']

actualGuild = None
def getUsers():
    if os.path.exists(userFile):
        f = open(userFile)
        users = json.load(f)
    else:
        users = {}
    return users
def getBannedChannels():
    if os.path.exists(bannedChannelsFile):
        f = open(bannedChannelsFile)
        bannedChannels = json.load(f)
    else:
        bannedChannels = []
    return bannedChannels
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
    if stat:
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
        if role.name in ranks.keys():
            rlRoles.append(role)
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
                log(member.name + ': ' + bestRank)
                if not bestRank in rlRoles:
                    roles = await guild.fetch_roles()
                    role = findRole(roles, bestRank)
                    if role:
                        await member.add_roles(role, atomic=True)
                for rlRole in rlRoles:
                    if rlRole.name != bestRank:
                        await member.remove_roles(rlRole)


@slash.slash(name="wwds", description="What would Dire say?", guild_ids=guild_ids, options=[
    create_option(
      name="keyword",
      description="keyword",
      required=False,
      option_type=3
    )
  ]
)
async def _wwds(ctx, keyword = None):
    vipQuotes = getVipQuotes()
    if vipQuotes:
        messages = vipQuotes['messages']
        if messages:
            if keyword: 
                lowerKeyword = keyword.lower()
                messages = list(filter(lambda message: lowerKeyword in message['content'].lower(), messages))
            if len(messages) > 0:
                random_item = random.choice(messages)
                member = await ctx.guild.fetch_member(int(VIP))
                timestamp = parser.parse(random_item['created_at'])
    
                embed = discord.Embed(
                            colour=discord.Colour(0xE5E242),
                            url=random_item['url'],
                            title="What would " + member.display_name + " say?",
                            timestamp=timestamp,
                            description=random_item['content']
                        )


                embed.set_author(name=member.display_name, icon_url=member.avatar_url)
                embed.set_footer(text='That\'s what ' + member.display_name + ' said!')  
                await ctx.send(embed=embed)         
            else:
                await ctx.send('Nothing found')
        else:
            await ctx.send('whoops')
    else:
        await ctx.send('whoops')

@slash.slash(name="rl-register", description="Register to have the DireBot read your rocket league rank.", guild_ids=guild_ids, options=[
    create_option(
      name="epic_username",
      description="Epic Username",
      required=True,
      option_type=3
    )
  ]
)
async def _register(ctx, epic_username):
    addToUserData(ctx.author.id, epic_username)
    await ctx.send("You been added to the RL registry!")

@slash.slash(name="rl-unregister", description="Unregister", guild_ids=guild_ids
)
async def _unregister(ctx,):
    removeFromUserData(ctx.author.id)
    member = await ctx.guild.fetch_member(ctx.author.id)
    rlRoles = findRLRoles(member)
    if len(rlRoles) > 0:
        for rlRole in rlRoles:
            await ctx.author.remove_roles(rlRole)
    await ctx.send("You been removed from the registry!")

@slash.slash(name="rl-playlists", description="Playlist I use to rank to you on this discord", guild_ids=guild_ids
)
async def _playlists(ctx):
    await ctx.send('\n'.join(playlists))



def removekey(d, key):
    r = dict(d)
    if key in r.keys():
        del r[key]
    return r

def removeFromUserData(id):
    users = getUsers()
    users = removekey(users, str(id))
    jsonStr = json.dumps(users, indent=4)
    with open(userFile, "w") as outfile:
        outfile.write(jsonStr)

def addToUserData(id, epic_username):
    users = getUsers()
    users[str(id)] = { 'epic-username' : epic_username}
    jsonStr = json.dumps(users, indent=4)
    with open(userFile, "w") as outfile:
        outfile.write(jsonStr)

def getVipQuotes():
    if os.path.exists(vipQuoteFile):
        f = open(vipQuoteFile)
        vipQuotes = json.load(f)
    else:
        vipQuotes = { 'messages': [], 'lastReadMessage':None }

    return vipQuotes

def parseMessage(message):
    if message.content and len(message.embeds) == 0:
        return { 'id' : message.id, 'content': message.content, 'authorid': message.author.id, 'created_at': message.created_at.isoformat(), 'url': message.jump_url, 'channel': message.channel.id}
    return None
def sortQuoteBy(quote):
    return quote['created_at']

async def readFullHistory( vipId):
    log('Reading full history')
    vipQuotes = getVipQuotes()
    messageList = vipQuotes['messages']
    limit = 200
    bannedChannels = getBannedChannels()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if not channel.id in bannedChannels:
                messages = await channel.history(limit=limit).flatten()
                while (len(messages) > 0):
                    vipMessages = filter(lambda message: message.author.id == int(vipId), messages)
                    myMesssages = list(filter(lambda message: message != None, map(lambda message : parseMessage(message), vipMessages)))
                    for m in myMesssages:
                        log('vip-content - ' + m['created_at'] + '-' + m['content'])
                    messageList.extend(myMesssages)
                    messages = await channel.history(limit=limit, before=messages[-1].created_at).flatten()

    messageList.sort(key=sortQuoteBy)
    vipQuotes['messages'] = messageList
    vipQuotes['lastReadMessage'] = datetime.datetime.now(pytz.utc).replace(tzinfo=None).isoformat()

    jsonStr = json.dumps(vipQuotes, indent=4)
    with open(vipQuoteFile, "w") as outfile:
        outfile.write(jsonStr)
    log('Done Reading full history')

def log(message):
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ": " + message)

async def readPartialHistory(vipId):
    log('Reading partial history')

    limit = 100
    vipQuotes = getVipQuotes()
    messageList = vipQuotes['messages']
    if vipQuotes.get('lastReadMessage'):
        lastReadMessage = parser.parse(vipQuotes['lastReadMessage'])
    else:
        lastReadMessage = None
    log('lastReadMessage: ' + vipQuotes['lastReadMessage'])
    bannedChannels = getBannedChannels()

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if not channel.id in bannedChannels:

                messages = await channel.history(limit=limit, after=lastReadMessage).flatten()
                while (len(messages) > 0):
                    vipMessages = filter(lambda message: message.author.id == int(vipId), messages)
                    myMesssages = list(filter(lambda message: message != None, map(lambda message : parseMessage(message), vipMessages)))
                    for m in myMesssages:
                        log('vip-content - ' + m['created_at'] + '-' + m['content'])

                    messageList.extend(myMesssages)
                    lastReadMessage = messages[-1].created_at
                    messages = await channel.history(limit=limit, after=lastReadMessage).flatten()

    messageList.sort(key=sortQuoteBy)
    vipQuotes['messages'] = messageList
    vipQuotes['lastReadMessage'] = datetime.datetime.now(pytz.utc).replace(tzinfo=None).isoformat()
    jsonStr = json.dumps(vipQuotes, indent=4)
    with open(vipQuoteFile, "w") as outfile:
        outfile.write(jsonStr)
    log('Done Reading partial history')

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.name == GUILD:
            actualGuild = guild
            break
    
    #for role in guild.roles:
    #    if role.name in ranks.keys():
    #        await role.delete()
    if False:
        for rank in list(ranks.keys()):
            role = findRole(guild.roles, rank)
            if(role == None):
                role = await guild.create_role(name=rank, hoist=True, colour=ranks[rank]['color'], mentionable=True)
            else:
                await role.edit(hoist=True, colour=ranks[rank]['color'], mentionable=True)

    log(
        f'{bot.user} is connected to the following guild: \n' 
        f'{guild.name} (id: {guild.id})'
    )

    # just trying to debug here
    if False:
        channels = '\n - '.join([channel.name + '-' + str(channel.id) for channel in guild.text_channels])

        members = '\n - '.join([member.name + '-' + str(member.id) for member in guild.members])
        roles = '\n - '.join([role.name + '-' + str(role.position) for role in guild.roles])

        log(f'Guild Channels:\n - {channels}')
        log(f'Guild Members:\n - {members}')
        log(f'Guild Roles:\n - {roles}')
@bot.event
async def on_message(message):
    if message.author.id == 238349304891310080:
        await message.delete()
        
import asyncio
import traceback
import threading
timerDelay = 60*10
lastResultJson = None

async def my_background_task():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await updateVipPosts()
        await updateStats()
        await asyncio.sleep(timerDelay)
async def updateVipPosts():
    try:
        vipQuotes = getVipQuotes()
        if vipQuotes != None and vipQuotes.get('lastReadMessage') != None:
            await readPartialHistory(VIP)
        else:
            await readFullHistory(VIP)
    except:
       traceback.print_exc()
async def updateStats():
    try:
        if os.path.exists(userFile):
            with open('stats.json',) as f:
                previousJson = f.read()
        else:
            previousJson = None
        log('Getting rocket league stats')
        stats = getAllStats()
        jsonStr = json.dumps(stats, indent=4)
        if previousJson != jsonStr:
            await processData(stats)
            with open('stats.json', "w") as outfile:
                outfile.write(jsonStr)
        log('Done rocket league stats')
    except:
        traceback.print_exc()

bot.loop.create_task(my_background_task())
bot.run(TOKEN)
