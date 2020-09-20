"""Discord bot display module

It contains all the functions and the strings that can be outputed by the bot.

It must be used by the rest of the programm for all the messages sent by the bot.

All the strings sent can then be modified easely in this file.

Import this module and use only the following public function:

    * channelSend(stringName, id, *args, **kwargs)
    * privateSend(stringName, id, *args, **kwargs)
    * send(stringName, ctx, *args, **kwargs)
    * edit(stringName, ctx, *args, **kwargs)

"""

# discord.py
from discord import Embed, Color, TextChannel, Message, User, File
from discord.ext.commands import Context

from datetime import datetime as dt
from datetime import timezone as tz

# Others
from enum import Enum

# Custom modules
import modules.config as cfg
from modules.enumerations import MatchStatus
from modules.tools import isAlNum
from modules.roles import isAdmin

_client = None


## PUBLIC:

def init(client):
    global _client
    _client = client

async def channelSend(stringName, id, *args, **kwargs):
    """ Send the message stringName in the channel identified with id, with aditional strings *args. Pass **kwargs to the embed function, if any
        Returns the message sent
    """
    channel = _client.get_channel(id)
    return await _StringEnum[stringName].value.display(channel, channel.send,  *args, **kwargs)

async def privateSend(stringName, id, *args, **kwargs):
    """ Send the message stringName in dm to user identified with id, with aditional strings *args. Pass **kwargs to the embed function, if any
        Returns the message sent
    """
    user = _client.get_user(id)
    return await _StringEnum[stringName].value.display(user, user.send, *args, **kwargs)

async def send(stringName, ctx, *args, **kwargs):
    """ Send the message stringName in context ctx, with aditional strings *args. Pass **kwargs to the embed function, if any
        Returns the message sent
    """
    try:
        sendFct = ctx.send
    except AttributeError:
        sendFct = _client.get_channel(ctx.channel.id).send
    return await _StringEnum[stringName].value.display(ctx, sendFct, *args, **kwargs)

async def edit(stringName, ctx, *args, **kwargs):
    """ Replaces the message ctx by the message stringName, with aditional strings *args. Pass **kwargs to the embed function, if any
        Returns the message sent
    """
    return await _StringEnum[stringName].value.display(ctx, ctx.edit,  *args, **kwargs)

async def remReaction(message, user=None):
    if user is None:
        global _client
        user = _client.user
    return await message.remove_reaction("✅", user)

async def imageSend(stringName, channelId, imagePath, *args):
    channel = _client.get_channel(channelId)
    return await channel.send(content=_StringEnum[stringName].value.string.format(*args), file=File(imagePath))

## PRIVATE:

## Embed functions

def _registerHelp(msg):
    """ Returns register help embed
    """
    embed = Embed(
        colour=Color.blurple(),
        title='How to register?',
        description=f'You have to accept the rules in <#{cfg.channels["rules"]}> to register'
    )
    embed.add_field(name  = 'If you don\'t have a Jaeger account',
                    value = '`=r no account`\n',
                    inline = False)
    embed.add_field(name  = 'If you have a Jaeger account',
                    value = '`=r charName` - If your character names have faction suffixes\n'
                            '`=r charName1 charName2 charName3` - If your character names don\'t have faction suffixes',
                    inline = False)
    embed.add_field(name  = 'Notify feature',
                    value = '`=notify` - To join or leave the Notify feature\n'
                            f'When suscribed to Notify, you can be mentionned with <@&{cfg.roles["notify"]}> '
                            'when the queue is almost full',
                    inline = False)
    try:
        if isAdmin(msg.author):
            embed.add_field(name  = "Staff Commands",
                            value = '`=unregister @player` - Permanently remove player profile from the system\n'
                                    '`=channel freeze`/`unfreeze` - Prevent / Allow players to send messages',
                            inline = False)
    except AttributeError:
        pass # if msg is from bot
    return embed

