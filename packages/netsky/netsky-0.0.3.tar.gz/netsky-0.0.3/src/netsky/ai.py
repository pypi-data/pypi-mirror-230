def ai_run(state={}, interactive=False):
    from rich.console import Console

    console = Console()
    console.print(f"netsky.ai: ", style="bold violet blink")

    from netsky.bots.netsky import bot

    console.print(f"access to: {bot.name}")

    if interactive:
        import ibis
        import IPython

        from rich import print

        ibis.options.interactive = True

        IPython.embed(colors="neutral")
