from .command import InstantiatedCommand, Command, picking_states
from match.classes import CaptainValidator
from match.common import after_pick_sub, get_check_captain
from match import MatchStatus

from display import AllStrings as disp, ContextWrapper

import modules.roles as roles
from classes import Player

class SubHandler(InstantiatedCommand):
    def __init__(self, obj):
        super().__init__(self, self.sub)
        self.validator = None
        self.sub_func = None
        self.factory = obj

    @property
    def match(self):
        return self.factory.match

    def start(self):
        self.validator = CaptainValidator(self.match)
        try:
            self.sub_func = self.match.get_process_attr("do_sub")
        except AttributeError:
            self.sub_func = None

        @self.validator.confirm
        async def do_sub(ctx, subbed, force_player=None):
            if self.sub_func:
                await self.sub_func(subbed, force_player)
            else:
                await after_pick_sub(self.match, subbed, force_player)

    def stop(self):
        self.validator.clean()

    def update(self):
        try:
            self.sub_func = self.match.get_process_attr("do_sub")
        except AttributeError:
            self.sub_func = None

    def on_team_ready(self, team):
        if "subbed" in self.validator.kwargs:
            player = self.validator.kwargs["subbed"]
            if player.active and (player.active.team is team):
                self.stop()

    @Command.command(*picking_states)
    async def sub(self, ctx, args):
        captain = None
        if not roles.is_admin(ctx.author):
            captain, msg = get_check_captain(ctx, self.match, check_turn=False)
            if msg:
                await msg
                return

            if await self.validator.check_message(ctx, captain, args):
                return

        if len(ctx.message.mentions) not in (1, 2):
            await disp.RM_MENTION_ONE.send(ctx)
            return

        subbed = Player.get(ctx.message.mentions[0].id)
        if not subbed:
            await disp.RM_NOT_IN_DB.send(ctx)
            return
        if not(subbed.match and subbed.match.id == self.match.id):
            await disp.SUB_NO.send(ctx)
            return
        if subbed.active and subbed.active.is_playing:
            await disp.SUB_RDY.send(ctx)
            return

        # Can't have a swap command running at the same time
        await self.factory.swap.stop()

        if roles.is_admin(ctx.author):
            player = None
            if len(ctx.message.mentions) == 2:
                player = Player.get(ctx.message.mentions[1].id)
                if not player:
                    await disp.RM_NOT_IN_DB.send(ctx)
                    return
                elif player.match:
                    await disp.SUB_NO.send(ctx)
                    return
            await self.validator.force_confirm(ctx, subbed=subbed, force_player=player)
            return
        else:
            other_captain = self.match.teams[captain.team.id - 1].captain
            msg = await disp.SUB_OK_CONFIRM.send(self.match.channel, subbed.mention, other_captain.mention)
            await self.validator.wait_valid(captain, msg, subbed=subbed)
