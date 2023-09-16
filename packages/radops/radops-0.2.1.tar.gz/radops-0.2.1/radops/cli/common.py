import rich
import typer


def _y_n_prompt_loop(prompt: str) -> None:
    while True:
        y_or_n = typer.prompt(prompt + " [y/n]").lower()
        if y_or_n == "y":
            return
        if y_or_n == "n":
            rich.print("Exiting")
            raise typer.Exit()
        else:
            rich.print("[red]Please respond with 'y' or 'n'")
