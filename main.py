import nextcord
from nextcord.ext import commands
import sys
import traceback
import os
import config
import importlib.util

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}, created by koz')
    activity = nextcord.Game(name=config.BOT_STATUS)
    await bot.change_presence(activity=activity)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f'Missing required argument: {error.param.name}')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have permission to use this command.")
    else:
        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def has_setup_function(module_name):
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        return False
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return hasattr(module, 'setup')

for entry in os.listdir("cogs"):
    if entry.endswith('.py'):
        module_name = f"cogs.{entry[:-3]}"
        if has_setup_function(module_name):
            bot.load_extension(module_name)
    elif os.path.isdir(f"cogs/{entry}"):
        for filename in os.listdir(f"cogs/{entry}"):
            if filename.endswith('.py'):
                module_name = f"cogs.{entry}.{filename[:-3]}"
                if has_setup_function(module_name):
                    bot.load_extension(module_name)

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)