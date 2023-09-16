from time import sleep
from sys import stdout
from rich import print


def progress_bar(current: int, total: int, bar_length: int = 20):
    """Displays a progress bar in the terminal

    Args:
        current (int): current advancment of the progress bar
        total (int): maximum value of the progress bar
        bar_length (int, optional): Length of the progress bar (in chars). Defaults to 20.
    """
    stdout.flush()
    fraction: float = current / total
    arrow: str = int(fraction * bar_length - 1) * '-' + '>'
    padding: str = int(bar_length - len(arrow)) * ' '
    ending: str = '\n' if current == total else '\r'
    print(
        f'[blue1]{int(fraction*100)}%\t[dark_orange][{arrow}{padding}]', end=ending)
