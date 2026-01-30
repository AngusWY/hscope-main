#!/usr/bin/env python3

from pathlib import Path
import os,sys
import pprint
from ctypes import c_void_p, cdll
import tree_sitter
import importlib
from engine.events.event_manager import EventManager
from engine.util import util
from engine.config import lang_config
from engine.config import config
from engine.config.constants import EVENT_KIND

from engine.events.handler_template import EventData
from engine.util.loader import Loader

from code_preprocessor import prepare_code

EXTENSIONS_LANG = lang_config.EXTENSIONS_LANG

def determine_lang_by_path(file_path):
    ext = os.path.splitext(file_path)[1]
    return EXTENSIONS_LANG.get(ext, None)

@profile
def is_empty_strict_version(node):
    """
    
    1. /
    2. 
    3. True
    """
    if not node:
        return True

    if isinstance(node, list) or isinstance(node, set):
        for child in node:
            if not is_empty(child):
                return False
        return True

    elif isinstance(node, dict):
        for myvalue in node.values():
            if not is_empty(myvalue):
                return False
        return True

    return False

def is_empty(node):
    """
    
    1. 
    2. 
    """
    if not node:
        return True

    if isinstance(node, list) or isinstance(node, set):
        for child in node:
            if not is_empty(child):
                return False
        return True

    elif isinstance(node, dict):
        if len(node) > 0:
            return False
        return True

    return False


class GIRProcessing:
    def __init__(self, node_id):
        self.node_id = node_id

    def assign_id(self):
        """
        ID
        1. 
        2. ID
        """
        previous = self.node_id
        self.node_id += 1
        return previous

    def get_id_from_node(self, node):
        """
        ID
        1. stmt_id
        2. assign_idID
        """
        if "stmt_id" not in node:
            node["stmt_id"] = self.assign_id()
        return node["stmt_id"]

    def init_stmt_id(self, stmt, parent_stmt_id):
        stmt["parent_stmt_id"] = parent_stmt_id
        stmt["stmt_id"] = self.assign_id()

    def is_gir_format(self, stmts):
        """
        GIR
        1. 
        2. 
        """
        if stmts and isinstance(stmts, list) and len(stmts) > 0 \
           and stmts[0] and isinstance(stmts[0], dict):
            return True

        return False

    def flatten_stmt(self, stmt, last_node: dict, dataframe, parent_stmt_id = 0):
        """
        
        1. 
        2. from
        3. 
        4. 
        """
        if not isinstance(stmt, dict):
            util.error("[Input format error] The input node should not be a dictionary: " + str(stmt))
            return

        flattened_node = {}
        dataframe.append(flattened_node)

        flattened_node["operation"] = list(stmt.keys())[0]
        stmt_content = stmt[flattened_node["operation"]]

        self.init_stmt_id(flattened_node, parent_stmt_id)

        if flattened_node["operation"] == "assign_stmt" and "operation" in last_node and last_node["operation"] == "variable_decl":
            last_node["from"] = flattened_node["stmt_id"]

        if not isinstance(stmt_content, dict):
            return

        for mykey, myvalue in stmt_content.items():
            if isinstance(myvalue, list):
                if not self.is_gir_format(myvalue):
                    if myvalue == []:
                        flattened_node[mykey] = None
                    else:
                        flattened_node[mykey] = str(myvalue)
                else:
                    block_id = self.flatten_block(myvalue, flattened_node["stmt_id"], dataframe)
                    flattened_node[mykey] = block_id

            elif isinstance(myvalue, dict):
                util.error_and_quit("[Input format error] Dictionary is not allowed: " + str(myvalue))
                continue
            else:
                flattened_node[mykey] = myvalue

        return flattened_node

    def flatten_block(self, block, parent_stmt_id, dataframe: list):
        """
        
        1. 
        2. 
        3. 
        4. ID
        """
        block_id = self.assign_id()
        dataframe.append({"operation": "block_start", "stmt_id": block_id, "parent_stmt_id": parent_stmt_id})
        last_node = {}
        for child in block:
            last_node = self.flatten_stmt(child, last_node, dataframe, block_id)

        dataframe.append({"operation": "block_end", "stmt_id": block_id, "parent_stmt_id": parent_stmt_id})
        return block_id

    def flatten_gir(self, stmts):
        """
        GIR
        1. 
        2. 
        3. 
        """
        flattened_nodes = []
        last_node = {}
        for stmt in stmts:
            last_node = self.flatten_stmt(stmt, last_node, flattened_nodes)

        return flattened_nodes

    def flatten(self, stmts):
        """
        GIR
        1. 
        2. flatten_gir
        3. ID
        """

        if not self.is_gir_format(stmts):
            util.error_and_quit("The input fromat of GLang IR is not correct.")
            return
        flattened_nodes = self.flatten_gir(stmts)
        return (self.node_id, flattened_nodes)

