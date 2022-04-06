import discord
import os

from discord_slash import SlashCommandOptionType, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from dotenv import load_dotenv
import random
import vrcpy
import json

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD = int(os.getenv("DISCORD_GUILD"))
VRC_USERNAME = os.getenv("VRC_USERNAME")
VRC_PASSWORD = os.getenv("VRC_PASSWORD")
QUESTION_KEYWORD = "question"
LINK_KEYWORD="link"
PROFILE_KEYWORD="profile"

vrc_client = vrcpy.Client()
client = discord.Client(intents=discord.Intents.all())
slash = SlashCommandOptionType(client, sync_commands=True)


@client.event
async def on_ready():
    global guild
    guild = client.get_guild(GUILD)
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )
    await client.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game('VRChatting'))
    await vrc_client.login(VRC_USERNAME, VRC_PASSWORD, None, True)

@client.event
async def on_message(message):
    if message.author == client.user or message.guild is None or message.guild.id != GUILD:
        return
    is_badword = await on_badwords(message)
    if is_badword:
        return
    if message.content.startswith("echo"):
        await on_echo(message)
    await on_kawaii(message)
    if message.content.startswith("!q"):
        await on_questions(message)
    elif message.content.startswith("!link"):
        await on_link(message)
    elif message.content.startswith("!profile"):
        await on_profile(message)

  @slash.slash(name=LINK_KEYWORD,
             description="Link your VRChat account with the bot",
             guild_ids=[GUILD],
             options=[create_option(
                 name="vrchat_id",
                 description="assigning your vrchat id with your discord profile",
                 option_type=SlashCommandOptionType.STRING,
                 required=True
             )]
             )
async def on_link(ctx, vrchat_id):
    try:
        vrchat_user = vrc_client.fetch_user_by_id(vrchat_id)
    except vrcpy.errors.NotFoundError:
        await message.channel.send("The id provided is invalid, please make sure you have spelled your id correctly.")
        return

    discord_id = message.author.id
    dictionary_id = {discord_id:vrchat_id}

    with open("info.json","r+") as file:
        json_dict = json.load(file)
        json_dict.update(dictionary_id)
        file.seek(0)
        json.dump(json_dict, file)

    await ctx.send(f"{ctx.author.mention} is succesfully linked to **{vrchat_user.displayName}**")

    @slash.slash(name=PROFILE_KEYWORD,
                 description="View your VRChat profile!",
                 guild_ids=[GUILD],
                 options=[create_option(
                     name="user",
                     description="the person who's profile you want to see",
                     option_type=SlashCommandOptionType.USER,
                     required=False
                 )]
                 )

    @client.event
    async def on_profile(message):
        with open("info.json") as file:
            dict_user = json.load(file)
            vrchat_id = dict_user.get(str(message.author.id), "Notfound")

        if vrchat_id == "Notfound":
            await ctx.send("Please link your id using the '!link' command")
            return

        vrchat_user = vrc_client.fetch_user(vrchat_id)

        vrc_mbed = discord.Embed(
            colour=(discord.Colour.magenta()),
            title=vrchat_user.displayName,
            description=vrchat_user.bio,
            url=f"https://vrchat.com/home/user/{vrchat_id}")

        vrc_mbed.set_thumbnail(url=vrchat_user.currentAvatarImageUrl)

        vrc_mbed.add_field(name="Description", value=str(vrchat_user.statusDescription), inline=False)

        vrc_mbed.add_field(name="Status", value=str(vrchat_user.status), inline=False)

        vrc_mbed.add_field(name="Platform", value=str(vrchat_user.last_platform), inline=False)

        vrc_mbed.add_field(name="Trust level", value=str(vrchat_user.tags), inline=False)

        vrc_mbed.add_field(name="Bio", value=str(vrchat_user.bio), inline=False)

        await ctx.send(embed=vrc_mbed)

       client.run(TOKEN)
