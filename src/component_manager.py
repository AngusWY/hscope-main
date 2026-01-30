import ast
from config.constant import AnalyzerInternal
from component_struct import Component
class ComponentStructBuilder:
    def __init__(self, code = None):
        self.components = []
        self.code = code
        self.ininitialRender = False
    
    def build(self, code):

        class_name = None
        current_scope = []
        for stmt in code:
            if self.is_class_decl(stmt):
                class_name = stmt["class_decl"]["name"]
                current_scope = [class_name]
            if self.is_method_decl(stmt) and self.method_is_initialRender(stmt):
                current_scope.append('initialRender')
                component = Component(class_name)
                self.components.append(component)
            
            # if self.isin_initialRender():


    def isin_initialRender(self):
        return self.ininitialRender
    def is_class_decl(self, stmt):
        if not isinstance(stmt, dict):
            return False
        return "class_decl" in stmt
    
    def is_method_decl(self, stmt):
        if not isinstance(stmt, dict):
            return False
        return "method_decl" in stmt
    
    def method_is_initialRender(self, method):
        if not isinstance(method, dict):
            return False
        
        if not self.is_method_decl(method):
            return False
        
        return method["method_decl"]["name"] == "initialRender"
    


    
    def add_method(self):
        pass

    def add_field(self):
        pass

    def add_component(self):
        pass

    def add_super(self):
        pass



