asyncakinator
=============


.. image:: https://discord.com/api/guilds/751490725555994716/embed.png
   :target: https://discord.gg/muTVFgDvKf
   :alt: Support Server Invite

An async API wrapper for the online game, Akinator, written in Python.

`Akinator <https://en.akinator.com/>`_ is a web-based game which tries to determine what character you are thinking of by asking a series of questions.


Installing
----------

To install, just run the following command:

.. code-block:: shell

    # MacOS/Linux
    python3 -m pip install -U asyncakinator

    # Windows
    py -3 -m pip install -U asyncakinator


Requirements
~~~~~~~~~~~~
- Python ≥3.9

- ``aiohttp``


Documentation
-------------
Documention can be found `here. <https://asyncakinator.readthedocs.io/en/latest/>`_


Quick Examples
--------------

Here's a quick little example of the library being used to make a simple, text-based Akinator game:

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