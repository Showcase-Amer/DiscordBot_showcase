import discord
from discord.ext import commands
from philerfunctions import *
from discord import app_commands


maps = [
            "Bazaar",
            "Jaguar Falls",
            "Serpent Beach",
            "Ice Mines",
            "Fish Market",
            "Stone Keep",
            "Brightmarsh",
            "Splitstone Quarry",
            "Ascension Peak",
            "Shattered Desert"
        ]

class mapCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded inventory command")
    

    @commands.command()
    async def map(self, ctx):
        yourmap = choice(maps)

        await ctx.reply(f"Your map is going to be **{yourmap}**.")


    @app_commands.command(name="map", description="Picks a random map")
    async def slashMap(self, interaction: discord.Interaction):
        yourmap = choice(maps)

        await interaction.response.send_message(f"Your map is going to be **{yourmap}**.")

async def setup(bot):
    await bot.add_cog(mapCommand(bot))