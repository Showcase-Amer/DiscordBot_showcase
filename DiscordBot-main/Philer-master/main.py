import discord
from discord.ext import commands, tasks
from random import randint, choice, random
import asyncio
import os
from philerfunctions import *
import json

bot = commands.Bot(command_prefix="!phil ",
                   intents=discord.Intents.all(),
                   case_insensitive=True)

rouletteParticipants = []

global canPlaceBet
canPlaceBet = False

global rouletteActive
rouletteActive = False

global PreviousCaptain
PreviousCaptain = None


def getRouletteWinners(color, multiplier):
  winners = ''
  global rouletteParticipants
  for participant in rouletteParticipants:
    print(participant)
    if participant["color"] == color:
      userid = participant["userid"]
      username = participant["username"]
      amount = participant["amount"]
      choice = participant["color"]

      if choice == color:
        addCrystals(userid, amount * multiplier)
        addGambleEarnings(userid, amount * multiplier)
        if username not in winners:
          winners += username + " "

  return winners


async def rouletteGame(cdtime):

  global cancelRoulette
  cancelRoulette = False

  while not cancelRoulette:

    print(cdtime)
    await asyncio.sleep(cdtime)

    channel = bot.get_channel(#actuallyId)
    rouletteNumbers = []

    for x in range(1, 11):
      rouletteNumbers.append(x)

    redNumbers = []
    blackNumbers = []

    counter = 0
    for number in rouletteNumbers:
      if counter == 1:
        blackNumbers.append(number)
        counter = 0
      else:
        redNumbers.append(number)
        counter += 1

    rouletteNumbers.append(0)

    num = choice(rouletteNumbers)


    print(redNumbers, blackNumbers)

    extraWinners = getRouletteWinners(num, 4)

    if num in redNumbers:
      color = "🔴"
      winners = getRouletteWinners("red", 2)

    elif num in blackNumbers:
      color = "⚫"
      winners = getRouletteWinners("black", 2)

    else:
      color = "🟢"
      winners = getRouletteWinners("green", 4)

    global cooldownTime

    embed = discord.Embed(title="🎲 Roulette 🎲", colour=discord.Colour.red())
    embed.add_field(name="🎯 Result 🎯", value=f"{color}  {num}", inline=True)
    embed.set_footer(text=f"Next results in {cooldownTime}")
    if len(winners) > 2 or len(extraWinners) > 2:
      embed.add_field(name="💸 Winners 💸",
                      value=f"{winners + extraWinners}",
                      inline=False)
    global rouletteParticipants
    rouletteParticipants.clear()
    await channel.send(embed=embed)


@tasks.loop(minutes=3.0)
async def syncProfiles():
  syncCrystals()

@tasks.loop(minutes=30.0)
async def syncNicknames():
  print("Starting task...")
  with open("userdata.json", "r") as fa:
    data = json.load(fa)

  inactiveAccs = 0
  for profile in data:
    discordID = profile["userid"]
    try:
      user = bot.get_user(int(discordID))
      if user.name != profile["discordname"]:
        print(f'Updated Username: {profile["discordname"]} -> {user.name}')
        profile["discordname"] = user.name
    except:
      inactiveAccs += 1
      continue
  
  print(inactiveAccs)
  with open("userdata.json", "w") as fs:
    json.dump(data, fs, indent=5)




@bot.event
async def on_ready():


  print("Bot launched")

  #noricommunity = bot.get_guild(919963255005401118)

  #print(noricommunity.premium_subscribers)

  syncProfiles.start()
  #syncNicknames.start()

  await bot.load_extension("cogs.profile")
  await bot.load_extension("cogs.id")
  await bot.load_extension("cogs.inventory")
  await bot.load_extension("cogs.match")
  await bot.load_extension("cogs.code")
  await bot.load_extension("cogs.slots")
  await bot.load_extension("cogs.redeem")
  await bot.load_extension("cogs.results")
  await bot.load_extension("cogs.coinflip")
  await bot.load_extension("cogs.maps")
  await bot.load_extension("cogs.send")
  await bot.load_extension("cogs.dice")
  await bot.load_extension("cogs.banker")
  await bot.load_extension("cogs.rps")
  await bot.load_extension("cogs.philJack")
  await bot.load_extension("cogs.hangman")
  await bot.load_extension("cogs.banners")
  await bot.load_extension("cogs.party")
  await bot.load_extension("cogs.memory")
  await bot.load_extension("cogs.connectfour")
  await bot.load_extension("cogs.scratches")

  print("Cogs loaded")
  try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} slash commands")
  except Exception as e:
    print(e)
  



@bot.event
async def on_command_error(ctx, error):

  if isinstance(error, commands.CommandNotFound):

    button = discord.ui.Button(style=discord.ButtonStyle.green, label="Click for help")

    async def button_callback(interaction: discord.Interaction):
      channel = await interaction.user.create_dm()
      await helpMessage(channel, interaction.user)
      await interaction.response.defer()

    view = discord.ui.View()
    button.callback = button_callback
    view.add_item(button)

    await ctx.send("Invalid command. Did you spell it correctly?", view=view)

  if isinstance(error, commands.CommandOnCooldown):
    print(error.retry_after / 60 / 60)
    await ctx.send(
      f'Youre currently on cooldown. Come back in **{round(error.retry_after / 60)}**min'
    )
  if isinstance(error, commands.CheckFailure):
    await ctx.send("You dont match the conditions to use this command.")
  raise error


@bot.command()
async def add(ctx):

  print("command used")
  canUseCommand = checkRole(ctx.author, "Clown")

  if not canUseCommand:
    await ctx.reply("You can't use this command.")
    return

  try:
    amount = ctx.message.content.split(' ')[-1]
    users = ctx.message.content.split(' ')[2:-1]
    print(amount, users)
  except:
    await ctx.reply("Missing parameter")
    return

  for user in users:
    user = pingToID(user)
    user = bot.get_user(user)
    if getUserValues(user.id) is None:
      await ctx.send(f"{user.mention} doesn't have a profile.")
    else:
      addCrystals(user.id, int(amount))
      await ctx.send(f"Added **{amount}** crystals to {user.mention}")


@bot.command()
async def subtract(ctx):

  print("command used")
  canUseCommand = checkRole(ctx.author, "Clown")

  if not canUseCommand:
    await ctx.reply("You can't use this command.")
    return

  try:
    amount = ctx.message.content.split(' ')[-1]
    users = ctx.message.content.split(' ')[2:-1]
  except:
    await ctx.reply("Missing parameter")
    return

  for user in users:
    user = pingToID(user)
    user = bot.get_user(user)
    if getUserValues(user.id) is None:
      await ctx.send(f"{user.mention} doesn't have a profile.")
    else:
      subtractCrystals(user.id, int(amount))
      await ctx.send(f"Subtracted **{amount}** crystals from {user.mention}")

@bot.command()
async def remove(ctx, *, amount):


  try:
    amount = int(amount)
  except:
    await ctx.reply("Something went wrong.")
    return


  if amount < 0:
    await ctx.reply("Nice try you muffin.")
    return
  
  if amount % 200 != 0:
    await ctx.reply("Your number has to be dividable by 200")
    return

  subtractCrystals(ctx.author.id, int(amount))
  await ctx.reply(f"Sucessfully removed **{amount}** crystals from your account")



@bot.command()
async def set(ctx):

  print("command used")
  canUseCommand = checkRole(ctx.author, "Clown")

  if not canUseCommand:
    await ctx.reply("You can't use this command.")
    return

  try:
    amount = ctx.message.content.split(' ')[-1]
    users = ctx.message.content.split(' ')[2:-1]
  except:
    await ctx.reply("Missing parameter")
    return

  for user in users:
    user = pingToID(user)
    user = bot.get_user(user)
    if getUserValues(user.id) is None:
      await ctx.send(f"{user.mention} doesn't have a profile.")
    else:
      setCrystals(user.id, int(amount))
      await ctx.send(f"{user.mention}'s crystal amount was set to {amount}")


