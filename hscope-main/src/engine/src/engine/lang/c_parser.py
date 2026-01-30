#!/usr/bin/env python3

import re
#from engine.src.engine.config.constants import EngineInternalDataType
import engine.lang.common_parser as common_parser
from engine.util import util
from engine.config.constants import ENGINE_INTERNAL

class Parser(common_parser.Parser):
    def init(self):
        self.CONSTANTS_MAP = {
            "null"                          : ENGINE_INTERNAL.NULL,
            "true"                          : ENGINE_INTERNAL.TRUE,
            "false"                         : ENGINE_INTERNAL.FALSE,
        }

        self.LITERAL_MAP = {
            "number_literal"                : self.regular_number_literal,
            "true"                          : self.regular_literal,
            "false"                         : self.regular_literal,
            "char_literal"                  : self.char_literal,
            "null_literal"                  : self.regular_literal,
            "identifier"                    : self.regular_literal,
            "field_identifier"              : self.regular_literal,
            "string_literal"                : self.string_literal,
            "concatenated_string"           : self.concatenated_string,
            "storage_class_specifier"       : self.regular_literal,
            "type_qualifier"                : self.regular_literal,
            "ms_call_modifier"              : self.regular_literal,
            "ms_pointer_modifier"           : self.regular_literal,
            "initializer_list"              : self.initializer_list,
        }

        self.EXPRESSION_HANDLER_MAP = {
            "assignment_expression"         : self.assignment_expression,
            "binary_expression"             : self.binary_expression,
            "pointer_expression"            : self.pointer_expression,
            "subscript_expression"          : self.array,
            "field_expression"              : self.field,
            "call_expression"               : self.call_expression,
            "update_expression"             : self.update_expression,
            "cast_expression"               : self.cast_expression,
            "sizeof_expression"             : self.sizeof_expression,
            "unary_expression"              : self.unary_expression,
            "offsetof_expression"           : self.offsetof_expression,
            "generic_expression"            : self.generic_expression,
            "conditional_expression"        : self.conditional_expression,
            "compound_literal_expression"   : self.compound_literal_expression,
            "alignof_expression"            : self.alignof_expression,
            "gnu_asm_expression"            : self.gnu_asm_expression,
            "parenthesized_expression"      : self.parenthesized_expression,

        }

        self.DECLARATION_HANDLER_MAP = {
            "function_definition"           : self.function_declaration,
            "type_definition"               : self.type_definition,
            "parameter_declaration"         : self.parameter_declaration,
            "struct_specifier"              : self.struct_specifier,
            "union_specifier"               : self.struct_specifier,
            "declaration"                   : self.variable_declaration,
            "enum_specifier"                : self.enum_declaration,
        }

        self.STATEMENT_HANDLER_MAP = {
            "return_statement"              : self.return_statement,
            "if_statement"                  : self.if_statement,
            "while_statement"               : self.while_statement,
            "for_statement"                 : self.for_statement,
            "switch_statement"              : self.switch_statement,
            "break_statement"               : self.break_statement,
            "continue_statement"            : self.continue_statement,
            "goto_statement"                : self.goto_statement,
            "do_statement"                  : self.dowhile_statement,
            "labeled_statement"             : self.label_statement,
            "attributed_statement"          : self.attributed_statement,
            "case_statement"                : self.case_statement,
            "seh_try_statement"             : self.seh_try_statement,
            "seh_leave_statement"           : self.seh_leave_statement,
        }


    # “”
    def is_expression(self, node):
        # return False
        # “”
        return self.check_expression_handler(node) is not None

    # “”
    def expression(self, node, statements):
        handler = self.check_expression_handler(node)
        return handler(node, statements)

    # ""
    def check_expression_handler(self, node):
        # 
        return self.EXPRESSION_HANDLER_MAP.get(node.type, None)

    def assignment_expression(self, node, statements):
        left = self.find_child_by_field(node, "left")

        while left.type == "parenthesized_expression":
            # assert left.named_child_count == 1
            left = left.named_children[0]

        operator = self.find_child_by_field(node, "operator")
        # "="
        shadow_operator = self.read_node_text(operator).replace("=", "")

        right = self.find_child_by_field(node, "right")
        # parsebinary_assignment %1
        shadow_right = self.parse(right, statements)

        # 
        #  arr[i] = ...
        if left.type == "subscript_expression":
            shadow_array, shadow_index = self.parse_array(left, statements)
            # =
            if not shadow_operator:
                self.append_stmts(statements,  node, {"array_write":
                    {"array": shadow_array, "index": shadow_index, "source": shadow_right}}
                )
                return shadow_right

            # +=
            tmp_var = self.tmp_variable()
            self.append_stmts(statements,  node, {"array_read": {"target": tmp_var, "array": shadow_array, "index": shadow_index}})
            tmp_var2 = self.tmp_variable()
            self.append_stmts(statements,  node, {"assign_stmt":
                                   {"target": tmp_var2, "operator": shadow_operator, "operand": tmp_var,
                                    "operand2": shadow_right}})
            self.append_stmts(statements,  node, {"array_write": {"array": shadow_array, "index": shadow_index, "source": tmp_var2}})
            return tmp_var2

        #  x.f = ...
        if left.type == "field_expression":
            shadow_argument, shadow_field = self.parse_field(left, statements)
            # =
            if not shadow_operator:
                self.append_stmts(statements,  node, {"field_write": {"receiver_object": shadow_argument, "field": shadow_field, "source": shadow_right}})
                return shadow_right

            # +=
            tmp_var = self.tmp_variable()
            self.append_stmts(statements,  node, {"field_read": {"target": tmp_var, "receiver_object": shadow_argument, "field": shadow_field}})
            tmp_var2 = self.tmp_variable()
            self.append_stmts(statements,  node, {"assign_stmt":
                {"target": tmp_var2, "operator": shadow_operator, "operand": tmp_var,
                "operand2": shadow_right}})
            self.append_stmts(statements,  node, {"field_write": {"receiver_object": shadow_argument, "field": shadow_field, "source": tmp_var2}})
            return tmp_var2

        # 
        if left.type == "pointer_expression":
            shadow_argument = self.parse_pointer(left, statements)
            # =
            if not shadow_operator:
                self.append_stmts(statements,  node, {"mem_write": {"address": shadow_argument, "source": shadow_right}})
                return shadow_right

            # +=
            tmp_var = self.tmp_variable()
            self.append_stmts(statements,  node, {"mem_read": {"target": tmp_var, "address": shadow_argument}})
            tmp_var2 = self.tmp_variable()
            self.append_stmts(statements,  node, {"assign_stmt": {
                "target": tmp_var2, "operator": shadow_operator, "operand": tmp_var, "operand2": shadow_right}})
            self.append_stmts(statements,  node, {"mem_write": {"address": shadow_argument, "source": tmp_var2}})
            return tmp_var2

        # 
        shadow_left = self.parse(left)
        # "="
        if not shadow_operator:
            self.append_stmts(statements,  node, {"assign_stmt": {"target": shadow_left, "operand": shadow_right}})
        # "+="
        else:
            self.append_stmts(statements,  node, {"assign_stmt": {
                "target": shadow_left, "operator": shadow_operator,
                "operand": shadow_left, "operand2": shadow_right}})

        return shadow_left

    def binary_expression(self, node, statements):
        left = self.find_child_by_field(node, "left")
        right = self.find_child_by_field(node, "right")
        operator = self.find_child_by_field(node, "operator")

        shadow_operator = self.read_node_text(operator)
        # 
        shadow_left = self.parse(left, statements)
        shadow_right = self.parse(right, statements)

        #  %1=b+c
        tmp_var = self.tmp_variable()
        self.append_stmts(statements,  node, {"assign_stmt": {"target": tmp_var, "operator": shadow_operator,
                                           "operand": shadow_left, "operand2": shadow_right}})
        return tmp_var

    #  *&
    def pointer_expression(self, node, statements):
        operator = self.find_child_by_field(node, "operator")
        operator = self.read_node_text(operator)
        tmp_var = self.tmp_variable()
        shadow_argument = self.parse_pointer(node, statements)
        # *
        if (operator == "*"):
            self.append_stmts(statements,  node, {"mem_read": {"target": tmp_var, "address": shadow_argument}})
        # &
        elif (operator == "&"):
            self.append_stmts(statements,  node, {"addr_of": {"target": tmp_var, "source": shadow_argument}})

        return tmp_var

    # 
    def parse_pointer(self, node, statements):
        argument = self.find_child_by_field(node, "argument")
        # 
        shadow_argument = self.parse(argument, statements)
        return shadow_argument

    # 
    def parse_array(self, node, statements):
        array = self.find_child_by_field(node, "argument")
        shadow_array = self.parse(array, statements)
        index = self.find_child_by_field(node, "index")
        shadow_index = self.parse(index, statements)
        return (shadow_array, shadow_index)

    # %1=arr[i]
    def array(self, node, statements):
        tmp_var = self.tmp_variable()
        shadow_array, shadow_index = self.parse_array(node, statements)
        self.append_stmts(statements,  node, {"array_read": {"target": tmp_var, "array": shadow_array, "index": shadow_index}})
        return tmp_var

    # 
    def parse_field(self, node, statements):
        argument = self.find_child_by_field(node, "argument")
        # argumenta.b.c.djava(javasuperparse)
        shadow_argument = self.parse(argument, statements)
        field = self.find_child_by_field(node, "field")
        shadow_field = self.read_node_text(field)
        return (shadow_argument, shadow_field)

    #   %1=a.b
    def field(self, node, statements):
        tmp_var = self.tmp_variable()
        shadow_argument, shadow_field = self.parse_field(node, statements)
        self.append_stmts(statements,  node, {"field_read": {"target": tmp_var, "receiver_object": shadow_argument, "field": shadow_field}})
        return tmp_var

    # 
    def call_expression(self, node, statements):
        function = self.find_child_by_field(node, "function")
        shadow_name = self.parse(function)

        arguments = self.find_child_by_field(node, "arguments")
        arg_list = []

        if arguments.named_child_count > 0:
            for child in arguments.named_children:
                if self.is_comment(child):
                    continue
                arg_list.append(self.parse(child, statements))

        tmp_return = self.tmp_variable()
        self.append_stmts(statements,  node, {"call_stmt": {"target": tmp_return, "name": shadow_name, "positional_args": arg_list}})

        # 
        return tmp_return

    # expression++ , expression--
    def update_expression(self, node, statements):
        shadow_node = self.read_node_text(node)

        update_operator = self.find_child_by_field(node, "operator")
        operator_text = self.read_node_text(update_operator)

        operator = ""
        if "++" == operator_text:
            operator = "+"
        elif "--" == operator_text:
            operator = "-"
        else:
            util.debug("update expression++--")
        # ++or
        is_after = False
        if shadow_node[-1] == operator:
            is_after = True

        tmp_var = self.tmp_variable()

        expression = self.find_child_by_field(node, "argument")

        while expression.type == "parenthesized_expression":
            # assert operand.named_child_count == 1
            expression = expression.named_children[0]

        if expression.type == "field_expression":
            shadow_object, field = self.parse_field(expression, statements)

            self.append_stmts(statements,  node, {"field_read": {"target": tmp_var, "receiver_object": shadow_object, "field": field}})
            tmp_var2 = self.tmp_variable()
            self.append_stmts(statements,  node, {"assign_stmt": {"target": tmp_var2, "operator": operator, "operand": tmp_var, "operand2": "1"}})
            self.append_stmts(statements,  node, {"field_write": {"receiver_object": shadow_object, "field": field, "source": tmp_var2}})

            # 
            if is_after:
                return tmp_var
            # 
            return tmp_var2

        if expression.type == "subscript_expression":
            shadow_array, shadow_index = self.parse_array(expression, statements)

            self.append_stmts(statements,  node, {"array_read": {"target": tmp_var, "array": shadow_array, "index": shadow_index}})
            tmp_var2 = self.tmp_variable()
            self.append_stmts(statements,  node,
                {"assign_stmt": {"target": tmp_var2, "operator": operator, "operand": tmp_var, "operand2": "1"}})
            self.append_stmts(statements,  node, {"array_write": {"array": shadow_array, "index": shadow_index, "source": tmp_var2}})

            if is_after:
                return tmp_var
            return tmp_var2

        shadow_expression = self.parse(expression, statements)
        self.append_stmts(statements,  node, {"assign_stmt": {"target": tmp_var, "operand": shadow_expression}})
        self.append_stmts(statements,  node, {"assign_stmt": {"target": shadow_expression, "operator": operator,
                                           "operand": shadow_expression, "operand2": "1"}})

        # 
        if is_after:
            return tmp_var
        # 
        return shadow_expression


    # 
    def cast_expression(self, node, statements):
        attrs = []
        value = self.find_child_by_field(node, "value")
        shadow_value = self.parse(value, statements)
        type_descriptor = self.find_child_by_field(node, "type")
        # 
        self.search_for_modifiers(type_descriptor, attrs)
        _type_specifier = self.find_child_by_field(type_descriptor, "type")
        shadow_type = self.parse(_type_specifier, statements)
        if _abstract_declarator:=self.find_child_by_field(type_descriptor, "declarator"):
            shadow_abstract_declarator = self.read_node_text(_abstract_declarator)
            shadow_type = f"{shadow_type}{shadow_abstract_declarator}"
            self.search_for_modifiers(_abstract_declarator, attrs)

        # ()
        tmp = self.tmp_variable()
        self.append_stmts(statements,  node, {"type_cast_stmt" : {"target" : tmp, "data_type" : shadow_type, "source" : shadow_value}})
        return tmp

    def sizeof_expression(self,node,statements):
        value = self.find_child_by_field(node,"value")
        type_descriptor = self.find_child_by_field(node,"type")
        shadow_value = 0
        if value:
            shadow_value = self.parse(value,statements)
        elif type_descriptor:
            shadow_value = self.parse(type_descriptor,statements)
        tmp = self.tmp_variable()
        self.append_stmts(statements,  node, {"assign_stmt":{"target":tmp, "operator":"sizeof", "operand":shadow_value}})
        return tmp

    # ~a  assign_stmt %v0, ~, a
    def unary_expression(self, node, statements):
        operand = self.find_child_by_field(node, "argument")
        shadow_operand = self.parse(operand, statements)
        operator = self.find_child_by_field(node, "operator")
        shadow_operator = self.read_node_text(operator)

        tmp_var = self.tmp_variable()

        self.append_stmts(statements,  node, {"assign_stmt": {"target": tmp_var, "operator": shadow_operator, "operand": shadow_operand}})
        return tmp_var

    # offset_height = offsetof(struct Person, height);
    def offsetof_expression(self, node, statements):
        type_discriptor = self.find_child_by_field(node, "type")
        type_discriptor_name = self.parse(type_discriptor, statements)
        # typefield
        field = self.find_child_by_field(node, "member")
        field_discriptor_name = self.parse(field, statements)

        tmp_return = self.tmp_variable()

        self.append_stmts(statements,  node, {"field_addr": {"target": tmp_return, "data_type": type_discriptor_name, "name": field_discriptor_name}})
        return tmp_return

    def generic_expression(self, node, statements):
        type_list = []
        expr_list = []
        children = node.named_children
        variable_descriptor = self.parse(children[0], statements)
        type_list = [self.read_node_text(children[i]) for i in range(len(children)) if i % 2 != 0]
        expr_list = [self.parse(children[i], statements) for i in range(len(children)) if i % 2 == 0 and i != 0]

        tmp_return = self.tmp_variable()
        self.append_stmts(statements,  node, {"switch_type_stmt": {"target": tmp_return, "condition": variable_descriptor, "type_list": type_list, "expr_list": expr_list}})

        return tmp_return

    def conditional_expression(self, node, statements):
        condition = self.find_child_by_field(node, "condition")
        consequence = self.find_child_by_field(node, "consequence")
        alternative = self.find_child_by_field(node, "alternative")

        condition = self.parse(condition, statements)

        then_body = []
        else_body = []
        tmp_var = self.tmp_variable()

        expr1 = self.parse(consequence, then_body)
        then_body.append({"assign_stmt": {"target": tmp_var, "operand": expr1}})

        expr2 = self.parse(alternative, else_body)
        else_body.append({"assign_stmt": {"target": tmp_var, "operand": expr2}})

        self.append_stmts(statements,  node, {"if_stmt": {"condition": condition, "then_body": then_body, "else_body": else_body}})
        return tmp_var

    def compound_literal_expression(self, node, statements):
        # new
        # offsetoftypevalue
        array_list = []

        type_discriptor = self.find_child_by_field(node, "type")
        type_discriptor_name = self.read_node_text(type_discriptor)
        declarators = self.find_children_by_field(type_discriptor, "declarator")
        declarator = type_discriptor
        while child_declarator := self.find_child_by_field(declarator, "declarator"):
            if child_declarator.type == "abstract_array_declarator":
                array_list.append("array")
            declarator = child_declarator

        field = self.find_child_by_field(node, "value")
        tmp_return = self.initializer_list(field, statements, array_list)


        return tmp_return

    def alignof_expression(self, node, statements):
        type_descriptor = self.find_child_by_field(node, "type")
        type_descriptor_name = self.read_node_text(type_descriptor)

        tmp_return = self.tmp_variable()

        self.append_stmts(statements,  node, {"call_stmt": {"target": tmp_return, "name": "alignof", "type_name": type_descriptor_name}})
        return tmp_return

    def gnu_asm_expression(self, node, statements):
        def get_list(target):
            ret = []
            if target:
                if target.named_child_count > 0:
                    for child in target.children:
                        shadow_variable = self.parse(child, statements)
                        if shadow_variable:
                            ret.append(self.read_node_text(child))
            return ret

        assembly_code = self.find_child_by_field(node, "assembly_code")
        shadow_assembly_code = self.parse(assembly_code)

        output_operands = self.find_child_by_field(node, "output_operands")
        output_operands_list = get_list(output_operands)

        input_operands = self.find_child_by_field(node, "input_operands")
        input_operands_list = get_list(input_operands)

        clobbers = self.find_child_by_field(node, "clobbers")
        registers_list = get_list(clobbers)

        goto_labels = self.find_child_by_field(node, "goto_labels")
        labels_list = get_list(goto_labels)

        self.append_stmts(statements,  node, {
            "asm_stmt": {
                "assembly_code": shadow_assembly_code,
                "output_operands": output_operands_list,
                "input_operands": input_operands_list,
                "registers": registers_list,
                "labels": labels_list
            }})

        return 0

    def parenthesized_expression(self, node, statements):
        return self.parse(node.children[1], statements)

    # 
    def is_identifier(self, node):
        return node.type in [
            "identifier",
            "type_identifier",
            "primitive_type",
            "storage_class_specifier",
            "ms_call_modifier",
            "ms_pointer_modifier",
            "type_qualifier",
            "field_identifier",
            "statement_identifier",
        ]

    # 
    def is_literal(self, node):
        return self.obtain_literal_handler(node) is not None

    def literal(self, node, statements, replacement):
        handler = self.obtain_literal_handler(node)
        return handler(node, statements, replacement)

    def obtain_literal_handler(self, node):
        return self.LITERAL_MAP.get(node.type, None)

    # 
    def regular_number_literal(self, node, statements, replacement):
        value = self.read_node_text(node)
        value = self.common_eval(value)
        return str(value)

    def regular_literal(self, node, statements, replacement):
        content = self.read_node_text(node)
        return self.CONSTANTS_MAP.get(content, content)

    def concatenated_string(self, node, statements, replacement):
        #print(node)
        replacement = []
        ret = ""

        for child in node.named_children:
            if child.type == "string_literal":
                parsed = self.parse(child, statements, replacement)
                #print(parsed)
                ret += parsed[1:-1]


        if replacement:
            for r in replacement:
                (expr, value) = r
                ret = ret.replace(self.read_node_text(expr), value)

        ret = self.handle_hex_string(ret)

        return self.escape_string(ret)

    # FIXME: ()
    def string_literal(self, node, statements, replacement):
        return self.read_node_text(node)

    def char_literal(self, node, statements, replacement):
        return self.read_node_text(node)

    # 
    def is_declaration(self, node):
        # return False
        return self.check_declaration_handler(node) is not None

    def declaration(self, node, statements):
        handler = self.check_declaration_handler(node)
        return handler(node, statements)

    def check_declaration_handler(self, node):
        return self.DECLARATION_HANDLER_MAP.get(node.type, None)

    # modifiersmodifiersast
    def search_for_modifiers(self, input_node, modifiers):
        for m in ["storage_class_specifier", "type_qualifier", "attribute_specifier", "attribute_declaration",
                  "ms_declspec_modifier"]:
            ms = self.find_children_by_type(input_node, m)
            for m in ms:
                modifiers.append(self.read_node_text(m))

    def function_declaration(self, node, statements):
        # 
        modifiers = []
        self.search_for_modifiers(node, modifiers)
        func_decl = self.find_child_by_field(node, "declarator")
        if attr_spec := self.find_child_by_type(func_decl, "attribute_specifier"):
            attr_arg_list = self.find_child_by_type(attr_spec, "argument_list")
            if attr_arg_list.named_child_count > 0:
                for a in attr_arg_list.named_children:
                    shadow_a = self.parse(a, statements)
                    modifiers.append(shadow_a)

        # 
        mytype = self.find_child_by_field(node, "type")
        shadow_type = self.read_node_text(mytype)

        # function_declaratorfunc(int a,int b)
        child = self.find_child_by_field(node, "declarator")
        while child.type != "function_declarator":
            # 
            if child.type == "pointer_declarator":
                shadow_type += "*"
                modifiers.append(ENGINE_INTERNAL.POINTER)
            child = self.find_child_by_field(child, "declarator")
        if child.type != "function_declarator":
            util.debug(",function_declarator")
            return
        # function_declaratordeclarator
        name = self.find_child_by_field(child, "declarator")
        shadow_name = self.read_node_text(name)

        all_parameters = []
        # declaratorparameters(int a,int b)
        parameters = self.find_child_by_field(child, "parameters")
        if parameters and parameters.named_child_count > 0:
            for p in parameters.named_children:
                if self.is_comment(p):
                    continue

                # pparameter_declarationinit
                self.parse(p, all_parameters)

        new_body = []
        #self.sync_tmp_variable(new_body, init)
        body = self.find_child_by_field(node, "body")
        self.parse(body, new_body)

        self.append_stmts(statements,  node, {"method_decl": {"attrs": modifiers, "data_type": shadow_type, "name": shadow_name,
                                           "parameters": all_parameters, "body": new_body}})

    # javaformal_parameter
    def parameter_declaration(self, node, statements):
        modifiers = []
        # attrstructunionarraypointerattr
        type_modifiers = []

        # parameter_declarationmodifiers
        self.search_for_modifiers(node, modifiers)

        mytype = self.find_child_by_field(node, "type")
        shadow_type = self.read_node_text(mytype)

        # struct Point p
        if mytype.type == "struct_specifier":
            type_modifiers = ["struct"]
            shadow_type = shadow_type.replace("struct ", "")
        # union Data d
        if mytype.type == "union_specifier":
            type_modifiers = ["union"]
            shadow_type = shadow_type.replace("union ", "")
        # enum Color color
        if mytype.type == "enum_specifier":
            type_modifiers = ["enum"]
            shadow_type = shadow_type.replace("enum ", "")

        # type_declarator
        declarator = self.find_child_by_field(node, "declarator")
        if declarator:
        # declaratordeclarator
            while child_declarator := self.find_child_by_field(declarator, "declarator"):
                # util.debug("--------------------------------declarator" + declarator.type)

                # modifiers
                self.search_for_modifiers(declarator, modifiers)

                # int x[]int x[][]
                if declarator.type == "array_declarator":
                    shadow_type += "[]"
                    # modifiersattr(bug)attrattr
                    type_modifiers = ["array"]

                # int *pint **passignment_expressionread
                if declarator.type == "pointer_declarator":
                    shadow_type += "*"
                    type_modifiers = ["pointer"]

                #  int (*operation)(int, int)
                if declarator.type == "function_declarator":
                    # type
                    shadow_type += self.read_node_text(declarator)
                    type_modifiers = ["pointer"]
                    # 
                    child_declarator = self.find_child_by_field_type(
                        declarator, "declarator", "pointer_declarator")

                declarator = child_declarator

        # declarator
        shadow_name = self.read_node_text(declarator)

        # attrmodifiers
        modifiers.extend(type_modifiers)

        self.append_stmts(statements,  node, {"parameter_decl": {"attrs": modifiers, "data_type": shadow_type, "name": shadow_name}})


    STRUCT_TYPE_MAP = {
        "struct_specifier": "struct",
        "union_specifier": "union"
    }

    # /
    def struct_specifier(self, node, statements):
        gir_node = {}
        gir_node["attrs"] = []

        # StructUnion
        if node.type in self.STRUCT_TYPE_MAP:
            gir_node["attrs"].append(self.STRUCT_TYPE_MAP[node.type])

        self.search_for_modifiers(node, gir_node["attrs"])

        name = self.find_child_by_field(node, "name")
        if name:
            shadow_name = self.read_node_text(name)
        else:
            shadow_name = self.tmp_variable()
        gir_node["name"] = shadow_name

        body = self.find_child_by_field(node, "body")
        if body:
            self.struct_body(body, gir_node)
            #print({f"{self.STRUCT_TYPE_MAP[node.type]}_decl": gir_node})
            self.append_stmts(statements,  node, {f"{self.STRUCT_TYPE_MAP[node.type]}_decl": gir_node})

        return gir_node["name"]

    # body
    def struct_body(self, node, gir_node):
        if field_decls := self.find_children_by_type(node, "field_declaration"):
            gir_node["fields"] = []
            for field_decl in field_decls:
                field_statements = []

                attrs = []
                self.search_for_modifiers(field_decl, attrs)
                # for decl_modifiers in ["storage_class_specifier", "type_qualifier", "attribute_specifier", "attribute_declaration", "ms_declspec_modifier"]:
                #     if modifiers := self.find_children_by_type(field_decl, decl_modifiers):
                #         for m in modifiers:
                #             attrs.append(self.read_node_text(m))

                decl_type = self.find_child_by_field(field_decl, "type")
                if decl_type.type == "struct_specifier":
                    attrs.append("struct")
                elif decl_type.type == "union_specifier":
                    attrs.append("union")
                shadow_decl_type = self.read_node_text(decl_type)

                # function_declaratordeclarator int a,*b;
                declarators = self.find_children_by_field(
                    field_decl, "declarator")
                for declarator in declarators:
                    # pointerarray
                    type_attr = []
                    shadow_decl_type_copy = shadow_decl_type
                    attr_copy = attrs.copy()

                    while child_declarator := self.find_child_by_field(declarator, "declarator"):
                        if declarator.type == "pointer_declarator":
                            shadow_decl_type_copy += "*"
                            # type_attr
                            type_attr = ["pointer"]
                        if declarator.type == "array_declarator":
                            # 
                            if type_attr != ["array"]:
                                # 
                                array_size = re.sub(
                                    r'^\w+', '', self.read_node_text(declarator))
                                shadow_decl_type_copy += array_size
                                type_attr = ["array"]

                        # declarator
                        declarator = child_declarator

                    # declaratorfield_identifier
                    shadow_declarator = self.read_node_text(declarator)

                    attr_copy.extend(type_attr)
                    # (attr)attr_copyC
                    self.append_stmts(field_statements,  node, {"variable_decl" :
                                             {"attrs": attr_copy,
                                              "data_type": shadow_decl_type_copy,
                                              "name": shadow_declarator}})


                gir_node["fields"].extend(field_statements)

    def struct_array(self, node, struct_name, statements):
        tmp_var = self.tmp_variable()
        self.append_stmts(statements,  node, {"new_array" : {"data_type": struct_name,
                                          "target": tmp_var}})
        #print(node)
        index = 0
        for child_list in node.children:
            #struct
            if child_list.type == "initializer_list":
                tmp_struct = self.tmp_variable()
                child_count = child_list.named_child_count
                self.append_stmts(statements,  node, {"new_struct":{"data_type" :struct_name, "target":tmp_struct}})
                for index in range(child_count):
                    value = self.parse(child_list.named_child(index), statements)
                    self.append_stmts(statements,  node, {"field_write" :
                                       {"receiver_object" : tmp_struct,
                                        "field" : "not found yet",
                                        "source" : value}})
                self.append_stmts(statements,  node, {"array_write":
                                   {"array" : tmp_var,
                                    "source" : tmp_struct,
                                    "index" : str(index)}})
            index = index + 1

    def initializer_list(self, node, statements, array_list):
        tmp_var = self.tmp_variable()
        is_array = True
        data_type = ""
        if len(array_list) != 0 and array_list[-1] != "array":
            data_type = array_list[-1]
            array_list.pop()
        if len(array_list) != 0 and array_list[0] == "array":
            self.append_stmts(statements,  node, {"new_array" : { "data_type" : data_type, "target": tmp_var}})
            array_list.pop()
        else:
            self.append_stmts(statements,  node, {"new_struct": { "data_type" : data_type, "target":tmp_var}})
            is_array = False
        index = 0
        for child_list in node.children:
            if child_list.type == "initializer_list":
                result = self.initializer_list(child_list, statements, array_list)

                if is_array:
                    self.append_stmts(statements,  node, {"array_write":
                                       {"array" : tmp_var,
                                        "source" : result,
                                        "index" : str(index)}})
                else:
                    self.append_stmts(statements,  node, {"field_write" :
                                       {"receiver_object" : tmp_var,
                                        "field" : str(index),
                                        "source" : result}})
                index = index + 1

            elif child_list.type == "initializer_pair":
                designator = self.find_child_by_field(child_list, "designator")
                value = self.find_child_by_field(child_list, "value")
                value = self.parse(value, statements)
                shadow_designator= self.parse(designator,[])
                self.append_stmts(statements,  node, {"field_write" :
                                   {"receiver_object" : tmp_var,
                                    "field" : shadow_designator,
                                    "source" : value}})

            else:
                value = self.parse(child_list, statements)
                if value:
                    if is_array:
                        self.append_stmts(statements,  node, {"array_write":
                                           {"array" : tmp_var,
                                            "source" : value,
                                            "index" : str(index)}})
                    else:
                        self.append_stmts(statements,  node, {"field_write" :
                                           {"receiver_object" : tmp_var,
                                            "field" : str(index),
                                            "source" : value}})
                    index = index + 1

        return tmp_var

    def type_definition(self, node, statements):
        mytype = self.find_child_by_field(node, "type")
        source_type = self.read_node_text(mytype)
        declarators = self.find_child_by_field(node, "declarator")
        target = self.read_node_text(declarators)
        while child_declarator := self.find_child_by_field(declarators, "declarator"):
            declarators = child_declarator
            target = self.read_node_text(child_declarator)
            #print(f"typedef{source_type}")
            #print({"type_alias_decl" : {"target" : target, "source" : source_type}})
            self.append_stmts(statements,  node, {"type_alias_decl" : {"name" : target, "data_type" : source_type}})

    def internal_struct_init(self, node, statements, value, mytype, struct_name):
        struct_or_union = "struct" if mytype.type == "struct_specifier" else "union"
        # statements
        tmp_var_id = self.tmp_variable()

        self.append_stmts(statements,  node, {"new_struct" :{"data_type" :struct_name, "target" : tmp_var_id}})
        # stru = {.field1 = value1,.field2 = value2}
        initializer_pairs = self.find_children_by_type(value,"initializer_pair")
        if initializer_pairs:
            for initializer_pair in initializer_pairs:
                designator = self.find_child_by_field(initializer_pair,"designator")
                init_value = self.find_child_by_field(initializer_pair,"value")
                shadow_designator= self.parse(designator,[])
                shadow_init_value = self.parse(init_value,statements)
                self.append_stmts(statements,  node, {"field_write":
                            {"receiver_object": tmp_var_id, "field": shadow_designator, "source": shadow_init_value}})

        else:
            for stmt in statements:
                if f"{struct_or_union}_decl" in stmt and stmt[f"{struct_or_union}_decl"]["name"] == struct_name.split(' ')[0]:
                    members = stmt[f"{struct_or_union}_decl"]["fields"]
                    # 
                    if len(members) < value.named_child_count:
                        util.debug(f"{struct_name}{len(members)}",
                                   "{value.named_child_count}")
                        continue

                    value_number = value.named_child_count
                    for field_index,field_member_list in enumerate(members):
                        if value_number == 0:
                            continue
                        # field_member_list
                        field_member = field_member_list[0]
                        # util.debug(f"field_index: {field_index} , field_member: {field_member}")
                        if any("variable_decl" in member for member in field_member):
                            field_name = field_member["variable_decl"]["name"]
                            field_value = self.parse(value.named_child(field_index), statements)
                            self.append_stmts(statements,  node, {"field_write":
                                                    {"receiver_object": tmp_var_id, "field": field_name,
                                                    "source": field_value}})
                            value_number = value_number - 1
                    break  # struct
                else:
                    util.debug(f"ERROR========={struct_or_union}{struct_or_union}")
        return tmp_var_id

    def array_declaration(self, node, statements, value, modifiers, shadow_type):
        middle_result = None
        array_node = node
        array_dimensions = []
        #
        #
        if value and value.type == "initializer_list" and value.named_child_count > 0:
            element = []
            times = 0
            def recursive_search_element(n):
                for child in n.children:
                    if child.type == "initializer_list":
                        recursive_search_element(child)
                    else:
                        child = self.parse(child, statements)
                        if child is not None:
                            element.append(child)
            recursive_search_element(value)
            middle_result = element
        #
        tmp_value = value

        while True:
            #  size
            if value:
                size = len(middle_result)
                array_dimensions.append(size)
                tmp_value = self.find_child_by_type(tmp_value, "initializer_list")
                if tmp_value is None:
                    break
                continue  # size
            else:
                size = self.find_child_by_field(array_node, "size")
                size = 1
                array_dimensions.append(size)
                """ if size:
                    size = int(self.read_node_text(size))
                    array_dimensions.append(size) """
                array_node = self.find_child_by_type(array_node, "array_declarator")
                if array_node is None:
                    # size
                    array_dimensions.reverse()
                    break

        array_dimensions_len = len(array_dimensions)

        for current_dim_index in range(array_dimensions_len):  # current_dim_index 0~len-1
            inner_array_create_count = 1

            # 
            for e in array_dimensions[:array_dimensions_len - 1 - current_dim_index]:
                inner_array_create_count *= e
            # util.debug(f"{current_dim_index}{inner_array_create_count}")

            new_middle_result = []  # middle_result

            # 
            for array_create_id in range(inner_array_create_count):
                inner_array_tmp_var = self.tmp_variable()
                self.append_stmts(statements,  node, {"new_array": {"attrs": modifiers, "data_type": shadow_type,
                                                    "target": inner_array_tmp_var}})
                # 
                if value:
                    index = 0
                    current_arr_size = array_dimensions[-(current_dim_index + 1)]  # -1
                    for i in range(current_arr_size):
                        self.append_stmts(statements,  node, {"array_write": {"array": inner_array_tmp_var,
                                                            "index": str(index), "source": middle_result[
                                current_arr_size * array_create_id + i]}})
                        index += 1
                    # 
                    new_middle_result.append(inner_array_tmp_var)

            middle_result = new_middle_result
            shadow_type = f"{shadow_type}[]"
        shadow_value = inner_array_tmp_var
        return shadow_value
    # 
    def variable_declaration(self, node, statements):

        modifiers = []
        self.search_for_modifiers(node, modifiers)
        mytype = self.find_child_by_field(node, "type")
        shadow_mytype = self.read_node_text(mytype)
        self.search_for_modifiers(mytype,modifiers)

         # 
        if mytype.type == "enum_specifier":
            enum_name = self.enum_declaration(mytype, statements)
            shadow_mytype = enum_name
        # 
        elif mytype.type in ["struct_specifier","union_specifier"]:
            struct_name = self.struct_specifier(mytype,statements)
            shadow_mytype = struct_name

        declarators = self.find_children_by_field(node, "declarator")
        for declarator in declarators:
            shadow_type = shadow_mytype
            shadow_value = None
            has_init = False
            value = self.find_child_by_field(declarator, "value")
            if value != None and value.type == "compound_literal_expression":
                value = self.find_child_by_field(value, "value")
            #declarator
            array_list = []
            while child_declarator := self.find_child_by_field(declarator, "declarator"):
                if declarator.type == "array_declarator":
                    has_init = True
                    array_list.append("array")
                elif declarator.type == "function_declarator":
                    return
                elif declarator.type == "pointer_declarator":
                    shadow_type += '*'
                #search_for_modifier,attr
                declarator = child_declarator
            array_list.append(shadow_type)
            if value is None:
                pass
            elif value.type == "initializer_list":
                has_init = True
                shadow_value = self.initializer_list(value, statements, array_list)
            else:
                has_init = True
                shadow_value = self.parse(value, statements)
            name = self.read_node_text(declarator)

            self.append_stmts(statements,  node, {"variable_decl":
                               {"attrs": modifiers,
                                "data_type": shadow_type,
                                "name": name}})
            if has_init:
                if value and (value.type == "number_literal" or value.type == "char_literal"):
                    value = self.parse(value, statements)
                    self.append_stmts(statements,  node, {"assign_stmt":
                                   {"target": name,
                                    "operand": value,
                                    "data_type": shadow_type}})
                else:
                    self.append_stmts(statements,  node, {"assign_stmt":
                                    {"target": name,
                                        "operand": shadow_value,
                                        "data_type": shadow_type}})


    def enum_declaration(self, node, statements):
        # 
        child_node = ["name", "underlying_type"]
        children = {}
        attrs = []
        enum_constants = []
        for cn in child_node:
            child = self.find_child_by_field(node, cn)
            if child:
                shadow_child = f"shadow_{cn}"
                # util.debug(f"enum_declaration----{self.read_node_text(child)}")
                children[shadow_child] = self.parse(child, statements)
        if children.get("shadow_underlying_type"):
            attrs.append(children["shadow_underlying_type"])
        # optional($.attribute_specifier),
        if attribute_specifier := self.find_child_by_type(node, "attribute_specifier"):
            attrs.append(self.read_node_text(attribute_specifier))
        name = children["shadow_name"] if children.get("shadow_name") else self.tmp_variable()

        # 
        body = self.find_child_by_field(node, "body")
        # body
        if body:
            self.enum_body(body, enum_constants)
            self.append_stmts(statements,  node, {"enum_decl": {"name": name, "attrs": attrs, "enum_constants": enum_constants}})
        return f"name"

    def enum_body(self, node, enum_constants_list):
        enumerator_children = self.find_children_by_type(node, "enumerator")
        for enumerator in enumerator_children:
            name = self.find_child_by_field(enumerator, "name")
            value = self.find_child_by_field(enumerator, "value")
            shadow_name = self.read_node_text(name)
            shadow_value = self.parse(value, list) if value else ""
            enum_constants_list.append({"enum_constant": {"name": shadow_name, "value": shadow_value}})

    # ----------------------------------------------------------------------------

    # 
    def is_statement(self, node):
        return self.check_statement_handler(node) is not None

    def statement(self, node, statements):
        handler = self.check_statement_handler(node)
        return handler(node, statements)

    def check_statement_handler(self, node):
        return self.STATEMENT_HANDLER_MAP.get(node.type, None)

    def return_statement(self, node, statements):
        shadow_name = ""
        if node.named_child_count > 0:
            name = node.named_children[0]
            shadow_name = self.parse(name, statements)

        self.append_stmts(statements,  node, {"return_stmt": {"name": shadow_name}})
        return shadow_name

    def if_statement(self, node, statements):
        condition_part = self.find_child_by_field(node, "condition")
        # ifthen
        true_part = self.find_child_by_field(node, "consequence")
        # ifelseelse if
        false_part = self.find_child_by_field(node, "alternative")

        true_body = []
        #self.sync_tmp_variable(statements, true_body)
        false_body = []
        #self.sync_tmp_variable(statements, false_body)

        shadow_condition = self.parse(condition_part, statements)
        self.parse(true_part, true_body)
        self.parse(false_part, false_body)

        self.append_stmts(statements,  node, {"if_stmt": {"condition": shadow_condition, "then_body": true_body, "else_body": false_body}})

    def while_statement(self, node, statements):
        condition = self.find_child_by_field(node, "condition")
        body = self.find_child_by_field(node, "body")

        new_condition_init = []

        #self.sync_tmp_variable(new_condition_init, statements)
        shadow_condition = self.parse(condition, new_condition_init)

        new_while_body = []
        #self.sync_tmp_variable(new_while_body, statements)
        self.parse(body, new_while_body)

        #statements.extend(new_condition_init)
        #new_while_body.extend(new_condition_init)

        self.append_stmts(statements,  node, {"while_stmt": {
            "condition": shadow_condition, "condition_prebody": new_condition_init, "body": new_while_body
        }})

    def for_statement(self, node, statements):
        init_children = self.find_children_by_field(node, "initializer")
        step_children = self.find_children_by_field(node, "update")

        condition = self.find_child_by_field(node, "condition")

        init_body = []
        condition_init = []
        step_body = []

        #self.sync_tmp_variable(init_body, statements)
        #self.sync_tmp_variable(condition_init, statements)
        #self.sync_tmp_variable(step_body, statements)

        shadow_condition = self.parse(condition, condition_init)
        for child in init_children:
            # FIXME: Cdeclaration
            self.parse(child, init_body)

        for child in step_children:
            self.parse(child, step_body)

        for_body = []
        #self.sync_tmp_variable(for_body, statements)

        body_compound = self.find_child_by_field(node, "body")
        self.parse(body_compound, for_body)

        self.append_stmts(statements,  node, {"for_stmt":
                               {"init_body": init_body,
                                "condition": shadow_condition,
                                "condition_prebody": condition_init,
                                "update_body": step_body,
                                "body": for_body}})

    def switch_statement(self, node, statements):
        # returnswitch_return
        switch_ret = self.tmp_variable()

        switch_body = self.find_child_by_field(node, "body")
        condition = self.find_child_by_field(node, "condition")
        shadow_condition = self.parse(condition, statements)

        case_stmt_list = []
        #self.sync_tmp_variable(statements, case_stmt_list)
        self.append_stmts(statements,  node, {"switch_stmt": {"condition": shadow_condition, "body": case_stmt_list}})

        # case_statementccase
        for case in switch_body.named_children:
            # util.debug(f"nnnnnnnnnnn----case.children[0]_text is : {self.read_node_text(case.children[0])}")  # case or default

            if case.type == "comment":
                continue
            if self.read_node_text(case.children[0]) == "case":
                label = self.find_child_by_field(case, "value")
                case_init = []
                #self.sync_tmp_variable(statements, case_init)
                shadow_label = self.parse(label, case_init)
                if case_init != []:
                    statements.insert(-1, case_init)

                    # for c in case.children:
                    #     util.debug(self.read_node_text(c)+"///")
                    '''
                    case///
                    2///
                    :///
                    c = 4;///
                    break;///
                    '''

                # case statement
                if label == case.named_children[-1]:
                    case_stmt_list.append({"case_stmt": {"condition": shadow_label}})

                # 
                else:
                    new_body = []
                    #self.sync_tmp_variable(statements, new_body)
                    # 
                    for stmt in case.named_children[1:]:
                        self.parse(stmt, new_body)
                    case_stmt_list.append({"case_stmt": {"condition": shadow_label, "body": new_body}})


            # default
            elif self.read_node_text(case.children[0]) == "default":
                new_body = []
                #self.sync_tmp_variable(statements, new_body)
                # 
                for stmt in case.named_children:
                    self.parse(stmt, new_body)
                case_stmt_list.append({"default_stmt": {"body": new_body}})

        return switch_ret  # ?

    def dowhile_statement(self, node, statements):
        body = self.find_child_by_field(node, "body")
        condition = self.find_child_by_field(node, "condition")

        do_body = []
        #self.sync_tmp_variable(do_body, statements)
        self.parse(body, do_body)
        condition_body = []
        shadow_condition = self.parse(condition, condition_body)

        self.append_stmts(statements, node, {"dowhile_stmt": {
            "body": do_body, "condition_prebody": condition_body, "condition": shadow_condition
        }})

    def break_statement(self, node, statements):
        self.append_stmts(statements,  node, {"break_stmt": {}})

    def continue_statement(self, node, statements):
        self.append_stmts(statements,  node, {"continue_stmt": {}})

    def goto_statement(self, node, statements):
        label = self.find_child_by_field(node, "label")
        label_text = self.read_node_text(label)
        self.append_stmts(statements,  node, {"goto_stmt": {"name": label_text}})

    def label_statement(self, node, statements):
        label = self.find_child_by_field(node, "label")
        shadow_label = self.read_node_text(label)
        self.append_stmts(statements,  node, {"label_stmt": {"name": shadow_label}})

        if node.named_child_count > 1:
            stmt = node.named_children[1]
            self.parse(stmt, statements)

    def attributed_statement(self, node, statements):
        # attributed_statement = "attribute_declaration"* statement
        # attr_decls = []
        # for child in node.named_children:
        #     if child.type == "attribute_declaration":
        #         self.parse(child, attr_decls)
        #     else: # attr_declstatememtattr_decl
        #         self.append_stmts(statements,  node, {"attributed_stmt": attr_decls})
        #         self.parse(child, statements)
        return ""

    def case_statement(self, node, statements):
        # case_statement = "case" "(" expression ")" statement ("default" statement)?

        body = []
        if self.read_node_text(node.children[0]) == "default":
            for child in node.named_children:
                self.parse(child, body)
            self.append_stmts(statements,  node, {"default_stmt": {"body": body}})
        else:
            value = self.find_child_by_field(node, "value")
            shadow_value = self.parse(value, statements)
            for child in node.named_children[1:]:
                self.parse(child, body)
            self.append_stmts(statements,  node, {"case_stmt": {"condition": shadow_value, "body": body}})

        return 0

    def seh_try_statement(self, node, statements):
        try_op = {}

        body = self.find_child_by_field(node, "body")
        try_body = []
        self.parse(body, try_body)
        try_op["body"] = try_body

        except_clause = self.find_child_by_type(node, "seh_except_clause")
        if except_clause:
            filter = self.find_child_by_field(except_clause, "filter")
            shadow_filter = self.parse(filter, statements)
            body = self.find_child_by_field(except_clause, "body")
            shadow_body = []
            self.parse(body, shadow_body)
            try_op["except_clause"] = [{"filter": shadow_filter, "body": shadow_body}]
        else:
            finally_clause = self.find_child_by_type(node, "seh_finally_clause")
            body = self.find_child_by_field(finally_clause, "body")
            shadow_body = []
            self.parse(body, shadow_body)
            try_op["finally_clause"] = [{"body": shadow_body}]

        self.append_stmts(statements,  node, {"try_stmt": try_op})

        return 0

    def seh_leave_statement(self, node, statements):
        # self.append_stmts(statements,  node, {"leave_stmt": {}})
        return 0
    # ----------------------------------------------------------------------------

    def is_comment(self, node):
        # // printf("//xxxx")
        if self.read_node_text(node).startswith("//"):
            return True
        return False
