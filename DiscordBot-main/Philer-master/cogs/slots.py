import discord
from discord.ext import commands
from philerfunctions import *
from random import randint

def all_same(items):
    return all(x == items[0] for x in items)

class slots(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded slots command")
    

    @commands.command()
    async def slots(self, ctx):
        user = getUserValues(ctx.author.id)


        if user is None:
            await ctx.reply("You don't have a profile.")
            return
        
        userinventory = user["inventory"]
        freespins = userinventory["freespins"]

        if user["crystals"] >= 5000:
            await ctx.reply("You have reached the limit of 5k crystals. Leave some for the rest greedy muffin.")
            return

        if freespins <= 0:
            if user["crystals"] < 200:
                await ctx.reply("You need alteast 200 crystals.")
                return
        

        if freespins > 0:
            removeInventoryItem(ctx.author.id, "freespins", 1)
        else:
            subtractCrystals(ctx.author.id, 200)
            addGambleSpendings(ctx.author.id, 200)
        
        if randint(1, 100) == 50:
            wonFreeSpins = randint(1, 8)
            await ctx.reply(f"💎 | 💎 | 💎 YOU WON **{wonFreeSpins}** free spins!")
            addInventoryItem(ctx.author.id, "freespins", wonFreeSpins)
            return


        fruits = ["🍒", "🍋", "🍑", "🍍"]

        result = []
        for x in range(3):
            result.append(choice(fruits))

        stringResults = " | ".join(result)


        win = all_same(result)

        if win:
            if randint(1, 3) == 2:
                await ctx.reply(f"{stringResults} YOU WON **2000** CRYSTALS")
                addCrystals(ctx.author.id, 2000)
                addGambleEarnings(ctx.author.id, 2000)
                return
            else:
                print("avoided jackpot")
                await ctx.reply("🍋 | 🍒 |  🍑 You lost. Better luck next time")

        elif result[0] == result[1]:
            await ctx.reply(f"{stringResults} YOU WON **400** CRYSTALS")
            addCrystals(ctx.author.id, 400)
            addGambleEarnings(ctx.author.id, 400)
            return

        else:
            await ctx.reply(f"{stringResults} You lost. Better luck next time")
            return


async def setup(bot):
    await bot.add_cog(slots(bot))