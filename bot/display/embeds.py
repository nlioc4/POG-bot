from discord import Embed, Color
import modules.config as cfg
from datetime import datetime as dt
from datetime import timezone as tz

from modules.roles import isAdmin
from modules.enumerations import MatchStatus



def register_help(msg):
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
        pass  # if msg is from bot
    return embed


def lobby_help(msg):
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

def admin_help(msg):
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


def default_help(msg):
    """ Returns fallback help embed
    """
    embed = Embed(colour=Color.red())
    embed.add_field(name  = 'No available command',
                    value = 'You are not supposed to use the bot on this channel',
                    inline = False)
    return embed


def map_help(ctx):
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


def timeout_help(ctx):
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


def muted_help(ctx):
    """ Returns help for muted players embed
    """
    embed = Embed(colour=Color.blurple())
    embed.add_field(name  = 'You are currently muted!',
                    value = '`=escape` See how long you are muted for, give back permissions if no longer muted',
                    inline = False)
    return embed


def match_help(msg):
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


def account(msg, account):
    """ Returns account message embed
    """
    desc = ""
    color = None
    if account.isDestroyed:
        desc = "This account token is no longer valid"
        color = Color.dark_grey()
    elif account.isValidated:
        desc = f'Id: `{account.strId}`\n' + f'Username: `{account.ident}`\n' + f'Password: `{account.pwd}`\n' + 'Note: This account is given to you only for the time of **ONE** match'
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


def auto_help(msg):
    """ Return help embed depending on current channel """
    if msg.channel.id == cfg.channels['register']:
        return register_help(msg)
    if msg.channel.id == cfg.channels['lobby']:
        return lobby_help(msg)
    if msg.channel.id in cfg.channels['matches']:
        return match_help(msg)
    if msg.channel.id == cfg.channels['muted']:
        return muted_help(msg)
    if msg.channel.id == cfg.channels['staff']:
        return admin_help(msg)
    return default_help(msg)


def lobby_list(msg, namesInLobby):
    """ Returns the lobby list """
    embed = Embed(colour=Color.blue())
    listOfNames = "\n".join(namesInLobby)
    if listOfNames == "":
        listOfNames = "Queue is empty"
    embed.add_field(name=f'Lobby: {len(namesInLobby)} / {cfg.general["lobby_size"]}', value=listOfNames, inline = False)
    return embed


# def selected_maps(msg, sel):
#     """ Returns a list of maps after a search selected
#     """
#     embed = Embed(colour=Color.blue())
#     embed_text = sel.toString() + f"\n⤾ - Back to Maps"
#     embed.add_field(name=f"{len(sel.getSelection())} maps found", value=embed_text, inline=False)
#     return embed


def selected_maps(msg, sel):
    """ Returns a list of maps currently selected
    """
    embed = Embed(colour=Color.blue())
    maps = sel.stringList
    embed.add_field(name=f"{len(maps)} maps found",value="\n".join(maps),inline = False)
    return embed

def offline_list(msg, pList):
    embed = Embed(
        colour=Color.red(),
        title='Offline Players',
        description=f'If your character info is incorrect, re-register using `=r` in <#{cfg.channels["register"]}>!'
    )
    embed.add_field(name  = "The following players are not online ingame:",
                    value = "\n".join(f"{p.igName} ({p.mention})" for p in pList),
                    inline = False)

    return embed


def global_info(msg, lobby, match_list):
    embed = Embed(
        colour=Color.greyple(),
        title='Global Info',
        description=f'POG bot version `{cfg.VERSION}`'
    )
    lb_embed = lobby_list(msg, namesInLobby=lobby).fields[0]
    embed.add_field(name = lb_embed.name, value = lb_embed.value, inline = lb_embed.inline)
    for m in match_list:
        desc = ""
        if m.status is not MatchStatus.IS_FREE:
            if m.round_no != 0:
                desc += f"*Match {m.number} - Round {m.round_no}*"
            else:
                desc += f"*Match {m.number}*"
            desc += "\n"
        desc += f"Status: {m.status_string}"
        if m.status in (MatchStatus.IS_WAITING, MatchStatus.IS_PLAYING, MatchStatus.IS_RESULT):
            desc += f"\nBase: **{m.map.name}**\n"
            desc += " / ".join(f"{tm.name}: **{cfg.factions[tm.faction]}**" for tm in m.teams)
        if m.status is MatchStatus.IS_PLAYING:
            desc += f"\nTime Remaining: **{m.formated_time_to_round_end}**"
        embed.add_field(name  = m.channel.name, value = desc, inline = False)
    return embed

def pil_accounts(msg, account_names):
    embed = Embed(
        colour=Color.red(),
        title='PIL Account!',
        description=f'The password of your PIL account have been flipped!'
    )
    embed.add_field(name  = "Characters affected:",
                    value = "\n".join(i_name for i_name in account_names),
                    inline = False)

    return embed

def team_update(arg, match):
    """ Returns the current teams
    """
    # title = ""
    if match.round_no != 0:
        title = f"Match {match.number} - Round {match.round_no}"
    else:
        title = f"Match {match.number}"
    desc = match.status_string
    if match.status is MatchStatus.IS_PLAYING:
        desc += f"\nTime Remaining: **{match.formated_time_to_round_end}**"
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
        value += "Players:\n" + '\n'.join(tm.player_pings)
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
        embed.add_field(name=f'Remaining', value="\n".join(match.player_pings), inline = False)
    return embed


def jaeger_calendar(arg):
    """ Returns an embedded link to the formatted Jaeger Calendar
    """
    embed = Embed(colour=Color.blue(), title="Jaeger Calendar",
                  url="https://docs.google.com/spreadsheets/d/1eA4ybkAiz-nv_mPxu_laL504nwTDmc-9GnsojnTiSRE",
                  description="Pick a base currently available in the calendar!")
    date = dt.now(tz.utc)
    embed.add_field(name="Current UTC time",
                    value=date.strftime("%Y-%m-%d %H:%M UTC"),
                    inline=False)
    return embed


def map_pool(msg, mapSel):
    map = mapSel.navigator.current
    if map is not None:
        if map.name in cfg.map_pool_images:
            embed = Embed(colour=Color.blue(), title=map.name)
            embed.set_author(name="Click here for the map pool document",
                            url="https://docs.google.com/presentation/d/1KEDlqHxbpG2zXxuEZetAM9IpUHIisWTnrtybn3Kq-Is/")
            embed.set_image(url=cfg.map_pool_images[map.name])
        else:
            embed = Embed(colour=Color.red(), title="No map image available")
    return embed