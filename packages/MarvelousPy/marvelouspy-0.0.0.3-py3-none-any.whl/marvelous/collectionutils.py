from src.marvelous import switch
from src.pipe.switch.SwitchBlock import binary_switch
from src.typeutils import is_iterable


def generate_repeated_list(item, repetitions):

    # return binary_switch(is_iterable) \
    #     .add_true(lambda item: item * repetitions) \
    #     .add_false(lambda item: [item] * repetitions) \
    #     .apply(item)

    # fcn(is_iterable,
    #     lambda item: item * repetitions,
    #     lambda item: [item] * repetitions)

    if is_iterable(item):
        return item * repetitions
        # [item for i in range(0, repetitions)]
    else:
        return [item] * repetitions




