from enum import Enum

from colored import Fore, Style, Back


class TermColor(Enum):
    """
    Color codes for terminal text

    See colors from `colored`:
    https://gitlab.com/dslackw/colored/-/blob/269aaa136d14a99d112c117a406a741f58c4338c/colored/library.py#L66
    """

    ###################################################################################################################
    # Direct colors:
    # do not use them directly, use semantic colors instead (below).

    back_dark_yellow = Back.yellow

    fore_dark_red = Fore.red
    fore_dark_green = Fore.green
    fore_dark_cyan = Fore.cyan
    fore_dark_magenta = Fore.magenta
    fore_dark_gray = Fore.dark_gray

    fore_bright_yellow = Fore.light_yellow
    fore_bright_blue = Fore.light_blue
    fore_bright_cyan = Fore.light_cyan

    ###################################################################################################################
    # Semantic colors:

    prefix_highlight = back_dark_yellow

    known_envelope_id = fore_dark_gray
    unknown_envelope_id = fore_dark_red

    no_help_hint = fore_dark_red

    help_hint = fore_dark_green

    tangent_token_l_part = fore_bright_cyan
    """
    See `ParsedContext.tan_token_l_part`
    """

    tangent_token_r_part = fore_dark_cyan
    """
    See `ParsedContext.tangent_token_r_part`
    """

    explicit_pos_arg_value = fore_bright_blue
    """
    See `ArgSource.ExplicitPosArg`.
    """

    other_assigned_arg_value = fore_dark_green
    """
    Any other assigned arg value except `explicit_pos_arg_value`.
    """

    remaining_value = fore_bright_yellow
    """
    See `EnvelopeContainer.remaining_types_to_values`.
    """

    consumed_token = fore_bright_blue
    """
    See:
    *   `InterpContext.consumed_tokens`
    *   `BaseResponse.consumed_tokens`
    """

    unconsumed_token = fore_dark_magenta
    """
    See:
    *   `InterpContext.unconsumed_tokens`
    """

    no_option_to_suggest = fore_dark_gray

    debug_output = fore_dark_gray

    reset_style = Style.reset