@bot.command()
async def roulette(ctx):

  global canPlaceBet
  if not canPlaceBet:
    await ctx.reply("Roulette is currently not active. Try again later.")
    return

  try:
    color = ctx.message.content.split(' ')[2]
    amount = int(ctx.message.content.split(' ')[3])
    print(color, amount)

  except:
    await ctx.reply("Something went wrong. Try again")
    return

  if str(color.lower()) not in ["green", "red", "black"]:
    try:
      color = int(color)

      if color > 10 or color < 0: 
        await ctx.reply("Invalid number.")
        return

    except:
      await ctx.reply("Invalid color")
      return

  authorid = ctx.author.id
  philerprofile = getUserValues(authorid)

  if philerprofile is None:
    await ctx.reply("You don't have a profile.")
    return

  rouletteTickes = readInventoryItem(ctx.author.id, "rouletteGames")
  crystals = philerprofile["crystals"]
  print(crystals)

  if crystals >= 5000:
    await ctx.reply(
      "You have reached the limit of 5k crystals. Leave some for the rest greedy muffin."
    )
    return

  if amount != 400 and rouletteTickes > 0 or rouletteTickes <= 0:

    if amount < 400:
      await ctx.reply("You need to bet atleast 400 crystals.")
      return

    if amount % 200 != 0:
      await ctx.reply("Your bet has to be dividable by 200.")
      return

    if crystals < amount:
      await ctx.reply("You dont have enough crystals.")
      return

    if crystals + amount > 5000:
      await ctx.reply(
        f"You can't bet more than **{5000 - crystals}** crystals because you would surpass the limit of 5k."
      )
      return

    subtractCrystals(authorid, amount)
    addGambleSpendings(authorid, amount)

  elif amount == 400 and rouletteTickes > 0:
    removeInventoryItem(ctx.author.id, "rouletteGames", 1)

  else:
    await ctx.reply("You don't have enough crystals")
    print("else condition")
    return

  authorName = ctx.author.name

  try:
    color = color.lower()
  except:
    pass


  profile = {
    "username": authorName,
    "userid": authorid,
    "color": color,
    "amount": int(amount)
  }

  print(profile)

  global rouletteParticipants
  rouletteParticipants.append(profile)

  await ctx.reply("Sucessfully joined a game of roulette.")


@bot.command()
async def startroulette(ctx, *, cd):
  print("command used")
  canUseCommand = checkRole(ctx.author, "Clown")

  if not canUseCommand:
    await ctx.reply("You can't use this command.")
    return

  global rouletteActive
  if rouletteActive:
    await ctx.reply("Roulette is already running.")
    return

  global canPlaceBet
  canPlaceBet = True

  global cooldownTime
  cooldownTime = cd

  global cancelRoulette
  cancelRoulette = False

  parameter = cooldownTime[-1]
  cdtime = int(cooldownTime[:-1])
  print(cdtime, parameter)

  if parameter.lower() == "m":

    cdtime *= 60

  elif parameter.lower() == "h":
    cdtime *= 3600

    print("hours")

  rouletteActive = True
  await ctx.reply(
    f"Sucessfully started roulette. Results will be shown every **{cooldownTime[:-1]}{parameter}**."
  )
  bot.loop.create_task(rouletteGame(cdtime))


@bot.command()
async def stoproulette(ctx):

  global canPlaceBet
  canPlaceBet = False

  print("command used")
  canUseCommand = checkRole(ctx.author, "Clown")

  if not canUseCommand:
    await ctx.reply("You can't use this command.")
    return

  global cancelRoulette
  cancelRoulette = True

  global rouletteActive
  rouletteActive = False

  await ctx.reply("Successfully stopped roulette.")


