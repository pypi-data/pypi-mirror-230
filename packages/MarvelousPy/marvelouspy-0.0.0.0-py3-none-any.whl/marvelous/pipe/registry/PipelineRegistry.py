class PipelineRegistry:
    def __init__(self):
        self.__iterables_registry = {}
        self.__case_block_registry = {}

    # Cleanup & resetting

    def delete_pipe_from_registry(self, pipe):
        if pipe in self.__iterables_registry:
            del self.__iterables_registry[pipe]
        if pipe in self.__case_block_registry:
            del self.__case_block_registry[pipe]

    def generate_new_pipe(self, pipe):
        # TODO Throw if something already registered with this pipe
        pass





    # Define new switch block

    def define_new_switch_block(self, pipe, fcn):
        self.__iterables_registry[pipe] = fcn
        self.__case_block_registry[pipe] = {}

    def register_case(self, pipe, value, fcn_or_value):
        self.__case_block_registry[pipe][value] = fcn_or_value

    def register_default_case(self, pipe, fcn_or_value):
        self.__case_block_registry[pipe][None] = fcn_or_value

    # Checks

    def is_switch_expression_fcn_defined(self, pipe):
        return pipe in self.__iterables_registry

    def is_default_case_defined(self, pipe):
        return None in self.__case_block_registry[pipe]

    # Access the switch logic

    def get_switch_expression_fcn(self, pipe):
        return self.__iterables_registry[pipe]

    def get_case_values(self, pipe):
        #return pipeline_registry.__case_block_registry[pipe]
        pass
