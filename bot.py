import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

from dotenv import load_dotenv
import os
import random
from Utils.db import check_registered_user, get_user_data
from TextProcessing.app import wikipedia_search, Responder

registered_users = set()
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
PREFIX = "-"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

quiz_data = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Rome", "Berlin"],
        "answer": 0
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "answer": 1
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["Leonardo da Vinci", "Pablo Picasso", "Vincent van Gogh", "Salvador Dali"],
        "answer": 0
    }
]

responder = Responder()

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        user_id = str(message.author.id)
        registered = check_registered_user(registered_users, user_id)

        if registered:
             # Check if the message is a command
            ctx = await bot.get_context(message)
            if ctx.valid:
                await bot.process_commands(message)
            else:
                # Provide default response when no commands are detected
                response = responder.respond(prompt=message.content.strip(), uid=str(user_id))
                await message.channel.send(response)
        else:
            await message.channel.send(f"You have to register before using commands. Visit `https://intelli-learn.vercel.app` and sign up for an account. Your discord id is `{user_id}`. Provide this id in the form. Good luck 😀")

@bot.command()
async def info(ctx):
    embed = discord.Embed(
        title="Intelli Tutor",
        description="Your personalized tutor",
        color=discord.Color.green()
    )
    embed.add_field(name="Introduction", value="IntelliTutor is a friendly and intelligent Discord bot designed to enhance your learning experience. With its advanced AI capabilities, IntelliTutor provides personalized tutoring and guidance in various subjects.")
    await ctx.send(embed=embed)

@bot.command()
async def profile(ctx):
    # Get the user ID
    user_id = str(ctx.author.id)

    # Call get_user_data() function to retrieve user data
    user_data = get_user_data(user_id)

    # Create an embed to display the user's profile
    embed = discord.Embed(title=ctx.author.display_name, color=discord.Color.blue())

    # Add user's profile picture
    user_avatar_url = ctx.author.avatar
    embed.set_thumbnail(url=user_avatar_url)

    embed.add_field(name="Name", value=user_data["name"])
    embed.add_field(name="Email", value=user_data["email"])

    # Send the embed as a response
    await ctx.send(embed=embed)

@bot.command()
async def quiz(ctx):
    question = random.choice(quiz_data)

    class QuizView(View):
        def __init__(self):
            super().__init__()
            self.value = None

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            return interaction.user == ctx.author

        async def on_timeout(self):
            await ctx.send(f"{ctx.author.mention} Time's up! You took too long to answer.")

        @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
        async def option1(self, button: discord.ui.Button, interaction: discord.Interaction):
            self.value = 0
            self.stop()

        @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
        async def option2(self, button: discord.ui.Button, interaction: discord.Interaction):
            self.value = 1
            self.stop()

        @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
        async def option3(self, button: discord.ui.Button, interaction: discord.Interaction):
            self.value = 2
            self.stop()

        @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
        async def option4(self, button: discord.ui.Button, interaction: discord.Interaction):
            self.value = 3
            self.stop()

    view = QuizView()
    await ctx.send(embed=discord.Embed(title="Quiz", description=question["question"], color=discord.Color.blue()).add_field(name="Options", value="\n".join(f"{chr(65 + i)}. {option}" for i, option in enumerate(question["options"]))), view=view)

    try:
        await view.wait()
        chosen_option = view.value

        if chosen_option == question["answer"]:
            await ctx.send(f"{ctx.author.mention} Correct answer! Well done!")
        else:
            await ctx.send(f"{ctx.author.mention} Oops! That's incorrect. The correct answer was {question['options'][question['answer']]}.")

    except asyncio.TimeoutError:
        await view.on_timeout()

    # Cleanup view to avoid potential memory leaks
    view.stop()

@bot.command()
async def wiki(ctx, *, topic):
    res = wikipedia_search(topic=topic)
    await ctx.send(res)

bot.run(TOKEN)