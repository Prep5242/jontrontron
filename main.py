import string
import sys
import discord
import json
import traceback
import asyncio
import re
import requests
from random import choice

# What we use for what:
# sys is used for tracebaks in on_error.
# discord is obvious.
# json is used to load the config file.
# traceback is also used to print tracebacks. I'm a lazy ass.
# asyncio is because we're using the async branch of discord.py.
# https://github.com/Rapptz/discord.py/tree/async
# random.choice for choosing game ids

# A sample configs/config.json should be supplied.
with open('configs/config.json') as data:
    config = json.load(data)

with open('configs/responses.json') as data:
    shitposts = json.load(data)

with open('configs/games.json') as data:
    game_names = json.load(data)

games_list = []
for gname in game_names:
    games_list.append(discord.Game(name=gname))

colors = [
    discord.Color.teal(),
    discord.Color.dark_teal(),
    discord.Color.green(),
    discord.Color.dark_green(),
    discord.Color.blue(),
    discord.Color.dark_blue(),
    discord.Color.purple(),
    discord.Color.dark_purple(),
    discord.Color.magenta(),
    discord.Color.dark_magenta(),
    discord.Color.gold(),
    discord.Color.dark_gold(),
    discord.Color.orange(),
    discord.Color.dark_orange(),
    discord.Color.red(),
    discord.Color.dark_red()
]

def aan(string):
    '''Returns "a" or "an" depending on a string's first letter.'''
    if string[0].lower() in 'aeiou':
        return 'an'
    else:
        return 'a'

# log in
client = discord.Client(max_messages=5000)

# random game status
@asyncio.coroutine
def random_game():
    while True:
        yield from client.change_presence(game=choice(games_list), afk=False)
        yield from asyncio.sleep(600)

@client.async_event
def on_ready():
    yield from client.edit_profile(config['token'],username='JonTronTron')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    yield from random_game()
#    rainbows()


include = set(string.ascii_letters.join(string.digits))
currentAvy = ''

@client.async_event
def on_message(message):
    if message.author.id != client.user.id and '\u200b' not in message.content:
        s = ''.join(ch for ch in message.content if ch in include)
        if re.match(config['quit_command'], s, flags=re.I) and message.author.id in config['owner_id']:
            client.logout()
        if re.match(config['reload_command'], s, flags=re.I) and message.author.id in config['owner_id']:
            global shitposts
            global game_names

            with open('configs/responses.json') as z:
                shitposts = json.load(z)

            with open('configs/games.json') as z:
                game_names = json.load(z)

            if config['reload_response']: # If reload_response is blank, this won't trigger.
                yield from client.send_message(message.channel, config['reload_response'])

        if message.content.startswith('!echval') and message.author.id in config['owner_id']:
            g_1 = message.content.split(None, 1)[1]
            if g_1.startswith('yield from '):
                response = yield from eval(message.content.split(None, 2)[2])
            elif g_1.startswith('exec '):
                exec(message.content.split(None, 2)[2])
                response = False
            else:
                response = eval(message.content.split(None, 1)[1])
            if response:
                yield from client.send_message(
                    message.channel,
                    '```\n{}\n```'.format(response)
                    )

        for key in shitposts.keys():
            if re.match(key, s, flags=re.I):
                yield from client.send_typing(message.channel)
                response = choice(shitposts[key])
                global currentAvy
                if isinstance(response, list):
                    try:
                        if config['change_avy'] == "on":
                            filename = response[1]
                            if filename != currentAvy:
                                with open(filename, 'rb') as img:
                                    print('Changing avy to {}'.format(filename))
                                    yield from client.edit_profile(config['token'],avatar=img.read())
                                    currentAvy = filename
                    except:
                        print("RATE LIMITS EXCEEDED.")
                    print('channel: {}, input :"{}", response: "{}"'.format(message.channel.name,s,str(response[0].encode('utf-8'))))
                    yield from client.send_message(message.channel, response[0])
                else:
                    try:
                        if currentAvy != 'hamtron.png' and config['change_avy'] == "on":
                            with open('hamtron.png', 'rb') as img:
                                print('Changing avy to default')
                                yield from client.edit_profile(config['token'],avatar=img.read())
                            currentAvy = 'hamtron.png'
                    except:
                        print("RATE LIMITS EXCEEDED.")
                    print('channel: {}, input :"{}", response: "{}"'.format(message.channel.name,s,str(response.encode('utf-8'))))
                    response = '\u200b'+response
                    yield from client.send_message(message.channel, response)
                break

hilarious_snark = [
    'Oh, I get it now I need to eat a pizza because I\'m having *a fuckin\' panic attack* ***I gotta stress eat.***',
    'SURPRISE! IT\'S HELL ON EARTH.',
    '***AM I DEAD YET***',
    'I have **several** questions.',
    'I\'M GOIN\'. **I\'M GOIN\'!**',
    'There\'s a lot to see in this life. Not wasting it here.',
    'I have fallen... and I choose NOT to get up!',
    'CONGRATULATIONS!\nYOU HAVE FOUND THE SECRET LEVEL SELECT SCREEN!',
    'This presents a problem.',
    'I AM BROKEN SO VERY VERY BROKEN'
]

@client.async_event
def on_error(event, *args, **kwargs):
    # args[0] is the message that was recieved prior to the error. At least,
    # it should be. We check it first in case the cause of the error wasn't a
    # message.
    print('An error has been caught.')
    print(traceback.format_exc())
    if args and type(args[0]) == discord.Message:
        if args[0].channel.is_private:
            print('This error was caused by a DM with {}.\n'.format(args[0].author))
        else:
            print('This error was caused by a message.\nServer: {}. Channel: #{}.\n'.format(args[0].server.name, args[0].channel.name))

        if sys.exc_info()[0].__name__ == 'ClientOSError' or sys.exc_info()[0].__name__ == 'ClientResponseError' or sys.exc_info()[0].__name__ == 'HTTPException':
            yield from client.send_message(args[0].channel, 'Sorry, I am under heavy load right now! This is probably due to a poor internet connection. Please submit your command again later.')
        elif sys.exc_info()[0].__name__ == 'Forbidden':
            pass
#           yield from client.send_message(args[0].channel, 'You told me to do something that requires permissions I currently do not have. Ask an administrator to give me a proper role or something!')
        else:
            pass
#           yield from client.send_message(args[0].channel, '{}\n{}: You caused {} **{}** with your command.'.format(
#                choice(hilarious_snark),
#                args[0].author.mention,
#                aan(sys.exc_info()[0].__name__),
#                sys.exc_info()[0].__name__)
#            )

# I'm gonna be honest, I have *no clue* how asyncio works. This is all from the
# example in the docs.
def main_task():
    yield from client.login(config['token'])
    yield from client.connect()

loop = asyncio.get_event_loop()
loop.run_until_complete(main_task())
loop.close()

# If you're taking the senic tour of the code, you should check out
# cacobot/__init__.py next.
