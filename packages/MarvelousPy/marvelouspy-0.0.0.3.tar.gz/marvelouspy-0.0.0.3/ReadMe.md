# MarvelousPy

Amazing functional programming interface for Python.

# Pipelines

Data pipelines are defined which connect blocks.

# Blocks

Blocks are fundamental units composing pipelines.

# Types of Blocks

## Switch

Defines piecewise-defined switch block.

Define the matching function.

Define cases, composed of:
- Case expression
- Value expression

Cases are defined

## Binary Switch

A binary switch provides similar operation as the standard switch block, but restricts possible case values to True and False.

A binary switch may be defined trivially, and is applicable to use cases which require splitting the input data.

```
sw = binary_switch(lambda x: x == 4)
case(1, "One")
case(2, "Two")
default("Unknown")
apply([0, 1, 2])  # Returns [ "Unknown", "One", "Two"]



data_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 999]
expected_data_list = ["Not Four", "Not Four", "Not Four", "FOUND FOUR", "Not Four", "Not Four", "Not Four",
      "Not Four", "Not Four", "Not Four", "Not Four"]

# Set up the switch
data_pipe = binary_switch(lambda x: x == 4)

# Assign values (default implicitly assigned through the False case)
case_true(data_pipe, "FOUND FOUR")
case_false(data_pipe, "Not Four")

# Apply the switch
out_iterator = apply(data_pipe, data_list)
self.assertListEqual(list(out_iterator), expected_data_list)
```


        Defines a switch block.

            # Anatomy of a switch block declaration
            switch(<match expression>)
            case(<case expression>, <value expression>)
            default(<default value expression>)

            # Build a pure mapping function
            switch()
            default(lambda x: <transform>)

            # Build a switch block, switching based on raw value, generating a value
            switch()
            case(1, "One")
            case(2, "Two")
            default("Unknown")
            apply([0, 1, 2])  # Returns [ "Unknown", "One", "Two"]

            # Build a switch block, switching based on the value transformed through the match expression, generating
                a value
            switch(lambda x: x + 1)
            case(1, "One")
            default("Unknown")
            apply([0, 1, 2])  # Returns [ "One", "Unknown", "Unknown"]

            # Build a switch block, switching based on the case expression matched to the value processed by the match
                expression, generating an expression
            switch(lambda x: x + 1)
            case(lambda x: x == 4, lambda x: x*x)
            default("Unknown")
            apply([1, 2, 3])  # Returns [ "Unknown", "Unknown", 9]
            # Explanation:
            #   Consider value 3
            #   Match expression evaluates to 3 + 1
            #   Case expression evaluates to 4 == 4
            #   Value expression generates 3 * 3. Note that the item under consideration, not the result of the
                match expression, is plugged into the value expression.

        :param match_expression_function: Silent transformation function used to transform input prior to comparison with
            case lookup tables.
        :param pipe_from:
        :param pipe_to:


## Map

Perform 1:1 mapping operation for the input.






        :param case_lookup: Values or expressions mapped to output values or expressions. None key denotes default case. Example:

                {
                    1: "One",                   # Maps a value to a value
                    lambda x: x == 2: "Two",    # Evaluates the match expression (computed from the item), and if the function returns true the value "Two" is returned.
                    3: lambda x: "Three",       # Maps a value to a function which is executed on the item.
                    None: "Unknown"             # Provides a default value. If not provided, None is used as the default.
                 }

        :return: