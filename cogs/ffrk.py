import asyncio
import discord
import random
from .utils.dataIO import fileIO, dataIO
from discord.ext import commands

def weighted_choice(choices):
   total = sum(w for c, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w >= r:
         return c
      upto += w
   assert False, "Shouldn't get here"

class FFRK:
    """FFRK tools."""

    def __init__(self, bot):
        self.bot = bot
        self._process_characters()
        self._setup_gacha()
    
    def _process_characters(self):
        raw = dataIO.load_json("data/ffrk/characters.json")
        self._realm_char_map = raw
        self._realm_char_map["All"] = set()
        for realm in raw:
            self._realm_char_map["All"].update(raw[realm])

    def _setup_gacha(self):
        raw = dataIO.load_json("data/ffrk/gacha.json")
        self._gacha_rates = []
        self._gacha_rates_g5 = []
        for category in raw:
            rate_tup = (category, int(raw[category]))
            self._gacha_rates.append(rate_tup)
            if category in ["6", "5sb", "5off"]:
                self._gacha_rates_g5.append(rate_tup)
        self._gacha_aliases = {
            1 : ["1", "solo", "yolo", "5"],
            3 : ["3", "cot", "CoT", "c03", "Co3", "15"],
            11 : ["11", "g5", "G5", "🐳", "50"]
        }
        self._gacha_type_map = {
            "3" : "<:3star:230141147304034305>",
            "4" : "<:4star:230141169231724544>",
            "5off" : "<:5star:230141201393778698>",
            "5sb" : "<:relic:230141222948175872>",
            "6" : "<:6star:230142234123567114>"
        }
        
    def _rand_char(self, n):
        return random.sample(self._realm_char_map["All"], n)
        
    def _gacha(self, size, lucksack=False):
        if lucksack:
            rates = []
            for rate_tup in self._gacha_rates:
                if category in ["6", "5sb", "5off"]:
                    rates.append((rate_tup[0], rate_tup[1]*2))
                else:
                    rates.append(rate_tup)
        else:
            if random.range(10000) == 0:
                return ["Nope, only <:salt:230150323069517824> here for you, kupo!"]
            rates = self._gacha_rates
        result = []
        if size == 11:
            size -= 1
            g5 = weighted_choice(self._gacha_rates_g5)
            result.append(self._gacha_type_map[g5])
        for i in range(size):
            category = weighted_choice(rates)
            result.append(self._gacha_type_map[category])
        return result
        
    @commands.command(pass_context=True)
    async def who(self, ctx, *, question : str):
        """
        
        """
        if not question.endswith('?') or question == '?':
            await self.bot.say("That doesn't look like a question.")
            return
        question = "{}, {} " + question[0].lower() + question[1:-1] + '.'
        author = ctx.message.author
        choice = self._rand_char(1)
        await self.bot.say(question.format(author.mention, choice[0]))
        
    @commands.command(pass_context=True)
    async def party(self, ctx, size : int):
        """
        
        """
        if size < 1:
            await self.bot.say("Need at least one character in your party.")
            return
        elif size > 5:
            await self.bot.say("Can't have more than five characters in your party.")
            return
        author = ctx.message.author
        choices = self._rand_char(size)
        await self.bot.say("{} {}".format(author.mention, ", ".join(choices)))
    
    @commands.command(pass_context=True, aliases=["draw"])
    async def pull(self, ctx, choice : str):
        """
        
        """
        if choice in self._gacha_aliases[1]:
            size = 1
        elif choice in self._gacha_aliases[3]:
            size = 3
        elif choice in self._gacha_aliases[11]:
            size = 11
        else:
            await self.bot.say("Please choose a valid pull type: 1, 3, or 11.")
            return
        author = ctx.message.author
        # Yanhack
        lucksack = author.id == 168478810373619712
        result = self._gacha(size, lucksack)
        await self.bot.say("{} {}".format(author.mention, " ".join(result)))
        

def setup(bot):
    n = FFRK(bot)
    bot.add_cog(n)
