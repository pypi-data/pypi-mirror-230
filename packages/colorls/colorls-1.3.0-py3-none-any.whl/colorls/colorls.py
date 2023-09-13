"""Main module."""

import re
from typing import Dict, Tuple, List, Union, AnyStr, Iterable, Callable, Type, Optional

import colored

from . import size_col_width, ownership_col_width

## MULTI_COL_WIDTH = 20 + SIZE_COL_WIDTH

ISDIR_REGEX = re.compile(r"\s*d")


# == Interface functions ==
def cols_format(cols: int, ownership_cols: int, size_column: int, dir_column: int) -> str:
    size_str = cols[size_column].strip()
    # Pad based on the actual width, not the number of characters (as they
    # include zero-width highlighting data)
    padding = " " * (size_col_width - len(size_str))
    if ISDIR_REGEX.match(cols[dir_column]):
        # Don't highlight directory sizes
        size_output = size_str
    else:
        size_output = colorise(size_str)
    if ownership_cols == 0:
        # no owner/group columns
        return "%s %s%s" % ("".join(cols[0:size_column]), padding + size_output,
                             "".join(cols[size_column+1:]))
    else:
        # at least one owner/group column
        ownership_output = ownership_tweak(cols[size_column-ownership_cols:size_column])
        ## sep_str = " " * (MULTI_COL_WIDTH - len(ownership_output + size_str))
        multicol_output = ownership_output + " " + padding + size_output
        return "%s%s%s" % ("".join(cols[0:size_column-ownership_cols]),
                           multicol_output, "".join(cols[size_column+1:]))


# == Internal functions ==
# Recursive function to highlight every second group of 3 digts (starting from
# the right)
def tweak(s: Optional[str], n=0) -> Tuple[int, str]:
    if not s:
        return 0, ""
    else:
        count, s_prime = tweak(s[1:], n+1)
        # Odd modulo 3
        if int(count / 3) % 2 == 1 and s_prime:
            return count + 1, s[0] + "\b_" + s_prime
        else:
            return count + 1, s[0] + s_prime


def colorise(s: str) -> str:
    """Colorise integer values using underlines and colorise values with a suffix
    using various colours."""

    COLOURS = {"E": "purple_1b", "P": "deep_pink_2", "G": "magenta_2b", "M": "indian_red_1c", "K": "tan"}
    try:
        # See if the size is an integer values
        int(s) 

        ## return s + "\b_"
        length, string = tweak(s)
        return string
    except ValueError:
        # Size is a string, e.g. "3.5M"
        suffix = s[-1]
        try:
            colour = COLOURS[suffix]
            return "%s%s%s%s" % (colored.fg(colour), s[0:-1], colored.attr("reset"), suffix)
        except KeyError:
            return s


def ownership_tweak(cols: Iterable[str]) -> str:
    """Pad (and truncate if necessary) username/groupname columns."""

    def fragment(s: str) -> str:
        """Return a username/groupname truncated as per ps(1) if it won't fit."""
        if len(s) >= ownership_col_width:
            return s[0:ownership_col_width-2] + "+"
        else:
            # Left-justified in a field of one less character than the total column width
            return "%-*s" % (ownership_col_width-1, s)

    # The first column has one space of pre-padding
    return " " + "".join(fragment(col.strip()) + " " for col in cols)


# *** MODULE MAINLINE ***
colored.set_tty_aware(False)
