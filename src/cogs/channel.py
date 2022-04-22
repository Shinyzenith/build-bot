import logging
import os
from typing import Literal

import aiohttp
import coloredlogs
import disnake
from disnake.ext import commands, tasks

from utils.database import SqliteSingleton

test_guilds=[870887565274808393]

log = logging.getLogger("Channel cog")
coloredlogs.install(logger=log)

class ReleaseChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.notify_task.start()
        self.api_base_url=os.getenv("VERSIONS_API_BASE_URL")
        self.buildids = {
                "stable": '',
                "canary": '',
                "ptb": ''
            }

    @commands.Cog.listener()
    async def on_ready(self):
        log.warn(f"{self.__class__.__name__} Cog has been loaded")

    @tasks.loop(seconds=30, reconnect=False)
    async def notify_task(self):
        await self.bot.wait_until_ready()
        headers = { "X-API-Key": os.getenv("DISCORD_VERSION_API_KEY") }
        async with aiohttp.ClientSession() as session:
            for release_channel in self.buildids.keys():
                async with session.get(f"{self.api_base_url}buildid/{release_channel}", headers=headers) as response:
                    response = await response.json()
                    if response['build_id'] != self.buildids[release_channel]:
                        self.buildids[release_channel] = response['build_id']
                        cursor = await self.bot.conn.execute(f"SELECT {release_channel}_id FROM channel_data;")
                        channels = await cursor.fetchall()
                        await self.bot.conn.commit()
                        await cursor.close()
                        for channel in channels:
                            if channel[0] == None:
                                continue
                            async with session.get(f"{self.api_base_url}version/{release_channel}", headers=headers) as response:
                                response = await response.json()
                            embed=disnake.Embed(title=f"New {release_channel} build.")
                            embed.add_field(name="Build Number:",value=response['BuildNumber'])
                            embed.add_field(name="Version Hash:",value=response['VersionHash'])
                            await self.bot.get_channel(channel[0]).send(embed=embed)

    #TODO: Add error handler cog.
    #TODO: Add option to mention a role on notification.
    #TODO: Add slash command to REMOVE announcement channel ids.
    #TODO: Add slash command to check current server configuration.
    @commands.slash_command(name="SetReleaseChannel", guild_ids=test_guilds)
    @commands.cooldown(10, 60, commands.BucketType.guild)
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def set_canary(self, inter: disnake.ApplicationCommandInteraction, release_channel: Literal["stable", "ptb", "canary"], channel: disnake.TextChannel):
        """Set announcement channel for any release cycle.

        Parameters
        ----------
        release_channel: Discord release cycles.
        channel: Announcement channel for afore mentioned release cycle.
        """

        inter.response.defer
        cursor = await self.bot.conn.execute(f"SELECT {release_channel}_id FROM channel_data WHERE guild_id='{inter.guild.id}';")
        data = await cursor.fetchall()
        await self.bot.conn.commit()
        await cursor.close()

        if len(data)==0:
            await inter.response.send_message(f"Creating a database record for {inter.guild.name}...", ephemeral=True)
            cursor = await self.bot.conn.execute(f"INSERT INTO channel_data(guild_id,{release_channel}_id) VALUES ({inter.guild.id},{channel.id});")
            await self.bot.conn.commit()
            await cursor.close()
            return await inter.edit_original_message(content=f"{release_channel.capitalize()} announcement channel has been set.")
        elif data[0][0] == None:
            await inter.response.send_message(f"Creating a database record for {release_channel} announcement channel...", ephemeral=True)
            cursor = await self.bot.conn.execute(f"UPDATE channel_data SET {release_channel}_id={channel.id} WHERE guild_id={inter.guild.id};")
            await self.bot.conn.commit()
            await cursor.close()
            return await inter.edit_original_message(content=f"{release_channel.capitalize()} announcement channel has been set.")
        else:
            await inter.response.send_message(f"{release_channel.capitalize()} channel has already been set. Updating it...", ephemeral=True)
            cursor = await self.bot.conn.execute(f"UPDATE channel_data SET {release_channel}_id={channel.id} WHERE guild_id={inter.guild.id};")
            await self.bot.conn.commit()
            await cursor.close()
            await inter.edit_original_message(content=f"{release_channel.capitalize()} announcement channel has been been set to {channel.id}.")

def setup(bot: commands.Bot):
    bot.add_cog(ReleaseChannel(bot))
