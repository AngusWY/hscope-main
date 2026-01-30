#!/usr/bin/env python3
import os,sys

import config.config as config
print(config.TAINT_DIR)
print(config.TAINT_DIR1)
sys.path.extend([config.ENGINE_DIR, config.ANALYZER_DIR, config.TAINT_DIR1, config.TAINT_DIR])
 
from engine.main import Engine
from engine.args_parser import ArgsParser
from frontend.lang_analysis import LangAnalysis
from engine.basics.basic_analysis import BasicSemanticAnalysis
from engine.core.prelim_semantics import PrelimSemanticAnalysis
from engine.core.global_semantics import GlobalSemanticAnalysis
# from engine.semantic.basic_analysis.scope_hierarchy import ImportGraphTranslatorToUnitLevel
from engine.config.constants import SYMBOL_OR_STATE
from engine.taint.taint_analysis import TaintAnalysis
from frontend.abc_parser import ABCParser
import util

class AnalyzerArgsParser(ArgsParser):
    def init(self):
        # Create the top-level parser
        subparsers = self.main_parser.add_subparsers(dest='sub_command')
        # Create the parser for the "lang" command
        parser_compile = subparsers.add_parser('Analyzer', help="run Analyzer")

        parser_run = subparsers.add_parser('run', help='Run the Analyzer')

        for parser in [parser_compile, parser_run]:
            parser.add_argument('in_path', nargs='+', type=str, help='the input')
            parser.add_argument('-w', "--workspace", default=config.DEFAULT_WORKSPACE, type=str, help='the workspace directory (default:engine_workspace)')
            parser.add_argument("-f", "--force", action="store_true", help="Enable the FORCE mode for rewritting the workspace directory")
            parser.add_argument("-d", "--debug", action="store_true", help="Enable the DEBUG mode")
            parser.add_argument("-c", "--cores", default=1, help="Configure the available CPU cores")
            parser.add_argument("--strict-parse-mode", action="store_true", help="Enable the strict way to parse code")
            parser.add_argument("-noextern", action="store_true", help="Disable the external processing module")
            # parser.add_argument("--extern-dir-path", default=None, type=str, help="extern system code")
            parser.add_argument("--default-settings", type=str, help="Specify the default settings folder")
            parser.add_argument("--graph", action="store_true", help="Output sfg (state flow graph) to .dot files")


        return self

    def set_analyzer_default_options(self):
        self.options.lang        = config.LANG_NAME
        self.options.workspace   = config.DEFAULT_WORKSPACE,
        self.options.extern_path = config.EXTERN_SYSTEM_DIR
        return self



class Analyzer:
    def __init__(self):
        self.engine = Engine()
        self.unit_id_to_unit_info = {}
        self.loader = None

    def init_analyzer(self):
        analyzer_out_path = os.path.join(self.engine.options.workspace, config.OUT_DIR)
        self.engine.options.compiler_out_path = analyzer_out_path
        os.makedirs(analyzer_out_path, exist_ok=True)

        unit_headers = os.path.join(analyzer_out_path, config.UNIT_HEADERS)
        self.engine.options.unit_headers = unit_headers
        os.makedirs(unit_headers, exist_ok=True)

        generics_results = os.path.join(analyzer_out_path, config.GENERICS_RESULTS)
        self.engine.options.generics_results = generics_results
        os.makedirs(generics_results, exist_ok=True)

        bin_dir = os.path.join(analyzer_out_path, config.BIN_DIR)
        self.engine.options.bin_dir = bin_dir
        os.makedirs(bin_dir, exist_ok=True)

        # self.analyzer_loader = AnalyzerLoader(self.engine)

    def code_preparation(self):
        for unit_info in self.engine.loader.get_all_unit_info():
            unit_id = util.get_unit_id(unit_info)
            self.unit_id_to_unit_info[unit_id] = unit_info
        for unit_info in self.engine.loader.get_all_unit_info():
            unit_id = util.get_unit_id(unit_info)
            unit_gir = self.engine.loader.get_unit_gir(unit_id)
        pass


    def lang_analysis(self):
        self.engine = Engine()
        self.loader = self.engine.loader
        self.engine.add_lang(config.LANG_NAME, config.LANG_EXTENSION, config.LANG_SO_PATH, ABCParser)
        self.engine.options = AnalyzerArgsParser().init().set_analyzer_default_options().parse_cmds()
        self.engine.init_submodules()
        # self.init_analyzer()
        LangAnalysis(self.engine).run()
        self.code_preparation()
        BasicSemanticAnalysis(self.engine).run()
        prelim_semantic = PrelimSemanticAnalysis(self.engine)
        prelim_semantic.run()
        print(prelim_semantic.analyzed_method_list)
        GlobalSemanticAnalysis(self.engine, prelim_semantic.analyzed_method_list).run()
        self.engine.loader.export()
        # call_graph_p2 = self.loader.load_call_graph_p2()
        # print("call_paths_p2: ", list(call_graph_p2.graph.edges))
    
    def taint_analysis(self):
        self.engine.taint_analysis()
        # TaintAnalysis().run(self.engine)

    def run(self):
        self.lang_analysis()
        self.taint_analysis()

def main():
    Analyzer().run()

if __name__ == "__main__":
    main()

