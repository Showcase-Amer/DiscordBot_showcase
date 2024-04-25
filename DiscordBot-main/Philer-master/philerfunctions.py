import json
import time
from discord.ext import commands
from random import randrange, choice
import discord
import string
import datetime
import asyncio
import bs4
import requests
from abc import ABC, abstractmethod

def addProfileValue(user, value, amount):
    with open("userdata.json", "r") as f:
        data = json.load(f)
    
    for profile in data:
        if profile["userid"] == user:
            profile[value] += amount
            break
    
    with open("userdata.json", "w") as fa:
        json.dump(data, fa, indent=5)



#Normally this code has thousands of line, for simplicity, only one function is shown