async def dailyXDDDrofl(ctx):

  if not getUserValues(ctx.author.id):
    await ctx.reply("You dont have a profile.")
    return


  age = checkAccountAge(ctx)

  if age < 14:
    await ctx.reply("stop creating new accounts silly muffin")
    return

  probability = random()

  print(probability)
  if probability > 0.85:  # 1 - 0.9 10%
    print("test")
    payload = addRandomBanner(ctx.author.id)
    if payload == False:
      print("rolling new gift")
      await dailyXDDDrofl(ctx)
      return

    print(payload)
    await ctx.reply(f"You received a new banner: **{payload[0].upper() + payload[1:]}**\n Use `!phil banner {payload}` to equip it.")
    return

  elif probability > 0.75:  # 0.8 - 0.9%
    amount = randint(1, 5)
    addInventoryItem(ctx.author.id, "freespins", amount)
    await ctx.reply(f"🎰 You received **{amount}** free slot spins! 🎰")
    return

  elif probability > 0.6:  #
    amount = randint(1, 2)
    addInventoryItem(ctx.author.id, "rouletteGames", amount)
    await ctx.reply(
      f"🧧 You received **{amount}** free roulette games (Bet = *400* crystals)! 🧧"
    )
    return

  elif probability > 0.5:  # 20%
    crystalChoice = choice((200, 400))
    addCrystals(ctx.author.id, crystalChoice)
    await ctx.reply(f"💎 You received **{crystalChoice}** crystals! 💎")
    return
  else:
    await ctx.reply("Unfortunately nothing was inside this lootbox.")
    return


@bot.command()
async def lootbox(ctx):

  lootboxes = readInventoryItem(ctx.author.id, "lootboxes")

  if lootboxes <= 0:
    await ctx.reply("You dont have any lootboxes to unbox.")
    return

  removeInventoryItem(ctx.author.id, "lootboxes", 1)
  await dailyXDDDrofl(ctx)


@bot.tree.command(name="captain",
                  description="Picks a random user in your voice chat.")
async def captain(interaction: discord.Interaction):

  if interaction.user.voice is None:
    await interaction.response.send_message("You are not in a voice chat.")
    return
  vc = interaction.user.voice.channel

  role = discord.utils.get(interaction.user.guild.roles, name="Captain")

  captains = []
  for user in vc.members:
    print(user.roles)
    if role in user.roles:
      global PreviousCaptain
      if user.name != PreviousCaptain:
        captains.append(user.name)

  if len(captains) == 0:
    await interaction.response.send_message("Nobody wants to be a captain.")
    return

  captain = choice(captains)
  PreviousCaptain = captain

  await interaction.response.send_message(
    f"**{captain}** is going to be captain.")


