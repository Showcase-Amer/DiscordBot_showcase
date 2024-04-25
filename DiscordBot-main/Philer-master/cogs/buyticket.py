import discord
from discord.ext import commands
from philerfunctions import *

class buyticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded inventory command")
    

    @commands.command()
    async def buyticket(self, ctx):
        user = getUserValues(ctx.author.id)

        if user is None:
            await ctx.reply("You don't have a profile.")
            return

        try:
            amount = int(ctx.message.content.split(' ') [2])
            print(amount)
        except:
            amount = 1

        if user["crystals"] - 400 * amount < 0:
            await ctx.reply(f"You dont have enough crystals to buy **{amount}** ticket(s)")
            return

        subtractCrystals(ctx.author.id, 400 * amount)
        addToJackpot(ctx.author, amount)
        await ctx.reply(f"Succesfully bought **{amount}** ticket(s). Good Luck! ")

async def setup(bot):
    await bot.add_cog(buyticket(bot))