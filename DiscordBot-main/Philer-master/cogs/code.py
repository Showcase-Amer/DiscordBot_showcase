import json
import time
from discord.ext import commands
from philerfunctions import *

class code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded id command")
    

    @commands.command()
    async def code(self, ctx):
        canUseCommand = checkRole(ctx.author, "Clown")

        if not canUseCommand:
            await ctx.reply("You cant use that command")
            return
        
        try:
            amount = ctx.message.content.split(' ') [3]
        except:
            amount = 1
    

        try:
            value = ctx.message.content.split(' ') [2]
        
        except:
            await ctx.reply("Crystal amount missing.")
            return

        if value is None:
            await ctx.reply("Crystal amount missing.")
            return

        print(amount)
        for x in range(int(amount)):
            try:
                code = generateCode(int(value))
            except:
                code = generateCode(choice((-2000, -1200, -600, -400, 400, 600, 1200, 2000)))

            await ctx.reply(code)

async def setup(bot):
    await bot.add_cog(code(bot))
