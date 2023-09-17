import logging

from daconx.config import color_prefix
from daconx.utils import read_a_file

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AST_NodeTraverse():
    def __init__(self, solidity_file_content: str, solidity_absolute_path: str = ""):
        self.solidity_file_content = solidity_file_content
        self.solidity_absolute_path = solidity_absolute_path
        self.function_code_dict = {}
        self.event_code_dict={}
        self.state_variable_code_dict={}
        self.modifier_code_dict={}
        self.accumulated_print_results = ""  # used to save the intermediate example_results during the traverse. Almost equivalent to the example_results that can be printed out.
        if len(self.solidity_file_content) == 0:
            self.solidity_file_content = read_a_file(self.solidity_absolute_path)

    def traverse_ast(self, node):
        # Process the current node
        if hasattr(node, "nodeType"):

            # print node information
            if node.nodeType not in ["SourceUnit", "ContractDefinition"]:

                # separate the major components of smart contract code
                if node.nodeType in ['FunctionDefinition', 'ModifierDefinition', 'EventDefinition']:
                    self.record(f'====')

                if node.nodeType in ['VariableDeclaration']:
                    if hasattr(node, 'stateVariable'):
                        if node.stateVariable:
                            self.record(f'====')

                # separate the statements of the smart contract code
                if node.nodeType in ['ExpressionStatement', 'IfStatement', 'ForStatement',
                                     'VariableDeclarationStatement']:
                    self.record(f'----')

                # -------------- function handle --------------------
                # begin to handle each type nodes
                if node.nodeType == 'FunctionDefinition':
                    function_name = self.check_function_name_and_type(node)
                    self.check_properties(node,['functionSelector','visibility', 'id', 'implemented', 'stateMutability', 'virtual'])
                    self.check_modifiers(node)
                    self.check_parameters(node)
                    self.check_return_values(node)
                    # directly save function code instead of saving it to extract later
                    if hasattr(node, 'src'):
                        code = self.print_source_code(node.src, 'function_code')
                        self.function_code_dict[function_name] = code


                # -------------- state variable handle --------------------
                elif node.nodeType == 'VariableDeclaration':
                    self.record(f'state_variable_name:{node.name}')
                    self.check_properties(node,['id', 'visibility', 'typeDescriptions'])
                    if hasattr(node, 'value'):
                        if node.value is None:
                            self.record(f'NULL')
                        else:
                            self.traverse_ast(node.value)
                    if hasattr(node, 'src'):
                        code = self.print_source_code(node.src, 'state_variable_code')
                        self.state_variable_code_dict[node.name] = code

                # -------------- modifier handle --------------------
                elif node.nodeType == 'ModifierDefinition':
                    self.record(f'modifier_name:{node.name}')
                    self.check_properties(node,['id'])
                    if hasattr(node, 'src'):
                        code = self.print_source_code(node.src, 'modifier_code')
                        self.modifier_code_dict[node.name] = code

                # -------------- event handle --------------------
                elif node.nodeType == 'EventDefinition':
                    self.record(f'event_name:{node.name}')
                    self.check_properties(node,['id'])
                    self.check_parameters(node)
                    if hasattr(node, 'src'):
                        code = self.print_source_code(node.src, 'event_code')
                        self.event_code_dict[node.name] = code

                elif node.nodeType == 'ExpressionStatement':
                    if hasattr(node, 'expression'):
                        self.traverse_ast(node.expression)

                elif node.nodeType == 'IfStatement':
                    self.record(f'if_statement:')
                    if hasattr(node, 'condition'):
                        self.traverse_ast(node.condition)
                    if hasattr(node, 'trueBody'):
                        for body in node.trueBody:
                            self.traverse_ast(body)
                    if hasattr(node, 'falseBody'):
                        if isinstance(node.falseBody, list):
                            for body in node.falseBody:
                                self.traverse_ast(body)
                        else:
                            if node.falseBody is not None:
                                if hasattr(node.falseBody, 'nodeType'):
                                    if node.falseBody.nodeType == 'IfStatement':
                                        self.traverse_ast(node.falseBody)
                                    else:
                                        logger.info('need to handle if statement')

                elif node.nodeType == 'ForStatement':
                    self.record(f'for_statement')
                    if hasattr(node, 'condition'):
                        self.traverse_ast(node.condition)

                elif node.nodeType == 'VariableDeclarationStatement':
                    if hasattr(node, 'declarations'):
                        for declaration in node.declarations:
                            self.traverse_ast(declaration)

                    if hasattr(node, 'initialValue'):
                        self.record(f'initial_value:')
                        self.traverse_ast(node.initialValue)

                elif node.nodeType == 'TupleExpression':
                    logger.info(f'{color_prefix["Green"]}({color_prefix["Gray"]}')
                    self.accumulated_print_results += "(\n"
                    if hasattr(node, 'components'):
                        len_comp = len(node.components)
                        for idx, component in enumerate(node.components):
                            if idx > 0 and idx < len_comp - 1:
                                logger.info(f'{color_prefix["Green"]},{color_prefix["Gray"]}')
                                self.accumulated_print_results += ",\n"
                            self.traverse_ast(component)
                    logger.info(f'{color_prefix["Green"]}){color_prefix["Gray"]}')
                    self.accumulated_print_results += ")\n"

                elif node.nodeType == "FunctionCall":
                    # may also print out the name of the function call
                    if hasattr(node, 'expression'):
                        self.record(f'function_call:')
                        self.traverse_ast(node.expression)

                    if hasattr(node, 'arguments'):
                        # print(f'arguments:')
                        logger.info(f'{color_prefix["Green"]}({color_prefix["Gray"]}')  # (
                        self.accumulated_print_results += '(\n'
                        len_args = len(node.arguments)
                        for idx, argument in enumerate(node.arguments):
                            if idx > 0 and idx <= len_args - 1:
                                logger.info(f'{color_prefix["Green"]},{color_prefix["Gray"]}')
                                self.accumulated_print_results += ",\n"
                            self.traverse_ast(argument)
                        logger.info(f'{color_prefix["Green"]}){color_prefix["Gray"]}')  # )
                        self.accumulated_print_results += ")\n"

                elif node.nodeType == 'Assignment':
                    self.record(f'assignment:')

                    # e.g., owner=msg.sender (assignment)
                    if hasattr(node, 'leftHandSide'):
                        self.traverse_ast(node.leftHandSide)
                    if hasattr(node, 'operator'):
                        logger.info(f'{node.operator}')
                        self.accumulated_print_results += f'{node.operator}@@operator\n'
                    if hasattr(node, "rightHandSide"):
                        self.traverse_ast(node.rightHandSide)
                elif node.nodeType == 'BinaryOperation':
                    # e.g., now+60 days in "end=now+60 days" (binary expression)
                    if hasattr(node, 'leftExpression'):
                        self.traverse_ast(node.leftExpression)
                    if hasattr(node, 'operator'):
                        logger.info(f'{node.operator}')
                        self.accumulated_print_results += f'{node.operator}@@operator\n'
                    if hasattr(node, "rightExpression"):
                        self.traverse_ast(node.rightExpression)
                elif node.nodeType == 'UnaryOperation':
                    if hasattr(node, 'operator'):
                        logger.info(f'{node.operator}')
                        self.accumulated_print_results += f'{node.operator}@@operator\n'
                    if hasattr(node, 'subExpression'):
                        self.traverse_ast(node.subExpression)
                elif node.nodeType in ['Literal', 'IndexAccess', 'Identifier', 'MemberAccess', 'EventDefinition',
                                       'ElementaryTypeNameExpression']:

                    name = ""
                    if hasattr(node, 'name'):
                        name = node.name
                    # if hasattr(node, 'id'):
                    #     print(f'       id: {node.id}')
                    if hasattr(node, 'src'):
                        code = self.print_source_code(node.src)
                        self.accumulated_print_results += code + f'@@{node.nodeType}\n'
                    type = ""
                    if hasattr(node, 'typeDescriptions'):
                        type = str(node.typeDescriptions["typeString"])
                        # logger.info(f'....... {node.typeDescriptions["typeString"]}')
                        if type.startswith('function (') or type.startswith('function('):

                            if node.nodeType == 'Identifier':
                                self.accumulated_print_results += f'xxxxfunction_call:{name}\n'  # used to collect function call names
                            elif node.nodeType == 'MemberAccess':
                                if hasattr(node, 'expression'):
                                    if hasattr(node.expression, 'name'):
                                        name = node.expression.name
                                if hasattr(node, 'memberName'):
                                    member_name = node.memberName
                                    self.accumulated_print_results += f'xxxxfunction_call:{name}:{member_name}\n'  # used to collect function call names

                            else:
                                # member access like: token.mint, value.mul
                                logger.info(f'xx')

                    return

            if hasattr(node, 'nodes'):
                # Recursively process child nodes
                if len(node.nodes) > 0:
                    for child_node in node.nodes:
                        self.traverse_ast(child_node)

    def print_source_code(self, src: str, description: str = ""):
        items = src.split(":")
        assert len(items) >= 2
        start = int(items[0])
        length = int(items[1])
        content = self.solidity_file_content[start:start + length]
        if len(description) > 0:
            logger.info(f'{description}:{color_prefix["Blue"]}{content}{color_prefix["Gray"]}')
        else:
            logger.info(f'{color_prefix["Blue"]}{content}{color_prefix["Gray"]}')
        return content

    def check_properties(self, node, properties: list):
        """
        :param properties: ['visibility', 'id', 'implemented', 'stateMutability', 'virtual']
        :return:
        """
        for property in properties:
            if property == 'typeDescriptions':
                self.record(f'type:{node.typeDescriptions["typeString"]}')
            elif hasattr(node, property):
                attr_value = getattr(node, property)
                self.record(f'{property}:{attr_value}')


    def check_function_name_and_type(self, node):
        """
         get the function name and check whether it is a constructor or not
         "fallback","receive","constructor", regular function names
        :param node:
        :return:
        """
        function_name = node.name
        is_constructor = False
        if hasattr(node, 'isConstructor'):
            if node.isConstructor:
                if len(node.name) == 0:
                    function_name = 'constructor'
                is_constructor = True

        if hasattr(node, 'kind'):
            if node.kind == 'constructor':
                if len(node.name) == 0:
                    function_name = 'constructor'
                is_constructor = True
            elif node.kind == 'fallback':
                if len(node.name) == 0:
                    function_name = 'fallback'

        if len(function_name) == 0:
            function_name = 'fallback'

        self.record(f'function_name:{function_name}')
        self.record(f'is_constructor:{is_constructor}')

        return function_name

    def check_modifiers(self, node):
        if hasattr(node, 'modifiers'):
            len_m = len(node.modifiers)
            if len_m > 0:
                for modifier in node.modifiers:
                    if hasattr(modifier, 'modifierName'):
                        self.record(f'modifier_name:{modifier.modifierName.name}')
            else:
                self.record(f'modifiers:[]')

    def check_parameters(self, node):
        """
        check function parameters
        :param node:
        :return:
        """
        if hasattr(node, 'parameters'):
            len_args = len(node.parameters.parameters)
            if len_args > 0:
                for idx, parameter in enumerate(node.parameters.parameters):
                    if hasattr(parameter, 'typeDescriptions') and hasattr(parameter, 'name'):
                        id = -1
                        if hasattr(parameter, 'id'): id = parameter.id
                        self.record(
                            f'parameter_type:{parameter.typeDescriptions["typeString"]};parameter_name:{parameter.name};id:{parameter.id}')

            else:
                self.record(f'parameters:[]')

    def check_return_values(self, node):
        if hasattr(node, 'returnParameters'):
            len_args = len(node.returnParameters.parameters)
            if len_args > 0:
                for idx, parameter in enumerate(node.returnParameters.parameters):
                    if hasattr(parameter, 'typeDescriptions') and hasattr(parameter, 'name'):
                        if len(parameter.name) == 0:
                            parameter_name = 'NULL'
                        else:
                            parameter_name = parameter.name
                        id = -1
                        if hasattr(parameter, 'id'): id = parameter.id
                        self.record(
                            f'return_value_type:{parameter.typeDescriptions["typeString"]};return_value_name:{parameter_name};id:{parameter.id}')

            else:
                self.record(f'return_values:[]')

    def record(self, data: str):
        """
        save the data during traversing the ast nodes, the example_results of which will be used to extract data
        :param data:
        :return:
        """
        logger.info(data)  # used to see what is visited and debug
        self.accumulated_print_results += f'{data}\n'  # used to extract data
