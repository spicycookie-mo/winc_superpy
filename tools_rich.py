import sys
import csv
from typing import TYPE_CHECKING, Optional, Union

from rich.jupyter import JupyterMixin
from rich.segment import Segment
from rich.style import Style
from rich._emoji_codes import EMOJI
from rich._emoji_replace import _emoji_replace

from rich.console import Console
console = Console()

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal  # pragma: no cover


if TYPE_CHECKING:
    from rich.console import Console, ConsoleOptions, RenderResult


EmojiVariant = Literal["emoji", "text"]


class NoEmoji(Exception):
    """No emoji by that name."""




class Emoji(JupyterMixin):
    __slots__ = ["name", "style", "_char", "variant"]

    VARIANTS = {"text": "\uFE0E", "emoji": "\uFE0F"}

    def __init__(
        self,
        name: str,
        style: Union[str, Style] = "none",
        variant: Optional[EmojiVariant] = None,
    ) -> None:
        """A single emoji character.

        Args:
            name (str): Name of emoji.
            style (Union[str, Style], optional): Optional style. Defaults to None.

        Raises:
            NoEmoji: If the emoji doesn't exist.
        """
        self.name = name
        self.style = style
        self.variant = variant
        try:
            self._char = EMOJI[name]
        except KeyError:
            raise NoEmoji(f"No emoji called {name!r}")
        if variant is not None:
            self._char += self.VARIANTS.get(variant, "")



    @classmethod
    def replace(cls, text: str) -> str:
        """Replace emoji markup with corresponding unicode characters.

        Args:
            text (str): A string with emojis codes, e.g. "Hello :smiley:!"

        Returns:
            str: A string with emoji codes replaces with actual emoji.
        """
        return _emoji_replace(text)


    def __repr__(self) -> str:
        return f"<emoji {self.name!r}>"

    def __str__(self) -> str:
        return self._char

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        yield Segment(self._char, console.get_style(self.style))

######################################
######### my functions ###############
#######################################

def find_emoji(emoji):
        emojis_list = []

        for name in sorted(EMOJI.keys()):
            if "\u200D" not in name:
                emojis_list.append(name)
        # print(emojis_list)        
        if emoji in emojis_list:
            return True
        else:
            return False

def rich_style(value):
    if value >=0:
        style = 'green' 
    else:
        style = 'red'
    return style

# print(rich_style(78.3))
##########################################        
##########################################



if __name__ == "__main__":  # pragma: no cover
    import sys

    from rich.columns import Columns
    from rich.console import Console

    console = Console(record=True)

    columns = Columns(
        (f":{name}: {name}" for name in sorted(EMOJI.keys()) if "\u200D" not in name),
        column_first=True,
    )
        
    console.print(columns)
    
    
    if len(sys.argv) > 1:
        console.save_html(sys.argv[1])
