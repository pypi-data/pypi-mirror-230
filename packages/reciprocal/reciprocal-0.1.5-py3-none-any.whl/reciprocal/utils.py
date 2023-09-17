import click

ARROW_UP = "\x1b[A"
ARROW_DOWN = "\x1b[B"


def hide_cursor() -> None:
    click.echo('\033[?25l', nl=False)


def show_cursor() -> None:
    click.echo('\033[?25h', nl=False)


def clear_after_cursor() -> None:
    click.echo("\033[J", nl=False)


def move_cursor_to_start_line() -> None:
    click.echo("\r", nl=False)


def clear_line_after_cursor() -> None:
    click.echo("\033[K", nl=False)


def cursor_up(n: int = 1) -> None:
    click.echo(f"\033[{n}F")
