#!/usr/bin/env python3

import re
import ast
import sys

from tree_sitter import Node
from engine.util import util

from engine.config.constants import ENGINE_INTERNAL

class Parser:
    def __init__(self, options, unit_info):
        """
        
        1. //
        2. 
        3. 
        4. 
        """
        self.tmp_variable_id = 0
        self.method_id = 0
        self.class_id = 0
        self.options = options
        self.printed_flag = False
        self.unit_info = unit_info
        self.unit_path = unit_info.original_path

        # self.CONSTANTS_MAP = {
        #     "None"                          : EngineInternal.NULL,
        #     "none"                          : EngineInternal.NULL,
        #     "NONE"                          : EngineInternal.NULL,
        #     "NULL"                          : EngineInternal.NULL,
        #     "Null"                          : EngineInternal.NULL,
        #     "null"                          : EngineInternal.NULL,

        #     "true"                          : EngineInternal.TRUE,
        #     "True"                          : EngineInternal.TRUE,
        #     "TRUE"                          : EngineInternal.TRUE,

        #     "false"                         : EngineInternal.FALSE,
        #     "False"                         : EngineInternal.FALSE,
        #     "FALSE"                         : EngineInternal.FALSE,

        #     "undef"                         : EngineInternal.UNDEFINED,
        #     "undefine"                      : EngineInternal.UNDEFINED,
        #     "undefined"                     : EngineInternal.UNDEFINED,
        # }

        self.init()

    def init(self):
        pass

    def syntax_error(self, node: Node, msg: str):
        sys.stderr.write(
            f"Syntax Error: {msg}\n\n"
            f"--> {self.unit_path}:{node.start_point.row + 1}:{node.start_point.column}\n"
            f"      {self.read_node_text(node)}\n"
        )
        sys.exit(-1)

    def create_empty_node_with_init_list(self, *names):
        node = {}
        for each_name in names:
            node[each_name] = []
        return node

    def tmp_variable(self):
        self.tmp_variable_id += 1
        return ENGINE_INTERNAL.VARIABLE_DECL_PREF + str(self.tmp_variable_id)

    def default_value_variable(self):
        self.tmp_variable_id += 1
        return ENGINE_INTERNAL.DEFAULT_VALUE_PREF + str(self.tmp_variable_id)

    def tmp_method(self):
        self.method_id += 1
        return ENGINE_INTERNAL.METHOD_DECL_PREF + str(self.method_id)

    def tmp_class(self):
        self.class_id += 1
        return ENGINE_INTERNAL.CLASS_DECL_PREF + str(self.class_id)

    def append_stmts(self, stmts, node, content):
        if node:
            stmts.append(self.add_col_row_info(node, content))
        else:
            stmts.append(content)

    def handle_hex_string(self, input_string):
        """
        
        1. xHH
        2. UTF-8
        3. 
        """
        if self.is_hex_string(input_string):
            try:
                tmp_str = input_string.replace('\\x', "")
                tmp_str = bytes.fromhex(tmp_str).decode('utf8')
                return tmp_str
            except:
                pass

        return input_string

    def is_hex_string(self, input_string):
        if not input_string:
            return False
        # Check if the string is in the format "\\xHH" where HH is a hexadecimal value
        return len(input_string) % 4 == 0 and bool(re.match(r'^(\\x([0-9a-fA-F]{2}))+$', input_string))

    def is_string(self, input_string):
        """
        
        
        - 
        - /
        """
        if input_string is None:
            return False

        if not isinstance(input_string, str):
            return False

        return input_string[0] in ['"', "'"]

    def common_eval(self, input_string):
        """
        
        Python
        """
        try:
            return str(util.strict_eval(input_string))
        except:
            pass
        return input_string

    def escape_string(self, input_string):
        """
        
        1. 
        2. 
        3. /
        """
        if not input_string:
            return input_string

        if not isinstance(input_string, str):
            return input_string

        input_string = input_string.replace("'''", "")
        input_string = input_string.replace('"""', '')

        if len(input_string) == 0:
            return input_string

        if input_string[0] != '"' and input_string[0] != "'":
            ret_val = f'"{input_string}"'
            return ret_val
        return input_string

    def global_this(self):
        return ENGINE_INTERNAL.THIS

    def global_self(self):
        return ENGINE_INTERNAL.THIS

    def current_class(self):
        return ENGINE_INTERNAL.CLASS

    def global_super(self):
        return ENGINE_INTERNAL.SUPER

    def global_parent(self):
        return ENGINE_INTERNAL.PARENT

    def is_literal(self, node):
        return node.endswith("literal")

    def find_children_by_type(self, input_node, input_type):
        """
        
        """
        ret = []
        for child in input_node.named_children:
            if child.type == input_type:
                ret.append(child)
        return ret

    def find_child_by_type(self, input_node, input_type):
        """
        
        """
        for child in input_node.named_children:
            if child.type == input_type:
                return child

    def find_children_by_field(self, input_node, input_field):
        return input_node.children_by_field_name(input_field)

    def find_child_by_field(self, input_node, input_field):
        return input_node.child_by_field_name(input_field)

    def find_child_by_type_type(self, input_node, input_type, input_type2):
        node = self.find_child_by_type(input_node, input_type)
        if node:
            return self.find_child_by_type(node, input_type2)

    def find_child_by_field_type(self, input_node, input_field, input_type):
        """
        
        """
        node = self.find_child_by_field(input_node, input_field)
        if node:
            return self.find_child_by_type(node, input_type)

    def find_child_by_type_field(self, input_node, input_type, input_field):
        """
        
        """
        node = self.find_child_by_type(input_node, input_type)
        if node:
            return self.find_child_by_field(node, input_field)

    def find_child_by_field_field(self, input_node, input_field, input_field2):
        """
        
        1. 
        2. 
        """
        node = self.find_child_by_field(input_node, input_field)
        if node:
            return self.find_child_by_field(node, input_field2)

    def read_node_text(self, input_node):
        """
        
        UTF-8
        """
        if not input_node:
            return ""
        return str(input_node.text, 'utf8')

    def print_tree(self, node, level=0, field = None):
        """
        AST
        """
        if not node:
            return
        if field:
            print("   "*level + field, "-", node.type + f":{node.start_point.row+1}" + f"({node.text[:10]})")
        else:
            print("   "*level + node.type + f":{node.start_point.row+1}" + f"({node.text[:10]})")
        children = node.children
        for index, child in enumerate(children):
            if child.is_named:
                child_field = node.field_name_for_child(index)
                if child_field:
                    self.print_tree(child, level + 1, child_field)
                else:
                    self.print_tree(child, level + 1)

    def add_col_row_info(self, node, gir_dict):
        """
        
        """
        if node:
            start_line, start_col = node.start_point
            end_line, end_col = node.end_point
            first_key = next(iter(gir_dict))
            gir_dict[first_key]["start_row"] = start_line
            gir_dict[first_key]["start_col"] = start_col
            gir_dict[first_key]["end_row"] = end_line
            gir_dict[first_key]["end_col"] = end_col
        return gir_dict

    def parse(self, node, statements=[], replacement=[]):
        """
        
        
        1. AST
        2. 
        3. 
        4. 
           - 
           - 
           - 
           - 
           - 
        5. 
        """
        #self.print_tree(node)
        if self.options.debug and self.options.print_stmts and not self.printed_flag:
            self.print_tree(node)
            self.printed_flag = True

        if not node:
            return ""

        if self.is_comment(node):
            return

        if self.is_identifier(node):
            return self.read_node_text(node)

        if self.is_literal(node):
            result = self.literal(node, statements, replacement)
            if result is None:
                return self.read_node_text(node)
            return result

        if self.is_declaration(node):
            return self.declaration(node, statements)

        if self.is_statement(node):
            return self.statement(node, statements)

        if self.is_expression(node):
            return self.expression(node, statements)

        size = len(node.named_children)
        for i in range(size):
            ret = self.parse(node.named_children[i], statements, replacement)
            if node.type == "parenthesized_expression":
                return ret
            if i + 1 == size:
                return ret

    def start_parse(self, node, statements):
        pass

    def end_parse(self, node, statements):
        pass

    def validate_ast_tree(self, node):
        if node.type == 'ERROR':
            self.syntax_error(node, f"Found an error AST node in code ({self.read_node_text(node)[:40]})")

        for child in node.named_children:
            self.validate_ast_tree(child)

    def parse_gir(self, node, statements):
        #self.print_tree(node)

        if self.options.strict_parse_mode:
            self.validate_ast_tree(node)

        replacement = []
        self.start_parse(node, statements)
        self.parse(node, statements, replacement)
        self.end_parse(node, statements)
