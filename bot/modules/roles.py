# @CHECK 2.0 features OK

import modules.config as cfg
from modules.exceptions import ElementNotFound
from modules.enumerations import PlayerStatus

from discord import Status
from discord import PermissionOverwrite

_rolesDict = dict()
_guild = None


def init(client):
    global _guild
    _guild = client.get_channel(cfg.channels["rules"]).guild
    _rolesDict["registered"] = _guild.get_role(cfg.roles["registered"])
    _rolesDict["notify"] = _guild.get_role(cfg.roles["notify"])
    _rolesDict["info"] = _guild.get_role(cfg.roles["info"])
    _rolesDict["admin"] = _guild.get_role(cfg.roles["admin"])


def isAdmin(member):
    """ Check if user is admin
    """
    if member is None:
        return False
    return _rolesDict["admin"] in member.roles


async def forceInfo(pId):
    global _guild
    memb = _guild.get_member(pId)
    if memb is None:
        return
    if _rolesDict["info"] not in memb.roles:
        await memb.add_roles(_rolesDict["info"])
    if _rolesDict["registered"] in memb.roles:
        await memb.remove_roles(_rolesDict["registered"])
    if _rolesDict["notify"] in memb.roles:
        await memb.remove_roles(_rolesDict["notify"])


async def roleUpdate(player):
    if player.isTimeout:
        await forceInfo(player.id)
        return
    await permsMuted(False, player.id)
    global _guild
    memb = _guild.get_member(player.id)
    if memb is None:
        return
    if player.status is PlayerStatus.IS_REGISTERED and player.isNotify and memb.status not in (Status.offline, Status.dnd):
        if _rolesDict["notify"] not in memb.roles:
            await memb.add_roles(_rolesDict["notify"])
        if _rolesDict["registered"] in memb.roles:
            await memb.remove_roles(_rolesDict["registered"])
    else:
        if _rolesDict["registered"] not in memb.roles:
            await memb.add_roles(_rolesDict["registered"])
        if _rolesDict["notify"] in memb.roles:
            await memb.remove_roles(_rolesDict["notify"])
    if _rolesDict["info"] in memb.roles:
        await memb.remove_roles(_rolesDict["info"])


async def permsMuted(value, pId):
    global _guild
    memb = _guild.get_member(pId)
    if memb is None:
        return
    channel = _guild.get_channel(cfg.channels["muted"])
    if value:
        over = _guild.get_channel(cfg.channels["lobby"]).overwrites_for(_rolesDict["registered"])
        if memb not in channel.overwrites:
            await channel.set_permissions(memb, overwrite=over)
    else:
        if memb in channel.overwrites:
            await channel.set_permissions(memb, overwrite=None)


async def channelFreeze(value, id):
    global _guild
    channel = _guild.get_channel(id)
    ov_notify = channel.overwrites_for(_rolesDict["notify"])
    ov_registered = channel.overwrites_for(_rolesDict["registered"])
    ov_notify.send_messages = not value
    ov_registered.send_messages = not value
    await channel.set_permissions(_rolesDict["notify"], overwrite=ov_notify)
    await channel.set_permissions(_rolesDict["registered"], overwrite=ov_registered)
