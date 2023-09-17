#
#
#
#
#
# # ------------------------------------------------------------------------------
# # Pipeline infrastructure
# # ------------------------------------------------------------------------------
#
#
# class PipelineNode(Iterator):
#     def __init__(self, it):
#         self.iterator = it
#
#     def case(self, switch_expression_fcn_or_value, case_result_fcn_or):
#         return case(switch_expression_fcn_or_value, case_result_fcn_or)
#
#
# # ------------------------------------------------------------------------------
# # Pipeline registry management
# # ------------------------------------------------------------------------------
#
# class PipelineRegistryEntry:
#     def __init__(self):
#
#         # Need to store:
#         # resettable_iterator
#         #   collection_reference
#         #   get_iterator()
#         # registered switch nodes
#         # registered pipelines
#         #   these are callable and don't require construction,
#         #   however could be registered to enable fluent API
#
# class CaseBlockRegistryEntry(PipelineRegistryEntry):
#
#     def __init__(self):
#         self.case_blocks = []
#
#     def add_case(self, switch_expression_fcn_or_value, case_result_fcn_or_value):
#         self.case_blocks.append(CaseBlockRegistryEntry(switch_expression_fcn_or_value, case_result_fcn_or_value))
#
#
#
#
#
# class CaseBlockRegistryEntry:
#
#     def __init__(self, switch_expression_fcn_or_value, case_result_fcn_or_value):
#
#         # Callable function passed in
#         self.switch_expression_fcn = switch_expression_fcn_or_value
#         self.case_result_fcn = case_result_fcn_or_value
#
#         # If value passed in, change to callable function
#         if not callable(switch_expression_fcn_or_value):
#             self.switch_expression_fcn = lambda: switch_expression_fcn_or_value
#         if not callable(case_result_fcn_or_value):
#             self.case_result_fcn = lambda: case_result_fcn_or_value
#
#     def execute(self, item):
#
#
#
#
#
#
#
#
#
#
# # Define the registry singleton
# pipeline_registry = PipelineRegistry()
#
#
# # ------------------------------------------------------------------------------
# # Case block definition
# # ------------------------------------------------------------------------------
#
#
# def switch(iterable, fcn=None):
#     pipe = iter(iterable)
#
#     # Switch case expression may be determined by a function, or simply be the collection item
#     fcn = fcn or (lambda x: x)
#
#     pipeline_registry.delete_pipe_from_registry(pipe)
#     pipeline_registry.define_new_switch_block(pipe, fcn)
#     return pipe
#
#
# def case(pipe, value, fcn_or_value):
#     if not pipeline_registry.is_switch_expression_fcn_defined(pipe):
#         raise AttributeError("No switch block is defined for this pipe.")
#     pipeline_registry.register_case(pipe, value, fcn_or_value)
#
#
# def case_default(pipe, fcn_or_value):
#     if not pipeline_registry.is_switch_expression_fcn_defined(pipe):
#         raise AttributeError("No switch block is defined for this pipe.")
#     pipeline_registry.register_default_case(pipe, fcn_or_value)
#
#
#     if not pipeline_registry.is_switch_expression_fcn_defined(pipe):
# def apply_switch(pipe):
#         raise AttributeError("No switch block is defined for this pipe.")
#
#     if not pipeline_registry.is_default_case_defined(pipe):
#         raise AttributeError("Default case not defined for switch.")
#
#     switch_expression_fcn = pipeline_registry.get_switch_expression_fcn(pipe)
#
#     # Need to reset the iterator in each applicaiton of the pipe, but Python provides no way
#     new_pipe = pipeline_registry.generate_new_pipe(pipe)
#
#     for item in pipe:
#
#         switch_expression = switch_expression_fcn(item)
#
#         case_values = pipeline_registry.get_case_values(pipe)
#
#         if switch_expression in case_values:
#             fcn_or_value = case_values[item]
#         else:
#             fcn_or_value = case_values.get(None)
#
#         if callable(fcn_or_value):
#             yield fcn_or_value(item)
#         else:
#             yield fcn_or_value
#
#
#
# cases_from_dict(dictionary)
#
# cases_from_list_lookup(keys, values)
