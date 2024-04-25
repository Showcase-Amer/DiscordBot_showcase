import discord
from discord import app_commands
from discord.ext import commands
from philerfunctions import *
import asyncio
from random import shuffle


class connectFour(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(aliases=["connect4", "connectfour"])
    async def connect(self, ctx):
        try:
            opponent = self.bot.get_user(pingToID(ctx.message.content.split(' ') [2]))
            amount = int(ctx.message.content.split(' ') [3])
        except:
            await ctx.reply("Something went wrong. Try again")
            return
        
        ownProfile = getUserValues(ctx.author.id)

        level = ownProfile["level"]
        crystals = ownProfile["crystals"]


        limit = calculateLevelCrystalRel(level)

        if crystals > limit and amount != 0:
            await ctx.reply("You currently own more crystals than your limit. Use 0 crystals to play games.")
            return

        cangamble = ableToGamble(ctx.author.id, amount)

        if cangamble != True:
            await ctx.reply(cangamble)
            return
        

        if amount < 0:
            await ctx.reply("Your number can't be negative.")
            return

        opponentProfile = getUserValues(opponent.id)

        if opponentProfile is None:
            await ctx.reply("Opponent doesn't have a profile.")
            return
        
        if opponentProfile["crystals"] < amount:
            await ctx.reply("Opponent doesn't have enough crystals.")
            return
        
        if int(amount) % 200 != 0:
            await ctx.reply("You number has to be dividable by 200.")
            return
        
        if opponentProfile["crystals"] + amount > 5000:
            await ctx.reply(f'Opponent has too many crystals. The maximum challange amount is **{5000 - opponentProfile["crystals"]}.**')
            return


        yes = '✔️'
        no = '❌'

        validReactions = ['❌',  '✔️']

        message = await ctx.reply(f"Challenged **{opponent.name}** to Connect Four. Waiting for him/her to accept the match.")


        await message.add_reaction(yes)
        await message.add_reaction(no)

        
        try:
            def check(reaction, user):
                return user == opponent and str(reaction.emoji) in validReactions and reaction.message.id == message.id

            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

        except asyncio.TimeoutError:
            await ctx.reply("Connect Four offer expired.")
            return
        
        if str(reaction) == yes:
            cangamble = ableToGamble(ctx.author.id, amount)

            if cangamble != True:
                await ctx.reply(f"{ctx.author.mention} doesn't have enough crystals anymore.")
                return

            guild = ctx.message.guild
            category = discord.utils.get(ctx.guild.categories, name="GAME MODES")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(send_messages=False),
                ctx.author: discord.PermissionOverwrite(send_messages=True),
                opponent: discord.PermissionOverwrite(send_messages=True),
                self.bot.user: discord.PermissionOverwrite(send_messages=True)
            }

            channel = await guild.create_text_channel(f"╠-connect4-room-{randrange(1,101)}", category=category, overwrites=overwrites)
            await ctx.reply(f"**{opponent.name}** accepted your match. Go to {channel.mention}")

            rows = 6
            columns = 7

            board = [["","","","","","",""], 
                    ["","","","","","",""],
                    ["","","","","","",""],
                    ["","","","","","",""],
                    ["","","","","","",""],
                    ["","","","","","",""]]
                    


            for x in range(rows):
                for y in range(columns):
                    board[x][y] = "⬛"

            def checkGameFull():
                topRow = board[0]
                for item in topRow:
                    if item == "⬛":
                        return False
                return True

            def boardToText():
                text = ""
                for row in board:
                    for item in row:
                        text += item
                    text += "\n"
                text += "1⃣2⃣3⃣4⃣5⃣6⃣7⃣"
                return text

            def createEmbed(dc):
                textboard = boardToText()
                embed = discord.Embed(title="Connect four", description=f"Turn: {dc.mention}\n{textboard}", color=discord.Colour.green())
                #embed.add_field(name=f"Connect 4 pieces to win", value=f"Turn: {dc.mention}\n{textboard}")
                embed.set_footer(text=f"{playerList[0].discord.name} {playerList[0].color} • {playerList[1].discord.name} {playerList[1].color}")
                return embed
            

            def insertCoin(row, column, color):

                if board[-row][column - 1] != "⬛":
                    return insertCoin(row + 1, column, color)

                board[-row][column - 1] = color


            def checkForWinner(chip):
                # horizontal
                for row in range(rows):
                    field = board[row]
                    for x in range(columns - 3):
                        #print(field[x], field[x + 1], field[x + 2], field[x + 3])
                        if field[x] == chip and field[x + 1] == chip and field[x + 2] == chip and field[x + 3] == chip:
                            print("horizontal")
                            return True, chip

                # vertical
                for row in range(rows - 3):
                    for x in range(columns):
                        if board[row][x] == chip and board[row + 1][x] == chip and board[row + 2][x] == chip and board[row + 3][x] == chip:
                            print("vertical")
                            return True, chip


                for row in range(rows - 3): #4
                    #print(board[-row])
                    for x in range(columns - 3):
                        #print(board[row])
                        #print(board[row][x])
                        #print(board[-row])
                        #print(board[-row][x], board[-row - 1][x + 1], board[-row - 2][x + 2], board[-row - 3][x + 3])
                        for index, item in enumerate(board):
                            print(index, item)
                        print(board[row][-x], board[row + 1][-x - 1], board[row + 2][-x - 2], board[row + 3][-x -3])
                        if board[-row][x] == chip and board[-row - 1][x + 1] == chip and board[-row - 2][x + 2] == chip and board[-row - 3][x + 3] == chip:
                            print("bottom Left to top right")
                            return True, chip
                        

                        elif board[row][-x - 1] == chip and board[row + 1][-x - 2] == chip and board[row + 2][-x - 3] == chip and board[row +3][-x - 4] == chip:
                            print(row, -x)
                            print("top right to botton left")
                            return True, chip


                        elif board[-row][-x] == chip and board[-row - 1][-x -1] == chip and board[-row - 2] and board[-row - 2][-x -2] == chip and board[-row - 3][-x - 3] == chip:
                            print("bottom right to top left")
                            return True, chip
 
                        elif board[row][x] == chip and board[row + 1][x + 1] == chip and board[row + 2][x + 2] == chip and board[row + 3][x + 3] == chip:
                            print("top left to bottom right")
                            return True, chip

                            #print("     0----1----2----3----4----5----6")
                            """""
                            if lul[row][x] == chip and lul[row + 1][x + 1] == chip and lul[row + 2][x + 2] and lul[row + 3][x + 3] == chip:
                                print("Right to left")
                                return True, chip
                            """
                            #print(board[row][-x], board[row + 1][-x - 1], board[row + 2][-x - 2], board[row +3][-x - 3])
                            print(row, -x)
                            print("Right to left")
                            return True, chip

                return False, None

            class ConnectFourPlayer():
                def __init__(self, discord, color):
                    self.discord = discord
                    self.color = color


            player1 = ConnectFourPlayer(ctx.author, "🔴")
            player2 = ConnectFourPlayer(opponent, "🟡")
            playerList = [player1, player2]
            shuffle(playerList)

            scoreEmbed = createEmbed(playerList[0].discord)
            msg = await channel.send("Setting up...")
            reactions = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣"]

            reactionDic = {}

            counter = 1
            for reaction in reactions:
                await msg.add_reaction(reaction)
                reactionDic[reaction] = counter
                counter += 1
            
            await msg.edit(embed=scoreEmbed, content='')


            noWinner = False
            subtractCrystals(ctx.author. id, int(amount))
            subtractCrystals(opponent.id, int(amount))

            while not noWinner:
                for player in playerList:
                    try:

                        embed = createEmbed(player.discord)
                        await msg.edit(embed=embed)


                        def check(reaction, user):
                            return str(reaction) in reactions and user.id == player.discord.id and reaction.message.id == msg.id

                        validReaction = False
                        while not validReaction:
                            reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=120.0)

                            for key, value in reactionDic.items():
                                if key == str(reaction):
                                    try:
                                        insertCoin(1, value, player.color)
                                        await msg.remove_reaction(str(reaction), user)
                                        validReaction = True
                                        break
                                    except IndexError:
                                        await channel.send(f"{user.mention} you cant insert a coin at this position.")
                        noWinner, winnerColor = checkForWinner(player.color)
                        fullGame = checkGameFull()

                        if noWinner:
                            embed = createEmbed(player.discord)
                            await msg.edit(embed=embed)
                            break
                        elif fullGame:
                            embed = createEmbed(player.discord)
                            await msg.edit(embed=embed)
                            noWinner = True
                            break


                    except asyncio.TimeoutError:
                        await channel.send(f"{player.discord.mention} did not make a selection.")
                        
                        if player == player1:
                            addCrystals(player2.discord.id, int(amount * 2))
                            await channel.send(f"{player2.discord.mention} won {int(amount) * 2} crystals.")
                        else:
                            addCrystals(player1.discord.id, int(amount * 2))
                            await channel.send(f"{player1.discord.mention} won {int(amount) * 2} crystals.")                            

                        await stopGame(channel)
                        return

            print("Game ended")

            if fullGame:
                await channel.send("All slots are occupied. Nobody won.")
                addCrystals(player1.discord.id, int(amount))
                addCrystals(player2.discord.id, int(amount))
                await stopGame(channel)
                return

            for player in playerList:
                if player.color == winnerColor:
                    await channel.send(f"{player.discord.mention} won **{amount}** crystals.")
                    addCrystals(player.discord.id, int(amount) * 2)
                    await stopGame(channel)


        elif str(reaction) == no:
            await ctx.reply(f"{opponent.mention} did not accept your match.")
async def setup(bot):
    await bot.add_cog(connectFour(bot))