class GIRParser:
    def __init__(self, options, app_manager, loader, output_path):
        self.options = options
        self.app_manager = app_manager
        self.loader = loader

        self.accumulated_rows = []
        self.output_path = output_path
        self.max_rows = config.MAX_ROWS
        self.count = 0
        self.ananymous_func_to_scope = {}
    def parse(self, unit_info, file_path, lang_option, lang_table):
        """
        GIR
        1. 
        2. Tree-sitterAST
        3. parserGIR
        """
        if lang_option is None:
            return

        lang = None
        for language in lang_table:
            if language.name == lang_option:
                lang = language
                break

        if not lang:
            util.error_and_quit("Unsupported language: " + self.options.lang)

        lib = cdll.LoadLibrary(lang.so_path)
        lang_function = getattr(lib, "tree_sitter_%s" % lang_option)
        lang_function.restype = c_void_p
        lang_id = lang_function()
        lang_inter = tree_sitter.Language(lang_id)
        tree_sitter_parser = tree_sitter.Parser(lang_inter)

        code = None
        tree = None
        try:
            with open(file_path, 'r') as f:
                code = f.read()
        except:
            util.error("Failed to read file:", file_path)
            return

        if util.is_empty(code):
            return

        if f"{config.DEFAULT_WORKSPACE}/{config.EXTERNS_DIR}" in file_path:
            event = EventData(lang_option, EVENT_KIND.MOCK_SOURCE_CODE_READY, code)
            self.app_manager.notify(event)
            code = event.out_data

        event = EventData(lang_option, EVENT_KIND.ORIGINAL_SOURCE_CODE_READY, code)
        self.app_manager.notify(event)
        try:
            tree = tree_sitter_parser.parse(bytes(event.out_data, 'utf8'))
        except:
            util.error("Failed to parse AST:", file_path)
            return

        gir_statements = []
        parser = lang.parser(self.options, unit_info)
        parser.parse(tree.root_node, gir_statements)
        self.ananymous_func_to_scope = parser.ananymous_func_to_scope
        return gir_statements

    def deal_with_file_unit(self, current_node_id, unit_info, file_unit, lang_table):
        """
        
        1. 
        2. GIR
        3. 
        4. 
        """
        lang_option = determine_lang_by_path(file_unit)

        if self.options.debug:
            util.debug("GIR-Parsing:", file_unit)

        gir_statements = self.parse(unit_info, file_unit, lang_option, lang_table = lang_table)
        if not gir_statements:
            return (current_node_id, None)
        # if self.options.debug and self.options.print_stmts:
        #     pprint.pprint(gir_statements, compact=True, sort_dicts=False)
        event = EventData(lang_option, EVENT_KIND.UNFLATTENED_GIR_LIST_GENERATED, gir_statements)
        self.app_manager.notify(event)
        code = event.out_data
        code = prepare_code(self.ananymous_func_to_scope).run(code)
        # pprint.pprint(code)

        current_node_id, flatten_nodes = GIRProcessing(current_node_id).flatten(code)
        if not flatten_nodes:
            return (current_node_id, flatten_nodes)

        event = EventData(lang_option, EVENT_KIND.GIR_LIST_GENERATED, flatten_nodes)
        self.app_manager.notify(event)
        # if self.options.debug and self.options.print_stmts:
        #     pprint.pprint(event.out_data, compact=True, sort_dicts=False)
        flatten_nodes = prepare_code().find_lex_var(event.out_data)
        #  ComponentStructBuilder().build(flatten_nodes)
        return (current_node_id, flatten_nodes)

    @profile
    def add_unit_gir(self, unit_info, flatten_nodes):
        """
        GIR
        1. ID
        2. 
        """
        if is_empty(flatten_nodes):
            return

        unit_id = unit_info.module_id
        for node in flatten_nodes:
            node["unit_id"] = unit_id
        self.loader.save_unit_gir(unit_id, flatten_nodes)

    def export(self):
        self.loader.export_gir()

class LangAnalysis:
    def __init__(self, engine):
        self.options = engine.options
        self.app_manager: EventManager = engine.event_manager
        self.loader: Loader = engine.loader
        self.lang_table = engine.lang_table

    def init_start_stmt_id(self):
        """
        ID
        1. 
        2. ID10
        """
        symbol_table = self.loader.get_module_symbol_table()
        result = len(symbol_table)
        remainder = len(symbol_table) % 10
        result += 10 - remainder
        if remainder < 5:
            return result
        return result + 10

    def adjust_node_id(self, node_id):
        """
        ID
        1. ID
        ID
        """
        # remainder = node_id % 10
        # if remainder != 0:
        #     node_id += (10 - remainder)
        return node_id + config.MIN_ID_INTERVAL

    def run(self):
        """
        
        1. GIR
        2. 
        3. 
        4. 
        """
        if self.options.debug:
            util.debug("\n\t###########  # Language Parsing #  ###########")

        gir_parser = GIRParser(
            self.options,
            self.app_manager,
            self.loader,
            os.path.join(self.options.workspace, config.FRONTEND_DIR)
        )
        all_units = self.loader.get_all_unit_info()
        #all_units = [unit for unit in all_units if unit.lang !='c' or (unit.lang == 'c' and unit.unit_ext == '.i')]

        if self.options.benchmark:
            all_units = all_units.slice(0, config.MAX_BENCHMARK_TARGET)
        if len(all_units) == 0:
            util.error_and_quit("No files found for analysis.")

        current_node_id = self.init_start_stmt_id()
        for unit_info in all_units:
            # if row.symbol_type == constants.SymbolKind.UNIT_SYMBOL and row.unit_ext in extensions:
            current_node_id, gir = gir_parser.deal_with_file_unit(
                current_node_id, unit_info, unit_info.unit_path, lang_table = self.lang_table
            )
            gir_parser.add_unit_gir(unit_info, gir)
            current_node_id = self.adjust_node_id(current_node_id)
            # if self.options.debug:
            #     gir_parser.export()
        gir_parser.export()

        self.loader.export()