def _lobbyHelp(msg):
    """ Returns lobby help embed
    """
    embed = Embed(colour=Color.blurple())
    embed.add_field(name  = 'Lobby Commands',
                    value = '`=j` - Join the lobby\n'
                            '`=l` - Leave the lobby\n'
                            '`=q` - See the current lobby\n'
                            '`=i` - Display the global information prompt',
                    inline = False)
    if isAdmin(msg.author):
        embed.add_field(name  = "Staff Commands",
                        value = '`=clear` - Clear the lobby\n'
                                '`=channel freeze`/`unfreeze` - Prevent / Allow players to send messages\n'
                                '`=remove @player` - Remove player from lobby',
                        inline = False)
    return embed

def _adminHelp(msg):
    """ Returns admin help embed
    """
    embed = Embed(colour=Color.blurple())
    embed.add_field(name  = 'Debug Commands',
                    value = '`=channel (un)freeze` - Prevent users from typing in a channel\n'
                            '`=pog version` - Display current version and lock status\n'
                            '`=pog (un)lock` - Prevent users from interacting with the bot (but admins still can)\n',
                    inline = False)
    embed.add_field(name  = 'Lobby Commands',
                    value = '`=remove @player` - Remove the player from queue\n'
                            '`=clear` - Clear queue\n'
                            '`=lobby get` - Get all of the user IDs to restore the lobby\n'
                            '`=lobby restore id id ...` - Re-add all the users back to the lobby',
                    inline = False)
    embed.add_field(name  = 'Player Management Commands',
                    value = '`=timeout @player duration` - Mute the player from POF for a given time\n'
                            '`=unregister @player` - Forcibly unregisters and removes a user from the system',
                    inline = False)
    embed.add_field(name  = 'Match Commands',
                    value = '`=demote @player` - Force `=resign` the player\n'
                            '`=sub @player` - Pick someone in queue to replace the player\n'
                            '`=map name` - Force a map\n'
                            '`=pog ingame` - Toggle the in-game player check',
                    inline = False)
    return embed

def _defaultHelp(msg):
    """ Returns fallback help embed
    """
    embed = Embed(colour=Color.red())
    embed.add_field(name  = 'No available command',
                    value = 'You are not supposed to use the bot on this channel',
                    inline = False)
    return embed

def _mapHelp(ctx):
    """ Returns map help embed
    """
    embed = Embed(colour=Color.blurple())
    cmd = ctx.command.name
    if cmd == "pick":
        cmd = "p"
    embed.add_field(name  = 'Map selection commands',
                    value = f'`={cmd} a base` - Display all the maps containing *a base* in their name\n'
                            f'`={cmd} 3` - Chooses the map number 3 from the selection\n'
                            f'`={cmd}` - Display the current selection or show the help',
                    inline = False)
    return embed

def _timeoutHelp(ctx):
    """ Returns timeout help embed
    """
    embed = Embed(colour=Color.blurple())
    embed.add_field(name  = 'Timeout command',
                    value = '`=timeout @player 10 days` - Mute @player from POG for 10 days\n'
                            '`=timeout @player 10 hours` - Mute @player from POG for 10 hours\n'
                            '`=timeout @player 10 minutes` - Mute @player from POG for 10 minutes\n'
                            '`=timeout @player remove` - Unmute @player from POG\n'
                            '`=timeout @player` - Get info on current timeout for @player',
                    inline = False)
    return embed

def _mutedHelp(ctx):
    """ Returns help for muted players embed
    """
    embed = Embed(colour=Color.blurple())
    embed.add_field(name  = 'You are currently muted!',
                    value = '`=escape` See how long you are muted for, give back permissions if no longer muted',
                    inline = False)
    return embed

def _matchHelp(msg):
    """ Returns match help embed
    """
    embed = Embed(colour=Color.blurple())
    embed.add_field(name  = 'Match commands',
                    value = '`=m` - Display the match status and team composition\n'
                            "`=squittal` - Display player data for integration in Chirtle's script",
                    inline = False)
    embed.add_field(name  = 'Team Captain commands',
                    value = '`=p @player` - Pick a player in your team\n'
                            '`=p VS`/`NC`/`TR` - Pick a faction\n'
                            '`=p base name` - Pick the map *base name*\n'
                            '`=resign` - Resign from Team Captain position\n'
                            '`=ready` - To toggle the ready status of your team',
                    inline = False)
    if isAdmin(msg.author):
        embed.add_field(name  = "Staff Commands",
                        value = '`=clear` - Clear the match\n'
                                '`=map base name` - Force select a map\n'
                                '`=demote @player` - Remove Team Captain position from player\n'
                                '`=sub @player` - Pick someone in queue to replace the player\n'
                                '`=channel freeze`/`unfreeze` - Prevent / Allow players to send messages',
                        inline = False)
    return embed