@bot.event  # anti dm
async def on_message(message):
  
  matchChannel = bot.get_channel(#actualId)

  if message.author == bot.user:  # Don't reply to itself. Could again be client for you
    return

  if message.type == discord.MessageType.premium_guild_subscription or message.content.startswith("Test boost message"):
    print(f"Sent Premium message to {message.author.name}")
    viewUI = discord.ui.View()
    channelButton = discord.ui.Button(style=discord.ButtonStyle.green, url="#channelId", label="Go to exclusive channel")
    informationButton = discord.ui.Button(style=discord.ButtonStyle.primary, url="ChannelID", label="More Information")
    viewUI.add_item(channelButton)
    viewUI.add_item(informationButton)

    msg = ('--------------------------------------------------------------\n\n'
    '❤️ **THANK YOU FOR BOOSTING NORIC PUGS** ❤️ \n'
    '\nWe highly appreciate your contribution to the Pugs server and grant you following benefits:\n'
    '\n> 👑 Access to an **exclusive** channel where for instance, the team will occasionally drop codes'
    '\n> 💼 Increased **Lootbox** drop chance'
    '\n> 🌇 Custom **Philer Profile** banner'
    '\n> 👮‍♂️ Raised "payout excluded" period by one week (**14** ➡️ **21** days)\n'
    f'\nWe are looking forward to see you in pugs!{message.author.mention}')

    await message.author.send(msg, view=viewUI)


  #if not checkRole(message.author, "Clown"):
    #await message.channel.send("Philer is currently doing updates. Please try again later.")
    #return

  if message.channel != matchChannel:
    if message.content.lower().startswith('!phil match'):
      await message.channel.send("Don't use that channel for this command.")
      return

  if message.channel == matchChannel:
    if not message.content.lower().startswith('!phil match'):
      return


  if isinstance(
      message.channel, discord.DMChannel
  ):  #If you want this to work in a group channel, you could also check for discord.GroupChannel
    await message.channel.send("No dm's supported anymore")
    return
  await bot.process_commands(message)



@bot.command()
async def shutdown(ctx):



  if not checkRole(ctx.author, "Clown"):
    await ctx.reply("You can't use that command.")
    return


  channel = bot.get_channel(#channelID)
  await channel.send(file=discord.File(r"userdata.json"))
  await channel.send(file=discord.File(r"redeems.json"))

  await ctx.reply("Good night")
  await bot.close()


@bot.command()
async def guessgame(ctx):

    userprofile = getUserValues(ctx.author.id)
    inv = userprofile["inventory"]
    if not checkRole(ctx.author, "Clown") and inv["guessGames"] <= 0:
        await ctx.reply("You can't use that command.")
        return
    
    if checkRole(ctx.author, "Clown"):
      try:
          customRange2 = int(ctx.message.content.split(' ') [3])
          amount = int(ctx.message.content.split(' ') [2])
      except:
          await ctx.reply("Something went wrong. Try again")
          return
      

    if not checkRole(ctx.author, "Clown"):
      await ctx.reply("Ticket used.\nPrice **400** crystals\nRange 1- 100")
      removeInventoryItem(ctx.author.id, "guessGames", 1)
      customRange2 = 100
      amount = 400

    customRange = randint(1, customRange2)

    botpermission = {
      bot.user: discord.PermissionOverwrite(send_messages=True)
    }


    guild = ctx.message.guild
    category = discord.utils.get(ctx.guild.categories, name="GAME MODES")
    channel = await guild.create_text_channel("╠-guess-the-number", slowmode_delay=10, category=category, overwrites=botpermission)



    await ctx.reply(f"Created new channel. {channel.mention}")
  
    def check(m):
      return m.channel.id == channel.id

    gameActive = True


    print("The number is:", customRange)
    lastLetter = str(customRange) [-1]
    print(lastLetter)
    await channel.send(f"Write your guess in this chat. Range is 1 - {customRange2}")


    afterXmessages = randint(30, 75)
    print("Hint will be given after", afterXmessages, "messages")
    hintCounter = 0
    while gameActive:


      response = await bot.wait_for('message', check=check)

      if hintCounter == afterXmessages:
        await channel.send(f"**Hint**: Last letter is **{lastLetter}**")

      try:
        int(response.content)
        hintCounter += 1
      
      except:
        response.content = -1

      if int(response.content) == customRange:
        await channel.send(f"{response.author.mention} guessed the correct number and won **{amount}** crystals!")
        addCrystals(response.author.id, int(amount))
        gameActive = False

      print("Hint counter:", hintCounter)

    overwrites = {
      guild.default_role: discord.PermissionOverwrite(send_messages=False),
      bot.user: discord.PermissionOverwrite(manage_channels=True)
    }


    await channel.send("Game closed. Channel will be deleted in 1min.")
    await channel.edit(overwrites=overwrites)

    await asyncio.sleep(60)
    await channel.delete()


#keep_alive()
bot.run('SecretKEyTO access the bot')
