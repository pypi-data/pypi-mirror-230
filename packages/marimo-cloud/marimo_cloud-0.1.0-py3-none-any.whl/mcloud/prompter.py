from typing import List, Union, Generic, TypeVar, Callable
from rich.prompt import Confirm, Prompt
from rich.console import Console
import inquirer

console = Console()

T = TypeVar('T')

def select(message: str, items: List[T], to_display: Callable[[T], str] = None) -> T:
    """
    Prompt user to select an item from a list of items.

    Wraps inquirer.prompt() to provide a simple interface for selecting an item
    while preserving the whole item instead of just the item's name.
    """

    def _to_display(item: T) -> str:
        return str(item)

    if not to_display:
        to_display = _to_display

    choices = [to_display(item) if to_display else item for item in items]
    verify_unique = len(choices) == len(set(choices))
    if not verify_unique:
        raise ValueError('Items must be unique')

    answers = inquirer.prompt([
        inquirer.List('item',
            message=message,
            choices=choices,
        ),
    ])

    answer = answers['item']
    item = next((item for item in items if to_display(item) == answer), None)
    return item

def confirm(message: str, default: bool = False) -> bool:
    """
    Prompt user to confirm an action.
    """

    return Confirm.ask(message, default=default)

def text(message: str, default: str = None) -> str:
    """
    Prompt user to enter text.
    """

    return Prompt.ask(message, default=default)

def slug(message: str, default: str = None) -> str:
    """
    Prompt user to enter a slug.
    """

    def _slugify(text: str) -> str:
        return text.lower().replace(" ", "-").replace("_", "-")

    answer = Prompt.ask(message, default=_slugify(default) if default else None)
    return answer