def _account(msg, account):
    """ Returns account message embed
    """
    desc = ""
    color = None
    if account.isDestroyed:
        desc = "This account token is no longer valid"
        color = Color.dark_grey()
    elif account.isValidated:
        desc =  f'Id: `{account.strId}`\n'+f'Username: `{account.ident}`\n'+f'Password: `{account.pwd}`\n'+'Note: This account is given to you only for the time of **ONE** match'
        color = Color.green()
    else:
        desc = "Accept the rules by reacting with a checkmark to get your account details."
        color = Color.red()
    embed = Embed(
        colour=color,
        title='Jaeger Account',
        description=f'**MUST READ: [Account usage](https://planetsideguide.com/other/jaeger/)**'
    )
    embed.add_field(name = "Logging details",value = desc,inline = False)
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/739231714554937455/739522071423614996/logo_png.png")
    embed.set_footer(
        text='Failure to follow account usage rules can result in your suspension from ALL Jaeger events.')
    return embed

def _autoHelp(msg):
    """ Return help embed depending on current channel
    """
    if msg.channel.id == cfg.channels['register']:
        return _registerHelp(msg)
    if msg.channel.id == cfg.channels['lobby']:
        return _lobbyHelp(msg)
    if msg.channel.id in cfg.channels['matches']:
        return _matchHelp(msg)
    if msg.channel.id == cfg.channels['muted']:
        return _mutedHelp(msg)
    if msg.channel.id == cfg.channels['staff']:
        return _adminHelp(msg)
    return _defaultHelp(msg)

def _lobbyList(msg, namesInLobby):
    """ Returns the lobby list
    """
    embed = Embed(colour=Color.blue())
    listOfNames="\n".join(namesInLobby)
    if listOfNames == "":
        listOfNames = "Queue is empty"
    embed.add_field(name=f'Lobby: {len(namesInLobby)} / {cfg.general["lobby_size"]}',value=listOfNames,inline = False)
    return embed


def _selectedMaps(msg, sel):
    """ Returns a list of maps currently selected
    """
    embed = Embed(colour=Color.blue())
    maps = sel.stringList
    embed.add_field(name=f"{len(maps)} maps found",value="\n".join(maps),inline = False)
    return embed

def _offlineList(msg, pList):
    embed = Embed(
        colour=Color.red(),
        title='Offline Players',
        description=f'If your character info is incorrect, re-register using `=r` in <#{cfg.channels["register"]}>!'
    )
    embed.add_field(name  = "The following players are not online ingame:",
                    value = "\n".join(f"{p.igName} ({p.mention})" for p in pList),
                    inline = False)

    return embed


def _globalInfo(msg, lobby, matchList):
    embed = Embed(
        colour=Color.greyple(),
        title='Global Info',
        description=f'POG bot version `{cfg.VERSION}`'
    )
    lbEmbed = _lobbyList(msg, namesInLobby=lobby).fields[0]
    embed.add_field(name = lbEmbed.name, value = lbEmbed.value, inline = lbEmbed.inline)
    for m in matchList:
        desc = ""
        if m.status is not MatchStatus.IS_FREE:
            if m.roundNo != 0:
                desc += f"*Match {m.number} - Round {m.roundNo}*"
            else:
                desc += f"*Match {m.number}*"
            desc += "\n"
        desc += f"Status: {m.statusString}"
        if m.status in (MatchStatus.IS_WAITING, MatchStatus.IS_PLAYING, MatchStatus.IS_RESULT):
            desc += f"\nBase: **{m.map.name}**\n"
            desc += " / ".join(f"{tm.name}: **{cfg.factions[tm.faction]}**" for tm in m.teams)
        if m.status is MatchStatus.IS_PLAYING:
            desc += f"\nTime Remaining: **{m.formatedTimeToRoundEnd}**"
        embed.add_field(name  = m.channel.name, value = desc, inline = False)
    return embed


