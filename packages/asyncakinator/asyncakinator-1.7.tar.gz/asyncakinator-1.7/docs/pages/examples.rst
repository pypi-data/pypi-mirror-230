.. py:currentmodule:: asyncakinator



Quick Examples
==============

Here are some examples to get started.


Basic Example
-------------

.. code-block:: python

    import asyncio

    from asyncakinator import (
        Akinator,
        Answer,
        CanNotGoBack,
        InvalidAnswer,
        Language,
        NoMoreQuestions,
        Theme
    )


    game = Akinator(
        language=Language.ENGLISH,
        theme=Theme.ANIMALS,
    )


    async def main():
        question = await game.start()

        while game.progression <= 80:
            print(question)
            user_input = input("Answer:  ")
            try:
                answer = Answer.from_str(user_input)
            except InvalidAnswer:
                print("Invalid answer")
                continue
            try:
                question = await game.answer(answer)
            except CanNotGoBack:
                print("This is the first question, you can't go back.")
                continue
            except NoMoreQuestions:
                break

        await game.win()

        correct = input(
            f"You are thinking of {game.first_guess.name} ({game.first_guess.description}). "
            f"Am I correct?\n{game.first_guess.absolute_picture_path}\n---\nAnswer:  "
        )
        if Answer.from_str(correct) == Answer.YES:
            print("Nice.")
        else:
            print("Maybe next time.")
        await game.close()


    asyncio.run(main())


Discord Bot Example
-------------------

.. code-block:: python

    # This example requires the discord.py 2.0 library.

    import discord
    import asyncio
    from discord.ext import commands

    from asyncakinator import (
        Akinator,
        Answer,
        CanNotGoBack,
        InvalidAnswer,
        Language,
        InvalidLanguage,
        InvalidTheme,
        NoMoreQuestions,
        Theme,
    )


    intents = discord.Intents.default()
    intents.messages = True

    bot = commands.Bot(command_prefix="!", intents=intents)


    @bot.command()
    async def akinator(
        ctx: commands.Context[commands.Bot],
        language: str,
        theme: str,
    ):
        try:
            game_language = Language.from_str(language)
            game_theme = Theme.from_str(theme)
        except (InvalidLanguage, InvalidTheme):
            return await ctx.send("Invalid Arguments")

        game = Akinator(language=game_language, theme=game_theme, child_mode=True)

        question = await game.start()

        while game.progression <= 85:
            await ctx.send(question)
            try:
                msg = await bot.wait_for(
                    "message", timeout=60, check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                await ctx.send("Timeout, Game ended")
                break
            else:
                try:
                    answer = Answer.from_str(msg.content)
                except InvalidAnswer:
                    await ctx.send("Invalid answer")
                    continue
                try:
                    question = await game.answer(answer)
                except CanNotGoBack:
                    await ctx.send("This is the first question, you can't go back.")
                    continue
                except NoMoreQuestions:
                    break
        if game.progression > 85:
            await game.win()
            await ctx.send(
                f"You are thinking of {game.first_guess.name} ({game.first_guess.description})\n{game.first_guess.absolute_picture_path}."
            )