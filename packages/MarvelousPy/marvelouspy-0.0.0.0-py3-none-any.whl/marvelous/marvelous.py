from marvelous.pipe.switch.SwitchBlockRegistryEntry import SwitchBlockRegistryEntry


def switch(match_expression_function=None):
    """Defines a switch block."""
    return SwitchBlockRegistryEntry(match_expression_function)