def _teamUpdate(arg, match):
    """ Returns the current teams
    """
    channel = None
    try:
        channel = arg.channel
    except AttributeError:
        channel = arg
    #title = ""
    if match.roundNo != 0:
        title = f"Match {match.number} - Round {match.roundNo}"
    else:
        title = f"Match {match.number}"
    desc = match.statusString
    if match.status is MatchStatus.IS_PLAYING:
        desc += f"\nTime Remaining: **{match.formatedTimeToRoundEnd}**"
    embed = Embed(colour=Color.blue(), title=title, description = desc)
    if match.map is not None:
        embed.add_field(name = "Map",value = match.map.name,inline = False)
    for tm in match.teams:
        value = ""
        name = ""
        if tm.captain.isTurn and match.status in (MatchStatus.IS_FACTION, MatchStatus.IS_PICKING):
            value = f"Captain **[pick]**: {tm.captain.mention}\n"
        else:
            value = f"Captain: {tm.captain.mention}\n"
        value += "Players:\n"+'\n'.join(tm.playerPings)
        if match.status is MatchStatus.IS_WAITING:
            if tm.captain.isTurn:
                name = f"{tm.name} [{cfg.factions[tm.faction]}] - not ready"
            else:
                name = f"{tm.name} [{cfg.factions[tm.faction]}] - ready"
        elif tm.faction != 0:
            name = f"{tm.name} [{cfg.factions[tm.faction]}]"
        else:
            name = f"{tm.name}"
        embed.add_field(name = name,
                        value = value,
                        inline = False)
    if match.status is MatchStatus.IS_PICKING:
        embed.add_field(name=f'Remaining',value="\n".join(match.playerPings) ,inline = False)
    return embed

def _jaegerCalendar(arg):
    embed = Embed(colour=Color.blue(), title="Jaeger Calendar", url = "https://docs.google.com/spreadsheets/d/1eA4ybkAiz-nv_mPxu_laL504nwTDmc-9GnsojnTiSRE",
    description = "Pick a base currently available in the calendar!")
    date = dt.now(tz.utc)
    embed.add_field(name = "Current UTC time",
                        value = date.strftime("%Y-%m-%d %H:%M UTC"),
                        inline = False)
    return embed

class _Message():
    """ Class for the enum to use
    """
    def __init__(self, string, ping=True, embed=None):
        self.__str = string
        self.__embedFct = embed
        self.__ping = ping

    @property
    def string(self):
        return self.__str

    async def display(self, ctx, sendFct, *args, **kwargs):
        # If is Context instead of a Message, get the Message:
        embed = None
        msg = None

        try:
            author = ctx.author
        except AttributeError:
            author = None

        # Format the string to be sent with added args
        string = self.__str.format(*args)
        # Send the string
        if self.__embedFct!=None:
            embed = self.__embedFct(ctx, **kwargs)
            # Fixes the embed mobile bug but ugly af:
            #embed.set_author(name="_____________________________")

        if self.__ping and not author is None:
            msg = await sendFct(content=f'{author.mention} {string}', embed=embed)
        else:
            msg = await sendFct(content=string, embed=embed)
        return msg

