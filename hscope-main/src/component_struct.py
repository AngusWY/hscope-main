
class Component:
    def __init__(self, name = None):
        self.component_name = name
        self.callback = {}
    

    def add_callback(self, callback_name, callback_method):
        if callback_name not in self.callback:
            self.callback[callback_name] = [callback_method]
        else:
            self.callback[callback_name].append(callback_method)

    def isCustomComponent(self):
        pass

    def to_dict(self):
        pass

