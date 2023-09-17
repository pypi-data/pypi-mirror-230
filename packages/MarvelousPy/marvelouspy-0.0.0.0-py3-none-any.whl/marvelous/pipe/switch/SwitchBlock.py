from marvelous.pipe.switch.SwitchBlockRegistryEntry import SwitchBlockRegistryEntry, BinarySwitchBlockRegistryEntry


# ------------------------------------------------------------------------------
# Switch block builder interface
# ------------------------------------------------------------------------------


# def switch(match_expression_function=None):
#     """Defines a switch block."""
#     return SwitchBlockRegistryEntry(match_expression_function)


def case(data_pipe, match_expression, value_expression):
    """Adds a case to a switch block."""
    return data_pipe.add_case(match_expression, value_expression)


def cases_from_dict(data_pipe, case_lookup):
    """Adds cases from items in a dictionary."""
    data_pipe.add_cases_from_dict(case_lookup)


def case_default(data_pipe, value_expression):
    """Adds the default case to a switch block."""
    return data_pipe.add_default(value_expression)


# ------------------------------------------------------------------------------
# Binary switch block builder interface
# ------------------------------------------------------------------------------

def binary_switch(match_expression_function=None):
    """Defines a binary switch block."""
    return BinarySwitchBlockRegistryEntry(match_expression_function)


def case_true(data_pipe, value_expression):
    """Add True case handling."""
    data_pipe.add_true(value_expression)


def case_false(data_pipe, value_expression):
    """Add False case handling."""
    data_pipe.add_false(value_expression)


# ------------------------------------------------------------------------------
# Switch executor interface
# ------------------------------------------------------------------------------


def apply(data_pipe, data):
    """Apply the case block to any item or iterable."""
    return data_pipe.apply(data)


def apply_keys(data_pipe, dictionary_data):
    """Apply the case block to the keys of a dictionary."""
    return data_pipe.apply_keys(dictionary_data)


def apply_values(data_pipe, dictionary_data):
    """Apply the case block to the values of a dictionary."""
    return data_pipe.apply_values(dictionary_data)


# ------------------------------------------------------------------------------
# Map-reduce interface
# ------------------------------------------------------------------------------

def fmap(mapping_function):
    """Define a mapping block."""
    return SwitchBlockRegistryEntry().add_default(mapping_function)

# def reduce(reduce_function):
#     """Define a reduce block."""
#     data_pipe = SwitchBlockRegistryEntry()
