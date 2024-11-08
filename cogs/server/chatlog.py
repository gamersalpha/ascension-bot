import json
import nextcord
import aiohttp
import re
from nextcord.ext import commands, tasks
from settings import (
    CHATLOG_CHANNEL,
    WEBHOOK_URL,
    WEBHOOK_AVATAR
)
from gamercon_async import GameRCON
import asyncio

class ChatLogCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_config()
        self.channel_id = CHATLOG_CHANNEL
        self.session = aiohttp.ClientSession()
        self.filters = [
            'Server received, But no response!!',
            'AdminCmd',
            'Tribe Tamed a',
            'Tribe ',
            'Tamed a',
            'was killed!',
            'added to the Tribe',
            'RichColor',
            'RCON: Not connected',
            'froze'
        ]
        self.rcon_cooldown = 320
        self.get_chat.start()

    def load_config(self):
        config_path = '/app/data/config.json'
        with open(config_path) as config_file:
            config = json.load(config_file)
            self.servers = config["RCON_SERVERS"]

    @tasks.loop(seconds=1)
    async def get_chat(self):
        await self.bot.wait_until_ready()
        for server_name in self.servers:
            await self.send_rcon_command(server_name, "GetChat")

    async def send_rcon_command(self, server_name, command):
        server = self.servers[server_name]
        try:
            async with GameRCON(server["RCON_HOST"], server["RCON_PORT"], server["RCON_PASS"]) as ac:
                response = await ac.send(command)
                await self.parse_message(server_name, response)
        except Exception as error:
            print(f'Error in {server_name}:', error)
            await asyncio.sleep(self.rcon_cooldown)
      
    async def parse_message(self, server_name, res):
        if "Server received, But no response!!" not in res and not any(filter_word in res for filter_word in self.filters):
            match = re.search(r"(.+?) \((.+?)\): (.+)", res)
            if match:
                _, name_within_parentheses, message = match.groups()
                webhook_name = f"{name_within_parentheses} ({server_name})"
                await self.send_webhook(webhook_name, message)

    async def send_webhook(self, name, message):
        webhook = nextcord.Webhook.from_url(WEBHOOK_URL, session=self.session)
        await webhook.send(
            content=message,
            username=name,
            avatar_url=WEBHOOK_AVATAR
        )

    def cog_unload(self):
        self.get_chat.cancel()
        self.bot.loop.create_task(self.session.close())

def setup(bot):
    bot.add_cog(ChatLogCog(bot))