class _StringEnum(Enum):
    """ List of different message strings available
    """
    REG_NOT_REGISTERED = _Message("You are not registered!",embed=_registerHelp)
    REG_IS_REGISTERED_OWN = _Message("You are already registered with the following Jaeger characters: `{}`, `{}`, `{}`")
    REG_IS_REGISTERED_NOA = _Message("You are already registered without a Jaeger account! If you have your own account, please re-register with your Jaeger characters.")
    REG_HELP = _Message("Registration help:",embed=_registerHelp)
    REG_NO_ACCOUNT = _Message("You successfully registered without a Jaeger account!")
    REG_INVALID = _Message("Invalid registration!",embed=_registerHelp)
    REG_CHAR_NOT_FOUND = _Message("Invalid registration! Character `{}` is not valid!",embed=_registerHelp)
    REG_NOT_JAEGER = _Message("Invalid registration! Character `{}` doesn't belong to Jaeger!",embed=_registerHelp)
    REG_ALREADY_EXIST = _Message("Invalid registration! Character `{}` is already registered by {}!")
    REG_MISSING_FACTION = _Message("Invalid registration! Can't find a {} character in your list!",embed=_registerHelp)
    REG_UPDATE_OWN = _Message("You successfully updated your profile with the following Jaeger characters: `{}`, `{}`, `{}`")
    REG_UPDATE_NOA = _Message("You successfully removed your Jaeger characters from your profile.")
    REG_WITH_CHARS = _Message("You successfully registered with the following Jaeger characters: `{}`, `{}`, `{}`")
    REG_FROZEN = _Message("You can't register while you're playing a match")
    REG_RULES = _Message("{} You have accepted the rules, you may now register", embed=_registerHelp)
    REG_NO_RULE = _Message("You have to accept the rules before registering! Check <#{}>")
    REG_FROZEN_2 = _Message("You can't remove your account while being in a match!")

    LB_OFFLINE = _Message("You can't queue if your Discord status is offline/invisible!")
    LB_ALREADY_IN = _Message("You are already in queue!")
    LB_IN_MATCH = _Message("You are already in a match!")
    LB_ADDED = _Message("You've been added to the queue!",embed=_lobbyList)
    LB_REMOVED = _Message("You've been removed from the queue!",embed=_lobbyList)
    LB_NOT_IN = _Message("You're not in queue!")
    LB_QUEUE = _Message("Current players in queue:",embed=_lobbyList)
    LB_FULL = _Message("Lobby is already full! Waiting for a match to start...")
    LB_STUCK = _Message("Lobby is full, but can't start a new match yet. Please wait...",ping=False)
    LB_STUCK_JOIN = _Message("You can't join the lobby, it is already full!")
    LB_MATCH_STARTING = _Message("Lobby full, match can start! Join <#{}> for team selection!",ping=False)
    LB_WENT_INACTIVE = _Message("{} was removed from the lobby because they went offline!",embed=_lobbyList)
    LB_CLEARED = _Message("Lobby has been cleared!", embed=_lobbyList)
    LB_EMPTY = _Message("Lobby is already empty!")
    LB_NOTIFY = _Message("{} queue is almost full, join to start a match!")
    LB_GET = _Message("Restore the lobby with `=lobby restore {}`")

    PK_OVER = _Message("The teams are already made. You can't pick!")
    PK_NO_LOBBIED = _Message("You must first queue and wait for a match to begin. Check <#{}>")
    PK_WAIT_FOR_PICK = _Message("You can't do that! Wait for a Team Captain to pick you!")
    PK_WRONG_CHANNEL = _Message("You are in the wrong channel! Check <#{}> instead")
    PK_NOT_TURN = _Message("It's not your turn!")
    PK_NOT_CAPTAIN = _Message("You are not Team Captain!")
    PK_SHOW_TEAMS = _Message("Match status:",embed=_teamUpdate)
    PK_HELP = _Message("Picking help:", embed=_matchHelp)
    PK_NO_ARG = _Message("@ mention a player to pick!", embed=_matchHelp)
    PK_TOO_MUCH = _Message("You can't pick more than one player at the same time!")
    PK_INVALID = _Message("You can't pick that player!")
    PK_OK = _Message("Player picked! {} your turn, pick a player!",embed=_teamUpdate, ping=False)
    PK_OK_2 = _Message("Player picked!", ping=False)
    PK_LAST = _Message("Assigned {} to {}!")
    PK_OK_FACTION = _Message("Teams are ready! {} pick a faction!",embed=_teamUpdate, ping=False)
    PK_NOT_VALID_FACTION = _Message("Incorrect input! Pick a valid faction!", embed=_matchHelp)
    PK_FACTION_OK = _Message("{} chose {}!", ping=False)
    PK_FACTION_ALREADY = _Message("Faction already picked by the other team!")
    PK_FACTION_OK_NEXT = _Message("{} chose {}! {} pick a faction!", ping=False)
    PK_FACTION_CHANGED = _Message("{} changed to {}!")
    PK_FACTION_NOT_PLAYER = _Message("Pick a faction, not a player!", embed=_matchHelp)
    PK_OVER_READY = _Message("Can't do that if your team is ready!")
    PK_WAIT_MAP = _Message("{} {} Pick an available map!", ping=False, embed=_jaegerCalendar)
    PK_MAP_OK_CONFIRM = _Message("Picked {}! {} confirm with `=p confirm` if you agree")
    PK_NO_MAP = _Message("No map selected!")
    PK_RESIGNED = _Message("Successfully resigned! {} is the new captain for {}!")
    PK_PICK_STARTED = _Message("Can't do that, you already picked a player!")

    EXT_NOT_REGISTERED = _Message("You are not registered! Check <#{}>")
    UNKNOWN_ERROR = _Message("Something unexpected happened! Please try again or contact staff if it keeps happening.\nDetails: *{}*")
    STOP_SPAM = _Message("Please avoid spamming!")
    HELP = _Message("Available commands:",embed=_autoHelp)
    INVALID_COMMAND = _Message("Invalid command! Type `=help` for the list of available commands.")
    WRONG_USAGE = _Message("Wrong usage of the command `={}`!")
    WRONG_CHANNEL = _Message("The command `={}` can only be used in {}")
    WRONG_CHANNEL_2 = _Message("The command `={}` can't be used in {}")
    NO_PERMISSION = _Message("The command `={}` can only be used by staff members!")
    CHANNEL_INIT = _Message("`Bot init`: Correctly hooked in channel <#{}>")
    INVALID_STR = _Message("You entered an invalid caracter! `{}`")
    API_ERROR = _Message("Could not reach Planetside2 API, try again later!")
    GLOBAL_INFO = _Message("Here is what's going on in POG at the moment:", embed=_globalInfo)

    BOT_UNLOCKED = _Message("Unlocked!")
    BOT_LOCKED = _Message("Locked!")
    BOT_IS_LOCKED = _Message("Bot is locked!")
    BOT_ALREADY = _Message("Already {}!")
    BOT_VERSION = _Message("Version `{}`, locked: `{}`")
    BOT_FROZEN = _Message("Channel frozen!")
    BOT_UNFROZEN = _Message("Channel unfrozen!")
    BOT_BP_OFF = _Message("Ingame status check is now enabled!")
    BOT_BP_ON = _Message("Ingame status check is now disabled!")

    MATCH_INIT = _Message("{}\nMatch is ready, starting team selection...")
    MATCH_SHOW_PICKS = _Message("Captains have been selected, {} choose a player",embed=_teamUpdate)
    MATCH_MAP_AUTO = _Message("Match will be on **{}**", ping=False)
    MATCH_CONFIRM = _Message("{} {} Type `=ready` when your team is inside their sundy, ready to start", embed=_teamUpdate)
    MATCH_NOT_READY = _Message("You can't use command `={}`, the match is not ready!")
    MATCH_TEAM_READY = _Message("{} is now ready!", embed=_teamUpdate)
    MATCH_TEAM_UNREADY = _Message("{} is no longer ready!", embed=_teamUpdate)
    MATCH_STARTING_1 = _Message("Everyone is ready, round {} is starting in {} seconds!\nAll players will be pinged on round start")
    MATCH_STARTING_2 = _Message("Round {} is starting in {} seconds!")
    MATCH_STARTED = _Message("{}\n{}\nRound {} is starting now!")
    MATCH_NO_MATCH = _Message("Can't use command `={}`, no match is happening here!")
    MATCH_NO_COMMAND = _Message("Can't use command `={}` now!")
    MATCH_CLEARED = _Message("Successfully cleared!")
    MATCH_PLAYERS_NOT_READY = _Message("Can't get {} ready, {} did not accept their Jaeger accounts", ping=False)
    MATCH_PLAYERS_OFFLINE = _Message("Can't get {} ready, {} are not online in game!", ping=False, embed=_offlineList)
    MATCH_CLEAR = _Message("Clearing match...",ping=False)
    MATCH_MAP_SELECTED = _Message("Successfully selected **{}**")
    MATCH_ROUND_OVER = _Message("{}\n{}\nRound {} is over!")
    MATCH_OVER = _Message("The match is over!\nClearing channel...")
    MATCH_ALREADY = _Message("The match is already started!")
    MATCH_SWAP = _Message("Swap sundy placement for the next round!")

    MAP_HELP = _Message("Here is how to choose a map:", embed = _mapHelp)
    MAP_TOO_MUCH = _Message("Too many maps found! Try to be more precise")
    MAP_NOT_FOUND = _Message("Couldn't find a result for your search!")
    MAP_DISPLAY_LIST = _Message("Here are the maps found:", embed=_selectedMaps)
    MAP_SHOW_POOL = _Message("Map list:", embed=_selectedMaps)
    MAP_SELECTED = _Message("The current map is **{}**")

    MP_ADDED = _Message("Added {} to the map pool")
    MP_REMOVED = _Message("Removed {} from the map pool")

    ACC_NOT_ENOUGH = _Message("Not enough accounts are available for this match!\n**Match has been canceled!**")
    ACC_ERROR = _Message("Error when giving out Jaeger accounts!\n**Match has been canceled!**")
    ACC_UPDATE = _Message("", ping=False,embed=_account)
    ACC_SENT = _Message("**Successfully sent jaeger accounts  in DMs!**")
    ACC_SENDING = _Message("Loading Jaeger accounts...")
    ACC_OVER = _Message("Match is over, please log out of your Jaeger account!")
    ACC_CLOSED = _Message("{}'s DMS are locked, can't send them a Jaeger account!")

    NOTIFY_REMOVED = _Message("You left Notify!")
    NOTIFY_ADDED = _Message("You joined Notify!")

    NOT_CODED = _Message("The rest is not yet coded, work in progress. Clearing match...")

    RM_MENTION_ONE = _Message("Invalid request! @ mention one player!")
    RM_NOT_IN_DB = _Message("Can't find this player in the database!")
    RM_OK = _Message("Player successfully removed from the system!")
    RM_IN_MATCH = _Message("Can't remove a player who is in match!")
    RM_LOBBY = _Message("{} have been removed by staff!",embed=_lobbyList)
    RM_NOT_LOBBIED = _Message("This player is not in queue!")
    RM_TIMEOUT = _Message("{} will be muted from POG until {}!", ping=False)
    RM_TIMEOUT_FREE = _Message("{} is no longer muted!", ping=False)
    RM_TIMEOUT_ALREADY = _Message("Can't do that, player is not muted!")
    RM_TIMEOUT_HELP = _Message("Command usage:", embed=_timeoutHelp)
    RM_TIMEOUT_INVALID = _Message("Invalid use of the command!", embed=_timeoutHelp)
    RM_TIMEOUT_INFO = _Message("Player is muted until {}!")
    RM_TIMEOUT_NO = _Message("Player is not muted!")
    RM_DEMOTE_NO = _Message("Can't demote this player!")
    RM_DEMOTE_OK = _Message("Successfully demoted! {} is the new captain for {}!", ping=False)
    RM_DEMOTE_PICKING = _Message("Can't demote a captain who has already started picking!")

    MUTE_SHOW = _Message("You are muted from POG until {}!")
    MUTE_FREED = _Message("You are no longer muted from POG!")

    SC_ILLEGAL_WE = _Message("{} used {} during match {}! This weapon is banned! Ignoring {} kill(s)...")
    SC_PLAYERS_STRING = _Message("Here is player data for squittal script:\n{}")
    SC_RESULT_HALF = _Message("Match {} - **halftime**")
    SC_RESULT = _Message("Match {}")

    SUB_NO = _Message("This player can't be subbed!")
    SUB_NO_CAPTAIN = _Message("Can't sub a Team Captain!")
    SUB_NO_PLAYER = _Message("No player is available to substitute!")
    SUB_OKAY_TEAM = _Message("{} replaced {} in {}", ping=False, embed=_teamUpdate)
    SUB_OKAY = _Message("{} replaced {}!", ping=False, embed=_teamUpdate)
    SUB_LOBBY = _Message("{} you have been designed as a substitute, join <#{}>!", embed=_lobbyList)